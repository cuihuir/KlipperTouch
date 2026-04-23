# KlipperTouch

KlipperTouch is planned as a production-oriented PySide6 + QML touchscreen UI for Klipper printers. The long-term target is a functional 1:1 recreation of KlipperScreen behavior while keeping the new codebase clean, documented, testable, and maintainable.

## Current Status

This repository is in the research-first phase. The project is intentionally not scaffolded as a Python application yet. The first deliverable is a maintained implementation blueprint based on:

- KlipperScreen source analysis.
- The previous experimental KlipperTouch project at `/home/tope/project_py/KlipperTouch`.
- Read-only validation against the real printer at `192.168.123.117`.

## Documentation

- [Documentation index](docs/README.md)
- [Research-first design spec](docs/superpowers/specs/2026-04-23-klippertouch-research-first-design.md)
- [KlipperScreen architecture map](docs/research/klipperscreen-architecture.md)
- [Printer read-only probe](docs/research/printer-readonly-probe-2026-04-23.md)
- [Roadmap](docs/roadmap.md)

## Safety Boundary

Until an implementation plan explicitly changes this boundary, real-printer validation is read-only only. Do not send movement, homing, heating, extrusion, print-control, restart, firmware-restart, power, or emergency-stop commands from this project.

## License

GPL-3.0-or-later. See [LICENSE](LICENSE).

