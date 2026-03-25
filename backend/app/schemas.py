from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


Role = Literal["admin", "manager", "user"]
WorkerStatus = Literal["online", "busy", "offline"]
ChannelStatus = Literal["connected", "pending_reconnect", "disconnected"]
JobStatus = Literal["pending", "queueing", "downloading", "rendering", "uploading", "completed", "cancelled", "error"]
SourceMode = Literal["drive", "local"]


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
    max_local_upload_bytes: int = 2_147_483_648
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
