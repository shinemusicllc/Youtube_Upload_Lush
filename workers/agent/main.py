import json
import subprocess
import textwrap
import time
from pathlib import Path
from threading import Event, Lock, Thread

import httpx

from .config import load_config
from .control_plane import (
    LiveStreamStoppedError,
    claim_job,
    claim_live_stream,
    fail_job,
    fail_live_stream,
    heartbeat_live_worker,
    heartbeat_worker,
    is_worker_deleted_error,
    is_worker_missing_error,
    poll_decommission_task,
    register_live_worker,
    register_worker,
)


def _is_cancelled_job_conflict(exc: Exception) -> bool:
    if not isinstance(exc, httpx.HTTPStatusError):
        return False
    response = exc.response
    request = exc.request
    if response is None or request is None:
        return False
    if response.status_code != 409:
        return False
    return "/api/workers/jobs/" in str(request.url)


def _is_stopped_live_stream_conflict(exc: Exception) -> bool:
    if isinstance(exc, LiveStreamStoppedError):
        return True
    if not isinstance(exc, httpx.HTTPStatusError):
        return False
    response = exc.response
    request = exc.request
    if response is None or request is None:
        return False
    if response.status_code != 409:
        return False
    request_url = str(request.url)
    return "/api/live-workers/streams/" in request_url


def simulate_job(client: httpx.Client, config, job: dict) -> None:
    from .control_plane import complete_job, update_job_progress

    job_id = str(job["id"])
    steps = [
        ("downloading", [5, 30, 60, 100]),
        ("rendering", [8, 25, 50, 75, 100]),
        ("uploading", [10, 40, 70, 100]),
    ]
    for status, values in steps:
        for value in values:
            heartbeat_worker(client, config)
            update_job_progress(client, config, job_id, status=status, progress=value)
            time.sleep(config.simulate_step_seconds)
    output_url = f"https://youtube.example/{job_id}"
    complete_job(client, config, job_id, output_url=output_url)


