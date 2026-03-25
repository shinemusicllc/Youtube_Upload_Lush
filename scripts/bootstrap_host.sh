#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/youtube-upload-lush}"

mkdir -p "$APP_DIR"
cd "$APP_DIR"

if ! command -v docker >/dev/null 2>&1; then
  apt-get update
  apt-get install -y docker.io docker-compose-v2
fi

if [ ! -f .env.production ]; then
  cp .env.production.example .env.production
  echo "Da tao .env.production, vui long cap nhat secret truoc khi start."
fi

docker compose -f infra/docker/host/docker-compose.yml up -d --build
