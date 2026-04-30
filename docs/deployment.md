# KlipperTouch Deployment

This deployment keeps the existing `device-gui.service` untouched and installs an independent `klippertouch.service`.

## Target Layout

- Application root: `/home/tope/klippertouch`
- Virtual environment: `/home/tope/klippertouch/venv`
- Config: `/home/tope/printer_data/config/KlipperTouch.conf`
- Start script: `/usr/local/bin/klippertouch-start.sh`
- System service: `/etc/systemd/system/klippertouch.service`
- EGLFS experiment script: `/usr/local/bin/klippertouch-eglfs-start.sh`
- EGLFS experiment service: `/etc/systemd/system/klippertouch-eglfs.service`
- EGLFS KMS config: `/home/tope/printer_data/config/klippertouch-eglfs-kms.json`

## System Packages

Install the packages listed in `deploy/system-packages.txt`. The current target needed `python3.11-venv` for venv creation and `libxcb-cursor0` for the PySide6 xcb platform plugin.

## Runtime

The production service follows the KlipperScreen-style systemd pattern: systemd starts a small shell launcher, the launcher starts Xorg with `xinit`, and the X client stage rotates the HDMI output before launching the GUI.

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

The deployment now starts with controls enabled. Keep `read_only = false` in `/home/tope/printer_data/config/KlipperTouch.conf`, or keep the explicit `--allow-controls` service argument in place so the runtime policy does not fall back to read-only mode.

The production X11 service intentionally uses the Qt Quick software renderer:

```ini
Environment=QT_QUICK_BACKEND=software
Environment=KLIPPERTOUCH_RENDER_BACKEND=software
```

The `xcb_egl` path can create a Mali-G52 context on the RK3566 target, but it has shown grey-screen behavior where the rendered frames are not presented to the HDMI plane.

## Validated EGLFS Path

`klippertouch-eglfs.service` is installed as a manual experiment and is not enabled by default. It conflicts with `klippertouch.service` because EGLFS needs direct DRM/KMS access and must not run while Xorg owns the display.

The experiment uses:

```ini
Environment=QT_QPA_PLATFORM=eglfs
Environment=QT_QPA_EGLFS_INTEGRATION=eglfs_kms
Environment=QT_QPA_EGLFS_KMS_CONFIG=/home/tope/printer_data/config/klippertouch-eglfs-kms.json
Environment=KLIPPERTOUCH_DISPLAY_ROTATION=right
```

The display rotation is handled in QML for Qt Quick content because `QT_QPA_EGLFS_ROTATION` does not rotate OpenGL-based Qt Quick scenes reliably.

This path has been validated on the RK3566 target with the Mali-G52 renderer. The EGLFS log reports the HDMI panel as `440x1920` and creates an OpenGL ES context with `RENDERER: Mali-G52`; the QML scene then rotates the logical GUI right into the physical `1920x440` orientation.

## Issues and Resolutions

- X11 software rendering works and remains the conservative fallback, but CPU usage is high for the target hardware.
- X11 with `QT_XCB_GL_INTEGRATION=xcb_egl` can create a Mali-G52 context, but the target showed a grey screen because rendered frames were not reliably presented to the HDMI plane. This path is not used for the default X11 service.
- EGLFS/GBM avoids Xorg and uses direct DRM/KMS presentation. The service disables the hardware cursor and uses the KMS config in `deploy/klippertouch-eglfs-kms.json`.
- The HDMI panel reports portrait geometry (`440x1920`) even though the desired UI is landscape (`1920x440`). The application accepts `KLIPPERTOUCH_DISPLAY_ROTATION=right`, swaps the logical viewport, and rotates the QML `sceneRoot`.
- Qt Quick Controls `Popup` is not safe inside the rotated scene because it can be rendered through the window overlay instead of inheriting the rotated scene transform. Numeric editors now use ordinary `Item`/`Rectangle` overlays attached to a full-screen `scenePopupLayer` inside `sceneRoot`, so temperature and extrusion keypads stay aligned with the rotated GUI and remain on-screen.

To make EGLFS the boot default after final acceptance, add an `[Install]` section to `klippertouch-eglfs.service`, disable `klippertouch.service`, enable `klippertouch-eglfs.service`, and keep the X11 service installed as a rollback path.
