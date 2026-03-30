from __future__ import annotations

import shutil
from pathlib import Path

import httpx

from .config import WorkerConfig
from .control_plane import complete_job, get_job_youtube_target, update_job_progress
from .downloader import download_local_asset, download_remote_asset
from .ffmpeg_pipeline import render_job_assets
from .youtube_uploader import upload_video


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
    for index, slot in enumerate(["intro", "video_loop", "audio_loop", "outro"], start=1):
        asset = assets.get(slot)
        if not asset:
            continue
        if asset.get("source_mode") == "local":
            downloaded[slot] = download_local_asset(client, config, str(job["id"]), slot, downloads_dir)
        elif asset.get("url"):
            downloaded[slot] = download_remote_asset(str(asset["url"]), slot, downloads_dir)
        else:
            raise ValueError(f"Asset {slot} không có nguồn tải hợp lệ.")
        progress = min(30, 5 + index * 6)
        update_job_progress(
            client,
            config,
            str(job["id"]),
            status="downloading",
            progress=progress,
            message=f"Đã tải asset {slot}",
        )
    return downloaded


def run_job(client: httpx.Client, config: WorkerConfig, job: dict) -> None:
    job_id = str(job["id"])
    job_dir = config.work_root / job_id
    downloads_dir = job_dir / "downloads"
    outputs_dir = config.work_root / "outputs"
    config.work_root.mkdir(parents=True, exist_ok=True)
    outputs_dir.mkdir(parents=True, exist_ok=True)
    if job_dir.exists():
        shutil.rmtree(job_dir)
    downloads_dir.mkdir(parents=True, exist_ok=True)

    try:
        update_job_progress(client, config, job_id, status="downloading", progress=1, message="Bắt đầu tải asset")
        asset_paths = _download_assets(client, config, job, downloads_dir)
        update_job_progress(client, config, job_id, status="rendering", progress=32, message="Bắt đầu render")

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
                progress=2,
                message="Đang chuẩn bị upload YouTube",
            )
            target = get_job_youtube_target(client, config, job_id)
            upload_result = upload_video(
                target=target,
                file_path=final_output_path,
                chunk_bytes=config.youtube_upload_chunk_bytes,
                progress_callback=lambda ratio, message: update_job_progress(
                    client,
                    config,
                    job_id,
                    status="uploading",
                    progress=max(2, min(99, 2 + int(ratio * 97))),
                    message=message,
                ),
            )
            complete_job(
                client,
                config,
                job_id,
                output_url=upload_result.watch_url,
            )
        else:
            complete_job(client, config, job_id, output_url=local_output_url)
    finally:
        if not config.keep_job_dirs and job_dir.exists():
            shutil.rmtree(job_dir, ignore_errors=True)
