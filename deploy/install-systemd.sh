#!/usr/bin/env bash
set -euo pipefail

mode="${1:-eglfs}"
asset_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

bin_dir="${KLIPPERTOUCH_BIN_DIR:-/usr/local/bin}"
systemd_dir="${KLIPPERTOUCH_SYSTEMD_DIR:-/etc/systemd/system}"
config_dir="${KLIPPERTOUCH_CONFIG_DIR:-/home/tope/printer_data/config}"
kms_config="${config_dir}/klippertouch-eglfs-kms.json"
app_config="${config_dir}/KlipperTouch.conf"

if [ "$(id -u)" -ne 0 ]; then
    printf 'Run as root, for example: sudo %s %s\n' "$0" "$mode" >&2
    exit 1
fi

case "$mode" in
    eglfs|x11)
        ;;
    *)
        printf 'Usage: %s [eglfs|x11]\n' "$0" >&2
        exit 2
        ;;
esac

install -d "$bin_dir" "$systemd_dir" "$config_dir"
install -m 0755 "$asset_dir/klippertouch-start.sh" "$bin_dir/klippertouch-start.sh"
install -m 0755 "$asset_dir/klippertouch-eglfs-start.sh" "$bin_dir/klippertouch-eglfs-start.sh"
install -m 0644 "$asset_dir/klippertouch.service" "$systemd_dir/klippertouch.service"
install -m 0644 "$asset_dir/klippertouch-eglfs.service" "$systemd_dir/klippertouch-eglfs.service"
install -m 0644 "$asset_dir/klippertouch-eglfs-kms.json" "$kms_config"

if [ ! -f "$app_config" ] || [ "${KLIPPERTOUCH_OVERWRITE_CONFIG:-0}" = "1" ]; then
    install -m 0644 "$asset_dir/KlipperTouch.conf" "$app_config"
fi

systemctl daemon-reload

if [ "$mode" = "eglfs" ]; then
    systemctl disable klippertouch.service >/dev/null 2>&1 || true
    systemctl enable klippertouch-eglfs.service
    if [ "${KLIPPERTOUCH_START_AFTER_INSTALL:-0}" = "1" ]; then
        systemctl stop klippertouch.service >/dev/null 2>&1 || true
        systemctl restart klippertouch-eglfs.service
    fi
else
    systemctl disable klippertouch-eglfs.service >/dev/null 2>&1 || true
    systemctl enable klippertouch.service
    if [ "${KLIPPERTOUCH_START_AFTER_INSTALL:-0}" = "1" ]; then
        systemctl stop klippertouch-eglfs.service >/dev/null 2>&1 || true
        systemctl restart klippertouch.service
    fi
fi

