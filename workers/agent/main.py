import time

import httpx

from .browser_sessions import BrowserSessionCoordinator
from .cleanup import cleanup_stale_worker_artifacts
from .config import load_config
from .control_plane import claim_job, fail_job, heartbeat_worker, register_worker
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


def main() -> None:
    config = load_config()
    browser_sessions = BrowserSessionCoordinator(config)
    client_timeout = httpx.Timeout(connect=20.0, read=120.0, write=120.0, pool=20.0)
    janitor_interval_seconds = 3600.0
    with httpx.Client(base_url=config.control_plane_url, timeout=client_timeout) as client:
        register_worker(client, config)
        last_heartbeat_at = 0.0
        janitor_result = cleanup_stale_worker_artifacts(config)
        if any(janitor_result.values()):
            print(f"[cleanup] startup janitor: {janitor_result}", flush=True)
        last_janitor_at = time.monotonic()
        while True:
            now = time.monotonic()
            if now - last_heartbeat_at >= config.heartbeat_seconds:
                heartbeat_worker(client, config)
                last_heartbeat_at = now

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

            job = claim_job(client, config)
            if not job:
                time.sleep(config.poll_seconds)
                continue

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
                fail_job(client, config, str(job["id"]), message=str(exc))
                time.sleep(config.poll_seconds)


if __name__ == "__main__":
    main()
