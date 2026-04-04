from __future__ import annotations

import csv
import os
from io import StringIO
from pathlib import Path
from urllib.parse import quote, urlencode

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from starlette.concurrency import run_in_threadpool

from ..auth import (
    AdminSessionUser,
    AppSessionUser,
    GOOGLE_OAUTH_STATE_SESSION_KEY,
    clear_app_session,
    clear_admin_session,
    get_app_session_user,
    get_admin_session_user,
    normalize_manager_filter_ids,
    require_admin_access,
    require_admin_only,
    set_app_session_user,
    set_admin_session_user,
)
from ..store import store
from ..worker_bootstrap import (
    WorkerBootstrapError,
    bootstrap_worker_via_ssh,
    build_worker_bootstrap_request,
    suggest_next_worker_id,
)

templates = Jinja2Templates(directory=Path(__file__).resolve().parents[1] / "templates")
router = APIRouter(tags=["web"])

PUBLIC_APP_NAME = "JazzRelaxation Upload Manager"
PUBLIC_SUPPORT_EMAIL = "hoangpear99@gmail.com"


def _admin_identity_payload(current_user: AdminSessionUser) -> dict:
    return {
        "id": current_user.id,
        "username": current_user.username,
        "name": current_user.display_name,
        "display_name": current_user.display_name,
        "role": current_user.role,
        "role_label": "Admin" if current_user.role == "admin" else "Manager",
        "role_text": "Control plane" if current_user.role == "admin" else "Manager scope",
    }


def _public_shell_payload(*, request: Request, page_title: str, active_page: str) -> dict[str, object]:
    base_url = str(request.base_url).rstrip("/")
    return {
        "request": request,
        "page_title": page_title,
        "app_name": PUBLIC_APP_NAME,
        "support_email": PUBLIC_SUPPORT_EMAIL,
        "home_url": f"{base_url}/home",
        "privacy_url": f"{base_url}/privacy-policy",
        "terms_url": f"{base_url}/terms-of-service",
        "workspace_url": f"{base_url}/login",
        "active_page": active_page,
    }


def _app_login_template_payload(
    *,
    request: Request,
    page_title: str,
    next_url: str,
    notice: str | None,
    notice_level: str,
    form_data: dict[str, str],
    form_action: str,
    login_badge: str,
    login_heading: str,
    login_description: str,
    submit_label: str,
    switch_href: str | None,
    switch_label: str | None,
    hero_context_label: str,
    hero_status_label: str,
) -> dict[str, object]:
    return {
        "request": request,
        "page_title": page_title,
        "next_url": next_url,
        "notice": notice,
        "notice_level": notice_level,
        "form_data": form_data,
        "form_action": form_action,
        "login_badge": login_badge,
        "login_heading": login_heading,
        "login_description": login_description,
        "submit_label": submit_label,
        "switch_href": switch_href,
        "switch_label": switch_label,
        "hero_context_label": hero_context_label,
        "hero_status_label": hero_status_label,
    }


def _default_home_for_role(role: str) -> str:
    return "/app" if role == "user" else "/admin/user/index"


def _resolve_login_redirect(role: str, requested_next: str | None) -> str:
    candidate = (requested_next or "").strip()
    if role == "user":
        if candidate.startswith("/app") or candidate.startswith("/auth/google"):
            return candidate
        return "/app"
    if candidate.startswith("/admin"):
        return candidate
    return "/admin/user/index"


def _render(request: Request, dashboard: dict, status_code: int = 200):
    current_user = getattr(request.state, "admin_user", None) or get_admin_session_user(request)
    if current_user:
        store.assert_admin_session_user(current_user.id, current_user.role)
        dashboard["current_user"] = _admin_identity_payload(current_user)
    return templates.TemplateResponse(
        dashboard["template"],
        {"request": request, "dashboard": dashboard},
        status_code=status_code,
    )


def _redirect_with_notice(path: str, message: str, level: str = "success", **query: str):
    payload = {"notice": message, "notice_level": level}
    payload.update({key: value for key, value in query.items() if value})
    return RedirectResponse(url=f"{path}?{urlencode(payload)}", status_code=303)


def _resolve_bot_scope_manager_ids(selected_manager_ids: list[str], focus_user_id: str | None = None) -> list[str]:
    if selected_manager_ids:
        return selected_manager_ids
    if not focus_user_id:
        return selected_manager_ids
    focus_user = store._find_user(focus_user_id)
    if focus_user.role == "manager":
        return [focus_user.id]
    resolved_manager_id = store._resolved_user_manager_id(focus_user)
    return [resolved_manager_id] if resolved_manager_id else selected_manager_ids


def _redirect_bot_page_with_scope(
    message: str,
    level: str = "success",
    *,
    manager_ids: list[str] | None = None,
    user_id: str | None = None,
    page: str = "list",
):
    base_path = "/admin/ManagerBOT/index"
    query: list[tuple[str, str]] = [("notice", message), ("notice_level", level)]
    for manager_id in manager_ids or []:
        if manager_id:
            query.append(("manager_ids", manager_id))
    if user_id:
        query.append(("userId", user_id))
    return RedirectResponse(url=f"{base_path}?{urlencode(query, doseq=True)}", status_code=303)


def _resolve_worker_bootstrap_control_plane_url(request: Request) -> str:
    configured = str(os.getenv("WORKER_BOOTSTRAP_CONTROL_PLANE_URL", "")).strip()
    if configured:
        return configured.rstrip("/")
    return str(request.base_url).rstrip("/")


def _sanitize_next_url(value: str | None, *, default_path: str) -> str:
    candidate = str(value or "").strip()
    if not candidate.startswith("/") or candidate.startswith("//"):
        return default_path
    return candidate


def _resolve_user_id(user_id: str | None = None, username: str | None = None) -> str:
    if user_id:
        return user_id
    if username:
        for user in store.users:
            if user.username == username:
                return user.id
        raise ValueError("Không tìm thấy tài khoản với username đã nhập.")
    raise ValueError("Tên đăng nhập là bắt buộc.")


def _resolve_role_action(user_id: str, role_name: str, action: str | None) -> bool:
    if action == "promote":
        return True
    if action == "demote":
        return False
    user = next((item for item in store.users if item.id == user_id), None)
    if not user:
        raise KeyError("user")
    return user.role != role_name


def _resolve_manager_ids(request: Request, requested_ids: list[str] | None) -> list[str]:
    current_user = require_admin_access(request)
    available_ids = [user.id for user in store.users if user.role == "manager"]
    return normalize_manager_filter_ids(request, requested_ids, available_ids, current_user)


