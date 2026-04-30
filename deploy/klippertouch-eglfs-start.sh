#!/usr/bin/env bash
set -euo pipefail

log_file="${KLIPPERTOUCH_LOG:-/home/tope/printer_data/logs/klippertouch-eglfs.log}"
eglfs_client="${KLIPPERTOUCH_EGLFS_CLIENT:-/home/tope/klippertouch/venv/bin/klippertouch --config /home/tope/printer_data/config/KlipperTouch.conf --allow-controls --fullscreen}"

export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"
export QT_QPA_PLATFORM="${QT_QPA_PLATFORM:-eglfs}"
export QT_QPA_EGLFS_INTEGRATION="${QT_QPA_EGLFS_INTEGRATION:-eglfs_kms}"
export QT_QPA_EGLFS_KMS_CONFIG="${QT_QPA_EGLFS_KMS_CONFIG:-/home/tope/printer_data/config/klippertouch-eglfs-kms.json}"
export QT_QPA_EGLFS_ALWAYS_SET_MODE="${QT_QPA_EGLFS_ALWAYS_SET_MODE:-1}"
export QSG_RHI_BACKEND="${QSG_RHI_BACKEND:-opengl}"
export QSG_INFO="${QSG_INFO:-0}"
export KLIPPERTOUCH_DISPLAY_ROTATION="${KLIPPERTOUCH_DISPLAY_ROTATION:-right}"

mkdir -p "${log_file%/*}" "$XDG_RUNTIME_DIR" 2>/dev/null || true
printf 'KlipperTouch: starting EGLFS with %s/%s config %s rotation %s\n' \
    "$QT_QPA_PLATFORM" "$QT_QPA_EGLFS_INTEGRATION" "$QT_QPA_EGLFS_KMS_CONFIG" \
    "$KLIPPERTOUCH_DISPLAY_ROTATION" >> "$log_file" 2>/dev/null || true

exec /bin/bash -c "$eglfs_client" >> "$log_file" 2>&1
