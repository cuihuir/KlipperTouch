import sys
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication

from klippertouch.domain.printer import PrinterStatus
from klippertouch.moonraker.client import MoonrakerClient
from klippertouch.moonraker.status_stream import MoonrakerStatusStream
from klippertouch.qt_models.status_model import StatusModel, TemperatureDeviceListModel


def create_status_models(
    initial_status: PrinterStatus | None = None,
) -> tuple[StatusModel, TemperatureDeviceListModel]:
    temperature_device_model = TemperatureDeviceListModel()
    status_model = StatusModel(temperature_device_model=temperature_device_model)
    if initial_status is not None:
        status_model.set_status(initial_status)
    return status_model, temperature_device_model


def run_app(
    argv: list[str] | None = None,
    initial_status: PrinterStatus | None = None,
    status_stream_client: MoonrakerClient | None = None,
) -> int:
    app = QApplication(argv or [])
    engine = QQmlApplicationEngine()
    status_model, temperature_device_model = create_status_models(initial_status)
    engine.rootContext().setContextProperty("statusModel", status_model)
    engine.rootContext().setContextProperty("temperatureDeviceModel", temperature_device_model)
    qml_path = Path(__file__).parent / "qml" / "main.qml"
    engine.load(QUrl.fromLocalFile(str(qml_path)))
    if not engine.rootObjects():
        return 1
    if initial_status is not None and status_stream_client is not None:
        status_stream = MoonrakerStatusStream(status_stream_client, status_model, initial_status)
        status_stream.start()
        engine.status_stream = status_stream  # type: ignore[attr-defined]
    return app.exec()


def main(argv: list[str] | None = None) -> int:
    return run_app(argv or sys.argv)


if __name__ == "__main__":
    raise SystemExit(main())