def _force_manager_binding(current_user: AdminSessionUser, manager_id: str | None) -> str | None:
    if current_user.role == "manager":
        return current_user.id
    return manager_id


def _enforce_user_scope(current_user: AdminSessionUser, user_id: str) -> None:
    if current_user.role != "manager":
        return
    user = store._find_user(user_id)
    if user.role == "manager" and user.id != current_user.id:
        raise HTTPException(status_code=403, detail="Khong du quyen thao tac manager nay.")
    if user.role == "admin":
        raise HTTPException(status_code=403, detail="Manager khong duoc thao tac admin.")
    if user.role == "user" and user.manager_name != current_user.username:
        raise HTTPException(status_code=403, detail="Khong du quyen thao tac user khac manager.")


def _enforce_worker_scope(current_user: AdminSessionUser, worker_id: str) -> None:
    if current_user.role != "manager":
        return
    worker = store._find_worker(worker_id)
    if worker.manager_id != current_user.id:
        raise HTTPException(status_code=403, detail="Khong du quyen thao tac BOT ngoai scope manager.")


def _enforce_channel_scope(current_user: AdminSessionUser, channel_id: str) -> None:
    if current_user.role != "manager":
        return
    channel = store._find_channel(channel_id)
    if store._resolve_channel_manager_id(channel) != current_user.id:
        raise HTTPException(status_code=403, detail="Khong du quyen thao tac kenh ngoai scope manager.")


def _enforce_job_scope(current_user: AdminSessionUser, job_id: str) -> None:
    if current_user.role != "manager":
        return
    job = store._find_job(job_id)
    if store._resolve_job_manager_id(job) != current_user.id:
        raise HTTPException(status_code=403, detail="Khong du quyen thao tac job ngoai scope manager.")


def _scoped_job_ids(current_user: AdminSessionUser, *, channel_id: str | None = None) -> list[str]:
    jobs = list(store.jobs)
    if current_user.role == "manager":
        jobs = [job for job in jobs if store._resolve_job_manager_id(job) == current_user.id]
    if channel_id:
        jobs = [job for job in jobs if job.channel_id == channel_id]
    return [job.id for job in jobs]


def _enforce_user_bot_mapping_scope(current_user: AdminSessionUser, user_id: str, mapping_id: int) -> None:
    _enforce_user_scope(current_user, user_id)
    mapping = next((item for item in store.user_worker_links if int(item.get("id") or 0) == mapping_id), None)
    if mapping is None or str(mapping.get("user_id") or "").strip() != user_id:
        raise HTTPException(status_code=403, detail="Khong du quyen thao tac mapping BOT nay.")


def _admin_forbidden_redirect(path: str = "/admin/user/index") -> RedirectResponse:
    return _redirect_with_notice(path, "Khong du quyen truy cap khu vuc nay.", "error")


@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    if get_app_session_user(request):
        return RedirectResponse(url="/app", status_code=302)
    if get_admin_session_user(request):
        return RedirectResponse(url="/admin/user/index", status_code=302)
    return RedirectResponse(url="/login", status_code=302)


@router.get("/home", response_class=HTMLResponse)
async def public_home(request: Request):
    return templates.TemplateResponse(
        "public_home.html",
        {
            **_public_shell_payload(
                request=request,
                page_title=PUBLIC_APP_NAME,
                active_page="home",
            ),
            "hero_title": PUBLIC_APP_NAME,
            "hero_description": "A private web application for connecting YouTube channels with Google OAuth, preparing render jobs, and managing upload automation for JazzRelaxation workflows.",
            "feature_items": [
                {
                    "title": "Google OAuth channel connection",
                    "description": "Users connect their own Google and YouTube accounts to authorize uploads and channel management.",
                },
                {
                    "title": "Render job orchestration",
                    "description": "The control plane schedules loop-video and audio jobs, then distributes work to dedicated render workers.",
                },
                {
                    "title": "Managed publishing workflow",
                    "description": "The application stores job history, channel metadata, worker assignments, and upload status for internal operations.",
                },
            ],
        },
    )


@router.get("/privacy-policy", response_class=HTMLResponse)
async def privacy_policy(request: Request):
    return templates.TemplateResponse(
        "public_legal.html",
        {
            **_public_shell_payload(
                request=request,
                page_title=f"Privacy Policy | {PUBLIC_APP_NAME}",
                active_page="privacy",
            ),
            "legal_title": "Privacy Policy",
            "legal_updated_at": "March 26, 2026",
            "legal_sections": [
                {
                    "heading": "Who this application is for",
                    "body": [
                        "JazzRelaxation Upload Manager is a private operational tool used by authorized team members to connect YouTube channels, prepare render jobs, and manage upload automation.",
                    ],
                },
                {
                    "heading": "Google and YouTube data we access",
                    "body": [
                        "When a user connects a Google account, the application may access basic profile data such as account identifier, email address, and profile information.",
                        "When a user grants YouTube permissions, the application may access channel identity and upload-related permissions required to publish videos on behalf of that connected channel.",
                    ],
                },
                {
                    "heading": "How we use the data",
                    "body": [
                        "Connected account data is used only to identify the authorized channel, maintain channel configuration inside the application, and perform user-approved upload operations.",
                        "The application does not sell connected account data and does not use Google user data for advertising.",
                    ],
                },
                {
                    "heading": "Storage and retention",
                    "body": [
                        "The application stores operational metadata, channel mappings, worker assignments, and OAuth tokens needed to keep the publishing workflow running.",
                        "Access is limited to authorized operators and administrators who manage the internal publishing system.",
                    ],
                },
                {
                    "heading": "User controls",
                    "body": [
                        "Users can disconnect a connected channel inside the application and can revoke Google account access from their Google security settings at any time.",
                    ],
                },
                {
                    "heading": "Contact",
                    "body": [
                        f"For privacy questions related to this application, contact {PUBLIC_SUPPORT_EMAIL}.",
                    ],
                },
            ],
        },
    )


