#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/youtube-upload-lush}"
RUNTIME_DIR="${RUNTIME_DIR:-/opt/youtube-upload-lush-runtime}"
REPO_URL="${REPO_URL:-https://github.com/shinemusicllc/Youtube_Upload_Lush.git}"
BRANCH="${BRANCH:-main}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$SCRIPT_DIR/git_runtime_layout.sh"

apt-get update
apt-get install -y ffmpeg

mkdir -p "$RUNTIME_DIR"
install_base_packages
mkdir -p "$RUNTIME_DIR/.backup" "$RUNTIME_DIR/worker-data"
adopt_runtime_path "$APP_DIR" "$RUNTIME_DIR" ".venv" ".venv"
adopt_runtime_path "$APP_DIR" "$RUNTIME_DIR" ".backup" ".backup"
adopt_runtime_path "$APP_DIR" "$RUNTIME_DIR" "worker-data" "worker-data"
ensure_git_checkout "$APP_DIR" "$REPO_URL" "$BRANCH"
link_runtime_path "$APP_DIR" "$RUNTIME_DIR" ".venv" ".venv"
link_runtime_path "$APP_DIR" "$RUNTIME_DIR" ".backup" ".backup"
link_runtime_path "$APP_DIR" "$RUNTIME_DIR" "worker-data" "worker-data"

cd "$APP_DIR"

if [ ! -d "$RUNTIME_DIR/.venv" ]; then
  python3 -m venv "$RUNTIME_DIR/.venv"
fi
. .venv/bin/activate
pip install --upgrade pip
pip install -r workers/agent/requirements.txt

cp infra/systemd/youtube-upload-worker.service /etc/systemd/system/youtube-upload-worker.service

if [ ! -f /etc/youtube-upload-worker.env ]; then
  cat >/etc/youtube-upload-worker.env <<'EOF'
CONTROL_PLANE_URL=https://your-domain.example
WORKER_SHARED_SECRET=replace-with-a-long-random-worker-secret
WORKER_ID=worker-01
WORKER_NAME=worker-01
WORKER_MANAGER=system
WORKER_GROUP=workers
WORKER_CAPACITY=1
WORKER_THREADS=1
WORKER_HEARTBEAT_SECONDS=15
WORKER_POLL_SECONDS=5
WORKER_SIMULATE_JOBS=false
WORKER_EXECUTE_JOBS=false
WORKER_SIMULATE_STEP_SECONDS=2.5
WORKER_UPLOAD_TO_YOUTUBE=false
YOUTUBE_UPLOAD_CHUNK_BYTES=8388608
BROWSER_SESSION_ENABLED=0
BROWSER_SESSION_PUBLIC_BASE_URL=http://worker-public-ip
BROWSER_SESSION_DISPLAY_BASE=90
BROWSER_SESSION_VNC_PORT_BASE=15900
BROWSER_SESSION_WEB_PORT_BASE=16080
BROWSER_SESSION_DEBUG_PORT_BASE=19220
BROWSER_SESSION_BIND_HOST=0.0.0.0
BROWSER_SESSION_START_URL=https://studio.youtube.com
BROWSER_SESSION_NOVNC_WEB_DIR=/usr/share/novnc
BROWSER_SESSION_CHROMIUM_BIN=chromium-browser
EOF
  echo "Da tao /etc/youtube-upload-worker.env, vui long cap nhat gia tri truoc khi start service."
fi

set -a
. /etc/youtube-upload-worker.env
set +a

