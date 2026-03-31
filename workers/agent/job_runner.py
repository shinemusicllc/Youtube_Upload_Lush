from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import httpx

from .browser_uploader import upload_video_via_browser
from .config import WorkerConfig
from .control_plane import complete_job, get_job_youtube_target, update_job_progress, upload_job_thumbnail
from .downloader import download_local_asset, download_remote_asset
from .ffmpeg_pipeline import probe_media, render_job_assets


def _job_asset_map(job: dict) -> dict[str, dict]:
    return {str(asset["slot"]): asset for asset in job.get("assets") or []}


def _download_assets(
    client: httpx.Client,
    config: WorkerConfig,
    job: dict,
    downloads_dir: Path,
) -> dict[str, Path]:
    assets = _job_asset_map(job)
    downloaded: dict[str, Path] = {}
    ordered_assets = [
        (slot, assets.get(slot))
        for slot in ["intro", "video_loop", "audio_loop", "outro"]
        if assets.get(slot)
    ]
    total_assets = len(ordered_assets)
    if total_assets <= 0:
        return downloaded

    def _progress_callback_for(asset_index: int, slot_name: str):
        def _callback(ratio: float, _message: str | None) -> None:
            clamped_ratio = max(0.0, min(1.0, ratio))
            overall_ratio = (asset_index + clamped_ratio) / total_assets
            update_job_progress(
                client,
                config,
                str(job["id"]),
                status="downloading",
                progress=max(0, min(100, int(overall_ratio * 100))),
                message=f"Dang tai {slot_name} {int(clamped_ratio * 100)}%",
            )

        return _callback

    for index, (slot, asset) in enumerate(ordered_assets):
        if asset.get("source_mode") == "local":
            downloaded[slot] = download_local_asset(
                client,
                config,
                str(job["id"]),
                slot,
                downloads_dir,
                progress_callback=_progress_callback_for(index, slot),
            )
        elif asset.get("url"):
            downloaded[slot] = download_remote_asset(
                str(asset["url"]),
                slot,
                downloads_dir,
                progress_callback=_progress_callback_for(index, slot),
            )
        else:
            raise ValueError(f"Asset {slot} khong co nguon tai hop le.")
        update_job_progress(
            client,
            config,
            str(job["id"]),
            status="downloading",
            progress=max(0, min(100, int(((index + 1) / total_assets) * 100))),
            message=f"Da tai xong {slot}",
        )
    return downloaded


def _capture_video_preview(
    config: WorkerConfig,
    *,
    source_path: Path,
    destination_path: Path,
) -> Path:
    media_info = probe_media(config.ffprobe_bin, source_path)
    if not media_info.has_video:
        raise ValueError(f"Asset {source_path.name} khong co video stream.")

    duration_seconds = max(0.0, float(media_info.duration_seconds or 0.0))
    seek_seconds = 0.0
    if duration_seconds > 2:
        seek_seconds = min(max(duration_seconds * 0.15, 1.0), max(duration_seconds - 0.5, 0.0))

    command = [
        config.ffmpeg_bin,
        "-y",
        "-ss",
        f"{seek_seconds:.3f}",
        "-i",
        str(source_path),
        "-frames:v",
        "1",
        "-vf",
        "scale=480:-2:force_original_aspect_ratio=decrease",
        str(destination_path),
    ]
    result = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0 or not destination_path.exists():
        tail = "\n".join((result.stderr or result.stdout or "").splitlines()[-20:])
        raise RuntimeError(f"Khong the tao snapshot preview.\n{tail}".strip())
    return destination_path


def _try_upload_job_preview_thumbnail(
    client: httpx.Client,
    config: WorkerConfig,
    *,
    job_id: str,
    video_source_path: Path | None,
    job_dir: Path,
) -> None:
    if not video_source_path or not video_source_path.exists():
        return

    preview_dir = job_dir / "preview"
    preview_dir.mkdir(parents=True, exist_ok=True)
    preview_path = preview_dir / "video-loop-preview.jpg"
    try:
        snapshot_path = _capture_video_preview(
            config,
            source_path=video_source_path,
            destination_path=preview_path,
        )
        upload_job_thumbnail(
            client,
            config,
            job_id,
            file_name=snapshot_path.name,
            content_type="image/jpeg",
            payload=snapshot_path.read_bytes(),
        )
    except Exception as exc:
        print(f"[preview] job={job_id} thumbnail upload skipped: {exc}")


def run_job(client: httpx.Client, config: WorkerConfig, job: dict) -> None:
    job_id = str(job["id"])
    job_dir = config.work_root / job_id
    downloads_dir = job_dir / "downloads"
    outputs_dir = config.work_root / "outputs"
    final_output_path: Path | None = None
    config.work_root.mkdir(parents=True, exist_ok=True)
    outputs_dir.mkdir(parents=True, exist_ok=True)
    if job_dir.exists():
        shutil.rmtree(job_dir)
    downloads_dir.mkdir(parents=True, exist_ok=True)

    try:
        update_job_progress(client, config, job_id, status="downloading", progress=0, message="Bat dau tai asset")
        asset_paths = _download_assets(client, config, job, downloads_dir)
        update_job_progress(client, config, job_id, status="rendering", progress=1, message="Bat dau render")

        _try_upload_job_preview_thumbnail(
            client,
            config,
            job_id=job_id,
            video_source_path=asset_paths.get("video_loop"),
            job_dir=job_dir,
        )

        result = render_job_assets(
            config,
            job,
            asset_paths,
            job_dir,
            progress_callback=lambda progress, message: update_job_progress(
                client,
                config,
                job_id,
                status="rendering",
                progress=progress,
                message=message,
            ),
        )

        final_output_path = outputs_dir / f"{job_id}-{result.output_path.name}"
        shutil.move(str(result.output_path), str(final_output_path))
        local_output_url = f"worker://{config.worker_name}/{final_output_path.as_posix()}"

        if config.youtube_upload_enabled:
            update_job_progress(
                client,
                config,
                job_id,
                status="uploading",
                progress=0,
                message="Dang chuan bi upload YouTube",
            )
            target = get_job_youtube_target(client, config, job_id)
            upload_result = upload_video_via_browser(
                config=config,
                target=target,
                file_path=final_output_path,
                progress_callback=lambda ratio, message: update_job_progress(
                    client,
                    config,
                    job_id,
                    status="uploading",
                    progress=max(0, min(100, int(max(0.0, min(1.0, ratio)) * 100))),
                    message=message,
                ),
            )
            complete_job(
                client,
                config,
                job_id,
                output_url=upload_result.watch_url or getattr(upload_result, "studio_url", None),
            )
            if not config.keep_job_dirs and upload_result.cleanup_safe and final_output_path.exists():
                final_output_path.unlink(missing_ok=True)
        else:
            complete_job(client, config, job_id, output_url=local_output_url)
    except Exception:
        if not config.keep_job_dirs and final_output_path is not None and final_output_path.exists():
            final_output_path.unlink(missing_ok=True)
        raise
    finally:
        if not config.keep_job_dirs and job_dir.exists():
            shutil.rmtree(job_dir, ignore_errors=True)