@router.get("/terms-of-service", response_class=HTMLResponse)
async def terms_of_service(request: Request):
    return templates.TemplateResponse(
        "public_legal.html",
        {
            **_public_shell_payload(
                request=request,
                page_title=f"Terms of Service | {PUBLIC_APP_NAME}",
                active_page="terms",
            ),
            "legal_title": "Terms of Service",
            "legal_updated_at": "March 26, 2026",
            "legal_sections": [
                {
                    "heading": "Authorized use",
                    "body": [
                        "This application is intended only for authorized internal users and approved operators managing JazzRelaxation publishing workflows.",
                    ],
                },
                {
                    "heading": "User responsibilities",
                    "body": [
                        "Users are responsible for connecting only Google and YouTube accounts they are authorized to manage.",
                        "Users must ensure that uploaded content, metadata, and automation activity comply with applicable platform rules and internal policies.",
                    ],
                },
                {
                    "heading": "Service availability",
                    "body": [
                        "The application is provided on an operational best-effort basis and may be updated, suspended, or restricted for maintenance, security, or compliance reasons.",
                    ],
                },
                {
                    "heading": "Account and access controls",
                    "body": [
                        "Administrators may restrict, suspend, or remove access if misuse, policy violations, or security concerns are detected.",
                    ],
                },
                {
                    "heading": "Contact",
                    "body": [
                        f"For service questions related to this application, contact {PUBLIC_SUPPORT_EMAIL}.",
                    ],
                },
            ],
        },
    )


@router.get("/login", response_class=HTMLResponse)
async def app_login_page(
    request: Request,
    next: str | None = None,
    notice: str | None = None,
):
    current_app_user = get_app_session_user(request)
    if current_app_user:
        return RedirectResponse(url="/app", status_code=302)
    current_admin_user = get_admin_session_user(request)
    if current_admin_user:
        return RedirectResponse(url="/admin/user/index", status_code=302)
    next_url = _sanitize_next_url(next, default_path="/app")
    return templates.TemplateResponse(
        "admin/login.html",
        _app_login_template_payload(
            request=request,
            page_title="Đăng nhập hệ thống",
            next_url=next_url,
            notice=notice,
            notice_level="error" if notice else "success",
            form_data={"username": ""},
            form_action="/login",
            login_badge="Đăng nhập hệ thống",
            login_heading="Truy cập nền tảng",
            login_description="Nhập tài khoản một lần. User sẽ vào workspace làm việc, admin hoặc manager sẽ vào khu quản trị.",
            submit_label="Đăng nhập",
            switch_href=None,
            switch_label=None,
            hero_context_label="Unified Access",
            hero_status_label="System Online · Unified Access",
        ),
    )


@router.post("/login")
async def app_login_submit(request: Request):
    form = await request.form()
    username = str(form.get("username") or "").strip()
    password = str(form.get("password") or "").strip()
    next_url = _sanitize_next_url(form.get("next"), default_path="/app")

    try:
        session_payload = store.authenticate_login_user(username, password)
    except ValueError as exc:
        return templates.TemplateResponse(
            "admin/login.html",
            _app_login_template_payload(
                request=request,
                page_title="Đăng nhập hệ thống",
                next_url=next_url,
                notice=str(exc),
                notice_level="error",
                form_data={"username": username},
                form_action="/login",
                login_badge="Đăng nhập hệ thống",
                login_heading="Truy cập nền tảng",
                login_description="Nhập tài khoản một lần. User sẽ vào workspace làm việc, admin hoặc manager sẽ vào khu quản trị.",
                submit_label="Đăng nhập",
                switch_href=None,
                switch_label=None,
                hero_context_label="Unified Access",
                hero_status_label="System Online · Unified Access",
            ),
            status_code=400,
        )

    clear_app_session(request)
    clear_admin_session(request)
    if session_payload["role"] == "user":
        set_app_session_user(request, AppSessionUser(**session_payload))
    else:
        set_admin_session_user(request, AdminSessionUser(**session_payload))
    return RedirectResponse(url=_resolve_login_redirect(session_payload["role"], next_url), status_code=303)


@router.post("/logout")
async def app_logout(request: Request):
    clear_admin_session(request)
    clear_app_session(request)
    return RedirectResponse(url="/login", status_code=303)


@router.get("/app", response_class=HTMLResponse)
async def user_dashboard(
    request: Request,
    notice: str | None = None,
    notice_level: str = "success",
):
    current_user = get_app_session_user(request)
    admin_user = get_admin_session_user(request)
    if admin_user and (
        not current_user
        or current_user.id != admin_user.id
        or current_user.role != admin_user.role
    ):
        store.assert_admin_session_user(admin_user.id, admin_user.role)
        current_user = AppSessionUser(
            id=admin_user.id,
            username=admin_user.username,
            display_name=admin_user.display_name,
            role=admin_user.role,
            manager_name=admin_user.manager_name,
        )
        set_app_session_user(request, current_user)
    if not current_user:
        return RedirectResponse(url="/login?next=/app", status_code=302)
    store.assert_app_session_user(current_user.id, current_user.role)
    return templates.TemplateResponse(
        "user_dashboard.html",
        {
            "request": request,
            "dashboard": store.get_user_dashboard_view(
                user_id=current_user.id,
                notice=notice,
                notice_level=notice_level,
            ),
        },
    )


@router.get("/auth/google/callback")
async def google_oauth_callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
):
    request.session.pop(GOOGLE_OAUTH_STATE_SESSION_KEY, None)
    return _redirect_with_notice(
        "/app",
        "Luong OAuth da duoc tat tren nhanh hien tai. Hay dung '+ Them Kenh' de dang nhap bang Ubuntu Browser.",
        "error",
    )


@router.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    if get_app_session_user(request):
        return RedirectResponse(url="/app", status_code=302)
    if not get_admin_session_user(request):
        next_url = request.url.path
        return RedirectResponse(url=f"/login?next={next_url}", status_code=302)
    return RedirectResponse(url="/admin/user/index", status_code=302)


@router.get("/admin/login", response_class=HTMLResponse)
async def admin_login_page(
    request: Request,
    next: str | None = None,
    notice: str | None = None,
):
    target = _sanitize_next_url(next, default_path="/admin/user/index")
    payload = {"next": target}
    if notice:
        payload["notice"] = notice
    return RedirectResponse(url=f"/login?{urlencode(payload)}", status_code=302)


@router.post("/admin/login")
async def admin_login_submit(request: Request):
    return RedirectResponse(url="/login?next=/admin/user/index", status_code=303)


@router.post("/admin/logout")
async def admin_logout(request: Request):
    clear_app_session(request)
    clear_admin_session(request)
    return RedirectResponse(url="/login", status_code=303)


@router.post("/admin/UpdateSession")
async def admin_update_session(request: Request):
    require_admin_access(request)
    form = await request.form()
    values = form.getlist("manager_ids") or form.getlist("Manangers")
    selected_ids = [str(value).strip() for value in values if str(value).strip()]
    normalized_ids = _resolve_manager_ids(request, selected_ids)
    return JSONResponse({"ok": True, "manager_ids": normalized_ids})


