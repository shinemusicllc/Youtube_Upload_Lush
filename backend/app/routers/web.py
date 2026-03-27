from __future__ import annotations

import csv
from io import StringIO
from pathlib import Path
from urllib.parse import urlencode

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates

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
    raise KeyError("user")


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
    clear_app_session(request)
    return RedirectResponse(url="/login", status_code=303)


@router.get("/app", response_class=HTMLResponse)
async def user_dashboard(
    request: Request,
    notice: str | None = None,
    notice_level: str = "success",
):
    current_user = get_app_session_user(request)
    if not current_user and get_admin_session_user(request):
        return RedirectResponse(url="/admin/user/index", status_code=302)
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
    current_user = get_app_session_user(request)
    if not current_user:
        return _redirect_with_notice("/login", "Vui long dang nhap lai de tiep tuc Google OAuth.", "error", next="/app")
    store.assert_app_session_user(current_user.id, current_user.role)
    expected_state = str(request.session.pop(GOOGLE_OAUTH_STATE_SESSION_KEY, "") or "")
    if error:
        return _redirect_with_notice("/app", f"Google OAuth b\u1ecb t\u1eeb ch\u1ed1i: {error}", "error")

    if not code or not state:
        return _redirect_with_notice("/app", "Google OAuth callback thi\u1ebfu code ho\u1eb7c state.", "error")
    if not expected_state or state != expected_state:
        return _redirect_with_notice("/app", "State OAuth kh\u00f4ng h\u1ee3p l\u1ec7 ho\u1eb7c \u0111\u00e3 h\u1ebft h\u1ea1n.", "error")

    try:
        result = store.complete_google_oauth(
            user_id=current_user.id,
            code=code,
            base_url=str(request.base_url).rstrip("/"),
        )
    except ValueError as exc:
        return _redirect_with_notice("/app", str(exc), "error")
    except Exception:
        return _redirect_with_notice("/app", "OAuth callback g\u1eb7p l\u1ed7i n\u1ed9i b\u1ed9. Ki\u1ec3m tra l\u1ea1i v\u00e0 th\u1eed k\u1ebft n\u1ed1i l\u1ea1i k\u00eanh.", "error")

    return _redirect_with_notice(
        "/app",
        f"\u0110\u00e3 k\u1ebft n\u1ed1i k\u00eanh {result['channel_name']} ({result['youtube_channel_id']}).",
        "success",
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
    selected_manager_ids = _resolve_manager_ids(request, manager_ids)
    dashboard = store.get_admin_user_index_context(
        manager_ids=selected_manager_ids or None,
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
    dashboard = store.get_admin_user_create_context(notice=notice, notice_level=notice_level)
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
    display_name = str(form.get("DisplayName") or form.get("display_name") or "").strip() or (
        target_user.display_name if target_user else ""
    )
    telegram = str(form.get("Telegram") or form.get("link_telegram") or "").strip() or None
    manager_id = _force_manager_binding(current_admin, str(form.get("UserIdManager") or form.get("manager_id") or "").strip() or None)

    try:
        store.update_admin_user(
            user_id=user_id,
            display_name=display_name,
            telegram=telegram,
            manager_id=manager_id,
            updated_by=current_admin.username,
        )
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
    current_admin = require_admin_access(request)
    _enforce_user_scope(current_admin, userId)
    return _render(
        request,
        store.get_admin_user_reset_context(
            user_id=userId,
            notice=notice,
            notice_level=notice_level,
        ),
    )


@router.post("/admin/user/resetpassword")
async def admin_user_reset_password(request: Request):
    current_admin = require_admin_access(request)
    form = await request.form()
    user_id = str(form.get("userId") or form.get("user_id") or "").strip()
    _enforce_user_scope(current_admin, user_id)
    password = str(form.get("Password") or form.get("password") or "").strip()

    try:
        store.reset_admin_user_password(user_id, password, updated_by=current_admin.username)
        return _redirect_with_notice("/admin/user/index", "Đã reset mật khẩu user.", "success")
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
    user_id = _resolve_user_id(
        user_id=str(form.get("userId") or "").strip() or None,
        username=str(form.get("username") or form.get("userName") or "").strip() or None,
    )
    promote = _resolve_role_action(user_id, "manager", str(form.get("action") or "").strip() or None)
    try:
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
    user_id = _resolve_user_id(
        user_id=str(form.get("userId") or "").strip() or None,
        username=str(form.get("username") or form.get("userName") or "").strip() or None,
    )
    promote = _resolve_role_action(user_id, "admin", str(form.get("action") or "").strip() or None)
    try:
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
            notice=notice,
            notice_level=notice_level,
        ),
    )

