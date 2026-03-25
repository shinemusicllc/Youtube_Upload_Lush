from __future__ import annotations

from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile

from ..schemas import JobCreatePayload
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
    return store.start_oauth(base_url)


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
        target_path = store.upload_dir / f"{slot}-{file.filename}"
        target_path.write_bytes(await file.read())
        saved_files[slot] = Path(target_path).name

    derived_source_mode = "local" if any(file and file.filename for file in uploads.values()) else "drive"
    resolved_source_mode = source_mode or derived_source_mode
    parsed_schedule_time = _parse_schedule_time(schedule_time)

    if not channel_id.strip():
        raise HTTPException(status_code=422, detail="channel_id là bắt buộc.")
    if not (video_loop_url and video_loop_url.strip()) and not saved_files.get("video_loop"):
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
        time_render_string=time_render_string,
        schedule_time=parsed_schedule_time,
    )
    return store.create_job(payload, saved_files)


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
