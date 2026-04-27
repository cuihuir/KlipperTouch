# Runtime Safety Boundary

This document records the current production safety boundary for KlipperTouch.
It is intentionally conservative while the UI is being recreated.

## Current UI State

Read-only live panels:

- `Temperature`: displays heater and sensor temperatures from Moonraker startup reads and WebSocket status updates.
- `Print`: displays the G-code file list from Moonraker file manager reads.
- `Job Status`: opens automatically while `print_stats.state` is `printing` or `paused` and displays read-only job progress.
- `Move`: displays read-only toolhead position and homed axes while keeping all movement controls locked.
- `Extrude`: displays read-only nozzle temperature, target, and E position while keeping extrusion controls locked.
- `More`: displays printer and Moonraker/Klipper version information.

Locked visual skeleton panels:

- `Move`: shows axis and distance layout, but no controls are clickable and no motion commands are bound.
- `Extrude`: shows extrusion distance/speed layout, but no controls are clickable and no extrusion commands are bound.

Shell actions:

- `Back`, `Home`, and `Menu` only change local QML navigation state.
- `Stop` is present in the shell layout but intentionally does not send any printer command.

## Allowed Moonraker Operations

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

## Explicitly Forbidden Until Reviewed

Do not add or call any of these without a separate reviewed implementation plan:

- Movement, homing, or toolhead jogging.
- Heating, cooling, PID tuning, or temperature target changes.
- Extrusion or retraction.
- Print start, pause, resume, cancel, upload, delete, or file mutation.
- Firmware restart, Klipper restart, service restart, host reboot, or power control.
- Emergency stop wiring from the UI.
- Any direct `printer.gcode.script` command.

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

The current real-printer validation target is `192.168.123.227:7125`.

Allowed validation:

- Read startup server/printer/object information.
- Read G-code file metadata.
- Read Unicode temperature objects through read-only JSON-RPC query.
- Open the WebSocket and subscribe to read-only status updates.

Forbidden validation:

- Any command that can move hardware, change heat, alter files, or change print state.
