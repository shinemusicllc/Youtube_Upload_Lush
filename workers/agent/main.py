import time

import httpx

from .config import load_config
from .control_plane import claim_job, fail_job, heartbeat_worker, register_worker
from .job_runner import run_job


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
    with httpx.Client(base_url=config.control_plane_url, timeout=20.0) as client:
        register_worker(client, config)
        last_heartbeat_at = 0.0
        while True:
            now = time.monotonic()
            if now - last_heartbeat_at >= config.heartbeat_seconds:
                heartbeat_worker(client, config)
                last_heartbeat_at = now

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
                fail_job(client, config, str(job["id"]), message=str(exc))
                time.sleep(config.poll_seconds)


if __name__ == "__main__":
    main()
