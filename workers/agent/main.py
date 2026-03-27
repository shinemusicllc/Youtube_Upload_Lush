import threading
import time
from typing import Any

import httpx

from .config import load_config
from .control_plane import claim_job, complete_job, fail_job, heartbeat_worker, register_worker, update_job_progress
from .job_runner import run_job


def simulate_job(client: httpx.Client, config, job: dict) -> None:
    job_id = str(job["id"])
    steps = [
        ("downloading", [5, 30, 60, 100]),
        ("rendering", [8, 25, 50, 75, 100]),
        ("uploading", [10, 40, 70, 100]),
    ]
    for status, values in steps:
        for value in values:
            update_job_progress(client, config, job_id, status=status, progress=value)
            time.sleep(config.simulate_step_seconds)
    output_url = f"https://youtube.example/{job_id}"
    complete_job(client, config, job_id, output_url=output_url)


def _extract_desired_threads(payload: dict[str, Any] | None, fallback: int) -> int:
    try:
        worker_payload = payload.get("worker") if isinstance(payload, dict) else None
        thread_value = worker_payload.get("threads") if isinstance(worker_payload, dict) else None
        return max(1, int(thread_value or fallback or 1))
    except (TypeError, ValueError):
        return max(1, int(fallback or 1))


def _run_job_task(config, job: dict) -> None:
    job_id = str(job["id"])
    try:
        with httpx.Client(base_url=config.control_plane_url, timeout=20.0) as client:
            if config.simulate_jobs:
                simulate_job(client, config, job)
            else:
                run_job(client, config, job)
    except Exception as exc:
        try:
            with httpx.Client(base_url=config.control_plane_url, timeout=20.0) as client:
                fail_job(client, config, job_id, message=str(exc))
        except Exception as report_exc:
            print(f"[worker] failed to report error for {job_id}: {report_exc}")


def main() -> None:
    config = load_config()
    desired_threads = max(1, int(config.threads or config.capacity or 1))
    active_jobs: dict[str, threading.Thread] = {}

    with httpx.Client(base_url=config.control_plane_url, timeout=20.0) as client:
        register_payload = register_worker(client, config)
        desired_threads = _extract_desired_threads(register_payload, desired_threads)
        last_heartbeat_at = 0.0

        while True:
            for job_id, thread in list(active_jobs.items()):
                if not thread.is_alive():
                    thread.join(timeout=0)
                    active_jobs.pop(job_id, None)

            now = time.monotonic()
            if now - last_heartbeat_at >= config.heartbeat_seconds:
                heartbeat_payload = heartbeat_worker(client, config)
                desired_threads = _extract_desired_threads(heartbeat_payload, desired_threads)
                last_heartbeat_at = now

            if not config.simulate_jobs and not config.execute_jobs:
                time.sleep(config.poll_seconds)
                continue

            available_slots = max(0, desired_threads - len(active_jobs))
            claimed_any = False
            for _ in range(available_slots):
                job = claim_job(client, config)
                if not job:
                    break
                job_id = str(job["id"])
                if job_id in active_jobs:
                    continue
                thread = threading.Thread(
                    target=_run_job_task,
                    args=(config, job),
                    name=f"{config.worker_id}-{job_id}",
                    daemon=True,
                )
                thread.start()
                active_jobs[job_id] = thread
                claimed_any = True

            if claimed_any:
                continue

            time.sleep(config.poll_seconds)


if __name__ == "__main__":
    main()
