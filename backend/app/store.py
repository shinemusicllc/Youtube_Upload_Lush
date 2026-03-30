from __future__ import annotations

import hashlib
import hmac
from copy import deepcopy
from datetime import datetime, timedelta, timezone, tzinfo
import json
import mimetypes
import os
import re
import secrets
from pathlib import Path
import shutil
import sqlite3
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.request import Request, urlopen
from uuid import uuid4
from zoneinfo import ZoneInfo

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
    WorkerYouTubeUploadTarget,
)

load_dotenv(Path(__file__).resolve().parents[2] / ".env")


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
                name=self.KNOWN_WORKER_DISPLAY_NAMES["worker-02"],
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
        self._ensure_auth_tables()
        self._load_or_seed_state()
        normalized_worker_names = self._normalize_known_worker_names()
        migrated_credentials = self._migrate_legacy_user_meta_passwords()
        self._bootstrap_auth_tables_from_memory_if_empty()
        self._load_auth_state_from_tables()
        if migrated_credentials or normalized_worker_names:
            self._save_state()

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
                    updated_at TEXT,
                    FOREIGN KEY(user_id) REFERENCES auth_users(id) ON DELETE CASCADE
                )
                """
            )
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
            raise ValueError("Password không được để trống.")
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
        meta["password_hash"] = self._hash_password(password)
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
                meta.pop("password", None)
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
                    raise ValueError(f"User {user.username} chưa có password_hash.")
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
                    INSERT INTO auth_credentials (user_id, password_hash, password_algo, updated_at)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        user.id,
                        password_hash,
                        meta.get("password_algo") or "pbkdf2_sha256",
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
                    credentials.password_algo
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
            raise ValueError("Tên đăng nhập và mật khẩu là bắt buộc.")

        user = self._find_user_by_username(normalized_username)
        if not user:
            raise ValueError("Thông tin đăng nhập không hợp lệ.")
        if user.role not in {"admin", "manager"}:
            raise ValueError("Tài khoản này không được phép vào trang quản trị.")

        if not self._verify_user_password(user.id, normalized_password):
            raise ValueError("Thông tin đăng nhập không hợp lệ.")

        return self._build_session_payload(user)

    def authenticate_app_user(self, username: str, password: str) -> dict[str, Any]:
        normalized_username = username.strip().lower()
        normalized_password = password.strip()
        if not normalized_username or not normalized_password:
            raise ValueError("Tên đăng nhập và mật khẩu là bắt buộc.")

        user = self._find_user_by_username(normalized_username)
        if not user:
            raise ValueError("Thông tin đăng nhập không hợp lệ.")
        if user.role != "user":
            raise ValueError("Tài khoản này không được phép vào workspace user.")
        if not self._verify_user_password(user.id, normalized_password):
            raise ValueError("Thông tin đăng nhập không hợp lệ.")

        return self._build_session_payload(user)

    def authenticate_login_user(self, username: str, password: str) -> dict[str, Any]:
        normalized_username = username.strip().lower()
        normalized_password = password.strip()
        if not normalized_username or not normalized_password:
            raise ValueError("Tên đăng nhập và mật khẩu là bắt buộc.")

        user = self._find_user_by_username(normalized_username)
        if not user:
            raise ValueError("Thông tin đăng nhập không hợp lệ.")
        if not self._verify_user_password(user.id, normalized_password):
            raise ValueError("Thông tin đăng nhập không hợp lệ.")
        return self._build_session_payload(user)

    def assert_admin_session_user(self, user_id: str, role: str) -> None:
        user = self._find_user(user_id)
        if user.role not in {"admin", "manager"}:
            raise ValueError("Tài khoản không được phép vào trang quản trị.")
        if user.role != role:
            raise ValueError("Role session khong con hop le.")

    def assert_app_session_user(self, user_id: str, role: str) -> None:
        user = self._find_user(user_id)
        if user.role != "user":
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

    @staticmethod
    def _is_youtube_watch_url(value: str | None) -> bool:
        if not value:
            return False
        normalized = value.strip().lower()
        return normalized.startswith("https://www.youtube.com/watch") or normalized.startswith("https://youtube.com/watch")

    def _job_user_status_view(self, job: RenderJobRecord) -> dict[str, Any]:
        if job.status == "completed":
            if self._is_youtube_watch_url(job.output_url):
                return {
                    "label": "Đã upload YouTube",
                    "class": "inline-flex items-center rounded-full border border-emerald-200 bg-emerald-50 px-2.5 py-1 text-[10px] font-semibold text-emerald-700",
                    "progress_text_class": "text-emerald-600",
                    "progress_bar_class": "bg-emerald-500",
                    "render_at": self._format_datetime(job.upload_started_at or job.completed_at),
                    "upload_at": self._format_datetime(job.completed_at),
                    "youtube_watch_url": job.output_url,
                }
            return {
                "label": "Render hoàn tất",
                "class": "inline-flex items-center rounded-full border border-indigo-200 bg-indigo-50 px-2.5 py-1 text-[10px] font-semibold text-indigo-700",
                "progress_text_class": "text-indigo-600",
                "progress_bar_class": "bg-indigo-500",
                "render_at": self._format_datetime(job.completed_at),
                "upload_at": "-",
                "youtube_watch_url": None,
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
            "youtube_watch_url": None,
        }

    @staticmethod
    def _job_user_progress_view(job: RenderJobRecord) -> dict[str, int | str]:
        download_progress = 0
        render_progress = 0
        upload_progress = 0

        if job.status == "downloading":
            download_progress = min(max(job.progress, 0), 100)
        elif job.status == "rendering":
            download_progress = 100
            render_progress = job.progress
        elif job.status in {"uploading", "completed"}:
            download_progress = 100
            render_progress = 100
        elif job.status in {"error", "cancelled"}:
            if job.upload_started_at or AppStore._is_youtube_watch_url(job.output_url):
                download_progress = 100
                render_progress = 100
                upload_progress = min(max(job.progress, 0), 100)
            else:
                download_progress = 100 if job.started_at or job.claimed_at or job.completed_at else min(max(job.progress, 0), 100)
                render_progress = min(max(job.progress, 0), 100)

        if job.status == "uploading":
            upload_progress = job.progress
        elif job.status == "completed" and AppStore._is_youtube_watch_url(job.output_url):
            upload_progress = 100

        return {
            "mode": "download" if job.status == "downloading" else "pipeline",
            "download": min(max(download_progress, 0), 100),
            "render": min(max(render_progress, 0), 100),
            "upload": min(max(upload_progress, 0), 100),
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
            raise ValueError("Worker shared secret không hợp lệ.")
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
        max_threads = max(1, int(worker.threads or worker.capacity or 1))
        return {
            "running_threads": running_threads,
            "max_threads": max_threads,
            "thread_text": f"{running_threads}/{max_threads}",
        }

    def _sync_worker_runtime_status(self, worker: WorkerRecord) -> None:
        running_threads = self._count_worker_running_jobs(worker)
        worker.status = "busy" if running_threads > 0 else "online"

    def _refresh_worker_job_leases(self, worker_id: str, now: datetime | None = None) -> None:
        lease_base = now or self._now()
        active_statuses = self._worker_active_job_statuses()
        for job in self.jobs:
            if job.claimed_by_worker_id == worker_id and job.status in active_statuses:
                job.lease_expires_at = lease_base + timedelta(minutes=5)

    def register_worker(self, payload: WorkerRegisterPayload) -> WorkerControlResponse:
        if payload.shared_secret != self.get_worker_shared_secret():
            raise ValueError("Worker shared secret không hợp lệ.")

        now = self._now()
        worker_display_name = self._default_worker_display_name(payload.worker_id, payload.name)
        existing = next((worker for worker in self.workers if worker.id == payload.worker_id), None)
        manager = next((user for user in self.users if user.username == payload.manager_name and user.role == "manager"), None)
        if existing is None:
            worker = WorkerRecord(
                id=payload.worker_id,
                name=worker_display_name,
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
            existing.name = worker_display_name
            existing.manager_id = manager.id if manager else existing.manager_id
            existing.manager_name = payload.manager_name
            existing.group = payload.group or payload.manager_name
            existing.capacity = max(int(existing.capacity or 1), int(payload.capacity or 1))
            existing.threads = max(1, int(existing.threads or payload.threads or 1))
            existing.disk_total_gb = payload.disk_total_gb or existing.disk_total_gb
            existing.status = "online"
            existing.last_seen_at = now
            worker = existing

        self._save_state()
        return WorkerControlResponse(ok=True, worker=deepcopy(worker))

    def heartbeat_worker(self, payload: WorkerHeartbeatPayload) -> WorkerControlResponse:
        worker = self._authenticate_worker(payload.worker_id, payload.shared_secret)
        now = self._now()
        worker.load_percent = payload.load_percent
        worker.bandwidth_kbps = payload.bandwidth_kbps
        worker.disk_used_gb = payload.disk_used_gb
        worker.disk_total_gb = payload.disk_total_gb or worker.disk_total_gb
        worker.threads = payload.threads
        worker.last_seen_at = now
        if payload.active_job_ids is None:
            self._refresh_worker_job_leases(worker.id, now)
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
        worker = self._authenticate_worker(worker_id, shared_secret)
        now = self._now()
        max_threads = max(1, int(worker.threads or worker.capacity or 1))
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
        candidates.sort(key=lambda item: (item.queue_order or 10_000, item.created_at))

        if not candidates:
            self._sync_worker_runtime_status(worker)
            self._save_state()
            return deepcopy(worker), None

        job = candidates[0]
        job.status = "queueing"
        job.claimed_by_worker_id = worker_id
        job.claimed_at = now
        self._refresh_worker_job_leases(worker_id, now)
        job.started_at = job.started_at or now
        self._sync_worker_runtime_status(worker)
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
        worker = self._authenticate_worker(worker_id, shared_secret)
        job = self._find_claimed_job(job_id, worker_id)
        self._ensure_worker_job_can_continue(job)
        now = self._now()

        job.claimed_by_worker_id = worker_id
        job.claimed_at = job.claimed_at or now
        self._refresh_worker_job_leases(worker_id, now)
        job.started_at = job.started_at or now
        job.status = status  # type: ignore[assignment]
        job.progress = max(0, min(100, progress))
        if message:
            job.error_message = message
        if status == "downloading" and job.download_started_at is None:
            job.download_started_at = now
        if status == "uploading" and job.upload_started_at is None:
            job.upload_started_at = now
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
        worker = self._authenticate_worker(worker_id, shared_secret)
        job = self._find_claimed_job(job_id, worker_id)
        self._ensure_worker_job_can_continue(job)
        now = self._now()

        job.status = "completed"
        job.progress = 100
        job.completed_at = now
        job.can_cancel = False
        job.output_url = output_url
        job.error_message = message
        job.lease_expires_at = None
        self._sync_worker_runtime_status(worker)
        if self._is_youtube_watch_url(output_url):
            self._cleanup_uploaded_assets_for_job(job, exclude_job_id=job.id)
        self._refresh_queue_positions()
        self._save_state()
        return deepcopy(job)

    def fail_worker_job(self, *, job_id: str, worker_id: str, shared_secret: str, message: str) -> RenderJobRecord:
        worker = self._authenticate_worker(worker_id, shared_secret)
        job = self._find_claimed_job(job_id, worker_id)
        now = self._now()

        job.status = "error"
        job.completed_at = now
        job.can_cancel = False
        job.error_message = message
        job.lease_expires_at = None
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
        if user.role != "user":
            raise ValueError("Tai khoan khong duoc phep vao workspace user.")
        return user

    def _user_channel_ids(self, user_id: str) -> set[str]:
        return {link["channel_id"] for link in self.channel_user_links if link["user_id"] == user_id}

    def _user_has_channel_access(self, user_id: str, channel_id: str) -> bool:
        return channel_id in self._user_channel_ids(user_id)

    def _user_jobs_for_workspace(self, user_id: str) -> list[RenderJobRecord]:
        channel_ids = self._user_channel_ids(user_id)
        jobs = [job for job in self.jobs if job.channel_id in channel_ids]
        return sorted(deepcopy(jobs), key=lambda item: item.created_at, reverse=True)

    def _find_user_visible_job(self, user_id: str, job_id: str) -> RenderJobRecord:
        job = self._find_job(job_id)
        if not self._user_has_channel_access(user_id, job.channel_id):
            raise KeyError(job_id)
        return job

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
                "password_hash": "",
                "password_algo": "pbkdf2_sha256",
                "telegram": "",
                "updated_by": "system",
                "updated_at": None,
                "created_at": self._now(),
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
        selected_manager_ids = list(manager_ids or [])
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
            return len([worker for worker in self.workers if worker.manager_id == user.id])
        if user.role == "admin":
            return len(self.workers)
        return len([link for link in self.user_worker_links if link["user_id"] == user.id])

    def _user_channel_count(self, user: UserSummary) -> int:
        if user.role == "manager":
            return len([channel for channel in self.channels if self._resolve_channel_manager_id(channel) == user.id])
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

    @staticmethod
    def _normalize_text(value: str | None) -> str:
        return re.sub(r"\s+", " ", str(value or "").strip()).casefold()

    @classmethod
    def _parse_google_datetime(cls, value: str | None) -> datetime | None:
        cleaned = str(value or "").strip()
        if not cleaned:
            return None
        try:
            parsed = datetime.fromisoformat(cleaned.replace("Z", "+00:00"))
        except ValueError:
            return None
        return cls._normalize_datetime(parsed)

    def _exchange_channel_refresh_token(self, channel: ChannelRecord) -> str:
        refresh_token = str(channel.oauth_refresh_token or "").strip()
        client_id = str(os.getenv("GOOGLE_CLIENT_ID", "")).strip()
        client_secret = str(os.getenv("GOOGLE_CLIENT_SECRET", "")).strip()
        if not refresh_token:
            raise ValueError("Kênh chưa có refresh token OAuth thật.")
        if not client_id or not client_secret:
            raise ValueError("Thiếu GOOGLE_CLIENT_ID hoặc GOOGLE_CLIENT_SECRET trên control plane.")
        token_payload = self._post_form_json(
            "https://oauth2.googleapis.com/token",
            {
                "client_id": client_id,
                "client_secret": client_secret,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            },
        )
        access_token = str(token_payload.get("access_token") or "").strip()
        if not access_token:
            raise ValueError("Google không trả về access_token khi refresh token.")
        return access_token

    def _recover_uploaded_watch_url(self, job: RenderJobRecord) -> str | None:
        channel = self._find_channel_optional(job.channel_id)
        if not channel:
            return None
        try:
            access_token = self._exchange_channel_refresh_token(channel)
            payload = self._get_json(
                "https://www.googleapis.com/youtube/v3/search?"
                + urlencode(
                    {
                        "part": "id,snippet",
                        "forMine": "true",
                        "type": "video",
                        "order": "date",
                        "maxResults": 10,
                        "q": job.title,
                    }
                ),
                access_token,
            )
        except ValueError:
            return None

        target_title = self._normalize_text(job.title)
        expected_start = job.upload_started_at or job.completed_at or job.created_at
        best_match: tuple[int, datetime, str] | None = None
        for item in payload.get("items") or []:
            snippet = item.get("snippet") or {}
            video_id = str((item.get("id") or {}).get("videoId") or "").strip()
            published_at = self._parse_google_datetime(snippet.get("publishedAt"))
            candidate_title = self._normalize_text(snippet.get("title"))
            if not video_id or not published_at or candidate_title != target_title:
                continue
            delta_seconds = abs(int((published_at - expected_start).total_seconds())) if expected_start else 0
            candidate = (delta_seconds, published_at, f"https://www.youtube.com/watch?v={video_id}")
            if best_match is None or candidate < best_match:
                best_match = candidate
        return best_match[2] if best_match else None

    def _release_worker_job_claim(self, job: RenderJobRecord, *, reset_status: str = "pending", message: str | None = None) -> None:
        job.status = reset_status  # type: ignore[assignment]
        job.progress = 0 if reset_status == "pending" else job.progress
        job.can_cancel = reset_status not in {"completed", "error"}
        job.claimed_by_worker_id = None
        job.claimed_at = None
        job.lease_expires_at = None
        job.download_started_at = None if reset_status == "pending" else job.download_started_at
        job.upload_started_at = None if reset_status == "pending" else job.upload_started_at
        if message:
            job.error_message = message

    def _complete_recovered_job(self, job: RenderJobRecord, *, output_url: str, completed_at: datetime | None = None) -> None:
        finished_at = completed_at or self._now()
        job.status = "completed"
        job.progress = 100
        job.completed_at = finished_at
        job.can_cancel = False
        job.output_url = output_url
        job.error_message = None
        job.lease_expires_at = None
        if self._is_youtube_watch_url(output_url):
            self._cleanup_uploaded_assets_for_job(job, exclude_job_id=job.id)

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
                job.lease_expires_at = now + timedelta(minutes=5)
                continue
            if job.status == "uploading":
                recovered_watch_url = self._recover_uploaded_watch_url(job)
                if recovered_watch_url:
                    self._complete_recovered_job(job, output_url=recovered_watch_url)
                    continue
                job.status = "error"
                job.completed_at = now
                job.can_cancel = False
                job.lease_expires_at = None
                job.error_message = "Worker mất tracking ở pha upload; cần kiểm tra lại YouTube hoặc tạo lại job."
                continue
            self._release_worker_job_claim(
                job,
                reset_status="pending",
                message="Job được đưa lại hàng chờ vì worker không còn báo đang xử lý.",
            )
        self._refresh_queue_positions()

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
        user_id: str,
        notice: str | None = None,
        notice_level: str = "success",
    ) -> dict[str, Any]:
        bootstrap = self.get_user_bootstrap(user_id)
        jobs_response = self.get_user_jobs(user_id)
        now = self._now()

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
                    "avatar_url": channel.avatar_url,
                    "avatar_class": "bg-emerald-800 text-white",
                    "is_active": False,
                    "is_placeholder": False,
                }
            )

        connected_channels: list[dict[str, Any]] = []
        for channel in bootstrap.channels:
            worker_label = self._resolve_channel_worker_display_name(channel)
            connected_channels.append(
                {
                    "id": channel.id,
                    "title": channel.name,
                    "channel_id": channel.channel_id,
                    "worker_label": worker_label,
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
                    "meta": f"{job.source_label} • render {self._format_render_duration(job.time_render_string)} • ",
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
                    "status_class": status_view["class"],
                    "progress_text_class": status_view["progress_text_class"],
                    "progress_bar_class": status_view["progress_bar_class"],
                    "youtube_watch_url": status_view["youtube_watch_url"],
                    "icon": "hard-drive-download" if is_drive else None,
                    "icon_class": "text-sky-600",
                    "preview_kind": preview["kind"] if preview else None,
                    "preview_url": preview["url"] if preview else None,
                    "preview_text": (job.source_file_name or "Preview")[:16],
                    "can_cancel": job.can_cancel,
                }
            )

        return {
            "page_title": "Upload Youtube",
            "app_name": "Upload Youtube",
            "workspace_label": "User workspace",
            "user_name": bootstrap.user.display_name,
            "user_role": bootstrap.user.manager_name or bootstrap.user.role,
            "logout_path": "/logout",
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

    def get_user_bootstrap(self, user_id: str) -> UserBootstrapResponse:
        user = deepcopy(self._require_workspace_user(user_id))
        assigned_channel_ids = self._user_channel_ids(user.id)
        channels = deepcopy([channel for channel in self.channels if channel.id in assigned_channel_ids])
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
            "render_tabs": dashboard["render_tabs"],
            "render_jobs": dashboard["render_jobs"],
            "render_summary": dashboard["render_summary"],
        }

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
        self._require_workspace_user(user_id)
        channel = self._find_channel(payload.channel_id)
        if not self._user_has_channel_access(user_id, channel.id):
            raise ValueError("Ban khong co quyen tao job tren kenh nay.")
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

    @staticmethod
    def _credential_status_label(meta: dict[str, Any]) -> str:
        password_hash = str(meta.get("password_hash") or "").strip()
        if password_hash:
            return "PBKDF2 hash"
        if str(meta.get("password") or "").strip():
            return "Legacy plaintext"
        return "Chua cau hinh"

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
                    "credential_status": self._credential_status_label(meta),
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
                    "worker_name": self._resolve_worker_display_name(worker.id),
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
                "worker_candidates": [{"id": worker.id, "name": self._resolve_worker_display_name(worker.id)} for worker in self.workers],
            }
        )
        return context

    def _build_bot_rows(self, manager_ids: list[str] | None = None) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for index, worker in enumerate(self._filtered_workers(manager_ids), start=1):
            status_label, status_class = self._worker_status_badge(worker.status)
            thread_summary = self._worker_thread_summary(worker)
            rows.append(
                {
                    "index": index,
                    "id": worker.id,
                    "bot_id": worker.id,
                    "manager_id": worker.manager_id or "",
                    "manager_name": worker.manager_name,
                    "name": self._resolve_worker_display_name(worker.id),
                    "raw_name": self._resolve_worker_display_name(worker.id),
                    "group": worker.group or worker.manager_name,
                    "status_label": status_label,
                    "status_class": status_class,
                    "created_at": self._format_full_datetime(worker.last_seen_at),
                    "total_channels": len([channel for channel in self.channels if channel.worker_id == worker.id]),
                    "total_users": len([link for link in self.user_worker_links if link["worker_id"] == worker.id]),
                    "thread_text": thread_summary["thread_text"],
                    "running_threads": thread_summary["running_threads"],
                    "max_threads": thread_summary["max_threads"],
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
                    "bot_id": worker.id,
                    "name": self._resolve_worker_display_name(worker.id),
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
            page_title=f"Danh sách user của {self._resolve_worker_display_name(worker.id)}",
            active_page="workers",
            notice=notice,
            notice_level=notice_level,
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
            "password_hash": self._hash_password(password.strip()),
            "password_algo": "pbkdf2_sha256",
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
            raise ValueError("Tên đăng nhập là bắt buộc.")
        if any(
            user.id != exclude_user_id and user.username.lower() == normalized_username.lower()
            for user in self.users
        ):
            raise ValueError("Tên đăng nhập đã tồn tại.")
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
            raise ValueError("Không thể xóa admin cuối cùng.")
        if user.role == "manager" and any(item.role == "user" and item.manager_name == user.username for item in self.users):
            raise ValueError("Manager này đang quản lý user khác, chưa thể xóa.")

        self.users = [item for item in self.users if item.id != user_id]
        self.user_meta.pop(user_id, None)
        self.user_worker_links = [item for item in self.user_worker_links if item["user_id"] != user_id]
        self.channel_user_links = [item for item in self.channel_user_links if item["user_id"] != user_id]
        for session in [item for item in self.upload_sessions if item.owner_user_id == user_id]:
            self._remove_upload_session_file(session)
        self.upload_sessions = [item for item in self.upload_sessions if item.owner_user_id != user_id]
        self._save_state()

    def reset_admin_user_password(self, user_id: str, password: str, updated_by: str = "admin") -> None:
        if not password.strip():
            raise ValueError("Password mới là bắt buộc.")
        self._find_user(user_id)
        meta = self._user_meta_record(user_id)
        meta["password_hash"] = self._hash_password(password.strip())
        meta["password_algo"] = "pbkdf2_sha256"
        meta.pop("password", None)
        meta["updated_by"] = updated_by
        meta["updated_at"] = self._now()
        self._save_state()

    def update_admin_user(
        self,
        *,
        user_id: str,
        username: str,
        display_name: str,
        telegram: str | None,
        manager_id: str | None,
        actor_role: str = "admin",
        updated_by: str = "admin",
    ) -> UserSummary:
        user = self._find_user(user_id)
        if not display_name.strip():
            raise ValueError("DisplayName là bắt buộc.")

        old_username = user.username
        can_edit_username = actor_role == "admin" or (actor_role == "manager" and user.role == "user")
        if can_edit_username:
            normalized_username = self._validate_admin_username(username, exclude_user_id=user.id)
            user.username = normalized_username
            if user.role == "manager":
                self._cascade_manager_username_change(old_username, user.username)

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
        meta["updated_at"] = self._now()
        self._save_state()
        return user

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
        meta["updated_at"] = self._now()
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
        meta["updated_at"] = self._now()
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
        removed_jobs = [job for job in self.jobs if job.worker_name == worker_id]
        for job in removed_jobs:
            self._purge_job_artifacts(job, exclude_job_id=job.id)
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
            thread_summary = self._worker_thread_summary(worker)
            worker_rows.append(
                {
                    "index": index,
                    "id": worker.id,
                    "bot_id": worker.id,
                    "manager_name": worker.manager_name,
                    "name": self._resolve_worker_display_name(worker.id),
                    "group": worker.manager_name,
                    "status_label": status_label,
                    "status_class": status_class,
                    "created_at": self._format_full_datetime(worker.last_seen_at),
                    "total_channels": len([channel for channel in self.channels if channel.worker_id == worker.id]),
                    "total_users": len([link for link in self.user_worker_links if link["worker_id"] == worker.id]),
                    "thread_text": thread_summary["thread_text"],
                    "running_threads": thread_summary["running_threads"],
                    "max_threads": thread_summary["max_threads"],
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
            filtered_bot = {"id": worker.id, "name": self._resolve_worker_display_name(worker.id)}
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
                    "worker_name": self._resolve_channel_worker_display_name(channel),
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
                    "worker_name": self._resolve_job_worker_display_name(job),
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
                    "deleted_at": self._format_compact_datetime(self._now()),
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
                    "avatar_url": channel.avatar_url or "/legacy/admin-themes/assets/img/avatar/avatar-1.png",
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
            if user.role == "user" and user.manager_id and user.manager_id == self._resolve_channel_manager_id(channel)
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
        if user.manager_id and self._resolve_channel_manager_id(channel) != user.manager_id:
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
        channel.oauth_connected_at = self._now()
        self._save_state()

    def delete_channel(self, channel_id: str) -> None:
        self._find_channel(channel_id)
        removed_jobs = [job for job in self.jobs if job.channel_id == channel_id]
        for job in removed_jobs:
            self._purge_job_artifacts(job, exclude_job_id=job.id)
        self.channels = [channel for channel in self.channels if channel.id != channel_id]
        self.channel_user_links = [link for link in self.channel_user_links if link["channel_id"] != channel_id]
        self.jobs = [job for job in self.jobs if job.channel_id != channel_id]
        self._save_state()

    def delete_user_connected_channel(self, channel_id: str, *, user_id: str) -> None:
        channel = self._find_channel(channel_id)
        has_access = any(
            link["channel_id"] == channel.id and link["user_id"] == user_id
            for link in self.channel_user_links
        )
        if not has_access:
            raise ValueError("Bạn không có quyền xóa kênh này.")
        self.delete_channel(channel.id)

    def get_channel_export_rows(self) -> list[dict[str, Any]]:
        rows = []
        for channel in self.channels:
            rows.append(
                {
                    "Avatar": channel.avatar_url or "",
                    "ChannelName": channel.name,
                    "ChannelYTId": channel.channel_id,
                    "ChannelLink": self._channel_link(channel),
                    "BotName": self._resolve_channel_worker_display_name(channel),
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
                    "avatar_url": job.channel_avatar_url or "/legacy/admin-themes/assets/img/avatar/avatar-1.png",
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

        existing_channel = next((channel for channel in self.channels if channel.channel_id == channel_id), None)
        existing_refresh_token = existing_channel.oauth_refresh_token if existing_channel else None
        if not refresh_token and not existing_refresh_token:
            raise ValueError("Google khong tra ve refresh_token. Hay xoa quyen app cu va ket noi lai.")

        current_user = self._require_workspace_user(user_id)
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
            raise ValueError("Kích thước file phải lớn hơn 0.")
        if payload.size_bytes > capabilities.max_local_upload_bytes:
            raise ValueError("File vượt quá giới hạn local upload hiện tại.")

        extension = Path(payload.file_name).suffix.lower()
        if extension not in capabilities.allowed_extensions:
            raise ValueError(f"Định dạng file không hỗ trợ: {extension or '(không có extension)'}")

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
        session.updated_at = self._now(trim=False)
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
            raise ValueError("Uploaded asset không hợp lệ hoặc chưa hoàn tất.")
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
            raise ValueError("Asset này không phải local upload.")

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
        refresh_token = str(channel.oauth_refresh_token or "").strip()
        client_id = str(os.getenv("GOOGLE_CLIENT_ID", "")).strip()
        client_secret = str(os.getenv("GOOGLE_CLIENT_SECRET", "")).strip()
        if not refresh_token:
            raise ValueError("Kênh chưa có refresh token OAuth thật. Hãy kết nối lại Google/YouTube.")
        if not client_id or not client_secret:
            raise ValueError("Thiếu GOOGLE_CLIENT_ID hoặc GOOGLE_CLIENT_SECRET trên control plane.")
        privacy_status = job.visibility if job.visibility in {"private", "public", "unlisted"} else "private"
        return WorkerYouTubeUploadTarget(
            job_id=job.id,
            channel_id=channel.channel_id,
            channel_name=channel.name,
            title=job.title,
            description=job.description,
            privacy_status=privacy_status,
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=refresh_token,
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
