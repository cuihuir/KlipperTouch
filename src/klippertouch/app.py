import sys
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication

from klippertouch.qt_models.status_model import StatusModel


def run_app(argv: list[str] | None = None) -> int:
    app = QApplication(argv or [])
    engine = QQmlApplicationEngine()
    status_model = StatusModel()
    engine.rootContext().setContextProperty("statusModel", status_model)
    qml_path = Path(__file__).parent / "qml" / "main.qml"
    engine.load(QUrl.fromLocalFile(str(qml_path)))
    if not engine.rootObjects():
        return 1
    return app.exec()


def main(argv: list[str] | None = None) -> int:
    return run_app(argv or sys.argv)


if __name__ == "__main__":
    raise SystemExit(main())