@router.get("/admin/user/index", response_class=HTMLResponse)
async def admin_user_index(
    request: Request,
    manager_ids: list[str] = Query(default=[]),
    notice: str | None = None,
    notice_level: str = "success",
):
    current_admin = require_admin_access(request)
    selected_manager_ids = _resolve_manager_ids(request, manager_ids)
    dashboard = store.get_admin_user_index_context(
        manager_ids=selected_manager_ids,
        viewer_role=current_admin.role,
        viewer_id=current_admin.id,
        notice=notice,
        notice_level=notice_level,
    )
    return _render(request, dashboard)


@router.get("/admin/user/create", response_class=HTMLResponse)
async def admin_user_create(
    request: Request,
    notice: str | None = None,
    notice_level: str = "success",
):
    current_admin = require_admin_access(request)
    dashboard = store.get_admin_user_create_context(
        viewer_role=current_admin.role,
        viewer_id=current_admin.id,
        notice=notice,
        notice_level=notice_level,
    )
    if current_admin.role == "manager":
        dashboard["manager_candidates"] = [
            item for item in dashboard["manager_candidates"] if item["id"] == current_admin.id
        ]
        dashboard["form"]["manager_id"] = current_admin.id
        dashboard["manager_binding_locked"] = True
    return _render(request, dashboard)


@router.post("/admin/user/create", response_class=HTMLResponse)
async def admin_user_create_submit(request: Request):
    current_admin = require_admin_access(request)
    form = await request.form()
    username = str(form.get("username", "")).strip()
    password = str(form.get("password", "")).strip()
    manager_id = _force_manager_binding(current_admin, str(form.get("manager_id", "")).strip() or None)

    try:
        result = store.create_admin_user(
            username=username,
            display_name=username,
            password=password,
            role="user",
            manager_id=manager_id,
            telegram=None,
            updated_by=current_admin.username,
        )
        return _redirect_with_notice(
            "/admin/user/index",
            f"Đã tạo user {result['username']}.",
            "success",
        )
    except ValueError as exc:
        dashboard = store.get_admin_user_create_context(
            viewer_role=current_admin.role,
            viewer_id=current_admin.id,
            form_data={
                "username": username,
                "manager_id": manager_id or "",
            },
            error=str(exc),
            notice_level="error",
        )
        if current_admin.role == "manager":
            dashboard["manager_candidates"] = [
                item for item in dashboard["manager_candidates"] if item["id"] == current_admin.id
            ]
            dashboard["form"]["manager_id"] = current_admin.id
            dashboard["manager_binding_locked"] = True
        return _render(request, dashboard, status_code=400)


@router.get("/admin/user/edit", response_class=HTMLResponse)
async def admin_user_edit_page(
    request: Request,
    userId: str,
    notice: str | None = None,
    notice_level: str = "success",
):
    current_admin = require_admin_access(request)
    _enforce_user_scope(current_admin, userId)
    return _render(
        request,
        store.get_admin_user_edit_context(
            user_id=userId,
            viewer_role=current_admin.role,
            viewer_id=current_admin.id,
            notice=notice,
            notice_level=notice_level,
        ),
    )


@router.post("/admin/user/updatetelegram")
async def admin_user_update(request: Request):
    current_admin = require_admin_access(request)
    form = await request.form()
    user_id = str(form.get("UserId") or form.get("user_id") or "").strip()
    _enforce_user_scope(current_admin, user_id)
    target_user = next((item for item in store.users if item.id == user_id), None)
    username = str(form.get("UserName") or form.get("username") or "").strip() or (
        target_user.username if target_user else ""
    )
    password = str(form.get("Password") or form.get("password") or "").strip() or None
    manager_id = _force_manager_binding(current_admin, str(form.get("UserIdManager") or form.get("manager_id") or "").strip() or None)

    try:
        updated_user = store.update_admin_user(
            user_id=user_id,
            username=username,
            password=password,
            manager_id=manager_id,
            actor_role=current_admin.role,
            updated_by=current_admin.username,
        )
        if current_admin.id == updated_user.id:
            set_admin_session_user(request, AdminSessionUser(**store._build_session_payload(updated_user)))
        return _redirect_with_notice("/admin/user/index", "Đã cập nhật user.", "success")
    except (KeyError, ValueError) as exc:
        return _redirect_with_notice("/admin/user/index", str(exc), "error")


@router.get("/admin/user/resetpassword", response_class=HTMLResponse)
async def admin_user_reset_page(
    request: Request,
    userId: str,
    notice: str | None = None,
    notice_level: str = "success",
):
    require_admin_access(request)
    query = {"userId": userId, "notice": notice or "Đổi mật khẩu đã được gộp vào Sửa user.", "notice_level": notice_level}
    return RedirectResponse(url=f"/admin/user/edit?{urlencode(query)}", status_code=302)


@router.post("/admin/user/resetpassword")
async def admin_user_reset_password(request: Request):
    current_admin = require_admin_access(request)
    form = await request.form()
    user_id = str(form.get("userId") or form.get("user_id") or "").strip()
    if not user_id:
        return _redirect_with_notice("/admin/user/index", "Đổi mật khẩu đã được gộp vào Sửa user.", "info")
    try:
        _enforce_user_scope(current_admin, user_id)
        return _redirect_with_notice("/admin/user/edit", "Đổi mật khẩu đã được gộp vào Sửa user.", "info", userId=user_id)
    except (KeyError, ValueError) as exc:
        return _redirect_with_notice("/admin/user/index", str(exc), "error")


@router.post("/admin/user/delete")
async def admin_user_delete(request: Request):
    current_admin = require_admin_access(request)
    form = await request.form()
    user_id = str(form.get("userId") or form.get("user_id") or "").strip()
    _enforce_user_scope(current_admin, user_id)
    try:
        store.delete_admin_user(user_id)
        return _redirect_with_notice("/admin/user/index", "Đã xóa user.", "success")
    except (KeyError, ValueError) as exc:
        return _redirect_with_notice("/admin/user/index", str(exc), "error")


@router.get("/admin/user/manager", response_class=HTMLResponse)
async def admin_manager_list(
    request: Request,
    notice: str | None = None,
    notice_level: str = "success",
):
    require_admin_only(request)
    return _render(
        request,
        store.get_admin_manager_page_context(notice=notice, notice_level=notice_level),
    )


