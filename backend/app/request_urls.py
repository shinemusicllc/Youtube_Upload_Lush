from __future__ import annotations

import os

from fastapi import Request


def resolve_external_base_url(request: Request, *, env_key: str | None = None) -> str:
    configured = str(os.getenv(env_key or "", "")).strip() if env_key else ""
    if configured:
        return configured.rstrip("/")

    forwarded_proto = str(request.headers.get("x-forwarded-proto") or "").split(",", 1)[0].strip()
    forwarded_host = str(request.headers.get("x-forwarded-host") or "").split(",", 1)[0].strip()
    forwarded_prefix = str(request.headers.get("x-forwarded-prefix") or "").split(",", 1)[0].strip()

    scheme = forwarded_proto or str(request.url.scheme or "").strip() or "http"
    host = forwarded_host or str(request.headers.get("host") or "").strip()
    if host:
        normalized_prefix = ""
        if forwarded_prefix:
            normalized_prefix = forwarded_prefix if forwarded_prefix.startswith("/") else f"/{forwarded_prefix}"
            normalized_prefix = normalized_prefix.rstrip("/")
        return f"{scheme}://{host}{normalized_prefix}".rstrip("/")

    return str(request.base_url).rstrip("/")


def resolve_worker_bootstrap_control_plane_url(request: Request) -> str:
    return resolve_external_base_url(request, env_key="WORKER_BOOTSTRAP_CONTROL_PLANE_URL")
