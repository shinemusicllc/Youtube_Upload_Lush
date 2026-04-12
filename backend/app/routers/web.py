from __future__ import annotations

import csv
from datetime import datetime
from io import StringIO
from pathlib import Path
from urllib.parse import quote, urlencode

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates

from ..request_urls import resolve_external_base_url, resolve_worker_bootstrap_control_plane_url
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
    require_app_access,
    set_app_session_user,
    set_admin_session_user,
)
from ..store import store
from ..worker_bootstrap import (
    WorkerBootstrapError,
    build_worker_decommission_request,
    build_worker_bootstrap_request,
    start_worker_decommission_operation,
    start_worker_install_operation,
)

templates = Jinja2Templates(directory=Path(__file__).resolve().parents[1] / "templates")
router = APIRouter(tags=["web"])

PUBLIC_APP_NAME = "JazzRelaxation Upload Manager"
PUBLIC_SUPPORT_EMAIL = "hoangpear99@gmail.com"
ADMIN_DASHBOARD_HOME = "/admin/user/index"


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
    base_url = resolve_external_base_url(request)
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
    return "/app" if role == "user" else ADMIN_DASHBOARD_HOME


def _resolve_login_redirect(role: str, requested_next: str | None) -> str:
    candidate = (requested_next or "").strip()
    if role == "user":
        if candidate.startswith("/app") or candidate.startswith("/auth/google"):
            return candidate
        return "/app"
    return ADMIN_DASHBOARD_HOME


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


def _resolve_admin_workspace(value: str | None) -> str:
    normalized = str(value or "").strip().lower()
    return "live" if normalized == "live" else "upload"


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
    workspace: str = "upload",
):
    base_path = "/admin/ManagerBOT/index"
    query: list[tuple[str, str]] = [
        ("notice", message),
        ("notice_level", level),
        ("workspace", _resolve_admin_workspace(workspace)),
    ]
    for manager_id in manager_ids or []:
        if manager_id:
            query.append(("manager_ids", manager_id))
    if user_id:
        query.append(("userId", user_id))
    return RedirectResponse(url=f"{base_path}?{urlencode(query, doseq=True)}", status_code=303)


def _redirect_live_page_with_scope(
    message: str,
    level: str = "success",
    *,
    manager_ids: list[str] | None = None,
):
    query: list[tuple[str, str]] = [
        ("notice", message),
        ("notice_level", level),
    ]
    for manager_id in manager_ids or []:
        if manager_id:
            query.append(("manager_ids", manager_id))
    return RedirectResponse(url=f"/app/live?{urlencode(query, doseq=True)}", status_code=303)


def _resolve_channel_workspace_request(
    request: Request,
    *,
    workspace: str | None = None,
    form=None,
    redirect_to: str | None = None,
) -> str:
    candidates = [workspace, request.query_params.get("workspace")]
    if form is not None:
        candidates.append(form.get("workspace"))
        if redirect_to is None:
            redirect_to = str(form.get("redirect_to") or "").strip()
    referer = str(request.headers.get("referer") or "").strip().lower()
    redirect_hint = str(redirect_to or "").strip().lower()
    if "workspace=live" in referer or "workspace=live" in redirect_hint:
        return "live"
    for candidate in candidates:
        if _resolve_admin_workspace(candidate) == "live":
            return "live"
    return "upload"


def _redirect_live_channel_notice():
    return _redirect_with_notice("/app/live", "Workspace Live Stream không có Danh sách Kênh.", "info")


def _live_channel_json_error():
    return JSONResponse(
        {"ok": False, "error": "Workspace Live Stream không có Danh sách Kênh."},
        status_code=400,
    )


def _resolve_worker_bootstrap_control_plane_url(request: Request) -> str:
    return resolve_worker_bootstrap_control_plane_url(request)