@router.post("/admin/user/addbot")
async def admin_user_add_bot(request: Request):
    current_admin = require_admin_access(request)
    form = await request.form()
    user_id = str(form.get("user_id") or form.get("UserId") or "").strip()
    _enforce_user_scope(current_admin, user_id)
    worker_id = str(form.get("worker_id") or form.get("WorkerId") or "").strip()
    threads = int(str(form.get("number_of_threads") or form.get("Threads") or "1"))
    bot_type = str(form.get("bot_type") or "1080p").strip() or "1080p"

    try:
        store.add_user_bot(user_id, worker_id, threads, bot_type=bot_type)
        store._save_state()
        return _redirect_with_notice("/admin/user/managerbot", "Đã gán BOT cho user.", "success", userId=user_id)
    except (KeyError, ValueError) as exc:
        return _redirect_with_notice("/admin/user/managerbot", str(exc), "error", userId=user_id)


@router.post("/admin/user/deletebot")
async def admin_user_delete_bot(request: Request):
    current_admin = require_admin_access(request)
    form = await request.form()
    assignment_id = int(str(form.get("assignment_id") or form.get("id") or "0"))
    user_id = str(form.get("user_id") or form.get("userId") or "").strip()
    _enforce_user_scope(current_admin, user_id)

    try:
        store.delete_user_bot(assignment_id)
        store._save_state()
        return _redirect_with_notice("/admin/user/managerbot", "Đã xóa mapping BOT.", "success", userId=user_id)
    except (KeyError, ValueError) as exc:
        return _redirect_with_notice("/admin/user/managerbot", str(exc), "error", userId=user_id)


@router.post("/admin/user/updatebotuser")
async def admin_user_update_bot(request: Request):
    current_admin = require_admin_access(request)
    form = await request.form()
    assignment_id = int(str(form.get("assignment_id") or form.get("Id") or "0"))
    user_id = str(form.get("user_id") or form.get("UserId") or "").strip()
    _enforce_user_scope(current_admin, user_id)
    threads = int(str(form.get("number_of_threads") or form.get("Threads") or "1"))
    bot_type = str(form.get("bot_type") or "").strip() or None

    try:
        store.update_user_bot(assignment_id, threads, bot_type=bot_type)
        store._save_state()
        return _redirect_with_notice("/admin/user/managerbot", "Đã cập nhật mapping BOT.", "success", userId=user_id)
    except (KeyError, ValueError) as exc:
        return _redirect_with_notice("/admin/user/managerbot", str(exc), "error", userId=user_id)


@router.get("/admin/ManagerBOT/index", response_class=HTMLResponse)
@router.get("/admin/managerbot/index", response_class=HTMLResponse)
async def admin_bot_index(
    request: Request,
    manager_ids: list[str] = Query(default=[]),
    notice: str | None = None,
    notice_level: str = "success",
):
    selected_manager_ids = _resolve_manager_ids(request, manager_ids)
    return _render(
        request,
        store.get_admin_bot_index_context(
            manager_ids=selected_manager_ids or None,
            notice=notice,
            notice_level=notice_level,
        ),
    )


@router.post("/admin/bot/update")
async def admin_bot_update(request: Request):
    current_admin = require_admin_access(request)
    form = await request.form()
    worker_id = str(form.get("Id") or form.get("worker_id") or "").strip()
    name = str(form.get("Name") or form.get("name") or "").strip()
    group = str(form.get("Group") or form.get("group") or "").strip()
    manager_id = _force_manager_binding(current_admin, str(form.get("UserIdManager") or form.get("manager_id") or "").strip() or None)

    try:
        store.update_bot(worker_id, name, group, manager_id, updated_by=current_admin.username)
        return _redirect_with_notice("/admin/ManagerBOT/index", "Đã cập nhật BOT.", "success")
    except (KeyError, ValueError) as exc:
        return _redirect_with_notice("/admin/ManagerBOT/index", str(exc), "error")


