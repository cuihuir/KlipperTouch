# Main Menu Responsive Alignment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Align the QML main menu geometry with KlipperScreen's main menu behavior while preserving safe read-only UI placeholders.

**Architecture:** Keep the shell and status bar unchanged. Encode KlipperScreen's main-menu split and AutoGrid-like homogeneous menu behavior directly in `MainMenuPanel.qml`, with tests that assert the geometry contract from the source fork.

**Tech Stack:** PySide6, QML, pytest, ruff, mypy.

---

### Task 1: Capture KlipperScreen Main Menu Geometry

**Files:**
- Modify: `tests/qml/test_qml_loads.py`
- Modify: `src/klippertouch/qml/panels/MainMenuPanel.qml`

- [ ] **Step 1: Write the failing test**

Add a test that checks these source-derived contracts:

```python
def test_main_menu_matches_klipperscreen_split_and_autogrid_contract() -> None:
    qml = Path("src/klippertouch/qml/panels/MainMenuPanel.qml").read_text(encoding="utf-8")

    assert "property int virtualRows: 5" in qml
    assert "property int temperatureRows: 3" in qml
    assert "property int menuRows: 2" in qml
    assert "property int landscapeMenuRows: 3" in qml
    assert "property real landscapeTemperatureFraction: 0.5" in qml
    assert "width: root.metrics.portrait" in qml
    assert "height: root.metrics.portrait ? root.temperaturePanelHeight" in qml
    assert "columns: root.metrics.portrait ? 3 : 2" in qml
    assert "rows: root.metrics.portrait ? root.menuRows : root.landscapeMenuRows" in qml
    assert "Layout.columnSpan: root.shouldExpandLastTile(index) ? 2 : 1" in qml
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
UV_INDEX_URL=https://pypi.org/simple uv run --locked --extra dev pytest tests/qml/test_qml_loads.py::test_main_menu_matches_klipperscreen_split_and_autogrid_contract -q
```

Expected: fail because the new geometry contract is not yet encoded.

- [ ] **Step 3: Write minimal implementation**

In `MainMenuPanel.qml`, add explicit geometry properties:

```qml
property int virtualRows: 5
property int temperatureRows: 3
property int menuRows: 2
property int landscapeMenuRows: 3
property real landscapeTemperatureFraction: 0.5
property int temperaturePanelHeight: Math.round(parent.height * temperatureRows / virtualRows)
property int menuPanelHeight: parent.height - temperaturePanelHeight
function shouldExpandLastTile(index) {
    return index === menuModel.count - 1 && menuModel.count % 2 === 1
}
```

Use those properties so portrait allocates the temperature panel to 3/5 of content height and the menu to 2/5, landscape splits temperature/menu into equal columns, and the last odd menu tile spans two columns.

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
UV_INDEX_URL=https://pypi.org/simple uv run --locked --extra dev pytest tests/qml/test_qml_loads.py::test_main_menu_matches_klipperscreen_split_and_autogrid_contract -q
```

Expected: pass.

- [ ] **Step 5: Run full verification**

Run:

```bash
UV_INDEX_URL=https://pypi.org/simple uv run --locked --extra dev pytest -q
UV_INDEX_URL=https://pypi.org/simple uv run --locked --extra dev ruff check src tests
UV_INDEX_URL=https://pypi.org/simple uv run --locked --extra dev mypy src/klippertouch
```

Expected: all pass.

- [ ] **Step 6: Commit**

```bash
git add docs/superpowers/plans/2026-04-23-main-menu-responsive-alignment.md tests/qml/test_qml_loads.py src/klippertouch/qml/panels/MainMenuPanel.qml
git commit -m "fix: align main menu responsive geometry"
```
