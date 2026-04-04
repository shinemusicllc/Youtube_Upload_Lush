from __future__ import annotations

import os
import shutil
import time
from dataclasses import dataclass
from typing import Any

import httpx

from .config import WorkerConfig


_last_bandwidth_sample: tuple[float, int] | None = None
_last_cpu_sample: tuple[int, int] | None = None


def _load_percent() -> int:
    try:
        with open("/proc/stat", "r", encoding="utf-8") as handle:
            first_line = handle.readline().strip()
    except OSError:
        return 0

    if not first_line.startswith("cpu "):
        return 0

    parts = first_line.split()[1:]
    if len(parts) < 4:
        return 0

    try:
        counters = [int(value) for value in parts]
    except ValueError:
        return 0

    idle_ticks = counters[3] + (counters[4] if len(counters) > 4 else 0)
    total_ticks = sum(counters)

    global _last_cpu_sample
    previous_sample = _last_cpu_sample
    _last_cpu_sample = (total_ticks, idle_ticks)
    if previous_sample is None:
        return 0

    previous_total, previous_idle = previous_sample
    total_delta = total_ticks - previous_total
    idle_delta = idle_ticks - previous_idle
    if total_delta <= 0:
        return 0

    busy_ratio = 1 - (max(0, idle_delta) / total_delta)
    return max(0, min(100, int(round(busy_ratio * 100))))


def _disk_usage() -> tuple[float, float]:
    usage = shutil.disk_usage("/")
    total_gb = round(usage.total / (1024 ** 3), 2)
    used_gb = round((usage.total - usage.free) / (1024 ** 3), 2)
    return used_gb, total_gb


def _memory_usage() -> tuple[float, float, int]:
    mem_total_kb = 0
    mem_available_kb = 0
    try:
        with open("/proc/meminfo", "r", encoding="utf-8") as handle:
            for raw_line in handle:
                line = raw_line.strip()
                if line.startswith("MemTotal:"):
                    mem_total_kb = int(line.split()[1])
                elif line.startswith("MemAvailable:"):
                    mem_available_kb = int(line.split()[1])
    except (OSError, ValueError):
        return 0.0, 0.0, 0

    if mem_total_kb <= 0:
        return 0.0, 0.0, 0

    used_kb = max(0, mem_total_kb - mem_available_kb)
    total_gb = round(mem_total_kb / (1024 ** 2), 2)
    used_gb = round(used_kb / (1024 ** 2), 2)
    percent = max(0, min(100, int(round((used_kb / mem_total_kb) * 100))))
    return used_gb, total_gb, percent


def _network_total_bytes() -> int:
    try:
        with open("/proc/net/dev", "r", encoding="utf-8") as handle:
            lines = handle.readlines()[2:]
    except OSError:
        return 0

    total_bytes = 0
    for raw_line in lines:
        if ":" not in raw_line:
            continue
        interface_name, counters = raw_line.split(":", 1)
        iface = interface_name.strip()
        if iface == "lo":
            continue
        parts = counters.split()
        if len(parts) < 16:
            continue
        try:
            received_bytes = int(parts[0])
            transmitted_bytes = int(parts[8])
        except ValueError:
            continue
        total_bytes += received_bytes + transmitted_bytes
    return total_bytes


def _bandwidth_kbps() -> float:
    global _last_bandwidth_sample

    now = time.monotonic()
    total_bytes = _network_total_bytes()
    if total_bytes <= 0:
        _last_bandwidth_sample = (now, max(total_bytes, 0))
        return 0.0

    previous_sample = _last_bandwidth_sample
    _last_bandwidth_sample = (now, total_bytes)
    if previous_sample is None:
        return 0.0

    previous_time, previous_total = previous_sample
    elapsed_seconds = now - previous_time
    if elapsed_seconds <= 0:
        return 0.0

    delta_bytes = max(0, total_bytes - previous_total)
    return round((delta_bytes / elapsed_seconds) / 1024, 2)


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
    connection_mode: str = "browser_profile"
    browser_profile_key: str | None = None
    browser_profile_path: str | None = None


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
    ram_used_gb, ram_total_gb, ram_percent = _memory_usage()
    response = client.post(
        "/api/workers/heartbeat",
        json={
            "worker_id": config.worker_id,
            "shared_secret": config.shared_secret,
            "load_percent": _load_percent(),
            "ram_percent": ram_percent,
            "ram_used_gb": ram_used_gb,
            "ram_total_gb": ram_total_gb,
            "bandwidth_kbps": _bandwidth_kbps(),
            "disk_used_gb": used_gb,
            "disk_total_gb": total_gb,
            "threads": config.threads,
            "status": "online",
            "public_base_url": config.browser_public_base_url,
            "browser_session_enabled": config.browser_session_enabled,
            "browser_display_base": config.browser_display_base,
            "browser_vnc_port_base": config.browser_vnc_port_base,
            "browser_web_port_base": config.browser_web_port_base,
            "browser_debug_port_base": config.browser_debug_port_base,
            "active_job_ids": active_job_ids or [],
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
    sessions: list[BrowserSessionAssignment] = []
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
        connection_mode=str(payload.get("connection_mode") or "browser_profile"),
        browser_profile_key=payload.get("browser_profile_key"),
        browser_profile_path=payload.get("browser_profile_path"),
    )
