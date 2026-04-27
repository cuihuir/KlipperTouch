# Repository Guidelines

## Project Structure & Module Organization
Core application code lives in `src/klippertouch/`. Keep Python logic in focused packages:
- `config/` for config parsing and models
- `domain/` for printer and G-code domain objects
- `moonraker/` for read-only API, websocket, and refresh logic
- `qt_models/` for PySide models exposed to QML
- `qml/` for UI panels, shared components, models, and SVG assets

Tests live under `tests/`:
- `tests/unit/` for Python logic
- `tests/qml/` for QML structure and load checks

Utilities such as screenshot capture live in `tools/`. Longer-form docs and roadmap notes belong in `docs/`.

## Build, Test, and Development Commands
- `UV_INDEX_URL=https://pypi.org/simple uv sync --locked --extra dev` installs dev dependencies.
- `UV_INDEX_URL=https://pypi.org/simple uv run --locked python -m klippertouch --debug` launches the GUI locally.
- `UV_INDEX_URL=https://pypi.org/simple uv run --locked python -m klippertouch --probe` runs a read-only Moonraker probe.
- `UV_INDEX_URL=https://pypi.org/simple uv run --locked pytest -q` runs the full test suite.
- `UV_INDEX_URL=https://pypi.org/simple uv run --locked ruff check src tests tools` runs linting.
- `UV_INDEX_URL=https://pypi.org/simple uv run --locked mypy src/klippertouch` runs strict type checks.

## Coding Style & Naming Conventions
Use 4-space indentation and keep Python compatible with 3.10+. Ruff enforces import sorting and basic correctness; mypy runs in strict mode. Prefer small typed functions and dataclasses for domain state.

QML files use `PascalCase.qml` for components and panels. Python modules use `snake_case.py`. Match existing names such as `TemperaturePanel.qml`, `status_model.py`, and `test_status_model.py`.

## Testing Guidelines
Write pytest tests for every behavior change. Add unit tests beside the affected area and update `tests/qml/test_qml_loads.py` when changing QML structure. For UI work, generate screenshots with `tools/capture_qml_screenshots.py` and inspect target sizes such as `800x480` and `480x800`.

## Commit & Pull Request Guidelines
Recent history follows short conventional commits like `feat: ...`, `fix: ...`, and `chore: ...`. Keep subjects imperative and specific.

PRs should include:
- a short behavior summary
- linked issue or task context
- test results (`pytest`, `ruff`, `mypy`)
- screenshots for visible QML changes
- explicit note if real-printer validation was read-only

## Safety & Configuration Tips
Real printer interaction is read-only by default. Do not add movement, heating, extrusion, print-control, or restart commands without an explicit reviewed plan. Keep local printer configs out of git; use ignored files such as `config/KlipperTouch.conf`.
