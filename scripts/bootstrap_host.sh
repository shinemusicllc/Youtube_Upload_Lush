#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/youtube-upload-lush}"
RUNTIME_DIR="${RUNTIME_DIR:-/opt/youtube-upload-lush-runtime}"
REPO_URL="${REPO_URL:-https://github.com/shinemusicllc/Youtube_Upload_Lush.git}"
BRANCH="${BRANCH:-main}"
DEPLOY_MODE="${DEPLOY_MODE:-systemd}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$SCRIPT_DIR/git_runtime_layout.sh"

mkdir -p "$RUNTIME_DIR"

install_base_packages
adopt_runtime_path "$APP_DIR" "$RUNTIME_DIR" ".env" ".env"
adopt_runtime_path "$APP_DIR" "$RUNTIME_DIR" ".venv" ".venv"
adopt_runtime_path "$APP_DIR" "$RUNTIME_DIR" ".backup" ".backup"
adopt_runtime_path "$APP_DIR" "$RUNTIME_DIR" "backend/data" "backend-data"
ensure_git_checkout "$APP_DIR" "$REPO_URL" "$BRANCH"
link_runtime_path "$APP_DIR" "$RUNTIME_DIR" ".env" ".env"
link_runtime_path "$APP_DIR" "$RUNTIME_DIR" ".venv" ".venv"
link_runtime_path "$APP_DIR" "$RUNTIME_DIR" ".backup" ".backup"
link_runtime_path "$APP_DIR" "$RUNTIME_DIR" "backend/data" "backend-data"

cd "$APP_DIR"

if [ ! -f "$RUNTIME_DIR/.env" ]; then
  cp .env.example "$RUNTIME_DIR/.env"
  echo "Da tao $RUNTIME_DIR/.env, vui long cap nhat secret truoc khi start."
fi

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

if [ ! -d "$RUNTIME_DIR/.venv" ]; then
  python3 -m venv .venv
fi

./.venv/bin/pip install --upgrade pip
./.venv/bin/pip install -r backend/requirements.txt

cp infra/systemd/youtube-upload-web.service /etc/systemd/system/youtube-upload-web.service
systemctl daemon-reload
systemctl enable --now youtube-upload-web.service
