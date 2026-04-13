from __future__ import annotations

import os
import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import httpx

from .config import WorkerConfig
from .control_plane import (
    LiveStreamStoppedError,
    complete_live_stream,
    get_live_stream_runtime_state,
    update_live_stream_progress,
)
from .downloader import download_remote_asset
from .ffmpeg_pipeline import probe_media


def _env_int(name: str, default: int, *, minimum: int = 0) -> int:
    raw_value = str(os.getenv(name, str(default))).strip()
    try:
        parsed = int(raw_value)
    except ValueError:
        return default
    return max(minimum, parsed)


def _env_float(name: str, default: float, *, minimum: float = 0.0) -> float:
    raw_value = str(os.getenv(name, str(default))).strip()
    try:
        parsed = float(raw_value)
    except ValueError:
        return default
    return max(minimum, parsed)


LIVE_TARGET_VIDEO_BITRATE_KBPS = _env_int("WORKER_LIVE_TARGET_VIDEO_BITRATE_KBPS", 6800, minimum=256)
LIVE_TARGET_AUDIO_BITRATE_KBPS = _env_int("WORKER_LIVE_TARGET_AUDIO_BITRATE_KBPS", 160, minimum=64)
LIVE_TARGET_MAXRATE_KBPS = _env_int(
    "WORKER_LIVE_MAXRATE_KBPS",
    LIVE_TARGET_VIDEO_BITRATE_KBPS,
    minimum=LIVE_TARGET_VIDEO_BITRATE_KBPS,
)
LIVE_TARGET_BUFSIZE_KBPS = _env_int(
    "WORKER_LIVE_BUFSIZE_KBPS",
    LIVE_TARGET_MAXRATE_KBPS * 2,
    minimum=LIVE_TARGET_MAXRATE_KBPS,
)
LIVE_TARGET_X264_PRESET = str(os.getenv("WORKER_LIVE_X264_PRESET", "veryfast")).strip() or "veryfast"
LIVE_RUNTIME_GUARD_INTERVAL_SECONDS = _env_float("WORKER_LIVE_RUNTIME_GUARD_INTERVAL_SECONDS", 1.0, minimum=0.2)
LIVE_FFMPEG_PROGRESS_INTERVAL_SECONDS = _env_float("WORKER_LIVE_FFMPEG_PROGRESS_INTERVAL_SECONDS", 0.5, minimum=0.2)


def _app_timezone() -> ZoneInfo:
    return ZoneInfo(os.getenv("APP_TIMEZONE", "Asia/Saigon"))


def _now_local() -> datetime:
    return datetime.now(_app_timezone()).replace(tzinfo=None)


def _parse_control_plane_datetime(value: str | None) -> datetime | None:
    cleaned = str(value or "").strip()
    if not cleaned:
        return None
    normalized = cleaned.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is not None:
        return parsed.astimezone(_app_timezone()).replace(tzinfo=None)
    return parsed


def _rtmp_target(stream: dict) -> str:
    base_url = str(stream.get("rtmp_url") or "rtmp://x.rtmp.youtube.com/live2").strip().rstrip("/")
    stream_key = str(stream.get("stream_key") or "").strip()
    if not stream_key:
        raise ValueError("Thiếu stream_key cho live runtime.")
    return f"{base_url}/{stream_key}"


def _touch_activity(path: Path | None) -> None:
    if path is None:
        return
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
    except OSError:
        return


def _is_terminal_live_stream_conflict(exc: Exception) -> bool:
    if not isinstance(exc, httpx.HTTPStatusError):
        return False
    response = exc.response
    request = exc.request
    if response is None or request is None:
        return False
    request_url = str(request.url)
    if "/api/live-workers/streams/" not in request_url:
        return False
    return response.status_code in {404, 409}


