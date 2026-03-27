from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from fastapi import HTTPException, Request


ADMIN_SESSION_KEY = "admin_auth"
APP_SESSION_KEY = "app_auth"
MANAGER_FILTER_SESSION_KEY = "admin_manager_ids"
GOOGLE_OAUTH_STATE_SESSION_KEY = "google_oauth_state"


@dataclass
class AdminSessionUser:
    id: str
    username: str
    display_name: str
    role: str
    manager_name: str | None = None

    def to_session(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "username": self.username,
            "display_name": self.display_name,
            "role": self.role,
            "manager_name": self.manager_name,
        }


@dataclass
class AppSessionUser:
    id: str
    username: str
    display_name: str
    role: str
    manager_name: str | None = None

    def to_session(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "username": self.username,
            "display_name": self.display_name,
            "role": self.role,
            "manager_name": self.manager_name,
        }


def build_admin_session_user(payload: dict[str, Any]) -> AdminSessionUser:
    return AdminSessionUser(
        id=str(payload["id"]),
        username=str(payload["username"]),
        display_name=str(payload["display_name"]),
        role=str(payload["role"]),
        manager_name=(str(payload["manager_name"]) if payload.get("manager_name") else None),
    )


def build_app_session_user(payload: dict[str, Any]) -> AppSessionUser:
    return AppSessionUser(
        id=str(payload["id"]),
        username=str(payload["username"]),
        display_name=str(payload["display_name"]),
        role=str(payload["role"]),
        manager_name=(str(payload["manager_name"]) if payload.get("manager_name") else None),
    )


def get_admin_session_user(request: Request) -> AdminSessionUser | None:
    session_payload = request.session.get(ADMIN_SESSION_KEY)
    if not isinstance(session_payload, dict):
        return None
    try:
        return build_admin_session_user(session_payload)
    except KeyError:
        return None


def get_app_session_user(request: Request) -> AppSessionUser | None:
    session_payload = request.session.get(APP_SESSION_KEY)
    if not isinstance(session_payload, dict):
        return None
    try:
        return build_app_session_user(session_payload)
    except KeyError:
        return None


def set_admin_session_user(request: Request, user: AdminSessionUser) -> None:
    request.session[ADMIN_SESSION_KEY] = user.to_session()


def set_app_session_user(request: Request, user: AppSessionUser) -> None:
    request.session[APP_SESSION_KEY] = user.to_session()


def clear_admin_session(request: Request) -> None:
    request.session.pop(ADMIN_SESSION_KEY, None)
    request.session.pop(MANAGER_FILTER_SESSION_KEY, None)


def clear_app_session(request: Request) -> None:
    request.session.pop(APP_SESSION_KEY, None)
    request.session.pop(GOOGLE_OAUTH_STATE_SESSION_KEY, None)


def require_admin_access(request: Request, *roles: str) -> AdminSessionUser:
    session_user = getattr(request.state, "admin_user", None) or get_admin_session_user(request)
    if not isinstance(session_user, AdminSessionUser):
        raise HTTPException(status_code=401, detail="Admin session required.")
    allowed_roles = set(roles or ("admin", "manager"))
    if session_user.role not in allowed_roles:
        raise HTTPException(status_code=403, detail="Khong du quyen truy cap.")
    return session_user


def require_admin_only(request: Request) -> AdminSessionUser:
    return require_admin_access(request, "admin")


def require_app_access(request: Request, *roles: str) -> AppSessionUser:
    session_user = getattr(request.state, "app_user", None) or get_app_session_user(request)
    if not isinstance(session_user, AppSessionUser):
        raise HTTPException(status_code=401, detail="User session required.")
    allowed_roles = set(roles or ("user",))
    if session_user.role not in allowed_roles:
        raise HTTPException(status_code=403, detail="Khong du quyen truy cap workspace.")
    return session_user


def normalize_manager_filter_ids(
    request: Request,
    requested_ids: list[str] | None,
    available_manager_ids: list[str],
    current_user: AdminSessionUser,
) -> list[str]:
    allowed_ids = [current_user.id] if current_user.role == "manager" else list(available_manager_ids)
    query_has_manager_filter = "manager_ids" in request.query_params or "Manangers" in request.query_params

    if query_has_manager_filter:
        source_ids = requested_ids or []
    else:
        source_ids = [] if current_user.role == "admin" else list(allowed_ids)

    normalized = [manager_id for manager_id in source_ids if manager_id in allowed_ids]
    if not normalized:
        normalized = [] if current_user.role == "admin" else list(allowed_ids)

    request.session[MANAGER_FILTER_SESSION_KEY] = normalized
    return normalized
