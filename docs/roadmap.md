# KlipperTouch Roadmap

This project aims to recreate KlipperScreen behavior and layout in a PySide6/QML application while keeping the command surface safe and maintainable. Development should proceed in small commits with tests, screenshot checks, and real-printer validation where appropriate.

## Current Position

Status: Phase 1 and Phase 2 are complete enough for continued implementation. Phase 3 and Phase 4 are active.

Implemented:

- PySide6/QML application shell, responsive metrics, navigation stack, and top-level panels.
- Read-only Moonraker startup probe, websocket subscription, file refresh, and safety allowlist.
- Unicode Klipper object probing through read-only JSON-RPC fallback.
- Temperature, files, job status, move, extrude, and information panels with audited control
  bridges where currently enabled.
- Screenshot capture tooling for common target resolutions.
- Real-printer read-only validation against the Orange Pi Moonraker endpoint, including
  warnings, five-axis capability flags, G-code file list, metadata, and thumbnail URLs.

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
- Job Status page that appears automatically for active and terminal print states.
- Temperature, Move, Extrude, More/System pages with live data and audited controls where implemented.
- Screenshot regression set for `800x480`, `1024x600`, `480x800`, and later `1280x800`.

Exit criteria:

- Files and Job Status are not mixed.
- Each page has no overlap at target screen sizes.
- Navigation and automatic Job Status routing match the documented KlipperScreen behavior.

## Phase 5: Detailed Page Completion

Status: active

Goal: fill each page to production-quality visual and data completeness before risky controls are enabled.

Work packages:

- Files: implemented directory hierarchy, sorting, metadata, search/filter, lazy thumbnails, large detail thumbnail, and print/delete confirmation. Remaining work is better loading/error affordance and deeper real-printer regression.
- Job Status: implemented progress, filename, thumbnail, elapsed/remaining estimates, layers, filament, speed, flow, Z offset, terminal-state clear, object exclusion entry, and responsive summary/details. Remaining work is visual parity polish and richer current-temperature/context blocks.
- Temperature: implemented dynamic heater/sensor grid, graph selection persistence, historical graph, target display, and bounded target controls. Remaining work is graph performance measurement on target hardware.
- Move: implemented positions, step size UI, jog, home all, UVW/bed tilt subpage, disable motors, z tilt, accelerator leveling, and command confirmations where needed. Remaining work is final visual parity and real-motion hardware guards.
- Extrude: implemented nozzle temp, pressure advance/smooth time controls, extrude/retract, load/unload, and optional material-system entry. Remaining work is filament sensor state display when available.
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
- Completed: temperature target controls with `0..350` bounds and pending/failed UI state.
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

- Completed core directory hierarchy, sorting, metadata roles, search, thumbnails, print, and delete.
- Next: loading/error states and longer real-printer regression with nested directories.

Batch 2: Job Status visual parity

- Completed active/paused/terminal state routing, summary/details split, thumbnail, action confirmations, clear status, advanced Z/speed/flow controls, and small-screen scrolling.
- Next: compare against KlipperScreen for final information grouping and current-temperature treatment.

Batch 3: Temperature page data completeness

- Completed real temperature history, local graph visibility persistence, settable/read-only target behavior, and 80 ms coalesced pager refresh.
- Next: profile graph and pager CPU on Orange Pi class hardware.

Batch 4: Screenshot regression workflow

- Generate screenshots for every panel and target size.
- Add a human-review index and optional automated sanity checks for blank captures.

Batch 5: Long-running read-only validation

- Run websocket refresh against the real printer for reconnect and update behavior.
- Record failures and Moonraker object gaps without sending state-changing commands.

## Safety Rules

- Default mode is read-only.
- State-changing command groups must go through the audited control bridge and command policy.
- Any new Moonraker method outside the existing allowlist needs separate review, tests, and real-printer approval.
- QML pages should not contain raw Moonraker command strings for state-changing actions.