@router.post("/admin/user/updaterolemanager")
async def admin_manager_toggle(request: Request):
    current_admin = require_admin_only(request)
    form = await request.form()
    try:
        user_id = _resolve_user_id(
            user_id=str(form.get("userId") or "").strip() or None,
            username=str(form.get("username") or form.get("userName") or "").strip() or None,
        )
        promote = _resolve_role_action(user_id, "manager", str(form.get("action") or "").strip() or None)
        store.update_role_manager(user_id, promote=promote, updated_by=current_admin.username)
        return _redirect_with_notice("/admin/user/manager", "Đã cập nhật quyền manager.", "success")
    except (KeyError, ValueError) as exc:
        return _redirect_with_notice("/admin/user/manager", str(exc), "error")


@router.get("/admin/user/admins", response_class=HTMLResponse)
async def admin_admins_list(
    request: Request,
    notice: str | None = None,
    notice_level: str = "success",
):
    require_admin_only(request)
    return _render(
        request,
        store.get_admin_admin_page_context(notice=notice, notice_level=notice_level),
    )


@router.post("/admin/user/updateroleadmin")
async def admin_admin_toggle(request: Request):
    current_admin = require_admin_only(request)
    form = await request.form()
    try:
        user_id = _resolve_user_id(
            user_id=str(form.get("userId") or "").strip() or None,
            username=str(form.get("username") or form.get("userName") or "").strip() or None,
        )
        promote = _resolve_role_action(user_id, "admin", str(form.get("action") or "").strip() or None)
        store.update_role_admin(user_id, promote=promote, updated_by=current_admin.username)
        return _redirect_with_notice("/admin/user/admins", "Đã cập nhật quyền admin.", "success")
    except (KeyError, ValueError) as exc:
        return _redirect_with_notice("/admin/user/admins", str(exc), "error")


@router.get("/admin/user/managerbot", response_class=HTMLResponse)
async def admin_user_manager_bot(
    request: Request,
    userId: str,
    notice: str | None = None,
    notice_level: str = "success",
):
    current_admin = require_admin_access(request)
    _enforce_user_scope(current_admin, userId)
    return _render(
        request,
        store.get_admin_user_bot_context(
            user_id=userId,
            viewer_role=current_admin.role,
            viewer_id=current_admin.id,
            notice=notice,
            notice_level=notice_level,
        ),
    )

@router.post("/admin/user/addbot")
async def admin_user_add_bot(request: Request):
    current_admin = require_admin_access(request)
    form = await request.form()
    user_id = str(form.get("user_id") or form.get("UserId") or "").strip()
    try:
        if user_id:
            _enforce_user_scope(current_admin, user_id)
        return _redirect_bot_page_with_scope(
            "Luồng gán BOT cũ đã được gộp vào Danh sách BOT.",
            "info",
            user_id=user_id or None,
        )
    except (KeyError, ValueError) as exc:
        return _redirect_bot_page_with_scope(str(exc), "error", user_id=user_id or None)


@router.post("/admin/user/deletebot")
async def admin_user_delete_bot(request: Request):
    current_admin = require_admin_access(request)
    form = await request.form()
    user_id = str(form.get("user_id") or form.get("userId") or "").strip()
    try:
        if user_id:
            _enforce_user_scope(current_admin, user_id)
        return _redirect_bot_page_with_scope(
            "Luồng xóa mapping BOT cũ đã được gộp vào Danh sách BOT.",
            "info",
            user_id=user_id or None,
        )
    except (KeyError, ValueError) as exc:
        return _redirect_bot_page_with_scope(str(exc), "error", user_id=user_id or None)


@router.post("/admin/user/updatebotuser")
async def admin_user_update_bot(request: Request):
    current_admin = require_admin_access(request)
    form = await request.form()
    user_id = str(form.get("user_id") or form.get("UserId") or "").strip()
    try:
        if user_id:
            _enforce_user_scope(current_admin, user_id)
        return _redirect_bot_page_with_scope(
            "Luồng sửa mapping BOT cũ đã được gộp vào Danh sách BOT.",
            "info",
            user_id=user_id or None,
        )
    except (KeyError, ValueError) as exc:
        return _redirect_bot_page_with_scope(str(exc), "error", user_id=user_id or None)


@router.get("/admin/ManagerBOT/index", response_class=HTMLResponse)
@router.get("/admin/managerbot/index", response_class=HTMLResponse)
async def admin_bot_index(
    request: Request,
    manager_ids: list[str] = Query(default=[]),
    userId: str | None = None,
    notice: str | None = None,
    notice_level: str = "success",
):
    current_admin = require_admin_access(request)
    if userId:
        _enforce_user_scope(current_admin, userId)
    selected_manager_ids = _resolve_manager_ids(request, manager_ids)
    selected_manager_ids = _resolve_bot_scope_manager_ids(selected_manager_ids, userId)
    if current_admin.role == "manager" and not selected_manager_ids:
        selected_manager_ids = [current_admin.id]
    dashboard = store.get_admin_bot_index_context(
        manager_ids=selected_manager_ids,
        viewer_role=current_admin.role,
        viewer_id=current_admin.id,
        focus_user_id=userId,
        notice=notice,
        notice_level=notice_level,
    )
    dashboard["new_worker_defaults"] = {
        "worker_id": suggest_next_worker_id([worker.id for worker in store.workers]),
        "worker_name_hint": "IP VPS",
        "ssh_user": "root",
        "browser_session_enabled": True,
        "control_plane_url": _resolve_worker_bootstrap_control_plane_url(request),
    }
    return _render(request, dashboard)


@router.get("/admin/bot/assignment", response_class=HTMLResponse)
async def admin_bot_assignment(
    request: Request,
    manager_ids: list[str] = Query(default=[]),
    userId: str | None = None,
    notice: str | None = None,
    notice_level: str = "success",
):
    current_admin = require_admin_access(request)
    if userId:
        _enforce_user_scope(current_admin, userId)
    selected_manager_ids = _resolve_manager_ids(request, manager_ids)
    selected_manager_ids = _resolve_bot_scope_manager_ids(selected_manager_ids, userId)
    if current_admin.role == "manager" and not selected_manager_ids:
        selected_manager_ids = [current_admin.id]
    return _redirect_bot_page_with_scope(
        notice or "Cấp phát BOT đã được gộp vào Danh sách BOT.",
        notice_level or "info",
        manager_ids=selected_manager_ids,
        user_id=userId,
    )


