from __future__ import annotations

import json
import mimetypes
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import httpx

from .control_plane import YouTubeUploadTarget


UploadProgressCallback = Callable[[float, str | None], None]


@dataclass
class YouTubeUploadResult:
    video_id: str
    watch_url: str


def _parse_google_error(response: httpx.Response) -> str:
    try:
        payload = response.json()
    except Exception:
        return response.text.strip() or f"Google upload failed ({response.status_code})."
    error = payload.get("error") or {}
    if isinstance(error, dict):
        if isinstance(error.get("message"), str) and error["message"].strip():
            return error["message"].strip()
        errors = error.get("errors") or []
        if errors and isinstance(errors[0], dict):
            detail = errors[0].get("message") or errors[0].get("reason")
            if isinstance(detail, str) and detail.strip():
                return detail.strip()
    return response.text.strip() or f"Google upload failed ({response.status_code})."


def _exchange_refresh_token(target: YouTubeUploadTarget) -> str:
    with httpx.Client(timeout=60.0, follow_redirects=True) as client:
        response = client.post(
            target.token_uri,
            data={
                "client_id": target.client_id,
                "client_secret": target.client_secret,
                "refresh_token": target.refresh_token,
                "grant_type": "refresh_token",
            },
        )
        if response.status_code >= 400:
            raise RuntimeError(_parse_google_error(response))
        payload = response.json()
        access_token = str(payload.get("access_token") or "").strip()
        if not access_token:
            raise RuntimeError("Google không trả về access_token khi refresh token.")
        return access_token


def upload_video(
    *,
    target: YouTubeUploadTarget,
    file_path: Path,
    chunk_bytes: int,
    progress_callback: UploadProgressCallback | None = None,
) -> YouTubeUploadResult:
    file_size = file_path.stat().st_size
    if file_size <= 0:
        raise RuntimeError("File output rỗng, không thể upload YouTube.")

    access_token = _exchange_refresh_token(target)
    mime_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
    metadata = {
        "snippet": {
            "title": target.title,
            "description": target.description or "",
        },
        "status": {
            "privacyStatus": target.privacy_status,
        },
    }

    with httpx.Client(timeout=None, follow_redirects=True) as client:
        session_response = client.post(
            "https://www.googleapis.com/upload/youtube/v3/videos",
            params={"uploadType": "resumable", "part": "snippet,status"},
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
                "Content-Type": "application/json; charset=UTF-8",
                "X-Upload-Content-Length": str(file_size),
                "X-Upload-Content-Type": mime_type,
            },
            content=json.dumps(metadata),
        )
        if session_response.status_code >= 400:
            raise RuntimeError(_parse_google_error(session_response))
        session_url = session_response.headers.get("Location") or session_response.headers.get("location")
        if not session_url:
            raise RuntimeError("Google không trả về resumable upload session URL.")

        if progress_callback:
            progress_callback(0.02, "Đã tạo phiên upload YouTube")

        chunk_size = max(256 * 1024, int(chunk_bytes))
        uploaded_bytes = 0

        with file_path.open("rb") as file_obj:
            while True:
                chunk = file_obj.read(chunk_size)
                if not chunk:
                    break
                start = uploaded_bytes
                end = start + len(chunk) - 1
                response = client.put(
                    session_url,
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Length": str(len(chunk)),
                        "Content-Type": mime_type,
                        "Content-Range": f"bytes {start}-{end}/{file_size}",
                    },
                    content=chunk,
                )
                if response.status_code == 308:
                    uploaded_bytes = end + 1
                    if progress_callback:
                        progress_callback(min(0.98, uploaded_bytes / file_size), "Đang upload YouTube")
                    continue
                if response.status_code not in {200, 201}:
                    raise RuntimeError(_parse_google_error(response))

                payload = response.json()
                video_id = str(payload.get("id") or "").strip()
                if not video_id:
                    raise RuntimeError("Google không trả về video id sau khi upload xong.")
                if progress_callback:
                    progress_callback(1.0, "Đã upload YouTube thành công")
                return YouTubeUploadResult(
                    video_id=video_id,
                    watch_url=f"https://www.youtube.com/watch?v={video_id}",
                )

    raise RuntimeError("Upload YouTube kết thúc bất thường.")
