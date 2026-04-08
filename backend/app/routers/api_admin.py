from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from ..auth import normalize_manager_filter_ids, require_admin_access, require_admin_only
from ..store import store
from ..worker_bootstrap import (
    WorkerBootstrapError,
    build_worker_bootstrap_request,
    build_worker_decommission_request,
    start_worker_decommission_operation,
    start_worker_install_operation,
)

router = APIRouter(tags=["admin"])


class AdminUserCreatePayload(BaseModel):
    username: str
    password: str
    manager_id: str | None = None


class AdminUserUpdatePayload(BaseModel):
    username: str
    password: str | None = None
    manager_id: str | None = None
    telegram: str | None = None


class AdminResetPasswordPayload(BaseModel):
    password: str


class AdminUserBotPayload(BaseModel):
    worker_id: str
    threads: int = 1
    bot_type: str = "1080p"


class AdminUserBotUpdatePayload(BaseModel):
    threads: int = 1
    bot_type: str | None = None


class AdminBotUpdatePayload(BaseModel):
    name: str
    group: str | None = None
    manager_id: str | None = None
    assigned_user_id: str | None = None
    assigned_user_ids: list[str] | None = None
    confirm_manager_transfer_cleanup: bool = False


class AdminBotThreadPayload(BaseModel):
    thread: int


class AdminBotInstallPayload(BaseModel):
    vps_ip: str
    ssh_user: str = "root"
    auth_mode: str = "password"
    password: str | None = None
    ssh_private_key: str | None = None


class AdminBotDecommissionPayload(BaseModel):
    ssh_user: str = "root"
    auth_mode: str = "password"
    password: str | None = None
    ssh_private_key: str | None = None


class ManagerFilterPayload(BaseModel):
    manager_ids: list[str] = []


def _manager_ids_from_request(request: Request, manager_ids: list[str] | None = None) -> list[str]:
    current_user = require_admin_access(request)
    available_ids = [user.id for user in store.users if user.role == "manager"]
    return normalize_manager_filter_ids(request, manager_ids or [], available_ids, current_user)


def _current_user_payload(request: Request) -> dict[str, Any]:
    current_user = require_admin_access(request)
    return {
        "id": current_user.id,
        "username": current_user.username,
        "display_name": current_user.display_name,
        "role": current_user.role,
        "manager_name": current_user.manager_name,
        "manager_filter_ids": request.session.get("admin_manager_ids") or [],
    }


def _enforce_user_scope(request: Request, user_id: str) -> None:
    current_user = require_admin_access(request)
    if current_user.role != "manager":
        return
    user = store._find_user(user_id)
    if user.role == "admin":
        raise HTTPException(status_code=403, detail="Manager khong duoc thao tac admin.")
    if user.role == "manager" and user.id != current_user.id:
        raise HTTPException(status_code=403, detail="Khong du quyen thao tac manager nay.")
    if user.role == "user" and user.manager_name != current_user.username:
        raise HTTPException(status_code=403, detail="Khong du quyen thao tac user khac manager.")


def _enforce_worker_scope(request: Request, worker_id: str) -> None:
    current_user = require_admin_access(request)
    if current_user.role != "manager":
        return
    worker = store._find_worker(worker_id)
    if worker.manager_id != current_user.id:
        raise HTTPException(status_code=403, detail="Khong du quyen thao tac BOT ngoai scope manager.")


def _enforce_channel_scope(request: Request, channel_id: str) -> None:
    current_user = require_admin_access(request)
    if current_user.role != "manager":
        return
    channel = store._find_channel(channel_id)
    if store._resolve_channel_manager_id(channel) != current_user.id:
        raise HTTPException(status_code=403, detail="Khong du quyen thao tac kenh ngoai scope manager.")


def _enforce_job_scope(request: Request, job_id: str) -> None:
    current_user = require_admin_access(request)
    if current_user.role != "manager":
        return
    job = store._find_job(job_id)
    if store._resolve_job_manager_id(job) != current_user.id:
        raise HTTPException(status_code=403, detail="Khong du quyen thao tac job ngoai scope manager.")


