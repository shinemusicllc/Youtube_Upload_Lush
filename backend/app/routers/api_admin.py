from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from ..auth import normalize_manager_filter_ids, require_admin_access, require_admin_only
from ..store import store

router = APIRouter(tags=["admin"])


class AdminUserCreatePayload(BaseModel):
    username: str
    password: str
    display_name: str | None = None
    manager_id: str | None = None


class AdminUserUpdatePayload(BaseModel):
    display_name: str
    telegram: str | None = None
    manager_id: str | None = None


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
    manager_id: str | None = None
    user_id: str | None = None


class AdminBotAssignPayload(BaseModel):
    worker_ids: list[str]
    manager_id: str | None = None
    user_id: str | None = None


class AdminBotThreadPayload(BaseModel):
    thread: int


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


@router.get("/admin/session")
async def get_admin_session(request: Request):
    return {"current_user": _current_user_payload(request)}


@router.post("/admin/session/manager-filter")
async def update_admin_manager_filter(request: Request, payload: ManagerFilterPayload):
    manager_ids = _manager_ids_from_request(request, payload.manager_ids)
    return {"manager_ids": manager_ids}


@router.get("/admin/dashboard")
async def get_admin_dashboard(request: Request):
    _manager_ids_from_request(request, [])
    return store.get_admin_dashboard()


@router.get("/admin/users")
async def get_admin_users(request: Request, manager_ids: list[str] | None = None):
    selected_manager_ids = _manager_ids_from_request(request, manager_ids)
    return {"items": store._build_user_rows(selected_manager_ids)}


@router.get("/admin/users/{user_id}")
async def get_admin_user_detail(request: Request, user_id: str):
    _enforce_user_scope(request, user_id)
    return store.get_admin_user_edit_context(user_id=user_id)


