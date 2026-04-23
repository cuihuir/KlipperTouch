import sys
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication

from klippertouch.qt_models.status_model import StatusModel, TemperatureDeviceListModel


def run_app(argv: list[str] | None = None) -> int:
    app = QApplication(argv or [])
    engine = QQmlApplicationEngine()
    temperature_device_model = TemperatureDeviceListModel()
    status_model = StatusModel(temperature_device_model=temperature_device_model)
    engine.rootContext().setContextProperty("statusModel", status_model)
    engine.rootContext().setContextProperty("temperatureDeviceModel", temperature_device_model)
    qml_path = Path(__file__).parent / "qml" / "main.qml"
    engine.load(QUrl.fromLocalFile(str(qml_path)))
    if not engine.rootObjects():
        return 1
    return app.exec()


def main(argv: list[str] | None = None) -> int:
    return run_app(argv or sys.argv)


if __name__ == "__main__":
    raise SystemExit(main())
