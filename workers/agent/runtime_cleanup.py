from __future__ import annotations

import shutil
import time
from dataclasses import dataclass
from pathlib import Path

from .config import WorkerConfig


@dataclass
class RuntimeCleanupSummary:
    deleted_job_dirs: list[str]
    deleted_output_files: list[str]

    @property
    def changed(self) -> bool:
        return bool(self.deleted_job_dirs or self.deleted_output_files)


def _is_stale(path: Path, *, max_age_seconds: int, now: float) -> bool:
    if max_age_seconds <= 0:
        return False
    try:
        modified_at = path.stat().st_mtime
    except OSError:
        return False
    return (now - modified_at) >= max_age_seconds


def _cleanup_stale_job_dirs(work_root: Path, *, stale_after_seconds: int, now: float) -> list[str]:
    deleted: list[str] = []
    for path in sorted(work_root.glob("job-*")):
        if not path.is_dir():
            continue
        if not _is_stale(path, max_age_seconds=stale_after_seconds, now=now):
            continue
        shutil.rmtree(path, ignore_errors=True)
        deleted.append(path.name)
    return deleted


def _cleanup_stale_output_files(outputs_dir: Path, *, stale_after_seconds: int, now: float) -> list[str]:
    deleted: list[str] = []
    if not outputs_dir.exists():
        return deleted
    for path in sorted(outputs_dir.glob("job-*")):
        if not path.is_file():
            continue
        if not _is_stale(path, max_age_seconds=stale_after_seconds, now=now):
            continue
        path.unlink(missing_ok=True)
        deleted.append(path.name)
    return deleted


def cleanup_worker_runtime(config: WorkerConfig) -> RuntimeCleanupSummary:
    if config.keep_job_dirs or not config.runtime_cleanup_enabled:
        return RuntimeCleanupSummary(deleted_job_dirs=[], deleted_output_files=[])

    now = time.time()
    work_root = config.work_root
    outputs_dir = work_root / "outputs"

    deleted_job_dirs = _cleanup_stale_job_dirs(
        work_root,
        stale_after_seconds=config.stale_job_dir_seconds,
        now=now,
    )
    deleted_output_files = _cleanup_stale_output_files(
        outputs_dir,
        stale_after_seconds=config.stale_output_seconds,
        now=now,
    )
    return RuntimeCleanupSummary(
        deleted_job_dirs=deleted_job_dirs,
        deleted_output_files=deleted_output_files,
    )