def _enforce_user_bot_mapping_scope(request: Request, user_id: str, assignment_id: int) -> None:
    _enforce_user_scope(request, user_id)
    mapping = next((item for item in store.user_worker_links if int(item.get("id") or 0) == assignment_id), None)
    if mapping is None or str(mapping.get("user_id") or "").strip() != user_id:
        raise HTTPException(status_code=403, detail="Khong du quyen thao tac mapping BOT nay.")


def _scoped_job_ids(request: Request, *, channel_id: str | None = None) -> list[str]:
    current_user = require_admin_access(request)
    jobs = list(store.jobs)
    if current_user.role == "manager":
        jobs = [job for job in jobs if store._resolve_job_manager_id(job) == current_user.id]
    if channel_id:
        jobs = [job for job in jobs if job.channel_id == channel_id]
    return [job.id for job in jobs]


@router.get("/admin/session")
async def get_admin_session(request: Request):
    return {"current_user": _current_user_payload(request)}


@router.post("/admin/session/manager-filter")
async def update_admin_manager_filter(request: Request, payload: ManagerFilterPayload):
    manager_ids = _manager_ids_from_request(request, payload.manager_ids)
    return {"manager_ids": manager_ids}


@router.get("/admin/dashboard")
async def get_admin_dashboard(request: Request):
    current_user = require_admin_access(request)
    selected_manager_ids = _manager_ids_from_request(request, [])
    effective_manager_ids = store._effective_manager_scope_ids(
        viewer_role=current_user.role,
        viewer_id=current_user.id,
        manager_ids=selected_manager_ids,
    )
    scoped_users = store._build_user_rows(
        effective_manager_ids,
        viewer_role=current_user.role,
        viewer_id=current_user.id,
    )
    workers = [
        row
        for row in store.get_admin_bot_index_context(
            manager_ids=effective_manager_ids,
            viewer_role=current_user.role,
            viewer_id=current_user.id,
        ).get("workers", [])
    ]
    channels = store.get_admin_channel_index_context(
        manager_ids=effective_manager_ids,
        viewer_role=current_user.role,
        viewer_id=current_user.id,
    ).get("channels", [])
    renders = store.get_admin_render_index_context(
        manager_ids=effective_manager_ids,
        viewer_role=current_user.role,
        viewer_id=current_user.id,
    ).get("renders", [])
    return {
        "summary": store._scoped_admin_summary(
            viewer_role=current_user.role,
            viewer_id=current_user.id,
            manager_ids=effective_manager_ids,
        ),
        "users": scoped_users,
        "workers": workers,
        "channels": channels,
        "jobs": renders,
    }


@router.get("/admin/users")
async def get_admin_users(request: Request, manager_ids: list[str] | None = None):
    selected_manager_ids = _manager_ids_from_request(request, manager_ids)
    current_user = require_admin_access(request)
    return {"items": store._build_user_rows(selected_manager_ids, viewer_role=current_user.role, viewer_id=current_user.id)}


@router.get("/admin/users/{user_id}")
async def get_admin_user_detail(request: Request, user_id: str):
    _enforce_user_scope(request, user_id)
    current_user = require_admin_access(request)
    return store.get_admin_user_edit_context(user_id=user_id, viewer_role=current_user.role, viewer_id=current_user.id)


@router.post("/admin/users")
async def create_admin_user(request: Request, payload: AdminUserCreatePayload):
    current_user = require_admin_access(request)
    manager_id = current_user.id if current_user.role == "manager" else payload.manager_id
    if manager_id == "__bot_empty__":
        manager_id = None
    result = store.create_admin_user(
        username=payload.username,
        display_name=payload.username,
        password=payload.password,
        role="user",
        manager_id=manager_id,
        telegram=None,
        updated_by=current_user.username,
    )
    return result


@router.put("/admin/users/{user_id}")
async def update_admin_user(request: Request, user_id: str, payload: AdminUserUpdatePayload):
    current_user = require_admin_access(request)
    _enforce_user_scope(request, user_id)
    manager_id = current_user.id if current_user.role == "manager" else payload.manager_id
    payload_fields = getattr(payload, "model_fields_set", getattr(payload, "__fields_set__", set()))
    telegram = payload.telegram if "telegram" in payload_fields else None
    store.update_admin_user(
        user_id=user_id,
        username=payload.username,
        password=payload.password,
        manager_id=manager_id,
        telegram=telegram,
        actor_role=current_user.role,
        updated_by=current_user.username,
    )
    return {"ok": True}


