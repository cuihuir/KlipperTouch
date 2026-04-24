import sys
from pathlib import Path

from PySide6.QtCore import QSettings, QUrl
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication

from klippertouch.domain.gcode_files import files_from_moonraker
from klippertouch.domain.printer import PrinterStatus
from klippertouch.moonraker.client import MoonrakerClient
from klippertouch.moonraker.file_refresh import GCodeFileRefresh
from klippertouch.moonraker.status_stream import MoonrakerStatusStream
from klippertouch.qt_models.gcode_file_model import GCodeFileListModel
from klippertouch.qt_models.status_model import StatusModel, TemperatureDeviceListModel


def create_status_models(
    initial_status: PrinterStatus | None = None,
    initial_temperature_store: dict[str, object] | None = None,
) -> tuple[StatusModel, TemperatureDeviceListModel]:
    temperature_device_model = TemperatureDeviceListModel()
    status_model = StatusModel(temperature_device_model=temperature_device_model)
    if initial_status is not None:
        status_model.set_status(initial_status)
    if initial_temperature_store is not None:
        temperature_device_model.initialize_history(initial_temperature_store)
    return status_model, temperature_device_model


def create_gcode_file_model(
    initial_files: list[dict[str, object]] | None = None,
) -> GCodeFileListModel:
    model = GCodeFileListModel()
    if initial_files is not None:
        model.set_files(files_from_moonraker(initial_files))
    return model


def run_app(
    argv: list[str] | None = None,
    initial_status: PrinterStatus | None = None,
    initial_temperature_store: dict[str, object] | None = None,
    initial_files: list[dict[str, object]] | None = None,
    status_stream_client: MoonrakerClient | None = None,
    file_refresh_client: MoonrakerClient | None = None,
) -> int:
    app = QApplication(argv or [])
    app.setOrganizationName("KlipperTouch")
    app.setApplicationName("KlipperTouch")
    QSettings.setDefaultFormat(QSettings.Format.IniFormat)
    engine = QQmlApplicationEngine()
    status_model, temperature_device_model = create_status_models(
        initial_status,
        initial_temperature_store=initial_temperature_store,
    )
    gcode_file_model = create_gcode_file_model(initial_files)
    engine.rootContext().setContextProperty("statusModel", status_model)
    engine.rootContext().setContextProperty("temperatureDeviceModel", temperature_device_model)
    engine.rootContext().setContextProperty("gcodeFileModel", gcode_file_model)
    qml_path = Path(__file__).parent / "qml" / "main.qml"
    engine.load(QUrl.fromLocalFile(str(qml_path)))
    if not engine.rootObjects():
        return 1
    if initial_status is not None and status_stream_client is not None:
        status_stream = MoonrakerStatusStream(status_stream_client, status_model, initial_status)
        status_stream.start()
        engine.status_stream = status_stream  # type: ignore[attr-defined]
    if file_refresh_client is not None:
        file_refresh = GCodeFileRefresh(file_refresh_client, gcode_file_model)
        file_refresh.start()
        engine.gcode_file_refresh = file_refresh  # type: ignore[attr-defined]
    return app.exec()


def main(argv: list[str] | None = None) -> int:
    return run_app(argv or sys.argv)


if __name__ == "__main__":
    raise SystemExit(main())