def _stop_process(process: subprocess.Popen[str], *, timeout_seconds: float = 5.0) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    deadline = time.monotonic() + max(0.5, timeout_seconds)
    while process.poll() is None and time.monotonic() < deadline:
        time.sleep(0.1)
    if process.poll() is not None:
        return
    process.kill()
    try:
        process.wait(timeout=max(0.5, timeout_seconds))
    except subprocess.TimeoutExpired:
        return


def _make_progress_reporter(
    client: httpx.Client,
    config: WorkerConfig,
    stream_id: str,
    *,
    activity_path: Path | None = None,
):
    state = {
        "status": None,
        "progress": -1,
        "message": None,
        "sent_at": 0.0,
    }

    def _report(status: str, progress: int, message: str | None = None, *, force: bool = False) -> None:
        _touch_activity(activity_path)
        bounded = max(0, min(100, int(progress)))
        cleaned_message = (message or "").strip() or None
        now = time.monotonic()
        last_status = state["status"]
        last_progress = int(state["progress"])
        last_message = state["message"]
        last_sent_at = float(state["sent_at"])

        progress_jump = bounded - last_progress
        should_send = force
        should_send = should_send or last_status != status
        should_send = should_send or bounded in {0, 100}
        should_send = should_send or progress_jump >= 3
        should_send = should_send or (cleaned_message != last_message and now - last_sent_at >= 1.0)
        should_send = should_send or (progress_jump > 0 and now - last_sent_at >= 1.0)
        should_send = should_send or now - last_sent_at >= 10.0

        if not should_send:
            state["status"] = status
            state["progress"] = max(last_progress, bounded)
            state["message"] = cleaned_message
            return

        update_live_stream_progress(
            client,
            config,
            stream_id,
            status=status,
            progress=bounded,
            message=cleaned_message,
        )
        state["status"] = status
        state["progress"] = max(last_progress, bounded)
        state["message"] = cleaned_message
        state["sent_at"] = now

    return _report


def _make_live_runtime_guard(
    client: httpx.Client,
    config: WorkerConfig,
    stream_id: str,
):
    state = {"last_checked_at": 0.0}

    def _guard(*, force: bool = False) -> None:
        now = time.monotonic()
        last_checked_at = float(state["last_checked_at"])
        if not force and now - last_checked_at < LIVE_RUNTIME_GUARD_INTERVAL_SECONDS:
            return
        state["last_checked_at"] = now
        try:
            runtime_state = get_live_stream_runtime_state(client, config, stream_id)
        except Exception as exc:
            if isinstance(exc, LiveStreamStoppedError):
                raise
            if _is_terminal_live_stream_conflict(exc):
                raise LiveStreamStoppedError(stream_id, "stopped") from exc
            print(f"[live] runtime guard check failed for {stream_id}: {exc}", flush=True)
            return
        if runtime_state.should_stop:
            raise LiveStreamStoppedError(stream_id, runtime_state.status)

    return _guard


def _download_live_assets(
    stream: dict,
    downloads_dir: Path,
    report_progress,
    *,
    lifecycle_guard=None,
) -> tuple[Path, Path | None]:
    downloads_dir.mkdir(parents=True, exist_ok=True)
    video_url = str(stream.get("video_url") or "").strip()
    if not video_url:
        raise ValueError("Thiếu video_url cho live runtime.")
    audio_url = str(stream.get("audio_url") or "").strip()

    ordered_assets = [("video", video_url)]
    if audio_url:
        ordered_assets.append(("audio", audio_url))
    total_assets = len(ordered_assets)

    def _progress_callback_for(asset_index: int, slot_name: str):
        def _callback(ratio: float, _message: str | None) -> None:
            if lifecycle_guard:
                lifecycle_guard()
            clamped_ratio = max(0.0, min(1.0, ratio))
            overall_ratio = (asset_index + clamped_ratio) / total_assets
            report_progress(
                "downloading",
                max(0, min(100, int(overall_ratio * 100))),
                f"Đang tải {slot_name} {int(clamped_ratio * 100)}%",
            )

        return _callback

    if lifecycle_guard:
        lifecycle_guard(force=True)
    video_path = download_remote_asset(
        video_url,
        "video",
        downloads_dir,
        progress_callback=_progress_callback_for(0, "video"),
    )
    report_progress("downloading", max(1, int((1 / total_assets) * 100)), "Đã tải xong video")

    audio_path: Path | None = None
    if audio_url:
        if lifecycle_guard:
            lifecycle_guard(force=True)
        audio_path = download_remote_asset(
            audio_url,
            "audio",
            downloads_dir,
            progress_callback=_progress_callback_for(1, "audio"),
        )
        report_progress("downloading", 100, "Đã tải xong audio", force=True)
    else:
        report_progress("downloading", 100, "Đã tải xong media", force=True)
    return video_path, audio_path