def _start_self_decommission(config, operation_id: str, app_dir: str, runtime_dir: str) -> None:
    script_path = Path(f"/tmp/youtube-upload-self-decommission-{config.worker_id}.sh")
    script_body = textwrap.dedent(
        f"""\
        #!/usr/bin/env bash
        set -euo pipefail

        CONTROL_PLANE_URL={json.dumps(config.control_plane_url.rstrip("/"))}
        OPERATION_ID={json.dumps(operation_id)}
        WORKER_ID={json.dumps(config.worker_id)}
        WORKER_SECRET={json.dumps(config.shared_secret)}
        APP_DIR={json.dumps(app_dir)}
        RUNTIME_DIR={json.dumps(runtime_dir)}
        DECOMMISSION_SCRIPT="$APP_DIR/scripts/decommission_worker.sh"

        notify() {{
          local task_status="$1"
          local task_message="$2"
          if command -v python3 >/dev/null 2>&1; then
            python3 - "$CONTROL_PLANE_URL" "$OPERATION_ID" "$WORKER_ID" "$WORKER_SECRET" "$task_status" "$task_message" <<'PY' || true
import json
import sys
import urllib.request

control_plane_url, operation_id, worker_id, worker_secret, status, message = sys.argv[1:7]
url = f"{{control_plane_url}}/api/workers/decommission/{{operation_id}}/complete"
payload = json.dumps({{
    "worker_id": worker_id,
    "shared_secret": worker_secret,
    "status": status,
    "message": message,
}}).encode("utf-8")
request = urllib.request.Request(
    url,
    data=payload,
    headers={{"Content-Type": "application/json"}},
    method="POST",
)
with urllib.request.urlopen(request, timeout=20) as response:
    response.read()
PY
          fi
          return 0
        }}

        trap 'notify failed "Tự gỡ BOT trên VPS thất bại."' ERR

        if [[ -x "$DECOMMISSION_SCRIPT" || -f "$DECOMMISSION_SCRIPT" ]]; then
          env APP_DIR="$APP_DIR" RUNTIME_DIR="$RUNTIME_DIR" bash "$DECOMMISSION_SCRIPT"
        else
          systemctl stop youtube-upload-worker.service || true
          systemctl disable youtube-upload-worker.service || true
          rm -f /etc/systemd/system/youtube-upload-worker.service
          rm -f /etc/youtube-upload-worker.env
          systemctl daemon-reload || true
          systemctl reset-failed youtube-upload-worker.service || true
          rm -rf "$APP_DIR" "$RUNTIME_DIR"
        fi

        notify completed "BOT đã tự gỡ sạch khỏi VPS."
        rm -f -- "$0"
        """
    )
    script_path.write_text(script_body, encoding="utf-8")
    script_path.chmod(0o700)
    transient_unit = f"youtube-upload-self-decommission-{config.worker_id}"
    try:
        subprocess.run(
            [
                "systemd-run",
                "--unit",
                transient_unit,
                "--property=Type=oneshot",
                "--collect",
                "/bin/bash",
                str(script_path),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return
    except Exception:
        with open("/tmp/youtube-upload-self-decommission.log", "ab") as log_handle:
            subprocess.Popen(
                ["/bin/bash", str(script_path)],
                stdout=log_handle,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )


def _maybe_process_decommission(client: httpx.Client, config, heartbeat_loop: "UploadHeartbeatLoop") -> bool:
    assignment = poll_decommission_task(client, config)
    if assignment is None:
        return False
    print(f"[worker] nhận lệnh tự gỡ BOT {config.worker_id} khỏi VPS.", flush=True)
    heartbeat_loop.stop()
    _start_self_decommission(
        config,
        assignment.operation_id,
        assignment.app_dir,
        assignment.runtime_dir,
    )
    raise SystemExit("[worker] đã khởi chạy self-decommission, dừng tiến trình worker.")


class UploadHeartbeatLoop:
    def __init__(self, client: httpx.Client, config) -> None:
        self.client = client
        self.config = config
        self._active_ids: list[str] = []
        self._active_lock = Lock()
        self._stop_event = Event()
        self._thread = Thread(target=self._run, name="worker-heartbeat", daemon=True)

    def start(self) -> None:
        if not self._thread.is_alive():
            self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        self._thread.join(timeout=1.0)

    def set_active_ids(self, job_ids: list[str]) -> None:
        normalized = [str(job_id).strip() for job_id in job_ids if str(job_id).strip()]
        with self._active_lock:
            self._active_ids = normalized

    def clear_active_ids(self) -> None:
        self.set_active_ids([])

    def pulse_once(self) -> None:
        active_ids = self._snapshot_active_ids()
        try:
            heartbeat_worker(
                self.client,
                self.config,
                active_job_ids=active_ids,
            )
        except Exception as exc:
            if is_worker_deleted_error(exc):
                raise SystemExit("[worker] BOT này đã bị xoá khỏi control-plane, dừng worker.")
            if is_worker_missing_error(exc):
                print("[worker] heartbeat got 404 worker-missing, re-registering.", flush=True)
                register_worker(self.client, self.config)
                heartbeat_worker(
                    self.client,
                    self.config,
                    active_job_ids=active_ids,
                )
                return
            raise

    def _snapshot_active_ids(self) -> list[str]:
        with self._active_lock:
            return list(self._active_ids)

    def _run(self) -> None:
        while not self._stop_event.wait(self.config.heartbeat_seconds):
            try:
                self.pulse_once()
            except Exception as exc:
                if isinstance(exc, SystemExit):
                    print(str(exc), flush=True)
                    break
                print(f"[worker] heartbeat loop failed: {exc}", flush=True)
                time.sleep(self.config.poll_seconds)


class LiveHeartbeatLoop:
    def __init__(self, client: httpx.Client, config) -> None:
        self.client = client
        self.config = config
        self._active_ids: list[str] = []
        self._active_lock = Lock()
        self._stop_event = Event()
        self._thread = Thread(target=self._run, name="live-worker-heartbeat", daemon=True)

    def start(self) -> None:
        if not self._thread.is_alive():
            self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        self._thread.join(timeout=1.0)

    def set_active_ids(self, stream_ids: list[str]) -> None:
        normalized = [str(stream_id).strip() for stream_id in stream_ids if str(stream_id).strip()]
        with self._active_lock:
            self._active_ids = normalized

    def clear_active_ids(self) -> None:
        self.set_active_ids([])

    def pulse_once(self) -> None:
        active_ids = self._snapshot_active_ids()
        try:
            heartbeat_live_worker(
                self.client,
                self.config,
                active_stream_ids=active_ids,
            )
        except Exception as exc:
            if is_worker_deleted_error(exc):
                raise SystemExit("[live-worker] BOT này đã bị xoá khỏi control-plane, dừng worker.")
            if is_worker_missing_error(exc):
                print("[live-worker] heartbeat got 404 worker-missing, re-registering.", flush=True)
                register_live_worker(self.client, self.config)
                heartbeat_live_worker(
                    self.client,
                    self.config,
                    active_stream_ids=active_ids,
                )
                return
            raise

    def _snapshot_active_ids(self) -> list[str]:
        with self._active_lock:
            return list(self._active_ids)

    def _run(self) -> None:
        while not self._stop_event.wait(self.config.heartbeat_seconds):
            try:
                self.pulse_once()
            except Exception as exc:
                if isinstance(exc, SystemExit):
                    print(str(exc), flush=True)
                    break
                print(f"[live-worker] heartbeat loop failed: {exc}", flush=True)
                time.sleep(self.config.poll_seconds)


def _run_upload_worker(client: httpx.Client, config) -> None:
    from .browser_sessions import BrowserSessionCoordinator
    from .cleanup import cleanup_stale_worker_artifacts
    from .job_runner import run_job

    browser_sessions = BrowserSessionCoordinator(config)
    janitor_interval_seconds = 3600.0
    register_worker(client, config)
    heartbeat_loop = UploadHeartbeatLoop(client, config)
    heartbeat_loop.start()
    heartbeat_loop.pulse_once()
    janitor_result = cleanup_stale_worker_artifacts(config)
    if any(janitor_result.values()):
        print(f"[cleanup] startup janitor: {janitor_result}", flush=True)
    last_janitor_at = time.monotonic()
    try:
        while True:
            try:
                _maybe_process_decommission(client, config, heartbeat_loop)
                now = time.monotonic()
                if now - last_janitor_at >= janitor_interval_seconds:
                    janitor_result = cleanup_stale_worker_artifacts(config)
                    if any(janitor_result.values()):
                        print(f"[cleanup] periodic janitor: {janitor_result}", flush=True)
                    last_janitor_at = now

                try:
                    browser_sessions.reconcile(client)
                except Exception as exc:
                    print(f"[browser_sessions] reconcile failed: {exc}", flush=True)

                if not config.simulate_jobs and not config.execute_jobs:
                    time.sleep(config.poll_seconds)
                    continue

                try:
                    job = claim_job(client, config)
                except Exception as exc:
                    if is_worker_deleted_error(exc):
                        print("[worker] BOT này đã bị xoá khỏi control-plane, dừng worker.", flush=True)
                        break
                    if is_worker_missing_error(exc):
                        print("[worker] claim got 404 worker-missing, re-registering.", flush=True)
                        register_worker(client, config)
                        heartbeat_loop.pulse_once()
                        time.sleep(config.poll_seconds)
                        continue
                    raise
                if not job:
                    time.sleep(config.poll_seconds)
                    continue

                job_id = str(job["id"])
                heartbeat_loop.set_active_ids([job_id])
                heartbeat_loop.pulse_once()

                try:
                    if config.simulate_jobs:
                        simulate_job(client, config, job)
                    else:
                        run_job(client, config, job)
                except Exception as exc:
                    if _is_cancelled_job_conflict(exc):
                        print(f"[job] {job['id']} da bi huy tren control plane, dung worker flow sach se.", flush=True)
                        time.sleep(config.poll_seconds)
                        continue
                    fail_job(client, config, job_id, message=str(exc))
                finally:
                    heartbeat_loop.clear_active_ids()
                    try:
                        heartbeat_loop.pulse_once()
                    except Exception as exc:
                        print(f"[worker] post-job heartbeat failed: {exc}", flush=True)
                time.sleep(config.poll_seconds)
            except Exception as exc:
                if is_worker_deleted_error(exc):
                    print("[worker] BOT này đã bị xoá khỏi control-plane, dừng worker.", flush=True)
                    break
                print(f"[worker] main loop recovered from error: {exc}", flush=True)
                time.sleep(config.poll_seconds)
    finally:
        heartbeat_loop.stop()


def _run_live_worker(client: httpx.Client, config) -> None:
    from .cleanup import cleanup_stale_worker_artifacts
    from .live_runner import run_live_stream, simulate_live_stream

    janitor_interval_seconds = 3600.0
    register_live_worker(client, config)
    heartbeat_loop = LiveHeartbeatLoop(client, config)
    heartbeat_loop.start()
    heartbeat_loop.pulse_once()
    janitor_result = cleanup_stale_worker_artifacts(config)
    if any(janitor_result.values()):
        print(f"[cleanup] startup janitor: {janitor_result}", flush=True)
    last_janitor_at = time.monotonic()
    try:
        while True:
            try:
                now = time.monotonic()
                if now - last_janitor_at >= janitor_interval_seconds:
                    janitor_result = cleanup_stale_worker_artifacts(config)
                    if any(janitor_result.values()):
                        print(f"[cleanup] periodic janitor: {janitor_result}", flush=True)
                    last_janitor_at = now

                if not config.simulate_jobs and not config.execute_jobs:
                    time.sleep(config.poll_seconds)
                    continue

                try:
                    stream = claim_live_stream(client, config)
                except Exception as exc:
                    if is_worker_deleted_error(exc):
                        print("[live-worker] BOT này đã bị xoá khỏi control-plane, dừng worker.", flush=True)
                        break
                    if is_worker_missing_error(exc):
                        print("[live-worker] claim got 404 worker-missing, re-registering.", flush=True)
                        register_live_worker(client, config)
                        heartbeat_loop.pulse_once()
                        time.sleep(config.poll_seconds)
                        continue
                    raise
                if not stream:
                    time.sleep(config.poll_seconds)
                    continue

                stream_id = str(stream["id"])
                heartbeat_loop.set_active_ids([stream_id])
                heartbeat_loop.pulse_once()

                try:
                    if config.simulate_jobs:
                        simulate_live_stream(client, config, stream)
                    else:
                        run_live_stream(client, config, stream)
                except Exception as exc:
                    if _is_stopped_live_stream_conflict(exc):
                        print(f"[live] {stream['id']} không còn tiếp tục được trên control plane, dừng worker flow sạch sẽ.", flush=True)
                        time.sleep(config.poll_seconds)
                        continue
                    fail_live_stream(client, config, stream_id, message=str(exc))
                finally:
                    heartbeat_loop.clear_active_ids()
                    try:
                        heartbeat_loop.pulse_once()
                    except Exception as exc:
                        print(f"[live-worker] post-stream heartbeat failed: {exc}", flush=True)
                time.sleep(config.poll_seconds)
            except Exception as exc:
                if is_worker_deleted_error(exc):
                    print("[live-worker] BOT này đã bị xoá khỏi control-plane, dừng worker.", flush=True)
                    break
                print(f"[live-worker] main loop recovered from error: {exc}", flush=True)
                time.sleep(config.poll_seconds)
    finally:
        heartbeat_loop.stop()


def main() -> None:
    config = load_config()
    client_timeout = httpx.Timeout(connect=20.0, read=120.0, write=120.0, pool=20.0)
    with httpx.Client(base_url=config.control_plane_url, timeout=client_timeout) as client:
        if config.runtime_mode == "live":
            _run_live_worker(client, config)
            return
        _run_upload_worker(client, config)


if __name__ == "__main__":
    main()
