# KlipperTouch

KlipperTouch is planned as a production-oriented PySide6 + QML touchscreen UI for Klipper printers. The long-term target is a functional 1:1 recreation of KlipperScreen behavior while keeping the new codebase clean, documented, testable, and maintainable.

## Current Status

This repository now contains the clean PySide6/QML skeleton. It includes Python package scaffolding, application bootstrap, configuration loading, test tooling, and read-only Moonraker probe support. Printer control features remain disabled until separate reviewed implementation plans enable them.

The skeleton is grounded in the maintained implementation blueprint based on KlipperScreen source analysis, the previous experimental KlipperTouch project at `/home/tope/project_py/KlipperTouch`, and read-only validation against the real printer at `192.168.123.117`.

## Documentation

- [Documentation index](docs/README.md)
- [Research-first design spec](docs/superpowers/specs/2026-04-23-klippertouch-research-first-design.md)
- [KlipperScreen architecture map](docs/research/klipperscreen-architecture.md)
- [Printer read-only probe](docs/research/printer-readonly-probe-2026-04-23.md)
- [Roadmap](docs/roadmap.md)

## Development Commands

```bash
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
UV_INDEX_URL=https://pypi.org/simple uv run --locked --extra dev pytest
UV_INDEX_URL=https://pypi.org/simple uv run --locked --extra dev ruff check src tests
UV_INDEX_URL=https://pypi.org/simple uv run --locked --extra dev mypy src/klippertouch
UV_INDEX_URL=https://pypi.org/simple uv run --locked --extra dev python -m klippertouch --probe
```

Real-printer probes are read-only. Do not enable command execution without a separate reviewed plan.

## Safety Boundary

Until an implementation plan explicitly changes this boundary, real-printer validation is read-only only. Do not send movement, homing, heating, extrusion, print-control, restart, firmware-restart, power, or emergency-stop commands from this project.

## License

GPL-3.0-or-later. See [LICENSE](LICENSE).