def _parse_live_form_datetime(value: str | None) -> datetime | None:
    cleaned = str(value or "").strip()
    if not cleaned:
        return None
    for fmt in ("%d/%m/%Y %H:%M", "%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(cleaned, fmt)
        except ValueError:
            continue
    raise ValueError("Thời gian live không đúng định dạng hỗ trợ.")


def _extract_live_form_values(form) -> dict[str, str]:
    return {
        "stream_name": str(form.get("stream_name") or "").strip(),
        "video_url": str(form.get("video_url") or "").strip(),
        "audio_url": str(form.get("audio_url") or "").strip(),
        "stream_key": str(form.get("stream_key") or "").strip(),
        "backup_delay_minutes": str(form.get("backup_delay_minutes") or "3").strip() or "3",
        "primary_worker_id": str(form.get("primary_worker_id") or "").strip(),
        "backup_worker_id": str(form.get("backup_worker_id") or "").strip(),
        "start_at": str(form.get("start_time_live") or "").strip(),
        "end_at": str(form.get("end_time_live") or "").strip(),
    }


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


def _enforce_worker_scope(current_user: AdminSessionUser, worker_id: str, *, workspace_mode: str = "upload") -> None:
    if current_user.role != "manager":
        return
    worker = store._find_live_worker(worker_id) if workspace_mode == "live" else store._find_worker(worker_id)
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
    if get_admin_session_user(request):
        return RedirectResponse(url=ADMIN_DASHBOARD_HOME, status_code=302)
    if get_app_session_user(request):
        return RedirectResponse(url="/app", status_code=302)
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
    current_admin_user = get_admin_session_user(request)
    if current_admin_user:
        return RedirectResponse(url=ADMIN_DASHBOARD_HOME, status_code=302)
    current_app_user = get_app_session_user(request)
    if current_app_user:
        return RedirectResponse(url="/app", status_code=302)
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
    if admin_user:
        store.assert_admin_session_user(admin_user.id, admin_user.role)
        if current_user:
            clear_app_session(request)
        current_user = AppSessionUser(
            id=admin_user.id,
            username=admin_user.username,
            display_name=admin_user.display_name,
            role=admin_user.role,
            manager_name=admin_user.manager_name,
        )
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


@router.get("/app/live", response_class=HTMLResponse)
async def user_live_dashboard(
    request: Request,
    notice: str | None = None,
    notice_level: str = "success",
    edit: str | None = None,
    detail: str | None = None,
):
    current_user = get_app_session_user(request)
    admin_user = get_admin_session_user(request)
    if admin_user:
        store.assert_admin_session_user(admin_user.id, admin_user.role)
        if current_user:
            clear_app_session(request)
        current_user = AppSessionUser(
            id=admin_user.id,
            username=admin_user.username,
            display_name=admin_user.display_name,
            role=admin_user.role,
            manager_name=admin_user.manager_name,
        )
    if not current_user:
        return RedirectResponse(url="/login?next=/app/live", status_code=302)
    store.assert_app_session_user(current_user.id, current_user.role)
    return templates.TemplateResponse(
        "user_live_dashboard.html",
        {
            "request": request,
            "dashboard": store.get_user_live_workspace_view(
                user_id=current_user.id,
                notice=notice,
                notice_level=notice_level,
                editing_stream_id=edit,
                detail_stream_id=detail,
            ),
        },
    )


@router.post("/app/live/create")
async def user_live_create(request: Request):
    current_user = require_app_access(request, "user", "manager", "admin")
    form = await request.form()
    live_form_values = _extract_live_form_values(form)
    try:
        start_time_live = _parse_live_form_datetime(live_form_values["start_at"])
        end_time_live = _parse_live_form_datetime(live_form_values["end_at"])
        store.create_live_stream(
            owner_user_id=current_user.id,
            stream_name=live_form_values["stream_name"],
            primary_worker_id=live_form_values["primary_worker_id"],
            stream_key=live_form_values["stream_key"],
            video_url=live_form_values["video_url"],
            audio_url=live_form_values["audio_url"] or None,
            backup_worker_id=live_form_values["backup_worker_id"] or None,
            backup_delay_minutes=live_form_values["backup_delay_minutes"],
            start_time_live=start_time_live,
            end_time_live=end_time_live,
            is_live_now=False,
            is_forever=end_time_live is None,
            viewer_role=current_user.role,
            viewer_id=current_user.id,
        )
        return _redirect_with_notice("/app/live", "Đã tạo luồng live stream.", "success")
    except (KeyError, ValueError) as exc:
        return templates.TemplateResponse(
            "user_live_dashboard.html",
            {
                "request": request,
                "dashboard": store.get_user_live_workspace_view(
                    user_id=current_user.id,
                    notice=str(exc),
                    notice_level="error",
                    live_form_values=live_form_values,
                ),
            },
            status_code=422,
        )


@router.post("/app/live/update")
async def user_live_update(request: Request):
    current_user = require_app_access(request, "user", "manager", "admin")
    form = await request.form()
    stream_id = str(form.get("stream_id") or "").strip()
    live_form_values = _extract_live_form_values(form)
    try:
        start_time_live = _parse_live_form_datetime(live_form_values["start_at"])
        end_time_live = _parse_live_form_datetime(live_form_values["end_at"])
        store.update_live_stream(
            stream_id=stream_id,
            stream_name=live_form_values["stream_name"],
            primary_worker_id=live_form_values["primary_worker_id"],
            stream_key=live_form_values["stream_key"],
            video_url=live_form_values["video_url"],
            audio_url=live_form_values["audio_url"] or None,
            backup_worker_id=live_form_values["backup_worker_id"] or None,
            backup_delay_minutes=live_form_values["backup_delay_minutes"],
            start_time_live=start_time_live,
            end_time_live=end_time_live,
            is_live_now=False,
            is_forever=end_time_live is None,
            viewer_role=current_user.role,
            viewer_id=current_user.id,
        )
        return _redirect_with_notice("/app/live", "Đã cập nhật luồng live stream.", "success")
    except (KeyError, ValueError) as exc:
        return templates.TemplateResponse(
            "user_live_dashboard.html",
            {
                "request": request,
                "dashboard": store.get_user_live_workspace_view(
                    user_id=current_user.id,
                    notice=str(exc),
                    notice_level="error",
                    live_form_values=live_form_values,
                    editing_stream_id=stream_id,
                ),
            },
            status_code=422,
        )


@router.post("/app/live/delete")
async def user_live_delete(request: Request):
    current_user = require_app_access(request, "user", "manager", "admin")
    form = await request.form()
    stream_id = str(form.get("stream_id") or "").strip()
    try:
        store.delete_live_stream(
            stream_id,
            viewer_role=current_user.role,
            viewer_id=current_user.id,
        )
        return _redirect_with_notice("/app/live", "Đã xóa luồng live stream.", "success")
    except (KeyError, ValueError) as exc:
        return _redirect_with_notice("/app/live", str(exc), "error")


@router.post("/app/live/stop")
async def user_live_stop(request: Request):
    current_user = require_app_access(request, "user", "manager", "admin")
    form = await request.form()
    stream_id = str(form.get("stream_id") or "").strip()
    try:
        store.stop_live_stream(
            stream_id,
            viewer_role=current_user.role,
            viewer_id=current_user.id,
        )
        return _redirect_with_notice("/app/live", "Đã dừng luồng live stream.", "success")
    except (KeyError, ValueError) as exc:
        return _redirect_with_notice("/app/live", str(exc), "error")


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
    admin_user = get_admin_session_user(request)
    if admin_user:
        return RedirectResponse(url=ADMIN_DASHBOARD_HOME, status_code=302)
    if get_app_session_user(request):
        return RedirectResponse(url="/app", status_code=302)
    if not admin_user:
        next_url = request.url.path
        return RedirectResponse(url=f"/login?next={next_url}", status_code=302)
    return RedirectResponse(url=ADMIN_DASHBOARD_HOME, status_code=302)


@router.get("/admin/login", response_class=HTMLResponse)
async def admin_login_page(
    request: Request,
    next: str | None = None,
    notice: str | None = None,
):
    target = _sanitize_next_url(next, default_path=ADMIN_DASHBOARD_HOME)
    payload = {"next": target}
    if notice:
        payload["notice"] = notice
    return RedirectResponse(url=f"/login?{urlencode(payload)}", status_code=302)


@router.post("/admin/login")
async def admin_login_submit(request: Request):
    return RedirectResponse(url=f"/login?next={ADMIN_DASHBOARD_HOME}", status_code=303)


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
    workspace: str = "upload",
):
    current_admin = require_admin_access(request)
    selected_manager_ids = _resolve_manager_ids(request, manager_ids)
    workspace_mode = _resolve_admin_workspace(workspace)
    dashboard = store.get_admin_user_index_context(
        manager_ids=selected_manager_ids,
        viewer_role=current_admin.role,
        viewer_id=current_admin.id,
        notice=notice,
        notice_level=notice_level,
        workspace_mode=workspace_mode,
    )
    return _render(request, dashboard)


