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
adopt_runtime_path "$APP_DIR" "$RUNTIME_DIR" ".venv" ".venv"
adopt_runtime_path "$APP_DIR" "$RUNTIME_DIR" ".backup" ".backup"
adopt_runtime_path "$APP_DIR" "$RUNTIME_DIR" "worker-data" "worker-data"
ensure_git_checkout "$APP_DIR" "$REPO_URL" "$BRANCH"
link_runtime_path "$APP_DIR" "$RUNTIME_DIR" ".venv" ".venv"
link_runtime_path "$APP_DIR" "$RUNTIME_DIR" ".backup" ".backup"
link_runtime_path "$APP_DIR" "$RUNTIME_DIR" "worker-data" "worker-data"

cd "$APP_DIR"

if [ ! -d "$RUNTIME_DIR/.venv" ]; then
  python3 -m venv .venv
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
EOF
  echo "Da tao /etc/youtube-upload-worker.env, vui long cap nhat gia tri truoc khi start service."
fi

systemctl daemon-reload
systemctl enable youtube-upload-worker.service
systemctl restart youtube-upload-worker.service
