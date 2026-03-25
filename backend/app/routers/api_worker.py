from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..schemas import (
    WorkerAuthPayload,
    WorkerHeartbeatPayload,
    WorkerJobCompletePayload,
    WorkerJobFailPayload,
    WorkerJobProgressPayload,
    WorkerRegisterPayload,
)
from ..store import store

router = APIRouter(tags=["worker"])


@router.post("/workers/register")
async def register_worker(payload: WorkerRegisterPayload):
    try:
        return store.register_worker(payload)
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.post("/workers/heartbeat")
async def heartbeat_worker(payload: WorkerHeartbeatPayload):
    try:
        return store.heartbeat_worker(payload)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Worker chưa được đăng ký.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.post("/workers/claim")
async def claim_worker_job(payload: WorkerAuthPayload):
    try:
        worker, job = store.claim_next_job(payload.worker_id, payload.shared_secret)
        return {"ok": True, "worker": worker.model_dump(mode="json"), "job": job.model_dump(mode="json") if job else None}
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Worker chưa được đăng ký.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.post("/workers/jobs/{job_id}/progress")
async def update_worker_job_progress(job_id: str, payload: WorkerJobProgressPayload):
    try:
        return store.update_worker_job_progress(
            job_id=job_id,
            worker_id=payload.worker_id,
            shared_secret=payload.shared_secret,
            status=payload.status,
            progress=payload.progress,
            message=payload.message,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Không tìm thấy job.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/workers/jobs/{job_id}/complete")
async def complete_worker_job(job_id: str, payload: WorkerJobCompletePayload):
    try:
        return store.complete_worker_job(
            job_id=job_id,
            worker_id=payload.worker_id,
            shared_secret=payload.shared_secret,
            output_url=payload.output_url,
            message=payload.message,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Không tìm thấy job.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/workers/jobs/{job_id}/fail")
async def fail_worker_job(job_id: str, payload: WorkerJobFailPayload):
    try:
        return store.fail_worker_job(
            job_id=job_id,
            worker_id=payload.worker_id,
            shared_secret=payload.shared_secret,
            message=payload.message,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Không tìm thấy job.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