@router.post("/admin/bot/assign")
async def admin_bot_assign(request: Request):
    current_admin = require_admin_access(request)
    form = await request.form()
    user_id = str(form.get("user_id") or form.get("UserId") or "").strip() or None
    return_user_id = str(form.get("return_user_id") or "").strip() or None
    return_manager_ids = [str(value).strip() for value in form.getlist("return_manager_ids") if str(value).strip()]

    redirect_user_id = return_user_id or user_id
    scoped_manager_ids = return_manager_ids or _resolve_bot_scope_manager_ids([], redirect_user_id)
    if current_admin.role == "manager" and not scoped_manager_ids:
        scoped_manager_ids = [current_admin.id]

    try:
        if user_id:
            _enforce_user_scope(current_admin, user_id)
        return _redirect_bot_page_with_scope(
            "Màn Cấp phát BOT cũ đã được gộp vào Danh sách BOT.",
            "info",
            manager_ids=scoped_manager_ids,
            user_id=redirect_user_id,
        )
    except (KeyError, ValueError) as exc:
        return _redirect_bot_page_with_scope(
            str(exc),
            "error",
            manager_ids=scoped_manager_ids,
            user_id=redirect_user_id,
        )


@router.post("/admin/bot/update")
async def admin_bot_update(request: Request):
    current_admin = require_admin_access(request)
    form = await request.form()
    worker_id = str(form.get("Id") or form.get("worker_id") or "").strip()
    _enforce_worker_scope(current_admin, worker_id)
    name = str(form.get("Name") or form.get("name") or "").strip()
    group = str(form.get("Group") or form.get("group") or "").strip() or None
    manager_id = _force_manager_binding(current_admin, str(form.get("UserIdManager") or form.get("manager_id") or "").strip() or None)
    assigned_user_id = str(form.get("UserId") or form.get("user_id") or "").strip() or None
    return_user_id = str(form.get("return_user_id") or "").strip() or None
    return_manager_ids = [str(value).strip() for value in form.getlist("return_manager_ids") if str(value).strip()]
    if assigned_user_id:
        _enforce_user_scope(current_admin, assigned_user_id)

    try:
        store.update_bot(
            worker_id,
            name,
            group,
            manager_id,
            assigned_user_id=assigned_user_id,
            viewer_role=current_admin.role,
            viewer_id=current_admin.id,
            updated_by=current_admin.username,
        )
        return _redirect_bot_page_with_scope(
            "Đã cập nhật BOT.",
            "success",
            manager_ids=return_manager_ids,
            user_id=return_user_id,
        )
    except (KeyError, ValueError) as exc:
        return _redirect_bot_page_with_scope(
            str(exc),
            "error",
            manager_ids=return_manager_ids,
            user_id=return_user_id,
        )


@router.post("/admin/bot/create")
async def admin_bot_create(request: Request):
    current_admin = require_admin_access(request)
    form = await request.form()
    vps_ip = str(form.get("vps_ip") or "").strip()
    ssh_user = str(form.get("ssh_user") or "").strip() or "root"
    auth_mode = str(form.get("auth_mode") or "password").strip().lower() or "password"
    password = str(form.get("password") or "").strip()
    ssh_private_key = str(form.get("ssh_private_key") or "").replace("\r\n", "\n").strip()
    return_user_id = str(form.get("return_user_id") or "").strip() or None
    return_manager_ids = [str(value).strip() for value in form.getlist("return_manager_ids") if str(value).strip()]
    manager_name = current_admin.username if current_admin.role == "manager" else "system"
    worker_id = suggest_next_worker_id([worker.id for worker in store.workers])

    try:
        bootstrap_request = build_worker_bootstrap_request(
            vps_ip=vps_ip,
            ssh_user=ssh_user,
            password=password if auth_mode != "ssh_key" else None,
            ssh_private_key=ssh_private_key if auth_mode == "ssh_key" else None,
            shared_secret=store.get_worker_shared_secret(),
            control_plane_url=_resolve_worker_bootstrap_control_plane_url(request),
            worker_id=worker_id,
            manager_name=manager_name,
        )
        result = await run_in_threadpool(bootstrap_worker_via_ssh, bootstrap_request)
        return _redirect_bot_page_with_scope(
            f"Da khoi tao BOT {result.worker_id} tren {result.vps_ip}. Worker service dang {result.service_active} va se tu register voi control-plane.",
            "success",
            manager_ids=return_manager_ids,
            user_id=return_user_id,
        )
    except WorkerBootstrapError as exc:
        return _redirect_bot_page_with_scope(
            str(exc),
            "error",
            manager_ids=return_manager_ids,
            user_id=return_user_id,
        )


@router.post("/admin/managerbot/delete")
async def admin_bot_delete(request: Request):
    current_admin = require_admin_access(request)
    form = await request.form()
    worker_id = str(form.get("Id") or form.get("worker_id") or "").strip()
    _enforce_worker_scope(current_admin, worker_id)
    return_user_id = str(form.get("return_user_id") or "").strip() or None
    return_manager_ids = [str(value).strip() for value in form.getlist("return_manager_ids") if str(value).strip()]
    try:
        store.delete_bot(worker_id)
        return _redirect_bot_page_with_scope(
            "Đã xóa BOT.",
            "success",
            manager_ids=return_manager_ids,
            user_id=return_user_id,
        )
    except (KeyError, ValueError) as exc:
        return _redirect_bot_page_with_scope(
            str(exc),
            "error",
            manager_ids=return_manager_ids,
            user_id=return_user_id,
        )


@router.post("/admin/bot/updatethread")
@router.post("/admin/bot/updateThread")
async def admin_bot_update_thread(request: Request):
    current_admin = require_admin_access(request)
    form = await request.form()
    worker_id = str(form.get("Id") or form.get("worker_id") or "").strip()
    try:
        if worker_id:
            _enforce_worker_scope(current_admin, worker_id)
        return _redirect_with_notice(
            "/admin/ManagerBOT/index",
            "Thiết lập luồng BOT cũ đã được bỏ khỏi UI điều phối hiện tại.",
            "info",
        )
    except (KeyError, ValueError) as exc:
        return _redirect_with_notice("/admin/ManagerBOT/index", str(exc), "error")


@router.get("/admin/bot/user", response_class=HTMLResponse)
async def admin_bot_of_user(
    request: Request,
    userId: str,
    username: str | None = None,
    notice: str | None = None,
    notice_level: str = "success",
):
    current_admin = require_admin_access(request)
    _enforce_user_scope(current_admin, userId)
    return _render(
        request,
        store.get_admin_bots_of_user_context(
            user_id=userId,
            viewer_role=current_admin.role,
            viewer_id=current_admin.id,
            notice=notice,
            notice_level=notice_level,
        ),
    )


