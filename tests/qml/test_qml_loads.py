import ast
from pathlib import Path

import pytest
from PySide6.QtCore import QUrl
from PySide6.QtQml import QQmlApplicationEngine


def test_main_qml_loads(qapp) -> None:
    engine = QQmlApplicationEngine()
    qml_path = Path("src/klippertouch/qml/main.qml").resolve()
    engine.load(QUrl.fromLocalFile(str(qml_path)))
    assert engine.rootObjects()


def test_action_bar_has_at_most_four_shell_buttons() -> None:
    qml = Path("src/klippertouch/qml/components/ActionBar.qml").read_text(encoding="utf-8")
    marker = "property var buttonLabels:"
    model_line = next(line for line in qml.splitlines() if marker in line)
    model = ast.literal_eval(model_line.split(marker, maxsplit=1)[1].strip())

    assert len(model) <= 4


def test_action_bar_buttons_fill_available_axis() -> None:
    qml = Path("src/klippertouch/qml/components/ActionBar.qml").read_text(encoding="utf-8")

    assert "Flow {" not in qml
    assert "Grid {" in qml
    assert "rows: root.vertical ? root.buttonLabels.length : 1" in qml
    assert "columns: root.vertical ? 1 : root.buttonLabels.length" in qml
    assert "height: buttonGrid.cellHeight" in qml
    assert "width: buttonGrid.cellWidth" in qml


def test_status_bar_matches_klipperscreen_titlebar_structure() -> None:
    qml = Path("src/klippertouch/qml/components/StatusBar.qml").read_text(encoding="utf-8")

    assert "property string printerName" in qml
    assert "property string panelTitle" in qml
    assert "property string clockText" in qml
    assert "id: heaterStrip" in qml
    assert "id: titleLabel" in qml
    assert "id: clockLabel" in qml
    assert 'text: root.printerName + " | " + root.panelTitle' in qml


def test_shell_has_responsive_orientation_hooks() -> None:
    metrics_qml = Path("src/klippertouch/qml/Metrics.qml").read_text(encoding="utf-8")
    shell_qml = Path("src/klippertouch/qml/components/BaseShell.qml").read_text(encoding="utf-8")
    action_bar_qml = Path("src/klippertouch/qml/components/ActionBar.qml").read_text(
        encoding="utf-8"
    )

    assert "property bool portrait" in metrics_qml
    assert "property real fontSize" in metrics_qml
    assert "property int actionBarWidth" in metrics_qml
    assert "property int contentHeight" in metrics_qml
    assert "anchors.bottom: root.metrics.portrait ? parent.bottom : undefined" in shell_qml
    assert "property bool vertical" in action_bar_qml


def test_responsive_layout_components_exist() -> None:
    qml_dir = Path("src/klippertouch/qml")
    expected = [
        qml_dir / "Metrics.qml",
        qml_dir / "components" / "BaseShell.qml",
        qml_dir / "panels" / "MainMenuPanel.qml",
        qml_dir / "components" / "MenuTile.qml",
        qml_dir / "components" / "TemperatureSummary.qml",
        qml_dir / "components" / "FakeTemperatureGraph.qml",
    ]

    missing = [path for path in expected if not path.exists()]

    assert missing == []


def test_main_uses_responsive_base_shell_and_main_panel() -> None:
    main_qml = Path("src/klippertouch/qml/main.qml").read_text(encoding="utf-8")

    assert "BaseShell {" in main_qml
    assert "MainMenuPanel {" in main_qml
    assert "Metrics {" in main_qml


@pytest.mark.parametrize(("width", "height"), [(800, 480), (1024, 600), (480, 800)])
def test_main_qml_loads_common_screen_shapes(qapp, width: int, height: int) -> None:
    engine = QQmlApplicationEngine()
    qml_path = Path("src/klippertouch/qml/main.qml").resolve()
    engine.load(QUrl.fromLocalFile(str(qml_path)))
    assert engine.rootObjects()

    root = engine.rootObjects()[0]
    root.setProperty("width", width)
    root.setProperty("height", height)
    qapp.processEvents()

    assert root.property("width") == width
    assert root.property("height") == height