if [ "${BROWSER_SESSION_ENABLED:-0}" = "1" ]; then
  apt-get install -y xvfb openbox x11vnc websockify novnc || true

  # ---------- Install a REAL (non-snap) Chromium ----------
  # On Ubuntu 22.04+, the apt "chromium-browser" package is a snap
  # transitional wrapper. Snap chromium ignores --user-data-dir and
  # stores all state globally, which breaks multi-user profile isolation.
  #
  # Strategy:
  #   1. Remove the snap wrapper if present.
  #   2. Try installing ungoogled-chromium via the official PPA.
  #   3. Fallback: download Chromium deb from the Debian snapshot.
  #   4. Last resort: keep whatever is already installed.

  _install_native_chromium() {
    # Remove snap chromium if installed
    if snap list chromium >/dev/null 2>&1; then
      echo "[browser-setup] Removing snap chromium to avoid profile isolation bugs..."
      snap remove --purge chromium || true
    fi
    # Also remove the snap wrapper apt package
    apt-get remove -y chromium-browser 2>/dev/null || true

    # Option A: Use playwright bundled chromium (already in venv)
    if [ -d "$RUNTIME_DIR/.venv" ]; then
      . "$RUNTIME_DIR/.venv/bin/activate"
      pip install playwright >/dev/null 2>&1 || true
      python -m playwright install chromium 2>/dev/null || true
      PW_CHROMIUM=$(python -c "
from pathlib import Path
import subprocess, json, sys
try:
    r = subprocess.run([sys.executable, '-m', 'playwright', 'install', '--dry-run'], capture_output=True, text=True)
    # Find chromium path
    for line in Path.home().rglob('chrome-linux/chrome'):
        print(line); sys.exit(0)
    for line in Path('/root/.cache/ms-playwright').rglob('chrome-linux/chrome'):
        print(line); sys.exit(0)
except: pass
" 2>/dev/null || true)
      if [ -n "$PW_CHROMIUM" ] && [ -x "$PW_CHROMIUM" ]; then
        echo "[browser-setup] Using Playwright-bundled Chromium: $PW_CHROMIUM"
        # Update env file
        sed -i "s|^BROWSER_SESSION_CHROMIUM_BIN=.*|BROWSER_SESSION_CHROMIUM_BIN=$PW_CHROMIUM|" /etc/youtube-upload-worker.env 2>/dev/null || true
        return 0
      fi
    fi

    # Option B: Install chromium from prebuilt .deb
    apt-get install -y chromium 2>/dev/null && return 0 || true

    # Option C: Try ungoogled-chromium PPA
    add-apt-repository -y ppa:nicholasgasior/nicholasgasior 2>/dev/null || true
    apt-get update 2>/dev/null || true
    apt-get install -y ungoogled-chromium 2>/dev/null && {
      NATIVE_BIN=$(command -v ungoogled-chromium 2>/dev/null || command -v chromium 2>/dev/null || true)
      if [ -n "$NATIVE_BIN" ]; then
        sed -i "s|^BROWSER_SESSION_CHROMIUM_BIN=.*|BROWSER_SESSION_CHROMIUM_BIN=$NATIVE_BIN|" /etc/youtube-upload-worker.env 2>/dev/null || true
      fi
      return 0
    } || true

    # Fallback: reinstall apt chromium-browser (may be snap, but _build_browser_env handles it)
    apt-get install -y chromium-browser 2>/dev/null || true
    if ! command -v chromium-browser >/dev/null 2>&1 && ! command -v chromium >/dev/null 2>&1; then
      snap install chromium || true
    fi
  }
  _install_native_chromium

  for binary in Xvfb openbox x11vnc websockify; do
    if ! command -v "$binary" >/dev/null 2>&1; then
      echo "Missing required browser-session binary: $binary" >&2
      exit 1
    fi
  done
  if [ ! -d "${BROWSER_SESSION_NOVNC_WEB_DIR:-/usr/share/novnc}" ] || [ ! -f "${BROWSER_SESSION_NOVNC_WEB_DIR:-/usr/share/novnc}/vnc.html" ]; then
    echo "Missing noVNC web assets at ${BROWSER_SESSION_NOVNC_WEB_DIR:-/usr/share/novnc}" >&2
    exit 1
  fi
  if ! command -v "${BROWSER_SESSION_CHROMIUM_BIN:-chromium-browser}" >/dev/null 2>&1 && ! command -v chromium >/dev/null 2>&1; then
    echo "Missing Chromium binary for browser session." >&2
    exit 1
  fi
fi

systemctl daemon-reload
systemctl enable youtube-upload-worker.service
systemctl restart youtube-upload-worker.service