@router.get("/admin/user/create", response_class=HTMLResponse)
async def admin_user_create(
    request: Request,
    notice: str | None = None,
    notice_level: str = "success",
    workspace: str = "upload",
):
    current_admin = require_admin_access(request)
    workspace_mode = _resolve_admin_workspace(workspace)
    dashboard = store.get_admin_user_create_context(
        viewer_role=current_admin.role,
        viewer_id=current_admin.id,
        notice=notice,
        notice_level=notice_level,
        workspace_mode=workspace_mode,
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
    workspace_mode = _resolve_admin_workspace(str(form.get("workspace") or "").strip())
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
            workspace=workspace_mode,
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
            workspace_mode=workspace_mode,
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
    workspace: str = "upload",
):
    current_admin = require_admin_access(request)
    _enforce_user_scope(current_admin, userId)
    workspace_mode = _resolve_admin_workspace(workspace)
    return _render(
        request,
        store.get_admin_user_edit_context(
            user_id=userId,
            viewer_role=current_admin.role,
            viewer_id=current_admin.id,
            notice=notice,
            notice_level=notice_level,
            workspace_mode=workspace_mode,
        ),
    )


@router.post("/admin/user/updatetelegram")
async def admin_user_update(request: Request):
    current_admin = require_admin_access(request)
    form = await request.form()
    workspace_mode = _resolve_admin_workspace(str(form.get("workspace") or "").strip())
    user_id = str(form.get("UserId") or form.get("user_id") or "").strip()
    _enforce_user_scope(current_admin, user_id)
    target_user = next((item for item in store.users if item.id == user_id), None)
    username = str(form.get("UserName") or form.get("username") or "").strip() or (
        target_user.username if target_user else ""
    )
    password = str(form.get("Password") or form.get("password") or "").strip() or None
    telegram = str(form.get("TelegramId") or form.get("telegram") or "").strip()
    manager_id = _force_manager_binding(
        current_admin,
        str(form.get("UserIdManager") or form.get("manager_id") or "").strip() or None,
    )

    try:
        updated_user = store.update_admin_user(
            user_id=user_id,
            username=username,
            password=password,
            manager_id=manager_id,
            telegram=telegram,
            actor_role=current_admin.role,
            updated_by=current_admin.username,
        )
        if current_admin.id == updated_user.id:
            set_admin_session_user(request, AdminSessionUser(**store._build_session_payload(updated_user)))
        return _redirect_with_notice("/admin/user/index", "Da cap nhat user.", "success", workspace=workspace_mode)
    except (KeyError, ValueError) as exc:
        return _redirect_with_notice("/admin/user/index", str(exc), "error", workspace=workspace_mode)


@router.post("/admin/user/telegram-link/request")
async def admin_user_telegram_link_request(request: Request):
    current_admin = require_admin_access(request)
    form = await request.form()
    user_id = str(form.get("userId") or form.get("UserId") or form.get("user_id") or "").strip()
    try:
        _enforce_user_scope(current_admin, user_id)
        payload = store.create_telegram_link_request(user_id)
        return JSONResponse({"ok": True, **payload})
    except (HTTPException, KeyError, ValueError) as exc:
        error_message = exc.detail if isinstance(exc, HTTPException) else str(exc)
        status_code = exc.status_code if isinstance(exc, HTTPException) else 400
        return JSONResponse({"ok": False, "error": error_message}, status_code=status_code)


@router.get("/admin/user/telegram-link/status")
async def admin_user_telegram_link_status(request: Request, userId: str, code: str):
    current_admin = require_admin_access(request)
    try:
        _enforce_user_scope(current_admin, userId)
        payload = store.get_telegram_link_request_status(userId, code)
        return JSONResponse({"ok": True, **payload})
    except (HTTPException, KeyError, ValueError) as exc:
        error_message = exc.detail if isinstance(exc, HTTPException) else str(exc)
        status_code = exc.status_code if isinstance(exc, HTTPException) else 400
        return JSONResponse({"ok": False, "error": error_message}, status_code=status_code)


@router.get("/admin/user/resetpassword", response_class=HTMLResponse)
async def admin_user_reset_page(
    request: Request,
    userId: str,
    notice: str | None = None,
    notice_level: str = "success",
    workspace: str = "upload",
):
    require_admin_access(request)
    query = {
        "userId": userId,
        "notice": notice or "Doi mat khau da duoc gop vao sua user.",
        "notice_level": notice_level,
        "workspace": _resolve_admin_workspace(workspace),
    }
    return RedirectResponse(url=f"/admin/user/edit?{urlencode(query)}", status_code=302)


