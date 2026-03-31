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
    connection_mode: str = "oauth"
    browser_profile_key: str | None = None
    browser_profile_path: str | None = None
    client_id: str | None = None
    client_secret: str | None = None
    refresh_token: str | None = None
    token_uri: str = "https://oauth2.googleapis.com/token"


@dataclass
class BrowserSessionAssignment:
    session_id: str
    status: str
    profile_key: str
    display_number: int
    vnc_port: int
    web_port: int
    debug_port: int
    access_password: str
    current_url: str | None
    current_title: str | None
    detected_channel_id: str | None
    detected_channel_name: str | None
    novnc_url: str | None


@dataclass
class BrowserProfileCleanupAssignment:
    profile_key: str


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
            "public_base_url": config.browser_public_base_url,
            "browser_session_enabled": config.browser_session_enabled,
            "browser_display_base": config.browser_display_base,
            "browser_vnc_port_base": config.browser_vnc_port_base,
            "browser_web_port_base": config.browser_web_port_base,
            "browser_debug_port_base": config.browser_debug_port_base,
        },
    )
    response.raise_for_status()


def heartbeat_worker(
    client: httpx.Client,
    config: WorkerConfig,
    *,
    active_job_ids: list[str] | None = None,
) -> None:
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
            "active_job_ids": active_job_ids if active_job_ids is not None else [],
            "public_base_url": config.browser_public_base_url,
            "browser_session_enabled": config.browser_session_enabled,
            "browser_display_base": config.browser_display_base,
            "browser_vnc_port_base": config.browser_vnc_port_base,
            "browser_web_port_base": config.browser_web_port_base,
            "browser_debug_port_base": config.browser_debug_port_base,
        },
    )
    response.raise_for_status()


def poll_browser_sessions(
    client: httpx.Client,
    config: WorkerConfig,
) -> tuple[list[BrowserSessionAssignment], list[BrowserProfileCleanupAssignment]]:
    response = client.post(
        "/api/workers/browser-sessions/poll",
        json={
            "worker_id": config.worker_id,
            "shared_secret": config.shared_secret,
        },
    )
    response.raise_for_status()
    payload = response.json()
    sessions = []
    for item in payload.get("sessions") or []:
        sessions.append(
            BrowserSessionAssignment(
                session_id=str(item["session_id"]),
                status=str(item["status"]),
                profile_key=str(item["profile_key"]),
                display_number=int(item["display_number"]),
                vnc_port=int(item["vnc_port"]),
                web_port=int(item["web_port"]),
                debug_port=int(item["debug_port"]),
                access_password=str(item["access_password"]),
                current_url=item.get("current_url"),
                current_title=item.get("current_title"),
                detected_channel_id=item.get("detected_channel_id"),
                detected_channel_name=item.get("detected_channel_name"),
                novnc_url=item.get("novnc_url"),
            )
        )
    cleanup_profiles = [
        BrowserProfileCleanupAssignment(profile_key=str(item.get("profile_key") or "").strip())
        for item in (payload.get("cleanup_profiles") or [])
        if str(item.get("profile_key") or "").strip()
    ]
    return sessions, cleanup_profiles


def ack_browser_profile_cleanup(
    client: httpx.Client,
    config: WorkerConfig,
    profile_keys: list[str],
) -> None:
    if not profile_keys:
        return
    response = client.post(
        "/api/workers/browser-profiles/cleanup-ack",
        json={
            "worker_id": config.worker_id,
            "shared_secret": config.shared_secret,
            "profile_keys": profile_keys,
        },
    )
    response.raise_for_status()


def sync_browser_session(
    client: httpx.Client,
    config: WorkerConfig,
    session_id: str,
    *,
    status: str,
    novnc_url: str | None = None,
    current_url: str | None = None,
    current_title: str | None = None,
    detected_channel_id: str | None = None,
    detected_channel_name: str | None = None,
    last_error: str | None = None,
    profile_path: str | None = None,
    session_path: str | None = None,
    password_file: str | None = None,
    xvfb_pid: int | None = None,
    openbox_pid: int | None = None,
    chromium_pid: int | None = None,
    x11vnc_pid: int | None = None,
    websockify_pid: int | None = None,
) -> None:
    response = client.post(
        f"/api/workers/browser-sessions/{session_id}/sync",
        json={
            "worker_id": config.worker_id,
            "shared_secret": config.shared_secret,
            "status": status,
            "novnc_url": novnc_url,
            "current_url": current_url,
            "current_title": current_title,
            "detected_channel_id": detected_channel_id,
            "detected_channel_name": detected_channel_name,
            "last_error": last_error,
            "profile_path": profile_path,
            "session_path": session_path,
            "password_file": password_file,
            "xvfb_pid": xvfb_pid,
            "openbox_pid": openbox_pid,
            "chromium_pid": chromium_pid,
            "x11vnc_pid": x11vnc_pid,
            "websockify_pid": websockify_pid,
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


def upload_job_thumbnail(
    client: httpx.Client,
    config: WorkerConfig,
    job_id: str,
    *,
    file_name: str,
    payload: bytes,
    content_type: str = "image/jpeg",
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
        connection_mode=str(payload.get("connection_mode") or "oauth"),
        browser_profile_key=payload.get("browser_profile_key"),
        browser_profile_path=payload.get("browser_profile_path"),
        client_id=payload.get("client_id"),
        client_secret=payload.get("client_secret"),
        refresh_token=payload.get("refresh_token"),
        token_uri=str(payload.get("token_uri") or "https://oauth2.googleapis.com/token"),
    )
