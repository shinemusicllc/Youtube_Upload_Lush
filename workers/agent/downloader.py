from __future__ import annotations

import mimetypes
import re
from pathlib import Path
from urllib.parse import urlparse

import gdown
import httpx

from .config import WorkerConfig
from .control_plane import worker_auth_headers


def _sanitize_filename(file_name: str) -> str:
    value = re.sub(r"[^A-Za-z0-9._-]+", "-", (file_name or "").strip())
    value = value.strip(".-")
    return value or "download.bin"


def _filename_from_content_disposition(content_disposition: str | None) -> str | None:
    if not content_disposition:
        return None
    match = re.search(r'filename="?([^";]+)"?', content_disposition)
    if match:
        return _sanitize_filename(match.group(1))
    return None


def _extension_from_response(response: httpx.Response) -> str:
    content_type = (response.headers.get("content-type") or "").split(";")[0].strip()
    guessed = mimetypes.guess_extension(content_type) or ""
    return guessed if guessed != ".jpe" else ".jpg"


def _download_via_stream(url: str, destination: Path) -> Path:
    with httpx.Client(follow_redirects=True, timeout=None) as client:
        with client.stream("GET", url) as response:
            response.raise_for_status()
            file_name = _filename_from_content_disposition(response.headers.get("content-disposition"))
            if not destination.suffix:
                destination = destination.with_suffix(_extension_from_response(response))
            if file_name:
                destination = destination.with_name(file_name)
            with destination.open("wb") as file_obj:
                for chunk in response.iter_bytes():
                    if chunk:
                        file_obj.write(chunk)
    return destination


def _is_google_drive_url(url: str) -> bool:
    host = (urlparse(url).hostname or "").lower()
    return "drive.google.com" in host or "docs.google.com" in host


def download_local_asset(
    client: httpx.Client,
    config: WorkerConfig,
    job_id: str,
    slot: str,
    destination_dir: Path,
) -> Path:
    slot_dir = destination_dir / slot
    slot_dir.mkdir(parents=True, exist_ok=True)
    fallback_path = slot_dir / f"{slot}.bin"
    with client.stream(
        "GET",
        f"/api/workers/jobs/{job_id}/assets/{slot}",
        headers=worker_auth_headers(config),
    ) as response:
        response.raise_for_status()
        file_name = _filename_from_content_disposition(response.headers.get("content-disposition")) or fallback_path.name
        target_path = slot_dir / file_name
        with target_path.open("wb") as file_obj:
            for chunk in response.iter_bytes():
                if chunk:
                    file_obj.write(chunk)
    return target_path


def download_remote_asset(url: str, slot: str, destination_dir: Path) -> Path:
    slot_dir = destination_dir / slot
    slot_dir.mkdir(parents=True, exist_ok=True)
    parsed = urlparse(url)
    file_name = Path(parsed.path).name or slot
    target_path = slot_dir / _sanitize_filename(file_name)

    if _is_google_drive_url(url):
        downloaded_path = gdown.download(url=url, output=str(target_path), quiet=True, fuzzy=True)
        if not downloaded_path:
            raise RuntimeError(f"Không thể tải Google Drive asset: {url}")
        return Path(downloaded_path)

    return _download_via_stream(url, target_path)
