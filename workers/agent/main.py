import os
import logging
import time
from contextlib import suppress

try:
    import fcntl
except ImportError:  # pragma: no cover - Windows local dev only
    fcntl = None

import httpx

from .browser_sessions import BrowserSessionCoordinator
from .config import load_config
from .control_plane import claim_job, fail_job, heartbeat_worker, register_worker
from .job_runner import run_job
from .runtime_cleanup import cleanup_worker_runtime

logger = logging.getLogger(__name__)


def _format_job_error(exc: Exception) -> str:
    exception_name = exc.__class__.__name__
    detail = " ".join(str(exc or "").split()).strip(" :\n\t")
    if detail and detail.lower() not in {"message", exception_name.lower()}:
        if exception_name == "RuntimeError":
            return detail
        return f"{exception_name}: {detail}"
    return f"{exception_name}: Worker job failed."


def simulate_job(client: httpx.Client, config, job: dict) -> None:
    from .control_plane import complete_job, update_job_progress

    job_id = str(job["id"])
    steps = [
        ("downloading", [5, 30, 60, 100]),
        ("rendering", [8, 25, 50, 75, 100]),
        ("uploading", [10, 40, 70, 100]),
    ]
    for status, values in steps:
        for value in values:
            heartbeat_worker(client, config, active_job_ids=[job_id])
            update_job_progress(client, config, job_id, status=status, progress=value)
            time.sleep(config.simulate_step_seconds)
    output_url = f"https://youtube.example/{job_id}"
    complete_job(client, config, job_id, output_url=output_url)


def _acquire_single_instance_lock(config):
    lock_path = config.work_root / ".worker-agent.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    handle = lock_path.open("a+", encoding="utf-8")
    if fcntl is None:
        return handle
    try:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError as exc:
        handle.close()
        raise RuntimeError(f"Worker agent da ton tai process khac tren VPS nay ({lock_path}).") from exc
    handle.seek(0)
    handle.truncate()
    handle.write(str(os.getpid()))
    handle.flush()
    return handle


def main() -> None:
    config = load_config()
    browser_sessions = BrowserSessionCoordinator(config)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )
    if config.single_job_only:
        logger.info("worker single-job mode enabled for %s", config.worker_id)
    lock_handle = _acquire_single_instance_lock(config)
    try:
        with httpx.Client(base_url=config.control_plane_url, timeout=20.0) as client:
            while True:
                try:
                    register_worker(client, config)
                    break
                except Exception as exc:
                    logger.warning("register_worker failed: %s", exc)
                    time.sleep(config.poll_seconds)
            last_heartbeat_at = 0.0
            last_cleanup_at = 0.0
            while True:
                now = time.monotonic()
                if now - last_heartbeat_at >= config.heartbeat_seconds:
                    try:
                        heartbeat_worker(client, config, active_job_ids=[])
                        last_heartbeat_at = now
                    except Exception as exc:
                        logger.warning("heartbeat_worker failed: %s", exc)
                        time.sleep(config.poll_seconds)
                        continue

                if now - last_cleanup_at >= config.runtime_cleanup_interval_seconds:
                    try:
                        cleanup_summary = cleanup_worker_runtime(config)
                        if cleanup_summary.changed:
                            logger.info(
                                "runtime cleanup removed job_dirs=%s output_files=%s",
                                cleanup_summary.deleted_job_dirs,
                                cleanup_summary.deleted_output_files,
                            )
                        last_cleanup_at = now
                    except Exception as exc:
                        logger.warning("cleanup_worker_runtime failed: %s", exc)

                if config.browser_session_enabled:
                    try:
                        browser_sessions.reconcile(client)
                    except Exception as exc:
                        logger.warning("browser_sessions.reconcile failed: %s", exc)

                if not config.simulate_jobs and not config.execute_jobs:
                    time.sleep(config.poll_seconds)
                    continue

                try:
                    job = claim_job(client, config)
                except Exception as exc:
                    logger.warning("claim_job failed: %s", exc)
                    time.sleep(config.poll_seconds)
                    continue
                if not job:
                    time.sleep(config.poll_seconds)
                    continue

                try:
                    if config.simulate_jobs:
                        simulate_job(client, config, job)
                    else:
                        run_job(client, config, job)
                except Exception as exc:
                    try:
                        fail_job(client, config, str(job["id"]), message=_format_job_error(exc))
                    except Exception as fail_exc:
                        logger.warning("fail_job failed for %s: %s", job.get("id"), fail_exc)
                    time.sleep(config.poll_seconds)
    finally:
        with suppress(Exception):
            if fcntl is not None:
                fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)
        with suppress(Exception):
            lock_handle.close()


if __name__ == "__main__":
    main()
