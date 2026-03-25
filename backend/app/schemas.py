from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


Role = Literal["admin", "manager", "user"]
WorkerStatus = Literal["online", "busy", "offline"]
ChannelStatus = Literal["connected", "pending_reconnect", "disconnected"]
JobStatus = Literal["pending", "queueing", "downloading", "rendering", "uploading", "completed", "cancelled", "error"]
SourceMode = Literal["drive", "local"]
UploadSessionStatus = Literal["active", "completed", "expired", "cancelled"]


class UserSummary(BaseModel):
    id: str
    username: str
    display_name: str
    role: Role
    password: str | None = None
    manager_id: str | None = None
    manager_name: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    updated_by: str | None = None
    link_telegram: str | None = None


class WorkerRecord(BaseModel):
    id: str
    name: str
    manager_id: str | None = None
    manager_name: str
    group: str | None = None
    status: WorkerStatus
    capacity: int
    load_percent: int
    bandwidth_kbps: int
    disk_used_gb: float
    disk_total_gb: float
    threads: int
    last_seen_at: datetime | None = None


class ChannelRecord(BaseModel):
    id: str
    name: str
    channel_id: str
    avatar_url: str | None = None
    worker_id: str
    worker_name: str
    manager_name: str
    status: ChannelStatus
    oauth_email: str | None = None
    oauth_connected_at: datetime | None = None
    oauth_google_subject: str | None = None
    oauth_refresh_token: str | None = None
    oauth_scope: str | None = None
    oauth_token_type: str | None = None


class UserBotAssignment(BaseModel):
    id: str
    user_id: str
    user_name: str
    worker_id: str
    worker_name: str
    bot_type: Literal["1080p", "4k"]
    number_of_threads: int
    created_at: datetime | None = None


class UploadCapabilities(BaseModel):
    allow_local_upload: bool = True
    allow_resumable_upload: bool = True
    resumable_chunk_bytes: int = 8_388_608
    max_local_upload_bytes: int = 8_589_934_592
    allowed_extensions: list[str] = Field(default_factory=lambda: [".mp4", ".mov", ".webm", ".mp3", ".wav", ".jpg", ".png"])


class OAuthSummary(BaseModel):
    connected_count: int
    needs_reconnect_count: int


class UserBootstrapResponse(BaseModel):
    user: UserSummary
    channels: list[ChannelRecord]
    upload_capabilities: UploadCapabilities
    oauth: OAuthSummary


class JobAsset(BaseModel):
    slot: Literal["intro", "video_loop", "audio_loop", "outro"]
    label: str
    source_mode: SourceMode
    url: str | None = None
    file_name: str | None = None


class RenderJobRecord(BaseModel):
    id: str
    title: str
    description: str | None = None
    source_mode: SourceMode
    channel_id: str
    channel_name: str
    channel_avatar_url: str | None = None
    worker_name: str | None = None
    manager_name: str | None = None
    status: JobStatus
    progress: int = 0
    queue_order: int | None = None
    visibility: str = "private"
    time_render_string: str = "00:30:00"
    scheduled_at: datetime | None = None
    created_at: datetime
    download_started_at: datetime | None = None
    upload_started_at: datetime | None = None
    completed_at: datetime | None = None
    started_at: datetime | None = None
    claimed_at: datetime | None = None
    claimed_by_worker_id: str | None = None
    lease_expires_at: datetime | None = None
    error_message: str | None = None
    output_url: str | None = None
    source_label: str
    source_file_name: str | None = None
    thumbnail_url: str | None = None
    can_cancel: bool = True
    assets: list[JobAsset] = Field(default_factory=list)


class UserJobsResponse(BaseModel):
    jobs: list[RenderJobRecord]


class JobCreatePayload(BaseModel):
    channel_id: str
    title: str
    description: str | None = None
    source_mode: SourceMode
    intro_url: str | None = None
    video_loop_url: str | None = None
    audio_loop_url: str | None = None
    outro_url: str | None = None
    intro_asset_id: str | None = None
    video_loop_asset_id: str | None = None
    audio_loop_asset_id: str | None = None
    outro_asset_id: str | None = None
    time_render_string: str = "00:30:00"
    schedule_time: datetime | None = None


class OAuthStartResponse(BaseModel):
    auth_url: str | None = None
    message: str


class AdminSummary(BaseModel):
    total_managers: int
    total_users: int
    total_workers: int
    workers_online: int
    channels_connected: int
    queued_jobs: int
    running_jobs: int
    failed_jobs: int


class AdminDashboardResponse(BaseModel):
    summary: AdminSummary
    users: list[UserSummary]
    workers: list[WorkerRecord]
    channels: list[ChannelRecord]
    jobs: list[RenderJobRecord]


class UploadSessionCreateRequest(BaseModel):
    slot: Literal["intro", "video_loop", "audio_loop", "outro"]
    file_name: str
    size_bytes: int
    content_type: str | None = None


class UploadSessionRecord(BaseModel):
    session_id: str
    slot: Literal["intro", "video_loop", "audio_loop", "outro"]
    file_name: str
    content_type: str | None = None
    size_bytes: int
    received_bytes: int = 0
    chunk_size: int
    status: UploadSessionStatus = "active"
    created_at: datetime
    updated_at: datetime
    expires_at: datetime
    temp_path: str
    asset_id: str | None = None
    stored_file_name: str | None = None


class UploadSessionResponse(BaseModel):
    session_id: str
    slot: Literal["intro", "video_loop", "audio_loop", "outro"]
    file_name: str
    size_bytes: int
    received_bytes: int
    chunk_size: int
    status: UploadSessionStatus
    expires_at: datetime
    asset_id: str | None = None
    stored_file_name: str | None = None


class WorkerRegisterPayload(BaseModel):
    worker_id: str
    name: str
    shared_secret: str
    manager_name: str = "system"
    group: str | None = None
    capacity: int = 1
    threads: int = 1
    disk_total_gb: float = 0


class WorkerHeartbeatPayload(BaseModel):
    worker_id: str
    shared_secret: str
    load_percent: int = 0
    bandwidth_kbps: int = 0
    disk_used_gb: float = 0
    disk_total_gb: float = 0
    threads: int = 1
    status: WorkerStatus = "online"


class WorkerControlResponse(BaseModel):
    ok: bool
    worker: WorkerRecord


class WorkerAuthPayload(BaseModel):
    worker_id: str
    shared_secret: str


class WorkerClaimResponse(BaseModel):
    ok: bool
    worker: WorkerRecord
    job: RenderJobRecord | None = None


class WorkerJobProgressPayload(BaseModel):
    worker_id: str
    shared_secret: str
    status: JobStatus
    progress: int = 0
    message: str | None = None


class WorkerJobCompletePayload(BaseModel):
    worker_id: str
    shared_secret: str
    output_url: str | None = None
    message: str | None = None


class WorkerJobFailPayload(BaseModel):
    worker_id: str
    shared_secret: str
    message: str