@router.post("/admin/user/resetpassword")
async def admin_user_reset_password(request: Request):
    current_admin = require_admin_access(request)
    form = await request.form()
    workspace_mode = _resolve_admin_workspace(str(form.get("workspace") or "").strip())
    user_id = str(form.get("userId") or form.get("user_id") or "").strip()
    if not user_id:
        return _redirect_with_notice(
            "/admin/user/index",
            "Doi mat khau da duoc gop vao sua user.",
            "info",
            workspace=workspace_mode,
        )
    try:
        _enforce_user_scope(current_admin, user_id)
        return _redirect_with_notice(
            "/admin/user/edit",
            "Doi mat khau da duoc gop vao sua user.",
            "info",
            userId=user_id,
            workspace=workspace_mode,
        )
    except (KeyError, ValueError, WorkerBootstrapError) as exc:
        return _redirect_with_notice("/admin/user/index", str(exc), "error", workspace=workspace_mode)


@router.post("/admin/user/delete")
async def admin_user_delete(request: Request):
    current_admin = require_admin_access(request)
    form = await request.form()
    workspace_mode = _resolve_admin_workspace(str(form.get("workspace") or "").strip())
    user_id = str(form.get("userId") or form.get("user_id") or "").strip()
    _enforce_user_scope(current_admin, user_id)
    try:
        store.delete_admin_user(user_id)
        return _redirect_with_notice("/admin/user/index", "Da xoa user.", "success", workspace=workspace_mode)
    except (KeyError, ValueError) as exc:
        return _redirect_with_notice("/admin/user/index", str(exc), "error", workspace=workspace_mode)


@router.get("/admin/user/manager", response_class=HTMLResponse)
async def admin_manager_list(
    request: Request,
    notice: str | None = None,
    notice_level: str = "success",
    workspace: str = "upload",
):
    require_admin_only(request)
    return _render(
        request,
        store.get_admin_manager_page_context(
            notice=notice,
            notice_level=notice_level,
            workspace_mode=_resolve_admin_workspace(workspace),
        ),
    )


@router.post("/admin/user/updaterolemanager")
async def admin_manager_toggle(request: Request):
    current_admin = require_admin_only(request)
    form = await request.form()
    workspace_mode = _resolve_admin_workspace(str(form.get("workspace") or "").strip())
    try:
        user_id = _resolve_user_id(
            user_id=str(form.get("userId") or "").strip() or None,
            username=str(form.get("username") or form.get("userName") or "").strip() or None,
        )
        promote = _resolve_role_action(user_id, "manager", str(form.get("action") or "").strip() or None)
        store.update_role_manager(user_id, promote=promote, updated_by=current_admin.username)
        return _redirect_with_notice("/admin/user/manager", "Da cap nhat quyen manager.", "success", workspace=workspace_mode)
    except (KeyError, ValueError) as exc:
        return _redirect_with_notice("/admin/user/manager", str(exc), "error", workspace=workspace_mode)


@router.get("/admin/user/admins", response_class=HTMLResponse)
async def admin_admins_list(
    request: Request,
    notice: str | None = None,
    notice_level: str = "success",
    workspace: str = "upload",
):
    require_admin_only(request)
    return _render(
        request,
        store.get_admin_admin_page_context(
            notice=notice,
            notice_level=notice_level,
            workspace_mode=_resolve_admin_workspace(workspace),
        ),
    )


@router.post("/admin/user/updateroleadmin")
async def admin_admin_toggle(request: Request):
    current_admin = require_admin_only(request)
    form = await request.form()
    workspace_mode = _resolve_admin_workspace(str(form.get("workspace") or "").strip())
    try:
        user_id = _resolve_user_id(
            user_id=str(form.get("userId") or "").strip() or None,
            username=str(form.get("username") or form.get("userName") or "").strip() or None,
        )
        promote = _resolve_role_action(user_id, "admin", str(form.get("action") or "").strip() or None)
        store.update_role_admin(user_id, promote=promote, updated_by=current_admin.username)
        return _redirect_with_notice("/admin/user/admins", "Da cap nhat quyen admin.", "success", workspace=workspace_mode)
    except (KeyError, ValueError) as exc:
        return _redirect_with_notice("/admin/user/admins", str(exc), "error", workspace=workspace_mode)


@router.get("/admin/user/managerbot", response_class=HTMLResponse)
async def admin_user_manager_bot(
    request: Request,
    userId: str,
    workspace: str = "upload",
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
            workspace_mode=_resolve_admin_workspace(workspace),
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
    except (KeyError, ValueError, WorkerBootstrapError) as exc:
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
    except (KeyError, ValueError, WorkerBootstrapError) as exc:
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
    workspace: str = "upload",
):
    current_admin = require_admin_access(request)
    if userId:
        _enforce_user_scope(current_admin, userId)
    selected_manager_ids = _resolve_manager_ids(request, manager_ids)
    selected_manager_ids = _resolve_bot_scope_manager_ids(selected_manager_ids, userId)
    if current_admin.role == "manager" and not selected_manager_ids:
        selected_manager_ids = [current_admin.id]
    workspace_mode = _resolve_admin_workspace(workspace)
    dashboard = store.get_admin_bot_index_context(
        manager_ids=selected_manager_ids,
        viewer_role=current_admin.role,
        viewer_id=current_admin.id,
        focus_user_id=userId,
        notice=notice,
        notice_level=notice_level,
        workspace_mode=workspace_mode,
    )
    dashboard["new_worker_defaults"] = {
        "worker_id": (
            store.suggest_next_live_worker_bootstrap_id()
            if workspace_mode == "live"
            else store.suggest_next_worker_bootstrap_id()
        ),
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
    workspace: str = "upload",
):
    current_admin = require_admin_access(request)
    if userId:
        _enforce_user_scope(current_admin, userId)
    selected_manager_ids = _resolve_manager_ids(request, manager_ids)
    selected_manager_ids = _resolve_bot_scope_manager_ids(selected_manager_ids, userId)
    if current_admin.role == "manager" and not selected_manager_ids:
        selected_manager_ids = [current_admin.id]
    return _redirect_bot_page_with_scope(
        notice or "Cap phat BOT da duoc gop vao Danh sach BOT.",
        notice_level or "info",
        manager_ids=selected_manager_ids,
        user_id=userId,
        workspace=_resolve_admin_workspace(workspace),
    )