def _run_ffmpeg_with_progress(
    config: WorkerConfig,
    arguments: list[str],
    *,
    working_dir: Path,
    total_duration_seconds: float | None = None,
    progress_callback=None,
    end_time_live: datetime | None = None,
    lifecycle_guard=None,
) -> None:
    command = [
        config.ffmpeg_bin,
        "-stats_period",
        f"{LIVE_FFMPEG_PROGRESS_INTERVAL_SECONDS:.2f}",
        "-progress",
        "pipe:1",
        "-nostats",
        *arguments,
    ]
    process = subprocess.Popen(
        command,
        cwd=str(working_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    output_lines: list[str] = []
    terminated_for_end_time = False
    callback_error: Exception | None = None
    return_code: int | None = None
    try:
        assert process.stdout is not None
        while True:
            try:
                if lifecycle_guard:
                    lifecycle_guard()
                if end_time_live and _now_local() >= end_time_live and process.poll() is None:
                    terminated_for_end_time = True
                    _stop_process(process)
            except Exception as exc:
                if isinstance(exc, LiveStreamStoppedError) or _is_terminal_live_stream_conflict(exc):
                    callback_error = exc
                    _stop_process(process)
                    break
                raise
            raw_line = process.stdout.readline()
            if not raw_line:
                if process.poll() is not None:
                    break
                try:
                    if lifecycle_guard:
                        lifecycle_guard(force=True)
                except Exception as exc:
                    if isinstance(exc, LiveStreamStoppedError) or _is_terminal_live_stream_conflict(exc):
                        callback_error = exc
                        _stop_process(process)
                        break
                    raise
                time.sleep(0.1)
                continue
            line = raw_line.strip()
            if line:
                output_lines.append(line)
            if not progress_callback or not total_duration_seconds:
                continue
            if line.startswith("out_time_ms="):
                try:
                    current_seconds = int(line.split("=", 1)[1]) / 1_000_000
                except ValueError:
                    continue
                try:
                    progress_callback(max(0.0, min(1.0, current_seconds / total_duration_seconds)), current_seconds)
                except Exception as exc:
                    if isinstance(exc, LiveStreamStoppedError) or _is_terminal_live_stream_conflict(exc):
                        callback_error = exc
                        _stop_process(process)
                        break
                    print(f"[live] progress callback failed: {exc}", flush=True)
    finally:
        if process.poll() is None:
            try:
                return_code = process.wait(timeout=5.0)
            except subprocess.TimeoutExpired:
                _stop_process(process)
                return_code = process.wait(timeout=5.0)
        else:
            return_code = process.wait()
    if callback_error is not None:
        raise callback_error
    if terminated_for_end_time:
        return
    if return_code != 0:
        tail = "\n".join(output_lines[-40:])
        raise RuntimeError(f"FFmpeg live runtime failed ({return_code}).\n{tail}".strip())


def _prepare_rendered_media(
    config: WorkerConfig,
    *,
    video_path: Path,
    audio_path: Path | None,
    render_dir: Path,
    report_progress,
    lifecycle_guard=None,
) -> Path:
    render_dir.mkdir(parents=True, exist_ok=True)
    rendered_path = render_dir / "rendered.flv"
    video_info = probe_media(config.ffprobe_bin, video_path)
    video_duration = max(1.0, float(video_info.duration_seconds or 1.0))
    total_duration = video_duration

    def _on_progress(ratio: float, _current_seconds: float) -> None:
        report_progress(
            "preparing",
            max(0, min(100, int(ratio * 100))),
            "Đang chuẩn bị luồng RTMP",
        )

    if audio_path is not None:
        audio_info = probe_media(config.ffprobe_bin, audio_path)
        total_duration = max(1.0, float(audio_info.duration_seconds or video_duration))
        arguments = [
            "-y",
            "-stream_loop",
            "-1",
            "-i",
            str(video_path),
            "-i",
            str(audio_path),
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-c",
            "copy",
            "-shortest",
            "-f",
            "flv",
            str(rendered_path),
        ]
    else:
        arguments = [
            "-y",
            "-i",
            str(video_path),
            "-c",
            "copy",
            "-shortest",
            "-f",
            "flv",
            str(rendered_path),
        ]

    report_progress("preparing", 0, "Bắt đầu ghép media", force=True)
    _run_ffmpeg_with_progress(
        config,
        arguments,
        working_dir=render_dir,
        total_duration_seconds=total_duration,
        progress_callback=_on_progress,
        lifecycle_guard=lifecycle_guard,
    )
    report_progress("preparing", 100, "Đã chuẩn bị xong luồng", force=True)
    return rendered_path


def _wait_until_start(stream: dict, report_progress, *, lifecycle_guard=None) -> None:
    start_time_live = _parse_control_plane_datetime(stream.get("start_time_live"))
    if start_time_live is None:
        return

    waiting_message = f"Chờ tới giờ live {start_time_live:%d/%m/%Y %H:%M}"
    report_progress("waiting", 100, waiting_message, force=True)

    while True:
        if lifecycle_guard:
            lifecycle_guard(force=True)
        now = _now_local()
        diff = start_time_live - now
        remaining_seconds = diff.total_seconds()
        if remaining_seconds <= 0:
            break

        report_progress("waiting", 100, waiting_message)
        if remaining_seconds > 300:
            sleep_seconds = 15.0
        elif remaining_seconds > 60:
            sleep_seconds = 5.0
        elif remaining_seconds > 15:
            sleep_seconds = 1.0
        elif remaining_seconds > 5:
            sleep_seconds = 0.5
        elif remaining_seconds > 1:
            sleep_seconds = 0.2
        else:
            sleep_seconds = 0.05
        time.sleep(min(sleep_seconds, remaining_seconds))


def _stream_once(
    client: httpx.Client,
    config: WorkerConfig,
    *,
    stream_id: str,
    rendered_path: Path,
    rendered_duration: float,
    rtmp_target: str,
    report_progress,
    end_time_live: datetime | None,
    lifecycle_guard=None,
) -> None:
    def _on_progress(ratio: float, current_seconds: float) -> None:
        report_progress(
            "streaming",
            max(0, min(100, int(ratio * 100))),
            f"Đang live {time.strftime('%H:%M:%S', time.gmtime(max(0, int(current_seconds))))}",
        )

    _run_ffmpeg_with_progress(
        config,
        [
            "-re",
            "-f",
            "flv",
            "-i",
            str(rendered_path),
            "-vf",
            "scale=trunc(iw/2)*2:trunc(ih/2)*2,format=yuv420p",
            "-c:v",
            "libx264",
            "-preset",
            LIVE_TARGET_X264_PRESET,
            "-b:v",
            f"{LIVE_TARGET_VIDEO_BITRATE_KBPS}k",
            "-maxrate",
            f"{LIVE_TARGET_MAXRATE_KBPS}k",
            "-bufsize",
            f"{LIVE_TARGET_BUFSIZE_KBPS}k",
            "-g",
            "60",
            "-keyint_min",
            "60",
            "-sc_threshold",
            "0",
            "-c:a",
            "aac",
            "-b:a",
            f"{LIVE_TARGET_AUDIO_BITRATE_KBPS}k",
            "-ar",
            "48000",
            "-f",
            "flv",
            "-flvflags",
            "no_duration_filesize",
            rtmp_target,
        ],
        working_dir=rendered_path.parent,
        total_duration_seconds=rendered_duration,
        progress_callback=_on_progress,
        end_time_live=end_time_live,
        lifecycle_guard=lifecycle_guard,
    )
    update_live_stream_progress(
        client,
        config,
        stream_id,
        status="streaming",
        progress=100,
        message="Đã phát xong 1 vòng media",
    )


def run_live_stream(client: httpx.Client, config: WorkerConfig, stream: dict) -> None:
    stream_id = str(stream["id"])
    live_root = config.work_root / "live-streams"
    work_dir = live_root / stream_id
    downloads_dir = work_dir / "downloads"
    render_dir = work_dir / "render"
    activity_path = work_dir / "activity.touch"
    rendered_path: Path | None = None
    live_root.mkdir(parents=True, exist_ok=True)
    if work_dir.exists():
        shutil.rmtree(work_dir, ignore_errors=True)
    downloads_dir.mkdir(parents=True, exist_ok=True)
    report_progress = _make_progress_reporter(client, config, stream_id, activity_path=activity_path)
    lifecycle_guard = _make_live_runtime_guard(client, config, stream_id)
    _touch_activity(activity_path)

    try:
        lifecycle_guard(force=True)
        video_path, audio_path = _download_live_assets(
            stream,
            downloads_dir,
            report_progress,
            lifecycle_guard=lifecycle_guard,
        )
        rendered_path = _prepare_rendered_media(
            config,
            video_path=video_path,
            audio_path=audio_path,
            render_dir=render_dir,
            report_progress=report_progress,
            lifecycle_guard=lifecycle_guard,
        )
        shutil.rmtree(downloads_dir, ignore_errors=True)

        _wait_until_start(stream, report_progress, lifecycle_guard=lifecycle_guard)

        lifecycle_guard(force=True)
        rendered_info = probe_media(config.ffprobe_bin, rendered_path)
        rendered_duration = max(1.0, float(rendered_info.duration_seconds or 1.0))
        end_time_live = _parse_control_plane_datetime(stream.get("end_time_live"))
        target = _rtmp_target(stream)

        report_progress("streaming", 0, "Bắt đầu đẩy RTMP", force=True)
        while True:
            if end_time_live and _now_local() >= end_time_live:
                break
            _stream_once(
                client,
                config,
                stream_id=stream_id,
                rendered_path=rendered_path,
                rendered_duration=rendered_duration,
                rtmp_target=target,
                report_progress=report_progress,
                end_time_live=end_time_live,
                lifecycle_guard=lifecycle_guard,
            )
            if end_time_live and _now_local() >= end_time_live:
                break
        complete_live_stream(client, config, stream_id, message="Luồng live đã kết thúc theo lịch.")
    finally:
        if not config.keep_job_dirs and work_dir.exists():
            shutil.rmtree(work_dir, ignore_errors=True)


def simulate_live_stream(client: httpx.Client, config: WorkerConfig, stream: dict) -> None:
    stream_id = str(stream["id"])
    phases = [
        ("downloading", [10, 40, 70, 100], "Đang tải media"),
        ("preparing", [10, 45, 80, 100], "Đang chuẩn bị luồng"),
        ("waiting", [100], "Chờ đến giờ live"),
        ("streaming", [10, 45, 80, 100], "Đang live"),
    ]
    for status, values, message in phases:
        for value in values:
            update_live_stream_progress(
                client,
                config,
                stream_id,
                status=status,
                progress=value,
                message=message,
            )
            time.sleep(config.simulate_step_seconds)
    complete_live_stream(client, config, stream_id, message="Luồng live demo đã kết thúc.")
