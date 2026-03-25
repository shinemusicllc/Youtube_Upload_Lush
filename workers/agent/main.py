from __future__ import annotations

import os
import shutil
import socket
import time
from dataclasses import dataclass
from typing import Any

import httpx


def _env(name: str, default: str = "") -> str:
    value = os.getenv(name, default).strip()
    if not value:
        raise RuntimeError(f"Missing required env: {name}")
    return value


@dataclass
class WorkerConfig:
    control_plane_url: str
    shared_secret: str
    worker_id: str
    worker_name: str
    manager_name: str
    group: str
    capacity: int
    threads: int
    heartbeat_seconds: int
    poll_seconds: int
    simulate_jobs: bool
    simulate_step_seconds: float


def load_config() -> WorkerConfig:
    hostname = socket.gethostname().split(".")[0]
    return WorkerConfig(
        control_plane_url=_env("CONTROL_PLANE_URL").rstrip("/"),
        shared_secret=_env("WORKER_SHARED_SECRET"),
        worker_id=os.getenv("WORKER_ID", hostname).strip() or hostname,
        worker_name=os.getenv("WORKER_NAME", hostname).strip() or hostname,
        manager_name=os.getenv("WORKER_MANAGER", "system").strip() or "system",
        group=os.getenv("WORKER_GROUP", "workers").strip() or "workers",
        capacity=int(os.getenv("WORKER_CAPACITY", "1")),
        threads=int(os.getenv("WORKER_THREADS", "1")),
        heartbeat_seconds=int(os.getenv("WORKER_HEARTBEAT_SECONDS", "15")),
        poll_seconds=int(os.getenv("WORKER_POLL_SECONDS", "5")),
        simulate_jobs=os.getenv("WORKER_SIMULATE_JOBS", "false").strip().lower() in {"1", "true", "yes", "on"},
        simulate_step_seconds=float(os.getenv("WORKER_SIMULATE_STEP_SECONDS", "2.5")),
    )


def _load_percent() -> int:
    try:
        load_1m = os.getloadavg()[0]
        cpu_count = os.cpu_count() or 1
        return max(0, min(100, int((load_1m / cpu_count) * 100)))
    except OSError:
        return 0


def _disk_usage() -> tuple[float, float]:
    usage = shutil.disk_usage("/")
    total_gb = round(usage.total / (1024 ** 3), 2)
    used_gb = round((usage.total - usage.free) / (1024 ** 3), 2)
    return used_gb, total_gb


def register_worker(client: httpx.Client, config: WorkerConfig) -> None:
    _, total_gb = _disk_usage()
    response = client.post(
        "/api/workers/register",
        json={
            "worker_id": config.worker_id,
            "name": config.worker_name,
            "shared_secret": config.shared_secret,
            "manager_name": config.manager_name,
            "group": config.group,
            "capacity": config.capacity,
            "threads": config.threads,
            "disk_total_gb": total_gb,
        },
    )
    response.raise_for_status()


def heartbeat_worker(client: httpx.Client, config: WorkerConfig) -> None:
    used_gb, total_gb = _disk_usage()
    response = client.post(
        "/api/workers/heartbeat",
        json={
            "worker_id": config.worker_id,
            "shared_secret": config.shared_secret,
            "load_percent": _load_percent(),
            "bandwidth_kbps": 0,
            "disk_used_gb": used_gb,
            "disk_total_gb": total_gb,
            "threads": config.threads,
            "status": "online",
        },
    )
    response.raise_for_status()


def claim_job(client: httpx.Client, config: WorkerConfig) -> dict[str, Any] | None:
    response = client.post(
        "/api/workers/claim",
        json={
            "worker_id": config.worker_id,
            "shared_secret": config.shared_secret,
        },
    )
    response.raise_for_status()
    payload = response.json()
    return payload.get("job")


def update_job_progress(
    client: httpx.Client,
    config: WorkerConfig,
    job_id: str,
    *,
    status: str,
    progress: int,
    message: str | None = None,
) -> None:
    response = client.post(
        f"/api/workers/jobs/{job_id}/progress",
        json={
            "worker_id": config.worker_id,
            "shared_secret": config.shared_secret,
            "status": status,
            "progress": progress,
            "message": message,
        },
    )
    response.raise_for_status()


def complete_job(client: httpx.Client, config: WorkerConfig, job_id: str, *, output_url: str | None = None) -> None:
    response = client.post(
        f"/api/workers/jobs/{job_id}/complete",
        json={
            "worker_id": config.worker_id,
            "shared_secret": config.shared_secret,
            "output_url": output_url,
        },
    )
    response.raise_for_status()


def fail_job(client: httpx.Client, config: WorkerConfig, job_id: str, *, message: str) -> None:
    response = client.post(
        f"/api/workers/jobs/{job_id}/fail",
        json={
            "worker_id": config.worker_id,
            "shared_secret": config.shared_secret,
            "message": message,
        },
    )
    response.raise_for_status()


def simulate_job(client: httpx.Client, config: WorkerConfig, job: dict[str, Any]) -> None:
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
        while True:
            heartbeat_worker(client, config)
            if not config.simulate_jobs:
                time.sleep(config.heartbeat_seconds)
                continue

            job = claim_job(client, config)
            if not job:
                time.sleep(config.poll_seconds)
                continue

            try:
                simulate_job(client, config, job)
            except Exception as exc:
                fail_job(client, config, str(job["id"]), message=str(exc))
                time.sleep(config.poll_seconds)


if __name__ == "__main__":
    main()