@router.post("/admin/bot/assign")
async def admin_bot_assign(request: Request):
    current_admin = require_admin_access(request)
    form = await request.form()
    workspace_mode = _resolve_admin_workspace(str(form.get("workspace") or "").strip())
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
            "Man cap phat BOT cu da duoc gop vao Danh sach BOT.",
            "info",
            manager_ids=scoped_manager_ids,
            user_id=redirect_user_id,
            workspace=workspace_mode,
        )
    except (KeyError, ValueError) as exc:
        return _redirect_bot_page_with_scope(
            str(exc),
            "error",
            manager_ids=scoped_manager_ids,
            user_id=redirect_user_id,
            workspace=workspace_mode,
        )


@router.post("/admin/bot/update")
async def admin_bot_update(request: Request):
    current_admin = require_admin_access(request)
    form = await request.form()
    workspace_mode = _resolve_admin_workspace(str(form.get("workspace") or "").strip())
    worker_id = str(form.get("Id") or form.get("worker_id") or "").strip()
    _enforce_worker_scope(current_admin, worker_id, workspace_mode=workspace_mode)
    name = str(form.get("Name") or form.get("name") or "").strip()
    group = str(form.get("Group") or form.get("group") or "").strip() or None
    raw_manager_id = str(form.get("UserIdManager") or form.get("manager_id") or "").strip()
    if raw_manager_id == "__bot_empty__":
        raw_manager_id = ""
    manager_id = _force_manager_binding(current_admin, raw_manager_id or None)
    live_role = str(form.get("LiveRole") or form.get("live_role") or "").strip() or None
    assigned_user_id = str(form.get("UserId") or form.get("user_id") or "").strip() or None
    assigned_user_ids = [
        str(value).strip()
        for value in list(form.getlist("UserIds")) + list(form.getlist("user_ids"))
        if str(value).strip()
    ]
    confirm_manager_transfer_cleanup = str(form.get("confirm_manager_transfer_cleanup") or "").strip() == "1"
    manage_user_assignments = str(form.get("manage_user_assignments") or "").strip() == "1"
    return_user_id = str(form.get("return_user_id") or "").strip() or None
    return_manager_ids = [str(value).strip() for value in form.getlist("return_manager_ids") if str(value).strip()]
    existing_assigned_user_ids = set()
    if manage_user_assignments:
        try:
            existing_assigned_user_ids = {
                user.id
                for user in (
                    store._assigned_live_users_for_worker(worker_id)
                    if workspace_mode == "live"
                    else store._assigned_users_for_worker(worker_id)
                )
            }
        except KeyError:
            existing_assigned_user_ids = set()
    if current_admin.role == "admin" and manager_id:
        try:
            selected_owner = store._find_user(manager_id)
        except KeyError:
            selected_owner = None
        if selected_owner is None or selected_owner.role != "manager":
            assigned_user_id = None
    if assigned_user_id and not assigned_user_ids:
        _enforce_user_scope(current_admin, assigned_user_id)
    for selected_user_id in assigned_user_ids:
        if current_admin.role == "manager" and selected_user_id in existing_assigned_user_ids:
            continue
        _enforce_user_scope(current_admin, selected_user_id)

    try:
        store.update_bot(
            worker_id,
            name,
            group,
            manager_id,
            workspace_mode=workspace_mode,
            live_role=live_role,
            assigned_user_id=assigned_user_id,
            assigned_user_ids=assigned_user_ids if manage_user_assignments else None,
            confirm_manager_transfer_cleanup=confirm_manager_transfer_cleanup,
            viewer_role=current_admin.role,
            viewer_id=current_admin.id,
            updated_by=current_admin.username,
        )
        return _redirect_bot_page_with_scope(
            "Da cap nhat BOT.",
            "success",
            manager_ids=return_manager_ids,
            user_id=return_user_id,
            workspace=workspace_mode,
        )
    except (KeyError, ValueError) as exc:
        return _redirect_bot_page_with_scope(
            str(exc),
            "error",
            manager_ids=return_manager_ids,
            user_id=return_user_id,
            workspace=workspace_mode,
        )


@router.post("/admin/bot/create")
async def admin_bot_create(request: Request):
    current_admin = require_admin_access(request)
    form = await request.form()
    workspace_mode = _resolve_admin_workspace(str(form.get("workspace") or "").strip())
    vps_ip = str(form.get("vps_ip") or "").strip()
    ssh_user = str(form.get("ssh_user") or "").strip() or "root"
    return_user_id = str(form.get("return_user_id") or "").strip() or None
    auth_mode = str(form.get("auth_mode") or "password").strip().lower() or "password"
    password = str(form.get("password") or "").strip()
    ssh_private_key = str(form.get("ssh_private_key") or "").replace("\r\n", "\n").strip()
    return_manager_ids = [str(value).strip() for value in form.getlist("return_manager_ids") if str(value).strip()]
    manager_name = current_admin.username if current_admin.role == "manager" else "system"
    manager_id = current_admin.id if current_admin.role == "manager" else None
    worker_id = (
        store.suggest_next_live_worker_bootstrap_id()
        if workspace_mode == "live"
        else store.suggest_next_worker_bootstrap_id()
    )

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
            runtime_mode=workspace_mode,
        )
        task = start_worker_install_operation(
            store=store,
            request=bootstrap_request,
            ssh_user=ssh_user,
            auth_mode=auth_mode,
            password=password if auth_mode != "ssh_key" else None,
            ssh_private_key=ssh_private_key if auth_mode == "ssh_key" else None,
            manager_id=manager_id,
            manager_name=manager_name,
            requested_by=current_admin.username,
            requested_role=current_admin.role,
        )
        return _redirect_bot_page_with_scope(
            (
                f"Da tao yeu cau cai {'BOT live' if workspace_mode == 'live' else 'BOT'} {task['worker_id']} tren {task['vps_ip']}. "
                "Control-plane dang xu ly va bang BOT se tu cap nhat khi worker ket noi lai."
            ),
            "success",
            manager_ids=return_manager_ids,
            user_id=return_user_id,
            workspace=workspace_mode,
        )
    except (WorkerBootstrapError, ValueError) as exc:
        return _redirect_bot_page_with_scope(
            str(exc),
            "error",
            manager_ids=return_manager_ids,
            user_id=return_user_id,
            workspace=workspace_mode,
        )


