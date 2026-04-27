# Job Status Visual Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rework `JobStatusPanel.qml` into a styled dark industrial print console with consistent, compact controls.

**Architecture:** Keep behavior read-only and local to `JobStatusPanel.qml`. Add QML-local visual components for status cards, metric pills, and control buttons so the layout can be reused by summary, advanced tuning, and object exclusion subpages without introducing new Python state.

**Tech Stack:** PySide6/QML, existing `Theme.js`, pytest string-structure checks, offscreen screenshot capture.

---

### Task 1: Lock Visual Structure

**Files:**
- Modify: `tests/qml/test_qml_loads.py`

- [x] Add failing assertions for Job Status visual components: `MetricPill`, `StatusCard`, `ConsoleButton`, gradient background, danger/primary button variants, and compact control sizing.
- [x] Run `pytest tests/qml/test_qml_loads.py::test_job_status_panel_is_separate_from_files_panel_and_read_only -q` and verify failure before production code.

### Task 2: Redesign Job Status QML

**Files:**
- Modify: `src/klippertouch/qml/panels/JobStatusPanel.qml`

- [x] Replace the plain action area with compact console buttons.
- [x] Add a styled status card with gradient, accent line, styled progress bar, and metric pills.
- [x] Reuse button styling in Advanced and Object exclusion.
- [x] Preserve global Back behavior and read-only command boundary.

### Task 3: Validate And Commit

**Files:**
- Verify: `tests/qml/test_qml_loads.py`
- Verify: `tools/capture_qml_screenshots.py`

- [x] Capture `job_status` summary, advanced, and exclude at `800x480` and `480x800`.
- [x] Run `pytest`, `ruff`, `mypy`, and `git diff --check`.
- [x] Commit the redesign after screenshot review.
