# KlipperTouch Roadmap

This project aims to recreate KlipperScreen behavior and layout in a PySide6/QML application while keeping the command surface safe and maintainable. Development should proceed in small commits with tests, screenshot checks, and real-printer validation where appropriate.

## Current Position

Status: Phase 1 and Phase 2 are complete enough for continued implementation. Phase 3 and Phase 4 are active.

Implemented:

- PySide6/QML application shell, responsive metrics, navigation stack, and top-level panels.
- Read-only Moonraker startup probe, websocket subscription, file refresh, and safety allowlist.
- Unicode Klipper object probing through read-only JSON-RPC fallback.
- Read-only temperature, files, job status, move, extrude, and information panels.
- Screenshot capture tooling for common target resolutions.
- Real-printer read-only validation against the Orange Pi Moonraker endpoint.

## Phase 1: Research and Safety Blueprint

Status: complete

Goal: document what must be recreated from KlipperScreen and define the safety boundary before runtime features expand.

Deliverables:

- KlipperScreen architecture notes and behavior contracts.
- Real-printer read-only facts.
- Explicit safety rules for read-only versus state-changing Moonraker calls.
- Initial implementation plan for a clean PySide6/QML skeleton.

Exit criteria:

- Architecture map is sufficient to implement screens without guessing core behavior.
- Real-printer validation records prove basic Moonraker connectivity.
- Safety boundary is written and referenced by implementation work.

## Phase 2: Clean PySide6/QML Skeleton

Status: implemented skeleton

Goal: create a maintainable project foundation before adding broad printer features.

Deliverables:

- Python package structure under `src/klippertouch`.
- QML shell with action bar, status header, content loader, and responsive metrics.
- Config loading, CLI entrypoint, test framework, linting, typing, and packaging metadata.
- Local navigation that does not send printer commands.

Exit criteria:

- App starts locally and offscreen.
- QML loads at common screen shapes.
- Tests, ruff, and mypy pass.

## Phase 3: Read-Only Moonraker Integration

Status: active

Goal: build the complete read-only data model before enabling any state-changing printer operation.

Deliverables:

- REST startup probe for server info, printer info, objects, object status, and G-Code files.
- JSON-RPC read-only fallback for Unicode object names that HTTP query parameters cannot address reliably.
- Websocket subscription for temperatures, print state, toolhead state, and job state.
- Domain reducers that normalize Moonraker data into stable QML-facing models.
- File browser model with directory entries, sort state, metadata, and read-only navigation.
- Long-running read-only validation for reconnects and state transitions.

Exit criteria:

- All visible data updates through websocket or controlled refresh paths.
- No movement, heating, extrusion, print start, pause, resume, cancel, delete, rename, or upload command can be sent.
- Real-printer read-only probe and selected websocket checks pass.

## Phase 4: KlipperScreen Panel Recreation

Status: active

Goal: recreate the core KlipperScreen page structure and layout behavior while controls are enabled gradually through audited bridges.

Deliverables:

- Main menu layout matching KlipperScreen top-level concepts.
- Files/Gcodes page as a file manager only.
- Job Status page that appears automatically only during active print states.
- Temperature, Move, Extrude, More/System pages with live data and audited controls where implemented.
- Screenshot regression set for `800x480`, `1024x600`, `480x800`, and later `1280x800`.

Exit criteria:

- Files and Job Status are not mixed.
- Each page has no overlap at target screen sizes.
- Navigation and automatic Job Status routing match the documented KlipperScreen behavior.

## Phase 5: Detailed Page Completion

Status: planned

Goal: fill each page to production-quality visual and data completeness before risky controls are enabled.

Work packages:

