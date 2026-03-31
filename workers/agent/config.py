from __future__ import annotations

import os
import socket
from dataclasses import dataclass
from pathlib import Path


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
    single_job_only: bool
    capacity: int
    threads: int
    heartbeat_seconds: int
    poll_seconds: int
    simulate_jobs: bool
    execute_jobs: bool
    simulate_step_seconds: float
    work_root: Path
    keep_job_dirs: bool
    ffmpeg_bin: str
    ffprobe_bin: str
    youtube_upload_enabled: bool
    youtube_upload_chunk_bytes: int
    browser_session_enabled: bool
    browser_public_base_url: str | None
    browser_display_base: int
    browser_vnc_port_base: int
    browser_web_port_base: int
    browser_debug_port_base: int
    runtime_cleanup_enabled: bool
    runtime_cleanup_interval_seconds: int
    stale_job_dir_seconds: int
    stale_output_seconds: int


def load_config() -> WorkerConfig:
    hostname = socket.gethostname().split(".")[0]
    work_root = Path(os.getenv("WORKER_DATA_DIR", "/opt/youtube-upload-lush/worker-data")).expanduser()
    single_job_only = os.getenv("WORKER_SINGLE_JOB_ONLY", "true").strip().lower() in {"1", "true", "yes", "on"}
    configured_capacity = int(os.getenv("WORKER_CAPACITY", "1"))
    configured_threads = int(os.getenv("WORKER_THREADS", "1"))
    return WorkerConfig(
        control_plane_url=_env("CONTROL_PLANE_URL").rstrip("/"),
        shared_secret=_env("WORKER_SHARED_SECRET"),
        worker_id=os.getenv("WORKER_ID", hostname).strip() or hostname,
        worker_name=os.getenv("WORKER_NAME", hostname).strip() or hostname,
        manager_name=os.getenv("WORKER_MANAGER", "system").strip() or "system",
        group=os.getenv("WORKER_GROUP", "workers").strip() or "workers",
        single_job_only=single_job_only,
        capacity=1 if single_job_only else max(1, configured_capacity),
        threads=1 if single_job_only else max(1, configured_threads),
        heartbeat_seconds=int(os.getenv("WORKER_HEARTBEAT_SECONDS", "15")),
        poll_seconds=int(os.getenv("WORKER_POLL_SECONDS", "5")),
        simulate_jobs=os.getenv("WORKER_SIMULATE_JOBS", "false").strip().lower() in {"1", "true", "yes", "on"},
        execute_jobs=os.getenv("WORKER_EXECUTE_JOBS", "false").strip().lower() in {"1", "true", "yes", "on"},
        simulate_step_seconds=float(os.getenv("WORKER_SIMULATE_STEP_SECONDS", "2.5")),
        work_root=work_root,
        keep_job_dirs=os.getenv("WORKER_KEEP_JOB_DIRS", "false").strip().lower() in {"1", "true", "yes", "on"},
        ffmpeg_bin=os.getenv("FFMPEG_BIN", "ffmpeg").strip() or "ffmpeg",
        ffprobe_bin=os.getenv("FFPROBE_BIN", "ffprobe").strip() or "ffprobe",
        youtube_upload_enabled=os.getenv("WORKER_UPLOAD_TO_YOUTUBE", "false").strip().lower() in {"1", "true", "yes", "on"},
        youtube_upload_chunk_bytes=int(os.getenv("YOUTUBE_UPLOAD_CHUNK_BYTES", "8388608")),
        browser_session_enabled=os.getenv("BROWSER_SESSION_ENABLED", "false").strip().lower() in {"1", "true", "yes", "on"},
        browser_public_base_url=(os.getenv("BROWSER_SESSION_PUBLIC_BASE_URL", "").strip() or None),
        browser_display_base=int(os.getenv("BROWSER_SESSION_DISPLAY_BASE", "90")),
        browser_vnc_port_base=int(os.getenv("BROWSER_SESSION_VNC_PORT_BASE", "15900")),
        browser_web_port_base=int(os.getenv("BROWSER_SESSION_WEB_PORT_BASE", "16080")),
        browser_debug_port_base=int(os.getenv("BROWSER_SESSION_DEBUG_PORT_BASE", "19220")),
        runtime_cleanup_enabled=os.getenv("WORKER_RUNTIME_CLEANUP_ENABLED", "true").strip().lower() in {"1", "true", "yes", "on"},
        runtime_cleanup_interval_seconds=int(os.getenv("WORKER_RUNTIME_CLEANUP_INTERVAL_SECONDS", "900")),
        stale_job_dir_seconds=int(os.getenv("WORKER_STALE_JOB_DIR_SECONDS", str(6 * 60 * 60))),
        stale_output_seconds=int(os.getenv("WORKER_STALE_OUTPUT_SECONDS", str(6 * 60 * 60))),
    )