@router.get("/admin/bot/userofbot", response_class=HTMLResponse)
async def admin_user_of_bot(
    request: Request,
    botId: str,
    botName: str | None = None,
    notice: str | None = None,
    notice_level: str = "success",
):
    current_admin = require_admin_access(request)
    _enforce_worker_scope(current_admin, botId)
    return _render(
        request,
        store.get_admin_users_of_bot_context(
            worker_id=botId,
            viewer_role=current_admin.role,
            viewer_id=current_admin.id,
            notice=notice,
            notice_level=notice_level,
        ),
    )


@router.get("/admin/channel/index", response_class=HTMLResponse)
async def admin_channel_index(
    request: Request,
    manager_ids: list[str] = Query(default=[]),
    userId: str | None = None,
    botId: str | None = None,
    notice: str | None = None,
    notice_level: str = "success",
):
    current_admin = require_admin_access(request)
    if userId:
        _enforce_user_scope(current_admin, userId)
    if botId:
        _enforce_worker_scope(current_admin, botId)
    selected_manager_ids = _resolve_manager_ids(request, manager_ids)
    return _render(
        request,
        store.get_admin_channel_index_context(
            manager_ids=selected_manager_ids,
            user_id=userId,
            bot_id=botId,
            viewer_role=current_admin.role,
            viewer_id=current_admin.id,
            notice=notice,
            notice_level=notice_level,
        ),
    )


@router.get("/admin/channel/user", response_class=HTMLResponse)
async def admin_channel_of_user(
    request: Request,
    userId: str,
    username: str | None = None,
    notice: str | None = None,
    notice_level: str = "success",
):
    current_admin = require_admin_access(request)
    _enforce_user_scope(current_admin, userId)
    return _render(
        request,
        store.get_admin_channels_of_user_context(
            user_id=userId,
            viewer_role=current_admin.role,
            viewer_id=current_admin.id,
            notice=notice,
            notice_level=notice_level,
        ),
    )


@router.get("/admin/channel/bot", response_class=HTMLResponse)
async def admin_channel_of_bot(
    request: Request,
    botId: str,
    botName: str | None = None,
    notice: str | None = None,
    notice_level: str = "success",
):
    current_admin = require_admin_access(request)
    _enforce_worker_scope(current_admin, botId)
    return _render(
        request,
        store.get_admin_channel_index_context(
            bot_id=botId,
            viewer_role=current_admin.role,
            viewer_id=current_admin.id,
            manager_ids=[current_admin.id] if current_admin.role == "manager" else None,
            notice=notice,
            notice_level=notice_level,
        ),
    )


@router.get("/admin/channel/users", response_class=HTMLResponse)
async def admin_users_of_channel(
    request: Request,
    channelId: str,
    channelName: str | None = None,
    notice: str | None = None,
    notice_level: str = "success",
):
    current_admin = require_admin_access(request)
    _enforce_channel_scope(current_admin, channelId)
    return _render(
        request,
        store.get_admin_users_of_channel_context(
            channel_id=channelId,
            viewer_role=current_admin.role,
            viewer_id=current_admin.id,
            notice=notice,
            notice_level=notice_level,
        ),
    )


@router.post("/admin/channel/updateuserchannel")
@router.post("/admin/channel/UpdateUserChannel")
async def admin_channel_update_user(request: Request):
    current_admin = require_admin_access(request)
    form = await request.form()
    user_id = str(form.get("userId") or form.get("user_id") or "").strip()
    channel_id = str(form.get("channelId") or form.get("channel_id") or "").strip()
    username = str(form.get("username") or form.get("userName") or "").strip()
    _enforce_user_scope(current_admin, user_id)

    try:
        action = store.update_user_channel(user_id, channel_id)
        message = "Đã cấp quyền kênh cho user." if action == "added" else "Đã thu hồi quyền kênh của user."
        return _redirect_with_notice("/admin/channel/user", message, "success", userId=user_id, username=username)
    except (KeyError, ValueError) as exc:
        return _redirect_with_notice("/admin/channel/user", str(exc), "error", userId=user_id, username=username)


@router.post("/admin/channel/adduser")
@router.post("/admin/channel/addUser")
@router.post("/admin/Channel/addUser")
async def admin_channel_add_user(request: Request):
    current_admin = require_admin_access(request)
    form = await request.form()
    user_id = str(form.get("userId") or form.get("user_id") or "").strip()
    channel_id = str(form.get("channelId") or form.get("channel_id") or "").strip()
    channel_name = str(form.get("channelName") or form.get("channel_name") or "").strip()
    _enforce_user_scope(current_admin, user_id)

    try:
        action = store.add_user_to_channel(user_id, channel_id)
        message = "Đã thêm user vào kênh." if action == "added" else "Đã gỡ user khỏi kênh."
        return _redirect_with_notice("/admin/channel/users", message, "success", channelId=channel_id, channelName=channel_name)
    except (KeyError, ValueError) as exc:
        return _redirect_with_notice("/admin/channel/users", str(exc), "error", channelId=channel_id, channelName=channel_name)


@router.post("/admin/channel/updateprofile")
@router.post("/admin/channel/UpdateProfile")
async def admin_channel_update_profile(request: Request):
    current_admin = require_admin_access(request)
    form = await request.form()
    channel_id = str(form.get("id") or form.get("channelId") or form.get("channel_id") or "").strip()
    _enforce_channel_scope(current_admin, channel_id)
    redirect_to = str(form.get("redirect_to") or "/admin/channel/index").strip() or "/admin/channel/index"
    bot_id = str(form.get("botId") or "").strip()
    user_id = str(form.get("userId") or "").strip()
    username = str(form.get("username") or "").strip()
    channel_name = str(form.get("channelName") or "").strip()
    try:
        store.update_channel_profile(channel_id)
        if "channel/user" in redirect_to.lower():
            return _redirect_with_notice(redirect_to, "Đã cập nhật profile kênh.", "success", userId=user_id, username=username)
        if "channel/users" in redirect_to.lower():
            return _redirect_with_notice(redirect_to, "Đã cập nhật profile kênh.", "success", channelId=channel_id, channelName=channel_name)
        if "bot" in redirect_to.lower():
            return _redirect_with_notice(redirect_to, "Đã cập nhật profile kênh.", "success", botId=bot_id)
        return _redirect_with_notice(redirect_to, "Đã cập nhật profile kênh.", "success")
    except (KeyError, ValueError) as exc:
        if "channel/user" in redirect_to.lower():
            return _redirect_with_notice(redirect_to, str(exc), "error", userId=user_id, username=username)
        if "channel/users" in redirect_to.lower():
            return _redirect_with_notice(redirect_to, str(exc), "error", channelId=channel_id, channelName=channel_name)
        if "bot" in redirect_to.lower():
            return _redirect_with_notice(redirect_to, str(exc), "error", botId=bot_id)
        return _redirect_with_notice(redirect_to, str(exc), "error")