@router.post("/admin/users/{user_id}/reset-password")
async def reset_admin_user_password(request: Request, user_id: str, payload: AdminResetPasswordPayload):
    current_user = require_admin_access(request)
    _enforce_user_scope(request, user_id)
    store.reset_admin_user_password(user_id, payload.password, updated_by=current_user.username)
    return {"ok": True}


@router.delete("/admin/users/{user_id}")
async def delete_admin_user(request: Request, user_id: str):
    _enforce_user_scope(request, user_id)
    store.delete_admin_user(user_id)
    return {"ok": True}


@router.get("/admin/users/{user_id}/bots")
async def get_admin_user_bots(request: Request, user_id: str):
    _enforce_user_scope(request, user_id)
    current_user = require_admin_access(request)
    return store.get_admin_user_bot_context(
        user_id=user_id,
        viewer_role=current_user.role,
        viewer_id=current_user.id,
    )


@router.post("/admin/users/{user_id}/bots")
async def create_admin_user_bot(request: Request, user_id: str, payload: AdminUserBotPayload):
    require_admin_access(request)
    raise HTTPException(status_code=410, detail="Gán BOT đã được gộp vào Danh sách BOT.")


@router.put("/admin/users/{user_id}/bots/{assignment_id}")
async def update_admin_user_bot(request: Request, user_id: str, assignment_id: int, payload: AdminUserBotUpdatePayload):
    require_admin_access(request)
    raise HTTPException(status_code=410, detail="Sửa mapping BOT đã được gộp vào Danh sách BOT.")


@router.delete("/admin/users/{user_id}/bots/{assignment_id}")
async def delete_admin_user_bot(request: Request, user_id: str, assignment_id: int):
    require_admin_access(request)
    raise HTTPException(status_code=410, detail="Xóa mapping BOT đã được gộp vào Danh sách BOT.")


@router.get("/admin/roles/managers")
async def get_admin_manager_roles(request: Request):
    require_admin_only(request)
    return store.get_admin_manager_page_context()


@router.post("/admin/roles/managers/{user_id}")
async def toggle_manager_role(request: Request, user_id: str):
    current_user = require_admin_only(request)
    user = store._find_user(user_id)
    promote = user.role != "manager"
    store.update_role_manager(user_id, promote=promote, updated_by=current_user.username)
    return {"ok": True, "promote": promote}


@router.get("/admin/roles/admins")
async def get_admin_admin_roles(request: Request):
    require_admin_only(request)
    return store.get_admin_admin_page_context()


@router.post("/admin/roles/admins/{user_id}")
async def toggle_admin_role(request: Request, user_id: str):
    current_user = require_admin_only(request)
    user = store._find_user(user_id)
    promote = user.role != "admin"
    store.update_role_admin(user_id, promote=promote, updated_by=current_user.username)
    return {"ok": True, "promote": promote}


@router.get("/admin/bots")
async def get_admin_bots(
    request: Request,
    manager_ids: list[str] | None = None,
    userId: str | None = None,
    after_event_id: str | None = None,
):
    if userId:
        _enforce_user_scope(request, userId)
    selected_manager_ids = _manager_ids_from_request(request, manager_ids)
    if not selected_manager_ids and userId:
        focus_user = store._find_user(userId)
        if focus_user.role == "manager":
            selected_manager_ids = [focus_user.id]
        else:
            resolved_manager_id = store._resolved_user_manager_id(focus_user)
            if resolved_manager_id:
                selected_manager_ids = [resolved_manager_id]
    current_user = require_admin_access(request)
    if current_user.role == "manager" and not selected_manager_ids:
        selected_manager_ids = [current_user.id]
    notifications = store.get_admin_notifications(
        manager_ids=selected_manager_ids,
        after_id=after_event_id,
    )
    return {
        "items": store.get_admin_bot_index_context(
            manager_ids=selected_manager_ids,
            viewer_role=current_user.role,
            viewer_id=current_user.id,
        ).get("workers", []),
        "events": notifications.get("items", []),
        "event_cursor": notifications.get("cursor", ""),
    }