@router.post("/admin/managerbot/delete")
async def admin_bot_delete(request: Request):
    require_admin_access(request)
    form = await request.form()
    worker_id = str(form.get("Id") or form.get("worker_id") or "").strip()
    try:
        store.delete_bot(worker_id)
        return _redirect_with_notice("/admin/ManagerBOT/index", "Đã xóa BOT.", "success")
    except (KeyError, ValueError) as exc:
        return _redirect_with_notice("/admin/ManagerBOT/index", str(exc), "error")


@router.post("/admin/bot/updatethread")
@router.post("/admin/bot/updateThread")
async def admin_bot_update_thread(request: Request):
    require_admin_access(request)
    form = await request.form()
    worker_id = str(form.get("Id") or form.get("worker_id") or "").strip()
    thread = int(str(form.get("Thread") or form.get("thread") or "0"))
    try:
        store.update_bot_thread(worker_id, thread)
        return _redirect_with_notice("/admin/ManagerBOT/index", "Đã cập nhật số luồng BOT.", "success")
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
    require_admin_access(request)
    return _render(
        request,
        store.get_admin_users_of_bot_context(
            worker_id=botId,
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
    selected_manager_ids = _resolve_manager_ids(request, manager_ids)
    return _render(
        request,
        store.get_admin_channel_index_context(
            manager_ids=selected_manager_ids or None,
            user_id=userId,
            bot_id=botId,
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
    require_admin_access(request)
    return _render(
        request,
        store.get_admin_channel_index_context(
            bot_id=botId,
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
    require_admin_access(request)
    return _render(
        request,
        store.get_admin_users_of_channel_context(
            channel_id=channelId,
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
    require_admin_access(request)
    form = await request.form()
    channel_id = str(form.get("id") or form.get("channelId") or form.get("channel_id") or "").strip()
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
    require_admin_access(request)
    rows = store.get_channel_export_rows()
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
    payload = StringIO(buffer.getvalue())
    headers = {"Content-Disposition": 'attachment; filename="bao-cao-channel-youtube.csv"'}
    return StreamingResponse(iter([payload.getvalue()]), media_type="text/csv; charset=utf-8", headers=headers)


@router.get("/admin/channel/delete")
async def admin_channel_delete(request: Request, channelId: str, botId: str | None = None):
    require_admin_access(request)
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
    require_admin_access(request)
    if request.method == "POST":
        form = await request.form()
        id = str(form.get("id") or form.get("channelId") or "").strip() or id
    if not id:
        return JSONResponse({"ok": False, "error": "Missing channel id"}, status_code=400)
    try:
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
    selected_manager_ids = _resolve_manager_ids(request, manager_ids)
    return _render(
        request,
        store.get_admin_render_index_context(
            manager_ids=selected_manager_ids or None,
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
    selected_manager_ids = _resolve_manager_ids(request, manager_ids)
    return _render(
        request,
        store.get_admin_render_index_context(
            manager_ids=selected_manager_ids or None,
            channel_id=channelId,
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
    require_admin_access(request)
    return _render(
        request,
        store.get_admin_render_detail_context(
            job_id=id,
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
    store.delete_all_jobs(deleted_by=deleted_by)
    if channel_id:
        return _redirect_with_notice("/admin/render/channel", "Đã xóa toàn bộ dữ liệu render.", "success", channelId=channel_id)
    return _redirect_with_notice("/admin/render/index", "Đã xóa toàn bộ dữ liệu render.", "success")


@router.post("/admin/render/deletejob")
async def admin_render_delete_job(request: Request):
    require_admin_access(request)
    form = await request.form()
    job_id = str(form.get("id") or form.get("jobId") or "").strip()
    channel_id = str(form.get("channelId") or "").strip()
    try:
        store.delete_job(job_id)
        if channel_id:
            return _redirect_with_notice("/admin/render/channel", "Đã xóa job render.", "success", channelId=channel_id)
        return _redirect_with_notice("/admin/render/index", "Đã xóa job render.", "success")
    except KeyError as exc:
        if channel_id:
            return _redirect_with_notice("/admin/render/channel", str(exc), "error", channelId=channel_id)
        return _redirect_with_notice("/admin/render/index", str(exc), "error")
