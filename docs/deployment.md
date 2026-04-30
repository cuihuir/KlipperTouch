# KlipperTouch Deployment

This guide is for printer-attached hardware such as Orange Pi and RK3566 boards.
The goal is to run KlipperTouch as a stable GUI process without keeping the
development launcher in the process tree. The deployed service is independent
from any existing `device-gui.service`.

## Target Layout

- Application root: `/home/tope/klippertouch`
- Virtual environment: `/home/tope/klippertouch/venv`
- Config: `/home/tope/printer_data/config/KlipperTouch.conf`
- Start script: `/usr/local/bin/klippertouch-start.sh`
- System service: `/etc/systemd/system/klippertouch.service`
- EGLFS experiment script: `/usr/local/bin/klippertouch-eglfs-start.sh`
- EGLFS experiment service: `/etc/systemd/system/klippertouch-eglfs.service`
- EGLFS KMS config: `/home/tope/printer_data/config/klippertouch-eglfs-kms.json`

For other hosts, keep the same structure but adjust usernames and paths.

## Install Or Update

Clone or rsync the repository to the target host, then install dependencies:

```bash
cd /home/tope/klippertouch
UV_INDEX_URL=https://pypi.org/simple uv sync --locked
```

Use `--extra dev` only on development machines that need tests, ruff, mypy, or
screenshot tooling. Install system packages listed in `deploy/system-packages.txt`;
the current target needed `python3.11-venv` and `libxcb-cursor0`.

## Production Launch

Start the installed console script directly from the virtual environment:

```bash
cd /home/orangepi/KlipperTouch
.venv/bin/klippertouch --config /home/orangepi/printer_data/config/KlipperTouch.conf
```

This avoids an extra resolver/wrapper process and keeps runtime memory closer to
the real PySide/QML process cost. The config file should remain outside git and
point at the local Moonraker endpoint when possible.

## Runtime

The production service follows the KlipperScreen-style systemd pattern: systemd
starts a small shell launcher, the launcher starts Xorg with `xinit`, and the X
client stage rotates the HDMI output before launching the GUI.

The target panel reports as `440x1920`, so the service applies:

```bash
xrandr --output HDMI-1 --preferred --rotate right
```

The GUI starts with:

```bash
/home/tope/klippertouch/venv/bin/klippertouch \
  --config /home/tope/printer_data/config/KlipperTouch.conf \
  --debug \
  --allow-controls \
  --fullscreen
```

Controls are enabled in this deployment. Keep `read_only = false` in
`KlipperTouch.conf`, or keep the explicit `--allow-controls` service argument so
the runtime policy does not fall back to read-only mode.

## Rendering Backends

The production X11 service intentionally uses the Qt Quick software renderer:

```ini
Environment=QT_QUICK_BACKEND=software
Environment=KLIPPERTOUCH_RENDER_BACKEND=software
```

The `xcb_egl` path can create a Mali-G52 context on the RK3566 target, but it has
shown grey-screen behavior where rendered frames are not presented reliably to
the HDMI plane.

`klippertouch-eglfs.service` is installed as a manual experiment and is not
enabled by default. It conflicts with `klippertouch.service` because EGLFS needs
direct DRM/KMS access and must not run while Xorg owns the display.

The experiment uses:

```ini
Environment=QT_QPA_PLATFORM=eglfs
Environment=QT_QPA_EGLFS_INTEGRATION=eglfs_kms
Environment=QT_QPA_EGLFS_KMS_CONFIG=/home/tope/printer_data/config/klippertouch-eglfs-kms.json
Environment=KLIPPERTOUCH_DISPLAY_ROTATION=right
```

The display rotation is handled in QML for Qt Quick content because
`QT_QPA_EGLFS_ROTATION` does not rotate OpenGL-based Qt Quick scenes reliably.
This path has been validated on the RK3566 target with the Mali-G52 renderer.

## Validation

Before enabling the service, run a probe:

```bash
/home/tope/klippertouch/venv/bin/klippertouch \
  --config /home/tope/printer_data/config/KlipperTouch.conf \
  --probe
```

For visible UI changes, capture or manually check the target display resolution
before leaving the service enabled.

## Known Issues

- X11 software rendering works and remains the conservative fallback, but CPU
  usage is high for the target hardware.
- X11 with `QT_XCB_GL_INTEGRATION=xcb_egl` can create a Mali-G52 context, but the
  target showed a grey screen. This path is not used for the default X11 service.
- EGLFS/GBM avoids Xorg and uses direct DRM/KMS presentation. The service
  disables the hardware cursor and uses the KMS config in
  `deploy/klippertouch-eglfs-kms.json`.
- The HDMI panel reports portrait geometry (`440x1920`) even though the desired
  UI is landscape (`1920x440`). The application accepts
  `KLIPPERTOUCH_DISPLAY_ROTATION=right`, swaps the logical viewport, and rotates
  the QML `sceneRoot`.
- Qt Quick Controls `Popup` is not safe inside the rotated scene because it can
  render through the window overlay instead of inheriting the rotated scene
  transform. Numeric editors use ordinary `Item`/`Rectangle` overlays attached to
  a full-screen `scenePopupLayer` inside `sceneRoot`.

To make EGLFS the boot default after final acceptance, add an `[Install]` section
to `klippertouch-eglfs.service`, disable `klippertouch.service`, enable
`klippertouch-eglfs.service`, and keep the X11 service installed as a rollback
path.
