from __future__ import annotations

from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Body, File, Form, HTTPException, Request, UploadFile

from ..auth import GOOGLE_OAUTH_STATE_SESSION_KEY
from ..schemas import JobCreatePayload, UploadSessionCreateRequest
from ..store import store

router = APIRouter(tags=["user"])


def _parse_schedule_time(value: str | None) -> datetime | None:
    if not value or not value.strip():
        return None

    cleaned = value.strip()
    for fmt in ("%d/%m/%Y %H:%M", "%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(cleaned, fmt)
        except ValueError:
            continue
    raise HTTPException(status_code=422, detail="schedule_time không đúng định dạng hỗ trợ.")


@router.get("/user/bootstrap")
async def get_user_bootstrap():
    return store.get_user_bootstrap()


@router.get("/user/jobs")
async def get_user_jobs():
    return store.get_user_jobs()


@router.post("/user/oauth/connect/start")
async def start_user_oauth(request: Request):
    base_url = str(request.base_url).rstrip("/")
    state = uuid4().hex
    request.session[GOOGLE_OAUTH_STATE_SESSION_KEY] = state
    return store.start_oauth(base_url, state=state)


@router.post("/user/uploads/sessions")
async def create_upload_session(payload: UploadSessionCreateRequest = Body(...)):
    try:
        return store.create_upload_session(payload)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/user/uploads/sessions/{session_id}")
async def get_upload_session(session_id: str):
    try:
        return store.get_upload_session(session_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Không tìm thấy upload session.") from exc


@router.patch("/user/uploads/sessions/{session_id}")
async def append_upload_session_chunk(request: Request, session_id: str):
    offset_header = request.headers.get("x-upload-offset", "0")
    try:
        offset = int(offset_header)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="x-upload-offset không hợp lệ.") from exc
    body = await request.body()
    try:
        return store.append_upload_chunk(session_id, offset, body)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Không tìm thấy upload session.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.delete("/user/uploads/sessions/{session_id}")
async def delete_upload_session(session_id: str):
    try:
        store.abort_upload_session(session_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Không tìm thấy upload session.") from exc
    return {"status": "deleted", "session_id": session_id}


@router.post("/user/jobs")
async def create_user_job(
    channel_id: str = Form(...),
    title: str = Form(...),
    description: str | None = Form(default=None),
    source_mode: str | None = Form(default=None),
    time_render_string: str = Form(default="00:30:00"),
    schedule_time: str | None = Form(default=None),
    intro_url: str | None = Form(default=None),
    video_loop_url: str | None = Form(default=None),
    audio_loop_url: str | None = Form(default=None),
    outro_url: str | None = Form(default=None),
    intro_asset_id: str | None = Form(default=None),
    video_loop_asset_id: str | None = Form(default=None),
    audio_loop_asset_id: str | None = Form(default=None),
    outro_asset_id: str | None = Form(default=None),
    intro_file: UploadFile | None = File(default=None),
    video_loop_file: UploadFile | None = File(default=None),
    audio_loop_file: UploadFile | None = File(default=None),
    outro_file: UploadFile | None = File(default=None),
):
    uploads = {
        "intro": intro_file,
        "video_loop": video_loop_file,
        "audio_loop": audio_loop_file,
        "outro": outro_file,
    }
    saved_files: dict[str, str | None] = {}

    for slot, file in uploads.items():
        if not file:
            saved_files[slot] = None
            continue
        safe_name = store._sanitize_filename(file.filename)
        target_path = store.upload_asset_dir / f"asset-{uuid4().hex[:12]}-{safe_name}"
        with target_path.open("wb") as buffer:
            while chunk := await file.read(1024 * 1024):
                buffer.write(chunk)
        saved_files[slot] = Path(target_path).name

    uploaded_asset_ids = {
        "intro": intro_asset_id,
        "video_loop": video_loop_asset_id,
        "audio_loop": audio_loop_asset_id,
        "outro": outro_asset_id,
    }
    derived_source_mode = "local" if any(file and file.filename for file in uploads.values()) or any(uploaded_asset_ids.values()) else "drive"
    resolved_source_mode = source_mode or derived_source_mode
    parsed_schedule_time = _parse_schedule_time(schedule_time)

    if not channel_id.strip():
        raise HTTPException(status_code=422, detail="channel_id là bắt buộc.")
    if not (video_loop_url and video_loop_url.strip()) and not saved_files.get("video_loop") and not uploaded_asset_ids.get("video_loop"):
        raise HTTPException(status_code=422, detail="Cần nhập video loop hoặc upload file video loop.")

    payload = JobCreatePayload(
        channel_id=channel_id,
        title=title,
        description=description,
        source_mode=resolved_source_mode,  # type: ignore[arg-type]
        intro_url=intro_url,
        video_loop_url=video_loop_url,
        audio_loop_url=audio_loop_url,
        outro_url=outro_url,
        intro_asset_id=intro_asset_id,
        video_loop_asset_id=video_loop_asset_id,
        audio_loop_asset_id=audio_loop_asset_id,
        outro_asset_id=outro_asset_id,
        time_render_string=time_render_string,
        schedule_time=parsed_schedule_time,
    )
    try:
        return store.create_job(payload, saved_files)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.patch("/user/jobs/{job_id}/cancel")
async def cancel_user_job(job_id: str):
    try:
        return store.cancel_job(job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Không tìm thấy job.") from exc


@router.delete("/user/jobs/{job_id}")
async def delete_user_job(job_id: str):
    try:
        store.delete_job(job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Không tìm thấy job.") from exc
    return {"status": "deleted", "job_id": job_id}


@router.delete("/user/channels/{channel_id}")
async def delete_user_channel(channel_id: str):
    try:
        store.delete_user_connected_channel(channel_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Không tìm thấy kênh.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return {"status": "deleted", "channel_id": channel_id}
