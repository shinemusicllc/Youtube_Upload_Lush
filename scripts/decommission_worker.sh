#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/youtube-upload-lush}"
RUNTIME_DIR="${RUNTIME_DIR:-/opt/youtube-upload-lush-runtime}"
SERVICE_NAME="youtube-upload-worker.service"
WORKER_SYSTEM_USER="${WORKER_SYSTEM_USER:-ytworker}"
WORKER_SYSTEM_HOME="$(getent passwd "$WORKER_SYSTEM_USER" 2>/dev/null | cut -d: -f6 || true)"

systemctl stop "$SERVICE_NAME" || true
systemctl disable "$SERVICE_NAME" || true
rm -f "/etc/systemd/system/$SERVICE_NAME"
rm -f /etc/youtube-upload-worker.env
systemctl daemon-reload
systemctl reset-failed "$SERVICE_NAME" || true

pkill -f "python -m workers.agent.main" || true
pkill -f "workers.agent.main" || true
pkill -u "$WORKER_SYSTEM_USER" || true

rm -rf "$APP_DIR" "$RUNTIME_DIR"
rm -rf "${APP_DIR}.legacy-"*
rm -rf "${APP_DIR}.clone-"*
rm -rf /root/.config/google-chrome
rm -rf /root/.cache/google-chrome
rm -rf /root/.config/chromium
rm -rf /root/.cache/chromium
rm -rf /root/snap/chromium
rm -rf /root/Downloads/youtube-upload-lush
if id -u "$WORKER_SYSTEM_USER" >/dev/null 2>&1; then
  userdel -r "$WORKER_SYSTEM_USER" || true
fi
if getent group "$WORKER_SYSTEM_USER" >/dev/null 2>&1; then
  groupdel "$WORKER_SYSTEM_USER" || true
fi
if [ -n "$WORKER_SYSTEM_HOME" ]; then
  rm -rf "$WORKER_SYSTEM_HOME"
fi