@router.post("/admin/users")
async def create_admin_user(request: Request, payload: AdminUserCreatePayload):
    current_user = require_admin_access(request)
    manager_id = current_user.id if current_user.role == "manager" else payload.manager_id
    result = store.create_admin_user(
        username=payload.username,
        display_name=(payload.display_name or payload.username),
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
    store.update_admin_user(
        user_id=user_id,
        display_name=payload.display_name,
        telegram=payload.telegram,
        manager_id=manager_id,
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
    return store.get_admin_user_bot_context(user_id=user_id)


@router.post("/admin/users/{user_id}/bots")
async def create_admin_user_bot(request: Request, user_id: str, payload: AdminUserBotPayload):
    _enforce_user_scope(request, user_id)
    store.add_user_bot(user_id, payload.worker_id, payload.threads, bot_type=payload.bot_type)
    store._save_state()
    return {"ok": True}


@router.put("/admin/users/{user_id}/bots/{assignment_id}")
async def update_admin_user_bot(request: Request, user_id: str, assignment_id: int, payload: AdminUserBotUpdatePayload):
    _enforce_user_scope(request, user_id)
    store.update_user_bot(assignment_id, payload.threads, bot_type=payload.bot_type)
    store._save_state()
    return {"ok": True}


@router.delete("/admin/users/{user_id}/bots/{assignment_id}")
async def delete_admin_user_bot(request: Request, user_id: str, assignment_id: int):
    _enforce_user_scope(request, user_id)
    store.delete_user_bot(assignment_id)
    store._save_state()
    return {"ok": True}


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
async def get_admin_bots(request: Request, manager_ids: list[str] | None = None, userId: str | None = None):
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
    return {
        "items": store.get_admin_bot_index_context(
            manager_ids=selected_manager_ids,
            viewer_role=current_user.role,
            viewer_id=current_user.id,
        ).get("workers", [])
    }


@router.get("/admin/workers")
async def get_admin_workers_legacy(request: Request, manager_ids: list[str] | None = None):
    return await get_admin_bots(request, manager_ids)


@router.put("/admin/bots/{bot_id}")
async def update_admin_bot(request: Request, bot_id: str, payload: AdminBotUpdatePayload):
    current_user = require_admin_access(request)
    manager_id = current_user.id if current_user.role == "manager" else payload.manager_id
    store.update_bot(bot_id, payload.name, manager_id, assigned_user_id=payload.user_id, updated_by=current_user.username)
    return {"ok": True}


@router.post("/admin/bots/assign")
async def assign_admin_bots(request: Request, payload: AdminBotAssignPayload):
    current_user = require_admin_access(request)
    manager_id = current_user.id if current_user.role == "manager" else payload.manager_id
    if payload.user_id:
        _enforce_user_scope(request, payload.user_id)
    assigned_count = store.assign_available_bots(
        payload.worker_ids,
        manager_id=manager_id,
        assigned_user_id=payload.user_id,
        updated_by=current_user.username,
    )
    return {"ok": True, "assigned_count": assigned_count}


@router.post("/admin/bots/{bot_id}/threads")
async def update_admin_bot_threads(request: Request, bot_id: str, payload: AdminBotThreadPayload):
    require_admin_access(request)
    store.update_bot_thread(bot_id, 1)
    return {
        "ok": True,
        "thread": 1,
        "locked": True,
        "message": "Luồng BOT đang được khóa cố định 1 job active / VPS.",
    }


@router.delete("/admin/bots/{bot_id}")
async def delete_admin_bot(request: Request, bot_id: str):
    require_admin_access(request)
    store.delete_bot(bot_id)
    return {"ok": True}


@router.get("/admin/bots/of-user/{user_id}")
async def get_admin_bots_of_user(request: Request, user_id: str):
    _enforce_user_scope(request, user_id)
    return store.get_admin_bots_of_user_context(user_id=user_id)


@router.get("/admin/bots/{bot_id}/users")
async def get_admin_users_of_bot(request: Request, bot_id: str):
    require_admin_access(request)
    return store.get_admin_users_of_bot_context(worker_id=bot_id)


@router.get("/admin/channels")
async def get_admin_channels(
    request: Request,
    manager_ids: list[str] | None = None,
    user_id: str | None = None,
    bot_id: str | None = None,
):
    selected_manager_ids = _manager_ids_from_request(request, manager_ids)
    return store.get_admin_channel_index_context(manager_ids=selected_manager_ids, user_id=user_id, bot_id=bot_id)


@router.get("/admin/channels/of-user/{user_id}")
async def get_admin_channels_of_user(request: Request, user_id: str):
    _enforce_user_scope(request, user_id)
    return store.get_admin_channels_of_user_context(user_id=user_id)


@router.get("/admin/channels/of-bot/{bot_id}")
async def get_admin_channels_of_bot(request: Request, bot_id: str):
    require_admin_access(request)
    return store.get_admin_channel_index_context(bot_id=bot_id)


@router.get("/admin/channels/{channel_id}/users")
async def get_admin_channel_users(request: Request, channel_id: str):
    require_admin_access(request)
    return store.get_admin_users_of_channel_context(channel_id=channel_id)


@router.post("/admin/channels/{channel_id}/users")
async def update_admin_channel_user(request: Request, channel_id: str, payload: dict[str, str]):
    user_id = str(payload.get("user_id") or "").strip()
    if not user_id:
        raise HTTPException(status_code=422, detail="user_id la bat buoc.")
    _enforce_user_scope(request, user_id)
    action = store.update_user_channel(user_id, channel_id)
    return {"ok": True, "action": action}


@router.patch("/admin/channels/{channel_id}/profile")
async def update_admin_channel_profile(request: Request, channel_id: str):
    require_admin_access(request)
    store.update_channel_profile(channel_id)
    return {"ok": True}


@router.delete("/admin/channels/{channel_id}")
async def delete_admin_channel(request: Request, channel_id: str):
    require_admin_access(request)
    store.delete_channel(channel_id)
    return {"ok": True}


@router.get("/admin/renders")
async def get_admin_renders(request: Request, manager_ids: list[str] | None = None):
    selected_manager_ids = _manager_ids_from_request(request, manager_ids)
    return store.get_admin_render_index_context(manager_ids=selected_manager_ids)


@router.get("/admin/jobs")
async def get_admin_jobs_legacy(request: Request, manager_ids: list[str] | None = None):
    return await get_admin_renders(request, manager_ids)


@router.get("/admin/renders/of-channel/{channel_id}")
async def get_admin_renders_of_channel(request: Request, channel_id: str, manager_ids: list[str] | None = None):
    selected_manager_ids = _manager_ids_from_request(request, manager_ids)
    return store.get_admin_render_index_context(manager_ids=selected_manager_ids, channel_id=channel_id)


@router.get("/admin/renders/{job_id}")
async def get_admin_render_detail(request: Request, job_id: str):
    require_admin_access(request)
    return store.get_admin_render_detail_context(job_id=job_id)


@router.delete("/admin/renders/{job_id}")
async def delete_admin_render_job(request: Request, job_id: str):
    require_admin_access(request)
    store.delete_job(job_id)
    return {"ok": True}


@router.delete("/admin/renders")
async def delete_admin_renders(request: Request):
    current_user = require_admin_access(request)
    store.delete_all_jobs(deleted_by=current_user.username)
    return {"ok": True}