@router.post("/admin/managerbot/delete")
async def admin_bot_delete(request: Request):
    current_admin = require_admin_access(request)
    form = await request.form()
    workspace_mode = _resolve_admin_workspace(str(form.get("workspace") or "").strip())
    worker_id = str(form.get("Id") or form.get("worker_id") or "").strip()
    _enforce_worker_scope(current_admin, worker_id, workspace_mode=workspace_mode)
    return_user_id = str(form.get("return_user_id") or "").strip() or None
    return_manager_ids = [str(value).strip() for value in form.getlist("return_manager_ids") if str(value).strip()]
    try:
        worker_pool = store.live_workers if workspace_mode == "live" else store.workers
        worker = next((item for item in worker_pool if item.id == worker_id), None)
        if worker is None:
            raise KeyError(worker_id)
        connection_profile: dict[str, object] | None = None
        try:
            connection_profile = store.get_worker_connection_profile(worker_id, workspace_mode=workspace_mode)
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
            resolved_auth_mode = str(connection_profile.get("auth_mode") or "password").strip().lower() or "password"
            decommission_request = build_worker_decommission_request(
                vps_ip=str(connection_profile.get("vps_ip") or "").strip(),
                ssh_user=str(connection_profile.get("ssh_user") or "").strip() or "root",
                password=(str(connection_profile.get("password") or "").strip() or None) if resolved_auth_mode != "ssh_key" else None,
                ssh_private_key=(str(connection_profile.get("ssh_private_key") or "").strip() or None) if resolved_auth_mode == "ssh_key" else None,
                runtime_mode=workspace_mode,
            )
            task = start_worker_decommission_operation(
                store=store,
                worker_id=worker_id,
                request=decommission_request,
                ssh_user=str(connection_profile.get("ssh_user") or "").strip() or "root",
                workspace_mode=workspace_mode,
                requested_by=current_admin.username,
                requested_role=current_admin.role,
            )
            notice = (
                f"Da bat dau go {'BOT live' if workspace_mode == 'live' else 'BOT'} {worker_id} khoi VPS {task['vps_ip']} bang credential da luu. "
                "BOT se bien mat khoi danh sach sau khi service va du lieu tren may duoc don xong."
            )
        elif str(worker.status or "").strip() == "offline":
            if workspace_mode == "live":
                store.delete_live_bot_without_ssh(worker_id, deleted_by=current_admin.username)
            else:
                store.delete_bot_without_ssh(worker_id, deleted_by=current_admin.username)
            notice = (
                f"Da xoa {'BOT live' if workspace_mode == 'live' else 'BOT'} {worker_id} khoi he thong. "
                "BOT nay dang offline va khong co credential da luu, nen du lieu con lai tren VPS can don thu cong neu may van con chay."
            )
        else:
            raise WorkerBootstrapError(
                f"{'BOT live' if workspace_mode == 'live' else 'BOT'} nay chua co credential da luu de go tu dong. "
                "Hay go thu cong tren VPS hoac them lai BOT roi xoa lai."
            )
        return _redirect_bot_page_with_scope(
            notice,
            "success",
            manager_ids=return_manager_ids,
            user_id=return_user_id,
            workspace=workspace_mode,
        )
    except (KeyError, ValueError) as exc:
        return _redirect_bot_page_with_scope(
            str(exc),
            "error",
            manager_ids=return_manager_ids,
            user_id=return_user_id,
            workspace=workspace_mode,
        )


@router.post("/admin/bot/updatethread")
@router.post("/admin/bot/updateThread")
async def admin_bot_update_thread(request: Request):
    current_admin = require_admin_access(request)
    form = await request.form()
    workspace_mode = _resolve_admin_workspace(str(form.get("workspace") or "").strip())
    worker_id = str(form.get("Id") or form.get("worker_id") or "").strip()
    try:
        if worker_id:
            _enforce_worker_scope(current_admin, worker_id, workspace_mode=workspace_mode)
        return _redirect_with_notice(
            "/admin/ManagerBOT/index",
            "Thiet lap luong BOT cu da duoc bo khoi UI dieu phoi hien tai.",
            "info",
            workspace=workspace_mode,
        )
    except (KeyError, ValueError) as exc:
        return _redirect_with_notice("/admin/ManagerBOT/index", str(exc), "error", workspace=workspace_mode)


@router.get("/admin/live", response_class=HTMLResponse)
async def admin_live_index(
    request: Request,
    manager_ids: list[str] = Query(default=[]),
    notice: str | None = None,
    notice_level: str = "success",
    edit: str | None = None,
    detail: str | None = None,
):
    query = request.url.query
    return RedirectResponse(
        url=f"/app/live?{query}" if query else "/app/live",
        status_code=302,
    )


