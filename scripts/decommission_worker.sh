#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/youtube-upload-lush}"
RUNTIME_DIR="${RUNTIME_DIR:-/opt/youtube-upload-lush-runtime}"
SERVICE_NAME="youtube-upload-worker.service"

systemctl stop "$SERVICE_NAME" || true
systemctl disable "$SERVICE_NAME" || true
rm -f "/etc/systemd/system/$SERVICE_NAME"
rm -f /etc/youtube-upload-worker.env
systemctl daemon-reload
systemctl reset-failed "$SERVICE_NAME" || true

pkill -f "python -m workers.agent.main" || true
pkill -f "workers.agent.main" || true

rm -rf "$APP_DIR" "$RUNTIME_DIR"
rm -rf "${APP_DIR}.legacy-"*
rm -rf "${APP_DIR}.clone-"*
