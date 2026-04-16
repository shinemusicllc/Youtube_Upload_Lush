from __future__ import annotations

import mimetypes
import re
import threading
import time
from pathlib import Path
from typing import Callable
from urllib.parse import urlparse

import gdown
import httpx

from .config import WorkerConfig
from .control_plane import worker_auth_headers


DownloadProgressCallback = Callable[[float, str | None], None]


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


def _emit_download_progress(
    progress_callback: DownloadProgressCallback | None,
    ratio: float,
    message: str | None,
) -> None:
    if not progress_callback:
        return
    progress_callback(max(0.0, min(1.0, ratio)), message)


def _download_via_stream(
    url: str,
    destination: Path,
    *,
    progress_callback: DownloadProgressCallback | None = None,
    label: str = "asset",
) -> Path:
    with httpx.Client(follow_redirects=True, timeout=None) as client:
        with client.stream("GET", url) as response:
            response.raise_for_status()
            file_name = _filename_from_content_disposition(response.headers.get("content-disposition"))
            if not destination.suffix:
                destination = destination.with_suffix(_extension_from_response(response))
            if file_name:
                destination = destination.with_name(file_name)

            total_bytes = int(response.headers.get("content-length") or "0") or 0
            received_bytes = 0
            _emit_download_progress(progress_callback, 0.0, f"Dang tai {label}")
            with destination.open("wb") as file_obj:
                for chunk in response.iter_bytes():
                    if not chunk:
                        continue
                    file_obj.write(chunk)
                    if total_bytes <= 0:
                        continue
                    received_bytes += len(chunk)
                    ratio = min(received_bytes / total_bytes, 0.999)
                    _emit_download_progress(
                        progress_callback,
                        ratio,
                        f"Dang tai {label} {int(ratio * 100)}%",
                    )
            _emit_download_progress(progress_callback, 1.0, f"Da tai xong {label}")
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
    progress_callback: DownloadProgressCallback | None = None,
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
        total_bytes = int(response.headers.get("content-length") or "0") or 0
        received_bytes = 0
        _emit_download_progress(progress_callback, 0.0, f"Dang tai {slot}")
        with target_path.open("wb") as file_obj:
            for chunk in response.iter_bytes():
                if not chunk:
                    continue
                file_obj.write(chunk)
                if total_bytes <= 0:
                    continue
                received_bytes += len(chunk)
                ratio = min(received_bytes / total_bytes, 0.999)
                _emit_download_progress(
                    progress_callback,
                    ratio,
                    f"Dang tai {slot} {int(ratio * 100)}%",
                )
        _emit_download_progress(progress_callback, 1.0, f"Da tai xong {slot}")
    return target_path


def download_remote_asset(
    url: str,
    slot: str,
    destination_dir: Path,
    *,
    progress_callback: DownloadProgressCallback | None = None,
) -> Path:
    slot_dir = destination_dir / slot
    slot_dir.mkdir(parents=True, exist_ok=True)
    parsed = urlparse(url)
    file_name = Path(parsed.path).name or slot
    target_path = slot_dir / _sanitize_filename(file_name)

    if _is_google_drive_url(url):
        stop_poll = threading.Event()

        def _poll_partial_file() -> None:
            last_size = 0
            while not stop_poll.is_set():
                try:
                    current_size = target_path.stat().st_size if target_path.exists() else 0
                except OSError:
                    current_size = 0
                if current_size > 0 and current_size != last_size:
                    # Google Drive khong luon cung cap total size truoc khi xac nhan download.
                    pseudo_ratio = min(0.92, 0.08 + min(current_size / (96 * 1024 * 1024), 0.84))
                    _emit_download_progress(
                        progress_callback,
                        pseudo_ratio,
                        f"Dang tai {slot} tu Google Drive",
                    )
                    last_size = current_size
                time.sleep(0.8)

        _emit_download_progress(progress_callback, 0.02, f"Dang tai {slot} tu Google Drive")
        poller = threading.Thread(target=_poll_partial_file, daemon=True)
        poller.start()
        try:
            downloaded_path = gdown.download(url=url, output=str(target_path), quiet=True, fuzzy=True)
        finally:
            stop_poll.set()
            poller.join(timeout=1.0)
        if not downloaded_path:
            raise RuntimeError(f"Khong the tai Google Drive asset: {url}")
        _emit_download_progress(progress_callback, 1.0, f"Da tai xong {slot}")
        return Path(downloaded_path)

    return _download_via_stream(url, target_path, progress_callback=progress_callback, label=slot)