@router.post("/admin/live/create")
async def admin_live_create(request: Request):
    current_admin = require_admin_access(request)
    form = await request.form()
    manager_ids = [str(value).strip() for value in form.getlist("manager_ids") if str(value).strip()]
    if current_admin.role == "manager" and not manager_ids:
        manager_ids = [current_admin.id]
    live_form_values = _extract_live_form_values(form)
    try:
        start_time_live = _parse_live_form_datetime(live_form_values["start_at"])
        end_time_live = _parse_live_form_datetime(live_form_values["end_at"])
        owner = store.resolve_live_owner_from_primary_worker(
            live_form_values["primary_worker_id"],
            viewer_role=current_admin.role,
            viewer_id=current_admin.id,
        )
        store.create_live_stream(
            owner_user_id=owner.id,
            stream_name=live_form_values["stream_name"],
            primary_worker_id=live_form_values["primary_worker_id"],
            stream_key=live_form_values["stream_key"],
            video_url=live_form_values["video_url"],
            audio_url=live_form_values["audio_url"] or None,
            backup_worker_id=live_form_values["backup_worker_id"] or None,
            backup_delay_minutes=live_form_values["backup_delay_minutes"],
            start_time_live=start_time_live,
            end_time_live=end_time_live,
            is_live_now=False,
            is_forever=end_time_live is None,
            viewer_role=current_admin.role,
            viewer_id=current_admin.id,
        )
        return _redirect_live_page_with_scope("Đã tạo luồng live stream.", "success", manager_ids=manager_ids)
    except (KeyError, ValueError) as exc:
        dashboard = store.get_admin_live_workspace_context(
            manager_ids=manager_ids,
            viewer_role=current_admin.role,
            viewer_id=current_admin.id,
            notice=str(exc),
            notice_level="error",
            live_form_values=live_form_values,
        )
        return _render(request, dashboard, status_code=422)


@router.post("/admin/live/update")
async def admin_live_update(request: Request):
    current_admin = require_admin_access(request)
    form = await request.form()
    manager_ids = [str(value).strip() for value in form.getlist("manager_ids") if str(value).strip()]
    if current_admin.role == "manager" and not manager_ids:
        manager_ids = [current_admin.id]
    stream_id = str(form.get("stream_id") or "").strip()
    live_form_values = _extract_live_form_values(form)
    try:
        start_time_live = _parse_live_form_datetime(live_form_values["start_at"])
        end_time_live = _parse_live_form_datetime(live_form_values["end_at"])
        store.update_live_stream(
            stream_id=stream_id,
            stream_name=live_form_values["stream_name"],
            primary_worker_id=live_form_values["primary_worker_id"],
            stream_key=live_form_values["stream_key"],
            video_url=live_form_values["video_url"],
            audio_url=live_form_values["audio_url"] or None,
            backup_worker_id=live_form_values["backup_worker_id"] or None,
            backup_delay_minutes=live_form_values["backup_delay_minutes"],
            start_time_live=start_time_live,
            end_time_live=end_time_live,
            is_live_now=False,
            is_forever=end_time_live is None,
            viewer_role=current_admin.role,
            viewer_id=current_admin.id,
        )
        return _redirect_live_page_with_scope("Đã cập nhật luồng live stream.", "success", manager_ids=manager_ids)
    except (KeyError, ValueError) as exc:
        dashboard = store.get_admin_live_workspace_context(
            manager_ids=manager_ids,
            viewer_role=current_admin.role,
            viewer_id=current_admin.id,
            notice=str(exc),
            notice_level="error",
            live_form_values=live_form_values,
            editing_stream_id=stream_id,
        )
        return _render(request, dashboard, status_code=422)


@router.post("/admin/live/delete")
async def admin_live_delete(request: Request):
    current_admin = require_admin_access(request)
    form = await request.form()
    manager_ids = [str(value).strip() for value in form.getlist("manager_ids") if str(value).strip()]
    if current_admin.role == "manager" and not manager_ids:
        manager_ids = [current_admin.id]
    stream_id = str(form.get("stream_id") or "").strip()
    try:
        store.delete_live_stream(
            stream_id,
            viewer_role=current_admin.role,
            viewer_id=current_admin.id,
        )
        return _redirect_live_page_with_scope("Đã xóa luồng live stream.", "success", manager_ids=manager_ids)
    except (KeyError, ValueError) as exc:
        return _redirect_live_page_with_scope(str(exc), "error", manager_ids=manager_ids)


@router.post("/admin/live/stop")
async def admin_live_stop(request: Request):
    current_admin = require_admin_access(request)
    form = await request.form()
    manager_ids = [str(value).strip() for value in form.getlist("manager_ids") if str(value).strip()]
    if current_admin.role == "manager" and not manager_ids:
        manager_ids = [current_admin.id]
    stream_id = str(form.get("stream_id") or "").strip()
    try:
        store.stop_live_stream(
            stream_id,
            viewer_role=current_admin.role,
            viewer_id=current_admin.id,
        )
        return _redirect_live_page_with_scope("Đã dừng luồng live stream.", "success", manager_ids=manager_ids)
    except (KeyError, ValueError) as exc:
        return _redirect_live_page_with_scope(str(exc), "error", manager_ids=manager_ids)


@router.get("/admin/live/index")
async def admin_live_index_legacy(request: Request):
    query = request.url.query
    return RedirectResponse(
        url=f"/app/live?{query}" if query else "/app/live",
        status_code=302,
    )


@router.get("/admin/bot/user", response_class=HTMLResponse)
async def admin_bot_of_user(
    request: Request,
    userId: str,
    username: str | None = None,
    notice: str | None = None,
    notice_level: str = "success",
    workspace: str = "upload",
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
            workspace_mode=_resolve_admin_workspace(workspace),
        ),
    )


