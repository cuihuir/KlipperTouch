# Runtime Safety Boundary

This document records the current production safety boundary for KlipperTouch.
Read-only mode remains the default, while selected command groups are now enabled
when the local config explicitly sets `read_only = false`.

## Current UI State

Live panels:

- `Temperature`: displays heater and sensor temperatures from Moonraker startup reads and WebSocket status updates.
- `Print`: displays the G-code file list from Moonraker file manager reads.
- `Job Status`: opens automatically while `print_stats.state` is active and exposes audited print-control and tuning actions.
- `Move`: displays toolhead position and homed axes, with audited jog, homing, and disable-motors actions.
- `Extrude`: displays nozzle temperature, target, and E position, with audited extrude/retract and load/unload macro actions.
- `More`: displays printer and Moonraker/Klipper version information.

Still-incomplete visual skeleton areas:

- `Move`: speed configuration entries are placeholders.
- `Extrude`: Temperature, Pressure Advance, Retraction, and Spoolman entries are placeholders.

Shell actions:

- `Back`, `Home`, and `Menu` only change local QML navigation state.
- `Stop` sends Moonraker emergency stop through the audited job-control bridge.

## Read-Only Mode Allowlist

HTTP GET endpoints currently allowed by the read-only policy:

- `server/info`
- `server/files/list`
- `server/files/metadata`
- `server/temperature_store`
- `machine/update/status`
- `printer/info`
- `printer/objects/list`
- `printer/objects/query`

JSON-RPC methods currently allowed by the read-only policy:

- `server.info`
- `printer.objects.query`
- `printer.objects.subscribe`

`printer.objects.query` may be sent through JSON-RPC for read-only object queries,
including Unicode Klipper object names that are not reliable through HTTP query
parameters. It must not be used for G-code or printer control methods.

The WebSocket stream only subscribes to temperature/target fields for discovered temperature
devices, read-only print status fields from `print_stats`, `display_status`, and
`virtual_sdcard`, and read-only position fields from `toolhead` and `gcode_move`.
Reconnects repeat the same read-only subscription.

## Enabled Commands When `read_only = false`

All state-changing commands must be routed through `JobControlModel` and
`MoonrakerClient`; QML must not contain direct G-code strings or Moonraker method names.

Currently enabled groups:

- Files and print state: start print, delete G-code file, pause, resume, cancel, clear current SD file.
- Recovery: emergency stop, firmware restart, Klipper restart.
- Job tuning: Z offset, speed factor, flow factor, object exclusion.
- Move: `M84`, `G28`, and bounded jogs through `_CLIENT_LINEAR_MOVE X/Y/Z=... F=...`.
- Extrude: relative extrusion/retraction through `_CLIENT_LINEAR_MOVE E=... F=...`.
- Filament macros: `LOAD_FILAMENT SPEED=...` and `UNLOAD_FILAMENT SPEED=...`.
- Temperature targets: `SET_HEATER_TEMPERATURE` and `SET_TEMPERATURE_FAN_TARGET` with UI-clamped `0..350` values.

## Explicitly Forbidden Until Reviewed

Do not add or call any of these without a separate reviewed implementation plan:

- PID tuning and temperature commands outside the audited target setter.
- Service restart, host reboot, or power control.
- Direct `printer.gcode.script` calls from QML or UI components.
- Any new macro execution path that bypasses `JobControlModel`.

## Verification Commands

Use official PyPI URLs when running `uv`; the local environment may otherwise rewrite `uv.lock`
to a mirror URL.

```bash
UV_INDEX_URL=https://pypi.org/simple uv run --locked --extra dev pytest -q
UV_INDEX_URL=https://pypi.org/simple uv run --locked --extra dev ruff check src tests
UV_INDEX_URL=https://pypi.org/simple uv run --locked --extra dev mypy src/klippertouch
QT_QPA_PLATFORM=offscreen UV_INDEX_URL=https://pypi.org/simple timeout 3 uv run --locked python -m klippertouch --debug
```

After running dependency commands, check that `uv.lock` was not rewritten to a mirror:

```bash
rg -n "tuna|tsinghua" uv.lock
```

## Real Printer Validation

The current command-validation development target is `192.168.123.203:7125`.
It is a development board and may be used for the enabled command groups above.

The previous read-only validation target was `192.168.123.227:7125`.

Allowed read-only validation:

- Read startup server/printer/object information.
- Read G-code file metadata.
- Read Unicode temperature objects through read-only JSON-RPC query.
- Open the WebSocket and subscribe to read-only status updates.

Forbidden on real motion hardware unless explicitly approved:

- Any command that can move hardware unexpectedly, heat hardware, alter files, or change print state.
