# KlipperTouch Research-First Design

Date: 2026-04-23
Status: Approved for documentation phase
Repository phase: research-first, no application scaffold

## Goal

Create a maintainable implementation blueprint for a production-quality PySide6 + QML recreation of KlipperScreen. Phase 1 produces structured documentation and safe environment validation only. It does not create application runtime code, QML screens, printer-control features, packaging, or deployment scripts.

## Context

The new repository at `/home/tope/project/KlipperTouch` starts clean. The previous experimental project at `/home/tope/project_py/KlipperTouch` is a limited reference for requirements and lessons learned, not a source to migrate wholesale. The local KlipperScreen fork at `/home/tope/project_py/KlipperScreen` is the primary behavioral reference.

The first real printer target is reachable as `orangepi@192.168.123.117`. Phase 1 permits only read-only SSH and Moonraker checks. Direct printer motion and state-changing commands are explicitly out of scope.

## Phase 1 Deliverables

- A documentation index that explains how the project records specs, research, and roadmap decisions.
- A KlipperScreen architecture map covering startup, configuration, REST, WebSocket, printer state, navigation shell, and panels.
- A read-only printer probe report with environment facts and safety boundaries.
- A roadmap that sequences research, scaffold creation, read-only integration, core panels, control enablement, and production hardening.
- A clear transition point for the next phase: building a clean PySide6/QML skeleton from the documented contracts.

## Non-Goals

- No Python package scaffold.
- No PySide6 dependency installation.
- No QML implementation.
- No migration of old experimental code.
- No printer movement, homing, heating, extrusion, print control, restart, power control, or emergency-stop calls.
- No GitHub push from the local environment unless explicitly requested later.

## KlipperScreen Reference Model

KlipperScreen is structured around `screen.py`, which initializes configuration, display sizing, theme loading, the BasePanel shell, Moonraker REST, Moonraker WebSocket, file tracking, and dynamic panel loading.

Important reference modules:

- `screen.py`: application lifecycle, printer selection, connection startup, panel stack, websocket subscription, popup/error handling.
- `ks_includes/config.py`: config search, defaults, includes, validation, printer definitions, language setup, configurable options.
- `ks_includes/KlippyRest.py`: synchronous REST wrapper for Moonraker initialization and simple resource fetches.
- `ks_includes/KlippyWebsocket.py`: WebSocket thread, JSON-RPC request table, notification dispatch, Moonraker command wrapper.
- `ks_includes/printer.py`: printer state model, config-derived device inventory, status update processing, state transition callbacks.
- `panels/base_panel.py`: persistent shell with action bar, title bar, temperature summary, time, battery, emergency controls, and content slot.
- `panels/*.py`: feature panels loaded dynamically by name.
- `config/*.conf`: default menus and configurable navigation definitions.
- `styles/*`: CSS, icons, graph colors, and theme definitions.

## Planned KlipperTouch Architecture

The later PySide6/QML implementation should use these boundaries:

- `app`: Qt application bootstrap, CLI arguments, logging, environment checks, and QML engine setup.
- `config`: KlipperScreen-compatible INI loading, includes, validation, printer selection, and typed project settings.
- `moonraker`: REST client, WebSocket client, JSON-RPC dispatcher, reconnect policy, and command safety gates.
- `domain`: printer state, heaters, fans, files, print job, toolhead, config-derived capabilities, and update reducers.
- `ui_bridge`: Qt `QObject` models exposed to QML, signal mapping, command facade, and panel navigation state.
- `qml`: shell, top status bar, side or bottom action bar depending on orientation, panel views, shared components, and theme tokens.
- `safety`: read-only mode, command allowlist, command denylist, confirmation policies, and real-printer test profiles.
- `tests`: unit tests for config/domain/client logic, contract tests against captured Moonraker payloads, QML smoke tests, and safe integration probes.

## Data Flow

Startup should follow this sequence in the implementation phase:

1. Load project defaults and user configuration.
2. Select a printer from `[printer ...]` sections or show a printer selector.
3. Fetch read-only Moonraker startup data via REST.
4. Build a domain model from `printer/info`, `server/info`, `printer/objects/list`, and selected object queries.
5. Open WebSocket and subscribe to object updates.
6. Reduce updates into domain state.
7. Emit Qt model signals to QML.
8. Route panel requests through a navigation controller.
9. Gate all state-changing commands through the safety layer before they can reach Moonraker.

## Phase 1 Printer Validation Contract

Allowed read-only operations:

- SSH login and basic host identification.
- `GET /server/info`.
- `GET /printer/info`.
- `GET /printer/objects/list`.
- `GET /printer/objects/query` for selected objects.
- Reading service active states.
- Reading log filenames and small log excerpts.

Forbidden operations:

- `printer.gcode.script` with any script.
- Homing commands such as `G28`.
- Movement commands such as `G0`, `G1`, `FORCE_MOVE`, or macro wrappers that can move axes.
- Temperature commands such as `M104`, `M109`, `M140`, `M190`, or heater target setters.
- Extrusion and retract commands.
- `printer.print.start`, `printer.print.pause`, `printer.print.resume`, and `printer.print.cancel`.
- `printer.emergency_stop`, `printer.restart`, and `printer.firmware_restart`.
- Power device on/off calls.
- Klipper or Moonraker service restarts.

## Real Printer Observation

The first read-only probe on 2026-04-23 showed:

- Host: `orangepi3b`.
- Kernel: Linux `5.10.160-rockchip-rk356x` on `aarch64`.
- Moonraker: `v0.10.0-19-g1ed102e`.
- Moonraker API: `1.5.0`.
- Klippy connection: connected and ready.
- Klipper: `v0.13.0-593-g2f05309d-dirty`.
- Klipper config: `/home/orangepi/printer_data/config/printer.cfg`.
- Klipper log: `/home/orangepi/printer_data/logs/klippy.log`.
- Services: `moonraker` and `klipper` are active.
- Object list includes standard objects plus custom macros and devices, including `cartographer`, `z_tilt`, `extruder`, `heater_bed`, fans, LEDs, and Chinese-named fan entries.

Design implication: the implementation must handle Unicode object names, custom macros, multiple MCUs, custom sensors, and non-trivial object inventories without assuming a stock printer profile.

## Compatibility Requirements For Later Phases

- Preserve KlipperScreen-compatible configuration sections where practical: `[main]`, `[printer ...]`, `[preheat ...]`, `[menu ...]`, displayed macros, graph settings, and theme options.
- Keep panel behavior traceable to KlipperScreen panel names.
- Keep QML UI models independent from raw Moonraker payload shape.
- Support 800x480 minimum and orientation-dependent action bar placement.
- Treat read-only mode as a first-class runtime mode, not a temporary development hack.
- Support English as the initial UI language while keeping translation hooks available.

## Testing Strategy For Later Phases

- Unit tests for config validation and fallback behavior.
- Unit tests for domain reducers using captured Moonraker payload fixtures.
- Contract tests for REST endpoints in read-only mode.
- WebSocket parser tests using JSON-RPC response and notification samples.
- QML smoke tests that load the shell without a printer.
- Hardware integration checks that default to read-only and fail closed if a command is not explicitly allowed.

## Exit Criteria

Phase 1 is complete when the repository contains a stable documentation structure, architecture map, printer probe report, and roadmap sufficient to write a detailed implementation plan for the clean PySide6/QML skeleton.

