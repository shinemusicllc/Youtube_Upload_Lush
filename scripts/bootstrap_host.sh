#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/youtube-upload-lush}"
DEPLOY_MODE="${DEPLOY_MODE:-systemd}"

mkdir -p "$APP_DIR"
cd "$APP_DIR"

if [ "$DEPLOY_MODE" = "docker" ]; then
  if ! command -v docker >/dev/null 2>&1; then
    apt-get update
    apt-get install -y docker.io docker-compose-v2
  fi

  if [ ! -f .env.production ]; then
    cp .env.production.example .env.production
    echo "Da tao .env.production, vui long cap nhat secret truoc khi start."
  fi

  docker compose -f infra/docker/host/docker-compose.yml up -d --build
  exit 0
fi

if ! command -v python3 >/dev/null 2>&1; then
  apt-get update
  apt-get install -y python3 python3-venv python3-pip
fi

if [ ! -d .venv ]; then
  python3 -m venv .venv
fi

./.venv/bin/pip install --upgrade pip
./.venv/bin/pip install -r backend/requirements.txt

cp infra/systemd/youtube-upload-web.service /etc/systemd/system/youtube-upload-web.service
systemctl daemon-reload
systemctl enable --now youtube-upload-web.service
