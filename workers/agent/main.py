import time
from threading import Event, Lock, Thread

import httpx

from .browser_sessions import BrowserSessionCoordinator
from .cleanup import cleanup_stale_worker_artifacts
from .config import load_config
from .control_plane import (
    claim_job,
    fail_job,
    heartbeat_worker,
    is_worker_missing_error,
    register_worker,
)
from .job_runner import run_job


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


class HeartbeatLoop:
    def __init__(self, client: httpx.Client, config) -> None:
        self.client = client
        self.config = config
        self._active_job_ids: list[str] = []
        self._active_job_lock = Lock()
        self._stop_event = Event()
        self._thread = Thread(target=self._run, name="worker-heartbeat", daemon=True)

    def start(self) -> None:
        if not self._thread.is_alive():
            self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        self._thread.join(timeout=1.0)

    def set_active_job_ids(self, job_ids: list[str]) -> None:
        normalized = [str(job_id).strip() for job_id in job_ids if str(job_id).strip()]
        with self._active_job_lock:
            self._active_job_ids = normalized

    def clear_active_job_ids(self) -> None:
        self.set_active_job_ids([])

    def pulse_once(self) -> None:
        active_job_ids = self._snapshot_active_job_ids()
        try:
            heartbeat_worker(
                self.client,
                self.config,
                active_job_ids=active_job_ids,
            )
        except Exception as exc:
            if is_worker_missing_error(exc):
                print("[worker] heartbeat got 404 worker-missing, re-registering.", flush=True)
                register_worker(self.client, self.config)
                heartbeat_worker(
                    self.client,
                    self.config,
                    active_job_ids=active_job_ids,
                )
                return
            raise

    def _snapshot_active_job_ids(self) -> list[str]:
        with self._active_job_lock:
            return list(self._active_job_ids)

    def _run(self) -> None:
        while not self._stop_event.wait(self.config.heartbeat_seconds):
            try:
                self.pulse_once()
            except Exception as exc:
                print(f"[worker] heartbeat loop failed: {exc}", flush=True)
                time.sleep(self.config.poll_seconds)


def main() -> None:
    config = load_config()
    browser_sessions = BrowserSessionCoordinator(config)
    client_timeout = httpx.Timeout(connect=20.0, read=120.0, write=120.0, pool=20.0)
    janitor_interval_seconds = 3600.0
    with httpx.Client(base_url=config.control_plane_url, timeout=client_timeout) as client:
        register_worker(client, config)
        heartbeat_loop = HeartbeatLoop(client, config)
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
                    heartbeat_loop.set_active_job_ids([job_id])
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
                        heartbeat_loop.clear_active_job_ids()
                        try:
                            heartbeat_loop.pulse_once()
                        except Exception as exc:
                            print(f"[worker] post-job heartbeat failed: {exc}", flush=True)
                    time.sleep(config.poll_seconds)
                except Exception as exc:
                    print(f"[worker] main loop recovered from error: {exc}", flush=True)
                    time.sleep(config.poll_seconds)
        finally:
            heartbeat_loop.stop()


if __name__ == "__main__":
    main()