@router.get("/admin/channel/export")
async def admin_channel_export(request: Request):
    current_admin = require_admin_access(request)
    selected_manager_ids = _resolve_manager_ids(request, [])
    rows = store.get_channel_export_rows_filtered(
        manager_ids=selected_manager_ids if current_admin.role == "manager" or selected_manager_ids else None
    )
    fieldnames = [
        "Avatar",
        "ChannelName",
        "ChannelYTId",
        "ChannelLink",
        "BotName",
        "ChannelGmail",
        "Group",
        "CreatedTime",
        "TotalUser",
        "Status",
        "UserUpload",
        "Manager",
    ]
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    filename = "bao-cao-channel-youtube.csv"
    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"; filename*=UTF-8\'\'{quote(filename)}',
        "Cache-Control": "no-store",
        "X-Content-Type-Options": "nosniff",
    }
    return Response(content="\ufeff" + buffer.getvalue(), media_type="text/csv; charset=utf-8", headers=headers)


@router.get("/admin/channel/delete")
async def admin_channel_delete(request: Request, channelId: str, botId: str | None = None):
    current_admin = require_admin_access(request)
    _enforce_channel_scope(current_admin, channelId)
    if botId:
        _enforce_worker_scope(current_admin, botId)
    try:
        store.delete_channel(channelId)
        if botId:
            return _redirect_with_notice("/admin/channel/bot", "Đã xóa kênh.", "success", botId=botId)
        return _redirect_with_notice("/admin/channel/index", "Đã xóa kênh.", "success")
    except (KeyError, ValueError) as exc:
        if botId:
            return _redirect_with_notice("/admin/channel/bot", str(exc), "error", botId=botId)
        return _redirect_with_notice("/admin/channel/index", str(exc), "error")


@router.get("/admin/channel/deleteajax")
@router.post("/admin/channel/deleteajax")
async def admin_channel_delete_ajax(request: Request, id: str | None = None):
    current_admin = require_admin_access(request)
    if request.method == "POST":
        form = await request.form()
        id = str(form.get("id") or form.get("channelId") or "").strip() or id
    if not id:
        return JSONResponse({"ok": False, "error": "Missing channel id"}, status_code=400)
    try:
        _enforce_channel_scope(current_admin, id)
        store.delete_channel(id)
        return JSONResponse({"ok": True})
    except (KeyError, ValueError) as exc:
        return JSONResponse({"ok": False, "error": str(exc)}, status_code=400)


@router.get("/admin/render/index", response_class=HTMLResponse)
async def admin_render_index(
    request: Request,
    manager_ids: list[str] = Query(default=[]),
    notice: str | None = None,
    notice_level: str = "success",
):
    current_admin = require_admin_access(request)
    selected_manager_ids = _resolve_manager_ids(request, manager_ids)
    return _render(
        request,
        store.get_admin_render_index_context(
            manager_ids=selected_manager_ids,
            viewer_role=current_admin.role,
            viewer_id=current_admin.id,
            notice=notice,
            notice_level=notice_level,
        ),
    )


@router.get("/admin/render/channel", response_class=HTMLResponse)
async def admin_render_of_channel(
    request: Request,
    channelId: str,
    channelName: str | None = None,
    manager_ids: list[str] = Query(default=[]),
    notice: str | None = None,
    notice_level: str = "success",
):
    current_admin = require_admin_access(request)
    _enforce_channel_scope(current_admin, channelId)
    selected_manager_ids = _resolve_manager_ids(request, manager_ids)
    return _render(
        request,
        store.get_admin_render_index_context(
            manager_ids=selected_manager_ids,
            channel_id=channelId,
            viewer_role=current_admin.role,
            viewer_id=current_admin.id,
            notice=notice,
            notice_level=notice_level,
        ),
    )


@router.get("/admin/render/renderinfo", response_class=HTMLResponse)
async def admin_render_info(
    request: Request,
    id: str,
    notice: str | None = None,
    notice_level: str = "success",
):
    current_admin = require_admin_access(request)
    _enforce_job_scope(current_admin, id)
    return _render(
        request,
        store.get_admin_render_detail_context(
            job_id=id,
            viewer_role=current_admin.role,
            viewer_id=current_admin.id,
            notice=notice,
            notice_level=notice_level,
        ),
    )


@router.post("/admin/render/delete")
async def admin_render_delete_all(request: Request):
    current_admin = require_admin_access(request)
    form = await request.form()
    channel_id = str(form.get("channelId") or "").strip()
    deleted_by = str(form.get("deleted_by") or current_admin.username).strip() or current_admin.username
    if channel_id:
        _enforce_channel_scope(current_admin, channel_id)
    scoped_job_ids = _scoped_job_ids(current_admin, channel_id=channel_id or None)
    if current_admin.role == "admin" and not channel_id:
        store.delete_all_jobs(deleted_by=deleted_by)
    else:
        store.delete_jobs(scoped_job_ids)
    if channel_id:
        return _redirect_with_notice("/admin/render/channel", "Đã xóa toàn bộ dữ liệu render.", "success", channelId=channel_id)
    return _redirect_with_notice("/admin/render/index", "Đã xóa toàn bộ dữ liệu render.", "success")


@router.post("/admin/render/deletejob")
async def admin_render_delete_job(request: Request):
    current_admin = require_admin_access(request)
    form = await request.form()
    job_id = str(form.get("id") or form.get("jobId") or "").strip()
    channel_id = str(form.get("channelId") or "").strip()
    try:
        _enforce_job_scope(current_admin, job_id)
        store.delete_job(job_id)
        if channel_id:
            return _redirect_with_notice("/admin/render/channel", "Đã xóa job render.", "success", channelId=channel_id)
        return _redirect_with_notice("/admin/render/index", "Đã xóa job render.", "success")
    except KeyError as exc:
        if channel_id:
            return _redirect_with_notice("/admin/render/channel", str(exc), "error", channelId=channel_id)
        return _redirect_with_notice("/admin/render/index", str(exc), "error")
