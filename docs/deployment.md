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
- EGLFS start script: `/usr/local/bin/klippertouch-eglfs-start.sh`
- EGLFS system service: `/etc/systemd/system/klippertouch-eglfs.service`
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

Install or update the systemd assets from the repository checkout:

```bash
sudo deploy/install-systemd.sh eglfs
```

This installs both EGLFS and X11 service files, enables the EGLFS service by
default, disables the X11 service, installs the KMS config, and leaves an
existing `KlipperTouch.conf` untouched unless `KLIPPERTOUCH_OVERWRITE_CONFIG=1`
is set. To switch back to the X11 rollback service:

```bash
sudo deploy/install-systemd.sh x11
```

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

`klippertouch-eglfs.service` is the validated production service for the RK3566
target. It conflicts with `klippertouch.service` because EGLFS needs direct
DRM/KMS access and must not run while Xorg owns the display.

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
Verbose Qt scenegraph and KMS logging is disabled by default; set `QSG_INFO=1`
or `QT_LOGGING_RULES` in the service environment only when diagnosing rendering
issues.

## Validation

Before enabling the service, run a probe:

```bash
/home/tope/klippertouch/venv/bin/klippertouch \
  --config /home/tope/printer_data/config/KlipperTouch.conf \
  --probe
```

For visible UI changes, capture or manually check the target display resolution
before leaving the service enabled.

## Control Validation Checklist

Controls are enabled in this deployment, so validate each command group on an
idle printer before treating the installation as accepted:

- Set a low temperature target and confirm Moonraker receives the intended
  temperature target for the selected device.
- Exercise motion controls only when axes are homed and verify the requested
  motion direction and distance are correct.
- Exercise extrusion and retraction only when the extrusion guard permits it,
  and verify blocked extrusion reports an error instead of sending G-code.
- Test print control actions such as pause, resume, cancel, and file selection
  on a known safe file.
- Confirm emergency stop is reachable and sends the expected Moonraker command.
- Validate tuning controls including Z offset, speed factor, and extrusion
  factor on an idle or disposable validation job.
- Disconnect or block Moonraker once and confirm the UI reports command failure
  without silently retrying state-changing requests.

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

`klippertouch-eglfs.service` is installable as the boot default. Keep the X11
service installed as a rollback path, and use `deploy/install-systemd.sh x11` if
the direct DRM/KMS path needs to be disabled.

After changing the boot default, perform one operator-approved reboot validation
and confirm `klippertouch-eglfs.service` returns to `active` without manually
starting the service.