@router.get("/admin/bot/userofbot", response_class=HTMLResponse)
async def admin_user_of_bot(
    request: Request,
    botId: str,
    botName: str | None = None,
    notice: str | None = None,
    notice_level: str = "success",
    workspace: str = "upload",
):
    current_admin = require_admin_access(request)
    workspace_mode = _resolve_admin_workspace(workspace)
    _enforce_worker_scope(current_admin, botId, workspace_mode=workspace_mode)
    return _render(
        request,
        store.get_admin_users_of_bot_context(
            worker_id=botId,
            viewer_role=current_admin.role,
            viewer_id=current_admin.id,
            notice=notice,
            notice_level=notice_level,
            workspace_mode=workspace_mode,
        ),
    )


@router.get("/admin/channel/index", response_class=HTMLResponse)
async def admin_channel_index(
    request: Request,
    manager_ids: list[str] = Query(default=[]),
    userId: str | None = None,
    botId: str | None = None,
    workspace: str = "upload",
    notice: str | None = None,
    notice_level: str = "success",
):
    current_admin = require_admin_access(request)
    if userId:
        _enforce_user_scope(current_admin, userId)
    workspace_mode = _resolve_admin_workspace(workspace)
    if workspace_mode == "live":
        return _redirect_live_channel_notice()
    if botId:
        _enforce_worker_scope(current_admin, botId, workspace_mode=workspace_mode)
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
            workspace_mode=workspace_mode,
        ),
    )


@router.get("/admin/channel/user", response_class=HTMLResponse)
async def admin_channel_of_user(
    request: Request,
    userId: str,
    username: str | None = None,
    workspace: str | None = None,
    notice: str | None = None,
    notice_level: str = "success",
):
    if _resolve_channel_workspace_request(request, workspace=workspace) == "live":
        return _redirect_live_channel_notice()
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
    workspace: str | None = None,
    notice: str | None = None,
    notice_level: str = "success",
):
    if _resolve_channel_workspace_request(request, workspace=workspace) == "live":
        return _redirect_live_channel_notice()
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
    workspace: str | None = None,
    notice: str | None = None,
    notice_level: str = "success",
):
    if _resolve_channel_workspace_request(request, workspace=workspace) == "live":
        return _redirect_live_channel_notice()
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
    if _resolve_channel_workspace_request(request, form=form) == "live":
        return _redirect_live_channel_notice()
    user_id = str(form.get("userId") or form.get("user_id") or "").strip()
    channel_id = str(form.get("channelId") or form.get("channel_id") or "").strip()
    username = str(form.get("username") or form.get("userName") or "").strip()
    _enforce_user_scope(current_admin, user_id)

    try:
        action = store.update_user_channel(
            user_id,
            channel_id,
            viewer_role=current_admin.role,
            viewer_id=current_admin.id,
        )
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
    if _resolve_channel_workspace_request(request, form=form) == "live":
        return _redirect_live_channel_notice()
    user_id = str(form.get("userId") or form.get("user_id") or "").strip()
    channel_id = str(form.get("channelId") or form.get("channel_id") or "").strip()
    channel_name = str(form.get("channelName") or form.get("channel_name") or "").strip()
    _enforce_user_scope(current_admin, user_id)

    try:
        action = store.add_user_to_channel(
            user_id,
            channel_id,
            viewer_role=current_admin.role,
            viewer_id=current_admin.id,
        )
        message = "Đã thêm user vào kênh." if action == "added" else "Đã gỡ user khỏi kênh."
        return _redirect_with_notice("/admin/channel/users", message, "success", channelId=channel_id, channelName=channel_name)
    except (KeyError, ValueError) as exc:
        return _redirect_with_notice("/admin/channel/users", str(exc), "error", channelId=channel_id, channelName=channel_name)


@router.post("/admin/channel/updateprofile")
@router.post("/admin/channel/UpdateProfile")
async def admin_channel_update_profile(request: Request):
    current_admin = require_admin_access(request)
    form = await request.form()
    if _resolve_channel_workspace_request(request, form=form) == "live":
        return _redirect_live_channel_notice()
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
async def admin_channel_export(request: Request, workspace: str | None = None):
    if _resolve_channel_workspace_request(request, workspace=workspace) == "live":
        return _redirect_live_channel_notice()
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
async def admin_channel_delete(
    request: Request,
    channelId: str,
    botId: str | None = None,
    workspace: str | None = None,
):
    if _resolve_channel_workspace_request(request, workspace=workspace) == "live":
        return _redirect_live_channel_notice()
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
    workspace_mode = _resolve_channel_workspace_request(request)
    if request.method == "POST":
        form = await request.form()
        workspace_mode = _resolve_channel_workspace_request(request, form=form)
        id = str(form.get("id") or form.get("channelId") or "").strip() or id
    if workspace_mode == "live":
        return _live_channel_json_error()
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
    workspace: str = "upload",
    notice: str | None = None,
    notice_level: str = "success",
):
    current_admin = require_admin_access(request)
    workspace_mode = _resolve_admin_workspace(workspace)
    selected_manager_ids = _resolve_manager_ids(request, manager_ids)
    return _render(
        request,
        store.get_admin_render_index_context(
            manager_ids=selected_manager_ids,
            viewer_role=current_admin.role,
            viewer_id=current_admin.id,
            notice=notice,
            notice_level=notice_level,
            workspace_mode=workspace_mode,
        ),
    )


@router.get("/admin/render/channel", response_class=HTMLResponse)
async def admin_render_of_channel(
    request: Request,
    channelId: str,
    channelName: str | None = None,
    manager_ids: list[str] = Query(default=[]),
    workspace: str = "upload",
    notice: str | None = None,
    notice_level: str = "success",
):
    current_admin = require_admin_access(request)
    workspace_mode = _resolve_admin_workspace(workspace)
    if workspace_mode == "live":
        return _redirect_with_notice(
            "/admin/render/index",
            "Workspace Live Stream không có Danh sách Kênh.",
            "info",
            workspace="live",
        )
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
            workspace_mode=workspace_mode,
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