@router.post("/admin/bots/install")
async def install_admin_bot(request: Request, payload: AdminBotInstallPayload):
    current_user = require_admin_access(request)
    manager_name = current_user.username if current_user.role == "manager" else "system"
    manager_id = current_user.id if current_user.role == "manager" else None
    worker_id = store.suggest_next_worker_bootstrap_id()
    auth_mode = str(payload.auth_mode or "password").strip().lower() or "password"
    try:
        bootstrap_request = build_worker_bootstrap_request(
            vps_ip=payload.vps_ip,
            ssh_user=payload.ssh_user,
            password=payload.password if auth_mode != "ssh_key" else None,
            ssh_private_key=payload.ssh_private_key if auth_mode == "ssh_key" else None,
            shared_secret=store.get_worker_shared_secret(),
            control_plane_url=str(request.base_url).rstrip("/"),
            worker_id=worker_id,
            manager_name=manager_name,
        )
        task = start_worker_install_operation(
            store=store,
            request=bootstrap_request,
            ssh_user=payload.ssh_user,
            auth_mode=auth_mode,
            password=payload.password if auth_mode != "ssh_key" else None,
            ssh_private_key=payload.ssh_private_key if auth_mode == "ssh_key" else None,
            manager_id=manager_id,
            manager_name=manager_name,
            requested_by=current_user.username,
            requested_role=current_user.role,
        )
        return {
            "ok": True,
            "operation_id": task["id"],
            "worker_id": task["worker_id"],
            "vps_ip": task["vps_ip"],
        }
    except (ValueError, WorkerBootstrapError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/admin/workers")
async def get_admin_workers_legacy(request: Request, manager_ids: list[str] | None = None):
    return await get_admin_bots(request, manager_ids)


@router.put("/admin/bots/{bot_id}")
async def update_admin_bot(request: Request, bot_id: str, payload: AdminBotUpdatePayload):
    current_user = require_admin_access(request)
    _enforce_worker_scope(request, bot_id)
    manager_id = current_user.id if current_user.role == "manager" else payload.manager_id
    assigned_user_id = payload.assigned_user_id
    assigned_user_ids = [str(value).strip() for value in (payload.assigned_user_ids or []) if str(value).strip()]
    existing_assigned_user_ids = set()
    if payload.assigned_user_ids is not None:
        try:
            existing_assigned_user_ids = {user.id for user in store._assigned_users_for_worker(bot_id)}
        except KeyError:
            existing_assigned_user_ids = set()
    if current_user.role == "admin" and manager_id:
        try:
            selected_owner = store._find_user(manager_id)
        except KeyError:
            selected_owner = None
        if selected_owner is None or selected_owner.role != "manager":
            assigned_user_id = None
    if assigned_user_id and not assigned_user_ids:
        _enforce_user_scope(request, assigned_user_id)
    for selected_user_id in assigned_user_ids:
        if current_user.role == "manager" and selected_user_id in existing_assigned_user_ids:
            continue
        _enforce_user_scope(request, selected_user_id)
    store.update_bot(
        bot_id,
        payload.name,
        payload.group,
        manager_id,
        assigned_user_id=assigned_user_id,
        assigned_user_ids=assigned_user_ids if payload.assigned_user_ids is not None else None,
        confirm_manager_transfer_cleanup=bool(payload.confirm_manager_transfer_cleanup),
        viewer_role=current_user.role,
        viewer_id=current_user.id,
        updated_by=current_user.username,
    )
    return {"ok": True}


@router.post("/admin/bots/assign")
async def assign_admin_bots(request: Request):
    require_admin_access(request)
    raise HTTPException(status_code=410, detail="Cấp phát BOT đã được gộp vào Danh sách BOT.")


@router.post("/admin/bots/{bot_id}/threads")
async def update_admin_bot_threads(request: Request, bot_id: str, payload: AdminBotThreadPayload):
    require_admin_access(request)
    raise HTTPException(status_code=410, detail="Thiết lập luồng BOT cũ đã được bỏ khỏi UI điều phối hiện tại.")


@router.delete("/admin/bots/{bot_id}")
async def delete_admin_bot(request: Request, bot_id: str, payload: AdminBotDecommissionPayload):
    _enforce_worker_scope(request, bot_id)
    try:
        current_user = require_admin_access(request)
        worker = next((item for item in store.workers if item.id == bot_id), None)
        if worker is None:
            raise KeyError(bot_id)
        connection_profile: dict[str, object] | None = None
        try:
            connection_profile = store.get_worker_connection_profile(bot_id)
        except (KeyError, ValueError):
            connection_profile = None
        has_saved_credential = bool(
            connection_profile
            and (
                str(connection_profile.get("password") or "").strip()
                or str(connection_profile.get("ssh_private_key") or "").strip()
            )
        )
        if connection_profile and has_saved_credential:
            resolved_auth_mode = str(connection_profile.get("auth_mode") or payload.auth_mode or "password").strip().lower() or "password"
            decommission_request = build_worker_decommission_request(
                vps_ip=str(connection_profile.get("vps_ip") or "").strip(),
                ssh_user=str(connection_profile.get("ssh_user") or payload.ssh_user or "root").strip() or "root",
                password=(str(connection_profile.get("password") or "").strip() or None) if resolved_auth_mode != "ssh_key" else None,
                ssh_private_key=(str(connection_profile.get("ssh_private_key") or "").strip() or None) if resolved_auth_mode == "ssh_key" else None,
            )
            task = start_worker_decommission_operation(
                store=store,
                worker_id=bot_id,
                request=decommission_request,
                ssh_user=str(connection_profile.get("ssh_user") or payload.ssh_user or "root").strip() or "root",
                requested_by=current_user.username,
                requested_role=current_user.role,
            )
            return {
                "ok": True,
                "worker_id": bot_id,
                "deleted": False,
                "operation_id": task["id"],
                "mode": "ssh",
                "message": "Da bat dau go BOT bang credential da luu.",
            }
        if str(worker.status or "").strip() == "offline":
            store.delete_bot_without_ssh(bot_id, deleted_by=current_user.username)
            return {
                "ok": True,
                "worker_id": bot_id,
                "deleted": True,
                "mode": "local",
                "message": "BOT dang offline va khong co credential da luu, nen he thong chi xoa BOT khoi control-plane.",
            }
        raise WorkerBootstrapError(
            "BOT nay chua co credential da luu de go tu dong. Hay go thu cong tren VPS hoac them lai BOT roi xoa lai."
        )
    except (KeyError, ValueError, WorkerBootstrapError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/admin/bots/of-user/{user_id}")
async def get_admin_bots_of_user(request: Request, user_id: str):
    _enforce_user_scope(request, user_id)
    current_user = require_admin_access(request)
    return store.get_admin_bots_of_user_context(
        user_id=user_id,
        viewer_role=current_user.role,
        viewer_id=current_user.id,
    )


@router.get("/admin/bots/{bot_id}/users")
async def get_admin_users_of_bot(request: Request, bot_id: str):
    _enforce_worker_scope(request, bot_id)
    current_user = require_admin_access(request)
    return store.get_admin_users_of_bot_context(
        worker_id=bot_id,
        viewer_role=current_user.role,
        viewer_id=current_user.id,
    )


@router.get("/admin/channels")
async def get_admin_channels(
    request: Request,
    manager_ids: list[str] | None = None,
    user_id: str | None = None,
    bot_id: str | None = None,
):
    selected_manager_ids = _manager_ids_from_request(request, manager_ids)
    current_user = require_admin_access(request)
    if user_id:
        _enforce_user_scope(request, user_id)
    if bot_id:
        _enforce_worker_scope(request, bot_id)
    return store.get_admin_channel_index_context(
        manager_ids=selected_manager_ids,
        user_id=user_id,
        bot_id=bot_id,
        viewer_role=current_user.role,
        viewer_id=current_user.id,
    )


@router.get("/admin/channels/of-user/{user_id}")
async def get_admin_channels_of_user(request: Request, user_id: str):
    _enforce_user_scope(request, user_id)
    current_user = require_admin_access(request)
    return store.get_admin_channels_of_user_context(
        user_id=user_id,
        viewer_role=current_user.role,
        viewer_id=current_user.id,
    )


@router.get("/admin/channels/of-bot/{bot_id}")
async def get_admin_channels_of_bot(request: Request, bot_id: str):
    current_user = require_admin_access(request)
    _enforce_worker_scope(request, bot_id)
    return store.get_admin_channel_index_context(
        bot_id=bot_id,
        manager_ids=[current_user.id] if current_user.role == "manager" else None,
        viewer_role=current_user.role,
        viewer_id=current_user.id,
    )


@router.get("/admin/channels/{channel_id}/users")
async def get_admin_channel_users(request: Request, channel_id: str):
    current_user = require_admin_access(request)
    _enforce_channel_scope(request, channel_id)
    return store.get_admin_users_of_channel_context(
        channel_id=channel_id,
        viewer_role=current_user.role,
        viewer_id=current_user.id,
    )


@router.post("/admin/channels/{channel_id}/users")
async def update_admin_channel_user(request: Request, channel_id: str, payload: dict[str, str]):
    user_id = str(payload.get("user_id") or "").strip()
    if not user_id:
        raise HTTPException(status_code=422, detail="user_id la bat buoc.")
    _enforce_channel_scope(request, channel_id)
    _enforce_user_scope(request, user_id)
    action = store.update_user_channel(user_id, channel_id)
    return {"ok": True, "action": action}


@router.patch("/admin/channels/{channel_id}/profile")
async def update_admin_channel_profile(request: Request, channel_id: str):
    _enforce_channel_scope(request, channel_id)
    store.update_channel_profile(channel_id)
    return {"ok": True}


@router.delete("/admin/channels/{channel_id}")
async def delete_admin_channel(request: Request, channel_id: str):
    _enforce_channel_scope(request, channel_id)
    store.delete_channel(channel_id)
    return {"ok": True}


@router.get("/admin/renders")
async def get_admin_renders(request: Request, manager_ids: list[str] | None = None):
    selected_manager_ids = _manager_ids_from_request(request, manager_ids)
    current_user = require_admin_access(request)
    return store.get_admin_render_index_context(
        manager_ids=selected_manager_ids,
        viewer_role=current_user.role,
        viewer_id=current_user.id,
    )


@router.get("/admin/jobs")
async def get_admin_jobs_legacy(request: Request, manager_ids: list[str] | None = None):
    return await get_admin_renders(request, manager_ids)


@router.get("/admin/renders/of-channel/{channel_id}")
async def get_admin_renders_of_channel(request: Request, channel_id: str, manager_ids: list[str] | None = None):
    selected_manager_ids = _manager_ids_from_request(request, manager_ids)
    current_user = require_admin_access(request)
    _enforce_channel_scope(request, channel_id)
    return store.get_admin_render_index_context(
        manager_ids=selected_manager_ids,
        channel_id=channel_id,
        viewer_role=current_user.role,
        viewer_id=current_user.id,
    )


@router.get("/admin/renders/{job_id}")
async def get_admin_render_detail(request: Request, job_id: str):
    current_user = require_admin_access(request)
    _enforce_job_scope(request, job_id)
    return store.get_admin_render_detail_context(
        job_id=job_id,
        viewer_role=current_user.role,
        viewer_id=current_user.id,
    )


@router.delete("/admin/renders/{job_id}")
async def delete_admin_render_job(request: Request, job_id: str):
    _enforce_job_scope(request, job_id)
    store.delete_job(job_id)
    return {"ok": True}


@router.delete("/admin/renders")
async def delete_admin_renders(request: Request, channel_id: str | None = None):
    current_user = require_admin_access(request)
    if channel_id:
        _enforce_channel_scope(request, channel_id)
    scoped_job_ids = _scoped_job_ids(request, channel_id=channel_id)
    if current_user.role == "admin" and not channel_id:
        store.delete_all_jobs(deleted_by=current_user.username)
    else:
        store.delete_jobs(scoped_job_ids)
    return {"ok": True}
