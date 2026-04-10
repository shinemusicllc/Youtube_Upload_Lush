from __future__ import annotations

import hashlib
import hmac
import html
import logging
from copy import deepcopy
from datetime import datetime, timedelta, timezone, tzinfo
import json
import mimetypes
import os
import re
import secrets
import unicodedata
from pathlib import Path
import shutil
import sqlite3
from threading import Event, RLock, Thread
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, quote, urlencode, urlparse
from urllib.request import Request, urlopen
from uuid import uuid4
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

from .browser_runtime import BrowserRuntimeManager
from .schemas import (
    AdminDashboardResponse,
    AdminSummary,
    BrowserSessionRecord,
    BrowserSessionResponse,
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
    WorkerBrowserSessionSyncPayload,
    WorkerControlResponse,
    WorkerHeartbeatPayload,
    WorkerRegisterPayload,
    WorkerRecord,
    WorkerYouTubeUploadTarget,
)
from .worker_bootstrap import suggest_next_worker_id

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

logger = logging.getLogger(__name__)


class AppStore:
    KNOWN_WORKER_DISPLAY_NAMES = {
        "worker-01": "109.123.233.131",
        "worker-02": "62.72.46.42",
    }
    @staticmethod
    def _path_has_content(path: Path | None) -> bool:
        if path is None:
            return False
        try:
            return path.exists() and path.is_file() and path.stat().st_size > 0
        except OSError:
            return False

    @staticmethod
    def _app_timezone_name() -> str:
        return os.getenv("APP_TIMEZONE", "Asia/Saigon")

    @classmethod
    def _app_timezone(cls) -> tzinfo:
        preferred = cls._app_timezone_name()
        for candidate in (preferred, "Asia/Ho_Chi_Minh", "Etc/GMT-7"):
            try:
                return ZoneInfo(candidate)
            except Exception:
                continue
        return timezone(timedelta(hours=7))

    @classmethod
    def _normalize_datetime(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            return value
        return value.astimezone(cls._app_timezone()).replace(tzinfo=None)

    @classmethod
    def _now(cls, *, trim: bool = True) -> datetime:
        current = datetime.now(cls._app_timezone())
        if trim:
            current = current.replace(second=0, microsecond=0)
        return current.replace(tzinfo=None)

    @staticmethod
    def _worker_offline_alert_seconds() -> int:
        raw_value = str(os.getenv("WORKER_OFFLINE_ALERT_SECONDS", "180")).strip()
        try:
            value = int(raw_value)
        except (TypeError, ValueError):
            value = 180
        return max(60, value)

    @staticmethod
    def _worker_monitor_interval_seconds() -> int:
        raw_value = str(os.getenv("WORKER_MONITOR_INTERVAL_SECONDS", "30")).strip()
        try:
            value = int(raw_value)
        except (TypeError, ValueError):
            value = 30
        return max(10, value)

    @staticmethod
    def _worker_job_lease_seconds() -> int:
        raw_value = str(os.getenv("WORKER_JOB_LEASE_SECONDS", "90")).strip()
        try:
            value = int(raw_value)
        except (TypeError, ValueError):
            value = 90
        return max(30, value)

    @staticmethod
    def _telegram_alert_bot_token() -> str:
        return str(os.getenv("TELEGRAM_ALERT_BOT_TOKEN", "")).strip()

    @staticmethod
    def _telegram_alert_chat_id() -> str:
        return str(os.getenv("TELEGRAM_ALERT_CHAT_ID", "")).strip()

    @staticmethod
    def _telegram_link_ttl_seconds() -> int:
        raw_value = str(os.getenv("TELEGRAM_LINK_TTL_SECONDS", "600")).strip()
        try:
            value = int(raw_value)
        except (TypeError, ValueError):
            value = 600
        return max(120, value)

    @staticmethod
    def _normalize_telegram_chat_id(value: str | None) -> str:
        normalized = str(value or "").strip()
        if not normalized:
            return ""
        if not re.fullmatch(r"-?\d+", normalized):
            raise ValueError("Telegram ID phai la chat_id dang so.")
        return normalized

    def __init__(self) -> None:
        now = self._now()
        self.data_dir = Path(__file__).resolve().parents[1] / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.upload_dir = self.data_dir / "uploads"
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.upload_tmp_dir = self.upload_dir / "tmp"
        self.upload_tmp_dir.mkdir(parents=True, exist_ok=True)
        self.upload_asset_dir = self.upload_dir / "assets"
        self.upload_asset_dir.mkdir(parents=True, exist_ok=True)
        self.preview_dir = self.data_dir / "previews"
        self.preview_dir.mkdir(parents=True, exist_ok=True)
        self.state_db_path = self.data_dir / "app_state.db"
        self.upload_sessions: list[UploadSessionRecord] = []
        self.browser_runtime = BrowserRuntimeManager(self.data_dir)
        self.browser_sessions: list[BrowserSessionRecord] = []
        self.browser_profile_cleanup_tasks: list[dict[str, Any]] = []
        self.worker_round_robin_cursor: dict[str, str] = {}
        self.worker_connection_profiles: dict[str, dict[str, Any]] = {}
        self.worker_operation_tasks: list[dict[str, Any]] = []
        self.deleted_workers: dict[str, dict[str, Any]] = {}
        self.telegram_link_requests: dict[str, dict[str, Any]] = {}
        self.admin_notifications: list[dict[str, Any]] = []
        self._worker_state_lock = RLock()
        self._monitor_stop_event = Event()
        self._monitor_thread: Thread | None = None

        self.users = [
            UserSummary(id="admin-1", username="admin", display_name="Admin", role="admin"),
            UserSummary(id="manager-1", username="manager-alpha", display_name="Manager Alpha", role="manager"),
            UserSummary(id="user-1", username="demo-user", display_name="demo-user", role="user", manager_name="manager-alpha"),
        ]
        self.user_meta: dict[str, dict[str, Any]] = {
            "admin-1": {
                "password_hash": self._hash_password("admin123"),
                "password_algo": "pbkdf2_sha256",
                "telegram": "@admin-control",
                "updated_by": "system",
                "updated_at": now - timedelta(days=3),
                "created_at": now - timedelta(days=30),
            },
            "manager-1": {
                "password_hash": self._hash_password("manager123"),
                "password_algo": "pbkdf2_sha256",
                "telegram": "@manager-alpha",
                "updated_by": "admin",
                "updated_at": now - timedelta(days=2),
                "created_at": now - timedelta(days=20),
            },
            "user-1": {
                "password_hash": self._hash_password("demo123"),
                "password_algo": "pbkdf2_sha256",
                "telegram": "@demo-user",
                "updated_by": "manager-alpha",
                "updated_at": now - timedelta(hours=5),
                "created_at": now - timedelta(days=10),
            },
        }

        self.workers = [
            WorkerRecord(
                id="worker-01",
                name=self.KNOWN_WORKER_DISPLAY_NAMES["worker-01"],
                manager_id="manager-1",
                manager_name="manager-alpha",
                group="manager-alpha",
                created_at=now - timedelta(days=12),
                status="online",
                capacity=4,
                load_percent=45,
                ram_percent=73,
                ram_used_gb=5.84,
                ram_total_gb=8.0,
                bandwidth_kbps=1024,
                disk_used_gb=124.5,
                disk_total_gb=512.0,
                threads=2,
                last_seen_at=now,
            ),
            WorkerRecord(
                id="worker-02",
                name=self.KNOWN_WORKER_DISPLAY_NAMES["worker-02"],
                manager_id="manager-1",
                manager_name="manager-alpha",
                group="manager-alpha",
                created_at=now - timedelta(days=10),
                status="online",
                capacity=4,
                load_percent=28,
                ram_percent=41,
                ram_used_gb=3.28,
                ram_total_gb=8.0,
                bandwidth_kbps=832,
                disk_used_gb=88.2,
                disk_total_gb=512.0,
                threads=2,
                last_seen_at=now,
            ),
        ]
        self.user_worker_links: list[dict[str, Any]] = [
            {"id": 1, "user_id": "user-1", "worker_id": "worker-01", "threads": 2, "note": "BOT chÃ­nh"},
            {"id": 2, "user_id": "user-1", "worker_id": "worker-02", "threads": 1, "note": "BOT phá»¥"},
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
        self._ensure_auth_tables()
        self._load_or_seed_state()
        normalized_worker_names = self._normalize_known_worker_names()
        normalized_worker_created_at = self._normalize_worker_created_at()
        normalized_user_worker_assignments = self._normalize_user_worker_assignments()
        migrated_credentials = self._migrate_legacy_user_meta_passwords()
        self._bootstrap_auth_tables_from_memory_if_empty()
        self._load_auth_state_from_tables()
        normalized_visible_relationships = self._normalize_visible_admin_relationships()
        normalized_job_runtime_progress = self._normalize_job_runtime_progress()
        if (
            migrated_credentials
            or normalized_worker_names
            or normalized_worker_created_at
            or normalized_user_worker_assignments
            or normalized_visible_relationships
            or normalized_job_runtime_progress
        ):
            self._save_state()

    def get_session_secret(self) -> str:
        return os.getenv("SESSION_SECRET", "dev-control-plane-session-secret")

    def get_worker_shared_secret(self) -> str:
        return os.getenv("WORKER_SHARED_SECRET", "dev-worker-shared-secret")

    @staticmethod
    def _max_active_jobs_per_worker() -> int:
        raw_value = str(os.getenv("WORKER_MAX_ACTIVE_JOBS_PER_VPS", "1")).strip()
        try:
            limit = int(raw_value)
        except (TypeError, ValueError):
            limit = 1
        return max(1, limit)

    @staticmethod
    def _fixed_assignment_threads() -> int:
        return 1

    def _normalize_requested_worker_threads(self, requested_threads: int | None) -> int:
        requested = max(1, int(requested_threads or 1))
        return min(requested, self._max_active_jobs_per_worker())

    def _effective_worker_thread_limit(self, worker: WorkerRecord) -> int:
        configured = max(1, int(worker.threads or worker.capacity or 1))
        return min(configured, self._max_active_jobs_per_worker())

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
        return "https://www.googleapis.com/auth/youtube.readonly https://www.googleapis.com/auth/youtube.upload openid email profile"

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

    def _ensure_auth_tables(self) -> None:
        with sqlite3.connect(self.state_db_path) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS auth_users (
                    id TEXT PRIMARY KEY,
                    username TEXT NOT NULL UNIQUE,
                    display_name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    manager_id TEXT,
                    manager_name TEXT,
                    telegram TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    updated_by TEXT
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS auth_credentials (
                    user_id TEXT PRIMARY KEY,
                    password_hash TEXT NOT NULL,
                    password_algo TEXT NOT NULL,
                    password_plain TEXT,
                    updated_at TEXT,
                    FOREIGN KEY(user_id) REFERENCES auth_users(id) ON DELETE CASCADE
                )
                """
            )
            try:
                connection.execute("ALTER TABLE auth_credentials ADD COLUMN password_plain TEXT")
            except sqlite3.OperationalError:
                pass
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS auth_channel_grants (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    channel_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    UNIQUE(channel_id, user_id),
                    FOREIGN KEY(user_id) REFERENCES auth_users(id) ON DELETE CASCADE
                )
                """
            )
            connection.commit()

    @staticmethod
    def _password_iterations() -> int:
        return 390_000

    @classmethod
    def _hash_password(cls, password: str) -> str:
        normalized = password.strip()
        if not normalized:
            raise ValueError("Password khÃ´ng ÄÆ°á»£c Äá» trá»ng.")
        salt = secrets.token_hex(16)
        iterations = cls._password_iterations()
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            normalized.encode("utf-8"),
            bytes.fromhex(salt),
            iterations,
        ).hex()
        return f"pbkdf2_sha256${iterations}${salt}${digest}"

    @staticmethod
    def _verify_password_hash(password: str, password_hash: str) -> bool:
        try:
            algorithm, iteration_raw, salt, expected_digest = password_hash.split("$", 3)
            if algorithm != "pbkdf2_sha256":
                return False
            iterations = int(iteration_raw)
        except (TypeError, ValueError):
            return False
        derived = hashlib.pbkdf2_hmac(
            "sha256",
            password.strip().encode("utf-8"),
            bytes.fromhex(salt),
            iterations,
        ).hex()
        return hmac.compare_digest(expected_digest, derived)

    def _set_user_password(self, user_id: str, password: str, *, updated_at: datetime | None = None) -> None:
        meta = self._user_meta_record(user_id)
        normalized_password = password.strip()
        meta["password_hash"] = self._hash_password(normalized_password)
        meta["password_algo"] = "pbkdf2_sha256"
        meta.pop("password", None)
        if updated_at is not None:
            meta["updated_at"] = updated_at

    def _migrate_legacy_user_meta_passwords(self) -> bool:
        changed = False
        for user_id in [user.id for user in self.users]:
            meta = self._user_meta_record(user_id)
            password_hash = str(meta.get("password_hash") or "").strip()
            legacy_password = str(meta.get("password") or "").strip()
            if password_hash:
                meta["password_algo"] = str(meta.get("password_algo") or "pbkdf2_sha256")
                continue
            if not legacy_password:
                continue
            self._set_user_password(user_id, legacy_password, updated_at=meta.get("updated_at"))
            changed = True
        return changed

    def _save_auth_state(self) -> None:
        with sqlite3.connect(self.state_db_path) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute("DELETE FROM auth_channel_grants")
            connection.execute("DELETE FROM auth_credentials")
            connection.execute("DELETE FROM auth_users")

            manager_ids_by_username = {user.username: user.id for user in self.users if user.role == "manager"}
            for user in self.users:
                meta = self._user_meta_record(user.id)
                password_hash = str(meta.get("password_hash") or "").strip()
                if not password_hash:
                    raise ValueError(f"User {user.username} chÆ°a cÃ³ password_hash.")
                connection.execute(
                    """
                    INSERT INTO auth_users (
                        id, username, display_name, role, manager_id, manager_name, telegram, created_at, updated_at, updated_by
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        user.id,
                        user.username,
                        user.display_name,
                        user.role,
                        manager_ids_by_username.get(user.manager_name or ""),
                        user.manager_name,
                        meta.get("telegram") or None,
                        self._serialize_value(meta.get("created_at")),
                        self._serialize_value(meta.get("updated_at")),
                        meta.get("updated_by") or None,
                    ),
                )
                connection.execute(
                    """
                    INSERT INTO auth_credentials (user_id, password_hash, password_algo, password_plain, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        user.id,
                        password_hash,
                        meta.get("password_algo") or "pbkdf2_sha256",
                        None,
                        self._serialize_value(meta.get("updated_at")),
                    ),
                )

            for link in self.channel_user_links:
                connection.execute(
                    """
                    INSERT INTO auth_channel_grants (id, channel_id, user_id)
                    VALUES (?, ?, ?)
                    """,
                    (link["id"], link["channel_id"], link["user_id"]),
                )

            connection.commit()

    def _bootstrap_auth_tables_from_memory_if_empty(self) -> None:
        with sqlite3.connect(self.state_db_path) as connection:
            row = connection.execute("SELECT COUNT(*) FROM auth_users").fetchone()
        if row and int(row[0] or 0) > 0:
            return
        self._save_auth_state()

    def _load_auth_state_from_tables(self) -> None:
        with sqlite3.connect(self.state_db_path) as connection:
            connection.row_factory = sqlite3.Row
            user_rows = connection.execute(
                """
                SELECT
                    users.id,
                    users.username,
                    users.display_name,
                    users.role,
                    users.manager_id,
                    users.manager_name,
                    users.telegram,
                    users.created_at,
                    users.updated_at,
                    users.updated_by,
                    credentials.password_hash,
                    credentials.password_algo,
                    credentials.password_plain
                FROM auth_users AS users
                JOIN auth_credentials AS credentials ON credentials.user_id = users.id
                ORDER BY users.created_at ASC, users.username ASC
                """
            ).fetchall()
            grant_rows = connection.execute(
                "SELECT id, channel_id, user_id FROM auth_channel_grants ORDER BY id ASC"
            ).fetchall()

        if not user_rows:
            return

        self.users = []
        self.user_meta = {}
        for row in user_rows:
            self.users.append(
                UserSummary(
                    id=row["id"],
                    username=row["username"],
                    display_name=row["display_name"],
                    role=row["role"],
                    manager_id=row["manager_id"],
                    manager_name=row["manager_name"],
                    created_at=self._parse_datetime(row["created_at"]),
                    updated_at=self._parse_datetime(row["updated_at"]),
                    updated_by=row["updated_by"],
                    link_telegram=row["telegram"] or None,
                )
            )
            self.user_meta[row["id"]] = {
                "password_hash": row["password_hash"],
                "password_algo": row["password_algo"] or "pbkdf2_sha256",
                "password": "",
                "telegram": row["telegram"] or "",
                "updated_by": row["updated_by"] or "system",
                "updated_at": self._parse_datetime(row["updated_at"]),
                "created_at": self._parse_datetime(row["created_at"]) or self._now(),
            }

        self.channel_user_links = [
            {"id": int(row["id"]), "channel_id": row["channel_id"], "user_id": row["user_id"]}
            for row in grant_rows
        ]

    @staticmethod
    def _serialize_value(value: Any) -> Any:
        if isinstance(value, datetime):
            return AppStore._normalize_datetime(value).isoformat()
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
            return AppStore._normalize_datetime(value)
        if isinstance(value, str):
            return AppStore._normalize_datetime(datetime.fromisoformat(value))
        raise ValueError(f"Unsupported datetime payload: {value!r}")

    def _restore_worker_connection_profiles(self, payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
        restored: dict[str, dict[str, Any]] = {}
        for worker_id, raw_profile in payload.items():
            normalized_worker_id = str(worker_id or "").strip()
            if not normalized_worker_id or not isinstance(raw_profile, dict):
                continue
            profile = dict(raw_profile)
            normalized_ssh_private_key = str(profile.get("ssh_private_key") or "").strip() or None
            restored[normalized_worker_id] = {
                "worker_id": normalized_worker_id,
                "vps_ip": str(profile.get("vps_ip") or "").strip(),
                "ssh_user": str(profile.get("ssh_user") or "").strip() or "root",
                "auth_mode": str(profile.get("auth_mode") or "").strip().lower() or ("ssh_key" if normalized_ssh_private_key else "password"),
                "password": str(profile.get("password") or "").strip() or None,
                "ssh_private_key": normalized_ssh_private_key,
                "updated_at": self._parse_datetime(profile.get("updated_at")),
            }
        return restored

    def _restore_worker_operation_tasks(self, payload: list[dict[str, Any]]) -> list[dict[str, Any]]:
        tasks: list[dict[str, Any]] = []
        for raw_task in payload:
            if not isinstance(raw_task, dict):
                continue
            task = dict(raw_task)
            task_id = str(task.get("id") or "").strip()
            worker_id = str(task.get("worker_id") or "").strip()
            if not task_id or not worker_id:
                continue
            status = str(task.get("status") or "queued").strip()
            if status in {"completed", "failed"}:
                continue
            tasks.append(
                {
                    "id": task_id,
                    "worker_id": worker_id,
                    "worker_name": str(task.get("worker_name") or "").strip(),
                    "vps_ip": str(task.get("vps_ip") or "").strip(),
                    "manager_id": str(task.get("manager_id") or "").strip() or None,
                    "manager_name": str(task.get("manager_name") or "").strip(),
                    "group": str(task.get("group") or "").strip(),
                    "kind": str(task.get("kind") or "install").strip(),
                    "transport": str(task.get("transport") or "").strip() or ("ssh" if str(task.get("kind") or "").strip() == "decommission" else ""),
                    "status": status,
                    "message": str(task.get("message") or "").strip(),
                    "ssh_user": str(task.get("ssh_user") or "").strip() or "root",
                    "app_dir": str(task.get("app_dir") or "").strip() or "/opt/youtube-upload-lush",
                    "runtime_dir": str(task.get("runtime_dir") or "").strip() or "/opt/youtube-upload-lush-runtime",
                    "requested_by": str(task.get("requested_by") or "").strip() or "system",
                    "requested_role": str(task.get("requested_role") or "").strip() or "system",
                    "dispatched_at": self._parse_datetime(task.get("dispatched_at")),
                    "created_at": self._parse_datetime(task.get("created_at")) or self._now(trim=False),
                    "updated_at": self._parse_datetime(task.get("updated_at")) or self._now(trim=False),
                    "completed_at": self._parse_datetime(task.get("completed_at")),
                }
            )
        return tasks

    def _restore_deleted_workers(self, payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
        restored: dict[str, dict[str, Any]] = {}
        for worker_id, raw_meta in payload.items():
            normalized_worker_id = str(worker_id or "").strip()
            if not normalized_worker_id or not isinstance(raw_meta, dict):
                continue
            restored[normalized_worker_id] = {
                "worker_id": normalized_worker_id,
                "worker_name": str(raw_meta.get("worker_name") or "").strip() or normalized_worker_id,
                "vps_ip": str(raw_meta.get("vps_ip") or "").strip() or None,
                "deleted_by": str(raw_meta.get("deleted_by") or "").strip() or "system",
                "reason": str(raw_meta.get("reason") or "").strip() or "manual_delete",
                "deleted_at": self._parse_datetime(raw_meta.get("deleted_at")) or self._now(trim=False),
            }
        return restored

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
            "browser_sessions": [session.model_dump(mode="json") for session in self.browser_sessions],
            "browser_profile_cleanup_tasks": deepcopy(self.browser_profile_cleanup_tasks),
            "worker_round_robin_cursor": deepcopy(self.worker_round_robin_cursor),
            "worker_connection_profiles": self._serialize_value(self.worker_connection_profiles),
            "worker_operation_tasks": self._serialize_value(self.worker_operation_tasks),
            "deleted_workers": self._serialize_value(self.deleted_workers),
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
        self.browser_sessions = [BrowserSessionRecord.model_validate(item) for item in payload.get("browser_sessions", [])]
        self.browser_profile_cleanup_tasks = list(payload.get("browser_profile_cleanup_tasks") or [])
        self.worker_round_robin_cursor = {
            str(worker_id or "").strip(): str(owner_key or "").strip()
            for worker_id, owner_key in (payload.get("worker_round_robin_cursor") or {}).items()
            if str(worker_id or "").strip() and str(owner_key or "").strip()
        }
        self.worker_connection_profiles = self._restore_worker_connection_profiles(
            payload.get("worker_connection_profiles") or {}
        )
        self.worker_operation_tasks = self._restore_worker_operation_tasks(
            payload.get("worker_operation_tasks") or []
        )
        self.deleted_workers = self._restore_deleted_workers(payload.get("deleted_workers") or {})

        render_meta = payload.get("render_delete_meta") or {}
        self.render_delete_meta = {
            "user": render_meta.get("user") or "admin",
            "deleted_at": self._parse_datetime(render_meta.get("deleted_at"))
            or self._now(),
        }

    def _save_state(self) -> None:
        self._save_auth_state()
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
                (payload, self._now(trim=False).isoformat()),
            )
            connection.commit()

    def _load_or_seed_state(self) -> None:
        with sqlite3.connect(self.state_db_path) as connection:
            row = connection.execute("SELECT payload FROM app_state WHERE state_key = 'main'").fetchone()
        if row and row[0]:
            self._apply_state(json.loads(row[0]))
            return
        self._save_state()

    @staticmethod
    def _looks_like_ipv4(value: str | None) -> bool:
        normalized = str(value or "").strip()
        if not normalized:
            return False
        return bool(re.fullmatch(r"\d{1,3}(?:\.\d{1,3}){3}", normalized))

    def suggest_next_worker_bootstrap_id(self) -> str:
        reserved_ids = [worker.id for worker in self.workers]
        reserved_ids.extend(
            str(task.get("worker_id") or "").strip()
            for task in self.worker_operation_tasks
            if str(task.get("worker_id") or "").strip()
            and str(task.get("status") or "").strip() not in {"completed", "failed"}
        )
        return suggest_next_worker_id(reserved_ids)

    def _remember_worker_connection_profile(
        self,
        worker_id: str,
        *,
        vps_ip: str,
        ssh_user: str,
        auth_mode: str | None = None,
        password: str | None = None,
        ssh_private_key: str | None = None,
    ) -> None:
        normalized_worker_id = str(worker_id or "").strip()
        normalized_ip = str(vps_ip or "").strip()
        if not normalized_worker_id or not normalized_ip:
            return
        existing = dict(self.worker_connection_profiles.get(normalized_worker_id) or {})
        normalized_auth_mode = str(auth_mode or existing.get("auth_mode") or "").strip().lower()
        normalized_password = password if password is not None else existing.get("password")
        normalized_ssh_private_key = ssh_private_key if ssh_private_key is not None else existing.get("ssh_private_key")
        self.worker_connection_profiles[normalized_worker_id] = {
            "worker_id": normalized_worker_id,
            "vps_ip": normalized_ip,
            "ssh_user": str(ssh_user or "").strip() or "root",
            "auth_mode": normalized_auth_mode or ("ssh_key" if str(normalized_ssh_private_key or "").strip() else "password"),
            "password": str(normalized_password or "").strip() or None,
            "ssh_private_key": str(normalized_ssh_private_key or "").strip() or None,
            "updated_at": self._now(trim=False),
        }

    def _remember_deleted_worker(
        self,
        worker_id: str,
        *,
        worker_name: str | None = None,
        vps_ip: str | None = None,
        deleted_by: str | None = None,
        reason: str = "manual_delete",
    ) -> None:
        normalized_worker_id = str(worker_id or "").strip()
        if not normalized_worker_id:
            return
        normalized_vps_ip = str(vps_ip or "").strip() or None
        self.deleted_workers[normalized_worker_id] = {
            "worker_id": normalized_worker_id,
            "worker_name": str(worker_name or "").strip() or normalized_worker_id,
            "vps_ip": normalized_vps_ip,
            "deleted_by": str(deleted_by or "").strip() or "system",
            "reason": str(reason or "").strip() or "manual_delete",
            "deleted_at": self._now(trim=False),
        }

    def _clear_deleted_worker(self, worker_id: str) -> None:
        normalized_worker_id = str(worker_id or "").strip()
        if not normalized_worker_id:
            return
        self.deleted_workers.pop(normalized_worker_id, None)

    def _ensure_worker_not_deleted(self, worker_id: str) -> None:
        normalized_worker_id = str(worker_id or "").strip()
        if not normalized_worker_id:
            return
        deleted_meta = self.deleted_workers.get(normalized_worker_id)
        if not deleted_meta:
            return
        raise ValueError("BOT này dã b? xoá kh?i h? th?ng. Hãy thêm BOT l?i n?u mu?n k?t n?i l?i VPS này.")

    def get_worker_connection_profile(self, worker_id: str) -> dict[str, Any]:
        normalized_worker_id = str(worker_id or "").strip()
        if not normalized_worker_id:
            raise KeyError(worker_id)
        profile = dict(self.worker_connection_profiles.get(normalized_worker_id) or {})
        if not profile:
            worker = self._find_worker(normalized_worker_id)
            worker_name = str(self._resolve_worker_display_name(worker.id) or "").strip()
            if self._looks_like_ipv4(worker_name):
                profile = {
                    "worker_id": normalized_worker_id,
                    "vps_ip": worker_name,
                    "ssh_user": "root",
                    "updated_at": self._now(trim=False),
                }
        normalized_ip = str(profile.get("vps_ip") or "").strip()
        if not normalized_ip:
            raise ValueError("BOT này chua có thông tin VPS IP d? g? worker t? xa.")
        return {
            "worker_id": normalized_worker_id,
            "vps_ip": normalized_ip,
            "ssh_user": str(profile.get("ssh_user") or "").strip() or "root",
            "auth_mode": str(profile.get("auth_mode") or "").strip().lower() or ("ssh_key" if str(profile.get("ssh_private_key") or "").strip() else "password"),
            "password": str(profile.get("password") or "").strip() or None,
            "ssh_private_key": str(profile.get("ssh_private_key") or "").strip() or None,
            "updated_at": self._parse_datetime(profile.get("updated_at")),
        }

    @staticmethod
    def _worker_operation_is_finished(task: dict[str, Any]) -> bool:
        return str(task.get("status") or "").strip() in {"completed", "failed"}

    def _find_worker_operation_optional(self, operation_id: str) -> dict[str, Any] | None:
        normalized_id = str(operation_id or "").strip()
        if not normalized_id:
            return None
        for task in self.worker_operation_tasks:
            if str(task.get("id") or "").strip() == normalized_id:
                return task
        return None

    def _find_worker_operation(self, operation_id: str) -> dict[str, Any]:
        task = self._find_worker_operation_optional(operation_id)
        if task is not None:
            return task
        raise KeyError(operation_id)

    def _worker_operation_badge(self, task: dict[str, Any]) -> tuple[str, str]:
        kind = str(task.get("kind") or "").strip()
        status = str(task.get("status") or "").strip()
        mapping = {
            ("install", "queued"): (
                "Ðang x?p hàng cài d?t...",
                "inline-flex items-center rounded-full border border-indigo-200 bg-indigo-50 px-2.5 py-1 text-[10px] font-semibold text-indigo-700",
            ),
            ("install", "running"): (
                "Ðang cài d?t...",
                "inline-flex items-center rounded-full border border-indigo-200 bg-indigo-50 px-2.5 py-1 text-[10px] font-semibold text-indigo-700",
            ),
            ("install", "awaiting_registration"): (
                "Ch? BOT k?t n?i",
                "inline-flex items-center rounded-full border border-brand-100 bg-brand-50 px-2.5 py-1 text-[10px] font-semibold text-brand-700",
            ),
            ("install", "failed"): (
                "Cài d?t l?i",
                "inline-flex items-center rounded-full border border-rose-200 bg-rose-50 px-2.5 py-1 text-[10px] font-semibold text-rose-700",
            ),
            ("decommission", "queued"): (
                "Ðang x?p hàng g? BOT...",
                "inline-flex items-center rounded-full border border-rose-200 bg-rose-50 px-2.5 py-1 text-[10px] font-semibold text-rose-700",
            ),
            ("decommission", "running"): (
                "Ðang g? BOT...",
                "inline-flex items-center rounded-full border border-rose-200 bg-rose-50 px-2.5 py-1 text-[10px] font-semibold text-rose-700",
            ),
            ("decommission", "failed"): (
                "G? BOT l?i",
                "inline-flex items-center rounded-full border border-rose-200 bg-rose-50 px-2.5 py-1 text-[10px] font-semibold text-rose-700",
            ),
        }
        return mapping.get(
            (kind, status),
            (
                "Ðang x? lý",
                "inline-flex items-center rounded-full border border-slate-200 bg-slate-100 px-2.5 py-1 text-[10px] font-semibold text-slate-700",
            ),
        )

    def _push_admin_notification(
        self,
        *,
        message: str,
        level: str = "info",
        manager_id: str | None = None,
        scope: str = "bot-ops",
    ) -> dict[str, Any]:
        notification = {
            "id": f"notice-{uuid4().hex[:12]}",
            "message": str(message or "").strip(),
            "level": str(level or "info").strip() or "info",
            "manager_id": str(manager_id or "").strip() or None,
            "scope": str(scope or "bot-ops").strip() or "bot-ops",
            "created_at": self._now(trim=False),
        }
        self.admin_notifications.append(notification)
        self.admin_notifications = self.admin_notifications[-100:]
        return deepcopy(notification)

    def _latest_admin_notification_id(
        self,
        *,
        manager_ids: list[str] | None = None,
        scope: str = "bot-ops",
    ) -> str:
        selected_ids = set(self._selected_manager_ids(manager_ids))
        latest_id = ""
        for item in self.admin_notifications:
            if str(item.get("scope") or "").strip() != scope:
                continue
            manager_id = str(item.get("manager_id") or "").strip()
            if selected_ids and manager_id not in selected_ids:
                continue
            latest_id = str(item.get("id") or "").strip()
        return latest_id

    def get_admin_notifications(
        self,
        *,
        manager_ids: list[str] | None = None,
        after_id: str | None = None,
        scope: str = "bot-ops",
    ) -> dict[str, Any]:
        selected_ids = set(self._selected_manager_ids(manager_ids))
        normalized_after_id = str(after_id or "").strip()
        latest_id = self._latest_admin_notification_id(manager_ids=manager_ids, scope=scope)
        if not normalized_after_id:
            return {"items": [], "cursor": latest_id}
        if normalized_after_id == latest_id:
            return {"items": [], "cursor": latest_id}

        seen_after = False
        items: list[dict[str, Any]] = []
        for item in self.admin_notifications:
            if str(item.get("scope") or "").strip() != scope:
                continue
            item_id = str(item.get("id") or "").strip()
            if not seen_after:
                if item_id == normalized_after_id:
                    seen_after = True
                continue
            manager_id = str(item.get("manager_id") or "").strip()
            if selected_ids and manager_id not in selected_ids:
                continue
            items.append(
                {
                    "id": item_id,
                    "message": str(item.get("message") or "").strip(),
                    "level": str(item.get("level") or "info").strip() or "info",
                    "created_at": self._format_full_datetime(self._parse_datetime(item.get("created_at"))),
                }
            )
        return {"items": items, "cursor": latest_id}

    def fail_worker_operation(
        self,
        operation_id: str,
        *,
        message: str,
        level: str = "error",
    ) -> None:
        with self._worker_state_lock:
            task = self._find_worker_operation_optional(operation_id)
            task_message = str(message or "").strip() or "Không thể hoàn tất thao tác BOT."
            kind = str(task.get("kind") or "").strip() if task is not None else ""
            worker_id = str(task.get("worker_id") or "").strip() if task is not None else ""
            vps_ip = str(task.get("vps_ip") or "").strip() if task is not None else ""
            worker_name = (
                str(task.get("worker_name") or task.get("vps_ip") or task.get("worker_id") or "").strip()
                if task is not None
                else str(operation_id or "").strip()
            )
            manager_id = str(task.get("manager_id") or "").strip() or None if task is not None else None
            manager_name = str(task.get("manager_name") or "").strip() if task is not None else ""
            requested_by = str(task.get("requested_by") or "").strip() if task is not None else ""
            requested_role = str(task.get("requested_role") or "").strip() if task is not None else ""
            notice_prefix = "Cài đặt BOT" if kind == "install" else "Gỡ BOT"
            notice_message = f"{notice_prefix} {worker_name} thất bại: {task_message}"
            duplicated_notice = next(
                (
                    item
                    for item in reversed(self.admin_notifications)
                    if str(item.get("message") or "").strip() == notice_message
                    and str(item.get("level") or "").strip() == level
                    and str(item.get("manager_id") or "").strip() == str(manager_id or "").strip()
                ),
                None,
            )
            if duplicated_notice is None:
                self._push_admin_notification(
                    message=notice_message,
                    level=level,
                    manager_id=manager_id,
                )
            if task is not None:
                self.worker_operation_tasks = [
                    item
                    for item in self.worker_operation_tasks
                    if str(item.get("id") or "").strip() != str(operation_id or "").strip()
                ]
                if kind == "install" and worker_id and not any(str(worker.id or "").strip() == worker_id for worker in self.workers):
                    self.worker_connection_profiles.pop(worker_id, None)
            self._save_state()
        logger.error(
            "worker_operation_failed kind=%s operation_id=%s worker_id=%s worker_name=%s vps_ip=%s manager_id=%s manager_name=%s requested_by=%s requested_role=%s message=%s",
            kind or "unknown",
            str(operation_id or "").strip(),
            worker_id or "-",
            worker_name or "-",
            vps_ip or "-",
            manager_id or "-",
            manager_name or "-",
            requested_by or "-",
            requested_role or "-",
            task_message,
        )

    def enqueue_worker_install_operation(
        self,
        *,
        worker_id: str,
        worker_name: str,
        vps_ip: str,
        ssh_user: str,
        auth_mode: str = "password",
        password: str | None = None,
        ssh_private_key: str | None = None,
        manager_id: str | None,
        manager_name: str,
        group: str = "",
        requested_by: str = "system",
        requested_role: str = "system",
    ) -> dict[str, Any]:
        with self._worker_state_lock:
            normalized_worker_id = str(worker_id or "").strip()
            normalized_ip = str(vps_ip or "").strip()
            if not normalized_worker_id or not normalized_ip:
                raise ValueError("Worker bootstrap task thi?u worker_id ho?c VPS IP.")
            self._clear_deleted_worker(normalized_worker_id)
            if any(str(worker.id or "").strip() == normalized_worker_id for worker in self.workers):
                raise ValueError("Worker ID này dã t?n t?i trong control-plane.")
            if any(str(self._resolve_worker_display_name(worker.id) or "").strip() == normalized_ip for worker in self.workers):
                raise ValueError("VPS này dã t?n t?i trong danh sách BOT.")
            removed_failed_worker_ids: set[str] = set()
            remaining_tasks: list[dict[str, Any]] = []
            for task in self.worker_operation_tasks:
                is_replaceable_failed_install = (
                    str(task.get("kind") or "").strip() == "install"
                    and str(task.get("status") or "").strip() == "failed"
                    and (
                        str(task.get("worker_id") or "").strip() == normalized_worker_id
                        or str(task.get("vps_ip") or "").strip() == normalized_ip
                    )
                )
                if is_replaceable_failed_install:
                    failed_worker_id = str(task.get("worker_id") or "").strip()
                    if failed_worker_id:
                        removed_failed_worker_ids.add(failed_worker_id)
                    continue
                remaining_tasks.append(task)
            self.worker_operation_tasks = remaining_tasks
            for failed_worker_id in removed_failed_worker_ids:
                if not any(str(worker.id or "").strip() == failed_worker_id for worker in self.workers):
                    self.worker_connection_profiles.pop(failed_worker_id, None)
            for task in self.worker_operation_tasks:
                if self._worker_operation_is_finished(task):
                    continue
                if (
                    str(task.get("worker_id") or "").strip() == normalized_worker_id
                    or str(task.get("vps_ip") or "").strip() == normalized_ip
                ):
                    raise ValueError("BOT này dang có m?t ti?n trình cài d?t ho?c g? BOT khác chua xong.")
            now = self._now(trim=False)
            task = {
                "id": f"worker-op-{uuid4().hex[:10]}",
                "worker_id": normalized_worker_id,
                "worker_name": str(worker_name or normalized_ip).strip() or normalized_ip,
                "vps_ip": normalized_ip,
                "manager_id": str(manager_id or "").strip() or None,
                "manager_name": str(manager_name or "").strip() or "system",
                "group": str(group or "").strip(),
                "kind": "install",
                "status": "queued",
                "message": "Ðang ch? control-plane k?t n?i SSH vào VPS...",
                "requested_by": str(requested_by or "").strip() or "system",
                "requested_role": str(requested_role or "").strip() or "system",
                "created_at": now,
                "updated_at": now,
                "completed_at": None,
            }
            self.worker_operation_tasks.append(task)
            self._remember_worker_connection_profile(
                normalized_worker_id,
                vps_ip=normalized_ip,
                ssh_user=ssh_user,
                auth_mode=auth_mode,
                password=password,
                ssh_private_key=ssh_private_key,
            )
            self._save_state()
            return deepcopy(task)

    def enqueue_worker_decommission_operation(
        self,
        *,
        worker_id: str,
        vps_ip: str,
        ssh_user: str,
        transport: str = "ssh",
        app_dir: str = "/opt/youtube-upload-lush",
        runtime_dir: str = "/opt/youtube-upload-lush-runtime",
        requested_by: str = "system",
        requested_role: str = "system",
    ) -> dict[str, Any]:
        with self._worker_state_lock:
            worker = self._find_worker(worker_id)
            normalized_worker_id = str(worker.id or "").strip()
            normalized_ip = str(vps_ip or "").strip()
            if not normalized_ip:
                raise ValueError("BOT này chua có VPS IP d? g? worker t? xa.")
            for task in self.worker_operation_tasks:
                if self._worker_operation_is_finished(task):
                    continue
                if str(task.get("worker_id") or "").strip() == normalized_worker_id:
                    raise ValueError("BOT này dang có m?t ti?n trình cài d?t ho?c g? BOT khác chua xong.")
            now = self._now(trim=False)
            task = {
                "id": f"worker-op-{uuid4().hex[:10]}",
                "worker_id": normalized_worker_id,
                "worker_name": self._resolve_worker_display_name(worker.id),
                "vps_ip": normalized_ip,
                "manager_id": worker.manager_id,
                "manager_name": worker.manager_name,
                "group": str(worker.group or "").strip(),
                "kind": "decommission",
                "transport": str(transport or "ssh").strip() or "ssh",
                "status": "queued",
                "message": (
                    "Ðang ch? control-plane k?t n?i SSH d? g? worker kh?i VPS..."
                    if str(transport or "ssh").strip() != "self"
                    else "Ðang ch? BOT t? g? kh?i VPS..."
                ),
                "ssh_user": str(ssh_user or "").strip() or "root",
                "app_dir": str(app_dir or "").strip() or "/opt/youtube-upload-lush",
                "runtime_dir": str(runtime_dir or "").strip() or "/opt/youtube-upload-lush-runtime",
                "requested_by": str(requested_by or "").strip() or "system",
                "requested_role": str(requested_role or "").strip() or "system",
                "dispatched_at": None,
                "created_at": now,
                "updated_at": now,
                "completed_at": None,
            }
            self.worker_operation_tasks.append(task)
            self._remember_worker_connection_profile(normalized_worker_id, vps_ip=normalized_ip, ssh_user=ssh_user)
            self._save_state()
            return deepcopy(task)

    def get_worker_decommission_task(self, worker_id: str, shared_secret: str) -> dict[str, Any] | None:
        with self._worker_state_lock:
            worker = self._authenticate_worker(worker_id, shared_secret)
            now = self._now(trim=False)
            task = next(
                (
                    item
                    for item in self.worker_operation_tasks
                    if str(item.get("kind") or "").strip() == "decommission"
                    and str(item.get("transport") or "").strip() == "self"
                    and str(item.get("worker_id") or "").strip() == worker.id
                    and str(item.get("status") or "").strip() in {"queued", "running"}
                ),
                None,
            )
            if task is None:
                return None
            dispatched_at = self._parse_datetime(task.get("dispatched_at"))
            if dispatched_at and now - dispatched_at < timedelta(seconds=20):
                return None
            task["status"] = "running"
            task["message"] = "BOT dang t? g? service và d? li?u kh?i VPS..."
            task["updated_at"] = now
            task["dispatched_at"] = now
            self._save_state()
            return deepcopy(task)

    def complete_worker_decommission_task(
        self,
        *,
        operation_id: str,
        worker_id: str,
        shared_secret: str,
        status: str,
        message: str | None = None,
    ) -> None:
        cleaned_status = str(status or "").strip().lower() or "completed"
        with self._worker_state_lock:
            worker = self._authenticate_worker(worker_id, shared_secret)
            task = self._find_worker_operation(operation_id)
            if str(task.get("kind") or "").strip() != "decommission":
                raise ValueError("Task g? BOT không h?p l?.")
            if str(task.get("worker_id") or "").strip() != worker.id:
                raise ValueError("Task g? BOT không thu?c worker hi?n t?i.")
            task_message = str(message or "").strip()
            if cleaned_status == "completed":
                worker_name = self._resolve_worker_display_name(worker.id)
                self._remember_deleted_worker(
                    worker.id,
                    worker_name=worker_name,
                    vps_ip=str(task.get("vps_ip") or "").strip() or None,
                    deleted_by=str(task.get("requested_by") or "").strip() or "system",
                    reason="self_decommission",
                )
                if task_message:
                    task["message"] = task_message
                self.finalize_decommissioned_bot(worker.id, operation_id)
                return
        if cleaned_status == "completed":
            return
        self.fail_worker_operation(operation_id, message=task_message or "BOT t? g? kh?i VPS th?t b?i.")

    def update_worker_operation(
        self,
        operation_id: str,
        *,
        status: str | None = None,
        message: str | None = None,
        completed: bool = False,
    ) -> dict[str, Any]:
        with self._worker_state_lock:
            task = self._find_worker_operation(operation_id)
            now = self._now(trim=False)
            if status:
                task["status"] = str(status).strip()
            if message is not None:
                task["message"] = str(message).strip()
            task["updated_at"] = now
            task["completed_at"] = now if completed else None
            self._save_state()
            return deepcopy(task)

    def clear_install_operation_after_register(self, worker_id: str) -> bool:
        completed_task: dict[str, Any] | None = None
        with self._worker_state_lock:
            normalized_worker_id = str(worker_id or "").strip()
            completed_task = next(
                (
                    deepcopy(task)
                    for task in self.worker_operation_tasks
                    if str(task.get("kind") or "").strip() == "install"
                    and str(task.get("worker_id") or "").strip() == normalized_worker_id
                ),
                None,
            )
            before = len(self.worker_operation_tasks)
            self.worker_operation_tasks = [
                task
                for task in self.worker_operation_tasks
                if not (
                    str(task.get("kind") or "").strip() == "install"
                    and str(task.get("worker_id") or "").strip() == normalized_worker_id
                )
            ]
            changed = len(self.worker_operation_tasks) != before
            if changed:
                self._save_state()
        if changed and completed_task is not None:
            worker = self._find_worker(normalized_worker_id)
            worker_name = self._resolve_worker_display_name(worker.id)
            vps_ip = str(completed_task.get("vps_ip") or "").strip() or worker_name
            self._notify_telegram_chat_ids(
                self._bot_operation_recipient_chat_ids(completed_task),
                self._bot_install_completed_message(
                    completed_task,
                    worker_name=worker_name,
                    worker_id=worker.id,
                    vps_ip=vps_ip,
                ),
            )
        return changed

    def finalize_decommissioned_bot(self, worker_id: str, operation_id: str) -> None:
        completed_task: dict[str, Any] | None = None
        worker_name = ""
        vps_ip = ""
        with self._worker_state_lock:
            worker = self._find_worker(worker_id)
            task = next(
                (
                    item
                    for item in self.worker_operation_tasks
                    if str(item.get("id") or "").strip() == str(operation_id or "").strip()
                ),
                {},
            )
            completed_task = deepcopy(task) if task else None
            worker_name = self._resolve_worker_display_name(worker.id)
            vps_ip = str(task.get("vps_ip") or "").strip() or worker_name
            self._remember_deleted_worker(
                worker.id,
                worker_name=worker_name,
                vps_ip=str(task.get("vps_ip") or "").strip() or None,
                deleted_by=str(task.get("requested_by") or "").strip() or "system",
                reason=str(task.get("transport") or "").strip() or "decommission",
            )
            self._delete_bot_state(worker_id)
            self.worker_operation_tasks = [
                task
                for task in self.worker_operation_tasks
                if str(task.get("id") or "").strip() != str(operation_id or "").strip()
            ]
            self.worker_connection_profiles.pop(str(worker_id or "").strip(), None)
            self._save_state()
        if completed_task is not None:
            self._notify_telegram_chat_ids(
                self._bot_operation_recipient_chat_ids(completed_task),
                self._bot_decommission_completed_message(
                    completed_task,
                    worker_name=worker_name,
                    worker_id=str(worker_id or "").strip(),
                    vps_ip=vps_ip,
                ),
            )

    def start_background_services(self) -> None:
        with self._worker_state_lock:
            if self._monitor_thread and self._monitor_thread.is_alive():
                return
            self._reconcile_worker_connectivity(now=self._now(trim=False))
            self._monitor_stop_event.clear()
            self._monitor_thread = Thread(
                target=self._worker_monitor_loop,
                name="control-plane-worker-monitor",
                daemon=True,
            )
            self._monitor_thread.start()

    def stop_background_services(self) -> None:
        self._monitor_stop_event.set()
        monitor_thread = self._monitor_thread
        if monitor_thread and monitor_thread.is_alive():
            monitor_thread.join(timeout=2.0)
        self._monitor_thread = None

    def _worker_monitor_loop(self) -> None:
        interval_seconds = self._worker_monitor_interval_seconds()
        while not self._monitor_stop_event.wait(interval_seconds):
            try:
                with self._worker_state_lock:
                    now = self._now(trim=False)
                    self._reconcile_worker_connectivity(now=now)
                    self._reconcile_expired_worker_jobs(now=now)
            except Exception as exc:
                print(f"[worker_monitor] reconcile failed: {exc}", flush=True)

    def _send_telegram_alert(self, message: str, *, chat_id: str | None = None) -> bool:
        bot_token = self._telegram_alert_bot_token()
        resolved_chat_id = self._normalize_telegram_chat_id(chat_id or self._telegram_alert_chat_id())
        if not bot_token or not resolved_chat_id:
            return False

        encoded_message = urlencode(
            {
                "chat_id": resolved_chat_id,
                "text": message,
            }
        ).encode("utf-8")
        request = Request(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            data=encoded_message,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=10) as response:
                payload = json.loads(response.read().decode("utf-8"))
                return bool(payload.get("ok"))
        except Exception as exc:
            print(f"[telegram_alert] failed: {exc}", flush=True)
            return False

    def _telegram_api_payload(self, method: str, *, params: dict[str, str] | None = None) -> dict[str, Any]:
        bot_token = self._telegram_alert_bot_token()
        if not bot_token:
            raise ValueError("Bot Telegram thong bao chua duoc cau hinh.")

        normalized_method = str(method or "").strip().strip("/")
        if not normalized_method:
            raise ValueError("Telegram API method khong hop le.")

        request_url = f"https://api.telegram.org/bot{bot_token}/{normalized_method}"
        if params:
            request_url = f"{request_url}?{urlencode(params)}"

        request = Request(
            request_url,
            headers={"Accept": "application/json"},
            method="GET",
        )
        try:
            with urlopen(request, timeout=10) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            raise ValueError("Khong the ket noi Telegram Bot API.") from exc

        if not payload.get("ok"):
            description = str(payload.get("description") or "").strip() or "Telegram Bot API tra ve loi."
            raise ValueError(description)
        return payload

    def _telegram_bot_identity(self) -> dict[str, str]:
        payload = self._telegram_api_payload("getMe")
        result = payload.get("result") or {}
        username = str(result.get("username") or "").strip()
        first_name = str(result.get("first_name") or "").strip()
        if not username:
            raise ValueError("Bot Telegram chua co username cong khai.")
        return {
            "username": username,
            "display_name": first_name or username,
            "deep_link_base": f"https://t.me/{username}",
        }

    @staticmethod
    def _extract_telegram_link_code(text: str) -> str:
        normalized = str(text or "").strip()
        if not normalized:
            return ""
        for pattern in (
            r"^/start(?:@[A-Za-z0-9_]+)?\s+([A-Za-z0-9_-]+)$",
            r"^/link(?:@[A-Za-z0-9_]+)?\s+([A-Za-z0-9_-]+)$",
        ):
            match = re.fullmatch(pattern, normalized)
            if match:
                return str(match.group(1) or "").strip()
        return ""

    def _cleanup_expired_telegram_link_requests(self, *, now: datetime | None = None) -> None:
        current_time = now or self._now(trim=False)
        ttl = timedelta(seconds=self._telegram_link_ttl_seconds())
        expired_codes = [
            code
            for code, request in self.telegram_link_requests.items()
            if current_time - request.get("created_at", current_time) > ttl
        ]
        for code in expired_codes:
            self.telegram_link_requests.pop(code, None)

    def create_telegram_link_request(self, user_id: str) -> dict[str, Any]:
        self._find_user(user_id)
        now = self._now(trim=False)
        self._cleanup_expired_telegram_link_requests(now=now)
        bot_identity = self._telegram_bot_identity()
        code = secrets.token_urlsafe(6).replace("-", "").replace("_", "")
        expires_at = now + timedelta(seconds=self._telegram_link_ttl_seconds())
        self.telegram_link_requests[code] = {
            "user_id": user_id,
            "code": code,
            "created_at": now,
            "expires_at": expires_at,
            "chat_id": "",
            "telegram_username": "",
            "telegram_name": "",
        }
        return {
            "code": code,
            "bot_username": bot_identity["username"],
            "bot_display_name": bot_identity["display_name"],
            "deep_link_url": f"{bot_identity['deep_link_base']}?start={quote(code)}",
            "expires_in_seconds": self._telegram_link_ttl_seconds(),
        }

    def get_telegram_link_request_status(self, user_id: str, code: str) -> dict[str, Any]:
        cleaned_code = str(code or "").strip()
        if not cleaned_code:
            raise ValueError("Thieu ma lien ket Telegram.")

        now = self._now(trim=False)
        self._cleanup_expired_telegram_link_requests(now=now)
        request_state = self.telegram_link_requests.get(cleaned_code)
        if request_state is None or str(request_state.get("user_id") or "").strip() != str(user_id or "").strip():
            raise KeyError("Ma lien ket Telegram da het han hoac khong ton tai.")

        expires_at = request_state.get("expires_at")
        if isinstance(expires_at, datetime) and expires_at <= now:
            self.telegram_link_requests.pop(cleaned_code, None)
            raise ValueError("Ma lien ket Telegram da het han. Hay tao lai ma moi.")

        if not request_state.get("chat_id"):
            payload = self._telegram_api_payload("getUpdates", params={"limit": "100"})
            updates = payload.get("result") or []
            for update in reversed(updates):
                message = update.get("message") or update.get("edited_message") or {}
                matched_code = self._extract_telegram_link_code(message.get("text") or "")
                if matched_code != cleaned_code:
                    continue
                chat = message.get("chat") or {}
                chat_id = self._normalize_telegram_chat_id(str(chat.get("id") or "").strip())
                if not chat_id:
                    continue
                sender = message.get("from") or {}
                display_name = " ".join(
                    [
                        str(sender.get("first_name") or "").strip(),
                        str(sender.get("last_name") or "").strip(),
                    ]
                ).strip()
                request_state["chat_id"] = chat_id
                request_state["telegram_username"] = str(sender.get("username") or "").strip()
                request_state["telegram_name"] = display_name
                break

        chat_id = str(request_state.get("chat_id") or "").strip()
        if chat_id:
            return {
                "status": "linked",
                "chat_id": chat_id,
                "telegram_username": str(request_state.get("telegram_username") or "").strip(),
                "telegram_name": str(request_state.get("telegram_name") or "").strip(),
            }

        expires_in_seconds = 0
        if isinstance(expires_at, datetime):
            expires_in_seconds = max(0, int((expires_at - now).total_seconds()))
        return {
            "status": "pending",
            "expires_in_seconds": expires_in_seconds,
        }

    def _telegram_linked_confirmation_message(self, user: UserSummary) -> str:
        return (
            "Tài kho?n Telegram này dã du?c thêm d? nh?n thông báo t? app YouTube Upload.\n"
            f"Tài kho?n app: {user.username}\n"
            "N?u mu?n ng?t thông báo, hãy xóa Telegram ID trong m?c C?p nh?t user r?i luu l?i."
        )

    def _telegram_unlinked_confirmation_message(self, user: UserSummary) -> str:
        return (
            "Tài kho?n Telegram này dã du?c ng?t kh?i h? th?ng thông báo c?a app YouTube Upload.\n"
            f"Tài kho?n app: {user.username}\n"
            "T? bây gi? tài kho?n này s? không nh?n thông báo m?i t? app n?a."
        )

    @staticmethod
    def _bot_operation_actor_label(role: str | None, username: str | None) -> str:
        normalized_username = str(username or "").strip() or "system"
        return normalized_username

    def _bot_install_completed_message(self, task: dict[str, Any], *, worker_name: str, worker_id: str, vps_ip: str) -> str:
        actor_label = self._bot_operation_actor_label(task.get("requested_role"), task.get("requested_by"))
        manager_name = str(task.get("manager_name") or "").strip() or "system"
        return (
            "[BOT] Thêm BOT thành công\n"
            f"Ngu?i thao tác: {actor_label}\n"
            f"BOT: {worker_name}\n"
            f"BOT ID: {worker_id}\n"
            f"VPS: {vps_ip}\n"
            f"Manager s? h?u: {manager_name}"
        )

    def _bot_decommission_completed_message(self, task: dict[str, Any], *, worker_name: str, worker_id: str, vps_ip: str) -> str:
        actor_label = self._bot_operation_actor_label(task.get("requested_role"), task.get("requested_by"))
        manager_name = str(task.get("manager_name") or "").strip() or "system"
        return (
            "[BOT] Xóa BOT thành công\n"
            f"Ngu?i thao tác: {actor_label}\n"
            f"BOT: {worker_name}\n"
            f"BOT ID: {worker_id}\n"
            f"VPS: {vps_ip}\n"
            f"Manager tru?c khi xóa: {manager_name}"
        )

    def _user_telegram_chat_id(self, user_id: str) -> str:
        meta = self._user_meta_record(user_id)
        try:
            return self._normalize_telegram_chat_id(meta.get("telegram"))
        except ValueError:
            return ""

    def _telegram_recipient_chat_ids_for_users(self, users: list[UserSummary]) -> list[str]:
        chat_ids: list[str] = []
        seen_ids: set[str] = set()
        for user in users:
            chat_id = self._user_telegram_chat_id(user.id)
            if not chat_id or chat_id in seen_ids:
                continue
            chat_ids.append(chat_id)
            seen_ids.add(chat_id)
        return chat_ids

    def _all_admin_telegram_recipient_chat_ids(self) -> list[str]:
        admin_users = [user for user in self.users if user.role == "admin"]
        chat_ids = self._telegram_recipient_chat_ids_for_users(admin_users)
        if chat_ids:
            return chat_ids
        try:
            fallback_chat_id = self._normalize_telegram_chat_id(self._telegram_alert_chat_id())
        except ValueError:
            fallback_chat_id = ""
        return [fallback_chat_id] if fallback_chat_id else []

    def _manager_telegram_recipient_chat_ids(self, manager_usernames: set[str]) -> list[str]:
        if not manager_usernames:
            return []
        manager_users = [
            user
            for user in self.users
            if user.role == "manager" and user.username in manager_usernames
        ]
        return self._telegram_recipient_chat_ids_for_users(manager_users)

    def _bot_operation_recipient_chat_ids(self, task: dict[str, Any]) -> list[str]:
        recipient_chat_ids = self._all_admin_telegram_recipient_chat_ids()
        seen_ids = set(recipient_chat_ids)
        manager_usernames: set[str] = set()

        manager_name = str(task.get("manager_name") or "").strip()
        if manager_name and manager_name != "system":
            manager_usernames.add(manager_name)

        requested_by = str(task.get("requested_by") or "").strip()
        requested_role = str(task.get("requested_role") or "").strip().lower()
        if requested_by and requested_role == "manager":
            manager_usernames.add(requested_by)

        for chat_id in self._manager_telegram_recipient_chat_ids(manager_usernames):
            if chat_id in seen_ids:
                continue
            recipient_chat_ids.append(chat_id)
            seen_ids.add(chat_id)
        return recipient_chat_ids

    def _worker_alert_recipient_chat_ids(self, worker: WorkerRecord) -> list[str]:
        recipient_chat_ids = self._all_admin_telegram_recipient_chat_ids()
        seen_ids = set(recipient_chat_ids)
        manager_name = str(worker.manager_name or "").strip()
        if manager_name and manager_name != "system":
            for chat_id in self._manager_telegram_recipient_chat_ids({manager_name}):
                if chat_id in seen_ids:
                    continue
                recipient_chat_ids.append(chat_id)
                seen_ids.add(chat_id)
        return recipient_chat_ids

    def _notify_telegram_chat_ids(self, chat_ids: list[str], message: str) -> bool:
        recipient_chat_ids = [chat_id for chat_id in chat_ids if str(chat_id or "").strip()]
        if not recipient_chat_ids:
            return False
        delivered = False
        for chat_id in recipient_chat_ids:
            if self._send_telegram_alert(message, chat_id=chat_id):
                delivered = True
        return delivered

    def _worker_offline_message(self, worker: WorkerRecord, *, now: datetime) -> str:
        worker_name = worker.name or worker.id
        manager_name = worker.manager_name or "không rõ"
        return (
            "[C?NH BÁO] BOT m?t k?t n?i quá 3 phút\n"
            f"BOT: {worker_name}\n"
            f"BOT ID: {worker.id}\n"
            f"Manager: {manager_name}\n"
            "Tr?ng thái: BOT chua t? k?t n?i l?i v?i control-plane"
        )

    def _reconcile_worker_connectivity(self, *, now: datetime) -> bool:
        changed = False
        alert_seconds = self._worker_offline_alert_seconds()
        stale_cutoff = timedelta(seconds=alert_seconds)
        for worker in self.workers:
            last_seen = worker.last_seen_at
            running_threads = self._count_worker_running_jobs(worker)
            is_online = last_seen is not None and (now - last_seen) < stale_cutoff
            if is_online:
                desired_status = "busy" if running_threads > 0 else "online"
                if worker.status != desired_status:
                    worker.status = desired_status
                    changed = True
                if worker.offline_since_at is not None:
                    worker.offline_since_at = None
                    changed = True
                if worker.offline_alert_sent_at is not None:
                    worker.offline_alert_sent_at = None
                    changed = True
                continue

            if worker.status != "offline":
                worker.status = "offline"
                changed = True
            offline_since_at = last_seen or now
            if worker.offline_since_at != offline_since_at:
                worker.offline_since_at = offline_since_at
                changed = True
            if worker.offline_alert_sent_at is not None:
                continue
            message = self._worker_offline_message(worker, now=now)
            if self._notify_telegram_chat_ids(self._worker_alert_recipient_chat_ids(worker), message):
                worker.offline_alert_sent_at = now
                changed = True
        if changed:
            self._save_state()
        return changed

    def _normalize_user_worker_assignments(self) -> bool:
        changed = False
        normalized_links: list[dict[str, Any]] = []
        seen_pairs: set[tuple[str, str]] = set()

        def sort_key(mapping: dict[str, Any]) -> tuple[int, str, str]:
            try:
                mapping_id = int(mapping.get("id") or 0)
            except (TypeError, ValueError):
                mapping_id = 0
            return (mapping_id, str(mapping.get("user_id") or ""), str(mapping.get("worker_id") or ""))

        for raw_mapping in sorted(self.user_worker_links, key=sort_key):
            user_id = str(raw_mapping.get("user_id") or "").strip()
            worker_id = str(raw_mapping.get("worker_id") or "").strip()
            if not user_id or not worker_id:
                changed = True
                continue
            pair = (user_id, worker_id)
            if pair in seen_pairs:
                changed = True
                continue

            mapping = dict(raw_mapping)
            mapping["threads"] = self._fixed_assignment_threads()
            mapping["note"] = str(mapping.get("note") or "").strip() or "VPS duoc cap"
            normalized_links.append(mapping)
            seen_pairs.add(pair)
            if mapping != raw_mapping:
                changed = True

        if normalized_links != self.user_worker_links:
            self.user_worker_links = normalized_links
            changed = True

        for job in self.jobs:
            channel = next((item for item in self.channels if item.id == job.channel_id), None)
            if channel is None:
                continue
            if job.worker_name != channel.worker_id:
                job.worker_name = channel.worker_id
                changed = True

        return changed

    def _normalize_worker_created_at(self) -> bool:
        changed = False
        fallback_now = self._now(trim=False)
        for worker in self.workers:
            if worker.created_at is not None:
                continue
            worker.created_at = worker.last_seen_at or fallback_now
            changed = True
        return changed

    def _normalize_visible_admin_relationships(self) -> bool:
        changed = False
        valid_user_ids = {user.id for user in self.users if user.role in {"user", "manager", "admin"}}
        valid_worker_ids = {worker.id for worker in self.workers}
        valid_channel_ids = {channel.id for channel in self.channels}

        normalized_worker_links: list[dict[str, Any]] = []
        seen_worker_link_pairs: set[tuple[str, str]] = set()
        for raw_link in self.user_worker_links:
            user_id = str(raw_link.get("user_id") or "").strip()
            worker_id = str(raw_link.get("worker_id") or "").strip()
            if user_id not in valid_user_ids or worker_id not in valid_worker_ids:
                changed = True
                continue
            pair = (user_id, worker_id)
            if pair in seen_worker_link_pairs:
                changed = True
                continue
            normalized_worker_links.append(raw_link)
            seen_worker_link_pairs.add(pair)
        if normalized_worker_links != self.user_worker_links:
            self.user_worker_links = normalized_worker_links
            changed = True

        normalized_channel_links: list[dict[str, Any]] = []
        seen_channel_link_pairs: set[tuple[str, str]] = set()
        for raw_link in self.channel_user_links:
            channel_id = str(raw_link.get("channel_id") or "").strip()
            user_id = str(raw_link.get("user_id") or "").strip()
            if channel_id not in valid_channel_ids or user_id not in valid_user_ids:
                changed = True
                continue
            pair = (channel_id, user_id)
            if pair in seen_channel_link_pairs:
                changed = True
                continue
            normalized_channel_links.append(raw_link)
            seen_channel_link_pairs.add(pair)
        if normalized_channel_links != self.channel_user_links:
            self.channel_user_links = normalized_channel_links
            changed = True

        worker_by_id = {worker.id: worker for worker in self.workers}
        channel_by_id = {channel.id: channel for channel in self.channels}

        for worker in self.workers:
            assigned_user = self._assigned_user_for_worker(worker.id)
            if assigned_user is None:
                continue
            manager_id = self._resolved_user_manager_id(assigned_user)
            manager_name = assigned_user.manager_name or ""
            if manager_id and worker.manager_id != manager_id:
                worker.manager_id = manager_id
                changed = True
            if manager_name and worker.manager_name != manager_name:
                worker.manager_name = manager_name
                changed = True
            if manager_name and not str(worker.group or "").strip():
                worker.group = manager_name
                changed = True

        for channel in self.channels:
            linked_user_ids = [
                str(link.get("user_id") or "").strip()
                for link in self.channel_user_links
                if str(link.get("channel_id") or "").strip() == channel.id
            ]
            if len(linked_user_ids) != 1:
                continue
            try:
                linked_user = self._find_user(linked_user_ids[0])
            except KeyError:
                continue
            assigned_workers = self._assigned_workers_for_user(linked_user)
            assigned_worker_ids = {worker.id for worker in assigned_workers}
            assigned_worker = next((worker for worker in assigned_workers if worker.id == channel.worker_id), None)
            if assigned_worker is None and len(assigned_workers) == 1:
                assigned_worker = assigned_workers[0]
                if channel.worker_id != assigned_worker.id:
                    channel.worker_id = assigned_worker.id
                    changed = True
            if assigned_worker and channel.worker_name != assigned_worker.id:
                channel.worker_name = assigned_worker.id
                changed = True
            elif channel.worker_name != channel.worker_id and channel.worker_id in assigned_worker_ids:
                channel.worker_name = channel.worker_id
                changed = True
            resolved_manager_name = linked_user.manager_name or (assigned_worker.manager_name if assigned_worker else "")
            if resolved_manager_name and channel.manager_name != resolved_manager_name:
                channel.manager_name = resolved_manager_name
                changed = True

        for job in self.jobs:
            channel = channel_by_id.get(job.channel_id)
            if channel is None:
                continue
            if job.worker_name != channel.worker_id:
                job.worker_name = channel.worker_id
                changed = True
            resolved_manager_name = self._resolve_channel_manager_name(channel)
            if resolved_manager_name and job.manager_name != resolved_manager_name:
                job.manager_name = resolved_manager_name
                changed = True

        return changed

    def _build_session_payload(self, user: UserSummary) -> dict[str, Any]:
        return {
            "id": user.id,
            "username": user.username,
            "display_name": user.display_name,
            "role": user.role,
            "manager_name": user.manager_name,
        }

    def _find_user_by_username(self, username: str) -> UserSummary | None:
        normalized_username = username.strip().lower()
        return next((item for item in self.users if item.username.lower() == normalized_username), None)

    def _verify_user_password(self, user_id: str, password: str) -> bool:
        meta = self._user_meta_record(user_id)
        password_hash = str(meta.get("password_hash") or "").strip()
        if password_hash:
            return self._verify_password_hash(password, password_hash)
        legacy_password = str(meta.get("password") or "").strip()
        if legacy_password and legacy_password == password.strip():
            self._set_user_password(user_id, legacy_password, updated_at=meta.get("updated_at"))
            self._save_state()
            return True
        return False

    def authenticate_admin_user(self, username: str, password: str) -> dict[str, Any]:
        normalized_username = username.strip().lower()
        normalized_password = password.strip()
        if not normalized_username or not normalized_password:
            raise ValueError("Tên dang nh?p và m?t kh?u là b?t bu?c.")

        user = self._find_user_by_username(normalized_username)
        if not user:
            raise ValueError("Thông tin dang nh?p không h?p l?.")
        if user.role not in {"admin", "manager"}:
            raise ValueError("Tài kho?n này không du?c phép vào trang qu?n tr?.")

        if not self._verify_user_password(user.id, normalized_password):
            raise ValueError("Thông tin dang nh?p không h?p l?.")

        return self._build_session_payload(user)

    def authenticate_app_user(self, username: str, password: str) -> dict[str, Any]:
        normalized_username = username.strip().lower()
        normalized_password = password.strip()
        if not normalized_username or not normalized_password:
            raise ValueError("Tên dang nh?p và m?t kh?u là b?t bu?c.")

        user = self._find_user_by_username(normalized_username)
        if not user:
            raise ValueError("Thông tin dang nh?p không h?p l?.")
        if user.role != "user":
            raise ValueError("Tài kho?n này không du?c phép vào workspace user.")
        if not self._verify_user_password(user.id, normalized_password):
            raise ValueError("Thông tin dang nh?p không h?p l?.")

        return self._build_session_payload(user)

    def authenticate_login_user(self, username: str, password: str) -> dict[str, Any]:
        normalized_username = username.strip().lower()
        normalized_password = password.strip()
        if not normalized_username or not normalized_password:
            raise ValueError("Tên dang nh?p và m?t kh?u là b?t bu?c.")

        user = self._find_user_by_username(normalized_username)
        if not user:
            raise ValueError("Thông tin dang nh?p không h?p l?.")
        if not self._verify_user_password(user.id, normalized_password):
            raise ValueError("Thông tin dang nh?p không h?p l?.")
        return self._build_session_payload(user)

    def assert_admin_session_user(self, user_id: str, role: str) -> None:
        user = self._find_user(user_id)
        if user.role not in {"admin", "manager"}:
            raise ValueError("TÃ i khoáº£n khÃ´ng ÄÆ°á»£c phÃ©p vÃ o trang quáº£n trá».")
        if user.role != role:
            raise ValueError("Role session khong con hop le.")

    def assert_app_session_user(self, user_id: str, role: str) -> None:
        user = self._find_user(user_id)
        if user.role not in {"user", "manager", "admin"}:
            raise ValueError("Tai khoan khong duoc phep vao workspace.")
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
    def _guess_preview_kind(value: str | None) -> str | None:
        if not value:
            return None
        normalized = value.lower().split("?", 1)[0]
        extension = Path(normalized).suffix
        if extension in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
            return "image"
        if extension in {".mp4", ".mov", ".webm", ".m4v"}:
            return "video"
        return None

    @staticmethod
    def _format_render_duration(value: str | None) -> str:
        cleaned = (value or "").strip()
        if not cleaned:
            return "00:30:00"

        parts = cleaned.split(":")
        if len(parts) != 3 or not all(part.isdigit() for part in parts):
            return cleaned

        hours, minutes, seconds = (int(part) for part in parts)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    @staticmethod
    def _extract_google_drive_file_id(url: str | None) -> str | None:
        if not url:
            return None
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()
        if host not in {"drive.google.com", "docs.google.com"}:
            return None

        query_id = parse_qs(parsed.query).get("id", [])
        if query_id and query_id[0]:
            return query_id[0]

        match = re.search(r"/file/d/([^/]+)", parsed.path)
        if match:
            return match.group(1)

        return None

    @staticmethod
    def _extract_youtube_video_id(url: str | None) -> str | None:
        if not url:
            return None
        parsed = urlparse(url.strip())
        host = (parsed.hostname or "").lower()
        if host in {"www.youtube.com", "youtube.com"}:
            video_ids = parse_qs(parsed.query).get("v", [])
            return video_ids[0] if video_ids and video_ids[0] else None
        if host == "youtu.be":
            video_id = parsed.path.strip("/")
            return video_id or None
        return None

    @staticmethod
    def _extract_browser_session_channel_identity(url: str | None) -> str | None:
        if not url:
            return None
        parsed = urlparse(url.strip())
        host = (parsed.hostname or "").lower()
        path = parsed.path or ""
        query = parse_qs(parsed.query)
        if host == "studio.youtube.com":
            if "/channel/" in path:
                channel_id = path.split("/channel/", 1)[1].split("/", 1)[0].strip()
                return channel_id or None
            query_channel_ids = query.get("channel_id", [])
            return query_channel_ids[0].strip() if query_channel_ids and query_channel_ids[0].strip() else None
        if host in {"www.youtube.com", "youtube.com", "m.youtube.com"} and path.startswith("/channel/"):
            channel_id = path.split("/channel/", 1)[1].split("/", 1)[0].strip()
            return channel_id or None
        return None

    def _job_uploaded_asset_ids(self, job: RenderJobRecord) -> set[str]:
        return {
            str(asset.asset_id).strip()
            for asset in job.assets
            if asset.source_mode == "local" and str(asset.asset_id or "").strip()
        }

    def _job_local_asset_file_names(self, job: RenderJobRecord) -> set[str]:
        return {
            str(asset.file_name).strip()
            for asset in job.assets
            if asset.source_mode == "local" and str(asset.file_name or "").strip()
        }

    def _is_asset_referenced_by_other_job(self, asset_id: str, *, exclude_job_id: str | None = None) -> bool:
        normalized = asset_id.strip()
        if not normalized:
            return False
        for job in self.jobs:
            if exclude_job_id and job.id == exclude_job_id:
                continue
            if normalized in self._job_uploaded_asset_ids(job):
                return True
        return False

    def _is_local_file_referenced_by_other_job(self, file_name: str, *, exclude_job_id: str | None = None) -> bool:
        normalized = file_name.strip()
        if not normalized:
            return False
        for job in self.jobs:
            if exclude_job_id and job.id == exclude_job_id:
                continue
            if normalized in self._job_local_asset_file_names(job):
                return True
        return False

    def _remove_upload_session_file(self, session: UploadSessionRecord) -> None:
        relative_path = str(session.temp_path or "").strip()
        if not relative_path:
            return
        file_path = self._absolute_upload_path(relative_path)
        if file_path.exists():
            file_path.unlink(missing_ok=True)

    def _cleanup_uploaded_assets_for_job(self, job: RenderJobRecord, *, exclude_job_id: str | None = None) -> bool:
        removable_asset_ids = {
            asset_id
            for asset_id in self._job_uploaded_asset_ids(job)
            if not self._is_asset_referenced_by_other_job(asset_id, exclude_job_id=exclude_job_id)
        }
        removable_file_names = {
            file_name
            for file_name in self._job_local_asset_file_names(job)
            if not self._is_local_file_referenced_by_other_job(file_name, exclude_job_id=exclude_job_id)
        }
        if not removable_asset_ids and not removable_file_names:
            return False

        changed = False
        keep_sessions: list[UploadSessionRecord] = []
        removed_file_names: set[str] = set()
        for session in self.upload_sessions:
            asset_id = str(session.asset_id or "").strip()
            stored_file_name = str(session.stored_file_name or "").strip()
            temp_path_name = Path(str(session.temp_path or "").strip()).name
            if (
                (asset_id and asset_id in removable_asset_ids)
                or (stored_file_name and stored_file_name in removable_file_names)
                or (temp_path_name and temp_path_name in removable_file_names)
            ):
                self._remove_upload_session_file(session)
                if stored_file_name:
                    removed_file_names.add(stored_file_name)
                if temp_path_name:
                    removed_file_names.add(temp_path_name)
                changed = True
                continue
            keep_sessions.append(session)

        if changed:
            self.upload_sessions = keep_sessions
        for file_name in removable_file_names:
            if file_name in removed_file_names:
                continue
            file_path = self.upload_asset_dir / file_name
            if file_path.exists():
                file_path.unlink(missing_ok=True)
                changed = True
        return changed

    def _purge_job_artifacts(self, job: RenderJobRecord, *, exclude_job_id: str | None = None) -> None:
        self._cleanup_uploaded_assets_for_job(job, exclude_job_id=exclude_job_id)
        self._delete_job_preview_file(job)

    @staticmethod
    def _derive_legacy_job_phase_progress(job: RenderJobRecord) -> tuple[int, int, int]:
        download_progress = 0
        render_progress = 0
        upload_progress = 0

        if job.status == "downloading":
            download_progress = min(max(job.progress, 0), 100)
        elif job.status == "rendering":
            download_progress = 100
            render_progress = min(max(job.progress, 0), 100)
        elif job.status in {"uploading", "completed"}:
            download_progress = 100
            render_progress = 100
            upload_progress = 100 if job.status == "completed" and job.upload_started_at else min(max(job.progress, 0), 100)
        elif job.status in {"error", "cancelled"}:
            if job.upload_started_at:
                download_progress = 100
                render_progress = 100
                upload_progress = min(max(job.progress, 0), 100)
            elif job.started_at or job.claimed_at or job.completed_at:
                download_progress = 100
                render_progress = min(max(job.progress, 0), 100)

        return (
            min(max(download_progress, 0), 100),
            min(max(render_progress, 0), 100),
            min(max(upload_progress, 0), 100),
        )

    def _normalize_job_runtime_progress(self) -> bool:
        changed = False
        for job in self.jobs:
            if any(
                (
                    int(getattr(job, "download_progress", 0) or 0),
                    int(getattr(job, "render_progress", 0) or 0),
                    int(getattr(job, "upload_progress", 0) or 0),
                )
            ):
                continue
            derived_download, derived_render, derived_upload = self._derive_legacy_job_phase_progress(job)
            if job.download_progress != derived_download:
                job.download_progress = derived_download
                changed = True
            if job.render_progress != derived_render:
                job.render_progress = derived_render
                changed = True
            if job.upload_progress != derived_upload:
                job.upload_progress = derived_upload
                changed = True
        return changed

    @staticmethod
    def _job_status_label(status: str) -> str:
        mapping = {
            "pending": "Ch? t?o hàng d?i",
            "queueing": "Ðang x?p hàng",
            "downloading": "Ðang t?i ngu?n",
            "rendering": "Ðang render",
            "uploading": "Ðang upload",
            "completed": "Hoàn t?t",
            "cancelled": "Ðã h?y",
            "error": "L?i",
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

    def _job_user_status_view(self, job: RenderJobRecord) -> dict[str, Any]:
        if job.status == "completed":
            if job.upload_started_at:
                return {
                    "label": "Ðã upload YouTube",
                    "class": "inline-flex items-center rounded-full border border-sky-200 bg-sky-50 px-2.5 py-1 text-[10px] font-semibold text-sky-700",
                    "progress_text_class": "text-sky-600",
                    "progress_bar_class": "bg-sky-500",
                    "render_at": self._format_datetime(job.upload_started_at or job.completed_at),
                    "upload_at": self._format_datetime(job.completed_at),
                }
            return {
                "label": "Render hoàn t?t",
                "class": "inline-flex items-center rounded-full border border-indigo-200 bg-indigo-50 px-2.5 py-1 text-[10px] font-semibold text-indigo-700",
                "progress_text_class": "text-indigo-600",
                "progress_bar_class": "bg-indigo-500",
                "render_at": self._format_datetime(job.completed_at),
                "upload_at": "-",
            }

        progress_text_class = "text-amber-600"
        progress_bar_class = "bg-slate-300"
        if job.status == "downloading":
            progress_text_class = "text-sky-600"
            progress_bar_class = "bg-sky-400"
        elif job.status == "rendering":
            progress_text_class = "text-indigo-600"
            progress_bar_class = "bg-indigo-500"
        elif job.status == "uploading":
            progress_text_class = "text-cyan-600"
            progress_bar_class = "bg-cyan-500"
        elif job.status == "error":
            progress_text_class = "text-rose-600"
            progress_bar_class = "bg-rose-400"
        elif job.status == "cancelled":
            progress_text_class = "text-slate-500"
            progress_bar_class = "bg-slate-300"

        return {
            "label": self._job_status_label(job.status),
            "class": self._job_status_class(job.status),
            "progress_text_class": progress_text_class,
            "progress_bar_class": progress_bar_class,
            "render_at": self._format_datetime(job.upload_started_at),
            "upload_at": "-",
        }

    @staticmethod
    def _job_user_progress_view(job: RenderJobRecord) -> dict[str, int | str]:
        return {
            "mode": "download" if job.status == "downloading" else "pipeline",
            "download": min(max(int(job.download_progress or 0), 0), 100),
            "render": min(max(int(job.render_progress or 0), 0), 100),
            "upload": min(max(int(job.upload_progress or 0), 0), 100),
        }

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

    @classmethod
    def _default_worker_display_name(cls, worker_id: str | None, fallback: str | None = None) -> str:
        normalized_id = str(worker_id or "").strip()
        if normalized_id and normalized_id in cls.KNOWN_WORKER_DISPLAY_NAMES:
            return cls.KNOWN_WORKER_DISPLAY_NAMES[normalized_id]
        normalized_fallback = str(fallback or "").strip()
        return normalized_fallback or normalized_id or "-"

    def _normalize_known_worker_names(self) -> bool:
        changed = False
        for worker in self.workers:
            display_name = self._default_worker_display_name(worker.id, worker.name)
            if worker.name != display_name:
                worker.name = display_name
                changed = True
        return changed

    def _resolve_worker_display_name(self, worker_ref: str | None) -> str:
        if not worker_ref:
            return "-"
        normalized = worker_ref.strip()
        if not normalized:
            return "-"
        worker = next(
            (
                item
                for item in self.workers
                if normalized in {str(item.id or "").strip(), str(item.name or "").strip()}
            ),
            None,
        )
        if worker is None:
            return normalized
        display_name = str(worker.name or "").strip()
        return display_name or str(worker.id or normalized).strip() or normalized

    def _resolve_channel_worker_display_name(self, channel: ChannelRecord) -> str:
        return self._resolve_worker_display_name(channel.worker_id or channel.worker_name)

    def _resolve_job_worker_display_name(self, job: RenderJobRecord) -> str:
        return self._resolve_worker_display_name(job.worker_name)

    def _authenticate_worker(self, worker_id: str, shared_secret: str) -> WorkerRecord:
        if shared_secret != self.get_worker_shared_secret():
            raise ValueError("Worker shared secret khÃ´ng há»£p lá».")
        self._ensure_worker_not_deleted(worker_id)
        return self._find_worker(worker_id)

    def _refresh_queue_positions(self) -> None:
        queued_jobs = sorted(
            [
                job
                for job in self.jobs
                if job.status in {"pending", "queueing"} and (job.scheduled_at is None or job.scheduled_at <= self._now())
            ],
            key=lambda item: (item.queue_order or 10_000, item.created_at),
        )
        for index, job in enumerate(queued_jobs, start=1):
            job.queue_order = index
        for job in self.jobs:
            if job.status in {"completed", "cancelled", "error"}:
                job.queue_order = None

    @staticmethod
    def _worker_active_job_statuses() -> set[str]:
        return {"queueing", "downloading", "rendering", "uploading"}

    def _job_user_id(self, job: RenderJobRecord) -> str | None:
        for link in self.channel_user_links:
            if str(link.get("channel_id") or "").strip() != job.channel_id:
                continue
            user_id = str(link.get("user_id") or "").strip()
            if not user_id:
                continue
            try:
                self._find_user(user_id)
            except KeyError:
                continue
            return user_id
        return None

    def _job_dispatch_owner_key(self, job: RenderJobRecord) -> str:
        user_id = self._job_user_id(job)
        if user_id:
            return f"user:{user_id}"
        username = str(self._job_username(job) or "").strip().casefold()
        if username:
            return f"username:{username}"
        return f"job:{job.id}"

    def _pick_worker_round_robin_job(
        self,
        worker: WorkerRecord,
        candidates: list[RenderJobRecord],
    ) -> tuple[RenderJobRecord | None, str | None]:
        if not candidates:
            return None, None

        ordered_candidates = sorted(candidates, key=lambda item: (item.queue_order or 10_000, item.created_at))
        owner_order: list[str] = []
        jobs_by_owner: dict[str, list[RenderJobRecord]] = {}
        for job in ordered_candidates:
            owner_key = self._job_dispatch_owner_key(job)
            if owner_key not in jobs_by_owner:
                jobs_by_owner[owner_key] = []
                owner_order.append(owner_key)
            jobs_by_owner[owner_key].append(job)

        if not owner_order:
            return ordered_candidates[0], self._job_dispatch_owner_key(ordered_candidates[0])

        last_owner_key = str(self.worker_round_robin_cursor.get(worker.id) or "").strip()
        if last_owner_key and last_owner_key in owner_order:
            start_index = (owner_order.index(last_owner_key) + 1) % len(owner_order)
        else:
            start_index = 0

        for offset in range(len(owner_order)):
            owner_key = owner_order[(start_index + offset) % len(owner_order)]
            owner_jobs = jobs_by_owner.get(owner_key) or []
            if owner_jobs:
                return owner_jobs[0], owner_key

        return ordered_candidates[0], self._job_dispatch_owner_key(ordered_candidates[0])

    def _count_worker_running_jobs(self, worker: WorkerRecord) -> int:
        worker_aliases = {worker.id, worker.name, self._resolve_worker_display_name(worker.id)}
        active_statuses = self._worker_active_job_statuses()
        return sum(
            1
            for job in self.jobs
            if job.status in active_statuses
            and (
                job.claimed_by_worker_id == worker.id
                or (not job.claimed_by_worker_id and (job.worker_name in worker_aliases))
            )
        )

    def _worker_thread_summary(self, worker: WorkerRecord) -> dict[str, int | str]:
        running_threads = self._count_worker_running_jobs(worker)
        max_threads = self._effective_worker_thread_limit(worker)
        return {
            "running_threads": running_threads,
            "max_threads": max_threads,
            "thread_text": f"{running_threads}/{max_threads}",
        }

    def _sync_worker_runtime_status(self, worker: WorkerRecord) -> None:
        running_threads = self._count_worker_running_jobs(worker)
        worker.status = "busy" if running_threads > 0 else "online"

    def _refresh_worker_job_leases(
        self,
        worker_id: str,
        now: datetime | None = None,
        *,
        job_ids: list[str] | None = None,
    ) -> None:
        lease_base = now or self._now()
        active_statuses = self._worker_active_job_statuses()
        allowed_job_ids = {str(job_id).strip() for job_id in (job_ids or []) if str(job_id).strip()}
        lease_duration = timedelta(seconds=self._worker_job_lease_seconds())
        for job in self.jobs:
            if job.claimed_by_worker_id == worker_id and job.status in active_statuses:
                if allowed_job_ids and job.id not in allowed_job_ids:
                    continue
                job.lease_expires_at = lease_base + lease_duration

    def register_worker(self, payload: WorkerRegisterPayload) -> WorkerControlResponse:
        completed_task: dict[str, Any] | None = None
        worker_snapshot: WorkerRecord | None = None
        vps_ip = ""
        with self._worker_state_lock:
            if payload.shared_secret != self.get_worker_shared_secret():
                raise ValueError("Worker shared secret khÃ´ng há»£p lá».")
            self._ensure_worker_not_deleted(payload.worker_id)

            now = self._now(trim=False)
            worker_display_name = self._default_worker_display_name(payload.worker_id, payload.name)
            public_base_url = str(payload.public_base_url or "").strip() or None
            existing = next((worker for worker in self.workers if worker.id == payload.worker_id), None)
            install_task = next(
                (
                    task
                    for task in self.worker_operation_tasks
                    if str(task.get("kind") or "").strip() == "install"
                    and str(task.get("worker_id") or "").strip() == payload.worker_id
                ),
                None,
            )
            install_task_manager_id = str(install_task.get("manager_id") or "").strip() if install_task else ""
            install_task_manager_name = str(install_task.get("manager_name") or "").strip() if install_task else ""
            install_task_group = str(install_task.get("group") or "").strip() if install_task else ""
            manager = None
            if install_task_manager_id:
                manager = next(
                    (
                        user
                        for user in self.users
                        if user.id == install_task_manager_id and user.role == "manager"
                    ),
                    None,
                )
            if manager is None:
                manager = next((user for user in self.users if user.username == payload.manager_name and user.role == "manager"), None)
            resolved_manager_name = (
                manager.username if manager else (install_task_manager_name or str(payload.manager_name or "").strip() or "system")
            )
            resolved_group = install_task_group or str(payload.group or "").strip() or resolved_manager_name
            normalized_threads = self._normalize_requested_worker_threads(payload.threads)
            if existing is None:
                worker = WorkerRecord(
                    id=payload.worker_id,
                    name=worker_display_name,
                    manager_id=manager.id if manager else None,
                    manager_name=resolved_manager_name,
                    group=resolved_group,
                    created_at=now,
                    status="online",
                    capacity=payload.capacity,
                    load_percent=0,
                    ram_percent=0,
                    ram_used_gb=0,
                    ram_total_gb=0,
                    bandwidth_kbps=0,
                    disk_used_gb=0,
                    disk_total_gb=payload.disk_total_gb,
                    threads=normalized_threads,
                    last_seen_at=now,
                    public_base_url=public_base_url,
                    browser_session_enabled=payload.browser_session_enabled,
                    browser_display_base=payload.browser_display_base,
                    browser_vnc_port_base=payload.browser_vnc_port_base,
                    browser_web_port_base=payload.browser_web_port_base,
                    browser_debug_port_base=payload.browser_debug_port_base,
                )
                worker.offline_since_at = None
                worker.offline_alert_sent_at = None
                self.workers.append(worker)
            else:
                existing.name = worker_display_name
                existing.manager_id = manager.id if manager else existing.manager_id
                existing.manager_name = resolved_manager_name
                payload_group = resolved_group
                current_group = str(existing.group or "").strip()
                if payload_group:
                    if not current_group or current_group in {
                        str(existing.manager_name or "").strip(),
                        resolved_manager_name,
                    }:
                        existing.group = payload_group
                elif not current_group:
                    existing.group = resolved_manager_name
                existing.created_at = existing.created_at or now
                existing.capacity = max(int(existing.capacity or 1), int(payload.capacity or 1))
                existing.threads = self._normalize_requested_worker_threads(
                    payload.threads or existing.threads or 1,
                )
                existing.disk_total_gb = payload.disk_total_gb or existing.disk_total_gb
                existing.status = "online"
                existing.last_seen_at = now
                existing.offline_since_at = None
                existing.offline_alert_sent_at = None
                existing.public_base_url = public_base_url or existing.public_base_url
                existing.browser_session_enabled = payload.browser_session_enabled
                existing.browser_display_base = payload.browser_display_base
                existing.browser_vnc_port_base = payload.browser_vnc_port_base
                existing.browser_web_port_base = payload.browser_web_port_base
                existing.browser_debug_port_base = payload.browser_debug_port_base
                worker = existing

            if self._looks_like_ipv4(worker_display_name):
                existing_profile = self.worker_connection_profiles.get(payload.worker_id) or {}
                self._remember_worker_connection_profile(
                    payload.worker_id,
                    vps_ip=worker_display_name,
                    ssh_user=str(existing_profile.get("ssh_user") or "root"),
                )
            completed_task = deepcopy(install_task) if install_task is not None else None
            vps_ip = str(payload.name or "").strip() or worker_display_name
            self.worker_operation_tasks = [
                task
                for task in self.worker_operation_tasks
                if not (
                    str(task.get("kind") or "").strip() == "install"
                    and str(task.get("worker_id") or "").strip() == payload.worker_id
                )
            ]

            self._save_state()
            worker_snapshot = deepcopy(worker)
        if completed_task is not None and worker_snapshot is not None:
            self._notify_telegram_chat_ids(
                self._bot_operation_recipient_chat_ids(completed_task),
                self._bot_install_completed_message(
                    completed_task,
                    worker_name=self._resolve_worker_display_name(worker_snapshot.id),
                    worker_id=worker_snapshot.id,
                    vps_ip=vps_ip or self._resolve_worker_display_name(worker_snapshot.id),
                ),
            )
        return WorkerControlResponse(ok=True, worker=worker_snapshot)

    def heartbeat_worker(self, payload: WorkerHeartbeatPayload) -> WorkerControlResponse:
        with self._worker_state_lock:
            worker = self._authenticate_worker(payload.worker_id, payload.shared_secret)
            now = self._now(trim=False)
            worker.load_percent = payload.load_percent
            worker.ram_percent = payload.ram_percent
            worker.ram_used_gb = payload.ram_used_gb
            worker.ram_total_gb = payload.ram_total_gb or worker.ram_total_gb
            worker.bandwidth_kbps = payload.bandwidth_kbps
            worker.disk_used_gb = payload.disk_used_gb
            worker.disk_total_gb = payload.disk_total_gb or worker.disk_total_gb
            worker.threads = self._normalize_requested_worker_threads(payload.threads)
            worker.last_seen_at = now
            worker.offline_since_at = None
            worker.offline_alert_sent_at = None
            if payload.public_base_url is not None:
                worker.public_base_url = str(payload.public_base_url).strip() or None
            if payload.browser_session_enabled is not None:
                worker.browser_session_enabled = bool(payload.browser_session_enabled)
            if payload.browser_display_base is not None:
                worker.browser_display_base = payload.browser_display_base
            if payload.browser_vnc_port_base is not None:
                worker.browser_vnc_port_base = payload.browser_vnc_port_base
            if payload.browser_web_port_base is not None:
                worker.browser_web_port_base = payload.browser_web_port_base
            if payload.browser_debug_port_base is not None:
                worker.browser_debug_port_base = payload.browser_debug_port_base
            if payload.active_job_ids is None:
                self._reconcile_worker_jobs_from_heartbeat(
                    worker,
                    active_job_ids=[],
                    now=now,
                )
            else:
                self._reconcile_worker_jobs_from_heartbeat(
                    worker,
                    active_job_ids=payload.active_job_ids,
                    now=now,
                )
            if self._count_worker_running_jobs(worker) > 0:
                worker.status = "busy"
            else:
                worker.status = payload.status
            self._save_state()
            return WorkerControlResponse(ok=True, worker=deepcopy(worker))

    def claim_next_job(self, worker_id: str, shared_secret: str) -> tuple[WorkerRecord, RenderJobRecord | None]:
        with self._worker_state_lock:
            worker = self._authenticate_worker(worker_id, shared_secret)
            now = self._now()
            max_threads = self._effective_worker_thread_limit(worker)
            active_jobs = self._count_worker_running_jobs(worker)
            if active_jobs >= max_threads:
                self._sync_worker_runtime_status(worker)
                self._save_state()
                return deepcopy(worker), None

            candidates = [
                job
                for job in self.jobs
                if job.worker_name in {worker.id, worker.name}
                and job.status in {"pending", "queueing"}
                and (job.scheduled_at is None or job.scheduled_at <= now)
                and (job.claimed_by_worker_id is None or (job.lease_expires_at and job.lease_expires_at <= now))
            ]

            if not candidates:
                self._sync_worker_runtime_status(worker)
                self._save_state()
                return deepcopy(worker), None

            job, owner_key = self._pick_worker_round_robin_job(worker, candidates)
            if job is None:
                self._sync_worker_runtime_status(worker)
                self._save_state()
                return deepcopy(worker), None
            job.status = "queueing"
            job.claimed_by_worker_id = worker_id
            job.claimed_at = now
            if owner_key:
                self.worker_round_robin_cursor[worker.id] = owner_key
            self._refresh_worker_job_leases(worker_id, now, job_ids=[job.id])
            job.started_at = job.started_at or now
            self._sync_worker_runtime_status(worker)
            self._refresh_queue_positions()
            self._save_state()
            return deepcopy(worker), deepcopy(job)

    def _find_claimed_job(self, job_id: str, worker_id: str) -> RenderJobRecord:
        for job in self.jobs:
            if job.id == job_id:
                if job.claimed_by_worker_id not in {None, worker_id} and job.status not in {"completed", "cancelled", "error"}:
                    raise ValueError("Job dang thu?c worker khác.")
                return job
        raise KeyError(job_id)

    @staticmethod
    def _ensure_worker_job_can_continue(job: RenderJobRecord) -> None:
        if job.status == "cancelled":
            raise ValueError("Job da bi huy tren control plane.")
        if job.status == "completed":
            raise ValueError("Job da hoan tat tren control plane.")
        if job.status == "error":
            raise ValueError("Job da dung voi trang thai loi tren control plane.")

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
        with self._worker_state_lock:
            worker = self._authenticate_worker(worker_id, shared_secret)
            job = self._find_claimed_job(job_id, worker_id)
            self._ensure_worker_job_can_continue(job)
            now = self._now()

            job.claimed_by_worker_id = worker_id
            job.claimed_at = job.claimed_at or now
            self._refresh_worker_job_leases(worker_id, now, job_ids=[job.id])
            job.started_at = job.started_at or now
            job.status = status  # type: ignore[assignment]
            bounded_progress = max(0, min(100, progress))
            job.progress = bounded_progress
            job.status_message = (message or "").strip() or None
            job.error_message = None
            if status == "downloading" and job.download_started_at is None:
                job.download_started_at = now
            if status == "downloading":
                job.download_progress = max(int(job.download_progress or 0), bounded_progress)
                job.render_progress = 0
                job.upload_progress = 0
            if status == "uploading" and job.upload_started_at is None:
                job.upload_started_at = now
            if status == "rendering":
                job.download_progress = max(int(job.download_progress or 0), 100)
                job.render_progress = max(int(job.render_progress or 0), bounded_progress)
                job.upload_progress = 0
            elif status == "uploading":
                job.download_progress = max(int(job.download_progress or 0), 100)
                job.render_progress = max(int(job.render_progress or 0), 100)
                job.upload_progress = max(int(job.upload_progress or 0), bounded_progress)
            self._sync_worker_runtime_status(worker)

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
        with self._worker_state_lock:
            worker = self._authenticate_worker(worker_id, shared_secret)
            job = self._find_claimed_job(job_id, worker_id)
            self._ensure_worker_job_can_continue(job)
            now = self._now()

            job.status = "completed"
            job.progress = 100
            job.completed_at = now
            job.can_cancel = False
            job.output_url = output_url
            job.status_message = (message or "").strip() or None
            job.error_message = None
            job.lease_expires_at = None
            job.download_progress = max(int(job.download_progress or 0), 100 if job.started_at or job.download_started_at else 0)
            job.render_progress = max(int(job.render_progress or 0), 100 if job.started_at else 0)
            if job.upload_started_at:
                job.upload_progress = 100
            self._sync_worker_runtime_status(worker)
            if job.upload_started_at:
                self._cleanup_uploaded_assets_for_job(job, exclude_job_id=job.id)
            self._refresh_queue_positions()
            self._save_state()
            return deepcopy(job)

    def fail_worker_job(self, *, job_id: str, worker_id: str, shared_secret: str, message: str) -> RenderJobRecord:
        with self._worker_state_lock:
            worker = self._authenticate_worker(worker_id, shared_secret)
            job = self._find_claimed_job(job_id, worker_id)
            now = self._now()

            if job.status == "cancelled":
                job.can_cancel = False
                job.lease_expires_at = None
                self._sync_worker_runtime_status(worker)
                self._refresh_queue_positions()
                self._save_state()
                return deepcopy(job)

            job.status = "error"
            job.completed_at = now
            job.can_cancel = False
            job.error_message = message
            job.status_message = None
            job.lease_expires_at = None
            if job.upload_started_at:
                job.download_progress = max(int(job.download_progress or 0), 100)
                job.render_progress = max(int(job.render_progress or 0), 100)
                job.upload_progress = max(int(job.upload_progress or 0), min(max(job.progress, 0), 100))
            elif job.started_at or job.download_started_at:
                job.download_progress = max(int(job.download_progress or 0), 100 if job.download_started_at else 0)
                job.render_progress = max(int(job.render_progress or 0), min(max(job.progress, 0), 100))
            self._sync_worker_runtime_status(worker)
            self._refresh_queue_positions()
            self._save_state()
            return deepcopy(job)

    def _find_channel(self, channel_id: str) -> ChannelRecord:
        for channel in self.channels:
            if channel.id == channel_id:
                return channel
        raise KeyError(channel_id)

    def _require_workspace_user(self, user_id: str) -> UserSummary:
        user = self._find_user(user_id)
        if user.role not in {"user", "manager", "admin"}:
            raise ValueError("Tai khoan khong duoc phep vao workspace user.")
        return user

    def _workspace_workers_for_user(self, user: UserSummary | str) -> list[WorkerRecord]:
        current_user = self._require_workspace_user(user if isinstance(user, str) else user.id)
        workers = self._assigned_workers_for_user(current_user.id)
        return sorted(
            workers,
            key=lambda worker: (
                str(self._resolve_worker_display_name(worker.id) or "").casefold(),
                str(worker.id or "").casefold(),
            ),
        )

    def _workspace_worker_ids_for_user(self, user: UserSummary | str) -> set[str]:
        return {worker.id for worker in self._workspace_workers_for_user(user)}

    def _workspace_channels_for_user(self, user: UserSummary | str) -> list[ChannelRecord]:
        current_user = self._require_workspace_user(user if isinstance(user, str) else user.id)
        worker_ids = self._workspace_worker_ids_for_user(current_user)
        linked_channel_ids = self._user_channel_ids(current_user.id)
        channels = [channel for channel in self.channels if channel.id in linked_channel_ids]
        if worker_ids:
            channels = [channel for channel in channels if channel.worker_id in worker_ids]
        return channels

    def _user_channel_ids(self, user_id: str) -> set[str]:
        return {link["channel_id"] for link in self.channel_user_links if link["user_id"] == user_id}

    def _user_has_channel_access(self, user_id: str, channel_id: str) -> bool:
        user = self._require_workspace_user(user_id)
        return any(channel.id == channel_id for channel in self._workspace_channels_for_user(user))

    def _user_jobs_for_workspace(self, user_id: str) -> list[RenderJobRecord]:
        user = self._require_workspace_user(user_id)
        channel_ids = {channel.id for channel in self._workspace_channels_for_user(user)}
        jobs = [job for job in self.jobs if job.channel_id in channel_ids]
        assigned_workers = self._workspace_workers_for_user(user)
        if assigned_workers:
            allowed_worker_aliases = {
                alias
                for worker in assigned_workers
                for alias in {str(worker.id or "").strip(), str(worker.name or "").strip()}
                if alias
            }
            jobs = [job for job in jobs if (job.worker_name or "") in allowed_worker_aliases]
        return sorted(deepcopy(jobs), key=lambda item: item.created_at, reverse=True)

    def _find_user_visible_job(self, user_id: str, job_id: str) -> RenderJobRecord:
        job = self._find_job(job_id)
        if not self._user_has_channel_access(user_id, job.channel_id):
            raise KeyError(job_id)
        return job

    def _assigned_worker_link_for_user(self, user_id: str) -> dict[str, Any] | None:
        links = self._assigned_worker_links_for_user(user_id)
        if not links:
            return None
        return links[0]

    def _assigned_worker_links_for_user(self, user_id: str) -> list[dict[str, Any]]:
        links = [link for link in self.user_worker_links if str(link.get("user_id") or "").strip() == str(user_id or "").strip()]
        links.sort(key=lambda item: int(item.get("id") or 0))
        return links

    def _assigned_workers_for_user(self, user: UserSummary | str) -> list[WorkerRecord]:
        user_id = user.id if isinstance(user, UserSummary) else user
        workers: list[WorkerRecord] = []
        seen_worker_ids: set[str] = set()
        for link in self._assigned_worker_links_for_user(user_id):
            worker_id = str(link.get("worker_id") or "").strip()
            if not worker_id or worker_id in seen_worker_ids:
                continue
            try:
                worker = self._find_worker(worker_id)
            except KeyError:
                continue
            workers.append(worker)
            seen_worker_ids.add(worker_id)
        return workers

    def _assigned_worker_for_user(self, user: UserSummary | str) -> WorkerRecord | None:
        workers = self._assigned_workers_for_user(user)
        if not workers:
            return None
        return workers[0]

    def _pick_worker_for_user(self, user: UserSummary, worker_id: str | None = None) -> WorkerRecord:
        workers = self._workspace_workers_for_user(user)
        if worker_id:
            normalized_worker_id = str(worker_id).strip()
            worker = next((item for item in workers if item.id == normalized_worker_id), None)
            if worker is not None:
                return worker
            raise ValueError("VPS duoc chon khong nam trong danh sach da cap cho user.")
        worker = workers[0] if workers else None
        if worker is not None:
            return worker
        raise ValueError("User nay chua duoc cap VPS render/upload.")

    def _channel_matches_user_worker(self, user: UserSummary, channel: ChannelRecord) -> bool:
        assigned_worker_ids = {worker.id for worker in self._workspace_workers_for_user(user)}
        if not assigned_worker_ids:
            return False
        return channel.worker_id in assigned_worker_ids

    def _assert_channel_matches_user_worker(self, user: UserSummary, channel: ChannelRecord) -> WorkerRecord:
        assigned_workers = self._workspace_workers_for_user(user)
        if not assigned_workers:
            raise ValueError("User nay chua duoc cap VPS render/upload.")
        worker = next((item for item in assigned_workers if item.id == channel.worker_id), None)
        if worker is not None:
            return worker
        assigned_label = ", ".join(self._resolve_worker_display_name(worker.id) for worker in assigned_workers)
        channel_label = self._resolve_channel_worker_display_name(channel)
        raise ValueError(
            f"Kenh nay dang gan voi VPS {channel_label}. User {user.username} hien duoc cap cac VPS: {assigned_label}. "
            "Hay reconnect kenh tren mot VPS da duoc cap truoc khi render/upload."
        )

    @staticmethod
    def _worker_browser_base(worker: WorkerRecord) -> tuple[int, int, int, int]:
        return (
            int(worker.browser_display_base or 90),
            int(worker.browser_vnc_port_base or 15900),
            int(worker.browser_web_port_base or 16080),
            int(worker.browser_debug_port_base or 19220),
        )

    def _assert_worker_browser_ready(self, worker: WorkerRecord) -> None:
        worker_label = self._resolve_worker_display_name(worker.id)
        if not worker.browser_session_enabled:
            raise ValueError(f"VPS {worker_label} chua bat browser session.")
        if not str(worker.public_base_url or "").strip():
            raise ValueError(f"VPS {worker_label} chua khai bao public_base_url cho noVNC.")

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

    def _find_browser_session(self, session_id: str) -> BrowserSessionRecord:
        for session in self.browser_sessions:
            if session.session_id == session_id:
                return session
        raise KeyError(session_id)

    def _find_user_browser_session(self, user_id: str, session_id: str) -> BrowserSessionRecord:
        session = self._find_browser_session(session_id)
        if session.owner_user_id != user_id:
            raise KeyError(session_id)
        return session

    def _browser_session_response(self, session: BrowserSessionRecord) -> BrowserSessionResponse:
        return BrowserSessionResponse(
            session_id=session.session_id,
            status=session.status,
            target_worker_id=session.target_worker_id,
            target_worker_name=session.target_worker_name,
            target_worker_public_base_url=session.target_worker_public_base_url,
            novnc_url=session.novnc_url,
            access_password=session.access_password,
            expires_at=session.expires_at,
            current_url=session.current_url,
            current_title=session.current_title,
            detected_channel_id=session.detected_channel_id,
            detected_channel_name=session.detected_channel_name,
            channel_record_id=session.channel_record_id,
            last_error=session.last_error,
        )

    def _cleanup_stale_browser_sessions(self) -> None:
        now = self._now(trim=False)
        changed = False
        keep_sessions: list[BrowserSessionRecord] = []
        for session in self.browser_sessions:
            if session.status in {"closed", "expired"}:
                if session.expires_at < now - timedelta(hours=12):
                    changed = True
                    continue
                keep_sessions.append(session)
                continue

            if session.expires_at <= now:
                session.status = "expired"
                changed = True
                keep_sessions.append(session)
                continue
            keep_sessions.append(session)

        if changed:
            self.browser_sessions = keep_sessions
            self._save_state()

    def _active_browser_session_for_user(self, user_id: str) -> BrowserSessionRecord | None:
        self._cleanup_stale_browser_sessions()
        candidates = [
            session
            for session in self.browser_sessions
            if session.owner_user_id == user_id
            and session.status in {"launching", "awaiting_confirmation", "confirmed"}
            and session.expires_at > self._now(trim=False)
        ]
        if not candidates:
            return None
        return sorted(candidates, key=lambda item: item.created_at, reverse=True)[0]

    def _allocate_browser_ports_for_worker(self, worker: WorkerRecord) -> tuple[int, int, int, int]:
        display_base, vnc_base, web_base, debug_base = self._worker_browser_base(worker)
        now = self._now(trim=False)
        taken = {
            (session.display_number, session.vnc_port, session.web_port, session.debug_port)
            for session in self.browser_sessions
            if session.target_worker_id == worker.id
            if (
                session.status in {"launching", "awaiting_confirmation", "confirmed"}
                or session.expires_at >= now - timedelta(minutes=5)
            )
        }
        for offset in range(0, 200):
            candidate = (
                display_base + offset,
                vnc_base + offset,
                web_base + offset,
                debug_base + offset,
            )
            if candidate not in taken:
                return candidate
        raise ValueError(
            f"Da het pool port browser session tren VPS {self._resolve_worker_display_name(worker.id)}."
        )

    def _sync_browser_session_details(self, session: BrowserSessionRecord) -> BrowserSessionRecord:
        if not session.novnc_url and session.target_worker_public_base_url:
            session.novnc_url = self._build_browser_session_novnc_url(
                session.target_worker_public_base_url,
                session.web_port,
                session.access_password,
            )
        return session

    @staticmethod
    def _build_browser_session_novnc_url(base_url: str, web_port: int, access_password: str) -> str:
        encoded_password = quote(access_password, safe="")
        return (
            f"{base_url.rstrip('/')}:{web_port}/vnc.html?autoconnect=1&resize=scale&view_only=0"
            f"#password={encoded_password}"
        )

    @staticmethod
    def _extract_html_meta_content(document: str, *patterns: str) -> str | None:
        for pattern in patterns:
            match = re.search(pattern, document, re.IGNORECASE)
            if not match:
                continue
            value = html.unescape(str(match.group(1) or "").strip())
            if value:
                return value
        return None

    def _fetch_public_youtube_channel_metadata(self, channel_id: str) -> dict[str, str | None]:
        cleaned_channel_id = str(channel_id or "").strip()
        if not cleaned_channel_id:
            return {"channel_name": None, "avatar_url": None}

        request = Request(
            f"https://www.youtube.com/channel/{cleaned_channel_id}",
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36"
                )
            },
        )
        try:
            with urlopen(request, timeout=10) as response:
                document = response.read().decode("utf-8", errors="replace")
        except (HTTPError, URLError, TimeoutError, OSError):
            return {"channel_name": None, "avatar_url": None}

        channel_name = self._extract_html_meta_content(
            document,
            r'<meta\s+property="og:title"\s+content="([^"]+)"',
            r'<meta\s+name="title"\s+content="([^"]+)"',
            r"<title>([^<]+)</title>",
        )
        if channel_name:
            channel_name = re.sub(r"\s*-\s*YouTube\s*$", "", channel_name, flags=re.IGNORECASE).strip()
            if channel_name.lower() in {"youtube", "youtube studio", "studio"}:
                channel_name = None

        avatar_url = self._extract_html_meta_content(
            document,
            r'<meta\s+property="og:image"\s+content="([^"]+)"',
            r'<link\s+rel="image_src"\s+href="([^"]+)"',
        )
        return {
            "channel_name": channel_name,
            "avatar_url": avatar_url,
        }

    @staticmethod
    def _browser_channel_metadata_is_generic(channel: ChannelRecord) -> bool:
        if channel.connection_mode != "browser_profile":
            return False
        normalized_name = str(channel.name or "").strip().lower()
        if not normalized_name:
            return True
        if normalized_name in {
            "trang t?ng quan c?a kênh",
            "trang tong quan cua kenh",
            "youtube studio",
            "dashboard",
            "studio",
        }:
            return True
        return not str(channel.avatar_url or "").strip()

    def _refresh_browser_channel_metadata(self, channel: ChannelRecord) -> bool:
        if not self._browser_channel_metadata_is_generic(channel):
            return False

        public_metadata = self._fetch_public_youtube_channel_metadata(channel.channel_id)
        resolved_name = str(public_metadata.get("channel_name") or "").strip()
        resolved_avatar = str(public_metadata.get("avatar_url") or "").strip() or None
        changed = False

        if resolved_name and channel.name != resolved_name:
            channel.name = resolved_name
            changed = True
        if resolved_avatar and channel.avatar_url != resolved_avatar:
            channel.avatar_url = resolved_avatar
            changed = True

        if not changed:
            return False

        for job in self.jobs:
            if job.channel_id != channel.id:
                continue
            job.channel_name = channel.name
            job.channel_avatar_url = channel.avatar_url
        return True

    def _refresh_browser_channels_metadata(self, channels: list[ChannelRecord]) -> bool:
        changed = False
        for channel in channels:
            if self._refresh_browser_channel_metadata(channel):
                changed = True
        if changed:
            self._save_state()
        return changed

    def _upsert_browser_connected_channel(
        self,
        *,
        user: UserSummary,
        session: BrowserSessionRecord,
        channel_id: str,
        channel_name: str,
        avatar_url: str | None = None,
    ) -> ChannelRecord:
        worker = self._pick_worker_for_user(user, session.target_worker_id)
        existing_channel = next((item for item in self.channels if item.channel_id == channel_id), None)
        now = self._now()
        if existing_channel:
            linked_user_ids = {
                str(link.get("user_id") or "").strip()
                for link in self.channel_user_links
                if str(link.get("channel_id") or "").strip() == existing_channel.id
            }
            if linked_user_ids and str(user.id or "").strip() not in linked_user_ids:
                raise ValueError(
                    "Kênh này dang g?n v?i tài kho?n khác trên h? th?ng. "
                    "Hãy dang xu?t ho?c ch?n dúng kênh tru?c khi xác nh?n."
                )
            channel = existing_channel
        else:
            channel = ChannelRecord(
                id=f"channel-{uuid4().hex[:8]}",
                name=channel_name,
                channel_id=channel_id,
                avatar_url=avatar_url,
                worker_id=worker.id,
                worker_name=worker.id,
                manager_name=user.manager_name or worker.manager_name,
                status="connected",
                connection_mode="browser_profile",
            )
            self.channels.append(channel)

        previous_browser_profile_key = channel.browser_profile_key
        previous_connection_mode = channel.connection_mode
        channel.name = channel_name
        channel.status = "connected"
        channel.worker_id = worker.id
        channel.worker_name = worker.id
        channel.manager_name = user.manager_name or worker.manager_name
        channel.connection_mode = "browser_profile"
        channel.browser_profile_key = session.profile_key
        channel.browser_profile_path = session.profile_path
        channel.browser_connected_at = now
        if avatar_url:
            channel.avatar_url = avatar_url
        if (
            previous_connection_mode == "browser_profile"
            and previous_browser_profile_key
            and previous_browser_profile_key != session.profile_key
        ):
            self._queue_browser_profile_cleanup(
                worker_id=worker.id,
                profile_key=previous_browser_profile_key,
            )
        for job in self.jobs:
            if job.channel_id != channel.id:
                continue
            job.channel_name = channel.name
            job.channel_avatar_url = channel.avatar_url
        self._ensure_channel_user_link(channel_id=channel.id, user_id=user.id)
        return channel

    def create_browser_session(self, user_id: str, worker_id: str | None = None) -> BrowserSessionResponse:
        user = self._require_workspace_user(user_id)
        worker = self._pick_worker_for_user(user, worker_id)
        existing = self._active_browser_session_for_user(user.id)
        if existing:
            self._sync_browser_session_details(existing)
            existing.status = "closed"
            existing.expires_at = self._now(trim=False)
            if existing.target_worker_id != worker.id:
                existing.last_error = "Session cu dã dóng do VPS du?c c?p dã thay d?i."
            else:
                existing.last_error = "Session cu dã dóng d? m? phiên thêm kênh m?i."
            self._queue_browser_profile_cleanup_if_orphan(
                worker_id=existing.target_worker_id,
                profile_key=existing.profile_key,
            )
            self._save_state()

        self._close_orphan_browser_sessions_for_user(user.id)
        self._assert_worker_browser_ready(worker)
        display_number, vnc_port, web_port, debug_port = self._allocate_browser_ports_for_worker(worker)
        now = self._now(trim=False)
        lifetime_minutes = self.browser_runtime.load_config().lifetime_minutes
        session = BrowserSessionRecord(
            session_id=f"browser-{uuid4().hex[:12]}",
            owner_user_id=user.id,
            owner_username=user.username,
            target_worker_id=worker.id,
            target_worker_name=self._resolve_worker_display_name(worker.id),
            target_worker_public_base_url=str(worker.public_base_url or "").rstrip("/") or None,
            profile_key=f"{user.username}-{uuid4().hex[:10]}",
            display_number=display_number,
            vnc_port=vnc_port,
            web_port=web_port,
            debug_port=debug_port,
            access_password=secrets.token_urlsafe(9),
            status="launching",
            created_at=now,
            expires_at=now + timedelta(minutes=lifetime_minutes),
        )
        self.browser_sessions.append(session)
        self._sync_browser_session_details(session)
        self._save_state()
        return self._browser_session_response(session)

    def get_browser_session(self, user_id: str, session_id: str) -> BrowserSessionResponse:
        self._require_workspace_user(user_id)
        self._cleanup_stale_browser_sessions()
        session = self._find_user_browser_session(user_id, session_id)
        self._sync_browser_session_details(session)
        self._save_state()
        return self._browser_session_response(session)

    def confirm_browser_session(self, user_id: str, session_id: str) -> dict[str, Any]:
        user = self._require_workspace_user(user_id)
        self._cleanup_stale_browser_sessions()
        session = self._find_user_browser_session(user.id, session_id)
        if session.status not in {"awaiting_confirmation", "confirmed"}:
            raise ValueError("Browser session không còn ? tr?ng thái xác nh?n h?p l?.")

        self._sync_browser_session_details(session)
        session_channel_id = self._extract_browser_session_channel_identity(session.current_url)
        channel_id = str(session_channel_id or session.detected_channel_id or "").strip()
        channel_name = str(session.detected_channel_name or "").strip() or channel_id
        if not channel_id:
            raise ValueError("Chua nh?n di?n du?c channel. Hãy m? YouTube Studio dúng kênh r?i th? l?i.")
        if not session_channel_id:
            raise ValueError(
                "Phiên dang nh?p chua d?ng t?i YouTube Studio c?a kênh c?n thêm. "
                "Hãy m? dúng YouTube Studio r?i th? xác nh?n l?i."
            )

        session.detected_channel_id = channel_id
        public_metadata = self._fetch_public_youtube_channel_metadata(channel_id)
        channel_name = str(public_metadata.get("channel_name") or "").strip() or channel_name
        avatar_url = str(public_metadata.get("avatar_url") or "").strip() or None

        channel = self._upsert_browser_connected_channel(
            user=user,
            session=session,
            channel_id=channel_id,
            channel_name=channel_name or channel_id,
            avatar_url=avatar_url,
        )
        confirmed_at = self._now(trim=False)
        session.status = "closed"
        session.confirmed_at = confirmed_at
        session.channel_record_id = channel.id
        session.expires_at = confirmed_at
        self._save_state()
        return {
            "session": self._browser_session_response(session).model_dump(mode="json"),
            "channel": {
                "channel_record_id": channel.id,
                "channel_id": channel.channel_id,
                "channel_name": channel.name,
                "connection_mode": channel.connection_mode,
            },
        }

    def close_browser_session(self, user_id: str, session_id: str) -> BrowserSessionResponse:
        self._require_workspace_user(user_id)
        session = self._find_user_browser_session(user_id, session_id)
        session.status = "closed"
        session.expires_at = self._now(trim=False)
        self._queue_browser_profile_cleanup_if_orphan(
            worker_id=session.target_worker_id,
            profile_key=session.profile_key,
        )
        self._save_state()
        return self._browser_session_response(session)

    def get_worker_browser_sessions(self, worker_id: str, shared_secret: str) -> list[BrowserSessionRecord]:
        worker = self._authenticate_worker(worker_id, shared_secret)
        self._cleanup_stale_browser_sessions()
        now = self._now(trim=False)
        sessions = [
            session
            for session in self.browser_sessions
            if session.target_worker_id == worker.id
            and (
                session.status in {"launching", "awaiting_confirmation", "confirmed"}
                or session.expires_at >= now - timedelta(minutes=30)
            )
        ]
        for session in sessions:
            session.target_worker_public_base_url = str(worker.public_base_url or "").rstrip("/") or None
            self._sync_browser_session_details(session)
        return [deepcopy(session) for session in sessions]

    def get_worker_browser_profile_cleanup_tasks(
        self,
        worker_id: str,
        shared_secret: str,
    ) -> list[dict[str, str]]:
        worker = self._authenticate_worker(worker_id, shared_secret)
        tasks: list[dict[str, str]] = []
        for item in self.browser_profile_cleanup_tasks:
            if str(item.get("worker_id") or "").strip() != worker.id:
                continue
            profile_key = str(item.get("profile_key") or "").strip()
            if not profile_key:
                continue
            tasks.append({"profile_key": profile_key})
        return tasks

    def ack_worker_browser_profile_cleanup_tasks(
        self,
        worker_id: str,
        shared_secret: str,
        profile_keys: list[str],
    ) -> list[str]:
        worker = self._authenticate_worker(worker_id, shared_secret)
        normalized = {
            str(profile_key or "").strip()
            for profile_key in profile_keys
            if str(profile_key or "").strip()
        }
        if not normalized:
            return []

        cleared: list[str] = []
        remaining: list[dict[str, Any]] = []
        for item in self.browser_profile_cleanup_tasks:
            item_worker_id = str(item.get("worker_id") or "").strip()
            item_profile_key = str(item.get("profile_key") or "").strip()
            if item_worker_id == worker.id and item_profile_key in normalized:
                cleared.append(item_profile_key)
                continue
            remaining.append(item)

        if len(remaining) != len(self.browser_profile_cleanup_tasks):
            self.browser_profile_cleanup_tasks = remaining
            self._save_state()
        return cleared

    def sync_worker_browser_session(
        self,
        session_id: str,
        payload: WorkerBrowserSessionSyncPayload,
    ) -> BrowserSessionRecord:
        worker = self._authenticate_worker(payload.worker_id, payload.shared_secret)
        session = self._find_browser_session(session_id)
        if session.target_worker_id != worker.id:
            raise ValueError("Browser session dang thuoc VPS khac.")

        if not (
            session.status in {"closed", "expired"}
            and payload.status in {"launching", "awaiting_confirmation", "confirmed"}
        ):
            session.status = payload.status

        session.novnc_url = payload.novnc_url or session.novnc_url
        session.current_url = payload.current_url
        session.current_title = payload.current_title
        session.detected_channel_id = payload.detected_channel_id
        session.detected_channel_name = payload.detected_channel_name
        session.last_error = payload.last_error
        session.profile_path = payload.profile_path or session.profile_path
        session.session_path = payload.session_path or session.session_path
        session.password_file = payload.password_file or session.password_file
        session.xvfb_pid = payload.xvfb_pid
        session.openbox_pid = payload.openbox_pid
        session.chromium_pid = payload.chromium_pid
        session.x11vnc_pid = payload.x11vnc_pid
        session.websockify_pid = payload.websockify_pid
        if payload.status in {"awaiting_confirmation", "confirmed"} and session.launched_at is None:
            session.launched_at = self._now(trim=False)
        self._save_state()
        return deepcopy(session)

    def _user_meta_record(self, user_id: str) -> dict[str, Any]:
        return self.user_meta.setdefault(
            user_id,
            {
                "password_hash": "",
                "password_algo": "pbkdf2_sha256",
                "telegram": "",
                "updated_by": "system",
                "updated_at": None,
                "created_at": self._now(),
            },
        )

    @staticmethod
    def _normalize_admin_workspace(workspace_mode: str | None) -> str:
        normalized = str(workspace_mode or "").strip().lower()
        return "live" if normalized == "live" else "upload"

    @staticmethod
    def _with_query(path: str, **query: str | None) -> str:
        params = [(key, value) for key, value in query.items() if value]
        if not params:
            return path
        separator = "&" if "?" in path else "?"
        return f"{path}{separator}{urlencode(params)}"

    def _admin_workspace_href(self, active_page: str, workspace_mode: str) -> str:
        normalized_workspace = self._normalize_admin_workspace(workspace_mode)
        if active_page == "users":
            return self._with_query("/admin/user/index", workspace=normalized_workspace)
        if active_page == "workers":
            return self._with_query("/admin/ManagerBOT/index", workspace=normalized_workspace)
        if active_page == "channels":
            return self._with_query("/admin/channel/index", workspace=normalized_workspace)
        if active_page == "renders":
            return self._with_query("/admin/render/index", workspace=normalized_workspace)
        if active_page == "live_workspace":
            if normalized_workspace == "live":
                return "/admin/live/index"
            return self._with_query("/admin/ManagerBOT/index", workspace="upload")
        if normalized_workspace == "live":
            return "/admin/live/index"
        return "/admin/user/index"

    def _admin_workspace_tabs(self, active_page: str, workspace_mode: str) -> list[dict[str, str | bool]]:
        normalized_workspace = self._normalize_admin_workspace(workspace_mode)
        tabs = [
            {
                "key": "upload",
                "label": "Upload",
                "href": self._admin_workspace_href(active_page, "upload"),
            },
            {
                "key": "live",
                "label": "Live Stream",
                "href": self._admin_workspace_href(active_page, "live"),
            },
        ]
        for item in tabs:
            item["active"] = item["key"] == normalized_workspace
        return tabs

    def _admin_nav_items(self, workspace_mode: str = "upload") -> list[dict[str, str]]:
        normalized_workspace = self._normalize_admin_workspace(workspace_mode)
        shared_workspace = {"workspace": normalized_workspace}
        return [
            {"key": "users", "label": "Ngu?i dùng", "href": self._with_query("/admin/user/index", **shared_workspace), "icon": "users"},
            {"key": "workers", "label": "Danh sách BOT", "href": self._with_query("/admin/ManagerBOT/index", **shared_workspace), "icon": "server"},
            {"key": "channels", "label": "Danh sách Kênh", "href": self._with_query("/admin/channel/index", **shared_workspace), "icon": "link"},
            {"key": "renders", "label": "Danh sách Render", "href": self._with_query("/admin/render/index", **shared_workspace), "icon": "video"},
            {"key": "render_workspace", "label": "Ði?u ph?i Render", "href": "/app", "icon": "clapperboard"},
            {"key": "live_workspace", "label": "Ði?u ph?i live stream", "href": "/admin/live/index", "icon": "radio-tower"},
        ]

    def _user_section_tabs(
        self,
        active_key: str,
        viewer_role: str = "admin",
        workspace_mode: str = "upload",
    ) -> list[dict[str, str | bool]]:
        normalized_workspace = self._normalize_admin_workspace(workspace_mode)
        tabs = [
            {"key": "users", "label": "Danh sách user", "href": self._with_query("/admin/user/index", workspace=normalized_workspace)},
            {"key": "create", "label": "T?o user", "href": self._with_query("/admin/user/create", workspace=normalized_workspace)},
        ]
        if viewer_role != "manager":
            tabs.extend(
                [
                    {"key": "managers", "label": "Manager", "href": self._with_query("/admin/user/manager", workspace=normalized_workspace)},
                    {"key": "admins", "label": "Admin", "href": self._with_query("/admin/user/admins", workspace=normalized_workspace)},
                ]
            )
        for item in tabs:
            item["active"] = item["key"] == active_key
        return tabs

    def _selected_manager_ids(self, manager_ids: list[str] | None) -> list[str]:
        available_ids = [user.id for user in self.users if user.role == "manager"]
        if not manager_ids:
            return []
        return [manager_id for manager_id in manager_ids if manager_id in available_ids]

    def _manager_options(self, selected_ids: list[str] | None = None) -> list[dict[str, str | bool]]:
        selected_set = set(selected_ids or [])
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

    def _bot_manager_options(
        self,
        *,
        viewer_role: str = "admin",
        viewer_id: str | None = None,
    ) -> list[dict[str, str]]:
        options: list[dict[str, str]] = []
        seen_ids: set[str] = set()
        for user in self.users:
            include = user.role == "manager"
            if viewer_role == "manager" and viewer_id:
                include = user.id == viewer_id
            if not include or user.id in seen_ids:
                continue
            options.append(
                {
                    "id": user.id,
                    "username": user.username,
                    "display_name": user.display_name,
                    "role": user.role,
                }
            )
            seen_ids.add(user.id)
        options.sort(
            key=lambda item: (
                0 if (viewer_id and item["id"] == viewer_id) else 1,
                item["username"].casefold(),
            )
        )
        return options

    def _filtered_workers(self, manager_ids: list[str] | None = None) -> list[WorkerRecord]:
        selected_ids = set(self._selected_manager_ids(manager_ids))
        if not selected_ids:
            return list(self.workers)
        return [worker for worker in self.workers if worker.manager_id in selected_ids]

    def _effective_manager_scope_ids(
        self,
        *,
        viewer_role: str = "admin",
        viewer_id: str | None = None,
        manager_ids: list[str] | None = None,
    ) -> set[str]:
        selected_manager_ids = set(self._selected_manager_ids(manager_ids))
        if viewer_role == "manager" and viewer_id:
            return {viewer_id}
        return selected_manager_ids

    def _scoped_admin_summary(
        self,
        *,
        viewer_role: str = "admin",
        viewer_id: str | None = None,
        manager_ids: list[str] | None = None,
    ) -> AdminSummary:
        selected_manager_ids = self._effective_manager_scope_ids(
            viewer_role=viewer_role,
            viewer_id=viewer_id,
            manager_ids=manager_ids,
        )
        if not selected_manager_ids:
            return self.get_admin_dashboard().summary

        scoped_workers = [worker for worker in self.workers if worker.manager_id in selected_manager_ids]
        scoped_channels = [
            channel
            for channel in self.channels
            if self._resolve_channel_manager_id(channel) in selected_manager_ids
        ]
        scoped_jobs = [job for job in self.jobs if self._resolve_job_manager_id(job) in selected_manager_ids]
        scoped_users = [
            user
            for user in self.users
            if user.role == "user" and (self._resolved_user_manager_id(user) in selected_manager_ids)
        ]
        return AdminSummary(
            total_managers=len(selected_manager_ids),
            total_users=len(scoped_users),
            total_workers=len(scoped_workers),
            workers_online=len([worker for worker in scoped_workers if worker.status in {"online", "busy"}]),
            channels_connected=len([channel for channel in scoped_channels if channel.status == "connected"]),
            queued_jobs=len([job for job in scoped_jobs if job.status in {"pending", "queueing"}]),
            running_jobs=len([job for job in scoped_jobs if job.status in {"downloading", "rendering", "uploading"}]),
            failed_jobs=len([job for job in scoped_jobs if job.status == "error"]),
        )

    def _admin_shell_context(
        self,
        *,
        page_title: str,
        active_page: str,
        user_section: str | None = None,
        viewer_role: str = "admin",
        viewer_id: str | None = None,
        manager_ids: list[str] | None = None,
        notice: str | None = None,
        notice_level: str = "success",
        workspace_mode: str = "upload",
    ) -> dict[str, Any]:
        normalized_workspace = self._normalize_admin_workspace(workspace_mode)
        effective_manager_ids = self._effective_manager_scope_ids(
            viewer_role=viewer_role,
            viewer_id=viewer_id,
            manager_ids=manager_ids,
        )
        selected_manager_ids = list(effective_manager_ids)
        scoped_summary = self._scoped_admin_summary(
            viewer_role=viewer_role,
            viewer_id=viewer_id,
            manager_ids=selected_manager_ids,
        )
        context = {
            "page_title": page_title,
            "active_page": active_page,
            "nav_items": self._admin_nav_items(normalized_workspace),
            "workspace_mode": normalized_workspace,
            "workspace_tabs": self._admin_workspace_tabs(active_page, normalized_workspace),
            "workspace_heading": "Live Stream" if normalized_workspace == "live" else "Upload",
            "workspace_caption": "Admin workspace",
            "summary_strip": self._summary_strip(
                viewer_role=viewer_role,
                viewer_id=viewer_id,
                manager_ids=selected_manager_ids,
                workspace_mode=normalized_workspace,
            ),
            "summary": scoped_summary,
            "current_user": {"name": "Admin", "avatar": "/static/admin-themes/assets/img/avatar/avatar-1.png"},
            "manager_options": self._manager_options(selected_manager_ids),
            "selected_manager_ids": selected_manager_ids,
            "manager_filter_locked": viewer_role == "manager",
            "notice": notice,
            "notice_level": notice_level,
        }
        if user_section:
            context["user_tabs"] = self._user_section_tabs(
                user_section,
                viewer_role=viewer_role,
                workspace_mode=normalized_workspace,
            )
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

    @staticmethod
    def _worker_status_dot_class(status: str) -> str:
        normalized = str(status or "").strip().lower()
        mapping = {
            "online": "bg-emerald-500",
            "busy": "bg-amber-400",
            "offline": "bg-rose-500",
        }
        return mapping.get(normalized, "bg-slate-300")

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

    def _summary_strip(
        self,
        *,
        viewer_role: str = "admin",
        viewer_id: str | None = None,
        manager_ids: list[str] | None = None,
        workspace_mode: str = "upload",
    ) -> list[dict[str, str]]:
        normalized_workspace = self._normalize_admin_workspace(workspace_mode)
        summary = self._scoped_admin_summary(
            viewer_role=viewer_role,
            viewer_id=viewer_id,
            manager_ids=manager_ids,
        )
        selected_manager_ids = self._effective_manager_scope_ids(
            viewer_role=viewer_role,
            viewer_id=viewer_id,
            manager_ids=manager_ids,
        )
        upload_jobs = self.jobs
        if selected_manager_ids:
            upload_jobs = [job for job in upload_jobs if self._resolve_job_manager_id(job) in selected_manager_ids]
        uploading_count = len([job for job in upload_jobs if job.status == "uploading"])
        if normalized_workspace == "live":
            scope_count = len(selected_manager_ids) or summary.total_managers
            return [
                {
                    "value": str(scope_count),
                    "label": "Manager Trong Scope",
                    "icon": "users",
                    "icon_class": "text-emerald-500",
                    "accent": "Scope",
                    "accent_class": "text-emerald-600",
                    "accent_badge_class": "border-emerald-200 bg-emerald-50 text-emerald-700",
                    "value_class": "text-emerald-600",
                    "bar_color": "#10b981",
                },
                {
                    "value": f"{summary.workers_online}/{summary.total_workers}",
                    "label": "BOT Ðang Ch?y",
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
                    "label": "T?ng User",
                    "icon": "users",
                    "icon_class": "text-rose-500",
                    "accent": "Accounts",
                    "accent_class": "text-rose-500",
                    "accent_badge_class": "border-rose-200 bg-rose-50 text-rose-700",
                    "value_class": "text-slate-900",
                    "bar_color": "#f43f5e",
                },
                {
                    "value": "0",
                    "label": "Ðang Live",
                    "icon": "radio-tower",
                    "icon_class": "text-brand-500",
                    "accent": "Live",
                    "accent_class": "text-brand-600",
                    "accent_badge_class": "border-indigo-200 bg-indigo-50 text-indigo-700",
                    "value_class": "text-brand-600",
                    "bar_color": "#5d67df",
                },
                {
                    "value": "0",
                    "label": "Ch? Lên L?ch",
                    "icon": "clock-3",
                    "icon_class": "text-sky-500",
                    "accent": "Queue",
                    "accent_class": "text-sky-500",
                    "accent_badge_class": "border-sky-200 bg-sky-50 text-sky-700",
                    "value_class": "text-slate-900",
                    "bar_color": "#0284c7",
                },
                {
                    "value": "0",
                    "label": "BOT Backup",
                    "icon": "shield-check",
                    "icon_class": "text-amber-500",
                    "accent": "Fallback",
                    "accent_class": "text-amber-600",
                    "accent_badge_class": "border-amber-200 bg-amber-50 text-amber-700",
                    "value_class": "text-amber-600",
                    "bar_color": "#f59e0b",
                },
            ]
        return [
            {
                "value": str(summary.channels_connected),
                "label": "T?ng S? Kênh",
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
                "label": "BOT Ðang Ch?y",
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
                "label": "T?ng User",
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
                "label": "Ðang Render",
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
                "label": "Ðang Upload",
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
                "label": "Job Ðang Ch?",
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
        return len(self._assigned_worker_links_for_user(user.id))

    def _user_channel_count(self, user: UserSummary) -> int:
        return len(self._user_channel_ids(user.id))

    def _channel_users(self, channel: ChannelRecord) -> list[str]:
        assigned_ids = [link["user_id"] for link in self.channel_user_links if link["channel_id"] == channel.id]
        assigned = []
        for user_id in assigned_ids:
            try:
                assigned.append(self._find_user(user_id).display_name)
            except KeyError:
                continue
        return assigned

    def _natural_sort_text(self, value: str | None) -> str:
        normalized = unicodedata.normalize("NFKD", str(value or "").strip())
        ascii_folded = "".join(char for char in normalized if not unicodedata.combining(char))
        return ascii_folded.casefold()

    def _channel_user_count(self, channel_id: str) -> int:
        return len([link for link in self.channel_user_links if link["channel_id"] == channel_id])

    def _channel_link(self, channel: ChannelRecord) -> str:
        return f"https://www.youtube.com/channel/{channel.channel_id}"

    def _find_job(self, job_id: str) -> RenderJobRecord:
        for job in self.jobs:
            if job.id == job_id:
                return job
        raise KeyError(job_id)

    def _find_channel_optional(self, channel_id: str | None) -> ChannelRecord | None:
        if not channel_id:
            return None
        try:
            return self._find_channel(channel_id)
        except KeyError:
            return None

    def _find_worker_optional(self, worker_id: str | None) -> WorkerRecord | None:
        if not worker_id:
            return None
        try:
            return self._find_worker(worker_id)
        except KeyError:
            return None

    def _manager_username_to_id_map(self) -> dict[str, str]:
        return {
            user.username: user.id
            for user in self.users
            if user.role == "manager"
        }

    def _manager_username_from_id(self, manager_id: str | None) -> str | None:
        if not manager_id:
            return None
        try:
            user = self._find_user(manager_id)
        except KeyError:
            return None
        return user.username if user.role == "manager" else None

    def _resolve_channel_manager_id(self, channel: ChannelRecord) -> str | None:
        worker = self._find_worker_optional(channel.worker_id)
        if worker and worker.manager_id:
            return worker.manager_id
        manager_name = str(channel.manager_name or "").strip()
        if not manager_name:
            return None
        return self._manager_username_to_id_map().get(manager_name)

    def _resolve_channel_manager_name(self, channel: ChannelRecord) -> str:
        manager_name = self._manager_username_from_id(self._resolve_channel_manager_id(channel))
        if manager_name:
            return manager_name
        worker = self._find_worker_optional(channel.worker_id)
        if worker and worker.manager_name:
            return worker.manager_name
        return str(channel.manager_name or "-")

    @staticmethod
    def _channel_connected_at(channel: ChannelRecord) -> datetime | None:
        return channel.browser_connected_at or channel.oauth_connected_at

    def _resolve_job_manager_id(self, job: RenderJobRecord) -> str | None:
        username_to_id = self._manager_username_to_id_map()
        channel = self._find_channel_optional(job.channel_id)
        if channel:
            manager_id = self._resolve_channel_manager_id(channel)
            if manager_id:
                return manager_id

        worker = self._find_worker_optional(job.claimed_by_worker_id or job.worker_name)
        if worker and worker.manager_id:
            return worker.manager_id

        return username_to_id.get(str(job.manager_name or "").strip() or "")

    def _resolve_job_manager_name(self, job: RenderJobRecord) -> str:
        manager_name = self._manager_username_from_id(self._resolve_job_manager_id(job))
        if manager_name:
            return manager_name

        channel = self._find_channel_optional(job.channel_id)
        if channel:
            return self._resolve_channel_manager_name(channel)

        worker = self._find_worker_optional(job.claimed_by_worker_id or job.worker_name)
        if worker and worker.manager_name:
            return worker.manager_name

        return str(job.manager_name or "-")

    def _release_worker_job_claim(self, job: RenderJobRecord, *, reset_status: str = "pending", message: str | None = None) -> None:
        job.status = reset_status  # type: ignore[assignment]
        job.progress = 0 if reset_status == "pending" else job.progress
        if reset_status == "pending":
            job.download_progress = 0
            job.render_progress = 0
            job.upload_progress = 0
        job.can_cancel = reset_status not in {"completed", "error"}
        job.claimed_by_worker_id = None
        job.claimed_at = None
        job.lease_expires_at = None
        job.download_started_at = None if reset_status == "pending" else job.download_started_at
        job.upload_started_at = None if reset_status == "pending" else job.upload_started_at
        job.status_message = None
        if message:
            job.error_message = message

    @staticmethod
    def _upload_interruption_looks_requeueable(job: RenderJobRecord) -> bool:
        upload_progress = max(int(job.upload_progress or 0), int(job.progress or 0))
        if upload_progress > 10:
            return False
        if job.output_url:
            return False
        status_message = str(job.status_message or "").strip().casefold()
        committed_markers = (
            "processing",
            "dang xu ly",
            "dang x? lý",
            "da luu",
            "dã luu",
            "saved as",
            "uploaded",
            "dã t?i",
        )
        return not any(marker in status_message for marker in committed_markers)

    def _handle_interrupted_worker_job(
        self,
        job: RenderJobRecord,
        *,
        now: datetime,
        reason: str,
    ) -> None:
        if job.status == "uploading":
            if self._upload_interruption_looks_requeueable(job):
                self._release_worker_job_claim(
                    job,
                    reset_status="pending",
                    message=f"{reason} Job duoc dua lai hang cho vi upload moi bat dau.",
                )
                return
            job.status = "error"
            job.completed_at = now
            job.can_cancel = False
            job.lease_expires_at = None
            job.status_message = None
            job.download_progress = max(int(job.download_progress or 0), 100)
            job.render_progress = max(int(job.render_progress or 0), 100)
            job.upload_progress = max(int(job.upload_progress or 0), min(max(job.progress, 0), 99))
            job.error_message = (
                f"{reason} Job dang o pha upload da tien xa, "
                "nen duoc danh dau loi de tranh upload trung video."
            )
            return
        self._release_worker_job_claim(
            job,
            reset_status="pending",
            message=f"{reason} Job duoc dua lai hang cho de worker nhan lai sau khi ket noi on dinh.",
        )

    def _reconcile_expired_worker_jobs(self, *, now: datetime) -> bool:
        changed = False
        active_statuses = self._worker_active_job_statuses()
        for job in self.jobs:
            if job.status not in active_statuses:
                continue
            if not job.claimed_by_worker_id:
                continue
            if job.lease_expires_at is None or job.lease_expires_at > now:
                continue
            self._handle_interrupted_worker_job(
                job,
                now=now,
                reason="Control-plane khong nhan duoc heartbeat/progress cua worker trong thoi gian grace.",
            )
            changed = True
        if changed:
            self._refresh_queue_positions()
            self._save_state()
        return changed

    def _reconcile_worker_jobs_from_heartbeat(
        self,
        worker: WorkerRecord,
        *,
        active_job_ids: list[str],
        now: datetime,
    ) -> None:
        active_job_id_set = {str(job_id).strip() for job_id in active_job_ids if str(job_id).strip()}
        for job in self.jobs:
            if job.claimed_by_worker_id != worker.id or job.status not in self._worker_active_job_statuses():
                continue
            if job.id in active_job_id_set:
                job.lease_expires_at = now + timedelta(seconds=self._worker_job_lease_seconds())
                continue
            if job.lease_expires_at is not None and job.lease_expires_at > now:
                continue
            self._handle_interrupted_worker_job(
                job,
                now=now,
                reason="Worker khong con bao job nay trong heartbeat sau khi da qua grace window.",
            )
        self._refresh_queue_positions()

    def _job_username(self, job: RenderJobRecord) -> str:
        user_id = self._job_user_id(job)
        if user_id:
            try:
                return self._find_user(user_id).username
            except KeyError:
                pass
        return "demo-user"

    def _user_workspace_nav_items(self) -> list[dict[str, str]]:
        return [
            {
                "key": "render_workspace",
                "label": "\u0110i\u1ec1u ph\u1ed1i Render",
                "href": "/app",
                "icon": "layers",
            },
            {
                "key": "live_workspace",
                "label": "\u0110i\u1ec1u ph\u1ed1i Live",
                "href": "/app/live",
                "icon": "radio",
            },
        ]

    def get_user_dashboard_view(
        self,
        *,
        user_id: str,
        notice: str | None = None,
        notice_level: str = "success",
    ) -> dict[str, Any]:
        bootstrap = self.get_user_bootstrap(user_id)
        jobs_response = self.get_user_jobs(user_id)
        now = self._now()
        browser_workers = self._workspace_workers_for_user(bootstrap.user)
        has_assigned_worker = bool(browser_workers)
        active_browser_session = self._active_browser_session_for_user(user_id)
        active_browser_worker_id = active_browser_session.target_worker_id if active_browser_session else ""
        browser_worker = next((worker for worker in browser_workers if worker.id == active_browser_worker_id), None)
        if browser_worker is None and len(browser_workers) == 1:
            browser_worker = browser_workers[0]
        browser_session_enabled = any(
            worker.browser_session_enabled and str(worker.public_base_url or "").strip()
            for worker in browser_workers
        )
        browser_session_payload = None
        if active_browser_session:
            self._sync_browser_session_details(active_browser_session)
            browser_session_payload = self._browser_session_response(active_browser_session).model_dump(mode="json")

        visible_channel_ids = {channel.id for channel in bootstrap.channels}
        browser_worker_cards: list[dict[str, Any]] = []
        for index, worker in enumerate(browser_workers, start=1):
            worker_id = str(worker.id or "").strip()
            channel_count = len(
                [
                    channel
                    for channel in self.channels
                    if channel.id in visible_channel_ids and channel.worker_id == worker_id
                ]
            )
            is_browser_ready = bool(worker.browser_session_enabled and str(worker.public_base_url or "").strip())
            worker_status_key = str(worker.status or "").strip().lower()
            is_online = worker_status_key == "online"
            is_busy = worker_status_key == "busy"
            browser_worker_cards.append(
                {
                    "id": worker_id,
                    "name": self._resolve_worker_display_name(worker_id),
                    "label": f"VPS-{index:03d}",
                    "channel_count": channel_count,
                    "channel_text": f"{channel_count} k\u00eanh",
                    "status_key": "busy" if is_busy else ("online" if is_online else str(worker.status or "offline")),
                    "status_text": "\u0110ang x\u1eed l\u00fd" if is_busy else ("S\u1eb5n s\u00e0ng" if is_browser_ready else ("Offline" if not is_online else "Ch\u01b0a s\u1eb5n s\u00e0ng")),
                    "status_dot_class": self._worker_status_dot_class("busy" if is_busy else ("online" if is_browser_ready else worker.status)),
                    "disabled": not is_browser_ready,
                }
            )

        queued_jobs = [job for job in jobs_response.jobs if job.status in {"pending", "queueing"}]
        rendering_jobs = [job for job in jobs_response.jobs if job.status == "rendering"]
        uploading_jobs = [job for job in jobs_response.jobs if job.status == "uploading"]
        failed_jobs = [job for job in jobs_response.jobs if job.status == "error"]

        channels = [
            {"value": "", "label": "-- Ch\u1ecdn k\u00eanh --", "meta": "", "avatar": "", "avatar_class": "", "is_active": True, "is_placeholder": True}
        ]
        for channel in bootstrap.channels:
            channels.append(
                {
                    "value": channel.id,
                    "label": channel.name,
                    "meta": channel.channel_id,
                    "avatar": self._initials(channel.name),
                    "avatar_url": channel.avatar_url,
                    "avatar_class": "bg-emerald-800 text-white",
                    "is_active": False,
                    "is_placeholder": False,
                }
            )

        connected_channels: list[dict[str, Any]] = []
        worker_status_by_id: dict[str, str] = {
            str(worker.id or "").strip(): str(worker.status or "").strip().lower()
            for worker in browser_workers
        }
        worker_channel_count_by_id: dict[str, int] = {}
        for channel in bootstrap.channels:
            worker_key = str(channel.worker_id or channel.worker_name or "").strip()
            if not worker_key:
                continue
            worker_channel_count_by_id[worker_key] = worker_channel_count_by_id.get(worker_key, 0) + 1
        connected_channel_source = sorted(
            bootstrap.channels,
            key=lambda channel: (
                self._natural_sort_text(self._resolve_channel_worker_display_name(channel)),
                self._natural_sort_text(channel.worker_id or channel.worker_name or ""),
                self._natural_sort_text(channel.name),
                self._natural_sort_text(channel.channel_id),
            ),
        )
        for channel in connected_channel_source:
            worker_label = self._resolve_channel_worker_display_name(channel)
            worker_key = str(channel.worker_id or channel.worker_name or "").strip()
            worker_status = worker_status_by_id.get(worker_key, "offline")
            worker_channel_count = worker_channel_count_by_id.get(worker_key, 0)
            connected_channels.append(
                {
                    "id": channel.id,
                    "title": channel.name,
                    "channel_id": channel.channel_id,
                    "worker_label": worker_label,
                    "worker_status_dot_class": self._worker_status_dot_class(worker_status),
                    "worker_channel_count": worker_channel_count,
                    "search_text": " ".join(
                        part
                        for part in [
                            str(channel.name or "").strip(),
                            str(channel.channel_id or "").strip(),
                            str(worker_label or "").strip(),
                            f"{worker_channel_count} k\u00eanh" if worker_channel_count else "",
                        ]
                        if part
                    ).lower(),
                    "public_url": f"https://www.youtube.com/channel/{channel.channel_id}",
                    "avatar": self._initials(channel.name),
                    "avatar_url": channel.avatar_url,
                    "avatar_class": "bg-emerald-800 text-white",
                    "avatar_small": False,
                }
            )

        render_jobs: list[dict[str, Any]] = []
        for index, job in enumerate(jobs_response.jobs, start=1):
            is_drive = job.source_mode == "drive"
            preview = self._resolve_job_preview(job)
            status_view = self._job_user_status_view(job)
            progress_view = self._job_user_progress_view(job)
            scheduled_waiting = bool(job.scheduled_at and job.status in {"pending", "queueing"} and job.scheduled_at > now)
            scheduled_wait_at = self._format_compact_datetime(job.scheduled_at) if scheduled_waiting else ""
            worker_display_name = self._resolve_job_worker_display_name(job)
            bot_meta = job.worker_name if worker_display_name != (job.worker_name or "-") else (job.manager_name or "-")
            render_jobs.append(
                {
                    "id": job.id,
                    "index": index,
                    "kind": "Drive" if is_drive else "Upload",
                    "kind_class": "text-sky-600" if is_drive else "text-violet-600",
                    "title": job.title,
                    "meta": f"{job.source_label} \u2022 render {self._format_render_duration(job.time_render_string)} \u2022 ",
                    "job_id": job.id,
                    "description": (job.description or "").strip(),
                    "channel_avatar": self._initials(job.channel_name),
                    "channel_avatar_url": job.channel_avatar_url,
                    "channel_name": job.channel_name,
                    "queue_label": f"Queue #{job.queue_order or index}",
                    "bot": worker_display_name,
                    "bot_meta": bot_meta,
                    "owner": job.manager_name or "-",
                    "progress": f"{job.progress}%",
                    "progress_mode": progress_view["mode"],
                    "download_progress": progress_view["download"],
                    "render_progress": progress_view["render"],
                    "upload_progress": progress_view["upload"],
                    "created_at": self._format_datetime(job.created_at),
                    "render_at": status_view["render_at"],
                    "uploaded_at": status_view["upload_at"],
                    "scheduled_waiting": scheduled_waiting,
                    "scheduled_wait_at": scheduled_wait_at,
                    "status": status_view["label"],
                    "status_key": job.status,
                    "status_class": status_view["class"],
                    "progress_text_class": status_view["progress_text_class"],
                    "progress_bar_class": status_view["progress_bar_class"],
                    "error_message": (job.error_message or "").strip(),
                    "icon": "hard-drive-download" if is_drive else None,
                    "icon_class": "text-sky-600",
                    "preview_kind": preview["kind"] if preview else None,
                    "preview_url": preview["url"] if preview else None,
                    "preview_text": (job.source_file_name or "Preview")[:16],
                    "can_cancel": job.can_cancel,
                }
            )

        is_admin_shell = bootstrap.user.role in {"admin", "manager"}

        return {
            "page_title": "Upload Youtube",
            "app_name": "Youtube Upload" if is_admin_shell else "Upload Youtube",
            "admin_shell": is_admin_shell,
            "active_page": "render_workspace",
            "nav_items": (
                self._admin_nav_items()
                if is_admin_shell
                else self._user_workspace_nav_items()
            ),
            "workspace_label": {
                "admin": "Admin workspace",
                "manager": "Manager workspace",
            }.get(bootstrap.user.role, "User workspace"),
            "user_name": bootstrap.user.display_name,
            "user_role": {
                "admin": "control plane",
                "manager": "manager scope",
            }.get(bootstrap.user.role, bootstrap.user.manager_name or bootstrap.user.role),
            "logout_path": "/admin/logout" if is_admin_shell else "/logout",
            "upload_capabilities": bootstrap.upload_capabilities.model_dump(mode="json"),
            "channel_connect_mode": "browser_session",
            "channel_connect_blocked_message": (
                "B\u1ea1n ch\u01b0a \u0111\u01b0\u1ee3c manager c\u1ea5p VPS. H\u00e3y li\u00ean h\u1ec7 manager tr\u01b0\u1edbc khi th\u00eam k\u00eanh."
                if bootstrap.user.role == "user" and not has_assigned_worker
                else (
                    "B\u1ea1n ch\u01b0a c\u00f3 VPS n\u00e0o trong scope qu\u1ea3n l\u00fd \u0111\u1ec3 m\u1edf phi\u00ean th\u00eam k\u00eanh."
                    if bootstrap.user.role == "manager" and not has_assigned_worker
                    else (
                        "B\u1ea1n ch\u01b0a t\u1ef1 c\u1ea5p VPS cho t\u00e0i kho\u1ea3n admin n\u00e0y. H\u00e3y v\u00e0o Danh s\u00e1ch BOT r\u1ed3i g\u00e1n VPS cho ch\u00ednh m\u00ecnh."
                        if bootstrap.user.role == "admin" and not has_assigned_worker
                        else None
                    )
                )
            ),
            "browser_session_enabled": browser_session_enabled,
            "browser_worker_count": len(browser_workers),
            "browser_workers": browser_worker_cards,
            "browser_worker": {
                "id": browser_worker.id,
                "name": self._resolve_worker_display_name(browser_worker.id),
                "public_base_url": browser_worker.public_base_url,
            }
            if browser_worker
            else None,
            "browser_session": browser_session_payload,
            "notice": notice,
            "notice_level": notice_level,
            "kpis": [
                {"label": "K\u00eanh \u0111\u00e3 th\u00eam", "icon": "radio", "icon_class": "text-emerald-500", "value": bootstrap.oauth.connected_count, "accent": "Online", "accent_class": "text-emerald-600", "accent_badge_class": "border-emerald-200 bg-emerald-50 text-emerald-700", "value_class": "text-emerald-600", "bar_class": "bg-emerald-500"},
                {"label": "\u0110ang ch\u1edd x\u1eed l\u00fd", "icon": "layers", "icon_class": "text-amber-500", "value": len(queued_jobs), "accent": "Ch\u1edd", "accent_class": "text-amber-600", "accent_badge_class": "border-amber-200 bg-amber-50 text-amber-700", "value_class": "text-amber-600", "bar_class": "bg-amber-500"},
                {"label": "\u0110ang render", "icon": "loader", "icon_class": "text-brand-500", "value": len(rendering_jobs), "accent": "Render", "accent_class": "text-brand-600", "accent_badge_class": "border-indigo-200 bg-indigo-50 text-indigo-700", "value_class": "text-brand-600", "bar_class": "bg-brand-500"},
                {"label": "\u0110ang upload", "icon": "cloud-upload", "icon_class": "text-sky-500", "value": len(uploading_jobs), "accent": "Upload", "accent_class": "text-sky-500", "accent_badge_class": "border-sky-200 bg-sky-50 text-sky-700", "value_class": "text-slate-900" if len(uploading_jobs) == 0 else "text-sky-500", "bar_class": "bg-sky-400"},
                {"label": "X\u1eed l\u00fd l\u1ed7i", "icon": "shield-alert", "icon_class": "text-rose-500", "value": len(failed_jobs), "accent": "L\u1ed7i", "accent_class": "text-rose-500", "accent_badge_class": "border-rose-200 bg-rose-50 text-rose-700", "value_class": "text-slate-900" if len(failed_jobs) == 0 else "text-rose-500", "bar_class": "bg-rose-400"},
            ],
            "render_config": {"title": "C\u1ea5u h\u00ecnh render", "description": "Thi\u1ebft l\u1eadp ngu\u1ed3n \u0111\u1ea7u v\u00e0o, file loop v\u00e0 k\u00eanh xu\u1ea5t b\u1ea3n cho job m\u1edbi."},
            "quick_settings": {"video_title": "", "description_text": "", "duration": "03:30:00", "schedule_at": (now + timedelta(hours=1)).strftime("%d/%m/%Y %H:%M")},
            "channels": channels,
            "connected_channels": connected_channels,
            "render_tabs": [
                {"label": "Danh s\u00e1ch render", "count": len(render_jobs), "active": True},
                {"label": "\u0110ang x\u1eed l\u00fd", "count": len([job for job in render_jobs if job["status"] in {"\u0110ang render", "\u0110ang upload", "\u0110ang t\u1ea3i ngu\u1ed3n"}]), "active": False},
            ],
            "render_jobs": render_jobs,
            "render_summary": f"Hi\u1ec3n th\u1ecb 1 \u0111\u1ebfn {len(render_jobs)} trong s\u1ed1 {len(render_jobs)} k\u1ebft qu\u1ea3" if render_jobs else "Ch\u01b0a c\u00f3 job n\u00e0o trong h\u00e0ng \u0111\u1ee3i",
        }

    def get_user_bootstrap(self, user_id: str) -> UserBootstrapResponse:
        user = deepcopy(self._require_workspace_user(user_id))
        assigned_workers = self._workspace_workers_for_user(user)
        assigned_worker_ids = {worker.id for worker in assigned_workers}
        channels = self._workspace_channels_for_user(user)
        if user.role == "user" and assigned_worker_ids:
            channels = [channel for channel in channels if channel.worker_id in assigned_worker_ids]
        self._refresh_browser_channels_metadata(channels)
        channels = deepcopy(channels)
        connected_count = len([channel for channel in channels if channel.status == "connected"])
        reconnect_count = len([channel for channel in channels if channel.status != "connected"])
        return UserBootstrapResponse(
            user=user,
            channels=channels,
            upload_capabilities=self.get_upload_capabilities(),
            oauth=OAuthSummary(connected_count=connected_count, needs_reconnect_count=reconnect_count),
        )

    def get_user_jobs(self, user_id: str) -> UserJobsResponse:
        self._require_workspace_user(user_id)
        return UserJobsResponse(jobs=self._user_jobs_for_workspace(user_id))

    def get_user_dashboard_live_payload(self, user_id: str) -> dict[str, Any]:
        dashboard = self.get_user_dashboard_view(user_id=user_id)
        return {
            "kpis": dashboard["kpis"],
            "connected_channels": dashboard["connected_channels"],
            "render_tabs": dashboard["render_tabs"],
            "render_jobs": dashboard["render_jobs"],
            "render_summary": dashboard["render_summary"],
            "browser_session": dashboard.get("browser_session"),
        }

    def get_user_live_workspace_view(
        self,
        *,
        user_id: str,
        notice: str | None = None,
        notice_level: str = "success",
    ) -> dict[str, Any]:
        dashboard = self.get_user_dashboard_view(
            user_id=user_id,
            notice=notice,
            notice_level=notice_level,
        )
        bootstrap = self.get_user_bootstrap(user_id)
        now = self._now()
        workspace_workers = self._workspace_workers_for_user(bootstrap.user)
        live_worker_options: list[dict[str, Any]] = []
        connected_worker_count = 0

        for worker in workspace_workers:
            status_key = str(worker.status or "").strip().lower()
            is_connected = status_key in {"online", "busy"}
            if is_connected:
                connected_worker_count += 1
            live_worker_options.append(
                {
                    "id": worker.id,
                    "name": self._resolve_worker_display_name(worker.id),
                    "manager_name": worker.manager_name or "-",
                    "group": worker.group or "-",
                    "status_key": status_key or "offline",
                    "status_label": "S\u1eb5n s\u00e0ng" if is_connected else "M\u1ea5t k\u1ebft n\u1ed1i",
                    "status_class": (
                        "border-emerald-200 bg-emerald-50 text-emerald-700"
                        if is_connected
                        else "border-rose-200 bg-rose-50 text-rose-600"
                    ),
                    "thread_text": self._worker_thread_summary(worker)["thread_text"],
                }
            )

        live_rows: list[dict[str, Any]] = []

        dashboard.update(
            {
                "page_title": "Upload Youtube",
                "active_page": "live_workspace",
                "nav_items": (
                    self._admin_nav_items("live")
                    if dashboard.get("admin_shell")
                    else self._user_workspace_nav_items()
                ),
                "kpis": [
                    {
                        "label": "BOT \u0111\u01b0\u1ee3c c\u1ea5p",
                        "icon": "server",
                        "icon_class": "text-emerald-500",
                        "value": len(live_worker_options),
                        "accent": "Live + Backup",
                        "accent_class": "text-emerald-600",
                        "accent_badge_class": "border-emerald-200 bg-emerald-50 text-emerald-700",
                        "value_class": "text-emerald-600",
                        "bar_class": "bg-emerald-500",
                    },
                    {
                        "label": "BOT live s\u1eb5n s\u00e0ng",
                        "icon": "server",
                        "icon_class": "text-brand-500",
                        "value": connected_worker_count,
                        "accent": f"{connected_worker_count}/{len(live_worker_options)} BOT",
                        "accent_class": "text-brand-600",
                        "accent_badge_class": "border-indigo-200 bg-indigo-50 text-indigo-700",
                        "value_class": "text-brand-600",
                        "bar_class": "bg-brand-500",
                    },
                    {
                        "label": "\u0110ang live",
                        "icon": "radio",
                        "icon_class": "text-rose-500",
                        "value": 0,
                        "accent": "Live",
                        "accent_class": "text-rose-500",
                        "accent_badge_class": "border-rose-200 bg-rose-50 text-rose-700",
                        "value_class": "text-slate-900",
                        "bar_class": "bg-rose-400",
                    },
                    {
                        "label": "Ch\u1edd l\u00ean l\u1ecbch",
                        "icon": "clock-3",
                        "icon_class": "text-amber-500",
                        "value": 0,
                        "accent": "L\u1ecbch",
                        "accent_class": "text-amber-600",
                        "accent_badge_class": "border-amber-200 bg-amber-50 text-amber-700",
                        "value_class": "text-slate-900",
                        "bar_class": "bg-amber-500",
                    },
                    {
                        "label": "BOT backup",
                        "icon": "shield-check",
                        "icon_class": "text-sky-500",
                        "value": 0,
                        "accent": "Fallback",
                        "accent_class": "text-sky-600",
                        "accent_badge_class": "border-sky-200 bg-sky-50 text-sky-700",
                        "value_class": "text-slate-900",
                        "bar_class": "bg-sky-400",
                    },
                ],
                "live_config": {
                    "title": "Live Config",
                    "description": "Thi\u1ebft l\u1eadp BOT ch\u00ednh, BOT backup, media ngu\u1ed3n v\u00e0 l\u1ecbch live.",
                },
                "live_form": {
                    "stream_name": "",
                    "stream_key": "",
                    "video_url": "",
                    "audio_url": "",
                    "backup_delay_minutes": 3,
                    "start_at": (now + timedelta(hours=1)).strftime("%d/%m/%Y %H:%M"),
                    "end_at": (now + timedelta(hours=3)).strftime("%d/%m/%Y %H:%M"),
                },
                "live_channels": dashboard.get("channels", []),
                "live_workers": live_worker_options,
                "connected_channels": dashboard.get("connected_channels", []),
                "live_tabs": [
                    {"label": "Danh s\u00e1ch live", "count": len(live_rows), "active": True},
                    {"label": "Ch\u1edd l\u00ean l\u1ecbch", "count": 0, "active": False},
                ],
                "live_stream_rows": live_rows,
                "live_summary": (
                    f"Hi\u1ec3n th\u1ecb 1 \u0111\u1ebfn {len(live_rows)} trong s\u1ed1 {len(live_rows)} k\u1ebft qu\u1ea3"
                    if live_rows
                    else "Ch\u01b0a c\u00f3 lu\u1ed3ng live n\u00e0o trong danh s\u00e1ch"
                ),
            }
        )
        return dashboard

    def _resolve_job_preview(self, job: RenderJobRecord) -> dict[str, str] | None:


        if job.thumbnail_path and self._path_has_content(self._absolute_preview_path(str(job.thumbnail_path).strip())):
            return {
                "kind": "image",
                "url": self._preview_route(job.id),
            }

        video_asset = next((asset for asset in job.assets if asset.slot == "video_loop"), None)
        if not video_asset:
            youtube_video_id = self._extract_youtube_video_id(job.output_url)
            if youtube_video_id:
                return {
                    "kind": "image",
                    "url": f"https://i.ytimg.com/vi/{youtube_video_id}/hqdefault.jpg",
                }
            return None

        if video_asset.source_mode == "local" and video_asset.file_name:
            local_asset_path = self.upload_asset_dir / video_asset.file_name
            preview_kind = self._guess_preview_kind(video_asset.file_name) or "video"
            if self._path_has_content(local_asset_path):
                return {
                    "kind": preview_kind,
                    "url": f"/api/user/jobs/{job.id}/preview/video_loop",
                }

        if video_asset.url:
            preview_kind = self._guess_preview_kind(video_asset.url)
            if preview_kind:
                return {
                    "kind": preview_kind,
                    "url": video_asset.url,
                }

        if job.thumbnail_url:
            return {
                "kind": "image",
                "url": job.thumbnail_url,
            }

        youtube_video_id = self._extract_youtube_video_id(job.output_url)
        if youtube_video_id:
            return {
                "kind": "image",
                "url": f"https://i.ytimg.com/vi/{youtube_video_id}/hqdefault.jpg",
            }

        return None

    def create_job(self, user_id: str, payload: JobCreatePayload, source_file_names: dict[str, str | None]) -> RenderJobRecord:
        user = self._require_workspace_user(user_id)
        channel = self._find_channel(payload.channel_id)
        if not self._user_has_channel_access(user_id, channel.id):
            raise ValueError("B?n không có quy?n t?o job trên kênh này.")
        worker = self._assert_channel_matches_user_worker(user, channel)
        queue_order = max([job.queue_order or 0 for job in self.jobs], default=0) + 1
        created_at = self._now()
        normalize = lambda value: (value or "").strip() or None

        resolved_asset_ids = {
            "intro": normalize(payload.intro_asset_id),
            "video_loop": normalize(payload.video_loop_asset_id),
            "audio_loop": normalize(payload.audio_loop_asset_id),
            "outro": normalize(payload.outro_asset_id),
        }
        resolved_file_names = {
            "intro": normalize(source_file_names.get("intro")) or self.consume_uploaded_asset(user_id, resolved_asset_ids.get("intro")),
            "video_loop": normalize(source_file_names.get("video_loop")) or self.consume_uploaded_asset(user_id, resolved_asset_ids.get("video_loop")),
            "audio_loop": normalize(source_file_names.get("audio_loop")) or self.consume_uploaded_asset(user_id, resolved_asset_ids.get("audio_loop")),
            "outro": normalize(source_file_names.get("outro")) or self.consume_uploaded_asset(user_id, resolved_asset_ids.get("outro")),
        }

        assets = [
            JobAsset(
                slot="intro",
                label="Intro",
                source_mode="local" if resolved_file_names.get("intro") else "drive",
                asset_id=resolved_asset_ids.get("intro"),
                url=normalize(payload.intro_url),
                file_name=resolved_file_names.get("intro"),
            ),
            JobAsset(
                slot="video_loop",
                label="Video loop",
                source_mode="local" if resolved_file_names.get("video_loop") else "drive",
                asset_id=resolved_asset_ids.get("video_loop"),
                url=normalize(payload.video_loop_url),
                file_name=resolved_file_names.get("video_loop"),
            ),
            JobAsset(
                slot="audio_loop",
                label="Audio loop",
                source_mode="local" if resolved_file_names.get("audio_loop") else "drive",
                asset_id=resolved_asset_ids.get("audio_loop"),
                url=normalize(payload.audio_loop_url),
                file_name=resolved_file_names.get("audio_loop"),
            ),
            JobAsset(
                slot="outro",
                label="Outro",
                source_mode="local" if resolved_file_names.get("outro") else "drive",
                asset_id=resolved_asset_ids.get("outro"),
                url=normalize(payload.outro_url),
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
            worker_name=worker.id,
            manager_name=user.manager_name or worker.manager_name,
            status="pending",
            progress=0,
            queue_order=queue_order,
            visibility="draft",
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

    def cancel_job(self, job_id: str, *, user_id: str | None = None) -> RenderJobRecord:
        job = self._find_user_visible_job(user_id, job_id) if user_id else self._find_job(job_id)
        if job.status not in {"completed", "cancelled", "error"}:
            job.status = "cancelled"
            job.can_cancel = False
            job.completed_at = self._now()
            job.lease_expires_at = None
            self._refresh_queue_positions()
            self._save_state()
        return deepcopy(job)

    def delete_job(self, job_id: str, *, user_id: str | None = None) -> None:
        target_job = self._find_user_visible_job(user_id, job_id) if user_id else self._find_job(job_id)
        for index, job in enumerate(self.jobs):
            if job.id == target_job.id:
                self._purge_job_artifacts(job, exclude_job_id=job.id)
                self.jobs.pop(index)
                self._refresh_queue_positions()
                self._save_state()
                return
        raise KeyError(job_id)

    def delete_jobs(self, job_ids: list[str], *, user_id: str | None = None) -> list[str]:
        normalized_ids: list[str] = []
        for job_id in job_ids:
            cleaned = str(job_id or "").strip()
            if cleaned and cleaned not in normalized_ids:
                normalized_ids.append(cleaned)

        if not normalized_ids:
            return []

        visible_job_ids: set[str] = set()
        for job_id in normalized_ids:
            try:
                target_job = self._find_user_visible_job(user_id, job_id) if user_id else self._find_job(job_id)
            except KeyError:
                continue
            visible_job_ids.add(target_job.id)

        if not visible_job_ids:
            return []

        deleted_ids: list[str] = []
        remaining_jobs: list[RenderJobRecord] = []
        for job in self.jobs:
            if job.id in visible_job_ids:
                self._purge_job_artifacts(job, exclude_job_id=job.id)
                deleted_ids.append(job.id)
                continue
            remaining_jobs.append(job)

        if not deleted_ids:
            return []

        self.jobs = remaining_jobs
        self._refresh_queue_positions()
        self._save_state()
        return deleted_ids

    def delete_all_jobs(self, deleted_by: str = "admin") -> None:
        jobs_to_delete = list(self.jobs)
        self.jobs = []
        for job in jobs_to_delete:
            self._purge_job_artifacts(job)
        self.render_delete_meta = {
            "user": deleted_by,
            "deleted_at": self._now(),
        }
        self._save_state()

    def get_admin_dashboard(self) -> AdminDashboardResponse:
        queued = len([job for job in self.jobs if job.status in {"pending", "queueing"}])
        running = len([job for job in self.jobs if job.status in {"downloading", "rendering", "uploading"}])
        failed = len([job for job in self.jobs if job.status == "error"])
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

    @staticmethod
    def _normalize_live_bot_type(raw_type: Any, note: str | None = None) -> str:
        normalized = str(raw_type or "").strip().lower()
        normalized_note = str(note or "").strip().lower()
        if "backup" in normalized or "backup" in normalized_note or "phu" in normalized_note or "ph?" in normalized_note:
            return "backup"
        return "live"

    @staticmethod
    def _live_bot_type_label(bot_type: str) -> str:
        mapping = {
            "live": "Live Stream",
            "backup": "Backup",
            "mixed": "Live + Backup",
        }
        return mapping.get(str(bot_type or "").strip().lower(), "--")

    def _live_capacity_metrics_for_user(self, user: UserSummary) -> dict[str, int]:
        links = self._assigned_worker_links_for_user(user.id)
        metrics = {
            "threads_live_total": 0,
            "threads_backup_total": 0,
            "threads_live_running": 0,
            "threads_backup_running": 0,
            "threads_backup_pending": 0,
            "bots_live_total": 0,
            "bots_backup_total": 0,
        }
        seen_worker_ids: dict[str, set[str]] = {
            "live": set(),
            "backup": set(),
        }
        for link in links:
            worker_id = str(link.get("worker_id") or "").strip()
            bot_type = self._normalize_live_bot_type(link.get("bot_type"), str(link.get("note") or ""))
            threads = max(0, int(link.get("threads") or 0))
            if bot_type == "backup":
                metrics["threads_backup_total"] += threads
            else:
                metrics["threads_live_total"] += threads
            if worker_id:
                seen_worker_ids.setdefault(bot_type, set()).add(worker_id)
        metrics["bots_live_total"] = len(seen_worker_ids.get("live", set()))
        metrics["bots_backup_total"] = len(seen_worker_ids.get("backup", set()))
        return metrics

    def _build_user_rows(
        self,
        manager_ids: list[str] | None = None,
        *,
        viewer_role: str = "admin",
        viewer_id: str | None = None,
    ) -> list[dict[str, Any]]:
        selected_manager_ids = set(self._selected_manager_ids(manager_ids))
        rows: list[dict[str, Any]] = []
        managers_by_username = {user.username: user for user in self.users if user.role == "manager"}

        for user in self.users:
            manager = managers_by_username.get(user.manager_name or "")
            resolved_manager_id = user.manager_id or (manager.id if manager else "")

            if viewer_role == "manager":
                if not viewer_id:
                    continue
                if user.role == "manager":
                    if user.id != viewer_id:
                        continue
                elif user.role == "user":
                    if resolved_manager_id != viewer_id:
                        continue
                else:
                    continue

            include_row = True
            if selected_manager_ids:
                if user.role == "manager":
                    include_row = user.id in selected_manager_ids
                elif user.role == "user":
                    include_row = resolved_manager_id in selected_manager_ids

            if not include_row:
                continue

            role_label, role_class = self._role_badge(user.role)
            meta = self._user_meta_record(user.id)
            row_manager_name = user.manager_name or (user.username if user.role == "manager" else "-")
            row_manager_id = manager.id if manager else (user.id if user.role == "manager" else "")
            live_metrics = self._live_capacity_metrics_for_user(user)
            manager_meta = self._user_meta_record(row_manager_id) if row_manager_id else {}
            rows.append(
                {
                    "index": len(rows) + 1,
                    "id": user.id,
                    "username": user.username,
                    "display_name": user.username,
                    "avatar_initials": self._initials(user.username),
                    "avatar_class": self._avatar_palette(user.username),
                    "role": user.role,
                    "role_label": role_label,
                    "role_class": role_class,
                    "manager_name": row_manager_name,
                    "manager_id": row_manager_id,
                    "telegram": meta.get("telegram") or "",
                    "telegram_manager": manager_meta.get("telegram") or "",
                    "updated_meta": f"{meta.get('updated_by') or '-'}  {self._format_compact_datetime(meta.get('updated_at'))}",
                    "total_channels": self._user_channel_count(user),
                    "total_workers": self._user_worker_count(user),
                    "live_threads_total": live_metrics["threads_live_total"],
                    "live_threads_running": live_metrics["threads_live_running"],
                    "live_bots_total": live_metrics["bots_live_total"],
                    "live_threads_backup_total": live_metrics["threads_backup_total"],
                    "live_threads_backup_running": live_metrics["threads_backup_running"],
                    "live_threads_backup_pending": live_metrics["threads_backup_pending"],
                    "live_bots_backup_total": live_metrics["bots_backup_total"],
                    "live_total_bots": (
                        live_metrics["bots_live_total"]
                        + live_metrics["bots_backup_total"]
                    ),
                    "can_delete": not (
                        (viewer_role == "manager" and viewer_id and user.role == "manager" and user.id == viewer_id)
                        or (user.role == "admin" and len([item for item in self.users if item.role == "admin"]) <= 1)
                    ),
                }
            )
        return rows

    @staticmethod
    def _credential_status_label(meta: dict[str, Any]) -> str:
        password_hash = str(meta.get("password_hash") or "").strip()
        if password_hash:
            return "Ðã d?t m?t kh?u"
        if str(meta.get("password") or "").strip():
            return "C?n d?i l?i m?t kh?u"
        return "Chua d?t m?t kh?u"

    def _build_role_page_context(
        self,
        *,
        role_kind: str,
        notice: str | None = None,
        notice_level: str = "success",
        workspace_mode: str = "upload",
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
                    "credential_status": self._credential_status_label(meta),
                    "updated_meta": f"{meta.get('updated_by') or '-'}  {self._format_compact_datetime(meta.get('updated_at'))}",
                }
            )

        context = self._admin_shell_context(
            page_title="Danh sách manager" if is_manager else "Danh sách admin",
            active_page="users",
            user_section="managers" if is_manager else "admins",
            notice=notice,
            notice_level=notice_level,
            workspace_mode=workspace_mode,
        )
        context.update(
            {
                "template": "admin/user_role_list.html",
                "page_kind": role_kind,
                "heading": "Danh sách manager" if is_manager else "Danh sách admin",
                "role_label": "manager" if is_manager else "admin",
                "title": "Danh sách manager" if is_manager else "Danh sách admin",
                "description": "B? nhi?m ho?c g? quy?n manager cho tài kho?n." if is_manager else "B? nhi?m ho?c g? quy?n admin cho tài kho?n.",
                "action_route": "/admin/user/updaterolemanager" if is_manager else "/admin/user/updateroleadmin",
                "rows": rows,
                "assignable_user_options": [
                    {
                        "id": user.id,
                        "username": user.username,
                        "search_text": " ".join(
                            part
                            for part in [
                                user.username,
                                user.display_name,
                                user.role,
                                user.manager_name,
                            ]
                            if part
                        ).lower(),
                        "description": "  ".join(
                            part
                            for part in [
                                f"Role: {user.role}",
                                user.display_name if user.display_name and user.display_name != user.username else "",
                            ]
                            if part
                        ),
                    }
                    for user in sorted(self.users, key=lambda item: (item.username or "").lower())
                ],
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
                    "worker_name": self._resolve_worker_display_name(worker.id),
                    "manager_name": worker.manager_name,
                    "status_label": status_label,
                    "status_class": status_class,
                    "bot_type": self._live_bot_type_label(
                        self._normalize_live_bot_type(mapping.get("bot_type"), str(mapping.get("note") or ""))
                    ),
                    "number_of_threads": mapping["threads"],
                    "note": mapping.get("note") or "VPS duoc cap",
                    "disk_text": f"{worker.disk_used_gb:.1f}/{worker.disk_total_gb:.1f}GB",
                    "bandwidth_text": f"{worker.bandwidth_kbps:.2f}KB/s",
                }
            )
        return rows

    def _worker_assigned_user_link(self, worker_id: str, *, exclude_user_id: str | None = None) -> dict[str, Any] | None:
        for mapping in self.user_worker_links:
            if mapping.get("worker_id") != worker_id:
                continue
            if exclude_user_id and mapping.get("user_id") == exclude_user_id:
                continue
            return mapping
        return None

    def _assigned_users_for_worker(self, worker_id: str) -> list[UserSummary]:
        users: list[UserSummary] = []
        seen_user_ids: set[str] = set()
        for mapping in sorted(self.user_worker_links, key=lambda item: int(item.get("id") or 0)):
            if str(mapping.get("worker_id") or "").strip() != str(worker_id or "").strip():
                continue
            user_id = str(mapping.get("user_id") or "").strip()
            if not user_id or user_id in seen_user_ids:
                continue
            try:
                user = self._find_user(user_id)
            except KeyError:
                continue
            users.append(user)
            seen_user_ids.add(user_id)
        return users

    def _worker_candidates_for_user(self, user: UserSummary) -> list[dict[str, str]]:
        candidates: list[dict[str, str]] = []
        current_worker_ids = {
            str(link.get("worker_id") or "").strip()
            for link in self._assigned_worker_links_for_user(user.id)
            if str(link.get("worker_id") or "").strip()
        }
        for worker in self.workers:
            if user.manager_name and worker.manager_name != user.manager_name:
                continue
            candidates.append({"id": worker.id, "name": self._resolve_worker_display_name(worker.id)})
        candidate_ids = {item["id"] for item in candidates}
        for worker_id in sorted(current_worker_ids):
            if worker_id in candidate_ids:
                continue
            worker = self._find_worker(worker_id)
            candidates.insert(0, {"id": worker.id, "name": self._resolve_worker_display_name(worker.id)})
            candidate_ids.add(worker.id)
        return candidates

    def _resolved_user_manager_id(self, user: UserSummary) -> str | None:
        if user.role != "user":
            return None
        if user.manager_id:
            return user.manager_id
        manager = next(
            (
                item
                for item in self.users
                if item.role == "manager" and item.username == (user.manager_name or "")
            ),
            None,
        )
        return manager.id if manager else None

    def _assigned_user_for_worker(self, worker_id: str) -> UserSummary | None:
        users = self._assigned_users_for_worker(worker_id)
        if not users:
            return None
        return users[0]

    def _bot_user_options(
        self,
        *,
        viewer_role: str = "admin",
        viewer_id: str | None = None,
    ) -> list[dict[str, Any]]:
        options: list[dict[str, Any]] = []
        viewer_scope_manager_id = str(viewer_id or "").strip()
        for user in self.users:
            scope_locked = False
            self_assignable = False
            if user.role == "user":
                manager_id = self._resolved_user_manager_id(user)
                assigned_workers = self._workspace_workers_for_user(user.id)
                if viewer_role == "manager" and viewer_scope_manager_id and manager_id != viewer_scope_manager_id:
                    assigned_workers = [
                        worker
                        for worker in assigned_workers
                        if str(worker.manager_id or "").strip() == viewer_scope_manager_id
                    ]
                    if not assigned_workers:
                        continue
                    scope_locked = True
                role_label = "User"
            elif user.role == "manager" and viewer_role == "manager" and viewer_id and user.id == viewer_id:
                manager_id = user.id
                assigned_workers = self._workspace_workers_for_user(user.id)
                role_label = "Manager"
                self_assignable = True
            elif user.role == "manager" and viewer_role == "manager" and viewer_scope_manager_id:
                manager_id = user.id
                assigned_workers = [
                    worker
                    for worker in self._workspace_workers_for_user(user.id)
                    if str(worker.manager_id or "").strip() == viewer_scope_manager_id
                ]
                if not assigned_workers:
                    continue
                role_label = "Manager"
                scope_locked = True
            elif user.role == "manager" and viewer_role == "admin":
                manager_id = user.id
                assigned_workers = self._workspace_workers_for_user(user.id)
                if not assigned_workers:
                    continue
                role_label = "Manager"
                scope_locked = True
            elif user.role == "admin" and viewer_role == "admin" and viewer_id and user.id == viewer_id:
                manager_id = ""
                assigned_workers = self._workspace_workers_for_user(user.id)
                role_label = "Admin"
                self_assignable = True
            elif user.role == "admin" and viewer_role == "manager" and viewer_scope_manager_id:
                assigned_workers = [
                    worker
                    for worker in self._workspace_workers_for_user(user.id)
                    if str(worker.manager_id or "").strip() == viewer_scope_manager_id
                ]
                if not assigned_workers:
                    continue
                manager_id = viewer_scope_manager_id
                role_label = "Admin"
                scope_locked = True
            else:
                continue
            assigned_worker = assigned_workers[0] if assigned_workers else None
            assigned_worker_ids = [worker.id for worker in assigned_workers]
            assigned_worker_names = [self._resolve_worker_display_name(worker.id) for worker in assigned_workers]
            options.append(
                {
                    "id": user.id,
                    "username": user.username,
                    "display_name": user.display_name,
                    "role": user.role,
                    "role_label": role_label,
                    "manager_id": manager_id or "",
                    "manager_name": user.manager_name or "",
                    "assigned_worker_id": assigned_worker.id if assigned_worker else "",
                    "assigned_worker_name": self._resolve_worker_display_name(assigned_worker.id) if assigned_worker else "",
                    "assigned_worker_ids": assigned_worker_ids,
                    "assigned_worker_names": assigned_worker_names,
                    "assigned_worker_count": len(assigned_workers),
                    "assigned_worker_names_text": ", ".join(assigned_worker_names),
                    "scope_locked": scope_locked,
                    "self_assignable": self_assignable,
                }
            )
        options.sort(
            key=lambda item: (
                0 if item.get("role") == "admin" else 1,
                (item["manager_name"] or "").casefold(),
                item["username"].casefold(),
            )
        )
        return options

    def _apply_worker_manager(self, worker: WorkerRecord, manager: UserSummary | None) -> None:
        worker.manager_id = manager.id if manager else None
        worker.manager_name = manager.username if manager else "system"
        if manager is None:
            worker.group = None
        elif not str(worker.group or "").strip():
            worker.group = manager.username
        updated_manager_name = worker.manager_name
        for channel in self.channels:
            if channel.worker_id == worker.id:
                channel.manager_name = updated_manager_name
        for job in self.jobs:
            if job.worker_name == worker.id:
                job.manager_name = updated_manager_name

    def _clear_worker_channels(self, worker_id: str) -> int:
        cleaned_worker_id = str(worker_id or "").strip()
        if not cleaned_worker_id:
            return 0

        worker_channel_ids = [
            channel.id
            for channel in self.channels
            if str(channel.worker_id or "").strip() == cleaned_worker_id
        ]
        if not worker_channel_ids:
            return 0

        channel_id_set = set(worker_channel_ids)
        linked_user_ids: set[str] = set()
        removed_jobs = [job for job in self.jobs if job.channel_id in channel_id_set]

        for channel in list(self.channels):
            if channel.id not in channel_id_set:
                continue
            linked_user_ids.update(
                str(link.get("user_id") or "").strip()
                for link in self.channel_user_links
                if link.get("channel_id") == channel.id
            )
            self._schedule_channel_browser_profile_cleanup(channel)

        for job in removed_jobs:
            self._purge_job_artifacts(job, exclude_job_id=job.id)

        self.channels = [channel for channel in self.channels if channel.id not in channel_id_set]
        self.channel_user_links = [
            link for link in self.channel_user_links if str(link.get("channel_id") or "").strip() not in channel_id_set
        ]
        self.jobs = [job for job in self.jobs if job.channel_id not in channel_id_set]

        for user_id in linked_user_ids:
            if user_id:
                self._close_orphan_browser_sessions_for_user(user_id)

        return len(worker_channel_ids)

    def _close_user_worker_browser_sessions(self, user_id: str, worker_id: str, *, reason: str) -> bool:
        cleaned_user_id = str(user_id or "").strip()
        cleaned_worker_id = str(worker_id or "").strip()
        if not cleaned_user_id or not cleaned_worker_id:
            return False
        closed_at = self._now(trim=False)
        changed = False
        for session in self.browser_sessions:
            if session.owner_user_id != cleaned_user_id:
                continue
            if str(session.target_worker_id or "").strip() != cleaned_worker_id:
                continue
            if session.status not in {"launching", "awaiting_confirmation", "confirmed"}:
                continue
            session.status = "closed"
            session.expires_at = closed_at
            session.last_error = reason
            changed = True
        return changed

    def _clear_user_worker_channels(self, user_id: str, worker_id: str) -> int:
        cleaned_user_id = str(user_id or "").strip()
        cleaned_worker_id = str(worker_id or "").strip()
        if not cleaned_user_id or not cleaned_worker_id:
            return 0

        affected_channels = [
            channel
            for channel in self.channels
            if str(channel.worker_id or "").strip() == cleaned_worker_id
            and any(
                str(link.get("channel_id") or "").strip() == channel.id
                and str(link.get("user_id") or "").strip() == cleaned_user_id
                for link in self.channel_user_links
            )
        ]
        if not affected_channels:
            self._close_user_worker_browser_sessions(
                cleaned_user_id,
                cleaned_worker_id,
                reason="Session da dong do user khong con duoc cap VPS.",
            )
            return 0

        affected_channel_ids = {channel.id for channel in affected_channels}
        self.channel_user_links = [
            link
            for link in self.channel_user_links
            if not (
                str(link.get("user_id") or "").strip() == cleaned_user_id
                and str(link.get("channel_id") or "").strip() in affected_channel_ids
            )
        ]

        removable_channel_ids: set[str] = set()
        removed_jobs: list[RenderJobRecord] = []
        for channel in affected_channels:
            still_linked = any(
                str(link.get("channel_id") or "").strip() == channel.id
                for link in self.channel_user_links
            )
            if still_linked:
                continue
            removable_channel_ids.add(channel.id)
            self._schedule_channel_browser_profile_cleanup(channel)
            removed_jobs.extend([job for job in self.jobs if job.channel_id == channel.id])

        for job in removed_jobs:
            self._purge_job_artifacts(job, exclude_job_id=job.id)

        if removable_channel_ids:
            self.channels = [channel for channel in self.channels if channel.id not in removable_channel_ids]
            self.jobs = [job for job in self.jobs if job.channel_id not in removable_channel_ids]

        self._close_user_worker_browser_sessions(
            cleaned_user_id,
            cleaned_worker_id,
            reason="Session da dong do user khong con duoc cap VPS.",
        )
        self._close_orphan_browser_sessions_for_user(cleaned_user_id)
        return len(affected_channels)

    def _purge_worker_assignment_scope(self, worker_id: str, *, session_reason: str) -> None:
        cleaned_worker_id = str(worker_id or "").strip()
        if not cleaned_worker_id:
            return

        linked_user_ids = {
            str(link.get("user_id") or "").strip()
            for link in self.user_worker_links
            if str(link.get("worker_id") or "").strip() == cleaned_worker_id and str(link.get("user_id") or "").strip()
        }
        for user_id in linked_user_ids:
            self._clear_user_worker_channels(user_id, cleaned_worker_id)

        self._clear_worker_channels(cleaned_worker_id)

        removed_jobs = [
            job for job in self.jobs if str(job.worker_name or "").strip() == cleaned_worker_id
        ]
        for job in removed_jobs:
            self._purge_job_artifacts(job, exclude_job_id=job.id)
        self.jobs = [job for job in self.jobs if str(job.worker_name or "").strip() != cleaned_worker_id]

        self.user_worker_links = [
            link for link in self.user_worker_links if str(link.get("worker_id") or "").strip() != cleaned_worker_id
        ]

        for user_id in linked_user_ids:
            self._close_user_worker_browser_sessions(user_id, cleaned_worker_id, reason=session_reason)
            self._close_orphan_browser_sessions_for_user(user_id)

    def get_admin_user_index_context(
        self,
        *,
        manager_ids: list[str] | None = None,
        viewer_role: str = "admin",
        viewer_id: str | None = None,
        notice: str | None = None,
        notice_level: str = "success",
        workspace_mode: str = "upload",
    ) -> dict[str, Any]:
        context = self._admin_shell_context(
            page_title="Danh sách ngu?i dùng",
            active_page="users",
            user_section="users",
            viewer_role=viewer_role,
            viewer_id=viewer_id,
            manager_ids=manager_ids,
            notice=notice,
            notice_level=notice_level,
            workspace_mode=workspace_mode,
        )
        context.update(
            {
                "template": "admin/user_index.html",
                "users": self._build_user_rows(manager_ids, viewer_role=viewer_role, viewer_id=viewer_id),
                "manager_form_options": [
                    {"id": user.id, "label": user.username}
                    for user in self.users
                    if user.role == "manager" and (viewer_role != "manager" or user.id == viewer_id)
                ],
            }
        )
        if viewer_role == "manager" and viewer_id:
            context["manager_options"] = [item for item in context["manager_options"] if item["id"] == viewer_id]
        return context

    def get_admin_user_create_context(
        self,
        *,
        viewer_role: str = "admin",
        viewer_id: str | None = None,
        notice: str | None = None,
        notice_level: str = "success",
        form_data: dict[str, Any] | None = None,
        error: str | None = None,
        workspace_mode: str = "upload",
    ) -> dict[str, Any]:
        context = self._admin_shell_context(
            page_title="T?o user",
            active_page="users",
            user_section="create",
            viewer_role=viewer_role,
            viewer_id=viewer_id,
            notice=notice,
            notice_level=notice_level,
            workspace_mode=workspace_mode,
        )
        context.update(
            {
                "template": "admin/user_create.html",
                "form": form_data
                or {
                    "username": "",
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
        viewer_role: str = "admin",
        viewer_id: str | None = None,
        notice: str | None = None,
        notice_level: str = "success",
        error: str | None = None,
        workspace_mode: str = "upload",
    ) -> dict[str, Any]:
        user = self._find_user(user_id)
        meta = self._user_meta_record(user.id)
        manager = next((item for item in self.users if item.username == user.manager_name), None)
        context = self._admin_shell_context(
            page_title="Cáº­p nháº­t user",
            active_page="users",
            user_section="users",
            viewer_role=viewer_role,
            viewer_id=viewer_id,
            notice=notice,
            notice_level=notice_level,
            workspace_mode=workspace_mode,
        )
        context.update(
            {
                "template": "admin/user_edit.html",
                "error": error,
                "manager_candidates": [{"id": item.id, "username": item.username} for item in self.users if item.role == "manager"],
                "user_record": {
                    "id": user.id,
                    "username": user.username,
                    "display_name": user.username,
                    "role": user.role,
                    "manager_id": manager.id if manager else "",
                    "telegram": meta.get("telegram") or "",
                    "password": "",
                },
            }
        )
        return context

    def get_admin_manager_page_context(
        self,
        *,
        notice: str | None = None,
        notice_level: str = "success",
        workspace_mode: str = "upload",
    ) -> dict[str, Any]:
        return self._build_role_page_context(
            role_kind="manager",
            notice=notice,
            notice_level=notice_level,
            workspace_mode=workspace_mode,
        )

    def get_admin_admin_page_context(
        self,
        *,
        notice: str | None = None,
        notice_level: str = "success",
        workspace_mode: str = "upload",
    ) -> dict[str, Any]:
        return self._build_role_page_context(
            role_kind="admin",
            notice=notice,
            notice_level=notice_level,
            workspace_mode=workspace_mode,
        )

    def get_admin_user_bot_context(
        self,
        *,
        user_id: str,
        viewer_role: str = "admin",
        viewer_id: str | None = None,
        notice: str | None = None,
        notice_level: str = "success",
        workspace_mode: str = "upload",
    ) -> dict[str, Any]:
        user = self._find_user(user_id)
        meta = self._user_meta_record(user.id)
        assigned_workers = self._assigned_workers_for_user(user)
        assigned_worker = assigned_workers[0] if assigned_workers else None
        context = self._admin_shell_context(
            page_title=f"BOT c?a {user.username}",
            active_page="users",
            user_section="users",
            viewer_role=viewer_role,
            viewer_id=viewer_id,
            notice=notice,
            notice_level=notice_level,
            workspace_mode=workspace_mode,
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
                "assigned_workers": [
                    {
                        "id": worker.id,
                        "name": self._resolve_worker_display_name(worker.id),
                    }
                    for worker in assigned_workers
                ],
                "assigned_worker": {
                    "id": assigned_worker.id,
                    "name": self._resolve_worker_display_name(assigned_worker.id),
                }
                if assigned_worker
                else None,
                "assigned_worker_count": len(assigned_workers),
                "rows": self._build_user_bot_links(user.id),
                "worker_candidates": self._worker_candidates_for_user(user),
            }
        )
        return context

    def _filtered_worker_operation_tasks(self, manager_ids: list[str] | None = None) -> list[dict[str, Any]]:
        selected_ids = set(self._selected_manager_ids(manager_ids))
        tasks: list[dict[str, Any]] = []
        for task in self.worker_operation_tasks:
            if self._worker_operation_is_finished(task):
                continue
            manager_id = str(task.get("manager_id") or "").strip()
            if selected_ids and manager_id not in selected_ids:
                continue
            tasks.append(task)
        tasks.sort(
            key=lambda item: (
                self._parse_datetime(item.get("created_at")) or self._now(trim=False),
                str(item.get("worker_id") or "").strip(),
            )
        )
        return tasks

    def _build_operation_placeholder_row(self, task: dict[str, Any]) -> dict[str, Any]:
        status_label, status_class = self._worker_operation_badge(task)
        placeholder_name = str(task.get("worker_name") or task.get("vps_ip") or task.get("worker_id") or "").strip()
        operation_failed = str(task.get("status") or "").strip() == "failed"
        return {
            "index": 0,
            "id": str(task.get("worker_id") or "").strip(),
            "bot_id": str(task.get("worker_id") or "").strip(),
            "manager_id": str(task.get("manager_id") or "").strip(),
            "manager_name": str(task.get("manager_name") or "").strip() or "system",
            "name": placeholder_name,
            "raw_name": placeholder_name,
            "group": str(task.get("group") or "").strip() or "-",
            "assigned_user_id": "",
            "assigned_user_ids": [],
            "assigned_user_name": "",
            "assigned_user_names_text": "",
            "status_key": f"{task.get('kind')}-{task.get('status')}",
            "status_label": status_label,
            "status_class": status_class,
            "created_at": self._format_full_datetime(self._parse_datetime(task.get("created_at"))),
            "total_channels": 0,
            "total_users": 0,
            "thread_text": "--",
            "running_threads": 0,
            "max_threads": 0,
            "threads": 0,
            "live_type_key": "",
            "live_type_label": "--",
            "live_thread_text": "--",
            "live_total_threads": 0,
            "live_running_threads": 0,
            "live_pending_threads": 0,
            "ram_text": "--",
            "ram_percent": 0,
            "disk_text": "--",
            "bandwidth_text": "--",
            "load_percent": 0,
            "cpu_percent": 0,
            "space_text": "--",
            "meta_text": str(task.get("message") or "").strip() or "Control-plane dang x? lý trên VPS.",
            "row_dimmed": True,
            "actions_disabled": not operation_failed,
            "is_operation_placeholder": True,
            "operation_kind": str(task.get("kind") or "").strip(),
            "operation_status": str(task.get("status") or "").strip(),
        }

    def _apply_operation_state_to_worker_row(self, row: dict[str, Any], task: dict[str, Any]) -> dict[str, Any]:
        status_label, status_class = self._worker_operation_badge(task)
        kind = str(task.get("kind") or "").strip()
        status = str(task.get("status") or "").strip()
        operation_failed = status == "failed"
        updated_row = dict(row)
        updated_row.update(
            {
                "status_key": f"{kind}-{status}",
                "status_label": status_label,
                "status_class": status_class,
                "meta_text": str(task.get("message") or "").strip() or updated_row.get("meta_text") or updated_row.get("manager_name") or "-",
                "row_dimmed": True,
                "actions_disabled": not operation_failed,
                "operation_kind": kind,
                "operation_status": status,
            }
        )
        return updated_row

    def _build_bot_rows(self, manager_ids: list[str] | None = None) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        operation_tasks = self._filtered_worker_operation_tasks(manager_ids)
        operation_by_worker_id = {
            str(task.get("worker_id") or "").strip(): task
            for task in operation_tasks
            if str(task.get("worker_id") or "").strip()
        }
        visible_worker_ids: set[str] = set()
        for worker in self._filtered_workers(manager_ids):
            status_label, status_class = self._worker_status_badge(worker.status)
            thread_summary = self._worker_thread_summary(worker)
            worker_links = [
                link
                for link in self.user_worker_links
                if str(link.get("worker_id") or "").strip() == worker.id
            ]
            live_total_threads = sum(max(0, int(link.get("threads") or 0)) for link in worker_links)
            if live_total_threads <= 0:
                live_total_threads = max(0, int(worker.threads or 0))
            live_type_keys = {
                self._normalize_live_bot_type(link.get("bot_type"), str(link.get("note") or ""))
                for link in worker_links
            }
            if not live_type_keys:
                live_type_key = ""
            elif len(live_type_keys) == 1:
                live_type_key = next(iter(live_type_keys))
            else:
                live_type_key = "mixed"
            live_type_label = self._live_bot_type_label(live_type_key)
            live_running_threads = 0
            live_pending_threads = 0
            if live_type_key == "backup":
                live_thread_text = f"{live_running_threads}/{live_pending_threads}/{live_total_threads}"
            else:
                live_thread_text = f"{live_running_threads}/{live_total_threads}"
            assigned_users = self._assigned_users_for_worker(worker.id)
            assigned_user_ids = [user.id for user in assigned_users]
            assigned_user_names = [user.username for user in assigned_users]
            if len(assigned_users) == 1:
                assigned_user_id = assigned_users[0].id
                assigned_user_name = assigned_users[0].username
            elif len(assigned_users) > 1:
                assigned_user_id = ""
                assigned_user_name = f"{len(assigned_users)} user"
            else:
                assigned_user_id = ""
                assigned_user_name = "BOT tr?ng"
            row = {
                "index": 0,
                "id": worker.id,
                "bot_id": worker.id,
                "manager_id": worker.manager_id or "",
                "manager_name": worker.manager_name,
                "name": self._resolve_worker_display_name(worker.id),
                "raw_name": self._resolve_worker_display_name(worker.id),
                "group": worker.group or worker.manager_name,
                "assigned_user_id": assigned_user_id,
                "assigned_user_ids": assigned_user_ids,
                "assigned_user_name": assigned_user_name,
                "assigned_user_names_text": ", ".join(assigned_user_names),
                "status_key": worker.status,
                "status_label": status_label,
                "status_class": status_class,
                "created_at": self._format_full_datetime(worker.created_at or worker.last_seen_at),
                "total_channels": len([channel for channel in self.channels if channel.worker_id == worker.id]),
                "total_users": len([link for link in self.user_worker_links if link["worker_id"] == worker.id]),
                "thread_text": thread_summary["thread_text"],
                "running_threads": thread_summary["running_threads"],
                "max_threads": thread_summary["max_threads"],
                "threads": worker.threads,
                "live_type_key": live_type_key,
                "live_type_label": live_type_label,
                "live_thread_text": live_thread_text,
                "live_total_threads": live_total_threads,
                "live_running_threads": live_running_threads,
                "live_pending_threads": live_pending_threads,
                "ram_text": f"{worker.ram_used_gb:.1f}GB / {worker.ram_total_gb:.1f}GB"
                if worker.ram_total_gb > 0
                else "--",
                "ram_percent": worker.ram_percent,
                "disk_text": f"{worker.disk_used_gb:.1f}/{worker.disk_total_gb:.1f}GB",
                "bandwidth_text": f"{worker.bandwidth_kbps:.2f}KB/s",
                "load_percent": worker.load_percent,
                "cpu_percent": worker.load_percent,
                "space_text": f"{worker.disk_used_gb:.1f}/{worker.disk_total_gb:.1f}GB",
                "meta_text": worker.manager_name,
                "row_dimmed": False,
                "actions_disabled": False,
                "is_operation_placeholder": False,
                "operation_kind": "",
                "operation_status": "",
            }
            worker_task = operation_by_worker_id.get(worker.id)
            if worker_task is not None:
                row = self._apply_operation_state_to_worker_row(row, worker_task)
            rows.append(row)
            visible_worker_ids.add(worker.id)
        for task in operation_tasks:
            if str(task.get("kind") or "").strip() != "install":
                continue
            task_worker_id = str(task.get("worker_id") or "").strip()
            if task_worker_id in visible_worker_ids:
                continue
            rows.append(self._build_operation_placeholder_row(task))
        for index, row in enumerate(rows, start=1):
            row["index"] = index
        return rows

    def get_admin_bot_index_context(
        self,
        *,
        manager_ids: list[str] | None = None,
        viewer_role: str = "admin",
        viewer_id: str | None = None,
        focus_user_id: str | None = None,
        notice: str | None = None,
        notice_level: str = "success",
        workspace_mode: str = "upload",
    ) -> dict[str, Any]:
        worker_rows = self._build_bot_rows(manager_ids)
        context = self._admin_shell_context(
            page_title="Danh sách BOT",
            active_page="workers",
            viewer_role=viewer_role,
            viewer_id=viewer_id,
            manager_ids=manager_ids,
            notice=notice,
            notice_level=notice_level,
            workspace_mode=workspace_mode,
        )
        focus_user: dict[str, Any] | None = None
        if focus_user_id:
            user = self._find_user(focus_user_id)
            resolved_manager_id = user.id if user.role == "manager" else (self._resolved_user_manager_id(user) or "")
            assigned_workers = self._workspace_workers_for_user(user.id) if user.role in {"user", "manager", "admin"} else []
            focus_user = {
                "id": user.id,
                "username": user.username,
                "display_name": user.display_name,
                "role": user.role,
                "manager_id": resolved_manager_id,
                "manager_name": user.manager_name or (user.username if user.role == "manager" else "-"),
                "assigned_worker_id": assigned_workers[0].id if assigned_workers else "",
                "assigned_worker_name": self._resolve_worker_display_name(assigned_workers[0].id) if assigned_workers else "",
                "assigned_worker_ids": [worker.id for worker in assigned_workers],
                "assigned_worker_names": [self._resolve_worker_display_name(worker.id) for worker in assigned_workers],
                "assigned_worker_count": len(assigned_workers),
                "total_channels": self._user_channel_count(user),
            }
        context.update(
            {
                "template": "admin/worker_index.html",
                "workers": worker_rows,
                "worker_event_cursor": self._latest_admin_notification_id(manager_ids=manager_ids),
                "focus_user": focus_user,
                "manager_binding_locked": viewer_role == "manager",
                "bot_manager_options": self._bot_manager_options(viewer_role=viewer_role, viewer_id=viewer_id),
                "bot_user_options": self._bot_user_options(viewer_role=viewer_role, viewer_id=viewer_id),
                "selected_manager_labels": [
                    item["username"] for item in context.get("manager_options", []) if item.get("selected")
                ],
            }
        )
        if viewer_role == "manager" and viewer_id:
            context["manager_options"] = [item for item in context["manager_options"] if item["id"] == viewer_id]
        return context

    def get_admin_live_workspace_context(
        self,
        *,
        manager_ids: list[str] | None = None,
        viewer_role: str = "admin",
        viewer_id: str | None = None,
        notice: str | None = None,
        notice_level: str = "success",
    ) -> dict[str, Any]:
        context = self._admin_shell_context(
            page_title="Ði?u ph?i live stream",
            active_page="live_workspace",
            viewer_role=viewer_role,
            viewer_id=viewer_id,
            manager_ids=manager_ids,
            notice=notice,
            notice_level=notice_level,
            workspace_mode="live",
        )
        selected_manager_labels = [
            item["username"] for item in context.get("manager_options", []) if item.get("selected")
        ]
        live_scope_count = len(selected_manager_labels)
        if viewer_role == "manager" and viewer_id:
            live_scope_count = 1
        if not live_scope_count:
            live_scope_count = context["summary"].total_managers
        scoped_manager_ids = self._effective_manager_scope_ids(
            viewer_role=viewer_role,
            viewer_id=viewer_id,
            manager_ids=manager_ids,
        )
        if scoped_manager_ids:
            scoped_workers = [worker for worker in self.workers if worker.manager_id in scoped_manager_ids]
            scoped_users = [
                user for user in self.users
                if user.role == "user" and self._resolved_user_manager_id(user) in scoped_manager_ids
            ]
        elif viewer_role == "manager" and viewer_id:
            scoped_workers = [worker for worker in self.workers if worker.manager_id == viewer_id]
            scoped_users = [
                user for user in self.users
                if user.role == "user" and self._resolved_user_manager_id(user) == viewer_id
            ]
        else:
            scoped_workers = list(self.workers)
            scoped_users = [user for user in self.users if user.role == "user"]

        live_bot_options: list[dict[str, Any]] = []
        for worker in scoped_workers:
            status_label, status_class = self._worker_status_badge(worker.status)
            thread_summary = self._worker_thread_summary(worker)
            live_bot_options.append(
                {
                    "id": worker.id,
                    "name": self._resolve_worker_display_name(worker.id),
                    "group": worker.group or worker.manager_name or "-",
                    "manager_name": worker.manager_name or "-",
                    "status_label": status_label,
                    "status_class": status_class,
                    "thread_text": thread_summary["thread_text"],
                    "connected": worker.status in {"online", "busy"},
                }
            )
        live_bot_options.sort(key=lambda item: str(item["name"]).casefold())

        live_user_options: list[dict[str, Any]] = []
        for user in scoped_users:
            live_user_options.append(
                {
                    "id": user.id,
                    "username": user.username,
                    "display_name": user.display_name or user.username,
                    "manager_name": user.manager_name or "-",
                    "channel_count": self._user_channel_count(user),
                    "bot_count": self._user_worker_count(user),
                }
            )
        live_user_options.sort(key=lambda item: str(item["username"]).casefold())

        connected_worker_count = len([worker for worker in scoped_workers if worker.status in {"online", "busy"}])
        context.update(
            {
                "template": "admin/live_workspace.html",
                "selected_manager_labels": selected_manager_labels,
                "live_shortcuts": [
                    {
                        "title": "Qu?n lý ngu?i dùng",
                        "description": "Dùng chung module user v?i Upload, d?i scope b?ng tab Live Stream ? d?u trang.",
                        "href": self._with_query("/admin/user/index", workspace="live"),
                        "icon": "users",
                        "button_label": "M? danh sách user",
                    },
                    {
                        "title": "Qu?n lý BOT live",
                        "description": "Dùng chung b?ng BOT hi?n t?i; ?n thao tác upload-only và gi? nguyên filter manager.",
                        "href": self._with_query("/admin/ManagerBOT/index", workspace="live"),
                        "icon": "server",
                        "button_label": "M? danh sách BOT",
                    },
                ],
                "live_scope": {
                    "manager_count": live_scope_count,
                    "manager_labels": selected_manager_labels,
                    "worker_count": context["summary"].total_workers,
                    "user_count": context["summary"].total_users,
                },
                "live_form_defaults": {
                    "platform_label": "YouTube RTMP",
                    "platform_note": "B? phân lo?i 1080/4K; ch?t lu?ng lu?ng ph? thu?c media d?u vào và pipeline ffmpeg.",
                    "backup_delay_minutes": 3,
                    "video_placeholder": "Dán link video ngu?n ho?c media URL kh? d?ng v?i downloader hi?n t?i",
                    "audio_placeholder": "Tùy ch?n: link audio n?n ho?c soundtrack riêng",
                },
                "live_scope_cards": [
                    {
                        "title": "Ngu?i dùng trong scope",
                        "value": str(len(live_user_options)),
                        "meta": "User du?c phép t?o lu?ng trong workspace hi?n t?i.",
                        "icon": "users",
                    },
                    {
                        "title": "BOT kh? d?ng",
                        "value": f"{connected_worker_count}/{len(live_bot_options)}",
                        "meta": "BOT dang k?t n?i / t?ng BOT trong scope manager.",
                        "icon": "server",
                    },
                    {
                        "title": "Backup m?c d?nh",
                        "value": f"{3} phút",
                        "meta": "Delay kh?i d?ng fallback theo rule cu, có th? ch?nh trên t?ng lu?ng.",
                        "icon": "shield-check",
                    },
                ],
                "live_user_options": live_user_options,
                "live_bot_options": live_bot_options,
                "live_backup_bot_options": live_bot_options,
                "live_policy_notes": [
                    "M?t lu?ng ch? ch?n m?t BOT chính và m?t BOT backup tùy ch?n.",
                    "YouTube RTMP du?c khóa c? d?nh ? phase UI d? bám nghi?p v? app cu.",
                    "Video là b?t bu?c, audio là tùy ch?n; backup delay gi? theo phút nhu app cu.",
                    "L?ch live dùng c?p th?i gian b?t d?u/k?t thúc, không còn nhánh 1080 hay 4K.",
                ],
                "live_stream_rows": [],
            }
        )
        if viewer_role == "manager" and viewer_id:
            context["manager_options"] = [item for item in context["manager_options"] if item["id"] == viewer_id]
        return context

    def get_admin_bots_of_user_context(
        self,
        *,
        user_id: str,
        viewer_role: str = "admin",
        viewer_id: str | None = None,
        notice: str | None = None,
        notice_level: str = "success",
        workspace_mode: str = "upload",
    ) -> dict[str, Any]:
        user = self._find_user(user_id)
        if user.role == "user":
            worker_source = self._assigned_workers_for_user(user)
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
                    "bot_id": worker.id,
                    "name": self._resolve_worker_display_name(worker.id),
                    "group": worker.group or worker.manager_name,
                    "status_label": status_label,
                    "status_class": status_class,
                    "created_at": self._format_full_datetime(worker.last_seen_at),
                    "total_channels": len([channel for channel in self.channels if channel.worker_id == worker.id]),
                    "total_users": len([link for link in self.user_worker_links if link["worker_id"] == worker.id]),
                    "threads": worker.threads,
                    "disk_text": f"{worker.disk_used_gb:.1f}/{worker.disk_total_gb:.1f}GB",
                    "bandwidth_text": f"{worker.bandwidth_kbps:.2f}KB/s",
                }
            )

        context = self._admin_shell_context(
            page_title=f"Danh sách BOT c?a {user.username}",
            active_page="workers",
            viewer_role=viewer_role,
            viewer_id=viewer_id,
            notice=notice,
            notice_level=notice_level,
            workspace_mode=workspace_mode,
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
        viewer_role: str = "admin",
        viewer_id: str | None = None,
        notice: str | None = None,
        notice_level: str = "success",
        workspace_mode: str = "upload",
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
            page_title=f"Danh sách user c?a {self._resolve_worker_display_name(worker.id)}",
            active_page="workers",
            viewer_role=viewer_role,
            viewer_id=viewer_id,
            notice=notice,
            notice_level=notice_level,
            workspace_mode=workspace_mode,
        )
        context.update(
            {
                "template": "admin/user_of_bot.html",
                "target_bot": {
                    "id": worker.id,
                    "name": self._resolve_worker_display_name(worker.id),
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
            raise ValueError("UserName, DisplayName vÃ  Password lÃ  báº¯t buá»c.")
        if any(user.username.lower() == username.lower() for user in self.users):
            raise ValueError("UserName ÄÃ£ tá»n táº¡i.")
        if role not in {"user", "manager", "admin"}:
            raise ValueError("Role khÃ´ng há»£p lá».")

        manager_name: str | None = None
        if role == "user":
            if not manager_id:
                manager_name = None
            else:
                manager = self._find_user(manager_id)
                if manager.role != "manager":
                    raise ValueError("Manager du?c ch?n không h?p l?.")
                manager_name = manager.username

        user_id = f"user-{uuid4().hex[:8]}"
        self.users.append(UserSummary(id=user_id, username=username, display_name=display_name, role=role, manager_name=manager_name))  # type: ignore[arg-type]
        self.user_meta[user_id] = {
            "password_hash": self._hash_password(password.strip()),
            "password_algo": "pbkdf2_sha256",
            "password": password.strip(),
            "telegram": (telegram or "").strip(),
            "updated_by": updated_by,
            "updated_at": self._now(),
            "created_at": self._now(),
        }
        self._save_state()
        return {"user_id": user_id, "username": username}

    def _validate_admin_username(self, username: str, *, exclude_user_id: str | None = None) -> str:
        normalized_username = username.strip()
        if not normalized_username:
            raise ValueError("TÃªn ÄÄng nháº­p lÃ  báº¯t buá»c.")
        if any(
            user.id != exclude_user_id and user.username.lower() == normalized_username.lower()
            for user in self.users
        ):
            raise ValueError("TÃªn ÄÄng nháº­p ÄÃ£ tá»n táº¡i.")
        return normalized_username

    def _cascade_manager_username_change(self, old_username: str, new_username: str) -> None:
        if old_username == new_username:
            return
        for user in self.users:
            if user.role == "user" and user.manager_name == old_username:
                user.manager_name = new_username
        for worker in self.workers:
            if worker.manager_name == old_username:
                worker.manager_name = new_username
        for channel in self.channels:
            if channel.manager_name == old_username:
                channel.manager_name = new_username
        for job in self.jobs:
            if job.manager_name == old_username:
                job.manager_name = new_username

    def delete_admin_user(self, user_id: str) -> None:
        user = self._find_user(user_id)
        if user.role == "admin" and len([item for item in self.users if item.role == "admin"]) <= 1:
            raise ValueError("KhÃ´ng thá» xÃ³a admin cuá»i cÃ¹ng.")
        if user.role == "manager" and any(item.role == "user" and item.manager_name == user.username for item in self.users):
            raise ValueError("Manager nÃ y Äang quáº£n lÃ½ user khÃ¡c, chÆ°a thá» xÃ³a.")

        self.users = [item for item in self.users if item.id != user_id]
        self.user_meta.pop(user_id, None)
        self.user_worker_links = [item for item in self.user_worker_links if item["user_id"] != user_id]
        self.channel_user_links = [item for item in self.channel_user_links if item["user_id"] != user_id]
        for session in [item for item in self.upload_sessions if item.owner_user_id == user_id]:
            self._remove_upload_session_file(session)
        self.upload_sessions = [item for item in self.upload_sessions if item.owner_user_id != user_id]
        self.browser_sessions = [item for item in self.browser_sessions if item.owner_user_id != user_id]
        self._save_state()

    def reset_admin_user_password(self, user_id: str, password: str, updated_by: str = "admin") -> None:
        if not password.strip():
            raise ValueError("Password má»i lÃ  báº¯t buá»c.")
        self._find_user(user_id)
        meta = self._user_meta_record(user_id)
        self._set_user_password(user_id, password.strip())
        meta["updated_by"] = updated_by
        meta["updated_at"] = self._now()
        self._save_state()

    def update_admin_user(
        self,
        *,
        user_id: str,
        username: str,
        password: str | None,
        manager_id: str | None,
        telegram: str | None = None,
        actor_role: str = "admin",
        updated_by: str = "admin",
    ) -> UserSummary:
        user = self._find_user(user_id)
        previous_telegram = self._user_telegram_chat_id(user_id)
        next_telegram = previous_telegram

        old_username = user.username
        can_edit_username = actor_role == "admin" or (actor_role == "manager" and user.role == "user")
        if can_edit_username:
            normalized_username = self._validate_admin_username(username, exclude_user_id=user.id)
            user.username = normalized_username
            if user.role == "manager":
                self._cascade_manager_username_change(old_username, user.username)

        user.display_name = user.username

        if user.role == "user":
            if not manager_id:
                user.manager_name = None
            else:
                manager = self._find_user(manager_id)
                if manager.role != "manager":
                    raise ValueError("Manager du?c ch?n không h?p l?.")
                user.manager_name = manager.username
        else:
            user.manager_name = None

        meta = self._user_meta_record(user_id)
        if telegram is not None:
            next_telegram = self._normalize_telegram_chat_id(telegram)
            meta["telegram"] = next_telegram
        if password and password.strip():
            self._set_user_password(user_id, password.strip(), updated_at=self._now())
        meta["updated_by"] = updated_by
        meta["updated_at"] = self._now()
        self._save_state()
        if next_telegram and next_telegram != previous_telegram:
            self._send_telegram_alert(
                self._telegram_linked_confirmation_message(user),
                chat_id=next_telegram,
            )
        elif previous_telegram and not next_telegram:
            self._send_telegram_alert(
                self._telegram_unlinked_confirmation_message(user),
                chat_id=previous_telegram,
            )
        return user

    def update_role_manager(self, user_id: str, promote: bool, updated_by: str = "admin") -> None:
        user = self._find_user(user_id)
        if promote:
            if user.role == "admin":
                raise ValueError("Admin hiá»n táº¡i khÃ´ng cáº§n gÃ¡n thÃªm quyá»n manager.")
            user.role = "manager"
            user.manager_name = None
        else:
            if user.role != "manager":
                raise ValueError("User nÃ y khÃ´ng pháº£i manager.")
            if any(item.role == "user" and item.manager_name == user.username for item in self.users):
                raise ValueError("Manager nÃ y Äang quáº£n lÃ½ user khÃ¡c, chÆ°a thá» gá»¡ quyá»n.")
            user.role = "user"
            user.manager_name = None

        meta = self._user_meta_record(user_id)
        meta["updated_by"] = updated_by
        meta["updated_at"] = self._now()
        self._save_state()

    def update_role_admin(self, user_id: str, promote: bool, updated_by: str = "admin") -> None:
        user = self._find_user(user_id)
        if promote:
            user.role = "admin"
            user.manager_name = None
        else:
            if user.role != "admin":
                raise ValueError("User nÃ y khÃ´ng pháº£i admin.")
            if len([item for item in self.users if item.role == "admin"]) <= 1:
                raise ValueError("KhÃ´ng thá» gá»¡ quyá»n admin cuá»i cÃ¹ng.")
            user.role = "user"
            user.manager_name = None

        meta = self._user_meta_record(user_id)
        meta["updated_by"] = updated_by
        meta["updated_at"] = self._now()
        self._save_state()

    def update_bot(
        self,
        worker_id: str,
        name: str,
        group: str | None,
        manager_id: str | None,
        *,
        assigned_user_id: str | None = None,
        assigned_user_ids: list[str] | None = None,
        confirm_manager_transfer_cleanup: bool = False,
        viewer_role: str = "admin",
        viewer_id: str | None = None,
        updated_by: str = "admin",
    ) -> None:
        worker = self._find_worker(worker_id)
        if not name.strip():
            raise ValueError("Tên BOT là b?t bu?c.")
        worker.name = name.strip()
        normalized_group = str(group or "").strip()
        normalized_user_id = str(assigned_user_id or "").strip()
        normalized_user_ids: list[str] = []
        seen_user_ids: set[str] = set()
        if assigned_user_ids is not None:
            for raw_user_id in assigned_user_ids:
                user_id = str(raw_user_id or "").strip()
                if not user_id or user_id in seen_user_ids:
                    continue
                normalized_user_ids.append(user_id)
                seen_user_ids.add(user_id)
        manager: UserSummary | None = None
        normalized_manager_id = str(manager_id or "").strip()
        if normalized_manager_id:
            manager = self._find_user(normalized_manager_id)
            if manager.role != "manager":
                raise ValueError("Manager du?c ch?n không h?p l?.")

        if viewer_role == "manager":
            if manager is None:
                raise ValueError("Manager du?c ch?n không h?p l?.")
            if viewer_id and manager.id != viewer_id:
                raise ValueError("Manager không du?c d?i ph?m vi BOT sang manager khác.")
            if worker.manager_id and worker.manager_id != manager.id:
                raise ValueError("BOT này không n?m trong ph?m vi manager hi?n t?i.")

            self._apply_worker_manager(worker, manager)
            if normalized_group:
                worker.group = normalized_group

            current_worker_links = [
                link for link in self.user_worker_links if str(link.get("worker_id") or "").strip() == worker.id
            ]
            current_links_by_user_id = {
                str(link.get("user_id") or "").strip(): link
                for link in current_worker_links
                if str(link.get("user_id") or "").strip()
            }
            current_user_ids = set(current_links_by_user_id.keys())

            if assigned_user_ids is not None:
                selected_users: list[UserSummary] = []
                for selected_user_id in normalized_user_ids:
                    assigned_user = self._find_user(selected_user_id)
                    already_assigned = assigned_user.id in current_user_ids
                    if assigned_user.role == "user":
                        assigned_user_manager_id = self._resolved_user_manager_id(assigned_user)
                        if assigned_user_manager_id != manager.id and not already_assigned:
                            raise ValueError("User ph?i thu?c manager hi?n t?i.")
                    elif assigned_user.role == "manager":
                        if assigned_user.id != manager.id and not already_assigned:
                            raise ValueError("Manager ch? du?c ch?n chính mình trong BOT này.")
                    elif assigned_user.role == "admin":
                        if not already_assigned:
                            raise ValueError("User du?c ch?n không h?p l?.")
                    else:
                        raise ValueError("User du?c ch?n không h?p l?.")
                    selected_users.append(assigned_user)

                current_links_by_user_id = {
                    str(link.get("user_id") or "").strip(): link
                    for link in current_worker_links
                    if str(link.get("user_id") or "").strip()
                }
                selected_user_ids = {user.id for user in selected_users}

                for removed_user_id in current_user_ids - selected_user_ids:
                    self._clear_user_worker_channels(removed_user_id, worker.id)

                self.user_worker_links = [
                    link
                    for link in self.user_worker_links
                    if not (
                        str(link.get("worker_id") or "").strip() == worker.id
                        and str(link.get("user_id") or "").strip() in (current_user_ids - selected_user_ids)
                    )
                ]

                next_id = max([int(item.get("id") or 0) for item in self.user_worker_links], default=0) + 1
                for assigned_user in selected_users:
                    existing_link = current_links_by_user_id.get(assigned_user.id)
                    if existing_link is None:
                        self.user_worker_links.append(
                            {
                                "id": next_id,
                                "user_id": assigned_user.id,
                                "worker_id": worker.id,
                                "threads": self._fixed_assignment_threads(),
                                "bot_type": "1080p",
                                "note": "VPS duoc cap",
                            }
                        )
                        next_id += 1
                    else:
                        existing_link["threads"] = self._fixed_assignment_threads()
                        existing_link["note"] = str(existing_link.get("note") or "").strip() or "VPS duoc cap"
            elif normalized_user_id:
                assigned_user = self._find_user(normalized_user_id)
                if assigned_user.role == "user":
                    assigned_user_manager_id = self._resolved_user_manager_id(assigned_user)
                    if assigned_user_manager_id != manager.id:
                        raise ValueError("User ph?i thu?c manager hi?n t?i.")
                elif assigned_user.role == "manager":
                    if assigned_user.id != manager.id:
                        raise ValueError("Manager ch? du?c ch?n chính mình trong BOT này.")
                elif assigned_user.role == "admin":
                    if assigned_user.id not in current_user_ids:
                        raise ValueError("User du?c ch?n không h?p l?.")
                else:
                    raise ValueError("User du?c ch?n không h?p l?.")
                existing_link = next(
                    (
                        link
                        for link in self.user_worker_links
                        if str(link.get("worker_id") or "").strip() == worker.id
                        and str(link.get("user_id") or "").strip() == assigned_user.id
                    ),
                    None,
                )
                if existing_link is None:
                    next_id = max([int(item.get("id") or 0) for item in self.user_worker_links], default=0) + 1
                    self.user_worker_links.append(
                        {
                            "id": next_id,
                            "user_id": assigned_user.id,
                            "worker_id": worker.id,
                            "threads": self._fixed_assignment_threads(),
                            "bot_type": "1080p",
                            "note": "VPS duoc cap",
                        }
                    )
                else:
                    existing_link["threads"] = self._fixed_assignment_threads()
                    existing_link["note"] = str(existing_link.get("note") or "").strip() or "VPS duoc cap"

            self._save_state()
            return

        current_manager_id = str(worker.manager_id or "").strip()
        next_manager_id = str(manager.id if manager else "").strip()
        manager_changed = current_manager_id != next_manager_id
        if manager_changed:
            worker_links = [link for link in self.user_worker_links if str(link.get("worker_id") or "").strip() == worker.id]
            worker_channels = [channel for channel in self.channels if str(channel.worker_id or "").strip() == worker.id]
            worker_jobs = [job for job in self.jobs if str(job.worker_name or "").strip() == worker.id]
            worker_link_user_ids = {
                str(link.get("user_id") or "").strip()
                for link in worker_links
                if str(link.get("user_id") or "").strip()
            }
            can_drop_self_workspace_link = (
                not worker_channels
                and not worker_jobs
                and viewer_id is not None
                and worker_link_user_ids == {str(viewer_id).strip()}
            )
            if can_drop_self_workspace_link:
                self.user_worker_links = [
                    link
                    for link in self.user_worker_links
                    if not (
                        str(link.get("worker_id") or "").strip() == worker.id
                        and str(link.get("user_id") or "").strip() == str(viewer_id).strip()
                    )
                ]
            elif worker_links or worker_channels or worker_jobs:
                if not confirm_manager_transfer_cleanup:
                    raise ValueError(
                        "Ð?i manager BOT này s? xóa s?ch d? li?u user/kênh/job c?a manager hi?n t?i. "
                        "Hãy xác nh?n c?nh báo r?i th? l?i."
                    )
                self._purge_worker_assignment_scope(
                    worker.id,
                    session_reason="Session da dong do BOT da duoc chuyen sang manager khac.",
                )
        self._apply_worker_manager(worker, manager)
        if normalized_group:
            worker.group = normalized_group
        if manager is None:
            self._save_state()
            return
        current_worker_links = [
            link for link in self.user_worker_links if str(link.get("worker_id") or "").strip() == worker.id
        ]
        current_links_by_user_id = {
            str(link.get("user_id") or "").strip(): link
            for link in current_worker_links
            if str(link.get("user_id") or "").strip()
        }
        current_user_ids = set(current_links_by_user_id.keys())

        if assigned_user_ids is not None:
            selected_users: list[UserSummary] = []
            for selected_user_id in normalized_user_ids:
                assigned_user = self._find_user(selected_user_id)
                already_assigned = assigned_user.id in current_user_ids
                if assigned_user.role == "user":
                    assigned_user_manager_id = self._resolved_user_manager_id(assigned_user)
                    if assigned_user_manager_id != manager.id and not already_assigned:
                        raise ValueError("User ph?i thu?c manager dã ch?n.")
                elif assigned_user.role == "manager":
                    if assigned_user.id != manager.id and not already_assigned:
                        raise ValueError("Manager ch? du?c ch?n chính mình trong BOT này.")
                elif assigned_user.role == "admin":
                    if not already_assigned and (not viewer_id or assigned_user.id != viewer_id):
                        raise ValueError("Admin ch? du?c t? gán BOT cho chính tài kho?n admin dang dang nh?p.")
                else:
                    raise ValueError("User du?c ch?n không h?p l?.")
                selected_users.append(assigned_user)

            current_links_by_user_id = {
                str(link.get("user_id") or "").strip(): link
                for link in current_worker_links
                if str(link.get("user_id") or "").strip()
            }
            selected_user_ids = {user.id for user in selected_users}

            for removed_user_id in current_user_ids - selected_user_ids:
                self._clear_user_worker_channels(removed_user_id, worker.id)

            self.user_worker_links = [
                link
                for link in self.user_worker_links
                if not (
                    str(link.get("worker_id") or "").strip() == worker.id
                    and str(link.get("user_id") or "").strip() in (current_user_ids - selected_user_ids)
                )
            ]

            next_id = max([int(item.get("id") or 0) for item in self.user_worker_links], default=0) + 1
            for assigned_user in selected_users:
                existing_link = current_links_by_user_id.get(assigned_user.id)
                if existing_link is None:
                    self.user_worker_links.append(
                        {
                            "id": next_id,
                            "user_id": assigned_user.id,
                            "worker_id": worker.id,
                            "threads": self._fixed_assignment_threads(),
                            "bot_type": "1080p",
                            "note": "VPS duoc cap",
                        }
                    )
                    next_id += 1
                else:
                    existing_link["threads"] = self._fixed_assignment_threads()
                    existing_link["note"] = str(existing_link.get("note") or "").strip() or "VPS duoc cap"
        elif normalized_user_id:
            assigned_user = self._find_user(normalized_user_id)
            if assigned_user.role == "user":
                assigned_user_manager_id = self._resolved_user_manager_id(assigned_user)
                if assigned_user_manager_id != manager.id:
                    raise ValueError("User ph?i thu?c manager dã ch?n.")
            elif assigned_user.role == "manager":
                if assigned_user.id != manager.id:
                    raise ValueError("Manager ch? du?c ch?n chính mình trong BOT này.")
            elif assigned_user.role == "admin":
                if not viewer_id or assigned_user.id != viewer_id:
                    raise ValueError("Admin ch? du?c t? gán BOT cho chính tài kho?n admin dang dang nh?p.")
            else:
                raise ValueError("User du?c ch?n không h?p l?.")
            existing_link = next(
                (
                    link
                    for link in self.user_worker_links
                    if str(link.get("worker_id") or "").strip() == worker.id
                    and str(link.get("user_id") or "").strip() == assigned_user.id
                ),
                None,
            )
            if existing_link is None:
                next_id = max([int(item.get("id") or 0) for item in self.user_worker_links], default=0) + 1
                self.user_worker_links.append(
                    {
                        "id": next_id,
                        "user_id": assigned_user.id,
                        "worker_id": worker.id,
                        "threads": self._fixed_assignment_threads(),
                        "bot_type": "1080p",
                        "note": "VPS duoc cap",
                    }
                )
            else:
                existing_link["threads"] = self._fixed_assignment_threads()
                existing_link["note"] = str(existing_link.get("note") or "").strip() or "VPS duoc cap"
        self._save_state()

    def reconcile_assignment_target_bots(
        self,
        worker_ids: list[str],
        *,
        manager_id: str | None,
        assigned_user_id: str | None = None,
        viewer_role: str = "admin",
        viewer_id: str | None = None,
        updated_by: str = "admin",
    ) -> int:
        normalized_worker_ids: list[str] = []
        seen_worker_ids: set[str] = set()
        for raw_worker_id in worker_ids:
            worker_id = str(raw_worker_id or "").strip()
            if not worker_id or worker_id in seen_worker_ids:
                continue
            normalized_worker_ids.append(worker_id)
            seen_worker_ids.add(worker_id)

        if not manager_id:
            raise ValueError("Vui lòng ch?n manager.")

        manager = self._find_user(manager_id)
        allowed_manager_roles = {"manager"}
        if viewer_role == "admin" and viewer_id and manager.id == viewer_id:
            allowed_manager_roles.add("admin")
        if viewer_role == "manager" and viewer_id and manager.id == viewer_id:
            allowed_manager_roles.add("manager")
        if manager.role not in allowed_manager_roles:
            raise ValueError("Manager du?c ch?n không h?p l?.")
        if viewer_role == "manager" and viewer_id and manager.id != viewer_id:
            raise ValueError("Manager không du?c d?i ph?m vi BOT sang manager khác.")

        assigned_user: UserSummary | None = None
        if assigned_user_id:
            assigned_user = self._find_user(assigned_user_id)
            if assigned_user.role not in {"user", "admin", "manager"}:
                raise ValueError("Ngu?i nh?n du?c ch?n không h?p l?.")
            if assigned_user.role == "user":
                assigned_user_manager_id = self._resolved_user_manager_id(assigned_user)
                if assigned_user_manager_id != manager.id:
                    raise ValueError("User ph?i thu?c manager dã ch?n.")
            elif assigned_user.role == "manager":
                if assigned_user.id != manager.id:
                    raise ValueError("Manager ch? du?c ch?n chính mình trong BOT này.")

        selected_workers: list[WorkerRecord] = []
        for worker_id in normalized_worker_ids:
            worker = self._find_worker(worker_id)
            selected_workers.append(worker)

        if assigned_user is not None:
            previous_links = self._assigned_worker_links_for_user(assigned_user.id)
            previous_links_by_worker_id = {
                str(link.get("worker_id") or ""): link
                for link in previous_links
                if str(link.get("worker_id") or "")
            }
            previous_worker_ids = set(previous_links_by_worker_id.keys())
            selected_worker_ids = {worker.id for worker in selected_workers}

            for worker_id in previous_worker_ids - selected_worker_ids:
                self._clear_user_worker_channels(assigned_user.id, worker_id)

            for worker in selected_workers:
                self._apply_worker_manager(worker, manager)

            self.user_worker_links = [
                link for link in self.user_worker_links if str(link.get("user_id") or "") != assigned_user.id
            ]

            next_id = max([int(item.get("id") or 0) for item in self.user_worker_links], default=0) + 1
            for worker in selected_workers:
                previous_link = previous_links_by_worker_id.get(worker.id)
                self.user_worker_links.append(
                    {
                        "id": next_id,
                        "user_id": assigned_user.id,
                        "worker_id": worker.id,
                        "threads": max(
                            1,
                            int((previous_link or {}).get("threads") or worker.threads or 1),
                        ),
                        "bot_type": str((previous_link or {}).get("bot_type") or "live").strip() or "live",
                        "note": str((previous_link or {}).get("note") or "").strip() or "VPS duoc cap",
                    }
                )
                next_id += 1
        else:
            current_manager_pool_ids = set(self._manager_inventory_worker_ids(manager.id))
            selected_worker_ids = {worker.id for worker in selected_workers}
            removed_worker_ids = current_manager_pool_ids - selected_worker_ids

            for worker in selected_workers:
                self._apply_worker_manager(worker, manager)

            for worker_id in removed_worker_ids:
                worker = self._find_worker(worker_id)
                if self._assigned_user_for_worker(worker.id) is not None:
                    continue
                self._clear_worker_channels(worker.id)
                self._apply_worker_manager(worker, None)

        self._save_state()
        return len(normalized_worker_ids)

    def _delete_bot_state(self, worker_id: str) -> None:
        self._find_worker(worker_id)
        self._clear_worker_channels(worker_id)
        removed_jobs = [job for job in self.jobs if job.worker_name == worker_id]
        for job in removed_jobs:
            self._purge_job_artifacts(job, exclude_job_id=job.id)
        self.workers = [worker for worker in self.workers if worker.id != worker_id]
        self.user_worker_links = [link for link in self.user_worker_links if link["worker_id"] != worker_id]
        self.jobs = [job for job in self.jobs if job.worker_name != worker_id]

    def delete_bot(self, worker_id: str) -> None:
        self._delete_bot_state(worker_id)
        self.worker_connection_profiles.pop(str(worker_id or "").strip(), None)
        self.worker_operation_tasks = [
            task
            for task in self.worker_operation_tasks
            if str(task.get("worker_id") or "").strip() != str(worker_id or "").strip()
        ]
        self._save_state()

    def delete_bot_without_ssh(self, worker_id: str, *, deleted_by: str = "system") -> None:
        completed_task: dict[str, Any] | None = None
        worker_name = ""
        vps_ip = ""
        with self._worker_state_lock:
            worker = self._find_worker(worker_id)
            profile = dict(self.worker_connection_profiles.get(worker.id) or {})
            worker_name = self._resolve_worker_display_name(worker.id)
            vps_ip = str(profile.get("vps_ip") or "").strip()
            if not vps_ip and self._looks_like_ipv4(worker_name):
                vps_ip = worker_name
            actor = self._find_user_by_username(deleted_by)
            completed_task = {
                "worker_id": worker.id,
                "worker_name": worker_name,
                "vps_ip": vps_ip,
                "manager_name": str(worker.manager_name or "").strip() or "system",
                "requested_by": str(deleted_by or "").strip() or "system",
                "requested_role": actor.role if actor else "system",
            }
            self._remember_deleted_worker(
                worker.id,
                worker_name=worker_name,
                vps_ip=vps_ip or None,
                deleted_by=deleted_by,
                reason="delete_without_ssh",
            )
            self._delete_bot_state(worker.id)
            self.worker_connection_profiles.pop(str(worker.id or "").strip(), None)
            self.worker_operation_tasks = [
                task
                for task in self.worker_operation_tasks
                if str(task.get("worker_id") or "").strip() != str(worker.id or "").strip()
            ]
            self._save_state()
        if completed_task is not None:
            self._notify_telegram_chat_ids(
                self._bot_operation_recipient_chat_ids(completed_task),
                self._bot_decommission_completed_message(
                    completed_task,
                    worker_name=worker_name,
                    worker_id=str(worker_id or "").strip(),
                    vps_ip=vps_ip or worker_name,
                ),
            )

    def update_bot_thread(self, worker_id: str, thread: int) -> None:
        worker = self._find_worker(worker_id)
        if thread < 1:
            raise ValueError("Sá» luá»ng pháº£i lá»n hÆ¡n hoáº·c báº±ng 1.")
        worker.threads = self._fixed_assignment_threads()
        worker.capacity = self._fixed_assignment_threads()
        self._save_state()

    def add_user_bot(self, user_id: str, worker_id: str, threads: int, bot_type: str = "live", note: str | None = None) -> None:
        user = self._find_user(user_id)
        worker = self._find_worker(worker_id)
        if user.role != "user":
            raise ValueError("Chi user thuong moi duoc cap VPS truc tiep.")
        if user.manager_name and worker.manager_name != user.manager_name:
            raise ValueError("User chi duoc cap VPS thuoc manager cua minh.")

        normalized_note = (note or "").strip() or "VPS duoc cap"
        existing = next(
            (
                item
                for item in self.user_worker_links
                if str(item.get("user_id") or "") == user_id and str(item.get("worker_id") or "") == worker_id
            ),
            None,
        )
        if existing:
            existing["threads"] = self._fixed_assignment_threads()
            existing["bot_type"] = bot_type.lower()
            existing["note"] = normalized_note
        else:
            next_id = max([int(item.get("id") or 0) for item in self.user_worker_links], default=0) + 1
            self.user_worker_links.append(
                {
                    "id": next_id,
                    "user_id": user_id,
                    "worker_id": worker_id,
                    "threads": self._fixed_assignment_threads(),
                    "bot_type": bot_type.lower(),
                    "note": normalized_note,
                }
            )

        self._save_state()

    def delete_user_bot(self, mapping_id: int) -> None:
        mapping = next((item for item in self.user_worker_links if item["id"] == mapping_id), None)
        if mapping is None:
            raise KeyError(mapping_id)
        removed_worker_id = str(mapping.get("worker_id") or "").strip()
        removed_user_id = str(mapping.get("user_id") or "").strip()
        self._clear_user_worker_channels(removed_user_id, removed_worker_id)
        self.user_worker_links = [item for item in self.user_worker_links if item["id"] != mapping_id]
        for session in self.browser_sessions:
            if session.owner_user_id != removed_user_id:
                continue
            if removed_worker_id and session.target_worker_id != removed_worker_id:
                continue
            if session.status in {"launching", "awaiting_confirmation", "confirmed"}:
                session.status = "closed"
                session.expires_at = self._now(trim=False)
                session.last_error = "Session da dong do user khong con duoc cap VPS."
        self._save_state()

    def update_user_bot(self, mapping_id: int, threads: int, bot_type: str | None = None, note: str | None = None) -> None:
        for mapping in self.user_worker_links:
            if mapping["id"] != mapping_id:
                continue
            mapping["threads"] = self._fixed_assignment_threads()
            if bot_type:
                mapping["bot_type"] = bot_type.lower()
            if note is not None:
                mapping["note"] = (note or "").strip() or mapping.get("note") or "VPS duoc cap"
            self._save_state()
            return
        raise KeyError(mapping_id)

    def _filtered_channels_v2(
        self,
        *,
        manager_ids: list[str] | None = None,
        user_id: str | None = None,
        bot_id: str | None = None,
    ) -> tuple[list[ChannelRecord], dict[str, Any] | None, dict[str, Any] | None]:
        selected_manager_ids = set(self._selected_manager_ids(manager_ids))

        channel_source = list(self.channels)
        if selected_manager_ids:
            channel_source = [
                channel
                for channel in channel_source
                if self._resolve_channel_manager_id(channel) in selected_manager_ids
            ]

        filtered_user: dict[str, Any] | None = None
        filtered_bot: dict[str, Any] | None = None

        if user_id:
            user = self._find_user(user_id)
            filtered_user = {"id": user.id, "username": user.username, "display_name": user.display_name}
            assigned_channel_ids = {link["channel_id"] for link in self.channel_user_links if link["user_id"] == user.id}
            channel_source = [channel for channel in channel_source if channel.id in assigned_channel_ids]

        if bot_id:
            worker = self._find_worker(bot_id)
            filtered_bot = {"id": worker.id, "name": self._resolve_worker_display_name(worker.id)}
            channel_source = [channel for channel in channel_source if channel.worker_id == worker.id]

        return channel_source, filtered_user, filtered_bot

    def _build_channel_rows_v2(self, channel_source: list[ChannelRecord]) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for index, channel in enumerate(channel_source, start=1):
            status_label, status_class = self._channel_status_badge(channel.status)
            worker = next((item for item in self.workers if item.id == channel.worker_id), None)
            manager_name = self._resolve_channel_manager_name(channel)
            rows.append(
                {
                    "index": index,
                    "id": channel.id,
                    "avatar_url": channel.avatar_url or "/static/admin-themes/assets/img/avatar/avatar-1.png",
                    "name": channel.name,
                    "channel_id": channel.channel_id,
                    "channel_link": self._channel_link(channel),
                    "gmail": channel.oauth_email or "-",
                    "manager_name": manager_name,
                    "users": self._channel_users(channel),
                    "worker_id": channel.worker_id,
                    "worker_name": self._resolve_channel_worker_display_name(channel),
                    "group": (worker.group if worker and worker.group else manager_name),
                    "status_label": status_label,
                    "status_class": status_class,
                    "created_at": self._format_full_datetime(self._channel_connected_at(channel)),
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
        viewer_role: str = "admin",
        viewer_id: str | None = None,
        notice: str | None = None,
        notice_level: str = "success",
        workspace_mode: str = "upload",
    ) -> dict[str, Any]:
        channels, filtered_user, filtered_bot = self._filtered_channels_v2(
            manager_ids=manager_ids,
            user_id=user_id,
            bot_id=bot_id,
        )
        context = self._admin_shell_context(
            page_title="Danh sách Kênh",
            active_page="channels",
            viewer_role=viewer_role,
            viewer_id=viewer_id,
            manager_ids=manager_ids,
            notice=notice,
            notice_level=notice_level,
            workspace_mode=workspace_mode,
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
        viewer_role: str = "admin",
        viewer_id: str | None = None,
        notice: str | None = None,
        notice_level: str = "success",
    ) -> dict[str, Any]:
        user = self._find_user(user_id)
        if user.role == "user":
            channel_source = [
                channel
                for channel in self.channels
                if self._resolve_channel_manager_id(channel) == user.manager_id
            ]
        elif user.role == "manager":
            channel_source = [
                channel
                for channel in self.channels
                if self._resolve_channel_manager_id(channel) == user.id
            ]
        else:
            channel_source = list(self.channels)

        granted_channel_ids = {link["channel_id"] for link in self.channel_user_links if link["user_id"] == user.id}
        rows = []
        for row in self._build_channel_rows_v2(channel_source):
            row["is_used"] = row["id"] in granted_channel_ids
            rows.append(row)

        context = self._admin_shell_context(
            page_title=f"Thêm kênh cho ngu?i dùng {user.username}",
            active_page="channels",
            viewer_role=viewer_role,
            viewer_id=viewer_id,
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
        viewer_role: str = "admin",
        viewer_id: str | None = None,
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
            if user.role == "user" and user.manager_id and user.manager_id == self._resolve_channel_manager_id(channel)
        ]

        context = self._admin_shell_context(
            page_title=f"Danh sách ngu?i dùng c?a kênh {channel.name}",
            active_page="channels",
            viewer_role=viewer_role,
            viewer_id=viewer_id,
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
            raise ValueError("Ch? user thu?ng m?i du?c gán vào kênh.")
        if user.manager_id and self._resolve_channel_manager_id(channel) != user.manager_id:
            raise ValueError("User không cùng manager v?i kênh này.")

        self._assert_channel_matches_user_worker(user, channel)

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
        channel.oauth_connected_at = self._now()
        self._save_state()

    def _queue_browser_profile_cleanup(self, *, worker_id: str, profile_key: str | None) -> None:
        cleaned_worker_id = str(worker_id or "").strip()
        cleaned_profile_key = str(profile_key or "").strip()
        if not cleaned_worker_id or not cleaned_profile_key:
            return
        for item in self.browser_profile_cleanup_tasks:
            if (
                str(item.get("worker_id") or "").strip() == cleaned_worker_id
                and str(item.get("profile_key") or "").strip() == cleaned_profile_key
            ):
                return
        self.browser_profile_cleanup_tasks.append(
            {
                "worker_id": cleaned_worker_id,
                "profile_key": cleaned_profile_key,
                "queued_at": self._now(trim=False).isoformat(),
            }
        )

    def _browser_profile_bound_channel(self, profile_key: str | None) -> ChannelRecord | None:
        cleaned_profile_key = str(profile_key or "").strip()
        if not cleaned_profile_key:
            return None
        return next(
            (
                channel
                for channel in self.channels
                if channel.connection_mode == "browser_profile"
                and str(channel.browser_profile_key or "").strip() == cleaned_profile_key
            ),
            None,
        )

    def _queue_browser_profile_cleanup_if_orphan(self, *, worker_id: str, profile_key: str | None) -> None:
        if self._browser_profile_bound_channel(profile_key) is not None:
            return
        self._queue_browser_profile_cleanup(worker_id=worker_id, profile_key=profile_key)

    def _close_orphan_browser_sessions_for_user(self, user_id: str) -> None:
        closed_at = self._now(trim=False)
        changed = False
        for session in self.browser_sessions:
            if session.owner_user_id != user_id:
                continue
            if session.status not in {"launching", "awaiting_confirmation", "confirmed"}:
                continue
            if self._browser_profile_bound_channel(session.profile_key) is not None:
                continue
            session.status = "closed"
            session.expires_at = closed_at
            session.last_error = "Session da dong vi profile tam khong con gan voi kenh nao."
            self._queue_browser_profile_cleanup_if_orphan(
                worker_id=session.target_worker_id,
                profile_key=session.profile_key,
            )
            changed = True
        if changed:
            self._save_state()

    def _close_browser_sessions_for_profile(self, profile_key: str | None) -> None:
        cleaned_profile_key = str(profile_key or "").strip()
        if not cleaned_profile_key:
            return
        closed_at = self._now(trim=False)
        for session in self.browser_sessions:
            if str(session.profile_key or "").strip() != cleaned_profile_key:
                continue
            if session.status not in {"launching", "awaiting_confirmation", "confirmed"}:
                continue
            session.status = "closed"
            session.expires_at = closed_at
            session.last_error = "Session da dong vi kenh/profile da bi xoa."

    def _schedule_channel_browser_profile_cleanup(self, channel: ChannelRecord) -> None:
        if channel.connection_mode != "browser_profile":
            return
        self._close_browser_sessions_for_profile(channel.browser_profile_key)
        self._queue_browser_profile_cleanup(
            worker_id=channel.worker_id,
            profile_key=channel.browser_profile_key,
        )

    def delete_channel(self, channel_id: str) -> None:
        channel = self._find_channel(channel_id)
        linked_user_ids = [
            str(link.get("user_id") or "").strip()
            for link in self.channel_user_links
            if link.get("channel_id") == channel.id
        ]
        self._schedule_channel_browser_profile_cleanup(channel)
        removed_jobs = [job for job in self.jobs if job.channel_id == channel_id]
        for job in removed_jobs:
            self._purge_job_artifacts(job, exclude_job_id=job.id)
        self.channels = [channel for channel in self.channels if channel.id != channel_id]
        self.channel_user_links = [link for link in self.channel_user_links if link["channel_id"] != channel_id]
        self.jobs = [job for job in self.jobs if job.channel_id != channel_id]
        for user_id in linked_user_ids:
            if user_id:
                self._close_orphan_browser_sessions_for_user(user_id)
        self._save_state()

    def delete_user_connected_channel(self, channel_id: str, *, user_id: str) -> None:
        channel = self._find_channel(channel_id)
        has_access = self._user_has_channel_access(user_id, channel.id)
        if not has_access:
            raise ValueError("B?n không có quy?n xóa kênh này.")
        self.delete_channel(channel.id)

    def get_channel_export_rows(self) -> list[dict[str, Any]]:
        return self.get_channel_export_rows_filtered()

    def get_channel_export_rows_filtered(self, *, manager_ids: list[str] | None = None) -> list[dict[str, Any]]:
        rows = []
        selected_manager_ids = set(self._selected_manager_ids(manager_ids))
        channel_source = list(self.channels)
        if selected_manager_ids:
            channel_source = [
                channel
                for channel in channel_source
                if self._resolve_channel_manager_id(channel) in selected_manager_ids
            ]
        for channel in channel_source:
            rows.append(
                {
                    "Avatar": channel.avatar_url or "",
                    "ChannelName": channel.name,
                    "ChannelYTId": channel.channel_id,
                    "ChannelLink": self._channel_link(channel),
                    "BotName": self._resolve_channel_worker_display_name(channel),
                    "ChannelGmail": channel.oauth_email or "",
                    "Group": next((worker.group for worker in self.workers if worker.id == channel.worker_id), channel.manager_name),
                    "CreatedTime": self._format_full_datetime(self._channel_connected_at(channel)),
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
        viewer_role: str = "admin",
        viewer_id: str | None = None,
        notice: str | None = None,
        notice_level: str = "success",
        workspace_mode: str = "upload",
    ) -> dict[str, Any]:
        context = self._admin_shell_context(
            page_title="Danh sách Render",
            active_page="renders",
            viewer_role=viewer_role,
            viewer_id=viewer_id,
            manager_ids=manager_ids,
            notice=notice,
            notice_level=notice_level,
            workspace_mode=workspace_mode,
        )

        selected_manager_ids = set(self._selected_manager_ids(manager_ids))
        job_source = list(self.jobs)
        if selected_manager_ids:
            job_source = [
                job for job in job_source
                if self._resolve_job_manager_id(job) in selected_manager_ids
            ]

        filtered_channel: dict[str, Any] | None = None
        if channel_id:
            channel = self._find_channel(channel_id)
            filtered_channel = {"id": channel.id, "name": channel.name, "channel_id": channel.channel_id}
            job_source = [job for job in job_source if job.channel_id == channel.id]

        render_rows: list[dict[str, Any]] = []
        for index, job in enumerate(sorted(job_source, key=lambda item: item.created_at, reverse=True), start=1):
            status_label, status_class = self._render_status_badge(job)
            primary_asset = next((asset for asset in job.assets if asset.url or asset.file_name), None)
            channel = self._find_channel_optional(job.channel_id)
            manager_name = self._resolve_job_manager_name(job)
            render_rows.append(
                {
                    "index": index,
                    "id": job.id,
                    "manager_name": manager_name,
                    "username": self._job_username(job),
                    "created_at": self._format_full_datetime(job.created_at),
                    "title": job.title,
                    "worker_name": self._resolve_job_worker_display_name(job),
                    "group": manager_name,
                    "avatar_url": job.channel_avatar_url or "/static/admin-themes/assets/img/avatar/avatar-1.png",
                    "channel_name": job.channel_name,
                    "channel_id": channel.channel_id if channel else job.channel_id,
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
        viewer_role: str = "admin",
        viewer_id: str | None = None,
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
            page_title="ThÃ´ng tin Render",
            active_page="renders",
            viewer_role=viewer_role,
            viewer_id=viewer_id,
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
                message="ÄÃ£ sáºµn sÃ ng cho flow Google OAuth. Cáº§n bá» sung GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET vÃ  GOOGLE_REDIRECT_URI Äá» báº­t káº¿t ná»i tháº­t.",
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
            message="ÄÃ£ táº¡o URL káº¿t ná»i Google OAuth.",
        )

    def complete_google_oauth(self, *, user_id: str, code: str, base_url: str | None = None) -> dict[str, str]:
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
        now = self._now()

        if not channel_id:
            raise ValueError("Google tra ve du lieu channel khong hop le.")

        current_user = self._require_workspace_user(user_id)
        worker = self._pick_worker_for_user(current_user)
        existing_channel = next((channel for channel in self.channels if channel.channel_id == channel_id), None)
        existing_refresh_token = existing_channel.oauth_refresh_token if existing_channel else None
        if not refresh_token and not existing_refresh_token:
            raise ValueError("Google khong tra ve refresh_token. Hay xoa quyen app cu va ket noi lai.")

        if existing_channel:
            channel = existing_channel
        else:
            channel = ChannelRecord(
                id=f"channel-{uuid4().hex[:8]}",
                name=channel_name,
                channel_id=channel_id,
                avatar_url=avatar_url,
                worker_id=worker.id,
                worker_name=worker.id,
                manager_name=current_user.manager_name or worker.manager_name,
                status="connected",
            )
            self.channels.append(channel)

        previous_browser_profile_key = channel.browser_profile_key
        previous_connection_mode = channel.connection_mode
        channel.name = channel_name
        channel.avatar_url = avatar_url or channel.avatar_url
        channel.status = "connected"
        channel.worker_id = worker.id
        channel.worker_name = worker.id
        channel.manager_name = current_user.manager_name or worker.manager_name
        channel.oauth_email = oauth_email or channel.oauth_email
        channel.oauth_connected_at = now
        channel.oauth_google_subject = oauth_google_subject or channel.oauth_google_subject
        channel.oauth_refresh_token = refresh_token or existing_refresh_token
        channel.oauth_scope = scope or channel.oauth_scope
        channel.oauth_token_type = token_type or channel.oauth_token_type
        channel.connection_mode = "oauth"
        channel.browser_profile_key = None
        channel.browser_profile_path = None
        channel.browser_connected_at = None
        if previous_connection_mode == "browser_profile" and previous_browser_profile_key:
            self._queue_browser_profile_cleanup(
                worker_id=worker.id,
                profile_key=previous_browser_profile_key,
            )

        self._ensure_channel_user_link(channel_id=channel.id, user_id=current_user.id)
        self._save_state()
        return {
            "channel_name": channel.name,
            "youtube_channel_id": channel.channel_id,
            "channel_record_id": channel.id,
        }

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

    def _absolute_preview_path(self, relative_path: str) -> Path:
        return self.preview_dir / relative_path

    @staticmethod
    def _preview_route(job_id: str) -> str:
        return f"/api/user/jobs/{job_id}/preview-thumbnail"

    def _delete_job_preview_file(self, job: RenderJobRecord) -> bool:
        relative_path = str(job.thumbnail_path or "").strip()
        if not relative_path:
            return False
        preview_path = self._absolute_preview_path(relative_path)
        if preview_path.exists():
            preview_path.unlink(missing_ok=True)
        job.thumbnail_path = None
        job.thumbnail_url = None
        return True

    def _find_upload_session(self, session_id: str) -> UploadSessionRecord:
        for session in self.upload_sessions:
            if session.session_id == session_id:
                return session
        raise KeyError(session_id)

    def _find_user_upload_session(self, user_id: str, session_id: str) -> UploadSessionRecord:
        session = self._find_upload_session(session_id)
        if session.owner_user_id != user_id:
            raise KeyError(session_id)
        return session

    def _cleanup_stale_uploads(self) -> None:
        now = self._now(trim=False)
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

    def create_upload_session(self, user_id: str, payload: UploadSessionCreateRequest) -> UploadSessionResponse:
        self._require_workspace_user(user_id)
        self._cleanup_stale_uploads()
        capabilities = self.get_upload_capabilities()
        if payload.size_bytes <= 0:
            raise ValueError("KÃ­ch thÆ°á»c file pháº£i lá»n hÆ¡n 0.")
        if payload.size_bytes > capabilities.max_local_upload_bytes:
            raise ValueError("File vÆ°á»£t quÃ¡ giá»i háº¡n local upload hiá»n táº¡i.")

        extension = Path(payload.file_name).suffix.lower()
        if extension not in capabilities.allowed_extensions:
            raise ValueError(f"Äá»nh dáº¡ng file khÃ´ng há» trá»£: {extension or '(khÃ´ng cÃ³ extension)'}")

        sanitized_name = self._sanitize_filename(payload.file_name)
        now = self._now(trim=False)
        session = UploadSessionRecord(
            session_id=f"upl-{uuid4().hex}",
            owner_user_id=user_id,
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

    def get_upload_session(self, user_id: str, session_id: str) -> UploadSessionResponse:
        self._require_workspace_user(user_id)
        self._cleanup_stale_uploads()
        session = self._find_user_upload_session(user_id, session_id)
        return self._upload_response(session)

    def append_upload_chunk(self, user_id: str, session_id: str, offset: int, chunk: bytes) -> UploadSessionResponse:
        self._require_workspace_user(user_id)
        session = self._find_user_upload_session(user_id, session_id)
        if session.status not in {"active", "completed"}:
            raise ValueError("Upload session khÃ´ng cÃ²n hoáº¡t Äá»ng.")
        if session.status == "completed":
            return self._upload_response(session)
        if offset < 0:
            raise ValueError("Offset khÃ´ng há»£p lá».")

        temp_path = self._absolute_upload_path(session.temp_path)
        temp_path.parent.mkdir(parents=True, exist_ok=True)
        current_size = temp_path.stat().st_size if temp_path.exists() else 0
        if offset != current_size:
            raise ValueError(f"Offset khÃ´ng khá»p. Server Äang cÃ³ {current_size} bytes.")
        if offset + len(chunk) > session.size_bytes:
            raise ValueError("Chunk vÆ°á»£t quÃ¡ kÃ­ch thÆ°á»c ÄÃ£ khai bÃ¡o.")

        with temp_path.open("ab") as file_obj:
            file_obj.write(chunk)

        session.received_bytes = temp_path.stat().st_size
        session.updated_at = self._now(trim=False)
        session.expires_at = session.updated_at + timedelta(hours=24)
        if session.received_bytes > session.size_bytes:
            raise ValueError("Upload vÆ°á»£t quÃ¡ kÃ­ch thÆ°á»c ÄÃ£ khai bÃ¡o.")

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

    def consume_uploaded_asset(self, user_id: str, asset_id: str | None) -> str | None:
        if not asset_id:
            return None
        session = next(
            (
                item
                for item in self.upload_sessions
                if item.asset_id == asset_id and item.owner_user_id == user_id
            ),
            None,
        )
        if session is None or session.status != "completed" or not session.stored_file_name:
            raise ValueError("Uploaded asset khÃ´ng há»£p lá» hoáº·c chÆ°a hoÃ n táº¥t.")
        return session.stored_file_name

    def _find_job_asset(self, job: RenderJobRecord, slot: str) -> JobAsset:
        for asset in job.assets:
            if asset.slot == slot:
                return asset
        raise KeyError(slot)

    def get_worker_job_asset_file(
        self,
        *,
        job_id: str,
        slot: str,
        worker_id: str,
        shared_secret: str,
    ) -> dict[str, Any]:
        self._authenticate_worker(worker_id, shared_secret)
        job = self._find_claimed_job(job_id, worker_id)
        self._ensure_worker_job_can_continue(job)
        asset = self._find_job_asset(job, slot)
        if asset.source_mode != "local" or not asset.file_name:
            raise ValueError("Asset nÃ y khÃ´ng pháº£i local upload.")

        file_path = self.upload_asset_dir / asset.file_name
        if not file_path.exists():
            raise FileNotFoundError(asset.file_name)

        return {
            "path": file_path,
            "file_name": asset.file_name,
        }

    def get_user_job_asset_file(self, *, user_id: str, job_id: str, slot: str) -> dict[str, Any]:
        self._require_workspace_user(user_id)
        job = self._find_user_visible_job(user_id, job_id)
        asset = self._find_job_asset(job, slot)
        if asset.source_mode != "local" or not asset.file_name:
            raise ValueError("Asset nay khong phai local upload.")

        file_path = self.upload_asset_dir / asset.file_name
        if not self._path_has_content(file_path):
            raise FileNotFoundError(asset.file_name)

        content_type, _ = mimetypes.guess_type(str(file_path))
        return {
            "path": file_path,
            "file_name": asset.file_name,
            "content_type": content_type or "application/octet-stream",
        }

    def get_user_job_preview_thumbnail_file(self, *, user_id: str, job_id: str) -> dict[str, Any]:
        self._require_workspace_user(user_id)
        job = self._find_user_visible_job(user_id, job_id)
        relative_path = str(job.thumbnail_path or "").strip()
        if not relative_path:
            raise FileNotFoundError(job_id)

        file_path = self._absolute_preview_path(relative_path)
        if not self._path_has_content(file_path):
            raise FileNotFoundError(relative_path)

        content_type, _ = mimetypes.guess_type(str(file_path))
        return {
            "path": file_path,
            "file_name": file_path.name,
            "content_type": content_type or "image/jpeg",
        }

    def store_worker_job_preview_thumbnail(
        self,
        *,
        job_id: str,
        worker_id: str,
        shared_secret: str,
        file_name: str,
        content_type: str | None,
        payload: bytes,
    ) -> RenderJobRecord:
        self._authenticate_worker(worker_id, shared_secret)
        job = self._find_claimed_job(job_id, worker_id)
        self._ensure_worker_job_can_continue(job)
        if not payload:
            raise ValueError("Preview payload rong.")

        suffix = Path(file_name or "preview.jpg").suffix.lower()
        if suffix not in {".jpg", ".jpeg", ".png", ".webp"}:
            suffix = ".jpg"

        self._delete_job_preview_file(job)
        relative_path = f"{job.id}{suffix}"
        preview_path = self._absolute_preview_path(relative_path)
        preview_path.parent.mkdir(parents=True, exist_ok=True)
        preview_path.write_bytes(payload)
        job.thumbnail_path = relative_path
        job.thumbnail_url = self._preview_route(job.id)
        self._save_state()
        return deepcopy(job)

    def get_worker_job_youtube_target(
        self,
        *,
        job_id: str,
        worker_id: str,
        shared_secret: str,
    ) -> WorkerYouTubeUploadTarget:
        self._authenticate_worker(worker_id, shared_secret)
        job = self._find_claimed_job(job_id, worker_id)
        self._ensure_worker_job_can_continue(job)
        channel = self._find_channel(job.channel_id)
        self._refresh_browser_channel_metadata(channel)
        if channel.connection_mode != "browser_profile":
            raise ValueError(
                "Luong OAuth/API upload da duoc tat tren nhanh hien tai. Hay reconnect kenh bang Ubuntu Browser truoc khi upload."
            )
        return WorkerYouTubeUploadTarget(
            job_id=job.id,
            channel_id=channel.channel_id,
            channel_name=channel.name,
            title=job.title,
            description=job.description,
            connection_mode="browser_profile",
            browser_profile_key=channel.browser_profile_key,
            browser_profile_path=channel.browser_profile_path,
        )

    def abort_upload_session(self, user_id: str, session_id: str) -> None:
        self._require_workspace_user(user_id)
        session = self._find_user_upload_session(user_id, session_id)
        temp_path = self._absolute_upload_path(session.temp_path)
        if temp_path.exists():
            temp_path.unlink(missing_ok=True)
        self.upload_sessions = [item for item in self.upload_sessions if item.session_id != session_id]
        self._save_state()
        return None


store = AppStore()
