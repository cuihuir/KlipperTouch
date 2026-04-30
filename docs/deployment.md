# Deployment Guide

This guide is for printer-attached hardware such as Orange Pi boards. The goal is
to run KlipperTouch as a stable GUI process without keeping the development
launcher in the process tree.

## Install Or Update

Clone or rsync the repository to the target host:

```bash
cd /home/orangepi/KlipperTouch
UV_INDEX_URL=https://pypi.org/simple uv sync --locked
```

Use `--extra dev` only on development machines that need tests, ruff, mypy, or
screenshot tooling.

## Production Launch

Start the installed console script directly from the virtual environment:

```bash
cd /home/orangepi/KlipperTouch
.venv/bin/klippertouch --config /home/orangepi/printer_data/config/KlipperTouch.conf
```

This avoids an extra resolver/wrapper process and keeps runtime memory closer to
the real PySide/QML process cost. The config file should remain outside git and
point at the local Moonraker endpoint when possible.

## User Systemd Service

Use `deploy/systemd/klippertouch.service.example` as a starting point for a user
service. Copy it to:

```bash
mkdir -p ~/.config/systemd/user
cp deploy/systemd/klippertouch.service.example ~/.config/systemd/user/klippertouch.service
systemctl --user daemon-reload
systemctl --user enable --now klippertouch.service
```

Adjust `QT_QPA_PLATFORM`, `WAYLAND_DISPLAY`, or `DISPLAY` for the compositor used
by the touchscreen image. Prefer `Restart=on-failure` so transient Moonraker or
Qt startup failures recover without hiding repeated crashes.

## Validation

Before enabling the service, run a read-only probe:

```bash
.venv/bin/klippertouch --config /home/orangepi/printer_data/config/KlipperTouch.conf --probe
```

For visible UI changes, capture or manually check the target display resolution
before leaving the service enabled.
