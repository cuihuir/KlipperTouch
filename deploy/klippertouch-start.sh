#!/usr/bin/env bash
set -euo pipefail

wait_for_xrandr() {
    local attempts="${1:-20}"
    local delay="${2:-0.3}"

    for _ in $(seq 1 "$attempts"); do
        if xrandr --query >/dev/null 2>&1; then
            return 0
        fi
        sleep "$delay"
    done
    return 1
}

wait_for_touch_hid() {
    local pattern="${1:-}"
    local attempts="${2:-20}"
    local delay="${3:-0.5}"

    if [ -z "$pattern" ]; then
        return 0
    fi

    for _ in $(seq 1 "$attempts"); do
        if ls /sys/bus/hid/drivers/hid-multitouch/ 2>/dev/null | grep -q "$pattern"; then
            return 0
        fi
        sleep "$delay"
    done
    return 1
}

if [ "${1:-}" = "--xclient" ]; then
    display="${KLIPPERTOUCH_DISPLAY:-:0}"
    output="${KLIPPERTOUCH_OUTPUT:-HDMI-1}"
    rotation="${KLIPPERTOUCH_ROTATE:-right}"
    reset_output="${KLIPPERTOUCH_RESET_OUTPUT:-0}"
    touch_pattern="${KLIPPERTOUCH_TOUCH_HID_PATTERN:-}"
    log_file="${KLIPPERTOUCH_LOG:-/home/tope/printer_data/logs/klippertouch.log}"
    xclient="${KLIPPERTOUCH_XCLIENT:-/home/tope/klippertouch/venv/bin/klippertouch --config /home/tope/printer_data/config/KlipperTouch.conf --allow-controls --fullscreen}"
    render_backend="${KLIPPERTOUCH_RENDER_BACKEND:-software}"

    export DISPLAY="$display"
    export QT_QPA_PLATFORM="${QT_QPA_PLATFORM:-xcb}"
    if [ "$render_backend" = "software" ]; then
        export QT_QUICK_BACKEND="${QT_QUICK_BACKEND:-software}"
        unset QT_XCB_GL_INTEGRATION
        unset QSG_RHI_BACKEND
    elif [ "$render_backend" = "xcb_egl" ]; then
        unset QT_QUICK_BACKEND
        export QT_XCB_GL_INTEGRATION="${QT_XCB_GL_INTEGRATION:-xcb_egl}"
        export QSG_RHI_BACKEND="${QSG_RHI_BACKEND:-opengl}"
    fi
    export QSG_INFO="${QSG_INFO:-0}"
    mkdir -p "${log_file%/*}" 2>/dev/null || true
    printf 'KlipperTouch: starting xclient on %s with %s backend %s\n' \
        "$display" "$QT_QPA_PLATFORM" "$render_backend" >> "$log_file" 2>/dev/null || true
    xset s off -dpms 2>/dev/null || true
    xsetroot -solid black 2>/dev/null || true

    if ! wait_for_xrandr 30 0.3; then
        printf 'KlipperTouch: xrandr did not become available on %s\n' "$display" >&2
    fi

    if [ "$reset_output" = "1" ]; then
        xrandr --output "$output" --off 2>/dev/null || true
        wait_for_touch_hid "$touch_pattern" 20 0.5 || true
    fi

    xrandr --output "$output" --preferred --rotate "$rotation" 2>/dev/null || true
    xset s off -dpms 2>/dev/null || true
    xsetroot -solid black 2>/dev/null || true

    exec /bin/bash -c "$xclient" >> "$log_file" 2>&1
fi

export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"
display="${KLIPPERTOUCH_DISPLAY:-:0}"

exec /usr/bin/xinit "$0" --xclient -- "$display" -keeptty -seat seat0 -nolisten tcp vt7 -novtswitch
