import ast
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtQml import QQmlApplicationEngine


def test_main_qml_loads(qapp) -> None:
    engine = QQmlApplicationEngine()
    qml_path = Path("src/klippertouch/qml/main.qml").resolve()
    engine.load(QUrl.fromLocalFile(str(qml_path)))
    assert engine.rootObjects()


def test_action_bar_has_at_most_four_shell_buttons() -> None:
    qml = Path("src/klippertouch/qml/components/ActionBar.qml").read_text(encoding="utf-8")
    marker = "model:"
    model_line = next(line for line in qml.splitlines() if marker in line)
    model = ast.literal_eval(model_line.split(marker, maxsplit=1)[1].strip())

    assert len(model) <= 4


def test_shell_has_responsive_orientation_hooks() -> None:
    main_qml = Path("src/klippertouch/qml/main.qml").read_text(encoding="utf-8")
    action_bar_qml = Path("src/klippertouch/qml/components/ActionBar.qml").read_text(
        encoding="utf-8"
    )

    assert "property bool isPortrait" in main_qml
    assert "property int barThickness" in main_qml
    assert "anchors.bottom: window.isPortrait ? parent.bottom : undefined" in main_qml
    assert "property bool vertical" in action_bar_qml
