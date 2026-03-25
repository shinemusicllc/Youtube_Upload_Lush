from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta
import json
import os
import re
from pathlib import Path
import shutil
import sqlite3
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from uuid import uuid4

from dotenv import load_dotenv

from .schemas import (
    AdminDashboardResponse,
    AdminSummary,
    ChannelRecord,
    JobAsset,
    JobCreatePayload,
    OAuthStartResponse,
    OAuthSummary,
    RenderJobRecord,
    UploadCapabilities,
    UploadSessionCreateRequest,
    UploadSessionRecord,
    UploadSessionResponse,
    UserBootstrapResponse,
    UserJobsResponse,
    UserSummary,
    WorkerControlResponse,
    WorkerHeartbeatPayload,
    WorkerRegisterPayload,
    WorkerRecord,
)

load_dotenv(Path(__file__).resolve().parents[2] / ".env")


class AppStore:
    def __init__(self) -> None:
        now = datetime.now().replace(second=0, microsecond=0)
        self.data_dir = Path(__file__).resolve().parents[1] / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.upload_dir = self.data_dir / "uploads"
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.upload_tmp_dir = self.upload_dir / "tmp"
        self.upload_tmp_dir.mkdir(parents=True, exist_ok=True)
        self.upload_asset_dir = self.upload_dir / "assets"
        self.upload_asset_dir.mkdir(parents=True, exist_ok=True)
        self.state_db_path = self.data_dir / "app_state.db"
        self.upload_sessions: list[UploadSessionRecord] = []

        self.users = [
            UserSummary(id="admin-1", username="admin", display_name="Admin", role="admin"),
            UserSummary(id="manager-1", username="manager-alpha", display_name="Manager Alpha", role="manager"),
            UserSummary(id="user-1", username="demo-user", display_name="demo-user", role="user", manager_name="manager-alpha"),
        ]
        self.user_meta: dict[str, dict[str, Any]] = {
            "admin-1": {
                "password": "admin123",
                "telegram": "@admin-control",
                "updated_by": "system",
                "updated_at": now - timedelta(days=3),
                "created_at": now - timedelta(days=30),
            },
            "manager-1": {
                "password": "manager123",
                "telegram": "@manager-alpha",
                "updated_by": "admin",
                "updated_at": now - timedelta(days=2),
                "created_at": now - timedelta(days=20),
            },
            "user-1": {
                "password": "demo123",
                "telegram": "@demo-user",
                "updated_by": "manager-alpha",
                "updated_at": now - timedelta(hours=5),
                "created_at": now - timedelta(days=10),
            },
        }

        self.workers = [
            WorkerRecord(
                id="worker-01",
                name="worker-01",
                manager_id="manager-1",
                manager_name="manager-alpha",
                group="manager-alpha",
                status="online",
                capacity=4,
                load_percent=45,
                bandwidth_kbps=1024,
                disk_used_gb=124.5,
                disk_total_gb=512.0,
                threads=2,
                last_seen_at=now,
            ),
            WorkerRecord(
                id="worker-02",
                name="worker-02",
                manager_id="manager-1",
                manager_name="manager-alpha",
                group="manager-alpha",
                status="online",
                capacity=4,
                load_percent=28,
                bandwidth_kbps=832,
                disk_used_gb=88.2,
                disk_total_gb=512.0,
                threads=2,
                last_seen_at=now,
            ),
        ]
        self.user_worker_links: list[dict[str, Any]] = [
            {"id": 1, "user_id": "user-1", "worker_id": "worker-01", "threads": 2, "note": "BOT chính"},
            {"id": 2, "user_id": "user-1", "worker_id": "worker-02", "threads": 1, "note": "BOT phụ"},
        ]

        self.channels = [
            ChannelRecord(
                id="channel-1",
                name="Kodi Lofi",
                channel_id="UCNaAEEC2W6ISnzTmmKjMCMg",
                avatar_url="https://images.unsplash.com/photo-1516280440614-37939bbacd81?auto=format&fit=crop&w=80&q=80",
                worker_id="worker-01",
                worker_name="worker-01",
                manager_name="manager-alpha",
                status="connected",
                oauth_email="kodi-lofi@example.com",
                oauth_connected_at=now - timedelta(days=2),
            ),
            ChannelRecord(
                id="channel-2",
                name="Daily Beats",
                channel_id="UCdemo00000000000000001",
                avatar_url="https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?auto=format&fit=crop&w=80&q=80",
                worker_id="worker-02",
                worker_name="worker-02",
                manager_name="manager-alpha",
                status="connected",
                oauth_email="daily-beats@example.com",
                oauth_connected_at=now - timedelta(days=1),
            ),
            ChannelRecord(
                id="channel-3",
                name="demo-user-youtube-channel",
                channel_id="UCuserdemo",
                avatar_url=None,
                worker_id="worker-01",
                worker_name="worker-01",
                manager_name="manager-alpha",
                status="connected",
                oauth_email="demo-user@example.com",
                oauth_connected_at=now - timedelta(hours=8),
            ),
        ]
        self.channel_user_links: list[dict[str, Any]] = [
            {"id": 1, "channel_id": "channel-1", "user_id": "user-1"},
            {"id": 2, "channel_id": "channel-2", "user_id": "user-1"},
        ]

        self.jobs = [
            RenderJobRecord(
                id="job-379e626e",
                title="Drive Job Local Check",
                source_mode="drive",
                channel_id="channel-1",
                channel_name="Kodi Lofi",
                channel_avatar_url=self.channels[0].avatar_url,
                worker_name="worker-01",
                manager_name="manager-alpha",
                status="queueing",
                progress=0,
                queue_order=1,
                created_at=now - timedelta(minutes=43),
                source_label="Google Drive/cloud",
                thumbnail_url=None,
                assets=[
                    JobAsset(slot="video_loop", label="Video loop", source_mode="drive", url="https://drive.google.com/video-loop"),
                    JobAsset(slot="audio_loop", label="Audio loop", source_mode="drive", url="https://drive.google.com/audio-loop"),
                ],
            ),
            RenderJobRecord(
                id="job-3787e1cd",
                title="Local Upload Test",
                source_mode="local",
                channel_id="channel-2",
                channel_name="Daily Beats",
                channel_avatar_url=self.channels[1].avatar_url,
                worker_name="worker-02",
                manager_name="manager-alpha",
                status="pending",
                progress=0,
                queue_order=2,
                created_at=now - timedelta(minutes=44),
                source_label="Local Upload",
                source_file_name="local-upload-test.mp4",
                thumbnail_url=None,
                assets=[
                    JobAsset(slot="video_loop", label="Video loop", source_mode="local", file_name="local-upload-test.mp4"),
                    JobAsset(slot="audio_loop", label="Audio loop", source_mode="local", file_name="ambient-loop.mp3"),
                ],
            ),
            RenderJobRecord(
                id="job-1002",
                title="Loop Mix Episode 2",
                source_mode="local",
                channel_id="channel-2",
                channel_name="Daily Beats",
                channel_avatar_url=self.channels[1].avatar_url,
                worker_name="worker-02",
                manager_name="manager-alpha",
                status="rendering",
                progress=42,
                queue_order=8,
                created_at=now - timedelta(hours=2),
                source_label="Local Upload",
                source_file_name="loop-mix-episode-2.mp4",
                thumbnail_url=None,
                assets=[
                    JobAsset(slot="video_loop", label="Video loop", source_mode="local", file_name="loop-mix-episode-2.mp4"),
                    JobAsset(slot="audio_loop", label="Audio loop", source_mode="local", file_name="loop-mix-episode-2.mp3"),
                ],
            ),
        ]
        self.render_delete_meta = {
            "user": "admin",
            "deleted_at": now - timedelta(minutes=5),
        }
        self._ensure_state_db()
        self._load_or_seed_state()

    def get_session_secret(self) -> str:
        return os.getenv("SESSION_SECRET", "dev-control-plane-session-secret")

    def get_worker_shared_secret(self) -> str:
        return os.getenv("WORKER_SHARED_SECRET", "dev-worker-shared-secret")

    def get_upload_capabilities(self) -> UploadCapabilities:
        max_local_upload_bytes = int(os.getenv("MAX_LOCAL_UPLOAD_BYTES", "8589934592"))
        resumable_chunk_bytes = int(os.getenv("UPLOAD_CHUNK_BYTES", "8388608"))
        return UploadCapabilities(
            allow_local_upload=True,
            allow_resumable_upload=True,
            resumable_chunk_bytes=resumable_chunk_bytes,
            max_local_upload_bytes=max_local_upload_bytes,
        )

    @staticmethod
    def _google_oauth_scope() -> str:
        return "https://www.googleapis.com/auth/youtube.upload openid email profile"

    @staticmethod
    def _oauth_callback_path() -> str:
        return "/auth/google/callback"

    def _ensure_state_db(self) -> None:
        with sqlite3.connect(self.state_db_path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS app_state (
                    state_key TEXT PRIMARY KEY,
                    payload TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            connection.commit()

    @staticmethod
    def _serialize_value(value: Any) -> Any:
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, dict):
            return {key: AppStore._serialize_value(item) for key, item in value.items()}
        if isinstance(value, list):
            return [AppStore._serialize_value(item) for item in value]
        return value

    @staticmethod
    def _parse_datetime(value: Any) -> datetime | None:
        if value in (None, "", "-"):
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            return datetime.fromisoformat(value)
        raise ValueError(f"Unsupported datetime payload: {value!r}")

    def _serialize_state(self) -> dict[str, Any]:
        return {
            "users": [user.model_dump(mode="json") for user in self.users],
            "user_meta": self._serialize_value(self.user_meta),
            "workers": [worker.model_dump(mode="json") for worker in self.workers],
            "user_worker_links": deepcopy(self.user_worker_links),
            "channels": [channel.model_dump(mode="json") for channel in self.channels],
            "channel_user_links": deepcopy(self.channel_user_links),
            "jobs": [job.model_dump(mode="json") for job in self.jobs],
            "upload_sessions": [session.model_dump(mode="json") for session in self.upload_sessions],
            "render_delete_meta": self._serialize_value(self.render_delete_meta),
        }

    def _apply_state(self, payload: dict[str, Any]) -> None:
        self.users = [UserSummary.model_validate(item) for item in payload.get("users", [])]
        self.user_meta = {}
        for user_id, meta in (payload.get("user_meta") or {}).items():
            restored = dict(meta)
            restored["created_at"] = self._parse_datetime(restored.get("created_at"))
            restored["updated_at"] = self._parse_datetime(restored.get("updated_at"))
            self.user_meta[user_id] = restored

        self.workers = [WorkerRecord.model_validate(item) for item in payload.get("workers", [])]
        self.user_worker_links = list(payload.get("user_worker_links") or [])
        self.channels = [ChannelRecord.model_validate(item) for item in payload.get("channels", [])]
        self.channel_user_links = list(payload.get("channel_user_links") or [])
        self.jobs = [RenderJobRecord.model_validate(item) for item in payload.get("jobs", [])]
        self.upload_sessions = [UploadSessionRecord.model_validate(item) for item in payload.get("upload_sessions", [])]

        render_meta = payload.get("render_delete_meta") or {}
        self.render_delete_meta = {
            "user": render_meta.get("user") or "admin",
            "deleted_at": self._parse_datetime(render_meta.get("deleted_at"))
            or datetime.now().replace(second=0, microsecond=0),
        }

    def _save_state(self) -> None:
        payload = json.dumps(self._serialize_state(), ensure_ascii=False)
        with sqlite3.connect(self.state_db_path) as connection:
            connection.execute(
                """
                INSERT INTO app_state (state_key, payload, updated_at)
                VALUES ('main', ?, ?)
                ON CONFLICT(state_key) DO UPDATE
                SET payload = excluded.payload,
                    updated_at = excluded.updated_at
                """,
                (payload, datetime.now().isoformat()),
            )
            connection.commit()

    def _load_or_seed_state(self) -> None:
        with sqlite3.connect(self.state_db_path) as connection:
            row = connection.execute("SELECT payload FROM app_state WHERE state_key = 'main'").fetchone()
        if row and row[0]:
            self._apply_state(json.loads(row[0]))
            return
        self._save_state()

    def authenticate_admin_user(self, username: str, password: str) -> dict[str, Any]:
        normalized_username = username.strip().lower()
        normalized_password = password.strip()
        if not normalized_username or not normalized_password:
            raise ValueError("UserName va Password la bat buoc.")

        user = next((item for item in self.users if item.username.lower() == normalized_username), None)
        if not user:
            raise ValueError("Thong tin dang nhap khong hop le.")
        if user.role not in {"admin", "manager"}:
            raise ValueError("Tai khoan nay khong duoc phep vao trang quan tri.")

        meta = self._user_meta_record(user.id)
        if str(meta.get("password") or "") != normalized_password:
            raise ValueError("Thong tin dang nhap khong hop le.")

        return {
            "id": user.id,
            "username": user.username,
            "display_name": user.display_name,
            "role": user.role,
            "manager_name": user.manager_name,
        }

    def assert_admin_session_user(self, user_id: str, role: str) -> None:
        user = self._find_user(user_id)
        if user.role not in {"admin", "manager"}:
            raise ValueError("Tai khoan khong duoc phep vao trang quan tri.")
        if user.role != role:
            raise ValueError("Role session khong con hop le.")

    @staticmethod
    def _format_datetime(value: datetime | None, fmt: str = "%H:%M %d/%m/%y") -> str:
        if not value:
            return "-"
        return value.strftime(fmt)

    @staticmethod
    def _format_full_datetime(value: datetime | None) -> str:
        if not value:
            return "-"
        return value.strftime("%d/%m/%Y %H:%M:%S")

    @staticmethod
    def _format_compact_datetime(value: datetime | None) -> str:
        if not value:
            return "-"
        return value.strftime("%d/%m/%Y %H:%M")

    @staticmethod
    def _initials(label: str) -> str:
        value = (label or "?").strip()
        return value[:1].upper() if value else "?"

    @staticmethod
    def _avatar_palette(label: str) -> str:
        palettes = [
            "bg-rose-500 text-white",
            "bg-emerald-500 text-white",
            "bg-violet-500 text-white",
            "bg-sky-500 text-white",
            "bg-amber-500 text-white",
            "bg-fuchsia-500 text-white",
            "bg-cyan-500 text-white",
            "bg-orange-500 text-white",
            "bg-indigo-500 text-white",
            "bg-teal-500 text-white",
        ]
        normalized = (label or "?").strip()
        index = sum(ord(char) for char in normalized) % len(palettes)
        return palettes[index]

    @staticmethod
    def _job_status_label(status: str) -> str:
        mapping = {
            "pending": "Chờ tạo hàng đợi",
            "queueing": "Đang xếp hàng",
            "downloading": "Đang tải nguồn",
            "rendering": "Đang render",
            "uploading": "Đang upload",
            "completed": "Hoàn tất",
            "cancelled": "Đã hủy",
            "error": "Lỗi",
        }
        return mapping.get(status, status)

    @staticmethod
    def _job_status_class(status: str) -> str:
        mapping = {
            "pending": "inline-flex items-center rounded-full border border-amber-200 bg-amber-50 px-2.5 py-1 text-[10px] font-semibold text-amber-700",
            "queueing": "inline-flex items-center rounded-full border border-orange-200 bg-orange-50 px-2.5 py-1 text-[10px] font-semibold text-orange-700",
            "downloading": "inline-flex items-center rounded-full border border-sky-200 bg-sky-50 px-2.5 py-1 text-[10px] font-semibold text-sky-700",
            "rendering": "inline-flex items-center rounded-full border border-indigo-200 bg-indigo-50 px-2.5 py-1 text-[10px] font-semibold text-indigo-700",
            "uploading": "inline-flex items-center rounded-full border border-cyan-200 bg-cyan-50 px-2.5 py-1 text-[10px] font-semibold text-cyan-700",
            "completed": "inline-flex items-center rounded-full border border-emerald-200 bg-emerald-50 px-2.5 py-1 text-[10px] font-semibold text-emerald-700",
            "cancelled": "inline-flex items-center rounded-full border border-slate-200 bg-slate-100 px-2.5 py-1 text-[10px] font-semibold text-slate-700",
            "error": "inline-flex items-center rounded-full border border-rose-200 bg-rose-50 px-2.5 py-1 text-[10px] font-semibold text-rose-700",
        }
        return mapping.get(status, "inline-flex items-center rounded-full border border-slate-200 bg-slate-100 px-2.5 py-1 text-[10px] font-semibold text-slate-700")

    def _find_user(self, user_id: str) -> UserSummary:
        for user in self.users:
            if user.id == user_id:
                return user
        raise KeyError(user_id)

    def _find_worker(self, worker_id: str) -> WorkerRecord:
        for worker in self.workers:
            if worker.id == worker_id:
                return worker
        raise KeyError(worker_id)

    def _authenticate_worker(self, worker_id: str, shared_secret: str) -> WorkerRecord:
        if shared_secret != self.get_worker_shared_secret():
            raise ValueError("Worker shared secret không hợp lệ.")
        return self._find_worker(worker_id)

    def _refresh_queue_positions(self) -> None:
        queued_jobs = sorted(
            [
                job
                for job in self.jobs
                if job.status in {"pending", "queueing"} and (job.scheduled_at is None or job.scheduled_at <= datetime.now())
            ],
            key=lambda item: (item.queue_order or 10_000, item.created_at),
        )
        for index, job in enumerate(queued_jobs, start=1):
            job.queue_order = index
        for job in self.jobs:
            if job.status in {"completed", "cancelled", "error"}:
                job.queue_order = None

    def register_worker(self, payload: WorkerRegisterPayload) -> WorkerControlResponse:
        if payload.shared_secret != self.get_worker_shared_secret():
            raise ValueError("Worker shared secret không hợp lệ.")

        now = datetime.now().replace(second=0, microsecond=0)
        existing = next((worker for worker in self.workers if worker.id == payload.worker_id), None)
        manager = next((user for user in self.users if user.username == payload.manager_name and user.role == "manager"), None)
        if existing is None:
            worker = WorkerRecord(
                id=payload.worker_id,
                name=payload.name,
                manager_id=manager.id if manager else None,
                manager_name=payload.manager_name,
                group=payload.group or payload.manager_name,
                status="online",
                capacity=payload.capacity,
                load_percent=0,
                bandwidth_kbps=0,
                disk_used_gb=0,
                disk_total_gb=payload.disk_total_gb,
                threads=payload.threads,
                last_seen_at=now,
            )
            self.workers.append(worker)
        else:
            existing.name = payload.name
            existing.manager_id = manager.id if manager else existing.manager_id
            existing.manager_name = payload.manager_name
            existing.group = payload.group or payload.manager_name
            existing.capacity = payload.capacity
            existing.threads = payload.threads
            existing.disk_total_gb = payload.disk_total_gb or existing.disk_total_gb
            existing.status = "online"
            existing.last_seen_at = now
            worker = existing

        self._save_state()
        return WorkerControlResponse(ok=True, worker=deepcopy(worker))

    def heartbeat_worker(self, payload: WorkerHeartbeatPayload) -> WorkerControlResponse:
        worker = self._authenticate_worker(payload.worker_id, payload.shared_secret)
        worker.status = payload.status
        worker.load_percent = payload.load_percent
        worker.bandwidth_kbps = payload.bandwidth_kbps
        worker.disk_used_gb = payload.disk_used_gb
        worker.disk_total_gb = payload.disk_total_gb or worker.disk_total_gb
        worker.threads = payload.threads
        worker.last_seen_at = datetime.now().replace(second=0, microsecond=0)
        self._save_state()
        return WorkerControlResponse(ok=True, worker=deepcopy(worker))

    def claim_next_job(self, worker_id: str, shared_secret: str) -> tuple[WorkerRecord, RenderJobRecord | None]:
        worker = self._authenticate_worker(worker_id, shared_secret)
        now = datetime.now().replace(second=0, microsecond=0)

        for job in self.jobs:
            if job.claimed_by_worker_id == worker_id and job.status in {"queueing", "downloading", "rendering", "uploading"}:
                job.lease_expires_at = now + timedelta(minutes=5)
                self._save_state()
                worker.status = "busy"
                return deepcopy(worker), deepcopy(job)

        candidates = [
            job
            for job in self.jobs
            if job.worker_name in {worker.id, worker.name}
            and job.status in {"pending", "queueing"}
            and (job.scheduled_at is None or job.scheduled_at <= now)
            and (job.claimed_by_worker_id is None or (job.lease_expires_at and job.lease_expires_at <= now))
        ]
        candidates.sort(key=lambda item: (item.queue_order or 10_000, item.created_at))

        if not candidates:
            worker.status = "online"
            self._save_state()
            return deepcopy(worker), None

        job = candidates[0]
        job.status = "queueing"
        job.claimed_by_worker_id = worker_id
        job.claimed_at = now
        job.lease_expires_at = now + timedelta(minutes=5)
        job.started_at = job.started_at or now
        worker.status = "busy"
        self._refresh_queue_positions()
        self._save_state()
        return deepcopy(worker), deepcopy(job)

    def _find_claimed_job(self, job_id: str, worker_id: str) -> RenderJobRecord:
        for job in self.jobs:
            if job.id == job_id:
                if job.claimed_by_worker_id not in {None, worker_id} and job.status not in {"completed", "cancelled", "error"}:
                    raise ValueError("Job đang thuộc worker khác.")
                return job
        raise KeyError(job_id)

    def update_worker_job_progress(
        self,
        *,
        job_id: str,
        worker_id: str,
        shared_secret: str,
        status: str,
        progress: int,
        message: str | None = None,
    ) -> RenderJobRecord:
        worker = self._authenticate_worker(worker_id, shared_secret)
        job = self._find_claimed_job(job_id, worker_id)
        now = datetime.now().replace(second=0, microsecond=0)

        job.claimed_by_worker_id = worker_id
        job.claimed_at = job.claimed_at or now
        job.lease_expires_at = now + timedelta(minutes=5)
        job.started_at = job.started_at or now
        job.status = status  # type: ignore[assignment]
        job.progress = max(0, min(100, progress))
        if message:
            job.error_message = message
        if status == "downloading" and job.download_started_at is None:
            job.download_started_at = now
        if status == "uploading" and job.upload_started_at is None:
            job.upload_started_at = now
        if status in {"downloading", "rendering", "uploading"}:
            worker.status = "busy"

        self._save_state()
        return deepcopy(job)

    def complete_worker_job(
        self,
        *,
        job_id: str,
        worker_id: str,
        shared_secret: str,
        output_url: str | None = None,
        message: str | None = None,
    ) -> RenderJobRecord:
        worker = self._authenticate_worker(worker_id, shared_secret)
        job = self._find_claimed_job(job_id, worker_id)
        now = datetime.now().replace(second=0, microsecond=0)

        job.status = "completed"
        job.progress = 100
        job.completed_at = now
        job.can_cancel = False
        job.output_url = output_url
        job.error_message = message
        job.lease_expires_at = None
        worker.status = "online"
        self._refresh_queue_positions()
        self._save_state()
        return deepcopy(job)

    def fail_worker_job(self, *, job_id: str, worker_id: str, shared_secret: str, message: str) -> RenderJobRecord:
        worker = self._authenticate_worker(worker_id, shared_secret)
        job = self._find_claimed_job(job_id, worker_id)
        now = datetime.now().replace(second=0, microsecond=0)

        job.status = "error"
        job.completed_at = now
        job.can_cancel = False
        job.error_message = message
        job.lease_expires_at = None
        worker.status = "online"
        self._refresh_queue_positions()
        self._save_state()
        return deepcopy(job)

    def _find_channel(self, channel_id: str) -> ChannelRecord:
        for channel in self.channels:
            if channel.id == channel_id:
                return channel
        raise KeyError(channel_id)

    def _current_app_user(self) -> UserSummary:
        for user in self.users:
            if user.role == "user":
                return user
        return self.users[-1]

    def _pick_worker_for_user(self, user: UserSummary) -> WorkerRecord:
        linked_worker_ids = [link["worker_id"] for link in self.user_worker_links if link["user_id"] == user.id]
        if linked_worker_ids:
            return self._find_worker(linked_worker_ids[0])
        if self.workers:
            return self.workers[0]
        raise ValueError("Chua co BOT nao de gan cho kenh OAuth.")

    def _ensure_channel_user_link(self, *, channel_id: str, user_id: str) -> None:
        exists = next(
            (
                link
                for link in self.channel_user_links
                if link["channel_id"] == channel_id and link["user_id"] == user_id
            ),
            None,
        )
        if exists:
            return

        next_id = max([item["id"] for item in self.channel_user_links], default=0) + 1
        self.channel_user_links.append({"id": next_id, "channel_id": channel_id, "user_id": user_id})

    def _user_meta_record(self, user_id: str) -> dict[str, Any]:
        return self.user_meta.setdefault(
            user_id,
            {
                "password": "",
                "telegram": "",
                "updated_by": "system",
                "updated_at": None,
                "created_at": datetime.now().replace(second=0, microsecond=0),
            },
        )

    def _admin_nav_items(self) -> list[dict[str, str]]:
        return [
            {"key": "users", "label": "Người dùng", "href": "/admin/user/index", "icon": "users"},
            {"key": "workers", "label": "Danh sách BOT", "href": "/admin/ManagerBOT/index", "icon": "server"},
            {"key": "channels", "label": "Danh sách Kênh", "href": "/admin/channel/index", "icon": "link"},
            {"key": "renders", "label": "Danh sách Render", "href": "/admin/render/index", "icon": "video"},
        ]

    def _user_section_tabs(self, active_key: str) -> list[dict[str, str | bool]]:
        tabs = [
            {"key": "users", "label": "Danh sách user", "href": "/admin/user/index"},
            {"key": "create", "label": "Tạo user", "href": "/admin/user/create"},
            {"key": "managers", "label": "Manager", "href": "/admin/user/manager"},
            {"key": "admins", "label": "Admin", "href": "/admin/user/admins"},
        ]
        for item in tabs:
            item["active"] = item["key"] == active_key
        return tabs

    def _selected_manager_ids(self, manager_ids: list[str] | None) -> list[str]:
        available_ids = [user.id for user in self.users if user.role == "manager"]
        if not manager_ids:
            return available_ids
        return [manager_id for manager_id in manager_ids if manager_id in available_ids]

    def _manager_options(self, selected_ids: list[str] | None = None) -> list[dict[str, str | bool]]:
        selected_set = set(selected_ids or [user.id for user in self.users if user.role == "manager"])
        return [
            {
                "id": user.id,
                "username": user.username,
                "display_name": user.display_name,
                "initials": self._initials(user.display_name or user.username),
                "avatar_class": self._avatar_palette(user.display_name or user.username),
                "selected": user.id in selected_set,
            }
            for user in self.users
            if user.role == "manager"
        ]

    def _filtered_workers(self, manager_ids: list[str] | None = None) -> list[WorkerRecord]:
        selected_ids = set(self._selected_manager_ids(manager_ids))
        if not selected_ids:
            return list(self.workers)
        return [worker for worker in self.workers if worker.manager_id in selected_ids]

    def _admin_shell_context(
        self,
        *,
        page_title: str,
        active_page: str,
        user_section: str | None = None,
        manager_ids: list[str] | None = None,
        notice: str | None = None,
        notice_level: str = "success",
    ) -> dict[str, Any]:
        selected_manager_ids = self._selected_manager_ids(manager_ids)
        context = {
            "page_title": page_title,
            "active_page": active_page,
            "nav_items": self._admin_nav_items(),
            "summary_strip": self._summary_strip(),
            "summary": self.get_admin_dashboard().summary,
            "current_user": {"name": "Admin", "avatar": "/admin-themes/assets/img/avatar/avatar-1.png"},
            "manager_options": self._manager_options(selected_manager_ids),
            "selected_manager_ids": selected_manager_ids,
            "notice": notice,
            "notice_level": notice_level,
        }
        if user_section:
            context["user_tabs"] = self._user_section_tabs(user_section)
            context["user_section"] = user_section
        return context

    def _role_badge(self, role: str) -> tuple[str, str]:
        mapping = {
            "admin": ("Admin", "inline-flex items-center rounded-full border border-rose-200 bg-rose-50 px-2.5 py-1 text-[10px] font-semibold text-rose-700"),
            "manager": ("Manager", "inline-flex items-center rounded-full border border-amber-200 bg-amber-50 px-2.5 py-1 text-[10px] font-semibold text-amber-700"),
            "user": ("User", "inline-flex items-center rounded-full border border-emerald-200 bg-emerald-50 px-2.5 py-1 text-[10px] font-semibold text-emerald-700"),
        }
        return mapping.get(role, (role, "inline-flex items-center rounded-full border border-slate-200 bg-slate-100 px-2.5 py-1 text-[10px] font-semibold text-slate-700"))

    def _worker_status_badge(self, status: str) -> tuple[str, str]:
        mapping = {
            "online": ("Connected", "inline-flex items-center rounded-full border border-emerald-200 bg-emerald-50 px-2.5 py-1 text-[10px] font-semibold text-emerald-700"),
            "busy": ("Busy", "inline-flex items-center rounded-full border border-sky-200 bg-sky-50 px-2.5 py-1 text-[10px] font-semibold text-sky-700"),
            "offline": ("Disconnected", "inline-flex items-center rounded-full border border-rose-200 bg-rose-50 px-2.5 py-1 text-[10px] font-semibold text-rose-700"),
        }
        return mapping.get(status, (status, "inline-flex items-center rounded-full border border-slate-200 bg-slate-100 px-2.5 py-1 text-[10px] font-semibold text-slate-700"))

    def _channel_status_badge(self, status: str) -> tuple[str, str]:
        mapping = {
            "connected": ("Connected", "inline-flex items-center rounded-full border border-emerald-200 bg-emerald-50 px-2.5 py-1 text-[10px] font-semibold text-emerald-700"),
            "pending_reconnect": ("Pending reconnect", "inline-flex items-center rounded-full border border-amber-200 bg-amber-50 px-2.5 py-1 text-[10px] font-semibold text-amber-700"),
            "disconnected": ("Disconnected", "inline-flex items-center rounded-full border border-rose-200 bg-rose-50 px-2.5 py-1 text-[10px] font-semibold text-rose-700"),
        }
        return mapping.get(status, (status, "inline-flex items-center rounded-full border border-slate-200 bg-slate-100 px-2.5 py-1 text-[10px] font-semibold text-slate-700"))

    def _render_status_badge(self, job: RenderJobRecord) -> tuple[str, str]:
        mapping = {
            "pending": ("Pending", "inline-flex items-center rounded-full border border-amber-200 bg-amber-50 px-2.5 py-1 text-[10px] font-semibold text-amber-700"),
            "queueing": ("Queueing", "inline-flex items-center rounded-full border border-orange-200 bg-orange-50 px-2.5 py-1 text-[10px] font-semibold text-orange-700"),
            "downloading": (f"Downloading ({job.progress}%)", "inline-flex items-center rounded-full border border-sky-200 bg-sky-50 px-2.5 py-1 text-[10px] font-semibold text-sky-700"),
            "rendering": (f"Rendering ({job.progress}%)", "inline-flex items-center rounded-full border border-indigo-200 bg-indigo-50 px-2.5 py-1 text-[10px] font-semibold text-indigo-700"),
            "uploading": (f"Uploading ({job.progress}%)", "inline-flex items-center rounded-full border border-cyan-200 bg-cyan-50 px-2.5 py-1 text-[10px] font-semibold text-cyan-700"),
            "completed": ("Completed", "inline-flex items-center rounded-full border border-emerald-200 bg-emerald-50 px-2.5 py-1 text-[10px] font-semibold text-emerald-700"),
            "cancelled": ("Cancelled", "inline-flex items-center rounded-full border border-slate-200 bg-slate-100 px-2.5 py-1 text-[10px] font-semibold text-slate-700"),
            "error": ("Error", "inline-flex items-center rounded-full border border-rose-200 bg-rose-50 px-2.5 py-1 text-[10px] font-semibold text-rose-700"),
        }
        return mapping.get(job.status, (job.status, "inline-flex items-center rounded-full border border-slate-200 bg-slate-100 px-2.5 py-1 text-[10px] font-semibold text-slate-700"))

    def _summary_strip(self) -> list[dict[str, str]]:
        summary = self.get_admin_dashboard().summary
        uploading_count = len([job for job in self.jobs if job.status == "uploading"])
        return [
            {
                "value": str(summary.channels_connected),
                "label": "Tổng Số Kênh",
                "icon": "radio",
                "icon_class": "text-emerald-500",
                "accent": "Online",
                "accent_class": "text-emerald-600",
                "accent_badge_class": "border-emerald-200 bg-emerald-50 text-emerald-700",
                "value_class": "text-emerald-600",
                "bar_color": "#10b981",
            },
            {
                "value": f"{summary.workers_online}/{summary.total_workers}",
                "label": "BOT Đang Chạy",
                "icon": "server",
                "icon_class": "text-brand-500",
                "accent": "Active",
                "accent_class": "text-brand-600",
                "accent_badge_class": "border-brand-100 bg-brand-50 text-brand-700",
                "value_class": "text-brand-600",
                "bar_color": "#6366f1",
            },
            {
                "value": str(summary.total_users),
                "label": "Tổng User",
                "icon": "users",
                "icon_class": "text-rose-500",
                "accent": "Accounts",
                "accent_class": "text-rose-500",
                "accent_badge_class": "border-rose-200 bg-rose-50 text-rose-700",
                "value_class": "text-slate-900",
                "bar_color": "#f43f5e",
            },
            {
                "value": str(summary.running_jobs),
                "label": "Đang Render",
                "icon": "loader",
                "icon_class": "text-brand-500",
                "accent": "Render",
                "accent_class": "text-brand-600",
                "accent_badge_class": "border-indigo-200 bg-indigo-50 text-indigo-700",
                "value_class": "text-brand-600",
                "bar_color": "#5d67df",
            },
            {
                "value": str(uploading_count),
                "label": "Đang Upload",
                "icon": "cloud-upload",
                "icon_class": "text-sky-500",
                "accent": "Upload",
                "accent_class": "text-sky-500",
                "accent_badge_class": "border-sky-200 bg-sky-50 text-sky-700",
                "value_class": "text-slate-900" if uploading_count == 0 else "text-sky-500",
                "bar_color": "#0284c7",
            },
            {
                "value": str(summary.queued_jobs),
                "label": "Job Đang Chờ",
                "icon": "layers",
                "icon_class": "text-amber-500",
                "accent": "Queue",
                "accent_class": "text-amber-600",
                "accent_badge_class": "border-amber-200 bg-amber-50 text-amber-700",
                "value_class": "text-amber-600",
                "bar_color": "#f59e0b",
            },
        ]

    def _user_worker_count(self, user: UserSummary) -> int:
        if user.role == "manager":
            return len([worker for worker in self.workers if worker.manager_name == user.username])
        if user.role == "admin":
            return len(self.workers)
        return len([link for link in self.user_worker_links if link["user_id"] == user.id])

    def _user_channel_count(self, user: UserSummary) -> int:
        if user.role == "manager":
            return len([channel for channel in self.channels if channel.manager_name == user.username])
        if user.role == "admin":
            return len(self.channels)
        return len([link for link in self.channel_user_links if link["user_id"] == user.id])

    def _channel_users(self, channel: ChannelRecord) -> list[str]:
        assigned_ids = [link["user_id"] for link in self.channel_user_links if link["channel_id"] == channel.id]
        assigned = []
        for user_id in assigned_ids:
            try:
                assigned.append(self._find_user(user_id).display_name)
            except KeyError:
                continue
        return assigned

    def _channel_user_count(self, channel_id: str) -> int:
        return len([link for link in self.channel_user_links if link["channel_id"] == channel_id])

    def _channel_link(self, channel: ChannelRecord) -> str:
        return f"https://www.youtube.com/channel/{channel.channel_id}"

    def _find_job(self, job_id: str) -> RenderJobRecord:
        for job in self.jobs:
            if job.id == job_id:
                return job
        raise KeyError(job_id)

    def _job_username(self, job: RenderJobRecord) -> str:
        user_ids = [link["user_id"] for link in self.channel_user_links if link["channel_id"] == job.channel_id]
        if user_ids:
            try:
                return self._find_user(user_ids[0]).username
            except KeyError:
                pass
        return "demo-user"

    def get_user_dashboard_view(
        self,
        *,
        notice: str | None = None,
        notice_level: str = "success",
    ) -> dict[str, Any]:
        bootstrap = self.get_user_bootstrap()
        jobs_response = self.get_user_jobs()
        now = datetime.now().replace(second=0, microsecond=0)

        queued_jobs = [job for job in jobs_response.jobs if job.status in {"pending", "queueing"}]
        rendering_jobs = [job for job in jobs_response.jobs if job.status == "rendering"]
        uploading_jobs = [job for job in jobs_response.jobs if job.status == "uploading"]
        failed_jobs = [job for job in jobs_response.jobs if job.status in {"cancelled", "error"}]

        channels = [
            {"value": "", "label": "-- Chọn kênh --", "meta": "", "avatar": "", "avatar_class": "", "is_active": True, "is_placeholder": True}
        ]
        for channel in bootstrap.channels:
            channels.append(
                {
                    "value": channel.id,
                    "label": channel.name,
                    "meta": channel.channel_id,
                    "avatar": self._initials(channel.name),
                    "avatar_class": "bg-emerald-800 text-white",
                    "is_active": False,
                    "is_placeholder": False,
                }
            )

        connected_channels: list[dict[str, Any]] = []
        for channel in bootstrap.channels:
            connected_channels.append(
                {
                    "id": channel.id,
                    "title": channel.name,
                    "meta": f"{channel.channel_id} • {channel.worker_name}",
                    "avatar": self._initials(channel.name),
                    "avatar_class": "bg-emerald-800 text-white",
                    "avatar_small": False,
                }
            )

        render_jobs: list[dict[str, Any]] = []
        for index, job in enumerate(jobs_response.jobs, start=1):
            is_drive = job.source_mode == "drive"
            render_jobs.append(
                {
                    "id": job.id,
                    "index": index,
                    "kind": "Drive" if is_drive else "Upload",
                    "kind_class": "text-sky-600" if is_drive else "text-violet-600",
                    "title": job.title,
                    "meta": f"{job.source_label} • render {job.time_render_string} • ",
                    "job_id": job.id,
                    "description": job.description or "Job đã vào hàng đợi xử lý và đang chờ worker VPS nhận việc.",
                    "channel_avatar": self._initials(job.channel_name),
                    "channel_name": job.channel_name,
                    "queue_label": f"Queue #{job.queue_order}" if job.queue_order else "Chưa xếp hàng",
                    "bot": job.worker_name or "-",
                    "owner": job.manager_name or "-",
                    "progress": f"{job.progress}%",
                    "created_at": self._format_datetime(job.created_at),
                    "uploaded_at": self._format_datetime(job.upload_started_at),
                    "status": self._job_status_label(job.status),
                    "status_class": self._job_status_class(job.status),
                    "icon": "hard-drive-download" if is_drive else None,
                    "icon_class": "text-sky-600",
                    "preview_text": (job.source_file_name or "Preview")[:16],
                    "can_cancel": job.can_cancel,
                }
            )

        return {
            "page_title": "Youtube Upload Lush",
            "app_name": "Youtube Upload Lush",
            "workspace_label": "User workspace",
            "user_name": bootstrap.user.display_name,
            "user_role": bootstrap.user.manager_name or bootstrap.user.role,
            "upload_capabilities": bootstrap.upload_capabilities.model_dump(mode="json"),
            "notice": notice,
            "notice_level": notice_level,
            "kpis": [
                {"label": "Kênh đã thêm", "icon": "radio", "icon_class": "text-emerald-500", "value": bootstrap.oauth.connected_count, "accent": "Online", "accent_class": "text-emerald-600", "accent_badge_class": "border-emerald-200 bg-emerald-50 text-emerald-700", "value_class": "text-emerald-600", "bar_class": "bg-emerald-500"},
                {"label": "Đang chờ xử lý", "icon": "layers", "icon_class": "text-amber-500", "value": len(queued_jobs), "accent": "Chờ", "accent_class": "text-amber-600", "accent_badge_class": "border-amber-200 bg-amber-50 text-amber-700", "value_class": "text-amber-600", "bar_class": "bg-amber-500"},
                {"label": "Đang render", "icon": "loader", "icon_class": "text-brand-500", "value": len(rendering_jobs), "accent": "Render", "accent_class": "text-brand-600", "accent_badge_class": "border-indigo-200 bg-indigo-50 text-indigo-700", "value_class": "text-brand-600", "bar_class": "bg-brand-500"},
                {"label": "Đang upload", "icon": "cloud-upload", "icon_class": "text-sky-500", "value": len(uploading_jobs), "accent": "Upload", "accent_class": "text-sky-500", "accent_badge_class": "border-sky-200 bg-sky-50 text-sky-700", "value_class": "text-slate-900" if len(uploading_jobs) == 0 else "text-sky-500", "bar_class": "bg-sky-400"},
                {"label": "Xử lý lỗi", "icon": "shield-alert", "icon_class": "text-rose-500", "value": len(failed_jobs), "accent": "Lỗi", "accent_class": "text-rose-500", "accent_badge_class": "border-rose-200 bg-rose-50 text-rose-700", "value_class": "text-slate-900" if len(failed_jobs) == 0 else "text-rose-500", "bar_class": "bg-rose-400"},
            ],
            "render_config": {"title": "Cấu hình render", "description": "Thiết lập nguồn đầu vào, file loop và kênh xuất bản cho job mới."},
            "quick_settings": {"video_title": "", "description_text": "", "duration": "03:30:00", "schedule_at": (now + timedelta(hours=1)).strftime("%d/%m/%Y %H:%M")},
            "channels": channels,
            "connected_channels": connected_channels,
            "render_tabs": [
                {"label": "Danh sách render", "count": len(render_jobs), "active": True},
                {"label": "Đang xử lý", "count": len([job for job in render_jobs if job["status"] in {"Đang render", "Đang upload", "Đang tải nguồn"}]), "active": False},
            ],
            "render_jobs": render_jobs,
            "render_summary": f"Hiển thị 1 đến {len(render_jobs)} trong số {len(render_jobs)} kết quả" if render_jobs else "Chưa có job nào trong hàng đợi",
        }

    def get_user_bootstrap(self) -> UserBootstrapResponse:
        user = deepcopy(self._current_app_user())
        assigned_channel_ids = {link["channel_id"] for link in self.channel_user_links if link["user_id"] == user.id}
        channels = deepcopy([channel for channel in self.channels if channel.id in assigned_channel_ids])
        connected_count = len([channel for channel in channels if channel.status == "connected"])
        reconnect_count = len([channel for channel in channels if channel.status != "connected"])
        return UserBootstrapResponse(
            user=user,
            channels=channels,
            upload_capabilities=self.get_upload_capabilities(),
            oauth=OAuthSummary(connected_count=connected_count, needs_reconnect_count=reconnect_count),
        )

    def get_user_jobs(self) -> UserJobsResponse:
        jobs = sorted(deepcopy(self.jobs), key=lambda item: item.created_at, reverse=True)
        return UserJobsResponse(jobs=jobs)

    def create_job(self, payload: JobCreatePayload, source_file_names: dict[str, str | None]) -> RenderJobRecord:
        channel = next(channel for channel in self.channels if channel.id == payload.channel_id)
        queue_order = max([job.queue_order or 0 for job in self.jobs], default=0) + 1
        created_at = datetime.now().replace(second=0, microsecond=0)

        resolved_file_names = {
            "intro": source_file_names.get("intro") or self.consume_uploaded_asset(payload.intro_asset_id),
            "video_loop": source_file_names.get("video_loop") or self.consume_uploaded_asset(payload.video_loop_asset_id),
            "audio_loop": source_file_names.get("audio_loop") or self.consume_uploaded_asset(payload.audio_loop_asset_id),
            "outro": source_file_names.get("outro") or self.consume_uploaded_asset(payload.outro_asset_id),
        }

        assets = [
            JobAsset(
                slot="intro",
                label="Intro",
                source_mode="local" if resolved_file_names.get("intro") else "drive",
                url=payload.intro_url,
                file_name=resolved_file_names.get("intro"),
            ),
            JobAsset(
                slot="video_loop",
                label="Video loop",
                source_mode="local" if resolved_file_names.get("video_loop") else "drive",
                url=payload.video_loop_url,
                file_name=resolved_file_names.get("video_loop"),
            ),
            JobAsset(
                slot="audio_loop",
                label="Audio loop",
                source_mode="local" if resolved_file_names.get("audio_loop") else "drive",
                url=payload.audio_loop_url,
                file_name=resolved_file_names.get("audio_loop"),
            ),
            JobAsset(
                slot="outro",
                label="Outro",
                source_mode="local" if resolved_file_names.get("outro") else "drive",
                url=payload.outro_url,
                file_name=resolved_file_names.get("outro"),
            ),
        ]

        has_local_asset = any(item["file_name"] for item in [
            {"file_name": resolved_file_names.get("intro")},
            {"file_name": resolved_file_names.get("video_loop")},
            {"file_name": resolved_file_names.get("audio_loop")},
            {"file_name": resolved_file_names.get("outro")},
        ])

        job = RenderJobRecord(
            id=f"job-{uuid4().hex[:8]}",
            title=payload.title,
            description=payload.description,
            source_mode="local" if has_local_asset else "drive",
            channel_id=channel.id,
            channel_name=channel.name,
            channel_avatar_url=channel.avatar_url,
            worker_name=channel.worker_name,
            manager_name=channel.manager_name,
            status="pending",
            progress=0,
            queue_order=queue_order,
            time_render_string=payload.time_render_string,
            scheduled_at=payload.schedule_time,
            created_at=created_at,
            source_label="Local Upload" if has_local_asset else "Google Drive/cloud",
            source_file_name=resolved_file_names.get("video_loop"),
            thumbnail_url=None,
            assets=[asset for asset in assets if asset.url or asset.file_name],
        )
        self.jobs.append(job)
        self._refresh_queue_positions()
        self._save_state()
        return deepcopy(job)

    def cancel_job(self, job_id: str) -> RenderJobRecord:
        for job in self.jobs:
            if job.id == job_id:
                if job.status not in {"completed", "cancelled", "error"}:
                    job.status = "cancelled"
                    job.can_cancel = False
                    job.completed_at = datetime.now().replace(second=0, microsecond=0)
                    job.lease_expires_at = None
                    self._refresh_queue_positions()
                    self._save_state()
                return deepcopy(job)
        raise KeyError(job_id)

    def delete_job(self, job_id: str) -> None:
        for index, job in enumerate(self.jobs):
            if job.id == job_id:
                self.jobs.pop(index)
                self._refresh_queue_positions()
                self._save_state()
                return
        raise KeyError(job_id)

    def delete_all_jobs(self, deleted_by: str = "admin") -> None:
        self.jobs = []
        self.render_delete_meta = {
            "user": deleted_by,
            "deleted_at": datetime.now().replace(second=0, microsecond=0),
        }
        self._save_state()

    def get_admin_dashboard(self) -> AdminDashboardResponse:
        queued = len([job for job in self.jobs if job.status in {"pending", "queueing"}])
        running = len([job for job in self.jobs if job.status in {"downloading", "rendering", "uploading"}])
        failed = len([job for job in self.jobs if job.status in {"cancelled", "error"}])
        workers_online = len([worker for worker in self.workers if worker.status in {"online", "busy"}])
        summary = AdminSummary(
            total_managers=len([user for user in self.users if user.role == "manager"]),
            total_users=len([user for user in self.users if user.role == "user"]),
            total_workers=len(self.workers),
            workers_online=workers_online,
            channels_connected=len([channel for channel in self.channels if channel.status == "connected"]),
            queued_jobs=queued,
            running_jobs=running,
            failed_jobs=failed,
        )
        return AdminDashboardResponse(
            summary=summary,
            users=deepcopy(self.users),
            workers=deepcopy(self.workers),
            channels=deepcopy(self.channels),
            jobs=deepcopy(self.jobs),
        )

    def _build_user_rows(self, manager_ids: list[str] | None = None) -> list[dict[str, Any]]:
        selected_manager_ids = set(self._selected_manager_ids(manager_ids))
        rows: list[dict[str, Any]] = []
        managers_by_username = {user.username: user for user in self.users if user.role == "manager"}

        for user in self.users:
            include_row = True
            if selected_manager_ids:
                if user.role == "manager":
                    include_row = user.id in selected_manager_ids
                elif user.role == "user":
                    manager = managers_by_username.get(user.manager_name or "")
                    include_row = bool(manager and manager.id in selected_manager_ids)

            if not include_row:
                continue

            role_label, role_class = self._role_badge(user.role)
            meta = self._user_meta_record(user.id)
            manager = managers_by_username.get(user.manager_name or "")
            rows.append(
                {
                    "index": len(rows) + 1,
                    "id": user.id,
                    "username": user.username,
                    "display_name": user.display_name,
                    "avatar_initials": self._initials(user.display_name or user.username),
                    "avatar_class": self._avatar_palette(user.display_name or user.username),
                    "role": user.role,
                    "role_label": role_label,
                    "role_class": role_class,
                    "manager_name": user.manager_name or "-",
                    "manager_id": manager.id if manager else "",
                    "telegram": meta.get("telegram") or "",
                    "updated_meta": f"{meta.get('updated_by') or '-'} • {self._format_compact_datetime(meta.get('updated_at'))}",
                    "total_channels": self._user_channel_count(user),
                    "total_workers": self._user_worker_count(user),
                }
            )
        return rows

    def _build_role_page_context(
        self,
        *,
        role_kind: str,
        notice: str | None = None,
        notice_level: str = "success",
    ) -> dict[str, Any]:
        is_manager = role_kind == "manager"
        current_role = "manager" if is_manager else "admin"
        rows = []
        for user in self.users:
            if user.role != current_role:
                continue
            meta = self._user_meta_record(user.id)
            rows.append(
                {
                    "index": len(rows) + 1,
                    "id": user.id,
                    "username": user.username,
                    "display_name": user.display_name,
                    "password": meta.get("password") or "-",
                    "updated_meta": f"{meta.get('updated_by') or '-'} • {self._format_compact_datetime(meta.get('updated_at'))}",
                }
            )

        context = self._admin_shell_context(
            page_title="Danh sách manager" if is_manager else "Danh sách admin",
            active_page="users",
            user_section="managers" if is_manager else "admins",
            notice=notice,
            notice_level=notice_level,
        )
        context.update(
            {
                "template": "admin/user_role_list.html",
                "page_kind": role_kind,
                "heading": "Danh sách manager" if is_manager else "Danh sách admin",
                "role_label": "manager" if is_manager else "admin",
                "title": "Danh sách manager" if is_manager else "Danh sách admin",
                "description": "Bổ nhiệm hoặc gỡ quyền manager cho tài khoản." if is_manager else "Bổ nhiệm hoặc gỡ quyền admin cho tài khoản.",
                "action_route": "/admin/user/updaterolemanager" if is_manager else "/admin/user/updateroleadmin",
                "rows": rows,
            }
        )
        return context

    def _build_user_bot_links(self, user_id: str) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for mapping in self.user_worker_links:
            if mapping["user_id"] != user_id:
                continue
            worker = self._find_worker(mapping["worker_id"])
            status_label, status_class = self._worker_status_badge(worker.status)
            rows.append(
                {
                    "index": len(rows) + 1,
                    "id": mapping["id"],
                    "worker_id": worker.id,
                    "worker_name": worker.name.replace("worker", "BOT"),
                    "manager_name": worker.manager_name,
                    "status_label": status_label,
                    "status_class": status_class,
                    "bot_type": mapping.get("bot_type", "1080p"),
                    "number_of_threads": mapping["threads"],
                    "note": mapping["note"],
                    "disk_text": f"{worker.disk_used_gb:.1f}GB / {worker.disk_total_gb:.1f}GB",
                    "bandwidth_text": f"{worker.bandwidth_kbps:,.0f} KB/s",
                }
            )
        return rows

    def get_admin_user_index_context(
        self,
        *,
        manager_ids: list[str] | None = None,
        notice: str | None = None,
        notice_level: str = "success",
    ) -> dict[str, Any]:
        context = self._admin_shell_context(
            page_title="Danh sách người dùng",
            active_page="users",
            user_section="users",
            manager_ids=manager_ids,
            notice=notice,
            notice_level=notice_level,
        )
        context.update(
            {
                "template": "admin/user_index.html",
                "users": self._build_user_rows(manager_ids),
                "manager_form_options": [{"id": user.id, "label": user.username} for user in self.users if user.role == "manager"],
            }
        )
        return context

    def get_admin_user_create_context(
        self,
        *,
        notice: str | None = None,
        notice_level: str = "success",
        form_data: dict[str, Any] | None = None,
        error: str | None = None,
    ) -> dict[str, Any]:
        context = self._admin_shell_context(
            page_title="Tạo user",
            active_page="users",
            user_section="create",
            notice=notice,
            notice_level=notice_level,
        )
        context.update(
            {
                "template": "admin/user_create.html",
                "form": form_data
                or {
                    "username": "",
                    "password": "",
                    "manager_id": "",
                },
                "error": error,
                "manager_candidates": [{"id": user.id, "username": user.username} for user in self.users if user.role == "manager"],
            }
        )
        return context

    def get_admin_user_edit_context(
        self,
        *,
        user_id: str,
        notice: str | None = None,
        notice_level: str = "success",
        error: str | None = None,
    ) -> dict[str, Any]:
        user = self._find_user(user_id)
        meta = self._user_meta_record(user.id)
        manager = next((item for item in self.users if item.username == user.manager_name), None)
        context = self._admin_shell_context(
            page_title="Cập nhật user",
            active_page="users",
            user_section="users",
            notice=notice,
            notice_level=notice_level,
        )
        context.update(
            {
                "template": "admin/user_edit.html",
                "error": error,
                "manager_candidates": [{"id": item.id, "username": item.username} for item in self.users if item.role == "manager"],
                "user_record": {
                    "id": user.id,
                    "username": user.username,
                    "display_name": user.display_name,
                    "role": user.role,
                    "manager_id": manager.id if manager else "",
                    "link_telegram": meta.get("telegram") or "",
                },
            }
        )
        return context

    def get_admin_user_reset_context(
        self,
        *,
        user_id: str,
        notice: str | None = None,
        notice_level: str = "success",
        error: str | None = None,
    ) -> dict[str, Any]:
        user = self._find_user(user_id)
        context = self._admin_shell_context(
            page_title="Reset password",
            active_page="users",
            user_section="users",
            notice=notice,
            notice_level=notice_level,
        )
        context.update(
            {
                "template": "admin/user_reset_password.html",
                "error": error,
                "user_record": {
                    "id": user.id,
                    "username": user.username,
                },
            }
        )
        return context

    def get_admin_manager_page_context(self, *, notice: str | None = None, notice_level: str = "success") -> dict[str, Any]:
        return self._build_role_page_context(role_kind="manager", notice=notice, notice_level=notice_level)

    def get_admin_admin_page_context(self, *, notice: str | None = None, notice_level: str = "success") -> dict[str, Any]:
        return self._build_role_page_context(role_kind="admin", notice=notice, notice_level=notice_level)

    def get_admin_user_bot_context(
        self,
        *,
        user_id: str,
        notice: str | None = None,
        notice_level: str = "success",
    ) -> dict[str, Any]:
        user = self._find_user(user_id)
        meta = self._user_meta_record(user.id)
        context = self._admin_shell_context(
            page_title=f"Gán BOT cho {user.username}",
            active_page="users",
            user_section="users",
            notice=notice,
            notice_level=notice_level,
        )
        context.update(
            {
                "template": "admin/user_manager_bot.html",
                "target_user": {
                    "id": user.id,
                    "username": user.username,
                    "display_name": user.display_name,
                    "manager_name": user.manager_name or "-",
                    "telegram": meta.get("telegram") or "-",
                },
                "user_record": {
                    "id": user.id,
                    "username": user.username,
                    "display_name": user.display_name,
                    "manager_name": user.manager_name or "-",
                    "link_telegram": meta.get("telegram") or "-",
                },
                "rows": self._build_user_bot_links(user.id),
                "worker_candidates": [{"id": worker.id, "name": worker.name.replace('worker', 'BOT')} for worker in self.workers],
            }
        )
        return context

    def _build_bot_rows(self, manager_ids: list[str] | None = None) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for index, worker in enumerate(self._filtered_workers(manager_ids), start=1):
            status_label, status_class = self._worker_status_badge(worker.status)
            rows.append(
                {
                    "index": index,
                    "id": worker.id,
                    "bot_id": worker.id.replace("worker", "BOT"),
                    "manager_id": worker.manager_id or "",
                    "manager_name": worker.manager_name,
                    "name": worker.name.replace("worker", "BOT"),
                    "raw_name": worker.name,
                    "group": worker.group or worker.manager_name,
                    "status_label": status_label,
                    "status_class": status_class,
                    "created_at": self._format_full_datetime(worker.last_seen_at),
                    "total_channels": len([channel for channel in self.channels if channel.worker_id == worker.id]),
                    "total_users": len([link for link in self.user_worker_links if link["worker_id"] == worker.id]),
                    "thread_text": f"{worker.threads}/{worker.capacity}",
                    "threads": worker.threads,
                    "disk_text": f"{worker.disk_used_gb:.1f}GB / {worker.disk_total_gb:.1f}GB",
                    "bandwidth_text": f"{worker.bandwidth_kbps:,.2f} KB/s",
                    "load_percent": worker.load_percent,
                }
            )
        return rows

    def get_admin_bot_index_context(
        self,
        *,
        manager_ids: list[str] | None = None,
        notice: str | None = None,
        notice_level: str = "success",
    ) -> dict[str, Any]:
        context = self._admin_shell_context(
            page_title="Danh sách BOT",
            active_page="workers",
            manager_ids=manager_ids,
            notice=notice,
            notice_level=notice_level,
        )
        context.update(
            {
                "template": "admin/worker_index.html",
                "workers": self._build_bot_rows(manager_ids),
            }
        )
        return context

    def get_admin_bots_of_user_context(
        self,
        *,
        user_id: str,
        notice: str | None = None,
        notice_level: str = "success",
    ) -> dict[str, Any]:
        user = self._find_user(user_id)
        if user.role == "user":
            worker_ids = [link["worker_id"] for link in self.user_worker_links if link["user_id"] == user.id]
            worker_source = [self._find_worker(worker_id) for worker_id in worker_ids]
        elif user.role == "manager":
            worker_source = [worker for worker in self.workers if worker.manager_name == user.username]
        else:
            worker_source = list(self.workers)

        rows = []
        for index, worker in enumerate(worker_source, start=1):
            status_label, status_class = self._worker_status_badge(worker.status)
            rows.append(
                {
                    "index": index,
                    "id": worker.id,
                    "bot_id": worker.id.replace("worker", "BOT"),
                    "name": worker.name.replace("worker", "BOT"),
                    "group": worker.group or worker.manager_name,
                    "status_label": status_label,
                    "status_class": status_class,
                    "created_at": self._format_full_datetime(worker.last_seen_at),
                    "total_channels": len([channel for channel in self.channels if channel.worker_id == worker.id]),
                    "total_users": len([link for link in self.user_worker_links if link["worker_id"] == worker.id]),
                    "threads": worker.threads,
                    "disk_text": f"{worker.disk_used_gb:.1f}GB / {worker.disk_total_gb:.1f}GB",
                    "bandwidth_text": f"{worker.bandwidth_kbps:,.2f} KB/s",
                }
            )

        context = self._admin_shell_context(
            page_title=f"Danh sách BOT của {user.username}",
            active_page="workers",
            notice=notice,
            notice_level=notice_level,
        )
        context.update(
            {
                "template": "admin/bot_of_user.html",
                "target_user": {
                    "id": user.id,
                    "username": user.username,
                    "display_name": user.display_name,
                },
                "workers": rows,
            }
        )
        return context

    def get_admin_users_of_bot_context(
        self,
        *,
        worker_id: str,
        notice: str | None = None,
        notice_level: str = "success",
    ) -> dict[str, Any]:
        worker = self._find_worker(worker_id)
        assigned_ids = [link["user_id"] for link in self.user_worker_links if link["worker_id"] == worker.id]
        rows = []
        for index, user_id in enumerate(assigned_ids, start=1):
            user = self._find_user(user_id)
            rows.append(
                {
                    "index": index,
                    "id": user.id,
                    "username": user.username,
                    "display_name": user.display_name,
                    "total_channels": self._user_channel_count(user),
                    "total_bots": self._user_worker_count(user),
                }
            )

        context = self._admin_shell_context(
            page_title=f"Danh sách user của {worker.name.replace('worker', 'BOT')}",
            active_page="workers",
            notice=notice,
            notice_level=notice_level,
        )
        context.update(
            {
                "template": "admin/user_of_bot.html",
                "target_bot": {
                    "id": worker.id,
                    "name": worker.name.replace("worker", "BOT"),
                },
                "users": rows,
            }
        )
        return context

    def create_admin_user(
        self,
        *,
        username: str,
        display_name: str,
        password: str,
        role: str,
        manager_id: str | None,
        telegram: str | None,
        updated_by: str = "admin",
    ) -> dict[str, str]:
        username = username.strip()
        display_name = display_name.strip()
        role = role.strip().lower()
        if not username or not display_name or not password.strip():
            raise ValueError("UserName, DisplayName và Password là bắt buộc.")
        if any(user.username.lower() == username.lower() for user in self.users):
            raise ValueError("UserName đã tồn tại.")
        if role not in {"user", "manager", "admin"}:
            raise ValueError("Role không hợp lệ.")

        manager_name: str | None = None
        if role == "user":
            if not manager_id:
                raise ValueError("User thường phải được gán manager.")
            manager = self._find_user(manager_id)
            if manager.role != "manager":
                raise ValueError("Manager được chọn không hợp lệ.")
            manager_name = manager.username

        user_id = f"user-{uuid4().hex[:8]}"
        self.users.append(UserSummary(id=user_id, username=username, display_name=display_name, role=role, manager_name=manager_name))  # type: ignore[arg-type]
        self.user_meta[user_id] = {
            "password": password.strip(),
            "telegram": (telegram or "").strip(),
            "updated_by": updated_by,
            "updated_at": datetime.now().replace(second=0, microsecond=0),
            "created_at": datetime.now().replace(second=0, microsecond=0),
        }
        self._save_state()
        return {"user_id": user_id, "username": username}

    def delete_admin_user(self, user_id: str) -> None:
        user = self._find_user(user_id)
        if user.role == "admin" and len([item for item in self.users if item.role == "admin"]) <= 1:
            raise ValueError("Không thể xóa admin cuối cùng.")
        if user.role == "manager" and any(item.role == "user" and item.manager_name == user.username for item in self.users):
            raise ValueError("Manager này đang quản lý user khác, chưa thể xóa.")

        self.users = [item for item in self.users if item.id != user_id]
        self.user_meta.pop(user_id, None)
        self.user_worker_links = [item for item in self.user_worker_links if item["user_id"] != user_id]
        self.channel_user_links = [item for item in self.channel_user_links if item["user_id"] != user_id]
        self._save_state()

    def reset_admin_user_password(self, user_id: str, password: str, updated_by: str = "admin") -> None:
        if not password.strip():
            raise ValueError("Password mới là bắt buộc.")
        self._find_user(user_id)
        meta = self._user_meta_record(user_id)
        meta["password"] = password.strip()
        meta["updated_by"] = updated_by
        meta["updated_at"] = datetime.now().replace(second=0, microsecond=0)
        self._save_state()

    def update_admin_user(
        self,
        *,
        user_id: str,
        display_name: str,
        telegram: str | None,
        manager_id: str | None,
        updated_by: str = "admin",
    ) -> None:
        user = self._find_user(user_id)
        if not display_name.strip():
            raise ValueError("DisplayName là bắt buộc.")
        user.display_name = display_name.strip()

        if user.role == "user":
            if not manager_id:
                raise ValueError("User thường phải được gán manager.")
            manager = self._find_user(manager_id)
            if manager.role != "manager":
                raise ValueError("Manager được chọn không hợp lệ.")
            user.manager_name = manager.username
        else:
            user.manager_name = None

        meta = self._user_meta_record(user_id)
        meta["telegram"] = (telegram or "").strip()
        meta["updated_by"] = updated_by
        meta["updated_at"] = datetime.now().replace(second=0, microsecond=0)
        self._save_state()

    def update_role_manager(self, user_id: str, promote: bool, updated_by: str = "admin") -> None:
        user = self._find_user(user_id)
        if promote:
            if user.role == "admin":
                raise ValueError("Admin hiện tại không cần gán thêm quyền manager.")
            user.role = "manager"
            user.manager_name = None
        else:
            if user.role != "manager":
                raise ValueError("User này không phải manager.")
            if any(item.role == "user" and item.manager_name == user.username for item in self.users):
                raise ValueError("Manager này đang quản lý user khác, chưa thể gỡ quyền.")
            user.role = "user"
            user.manager_name = None

        meta = self._user_meta_record(user_id)
        meta["updated_by"] = updated_by
        meta["updated_at"] = datetime.now().replace(second=0, microsecond=0)
        self._save_state()

    def update_role_admin(self, user_id: str, promote: bool, updated_by: str = "admin") -> None:
        user = self._find_user(user_id)
        if promote:
            user.role = "admin"
            user.manager_name = None
        else:
            if user.role != "admin":
                raise ValueError("User này không phải admin.")
            if len([item for item in self.users if item.role == "admin"]) <= 1:
                raise ValueError("Không thể gỡ quyền admin cuối cùng.")
            user.role = "user"
            user.manager_name = None

        meta = self._user_meta_record(user_id)
        meta["updated_by"] = updated_by
        meta["updated_at"] = datetime.now().replace(second=0, microsecond=0)
        self._save_state()

    def update_bot(self, worker_id: str, name: str, group: str, manager_id: str | None, updated_by: str = "admin") -> None:
        worker = self._find_worker(worker_id)
        if not name.strip():
            raise ValueError("Tên BOT là bắt buộc.")
        if not group.strip():
            raise ValueError("Group BOT là bắt buộc.")
        worker.name = name.strip()
        worker.group = group.strip()

        if manager_id:
            manager = self._find_user(manager_id)
            if manager.role != "manager":
                raise ValueError("Manager được chọn không hợp lệ.")
            manager_changed = worker.manager_id != manager.id
            worker.manager_id = manager.id
            worker.manager_name = manager.username
            if manager_changed:
                for channel in self.channels:
                    if channel.worker_id == worker.id:
                        channel.manager_name = manager.username
                for job in self.jobs:
                    if job.worker_name == worker.id:
                        job.manager_name = manager.username
                self.user_worker_links = [link for link in self.user_worker_links if link["worker_id"] != worker.id]
        self._save_state()

    def delete_bot(self, worker_id: str) -> None:
        self._find_worker(worker_id)
        deleted_channel_ids = {channel.id for channel in self.channels if channel.worker_id == worker_id}
        self.workers = [worker for worker in self.workers if worker.id != worker_id]
        self.channels = [channel for channel in self.channels if channel.worker_id != worker_id]
        self.channel_user_links = [link for link in self.channel_user_links if link["channel_id"] not in deleted_channel_ids]
        self.user_worker_links = [link for link in self.user_worker_links if link["worker_id"] != worker_id]
        self.jobs = [job for job in self.jobs if job.worker_name != worker_id]
        self._save_state()

    def update_bot_thread(self, worker_id: str, thread: int) -> None:
        worker = self._find_worker(worker_id)
        if thread < 1:
            raise ValueError("Số luồng phải lớn hơn hoặc bằng 1.")
        worker.threads = thread
        if worker.capacity < thread:
            worker.capacity = thread
        self._save_state()

    def add_user_bot(self, user_id: str, worker_id: str, threads: int, bot_type: str = "1080p", note: str | None = None) -> None:
        user = self._find_user(user_id)
        self._find_worker(worker_id)
        if user.role != "user":
            raise ValueError("Chỉ user thường mới gán BOT trực tiếp.")
        if any(item["user_id"] == user_id and item["worker_id"] == worker_id for item in self.user_worker_links):
            raise ValueError("BOT này đã được gán cho user.")
        next_id = max([item["id"] for item in self.user_worker_links], default=0) + 1
        self.user_worker_links.append(
            {
                "id": next_id,
                "user_id": user_id,
                "worker_id": worker_id,
                "threads": max(1, threads),
                "bot_type": bot_type.lower(),
                "note": (note or "").strip() or "BOT phụ",
            }
        )

    def delete_user_bot(self, mapping_id: int) -> None:
        exists = any(item["id"] == mapping_id for item in self.user_worker_links)
        if not exists:
            raise KeyError(mapping_id)
        self.user_worker_links = [item for item in self.user_worker_links if item["id"] != mapping_id]

    def update_user_bot(self, mapping_id: int, threads: int, bot_type: str | None = None, note: str | None = None) -> None:
        for mapping in self.user_worker_links:
            if mapping["id"] != mapping_id:
                continue
                raise ValueError("BOT này đã tồn tại trong danh sách gán.")
            mapping["threads"] = max(1, threads)
            mapping["note"] = (note or "").strip() or mapping["note"]
            return
        raise KeyError(mapping_id)

    def add_user_bot(self, user_id: str, worker_id: str, threads: int, bot_type: str = "1080p", note: str | None = None) -> None:
        user = self._find_user(user_id)
        self._find_worker(worker_id)
        if user.role != "user":
            raise ValueError("Chỉ user thường mới gán BOT trực tiếp.")
        if any(item["user_id"] == user_id and item["worker_id"] == worker_id for item in self.user_worker_links):
            raise ValueError("BOT này đã được gán cho user.")
        next_id = max([item["id"] for item in self.user_worker_links], default=0) + 1
        self.user_worker_links.append(
            {
                "id": next_id,
                "user_id": user_id,
                "worker_id": worker_id,
                "threads": max(1, threads),
                "bot_type": bot_type.lower(),
                "note": (note or "").strip() or "BOT phụ",
            }
        )

    def update_user_bot(self, mapping_id: int, threads: int, bot_type: str | None = None, note: str | None = None) -> None:
        for mapping in self.user_worker_links:
            if mapping["id"] != mapping_id:
                continue
            mapping["threads"] = max(1, threads)
            if bot_type:
                mapping["bot_type"] = bot_type.lower()
            if note is not None:
                mapping["note"] = (note or "").strip() or mapping.get("note", "BOT phụ")
            return
        raise KeyError(mapping_id)

    def get_admin_channel_index_context(self, *, user_id: str | None = None, bot_id: str | None = None) -> dict[str, Any]:
        return self.get_admin_template_context("channels", user_id=user_id, bot_id=bot_id)

    def get_admin_template_context(self, active_page: str, user_id: str | None = None, bot_id: str | None = None) -> dict[str, Any]:
        if active_page == "users":
            return self.get_admin_user_index_context()

        summary = self.get_admin_dashboard().summary
        page_map = {
            "workers": {"title": "Danh sách BOT", "template": "admin/worker_index.html"},
            "channels": {"title": "Danh sách Kênh", "template": "admin/channel_index.html"},
            "renders": {"title": "Danh sách Render", "template": "admin/render_index.html"},
        }
        page = page_map[active_page]
        context = self._admin_shell_context(page_title=page["title"], active_page=active_page)

        worker_rows: list[dict[str, Any]] = []
        for index, worker in enumerate(self.workers, start=1):
            status_label, status_class = self._worker_status_badge(worker.status)
            worker_rows.append(
                {
                    "index": index,
                    "id": worker.id,
                    "bot_id": worker.id.replace("worker", "BOT"),
                    "manager_name": worker.manager_name,
                    "name": worker.name.replace("worker", "BOT"),
                    "group": worker.manager_name,
                    "status_label": status_label,
                    "status_class": status_class,
                    "created_at": self._format_full_datetime(worker.last_seen_at),
                    "total_channels": len([channel for channel in self.channels if channel.worker_id == worker.id]),
                    "total_users": len([link for link in self.user_worker_links if link["worker_id"] == worker.id]),
                    "thread_text": f"{worker.threads}/{worker.capacity}",
                    "disk_text": f"{worker.disk_used_gb:.1f}GB / {worker.disk_total_gb:.1f}GB",
                    "bandwidth_text": f"{worker.bandwidth_kbps:,.2f} KB/s",
                    "load_percent": worker.load_percent,
                }
            )

        filtered_user: dict[str, Any] | None = None
        filtered_bot: dict[str, Any] | None = None
        channel_source = self.channels
        if active_page == "channels" and user_id:
            user = self._find_user(user_id)
            filtered_user = {"id": user.id, "username": user.username}
            if user.role == "user":
                worker_ids = {link["worker_id"] for link in self.user_worker_links if link["user_id"] == user.id}
                if worker_ids:
                    channel_source = [channel for channel in self.channels if channel.worker_id in worker_ids]
                else:
                    channel_source = [channel for channel in self.channels if channel.manager_name == user.manager_name]
            elif user.role == "manager":
                channel_source = [channel for channel in self.channels if channel.manager_name == user.username]
        if active_page == "channels" and bot_id:
            worker = self._find_worker(bot_id)
            filtered_bot = {"id": worker.id, "name": worker.name.replace("worker", "BOT")}
            channel_source = [channel for channel in channel_source if channel.worker_id == worker.id]

        channel_rows: list[dict[str, Any]] = []
        for index, channel in enumerate(channel_source, start=1):
            status_label, status_class = self._channel_status_badge(channel.status)
            channel_rows.append(
                {
                    "index": index,
                    "id": channel.id,
                    "avatar_url": channel.avatar_url or "/legacy/admin-themes/assets/img/avatar/avatar-1.png",
                    "name": channel.name,
                    "channel_id": channel.channel_id,
                    "gmail": channel.oauth_email or "-",
                    "manager_name": channel.manager_name,
                    "users": self._channel_users(channel),
                    "worker_name": channel.worker_name.replace("worker", "BOT"),
                    "group": channel.manager_name,
                    "status_label": status_label,
                    "status_class": status_class,
                    "created_at": self._format_full_datetime(channel.oauth_connected_at),
                }
            )

        render_rows: list[dict[str, Any]] = []
        for index, job in enumerate(sorted(self.jobs, key=lambda item: item.created_at, reverse=True), start=1):
            status_label, status_class = self._render_status_badge(job)
            primary_asset = next((asset for asset in job.assets if asset.url or asset.file_name), None)
            render_rows.append(
                {
                    "index": index,
                    "id": job.id,
                    "manager_name": job.manager_name or "-",
                    "username": "demo-user",
                    "created_at": self._format_full_datetime(job.created_at),
                    "title": job.title,
                    "worker_name": (job.worker_name or "-").replace("worker", "BOT"),
                    "group": job.manager_name or "-",
                    "avatar_url": job.channel_avatar_url or "/legacy/admin-themes/assets/img/avatar/avatar-1.png",
                    "channel_name": job.channel_name,
                    "channel_id": job.channel_id,
                    "video_link": primary_asset.url if primary_asset and primary_asset.url else (primary_asset.file_name if primary_asset else "-"),
                    "time_render_string": job.time_render_string,
                    "download_started_at": self._format_full_datetime(job.download_started_at),
                    "upload_started_at": self._format_full_datetime(job.upload_started_at),
                    "completed_at": self._format_full_datetime(job.completed_at),
                    "status_label": status_label,
                    "status_class": status_class,
                    "queue_order": job.queue_order or "-",
                }
            )

        context.update(
            {
                "template": page["template"],
                "users": self._build_user_rows(),
                "workers": worker_rows,
                "channels": channel_rows,
                "renders": render_rows,
                "filtered_user": filtered_user,
                "filtered_bot": filtered_bot,
                "delete_render_meta": {
                    "user": "admin",
                    "deleted_at": self._format_compact_datetime(datetime.now().replace(second=0, microsecond=0)),
                },
                "summary": summary,
            }
        )
        return context

    def _filtered_channels_v2(
        self,
        *,
        manager_ids: list[str] | None = None,
        user_id: str | None = None,
        bot_id: str | None = None,
    ) -> tuple[list[ChannelRecord], dict[str, Any] | None, dict[str, Any] | None]:
        selected_manager_ids = self._selected_manager_ids(manager_ids)
        manager_names = {self._find_user(manager_id).username for manager_id in selected_manager_ids} if selected_manager_ids else set()

        channel_source = list(self.channels)
        if manager_names:
            channel_source = [channel for channel in channel_source if channel.manager_name in manager_names]

        filtered_user: dict[str, Any] | None = None
        filtered_bot: dict[str, Any] | None = None

        if user_id:
            user = self._find_user(user_id)
            filtered_user = {"id": user.id, "username": user.username, "display_name": user.display_name}
            assigned_channel_ids = {link["channel_id"] for link in self.channel_user_links if link["user_id"] == user.id}
            channel_source = [channel for channel in channel_source if channel.id in assigned_channel_ids]

        if bot_id:
            worker = self._find_worker(bot_id)
            filtered_bot = {"id": worker.id, "name": worker.name.replace("worker", "BOT")}
            channel_source = [channel for channel in channel_source if channel.worker_id == worker.id]

        return channel_source, filtered_user, filtered_bot

    def _build_channel_rows_v2(self, channel_source: list[ChannelRecord]) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for index, channel in enumerate(channel_source, start=1):
            status_label, status_class = self._channel_status_badge(channel.status)
            worker = next((item for item in self.workers if item.id == channel.worker_id), None)
            rows.append(
                {
                    "index": index,
                    "id": channel.id,
                    "avatar_url": channel.avatar_url or "/legacy/admin-themes/assets/img/avatar/avatar-1.png",
                    "name": channel.name,
                    "channel_id": channel.channel_id,
                    "channel_link": self._channel_link(channel),
                    "gmail": channel.oauth_email or "-",
                    "manager_name": channel.manager_name,
                    "users": self._channel_users(channel),
                    "worker_id": channel.worker_id,
                    "worker_name": channel.worker_name.replace("worker", "BOT"),
                    "group": (worker.group if worker and worker.group else channel.manager_name),
                    "status_label": status_label,
                    "status_class": status_class,
                    "created_at": self._format_full_datetime(channel.oauth_connected_at),
                    "total_users": self._channel_user_count(channel.id),
                    "total_renders": len([job for job in self.jobs if job.channel_id == channel.id]),
                }
            )
        return rows

    def get_admin_channel_index_context(
        self,
        *,
        manager_ids: list[str] | None = None,
        user_id: str | None = None,
        bot_id: str | None = None,
        notice: str | None = None,
        notice_level: str = "success",
    ) -> dict[str, Any]:
        channels, filtered_user, filtered_bot = self._filtered_channels_v2(
            manager_ids=manager_ids,
            user_id=user_id,
            bot_id=bot_id,
        )
        context = self._admin_shell_context(
            page_title="Danh sách Kênh",
            active_page="channels",
            manager_ids=manager_ids,
            notice=notice,
            notice_level=notice_level,
        )
        context.update(
            {
                "template": "admin/channel_index.html",
                "channels": self._build_channel_rows_v2(channels),
                "filtered_user": filtered_user,
                "filtered_bot": filtered_bot,
            }
        )
        return context

    def get_admin_channels_of_user_context(
        self,
        *,
        user_id: str,
        notice: str | None = None,
        notice_level: str = "success",
    ) -> dict[str, Any]:
        user = self._find_user(user_id)
        if user.role == "user":
            channel_source = [channel for channel in self.channels if channel.manager_name == user.manager_name]
        elif user.role == "manager":
            channel_source = [channel for channel in self.channels if channel.manager_name == user.username]
        else:
            channel_source = list(self.channels)

        granted_channel_ids = {link["channel_id"] for link in self.channel_user_links if link["user_id"] == user.id}
        rows = []
        for row in self._build_channel_rows_v2(channel_source):
            row["is_used"] = row["id"] in granted_channel_ids
            rows.append(row)

        context = self._admin_shell_context(
            page_title=f"Thêm kênh cho người dùng {user.username}",
            active_page="channels",
            notice=notice,
            notice_level=notice_level,
        )
        context.update(
            {
                "template": "admin/channel_user.html",
                "target_user": {
                    "id": user.id,
                    "username": user.username,
                    "display_name": user.display_name,
                },
                "channels": rows,
            }
        )
        return context

    def get_admin_users_of_channel_context(
        self,
        *,
        channel_id: str,
        notice: str | None = None,
        notice_level: str = "success",
    ) -> dict[str, Any]:
        channel = self._find_channel(channel_id)
        assigned_ids = [link["user_id"] for link in self.channel_user_links if link["channel_id"] == channel.id]
        rows = []
        for index, user_id in enumerate(assigned_ids, start=1):
            user = self._find_user(user_id)
            rows.append(
                {
                    "index": index,
                    "id": user.id,
                    "username": user.username,
                    "display_name": user.display_name,
                    "total_channels": self._user_channel_count(user),
                    "total_bots": self._user_worker_count(user),
                }
            )

        available_users = [
            {"id": user.id, "username": user.username}
            for user in self.users
            if user.role == "user" and user.manager_name == channel.manager_name
        ]

        context = self._admin_shell_context(
            page_title=f"Danh sách người dùng của kênh {channel.name}",
            active_page="channels",
            notice=notice,
            notice_level=notice_level,
        )
        context.update(
            {
                "template": "admin/channel_users.html",
                "target_channel": {
                    "id": channel.id,
                    "name": channel.name,
                    "channel_id": channel.channel_id,
                },
                "users": rows,
                "available_users": available_users,
            }
        )
        return context

    def update_user_channel(self, user_id: str, channel_id: str) -> str:
        user = self._find_user(user_id)
        channel = self._find_channel(channel_id)
        if user.role != "user":
            raise ValueError("Chỉ user thường mới được gán vào kênh.")
        if user.manager_name and channel.manager_name != user.manager_name:
            raise ValueError("User không cùng manager với kênh này.")

        existing = next(
            (link for link in self.channel_user_links if link["user_id"] == user.id and link["channel_id"] == channel.id),
            None,
        )
        if existing:
            self.channel_user_links = [link for link in self.channel_user_links if link["id"] != existing["id"]]
            self._save_state()
            return "removed"

        next_id = max([item["id"] for item in self.channel_user_links], default=0) + 1
        self.channel_user_links.append({"id": next_id, "user_id": user.id, "channel_id": channel.id})
        self._save_state()
        return "added"

    def add_user_to_channel(self, user_id: str, channel_id: str) -> str:
        return self.update_user_channel(user_id, channel_id)

    def update_channel_profile(self, channel_id: str) -> None:
        channel = self._find_channel(channel_id)
        channel.status = "connected"
        channel.oauth_connected_at = datetime.now().replace(second=0, microsecond=0)
        self._save_state()

    def delete_channel(self, channel_id: str) -> None:
        self._find_channel(channel_id)
        self.channels = [channel for channel in self.channels if channel.id != channel_id]
        self.channel_user_links = [link for link in self.channel_user_links if link["channel_id"] != channel_id]
        self.jobs = [job for job in self.jobs if job.channel_id != channel_id]
        self._save_state()

    def get_channel_export_rows(self) -> list[dict[str, Any]]:
        rows = []
        for channel in self.channels:
            rows.append(
                {
                    "Avatar": channel.avatar_url or "",
                    "ChannelName": channel.name,
                    "ChannelYTId": channel.channel_id,
                    "ChannelLink": self._channel_link(channel),
                    "BotName": channel.worker_name.replace("worker", "BOT"),
                    "ChannelGmail": channel.oauth_email or "",
                    "Group": next((worker.group for worker in self.workers if worker.id == channel.worker_id), channel.manager_name),
                    "CreatedTime": self._format_full_datetime(channel.oauth_connected_at),
                    "TotalUser": self._channel_user_count(channel.id),
                    "Status": channel.status,
                    "UserUpload": ",".join(self._channel_users(channel)),
                    "Manager": channel.manager_name,
                }
            )
        return rows

    def get_admin_render_index_context(
        self,
        *,
        manager_ids: list[str] | None = None,
        channel_id: str | None = None,
        notice: str | None = None,
        notice_level: str = "success",
    ) -> dict[str, Any]:
        context = self._admin_shell_context(
            page_title="Danh sách Render",
            active_page="renders",
            manager_ids=manager_ids,
            notice=notice,
            notice_level=notice_level,
        )

        selected_manager_ids = self._selected_manager_ids(manager_ids)
        manager_names = {self._find_user(manager_id).username for manager_id in selected_manager_ids} if selected_manager_ids else set()
        job_source = list(self.jobs)
        if manager_names:
            job_source = [job for job in job_source if (job.manager_name or "") in manager_names]

        filtered_channel: dict[str, Any] | None = None
        if channel_id:
            channel = self._find_channel(channel_id)
            filtered_channel = {"id": channel.id, "name": channel.name, "channel_id": channel.channel_id}
            job_source = [job for job in job_source if job.channel_id == channel.id]

        render_rows: list[dict[str, Any]] = []
        for index, job in enumerate(sorted(job_source, key=lambda item: item.created_at, reverse=True), start=1):
            status_label, status_class = self._render_status_badge(job)
            primary_asset = next((asset for asset in job.assets if asset.url or asset.file_name), None)
            render_rows.append(
                {
                    "index": index,
                    "id": job.id,
                    "manager_name": job.manager_name or "-",
                    "username": self._job_username(job),
                    "created_at": self._format_full_datetime(job.created_at),
                    "title": job.title,
                    "worker_name": (job.worker_name or "-").replace("worker", "BOT"),
                    "group": job.manager_name or "-",
                    "avatar_url": job.channel_avatar_url or "/legacy/admin-themes/assets/img/avatar/avatar-1.png",
                    "channel_name": job.channel_name,
                    "channel_id": job.channel_id,
                    "video_link": primary_asset.url if primary_asset and primary_asset.url else (primary_asset.file_name if primary_asset else "-"),
                    "time_render_string": job.time_render_string,
                    "download_started_at": self._format_full_datetime(job.download_started_at),
                    "upload_started_at": self._format_full_datetime(job.upload_started_at),
                    "completed_at": self._format_full_datetime(job.completed_at),
                    "status_label": status_label,
                    "status_class": status_class,
                    "queue_order": job.queue_order or "-",
                }
            )

        context.update(
            {
                "template": "admin/render_index.html",
                "renders": render_rows,
                "filtered_channel": filtered_channel,
                "delete_render_meta": {
                    "user": self.render_delete_meta["user"],
                    "deleted_at": self._format_compact_datetime(self.render_delete_meta["deleted_at"]),
                },
            }
        )
        return context

    def get_admin_render_detail_context(
        self,
        *,
        job_id: str,
        notice: str | None = None,
        notice_level: str = "success",
    ) -> dict[str, Any]:
        job = self._find_job(job_id)
        channel = self._find_channel(job.channel_id)
        asset_map = {asset.slot: asset for asset in job.assets}

        def asset_value(slot: str) -> str:
            asset = asset_map.get(slot)
            if not asset:
                return ""
            return asset.url or asset.file_name or ""

        context = self._admin_shell_context(
            page_title="Thông tin Render",
            active_page="renders",
            notice=notice,
            notice_level=notice_level,
        )
        context.update(
            {
                "template": "admin/render_detail.html",
                "render_detail": {
                    "id": job.id,
                    "title": job.title,
                    "intro": asset_value("intro"),
                    "video_loop": asset_value("video_loop"),
                    "audio_loop": asset_value("audio_loop"),
                    "outro": asset_value("outro"),
                    "channel_name": channel.name,
                    "channel_id": channel.channel_id,
                    "time_render_string": job.time_render_string,
                    "scheduled_at": self._format_full_datetime(job.scheduled_at),
                    "source_mode": job.source_mode,
                },
            }
        )
        return context

    def get_admin_template_context(self, active_page: str, user_id: str | None = None, bot_id: str | None = None) -> dict[str, Any]:
        if active_page == "users":
            return self.get_admin_user_index_context()
        if active_page == "channels":
            return self.get_admin_channel_index_context(user_id=user_id, bot_id=bot_id)
        if active_page == "renders":
            return self.get_admin_render_index_context()
        raise KeyError(active_page)

    def _resolve_google_redirect_uri(self, base_url: str | None = None) -> str | None:
        return os.getenv("GOOGLE_REDIRECT_URI") or (
            f"{base_url}{self._oauth_callback_path()}" if base_url else None
        )

    def _google_oauth_config(self, base_url: str | None = None) -> dict[str, str | None]:
        return {
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
            "redirect_uri": self._resolve_google_redirect_uri(base_url),
        }

    @staticmethod
    def _parse_google_error(body: str) -> str:
        if not body:
            return ""
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            return body.strip()

        if isinstance(payload, dict):
            error = payload.get("error")
            description = payload.get("error_description")
            nested = payload.get("error")
            if isinstance(nested, dict):
                message = nested.get("message")
                status = nested.get("status")
                return " - ".join([part for part in [status, message] if part])
            return " - ".join([part for part in [str(error) if error else "", str(description) if description else ""] if part])
        return body.strip()

    def _post_form_json(self, url: str, payload: dict[str, str]) -> dict[str, Any]:
        encoded_payload = urlencode(payload).encode("utf-8")
        request = Request(
            url,
            data=encoded_payload,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
            },
            method="POST",
        )

        try:
            with urlopen(request, timeout=20) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = self._parse_google_error(exc.read().decode("utf-8", errors="ignore"))
            raise ValueError(detail or "Google token endpoint tra ve loi.") from exc
        except URLError as exc:
            raise ValueError("Khong the ket noi toi Google OAuth endpoint.") from exc

    def _get_json(self, url: str, access_token: str) -> dict[str, Any]:
        request = Request(
            url,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
            },
            method="GET",
        )
        try:
            with urlopen(request, timeout=20) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = self._parse_google_error(exc.read().decode("utf-8", errors="ignore"))
            raise ValueError(detail or "Google API tra ve loi.") from exc
        except URLError as exc:
            raise ValueError("Khong the ket noi toi Google API.") from exc

    def start_oauth(self, base_url: str | None = None, *, state: str) -> OAuthStartResponse:
        config = self._google_oauth_config(base_url)
        client_id = config["client_id"]
        redirect_uri = config["redirect_uri"]

        if not client_id or not redirect_uri:
            return OAuthStartResponse(
                auth_url=None,
                message="Đã sẵn sàng cho flow Google OAuth. Cần bổ sung GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET và GOOGLE_REDIRECT_URI để bật kết nối thật.",
            )

        query = urlencode(
            {
                "client_id": client_id,
                "redirect_uri": redirect_uri,
                "response_type": "code",
                "access_type": "offline",
                "include_granted_scopes": "true",
                "scope": self._google_oauth_scope(),
                "state": state,
                "prompt": "consent",
            }
        )
        return OAuthStartResponse(
            auth_url=f"https://accounts.google.com/o/oauth2/v2/auth?{query}",
            message="Đã tạo URL kết nối Google OAuth.",
        )

    def complete_google_oauth(self, *, code: str, base_url: str | None = None) -> dict[str, str]:
        config = self._google_oauth_config(base_url)
        client_id = config["client_id"]
        client_secret = config["client_secret"]
        redirect_uri = config["redirect_uri"]
        if not client_id or not client_secret or not redirect_uri:
            raise ValueError("Thieu GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET hoac GOOGLE_REDIRECT_URI.")

        token_payload = self._post_form_json(
            "https://oauth2.googleapis.com/token",
            {
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            },
        )
        access_token = str(token_payload.get("access_token") or "").strip()
        refresh_token = str(token_payload.get("refresh_token") or "").strip() or None
        scope = str(token_payload.get("scope") or self._google_oauth_scope()).strip()
        token_type = str(token_payload.get("token_type") or "").strip() or None
        if not access_token:
            raise ValueError("Google khong tra ve access_token.")

        userinfo = self._get_json("https://openidconnect.googleapis.com/v1/userinfo", access_token)
        youtube_payload = self._get_json(
            "https://www.googleapis.com/youtube/v3/channels?part=id,snippet&mine=true",
            access_token,
        )
        items = youtube_payload.get("items") or []
        if not items:
            raise ValueError("Tai khoan Google nay chua co YouTube channel hoac chua chon dung channel.")

        channel_payload = items[0] or {}
        channel_id = str(channel_payload.get("id") or "").strip()
        snippet = channel_payload.get("snippet") or {}
        channel_name = str(snippet.get("title") or "").strip() or "Untitled YouTube Channel"
        avatar_url = (
            ((snippet.get("thumbnails") or {}).get("default") or {}).get("url")
            or ((snippet.get("thumbnails") or {}).get("medium") or {}).get("url")
            or ((snippet.get("thumbnails") or {}).get("high") or {}).get("url")
        )
        oauth_email = str(userinfo.get("email") or "").strip() or None
        oauth_google_subject = str(userinfo.get("sub") or "").strip() or None
        now = datetime.now().replace(second=0, microsecond=0)

        if not channel_id:
            raise ValueError("Google tra ve du lieu channel khong hop le.")

        existing_channel = next((channel for channel in self.channels if channel.channel_id == channel_id), None)
        existing_refresh_token = existing_channel.oauth_refresh_token if existing_channel else None
        if not refresh_token and not existing_refresh_token:
            raise ValueError("Google khong tra ve refresh_token. Hay xoa quyen app cu va ket noi lai.")

        current_user = self._current_app_user()
        if existing_channel:
            channel = existing_channel
        else:
            worker = self._pick_worker_for_user(current_user)
            channel = ChannelRecord(
                id=f"channel-{uuid4().hex[:8]}",
                name=channel_name,
                channel_id=channel_id,
                avatar_url=avatar_url,
                worker_id=worker.id,
                worker_name=worker.name,
                manager_name=current_user.manager_name or worker.manager_name,
                status="connected",
            )
            self.channels.append(channel)

        channel.name = channel_name
        channel.avatar_url = avatar_url or channel.avatar_url
        channel.status = "connected"
        channel.oauth_email = oauth_email or channel.oauth_email
        channel.oauth_connected_at = now
        channel.oauth_google_subject = oauth_google_subject or channel.oauth_google_subject
        channel.oauth_refresh_token = refresh_token or existing_refresh_token
        channel.oauth_scope = scope or channel.oauth_scope
        channel.oauth_token_type = token_type or channel.oauth_token_type

        self._ensure_channel_user_link(channel_id=channel.id, user_id=current_user.id)
        self._save_state()

    @staticmethod
    def _sanitize_filename(file_name: str) -> str:
        value = re.sub(r"[^A-Za-z0-9._-]+", "-", (file_name or "").strip())
        value = value.strip(".-")
        return value or f"upload-{uuid4().hex[:8]}"

    @staticmethod
    def _path_for_session(session_id: str) -> str:
        return f"tmp/{session_id}.part"

    def _absolute_upload_path(self, relative_path: str) -> Path:
        return self.upload_dir / relative_path

    def _find_upload_session(self, session_id: str) -> UploadSessionRecord:
        for session in self.upload_sessions:
            if session.session_id == session_id:
                return session
        raise KeyError(session_id)

    def _cleanup_stale_uploads(self) -> None:
        now = datetime.now()
        changed = False
        keep_sessions: list[UploadSessionRecord] = []
        for session in self.upload_sessions:
            if session.status == "completed":
                keep_sessions.append(session)
                continue
            if session.expires_at > now:
                keep_sessions.append(session)
                continue
            session.status = "expired"
            temp_path = self._absolute_upload_path(session.temp_path)
            if temp_path.exists():
                temp_path.unlink(missing_ok=True)
            changed = True
        if changed:
            self.upload_sessions = keep_sessions
            self._save_state()

    @staticmethod
    def _upload_response(session: UploadSessionRecord) -> UploadSessionResponse:
        return UploadSessionResponse(
            session_id=session.session_id,
            slot=session.slot,
            file_name=session.file_name,
            size_bytes=session.size_bytes,
            received_bytes=session.received_bytes,
            chunk_size=session.chunk_size,
            status=session.status,
            expires_at=session.expires_at,
            asset_id=session.asset_id,
            stored_file_name=session.stored_file_name,
        )

    def create_upload_session(self, payload: UploadSessionCreateRequest) -> UploadSessionResponse:
        self._cleanup_stale_uploads()
        capabilities = self.get_upload_capabilities()
        if payload.size_bytes <= 0:
            raise ValueError("Kích thước file phải lớn hơn 0.")
        if payload.size_bytes > capabilities.max_local_upload_bytes:
            raise ValueError("File vượt quá giới hạn local upload hiện tại.")

        extension = Path(payload.file_name).suffix.lower()
        if extension not in capabilities.allowed_extensions:
            raise ValueError(f"Định dạng file không hỗ trợ: {extension or '(không có extension)'}")

        sanitized_name = self._sanitize_filename(payload.file_name)
        now = datetime.now()
        session = UploadSessionRecord(
            session_id=f"upl-{uuid4().hex}",
            slot=payload.slot,
            file_name=sanitized_name,
            content_type=payload.content_type,
            size_bytes=payload.size_bytes,
            received_bytes=0,
            chunk_size=capabilities.resumable_chunk_bytes,
            status="active",
            created_at=now,
            updated_at=now,
            expires_at=now + timedelta(hours=24),
            temp_path="",
        )
        session.temp_path = self._path_for_session(session.session_id)
        temp_path = self._absolute_upload_path(session.temp_path)
        temp_path.parent.mkdir(parents=True, exist_ok=True)
        temp_path.write_bytes(b"")
        self.upload_sessions.append(session)
        self._save_state()
        return self._upload_response(session)

    def get_upload_session(self, session_id: str) -> UploadSessionResponse:
        self._cleanup_stale_uploads()
        session = self._find_upload_session(session_id)
        return self._upload_response(session)

    def append_upload_chunk(self, session_id: str, offset: int, chunk: bytes) -> UploadSessionResponse:
        session = self._find_upload_session(session_id)
        if session.status not in {"active", "completed"}:
            raise ValueError("Upload session không còn hoạt động.")
        if session.status == "completed":
            return self._upload_response(session)
        if offset < 0:
            raise ValueError("Offset không hợp lệ.")

        temp_path = self._absolute_upload_path(session.temp_path)
        temp_path.parent.mkdir(parents=True, exist_ok=True)
        current_size = temp_path.stat().st_size if temp_path.exists() else 0
        if offset != current_size:
            raise ValueError(f"Offset không khớp. Server đang có {current_size} bytes.")
        if offset + len(chunk) > session.size_bytes:
            raise ValueError("Chunk vượt quá kích thước đã khai báo.")

        with temp_path.open("ab") as file_obj:
            file_obj.write(chunk)

        session.received_bytes = temp_path.stat().st_size
        session.updated_at = datetime.now()
        session.expires_at = session.updated_at + timedelta(hours=24)
        if session.received_bytes > session.size_bytes:
            raise ValueError("Upload vượt quá kích thước đã khai báo.")

        if session.received_bytes == session.size_bytes:
            session.status = "completed"
            session.asset_id = f"asset-{uuid4().hex[:12]}"
            stored_name = f"{session.asset_id}-{session.file_name}"
            asset_relative_path = f"assets/{stored_name}"
            final_path = self._absolute_upload_path(asset_relative_path)
            final_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(temp_path), str(final_path))
            session.stored_file_name = stored_name
            session.temp_path = asset_relative_path

        self._save_state()
        return self._upload_response(session)

    def consume_uploaded_asset(self, asset_id: str | None) -> str | None:
        if not asset_id:
            return None
        session = next((item for item in self.upload_sessions if item.asset_id == asset_id), None)
        if session is None or session.status != "completed" or not session.stored_file_name:
            raise ValueError("Uploaded asset không hợp lệ hoặc chưa hoàn tất.")
        return session.stored_file_name

    def abort_upload_session(self, session_id: str) -> None:
        session = self._find_upload_session(session_id)
        temp_path = self._absolute_upload_path(session.temp_path)
        if temp_path.exists():
            temp_path.unlink(missing_ok=True)
        self.upload_sessions = [item for item in self.upload_sessions if item.session_id != session_id]
        self._save_state()
        return {
            "channel_id": channel.id,
            "channel_name": channel.name,
            "youtube_channel_id": channel.channel_id,
            "oauth_email": channel.oauth_email or "",
        }


store = AppStore()
