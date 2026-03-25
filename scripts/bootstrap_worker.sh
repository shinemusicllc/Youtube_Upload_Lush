#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/youtube-upload-lush}"

apt-get update
apt-get install -y python3 python3-venv ffmpeg

mkdir -p "$APP_DIR"
cd "$APP_DIR"

python3 -m venv .venv
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
