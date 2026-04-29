# KlipperTouch

KlipperTouch is planned as a production-oriented PySide6 + QML touchscreen UI for Klipper printers. The long-term target is a functional 1:1 recreation of KlipperScreen behavior while keeping the new codebase clean, documented, testable, and maintainable.

## Current Status

This repository now contains the clean PySide6/QML application scaffold plus active KlipperScreen-style Files, Job Status, Temperature, Move, Extrude, More, and recovery surfaces. Read-only mode remains the default safety posture, while selected command groups are enabled when `config/KlipperTouch.conf` explicitly sets `read_only = false`.

The implementation is grounded in KlipperScreen source analysis, the previous experimental KlipperTouch project at `/home/tope/project_py/KlipperTouch`, and validation against Moonraker development targets including `192.168.123.203`.

## Documentation

- [Documentation index](docs/README.md)
- [Research-first design spec](docs/superpowers/specs/2026-04-23-klippertouch-research-first-design.md)
- [KlipperScreen architecture map](docs/research/klipperscreen-architecture.md)
- [Printer read-only probe](docs/research/printer-readonly-probe-2026-04-23.md)
- [Current printer read-only probe](docs/research/printer-readonly-probe-2026-04-24.md)
- [Runtime safety boundary](docs/safety-boundary.md)
- [Roadmap](docs/roadmap.md)

## Development Commands

```bash
UV_INDEX_URL=https://pypi.org/simple uv sync --locked --extra dev
UV_INDEX_URL=https://pypi.org/simple uv run --locked --extra dev pytest
UV_INDEX_URL=https://pypi.org/simple uv run --locked --extra dev ruff check src tests
UV_INDEX_URL=https://pypi.org/simple uv run --locked --extra dev mypy src/klippertouch
UV_INDEX_URL=https://pypi.org/simple uv run --locked --extra dev python -m klippertouch --probe
```

Use read-only probes for unknown printers. Enabled command groups must continue to route through the audited Moonraker client and Qt control model.

## Safety Boundary

Read-only mode is still the default. On the `192.168.123.203` development board, audited print, move, recovery, extrusion, and temperature-target commands are allowed for validation. New heating paths outside the audited target setter, host power/service control, and new macro execution paths remain forbidden until reviewed.

## License

GPL-3.0-or-later. See [LICENSE](LICENSE).