- Files: directory hierarchy, breadcrumbs, sorting, metadata, search/filter, thumbnails if available, empty/loading/error states.
- Job Status: progress, filename, thumbnail, elapsed/remaining estimates, layers, filament, speed, flow, Z offset, current temperatures, pause state.
- Temperature: dynamic heater/sensor grid, historical graph, target display, presets as disabled placeholders.
- Move: homed axes, position cards, step size UI, jog, home, disable motors, speed settings placeholders.
- Extrude: extruder temp, target temp, E position, extrude/retract, load/unload macros, filament sensor states where available.
- More/System: host info, Moonraker/Klipper versions, object list, network/runtime stats, logs entry, settings placeholders.

Exit criteria:

- Each page can be reviewed against KlipperScreen screenshots or behavior notes.
- Missing KlipperScreen features are tracked explicitly as planned, deferred for safety, or out of scope.

## Phase 6: Command Safety Framework

Status: in progress

Goal: create one audited path for all state-changing Moonraker commands.

Deliverables:

- Command policy with risk classes: file operation, print control, temperature, fan, movement, extrusion, emergency.
- Confirmation UI patterns with clear wording and cancel paths.
- Dry-run or test mode for development without sending commands.
- Hardware profile allowlist for the real test printer.
- Audit logging for every command request, result, and failure.

Exit criteria:

- No QML page can call Moonraker directly for a state-changing operation.
- Every state-changing command is covered by unit tests and safety tests.
- Real-printer execution requires explicit feature enablement.

## Phase 7: Controlled Command Enablement

Status: planned

Goal: enable real printer controls gradually, from lower risk to higher risk.

Recommended order:

- Completed: file selection, print start, delete, pause, resume, cancel, clear file, emergency stop, firmware restart, Klipper restart.
- Completed: movement, homing, disable motors, extrusion/retraction, filament load/unload macros.
- In progress: user-visible command feedback on Move and Extrude pages.
- Planned: fan controls with bounded values.
- Planned: temperature controls with target limits and confirmation.
- Planned: stronger printer-state guards for movement and extrusion on real motion hardware.

Exit criteria:

- Each command group has a dedicated implementation commit, tests, documentation, and real-printer validation note.
- Higher-risk controls are not enabled until lower-risk controls are stable.

## Phase 8: Production Hardening

Status: planned

Goal: make the application deployable and maintainable on printer-attached hardware.

Deliverables:

- Installation and update docs.
- systemd service or desktop autostart guidance.
- Runtime logs, crash recovery behavior, and user-visible error states.
- Performance and memory checks on target hardware.
- Theme consistency, localization readiness, and screen calibration notes.
- Packaging validation for source, wheel, and local deployment.

Exit criteria:

- A fresh machine can install and launch the GUI from documented steps.
- Long-duration read-only and enabled-command tests are recorded.
- Common failure modes have visible UI states and logs.

## Near-Term Execution Batches

Batch 1: Files/Gcodes read-only browser

- Complete directory hierarchy, sorting, metadata roles, breadcrumbs, and empty/loading states.
- Keep delete, rename, upload, and start-print disabled or absent.

Batch 2: Job Status visual parity

- Improve active-print layout, progress treatment, current job metadata, and temperature summary.
- Keep pause, resume, cancel, speed override, and extrusion controls disabled or absent.

Batch 3: Temperature page data completeness

- Replace fake graph with real read-only temperature history buffer.
- Improve dynamic layout for many heaters and sensors.

Batch 4: Screenshot regression workflow

- Generate screenshots for every panel and target size.
- Add a human-review index and optional automated sanity checks for blank captures.

Batch 5: Long-running read-only validation

- Run websocket refresh against the real printer for reconnect and update behavior.
- Record failures and Moonraker object gaps without sending state-changing commands.

## Safety Rules

- Default mode is read-only.
- Real movement, heating, extrusion, print control, file mutation, and emergency actions are not implemented until the command safety framework exists.
- Any feature that sends a Moonraker method outside the read-only allowlist needs separate review, tests, and real-printer approval.
- QML pages should not contain raw Moonraker command strings for state-changing actions.
