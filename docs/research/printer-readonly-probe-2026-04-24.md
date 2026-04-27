# Printer Read-Only Probe: 2026-04-24

Target: `192.168.123.227:7125`
Mode: read-only

## Commands Run

All validation used KlipperTouch read-only probes and Moonraker read-only object queries.
No G-code, print-control, movement, heating, extrusion, restart, upload, delete, or
file-mutation command was sent.

Read-only checks performed:

- `python -m klippertouch --probe`
- `printer.objects.query` JSON-RPC for Unicode temperature object fallback
- 5-second WebSocket status subscription smoke test
- offscreen GUI startup with `QT_QPA_PLATFORM=offscreen`

## Environment

- Hostname: `toper1`
- Klippy state: `ready`
- Moonraker version: `v0.10.0-10-gfb257f8`
- Active print state observed: `printing`
- Initial G-code files observed by GUI startup: `155`
- 5-second WebSocket smoke observed: `21` status updates, `21` temperature history
  updates, `21` print updates, and `0` toolhead UI notifications while the active
  panel was `main`.

## Temperature Object Notes

The printer exposes Unicode temperature objects such as:

- `temperature_fan SOC散热`
- `temperature_host SOC散热`

HTTP `printer/objects/query` parameters did not reliably return these names. The
read-only JSON-RPC method `printer.objects.query` returned the expected values:

- `temperature_fan SOC散热`: temperature `42.5`, target `40.0`
- `temperature_host SOC散热`: temperature `42.5`, target `null`

## Implementation Implications

- Unicode Klipper object names must use JSON-RPC read-only fallback during startup probe.
- `temperature_host` objects should be treated as temperature devices.
- The safety boundary still blocks all state-changing JSON-RPC methods before network I/O.
- Active-panel gating suppresses hidden toolhead UI notifications while still preserving
  the latest read-only status internally.
