from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from typing import Any

import httpx

from .config import WorkerConfig


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


def worker_auth_headers(config: WorkerConfig) -> dict[str, str]:
    return {
        "x-worker-id": config.worker_id,
        "x-worker-secret": config.shared_secret,
    }


@dataclass
class YouTubeUploadTarget:
    job_id: str
    channel_id: str
    channel_name: str
    title: str
    description: str | None
    privacy_status: str
    client_id: str
    client_secret: str
    refresh_token: str
    token_uri: str


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


def complete_job(
    client: httpx.Client,
    config: WorkerConfig,
    job_id: str,
    *,
    output_url: str | None = None,
    message: str | None = None,
) -> None:
    response = client.post(
        f"/api/workers/jobs/{job_id}/complete",
        json={
            "worker_id": config.worker_id,
            "shared_secret": config.shared_secret,
            "output_url": output_url,
            "message": message,
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


def get_job_youtube_target(client: httpx.Client, config: WorkerConfig, job_id: str) -> YouTubeUploadTarget:
    response = client.get(
        f"/api/workers/jobs/{job_id}/youtube-target",
        headers=worker_auth_headers(config),
    )
    response.raise_for_status()
    payload = response.json()
    return YouTubeUploadTarget(
        job_id=str(payload["job_id"]),
        channel_id=str(payload["channel_id"]),
        channel_name=str(payload["channel_name"]),
        title=str(payload["title"]),
        description=payload.get("description"),
        privacy_status=str(payload["privacy_status"]),
        client_id=str(payload["client_id"]),
        client_secret=str(payload["client_secret"]),
        refresh_token=str(payload["refresh_token"]),
        token_uri=str(payload.get("token_uri") or "https://oauth2.googleapis.com/token"),
    )


def upload_job_thumbnail(
    client: httpx.Client,
    config: WorkerConfig,
    job_id: str,
    *,
    file_name: str,
    content_type: str,
    payload: bytes,
) -> None:
    response = client.post(
        f"/api/workers/jobs/{job_id}/thumbnail",
        headers={
            **worker_auth_headers(config),
            "x-file-name": file_name,
            "content-type": content_type,
        },
        content=payload,
    )
    response.raise_for_status()
