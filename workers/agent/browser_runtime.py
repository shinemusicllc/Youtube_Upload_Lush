from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import quote
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


def _truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def _pid_is_running(pid: int | None) -> bool:
    if not pid or pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def _terminate_pid(pid: int | None) -> None:
    if not pid or pid <= 0:
        return
    try:
        os.kill(pid, signal.SIGTERM)
    except OSError:
        return

    deadline = time.time() + 5
    while time.time() < deadline:
        if not _pid_is_running(pid):
            return
        time.sleep(0.15)

    try:
        os.kill(pid, signal.SIGKILL)
    except OSError:
        return


@dataclass
class BrowserRuntimeConfig:
    enabled: bool
    public_base_url: str
    start_url: str
    bind_host: str
    novnc_web_dir: Path
    chromium_bin: str
    profile_root: Path
    session_root: Path
    viewport: str


class BrowserRuntimeManager:
    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir

    def load_config(self) -> BrowserRuntimeConfig:
        profile_root = Path(os.getenv("BROWSER_SESSION_PROFILE_ROOT", str(self.data_dir / "browser-profiles")))
        session_root = Path(os.getenv("BROWSER_SESSION_STATE_ROOT", str(self.data_dir / "browser-sessions")))
        chromium_bin = os.getenv("BROWSER_SESSION_CHROMIUM_BIN", "").strip()
        if not chromium_bin:
            chromium_bin = self._resolve_executable(["google-chrome-stable", "google-chrome", "chromium-browser", "chromium"])
        return BrowserRuntimeConfig(
            enabled=_truthy(os.getenv("BROWSER_SESSION_ENABLED")),
            public_base_url=str(os.getenv("BROWSER_SESSION_PUBLIC_BASE_URL", "")).strip().rstrip("/"),
            start_url=str(os.getenv("BROWSER_SESSION_START_URL", "https://studio.youtube.com")).strip()
            or "https://studio.youtube.com",
            bind_host=str(os.getenv("BROWSER_SESSION_BIND_HOST", "0.0.0.0")).strip() or "0.0.0.0",
            novnc_web_dir=Path(os.getenv("BROWSER_SESSION_NOVNC_WEB_DIR", "/usr/share/novnc")),
            chromium_bin=chromium_bin,
            profile_root=profile_root,
            session_root=session_root,
            viewport=str(os.getenv("BROWSER_SESSION_VIEWPORT", "1440,900")).strip() or "1440,900",
        )

    @staticmethod
    def _resolve_executable(candidates: list[str]) -> str:
        for candidate in candidates:
            resolved = shutil.which(candidate)
            if resolved:
                return resolved
        return candidates[0]

    def ensure_available(self, config: BrowserRuntimeConfig) -> None:
        if not config.enabled:
            raise ValueError("Browser session chua duoc bat tren worker.")
        if sys.platform != "linux":
            raise ValueError("Browser session chi ho tro host Linux/Ubuntu.")
        if not config.public_base_url:
            raise ValueError("Thieu BROWSER_SESSION_PUBLIC_BASE_URL tren worker.")
        if not config.novnc_web_dir.exists():
            raise ValueError(f"Khong tim thay noVNC web dir tai {config.novnc_web_dir}.")
        if not shutil.which(config.chromium_bin):
            raise ValueError(f"Khong tim thay Chromium binary '{config.chromium_bin}'.")
        for binary in ("Xvfb", "openbox", "x11vnc", "websockify"):
            if not shutil.which(binary):
                raise ValueError(f"Khong tim thay binary '{binary}'.")

    @staticmethod
    def _ensure_chromium_preferences(profile_dir: Path) -> None:
        default_dir = profile_dir / "Default"
        default_dir.mkdir(parents=True, exist_ok=True)
        preferences_path = default_dir / "Preferences"
        preferences: dict[str, Any] = {}
        if preferences_path.exists():
            try:
                preferences = json.loads(preferences_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                preferences = {}

        preferences["credentials_enable_service"] = False
        profile_prefs = preferences.get("profile")
        if not isinstance(profile_prefs, dict):
            profile_prefs = {}
        profile_prefs["password_manager_enabled"] = False
        profile_prefs["password_manager_leak_detection"] = False
        preferences["profile"] = profile_prefs

        browser_prefs = preferences.get("browser")
        if not isinstance(browser_prefs, dict):
            browser_prefs = {}
        browser_prefs["show_profile_picker_on_startup"] = False
        browser_prefs["check_default_browser"] = False
        preferences["browser"] = browser_prefs

        signin_prefs = preferences.get("signin")
        if not isinstance(signin_prefs, dict):
            signin_prefs = {}
        signin_prefs["allowed_on_next_startup"] = False
        preferences["signin"] = signin_prefs

        preferences_path.write_text(
            json.dumps(preferences, ensure_ascii=True, separators=(",", ":")),
            encoding="utf-8",
        )

    @staticmethod
    def _build_novnc_url(base_url: str, web_port: int, access_password: str) -> str:
        encoded_password = quote(access_password, safe="")
        return (
            f"{base_url}:{web_port}/vnc.html?autoconnect=1&resize=scale&view_only=0"
            f"#password={encoded_password}"
        )

    def launch(self, record: dict[str, Any]) -> dict[str, Any]:
        config = self.load_config()
        self.ensure_available(config)

        session_id = str(record["session_id"])
        profile_key = str(record["profile_key"])
        session_dir = config.session_root / session_id
        profile_dir = config.profile_root / profile_key
        log_dir = session_dir / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        profile_dir.mkdir(parents=True, exist_ok=True)
        self._ensure_chromium_preferences(profile_dir)

        password = str(record["access_password"])
        password_file = session_dir / "vnc.passwd"
        subprocess.run(
            ["x11vnc", "-storepasswd", password, str(password_file)],
            check=True,
            capture_output=True,
            text=True,
        )

        display_number = int(record["display_number"])
        display = f":{display_number}"
        viewport = config.viewport if "x" not in config.viewport else config.viewport.replace("x", ",")
        viewport_width, viewport_height = [part.strip() for part in viewport.split(",", 1)]
        geometry = f"{viewport_width}x{viewport_height}x24"

        xvfb_log = (log_dir / "xvfb.log").open("ab")
        xvfb = subprocess.Popen(
            ["Xvfb", display, "-screen", "0", geometry, "-ac", "-nolisten", "tcp"],
            stdout=xvfb_log,
            stderr=subprocess.STDOUT,
        )
        time.sleep(0.6)
        if xvfb.poll() is not None:
            raise ValueError("Khong the khoi dong Xvfb cho browser session.")

        env = os.environ.copy()
        env["DISPLAY"] = display
        env["HOME"] = str(profile_dir)
        env["XDG_RUNTIME_DIR"] = str(session_dir / "xdg")
        Path(env["XDG_RUNTIME_DIR"]).mkdir(parents=True, exist_ok=True)

        openbox_log = (log_dir / "openbox.log").open("ab")
        openbox = subprocess.Popen(["openbox"], env=env, stdout=openbox_log, stderr=subprocess.STDOUT)
        time.sleep(0.4)

        chromium_log = (log_dir / "chromium.log").open("ab")
        chromium = subprocess.Popen(
            [
                config.chromium_bin,
                f"--user-data-dir={profile_dir}",
                "--no-first-run",
                "--no-default-browser-check",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-features=PasswordManagerOnboarding,PasswordsImport,Translate,MediaRouter,SigninIntercept,DiceWebSigninInterception",
                "--disable-sync",
                "--disable-background-networking",
                "--window-position=0,0",
                f"--window-size={viewport_width},{viewport_height}",
                f"--remote-debugging-port={record['debug_port']}",
                config.start_url,
            ],
            env=env,
            stdout=chromium_log,
            stderr=subprocess.STDOUT,
        )
        time.sleep(1.5)
        if chromium.poll() is not None:
            raise ValueError("Chromium da thoat ngay sau khi khoi dong.")

        x11vnc_log = (log_dir / "x11vnc.log").open("ab")
        x11vnc = subprocess.Popen(
            [
                "x11vnc",
                "-display",
                display,
                "-rfbport",
                str(record["vnc_port"]),
                "-rfbauth",
                str(password_file),
                "-forever",
                "-shared",
                "-localhost",
            ],
            stdout=x11vnc_log,
            stderr=subprocess.STDOUT,
        )
        time.sleep(0.8)
        if x11vnc.poll() is not None:
            raise ValueError("Khong the khoi dong x11vnc cho browser session.")

        websockify_log = (log_dir / "websockify.log").open("ab")
        websockify = subprocess.Popen(
            [
                "websockify",
                "--web",
                str(config.novnc_web_dir),
                f"{config.bind_host}:{record['web_port']}",
                f"127.0.0.1:{record['vnc_port']}",
            ],
            stdout=websockify_log,
            stderr=subprocess.STDOUT,
        )
        time.sleep(0.8)
        if websockify.poll() is not None:
            raise ValueError("Khong the khoi dong websockify/noVNC cho browser session.")

        novnc_url = self._build_novnc_url(
            config.public_base_url,
            int(record["web_port"]),
            password,
        )
        return {
            "profile_path": str(profile_dir),
            "session_path": str(session_dir),
            "password_file": str(password_file),
            "novnc_url": novnc_url,
            "xvfb_pid": xvfb.pid,
            "openbox_pid": openbox.pid,
            "chromium_pid": chromium.pid,
            "x11vnc_pid": x11vnc.pid,
            "websockify_pid": websockify.pid,
        }

    @staticmethod
    def _session_record_path(session_path: Path) -> Path:
        return session_path / "session.json"

    def save_session_record(self, record: dict[str, Any]) -> None:
        session_path = Path(str(record.get("session_path") or "").strip())
        if not session_path:
            return
        session_path.mkdir(parents=True, exist_ok=True)
        payload = {
            key: value
            for key, value in record.items()
            if isinstance(value, (str, int, float, bool)) or value is None
        }
        self._session_record_path(session_path).write_text(
            json.dumps(payload, ensure_ascii=True, separators=(",", ":")),
            encoding="utf-8",
        )

    def load_persisted_sessions(self) -> dict[str, dict[str, Any]]:
        config = self.load_config()
        if not config.session_root.exists():
            return {}

        sessions: dict[str, dict[str, Any]] = {}
        for session_dir in config.session_root.iterdir():
            if not session_dir.is_dir():
                continue
            record_path = self._session_record_path(session_dir)
            if not record_path.exists():
                continue
            try:
                record = json.loads(record_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            session_id = str(record.get("session_id") or session_dir.name).strip()
            if not session_id:
                continue
            record["session_id"] = session_id
            record["session_path"] = str(record.get("session_path") or session_dir)
            sessions[session_id] = record
        return sessions

    def stop(self, record: dict[str, Any]) -> None:
        for key in ("websockify_pid", "x11vnc_pid", "chromium_pid", "openbox_pid", "xvfb_pid"):
            _terminate_pid(int(record.get(key) or 0) or None)
        session_path = str(record.get("session_path") or "").strip()
        if session_path:
            shutil.rmtree(session_path, ignore_errors=True)

    def delete_profile(self, profile_key: str) -> None:
        cleaned_key = str(profile_key or "").strip()
        if not cleaned_key:
            return
        config = self.load_config()
        profile_dir = config.profile_root / cleaned_key
        try:
            profile_dir.relative_to(config.profile_root)
        except ValueError:
            raise ValueError("Profile path cleanup nam ngoai browser profile root.")
        shutil.rmtree(profile_dir, ignore_errors=True)

    def is_running(self, record: dict[str, Any]) -> bool:
        chromium_pid = int(record.get("chromium_pid") or 0) or None
        websockify_pid = int(record.get("websockify_pid") or 0) or None
        x11vnc_pid = int(record.get("x11vnc_pid") or 0) or None
        return all(_pid_is_running(pid) for pid in (chromium_pid, websockify_pid, x11vnc_pid))

    def inspect(self, record: dict[str, Any]) -> dict[str, Any]:
        debug_port = int(record.get("debug_port") or 0)
        if debug_port <= 0:
            raise ValueError("Browser session chua co debug_port hop le.")

        try:
            with urlopen(f"http://127.0.0.1:{debug_port}/json/list", timeout=5) as response:
                tabs = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise ValueError("Khong the doc Chromium remote debugging endpoint.") from exc

        page_tabs = [item for item in tabs if item.get("type") == "page"]
        current = next(
            (item for item in page_tabs if "studio.youtube.com" in str(item.get("url") or "")),
            page_tabs[0] if page_tabs else None,
        )
        current_url = str((current or {}).get("url") or "").strip()
        current_title = str((current or {}).get("title") or "").strip()
        detected = self._extract_channel_identity(current_url, current_title)
        return {
            "current_url": current_url,
            "current_title": current_title,
            "channel_id": detected.get("channel_id"),
            "channel_name": detected.get("channel_name"),
        }

    @staticmethod
    def _extract_channel_identity(url: str, title: str) -> dict[str, str | None]:
        channel_id = None
        for marker in ("/channel/", "channel_id="):
            if marker == "/channel/" and marker in url:
                channel_id = url.split("/channel/", 1)[1].split("/", 1)[0].split("?", 1)[0]
                break
            if marker == "channel_id=" and marker in url:
                channel_id = url.split("channel_id=", 1)[1].split("&", 1)[0]
                break

        cleaned_title = title.replace(" - YouTube Studio", "").replace(" - YouTube", "").strip()
        if cleaned_title and cleaned_title.lower() in {"youtube studio", "dashboard"}:
            cleaned_title = None

        return {
            "channel_id": channel_id or None,
            "channel_name": cleaned_title or channel_id or None,
        }
