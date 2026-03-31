from __future__ import annotations

import mimetypes
import re
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


def _emit_progress(
    progress_callback: DownloadProgressCallback | None,
    ratio: float,
    *,
    state: dict[str, float] | None = None,
    message: str | None = None,
) -> None:
    if not progress_callback:
        return
    clamped = max(0.0, min(1.0, ratio))
    if state is None:
        progress_callback(clamped, message)
        return
    last_ratio = state.get("last_ratio", -1.0)
    if clamped >= 1.0 or last_ratio < 0 or abs(clamped - last_ratio) >= 0.01:
        state["last_ratio"] = clamped
        progress_callback(clamped, message)


def _download_via_stream(
    url: str,
    destination: Path,
    *,
    progress_callback: DownloadProgressCallback | None = None,
) -> Path:
    with httpx.Client(follow_redirects=True, timeout=None) as client:
        with client.stream("GET", url) as response:
            response.raise_for_status()
            file_name = _filename_from_content_disposition(response.headers.get("content-disposition"))
            if not destination.suffix:
                destination = destination.with_suffix(_extension_from_response(response))
            if file_name:
                destination = destination.with_name(file_name)
            total_bytes = int(response.headers.get("content-length") or "0")
            downloaded_bytes = 0
            progress_state = {"last_ratio": -1.0}
            with destination.open("wb") as file_obj:
                for chunk in response.iter_bytes():
                    if not chunk:
                        continue
                    file_obj.write(chunk)
                    downloaded_bytes += len(chunk)
                    if total_bytes > 0:
                        _emit_progress(progress_callback, downloaded_bytes / total_bytes, state=progress_state)
            _emit_progress(progress_callback, 1.0, state=progress_state)
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
    *,
    progress_callback: DownloadProgressCallback | None = None,
) -> Path:
    slot_dir = destination_dir / slot
    slot_dir.mkdir(parents=True, exist_ok=True)
    fallback_path = slot_dir / f"{slot}.bin"
    with client.stream(
        "GET",
        f"/api/workers/jobs/{job_id}/assets/{slot}",
        headers=worker_auth_headers(config),
        timeout=None,
    ) as response:
        response.raise_for_status()
        file_name = _filename_from_content_disposition(response.headers.get("content-disposition")) or fallback_path.name
        target_path = slot_dir / file_name
        total_bytes = int(response.headers.get("content-length") or "0")
        downloaded_bytes = 0
        progress_state = {"last_ratio": -1.0}
        with target_path.open("wb") as file_obj:
            for chunk in response.iter_bytes():
                if not chunk:
                    continue
                file_obj.write(chunk)
                downloaded_bytes += len(chunk)
                if total_bytes > 0:
                    _emit_progress(progress_callback, downloaded_bytes / total_bytes, state=progress_state)
        _emit_progress(progress_callback, 1.0, state=progress_state)
    return target_path


def _download_google_drive_asset(
    url: str,
    target_path: Path,
    *,
    progress_callback: DownloadProgressCallback | None = None,
) -> Path:
    tqdm_module = gdown.download.__globals__.get("tqdm")
    original_tqdm = getattr(tqdm_module, "tqdm", None) if tqdm_module is not None else None
    callback_tqdm = None

    if progress_callback and original_tqdm is not None:
        class CallbackTqdm(original_tqdm):  # type: ignore[misc, valid-type]
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self._codex_last_ratio = -1.0

            def update(self, n=1):
                result = super().update(n)
                if self.total:
                    ratio = max(0.0, min(1.0, self.n / self.total))
                    if ratio >= 1.0 or self._codex_last_ratio < 0 or abs(ratio - self._codex_last_ratio) >= 0.01:
                        self._codex_last_ratio = ratio
                        progress_callback(ratio, None)
                return result

        callback_tqdm = CallbackTqdm

    if callback_tqdm is not None and tqdm_module is not None:
        tqdm_module.tqdm = callback_tqdm
    try:
        downloaded_path = gdown.download(
            url=url,
            output=str(target_path),
            quiet=not bool(progress_callback),
            fuzzy=True,
            log_messages={"start": "", "output": ""},
        )
    finally:
        if callback_tqdm is not None and tqdm_module is not None and original_tqdm is not None:
            tqdm_module.tqdm = original_tqdm

    if not downloaded_path:
        raise RuntimeError(f"Khong the tai Google Drive asset: {url}")
    _emit_progress(progress_callback, 1.0)
    return Path(downloaded_path)


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
        return _download_google_drive_asset(url, target_path, progress_callback=progress_callback)

    return _download_via_stream(url, target_path, progress_callback=progress_callback)
