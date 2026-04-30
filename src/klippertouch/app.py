import os
import sys
from pathlib import Path

from PySide6.QtCore import QSettings, QUrl
from PySide6.QtGui import QSurfaceFormat
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication

from klippertouch.domain.gcode_files import files_from_moonraker
from klippertouch.domain.printer import PrinterStatus
from klippertouch.moonraker.client import MoonrakerClient
from klippertouch.moonraker.file_refresh import GCodeFileRefresh
from klippertouch.moonraker.startup_loader import (
    StartupDataLoader,
    coerce_file_list,
    coerce_mapping,
    coerce_printer_status,
)
from klippertouch.moonraker.status_stream import MoonrakerStatusStream
from klippertouch.qt_models.gcode_file_model import GCodeFileListModel
from klippertouch.qt_models.job_control_model import JobControlModel
from klippertouch.qt_models.notification_model import NotificationModel
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


def configure_scenegraph_surface_format() -> None:
    if os.environ.get("QT_XCB_GL_INTEGRATION") != "xcb_egl":
        return

    surface_format = QSurfaceFormat()
    surface_format.setRenderableType(QSurfaceFormat.RenderableType.OpenGLES)
    surface_format.setVersion(3, 2)
    surface_format.setRedBufferSize(8)
    surface_format.setGreenBufferSize(8)
    surface_format.setBlueBufferSize(8)
    surface_format.setAlphaBufferSize(0)
    surface_format.setDepthBufferSize(0)
    surface_format.setStencilBufferSize(0)
    surface_format.setSamples(0)
    QSurfaceFormat.setDefaultFormat(surface_format)


def resolve_display_rotation() -> str:
    rotation = os.environ.get("KLIPPERTOUCH_DISPLAY_ROTATION", "").strip().lower()
    if rotation in {"right", "90", "clockwise", "cw"}:
        return "right"
    if rotation in {"left", "-90", "270", "counterclockwise", "ccw"}:
        return "left"
    return ""


def run_app(
    argv: list[str] | None = None,
    initial_status: PrinterStatus | None = None,
    initial_temperature_store: dict[str, object] | None = None,
    initial_files: list[dict[str, object]] | None = None,
    status_stream_client: MoonrakerClient | None = None,
    file_refresh_client: MoonrakerClient | None = None,
    job_control_client: MoonrakerClient | None = None,
    material_system_enabled: bool = False,
    read_only: bool = True,
    full_screen: bool = False,
) -> int:
    configure_scenegraph_surface_format()
    display_rotation = resolve_display_rotation()
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
    job_control_model = JobControlModel(job_control_client, status_model.extrusion_guard_status)
    notification_model = NotificationModel()
    startup_loader: StartupDataLoader | None = None
    file_refresh: GCodeFileRefresh | None = None
    if file_refresh_client is not None:
        file_refresh = GCodeFileRefresh(
            file_refresh_client,
            gcode_file_model,
            status_model=status_model,
        )
    engine.rootContext().setContextProperty("statusModel", status_model)
    engine.rootContext().setContextProperty("temperatureDeviceModel", temperature_device_model)
    engine.rootContext().setContextProperty("gcodeFileModel", gcode_file_model)
    engine.rootContext().setContextProperty("gcodeFileRefresh", file_refresh)
    engine.rootContext().setContextProperty("jobControlModel", job_control_model)
    engine.rootContext().setContextProperty("notificationModel", notification_model)
    engine.rootContext().setContextProperty(
        "configuredMaterialSystemEnabled",
        material_system_enabled,
    )
    engine.rootContext().setContextProperty("configuredReadOnly", read_only)
    engine.rootContext().setContextProperty("configuredFullScreen", full_screen)
    engine.rootContext().setContextProperty("configuredDisplayRotation", display_rotation)
    engine.job_control_model = job_control_model  # type: ignore[attr-defined]
    engine.notification_model = notification_model  # type: ignore[attr-defined]

    def start_status_stream(status: PrinterStatus) -> None:
        status_model.set_status(status)
        notification_model.addMoonrakerWarnings(status.moonraker_warnings)
        notification_model.addKlipperWarnings(status.klipper_warnings)
        if status_stream_client is None or hasattr(engine, "status_stream"):
            return
        if not status.objects:
            return
        status_stream = MoonrakerStatusStream(status_stream_client, status_model, status)
        status_stream.gcodeResponseReceived.connect(
            lambda message: notification_model.showToast("info", "Printer message", message)
        )
        status_stream.start()
        engine.status_stream = status_stream  # type: ignore[attr-defined]

    def apply_startup_status(value: object) -> None:
        status = coerce_printer_status(value)
        if status is not None:
            start_status_stream(status)

    def apply_startup_temperature_store(value: object) -> None:
        store = coerce_mapping(value)
        if store is not None:
            temperature_device_model.initialize_history(store)

    def apply_startup_files(value: object) -> None:
        files = coerce_file_list(value)
        if files is not None:
            gcode_file_model.set_files(files_from_moonraker(files))

    qml_path = Path(__file__).parent / "qml" / "main.qml"
    engine.load(QUrl.fromLocalFile(str(qml_path)))
    if not engine.rootObjects():
        return 1
    if initial_status is not None:
        start_status_stream(initial_status)
    elif status_stream_client is not None:
        startup_loader = StartupDataLoader(status_stream_client)
        startup_loader.statusLoaded.connect(apply_startup_status)
        startup_loader.temperatureStoreLoaded.connect(apply_startup_temperature_store)
        startup_loader.filesLoaded.connect(apply_startup_files)
        startup_loader.finished.connect(status_model.markBootstrapComplete)
        status_model.statusRetryRequested.connect(startup_loader.start)
        startup_loader.start()
        engine.startup_loader = startup_loader  # type: ignore[attr-defined]
    if file_refresh is not None:
        file_refresh.start()
        engine.gcode_file_refresh = file_refresh  # type: ignore[attr-defined]
    try:
        return app.exec()
    finally:
        job_control_model.stop()
        status_stream = getattr(engine, "status_stream", None)
        if status_stream is not None:
            status_stream.stop()
        if startup_loader is not None:
            startup_loader.stop()
        if file_refresh is not None:
            file_refresh.stop()


def main(argv: list[str] | None = None) -> int:
    return run_app(argv or sys.argv)


if __name__ == "__main__":
    raise SystemExit(main())
