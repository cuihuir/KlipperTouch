#!/usr/bin/env bash
set -euo pipefail

usage() {
    cat <<'EOF'
Usage: update-installed-app.sh [--no-restart] [--service NAME] [CHECKOUT_DIR]

Synchronize a KlipperTouch source checkout into the virtualenv package used by
the systemd service, then restart the service.

Defaults match the RK3566 printer deployment:
  CHECKOUT_DIR              current directory
  KLIPPERTOUCH_VENV         /home/tope/klippertouch/venv
  KLIPPERTOUCH_SERVICE      klippertouch-eglfs.service

Examples:
  cd /home/tope/KlipperTouch
  ./deploy/update-installed-app.sh

  KLIPPERTOUCH_VENV=/home/tope/klippertouch/venv \
    ./deploy/update-installed-app.sh --service klippertouch-eglfs.service
EOF
}

restart_service=1
service_name="${KLIPPERTOUCH_SERVICE:-klippertouch-eglfs.service}"
checkout_dir="${KLIPPERTOUCH_CHECKOUT:-}"
venv_dir="${KLIPPERTOUCH_VENV:-/home/tope/klippertouch/venv}"

while [ "$#" -gt 0 ]; do
    case "$1" in
        --help|-h)
            usage
            exit 0
            ;;
        --no-restart)
            restart_service=0
            shift
            ;;
        --service)
            if [ "$#" -lt 2 ]; then
                printf 'error: --service requires a service name\n' >&2
                exit 2
            fi
            service_name="$2"
            shift 2
            ;;
        -*)
            printf 'error: unknown option: %s\n' "$1" >&2
            usage >&2
            exit 2
            ;;
        *)
            if [ -n "$checkout_dir" ]; then
                printf 'error: multiple checkout directories provided\n' >&2
                exit 2
            fi
            checkout_dir="$1"
            shift
            ;;
    esac
done

checkout_dir="${checkout_dir:-$PWD}"
source_pkg="$checkout_dir/src/klippertouch"
python_bin="$venv_dir/bin/python"

if [ ! -d "$checkout_dir" ]; then
    printf 'error: checkout directory does not exist: %s\n' "$checkout_dir" >&2
    exit 1
fi

if [ ! -d "$source_pkg" ]; then
    printf 'error: source package does not exist: %s\n' "$source_pkg" >&2
    exit 1
fi

if [ ! -x "$python_bin" ]; then
    printf 'error: virtualenv python is not executable: %s\n' "$python_bin" >&2
    exit 1
fi

if ! command -v rsync >/dev/null 2>&1; then
    printf 'error: rsync is required but was not found\n' >&2
    exit 1
fi

site_dir="$("$python_bin" - <<'PY'
import site

for path in site.getsitepackages():
    if path.endswith("site-packages"):
        print(path)
        break
else:
    raise SystemExit("site-packages directory not found")
PY
)"

target_pkg="$site_dir/klippertouch"

if [ ! -d "$target_pkg" ]; then
    printf 'error: installed package does not exist: %s\n' "$target_pkg" >&2
    exit 1
fi

printf 'KlipperTouch update\n'
printf '  checkout: %s\n' "$checkout_dir"
printf '  source:   %s\n' "$source_pkg"
printf '  target:   %s\n' "$target_pkg"
printf '  venv:     %s\n' "$venv_dir"
printf '  service:  %s\n' "$service_name"

if git -C "$checkout_dir" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    printf '  revision: '
    git -C "$checkout_dir" log -1 --oneline --decorate
fi

printf '\nSyncing package files...\n'
rsync -a --delete "$source_pkg/" "$target_pkg/"

printf 'Compiling Python files...\n'
"$python_bin" -m compileall -q "$target_pkg"

if [ -f "$source_pkg/qml/panels/JobStatusPanel.qml" ] && command -v sha256sum >/dev/null 2>&1; then
    printf '\nChecksum check:\n'
    sha256sum \
        "$source_pkg/qml/panels/JobStatusPanel.qml" \
        "$target_pkg/qml/panels/JobStatusPanel.qml"
fi

if [ "$restart_service" -eq 1 ]; then
    printf '\nRestarting %s...\n' "$service_name"
    sudo systemctl restart "$service_name"
    sleep 2
    systemctl --no-pager --full status "$service_name" | sed -n '1,12p'
else
    printf '\nSkipped service restart.\n'
fi
