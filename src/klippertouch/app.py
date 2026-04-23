from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication


def run_app(argv: list[str] | None = None) -> int:
    app = QApplication(argv or [])
    engine = QQmlApplicationEngine()
    qml_path = Path(__file__).parent / "qml" / "main.qml"
    engine.load(QUrl.fromLocalFile(str(qml_path)))
    if not engine.rootObjects():
        return 1
    return app.exec()
