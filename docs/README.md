# KlipperTouch Documentation

This documentation is organized for long-term maintenance rather than short-term prototyping.

## Primary Specs

- `docs/superpowers/specs/2026-04-23-klippertouch-research-first-design.md` defines the approved research-first phase.

## Research

- `docs/research/klipperscreen-architecture.md` maps KlipperScreen concepts to planned KlipperTouch modules.
- `docs/research/printer-readonly-probe-2026-04-23.md` records the real-printer read-only validation result.
- `docs/research/printer-readonly-probe-2026-04-24.md` records the current real-printer read-only validation result.
- `docs/research/printer-readonly-probe-2026-04-30.md` records the current read-only
  status, file-list, metadata, and thumbnail validation result.

## Planning

- `docs/roadmap.md` tracks the staged path from research to a production-ready PySide6/QML application.
- `docs/safety-boundary.md` records the current runtime safety boundary, read-only allowlist, enabled commands, and verification commands.

## Documentation Rules

- Keep source-derived observations separate from design decisions.
- Record real-printer commands before running them, and keep new command groups behind the audited control bridge.
- Prefer small, stable documents with clear ownership over large catch-all notes.
- Update the roadmap when a spec changes scope.
