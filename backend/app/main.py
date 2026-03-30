from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from .auth import ADMIN_SESSION_KEY
from .routers import api_admin, api_user, api_worker, web
from .store import store


def create_app() -> FastAPI:
    app = FastAPI(
        title="YouTube Upload Control Plane",
        version="0.1.0",
    )

    app.add_middleware(
        SessionMiddleware,
        secret_key=store.get_session_secret(),
        session_cookie=ADMIN_SESSION_KEY,
        same_site="lax",
        https_only=False,
    )

    app.include_router(web.router)
    app.include_router(api_user.router, prefix="/api")
    app.include_router(api_admin.router, prefix="/api")
    app.include_router(api_worker.router, prefix="/api")

    local_static_dir = Path(__file__).resolve().parent / "static"
    admin_theme_dir = local_static_dir / "admin-themes"

    if local_static_dir.exists():
        app.mount("/legacy", StaticFiles(directory=local_static_dir), name="legacy")
        app.mount("/static", StaticFiles(directory=local_static_dir), name="static")
    if admin_theme_dir.exists():
        app.mount("/admin-themes", StaticFiles(directory=admin_theme_dir), name="admin-themes")

    @app.get("/api/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
