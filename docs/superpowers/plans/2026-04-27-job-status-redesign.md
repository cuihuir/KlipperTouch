# Job Status Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace per-metric `job_status` navigation with three semantic summary zones and a cleaner consumer-facing layout.

**Architecture:** Keep the implementation inside `JobStatusPanel.qml` because the existing panel already owns job state, details, and staged adjustment signals. Add small QML helper functions and a reusable summary-zone component, while preserving existing detail pages and read-only safety.

**Tech Stack:** PySide6, QML, pytest structure tests, offscreen screenshot capture.

---

### Task 1: Lock the Desired Structure With Tests

**Files:**
- Modify: `tests/qml/test_qml_loads.py`
- Read: `src/klippertouch/qml/panels/JobStatusPanel.qml`

- [ ] **Step 1: Write the failing structure assertions**

Add assertions to `test_job_status_panel_is_separate_from_files_panel_and_read_only` requiring `groupedSummaryModel`, `summaryZoneGrid`, `timeSummaryZone`, `motionSummaryZone`, and `materialSummaryZone`. Replace assertions that require `quickInfoGrid`, `summaryInfoModel`, and `onClicked: root.detailPage = modelData.target` with assertions that reject those strings.

- [ ] **Step 2: Run the targeted test and verify it fails**

Run: `.venv/bin/pytest tests/qml/test_qml_loads.py::test_job_status_panel_is_separate_from_files_panel_and_read_only -q`

Expected: failure showing the new grouped summary strings are missing.

### Task 2: Replace Per-Metric Cards With Three Summary Zones

**Files:**
- Modify: `src/klippertouch/qml/panels/JobStatusPanel.qml`
- Test: `tests/qml/test_qml_loads.py`

- [ ] **Step 1: Add grouped data helpers**

Replace `quickInfoLimit()` and `summaryInfoModel()` with `summaryZoneRows(zone)` and `groupedSummaryModel()`. The model must return exactly three entries: `time`, `motion`, and `extrusion`.

- [ ] **Step 2: Add a `SummaryZone` component**

Create one component that renders a title, a primary value, two to three secondary rows, and a single `MouseArea` for the whole zone.

- [ ] **Step 3: Replace `quickInfoGrid`**

Remove the eight-card `quickInfoGrid` and add `summaryZoneGrid` with three zone instances. Landscape should use three columns. Portrait should use one column so the zones remain readable.

- [ ] **Step 4: Run the targeted test and verify it passes**

Run: `.venv/bin/pytest tests/qml/test_qml_loads.py::test_job_status_panel_is_separate_from_files_panel_and_read_only -q`

Expected: pass.

### Task 3: Visual Pass and Screenshot Validation

**Files:**
- Modify: `src/klippertouch/qml/panels/JobStatusPanel.qml`
- Generate: `/tmp/klippertouch-job-redesign-round*/`

- [ ] **Step 1: Balance summary screen spacing**

Reduce visual noise, keep the hero compact, keep action buttons clearly button-like, and make summary zones dominant enough to read as grouped entry points.

- [ ] **Step 2: Capture screenshots**

Run: `QT_QPA_PLATFORM=offscreen .venv/bin/python tools/capture_qml_screenshots.py --output /tmp/klippertouch-job-redesign-round1 --sizes 800x480 480x800 1024x600 1920x440 --panels job_status --sample-files --sample-status --job-detail-pages summary time motion extrusion advanced exclude`

Expected: screenshots render without QML load errors.

- [ ] **Step 3: Iterate screenshots twice**

Repeat the capture into `round2` and `round3` after layout adjustments. Stop when summary, details, advanced, and exclude are all legible at the target sizes.

### Task 4: Full Verification and Commit

**Files:**
- Modify: `src/klippertouch/qml/panels/JobStatusPanel.qml`
- Modify: `tests/qml/test_qml_loads.py`
- Add: `docs/superpowers/specs/2026-04-27-job-status-redesign-design.md`
- Add: `docs/superpowers/plans/2026-04-27-job-status-redesign.md`

- [ ] **Step 1: Run checks**

Run:

```bash
.venv/bin/pytest -q
.venv/bin/ruff check src tests tools
.venv/bin/mypy src/klippertouch
git diff --check
```

Expected: all commands pass.

- [ ] **Step 2: Commit**

Run:

```bash
git add docs/superpowers src/klippertouch/qml/panels/JobStatusPanel.qml tests/qml/test_qml_loads.py
git commit -m "feat: group job status summary navigation"
```
