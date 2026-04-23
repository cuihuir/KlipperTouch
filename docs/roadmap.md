# KlipperTouch Roadmap

## Phase 1: Research-First Blueprint

Status: active

Scope:

- Document KlipperScreen architecture and behavior contracts.
- Record real-printer read-only facts.
- Define project boundaries, safety rules, and implementation phases.
- Keep the repository free of application runtime code until the blueprint is reviewed.

Exit criteria:

- Design spec is complete.
- Architecture map is complete enough to plan the PySide6/QML skeleton.
- Real-printer read-only probe is recorded.
- Next-phase implementation plan can be written without relying on unstated assumptions.

## Phase 2: Clean PySide6/QML Skeleton

Scope:

- Create Python package structure.
- Add PySide6/QML bootstrap.
- Add logging, config search, and test framework.
- Load a shell window with non-functional sample status and navigation.
- Keep Moonraker integration disabled or mocked by default.

Safety:

- No state-changing printer commands.
- Read-only mode remains default.

## Phase 3: Read-Only Moonraker Integration

Scope:

- Implement REST startup checks.
- Implement WebSocket connection and object subscription.
- Build domain reducers for printer status, heaters, toolhead, files, and print state.
- Display real status in QML without controls that can change printer state.

Safety:

- The Moonraker layer rejects all commands outside the read-only allowlist.

## Phase 4: Core Panel Recreation

Scope:

- Recreate KlipperScreen shell behavior.
- Implement main/status, files, job status, temperature readout, move readout, and extrude readout as QML panels.
- Add visual regression screenshots for target resolutions.

Safety:

- Control buttons remain disabled or routed to mock handlers until explicit enablement.

## Phase 5: Controlled Command Enablement

Scope:

- Introduce command permissions, confirmation policies, and hardware test profiles.
- Enable low-risk commands first in a staged manner.
- Add audit logging for every command sent to Moonraker.

Safety:

- Movement, heating, extrusion, print control, and emergency stop each require separate review before being enabled.

## Phase 6: Production Hardening

Scope:

- Packaging, systemd service, deployment docs, performance testing, memory checks, crash recovery, localization, and theme completeness.
- Compatibility checks against KlipperScreen configuration patterns.
- Long-duration testing on embedded hardware.
