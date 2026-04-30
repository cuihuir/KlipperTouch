from PySide6.QtGui import QSurfaceFormat

from klippertouch import app
from klippertouch.domain.printer import PrinterStatus


def test_app_main_delegates_to_run_app(monkeypatch) -> None:
    calls: list[list[str]] = []

    def fake_run_app(argv: list[str] | None = None) -> int:
        calls.append(argv or [])
        return 0

    monkeypatch.setattr(app, "run_app", fake_run_app)

    assert app.main(["klippertouch"]) == 0
    assert calls == [["klippertouch"]]


def test_app_registers_temperature_device_model_context() -> None:
    source = app.Path(app.__file__).read_text(encoding="utf-8")

    assert "TemperatureDeviceListModel" in source
    assert "status_model = StatusModel(temperature_device_model=temperature_device_model)" in source
    assert 'setContextProperty("temperatureDeviceModel", temperature_device_model)' in source


def test_app_registers_gcode_file_model_context() -> None:
    source = app.Path(app.__file__).read_text(encoding="utf-8")

    assert "GCodeFileListModel" in source
    assert 'setContextProperty("gcodeFileModel", gcode_file_model)' in source


def test_app_registers_job_control_context() -> None:
    source = app.Path(app.__file__).read_text(encoding="utf-8")

    assert "JobControlModel" in source
    assert (
        "job_control_model = JobControlModel("
        "job_control_client, status_model.extrusion_guard_status)"
        in source
    )
    assert 'setContextProperty("jobControlModel", job_control_model)' in source


def test_app_registers_notification_context() -> None:
    source = app.Path(app.__file__).read_text(encoding="utf-8")

    assert "NotificationModel" in source
    assert "notification_model = NotificationModel()" in source
    assert "notification_model.addMoonrakerWarnings(status.moonraker_warnings)" in source
    assert "notification_model.addKlipperWarnings(status.klipper_warnings)" in source
    assert 'setContextProperty("notificationModel", notification_model)' in source
    assert "engine.notification_model = notification_model" in source


def test_app_registers_material_system_context() -> None:
    source = app.Path(app.__file__).read_text(encoding="utf-8")

    assert "material_system_enabled: bool = False" in source
    assert 'setContextProperty(\n        "configuredMaterialSystemEnabled"' in source


def test_app_registers_fullscreen_context() -> None:
    source = app.Path(app.__file__).read_text(encoding="utf-8")

    assert "full_screen: bool = False" in source
    assert 'setContextProperty("configuredFullScreen", full_screen)' in source


def test_app_registers_read_only_context() -> None:
    source = app.Path(app.__file__).read_text(encoding="utf-8")

    assert "read_only: bool = True" in source
    assert 'setContextProperty("configuredReadOnly", read_only)' in source


def test_resolve_display_rotation_normalizes_supported_values(monkeypatch) -> None:
    monkeypatch.setenv("KLIPPERTOUCH_DISPLAY_ROTATION", " RIGHT ")
    assert app.resolve_display_rotation() == "right"

    monkeypatch.setenv("KLIPPERTOUCH_DISPLAY_ROTATION", "90")
    assert app.resolve_display_rotation() == "right"

    monkeypatch.setenv("KLIPPERTOUCH_DISPLAY_ROTATION", "-90")
    assert app.resolve_display_rotation() == "left"

    monkeypatch.setenv("KLIPPERTOUCH_DISPLAY_ROTATION", "none")
    assert app.resolve_display_rotation() == ""


def test_app_registers_display_rotation_context() -> None:
    source = app.Path(app.__file__).read_text(encoding="utf-8")

    assert "resolve_display_rotation()" in source
    assert 'setContextProperty("configuredDisplayRotation", display_rotation)' in source


def test_app_configures_x11_egl_surface_format(monkeypatch) -> None:
    original_format = QSurfaceFormat.defaultFormat()
    try:
        QSurfaceFormat.setDefaultFormat(QSurfaceFormat())
        monkeypatch.setenv("QT_XCB_GL_INTEGRATION", "xcb_egl")

        app.configure_scenegraph_surface_format()

        surface_format = QSurfaceFormat.defaultFormat()
        assert surface_format.renderableType() == QSurfaceFormat.RenderableType.OpenGLES
        assert surface_format.redBufferSize() == 8
        assert surface_format.greenBufferSize() == 8
        assert surface_format.blueBufferSize() == 8
        assert surface_format.alphaBufferSize() == 0
        assert surface_format.depthBufferSize() == 0
        assert surface_format.stencilBufferSize() == 0
        assert surface_format.samples() == 0
    finally:
        QSurfaceFormat.setDefaultFormat(original_format)


def test_create_status_models_applies_initial_status(qtbot) -> None:
    status = PrinterStatus(objects=("extruder", "heater_bed"))

    status_model, temperature_model = app.create_status_models(status)

    assert status_model.temperatureDeviceCount == 2
    assert temperature_model.rowCount() == 2


def test_create_gcode_file_model_applies_initial_files(qtbot) -> None:
    file_model = app.create_gcode_file_model(
        [
            {
                "path": "calibration/cube.gcode",
                "modified": 1710000000.5,
                "size": 2048,
                "permissions": "rw",
            }
        ]
    )

    assert file_model.rowCount() == 1


def test_run_app_wires_optional_read_only_status_stream() -> None:
    source = app.Path(app.__file__).read_text(encoding="utf-8")

    assert "MoonrakerStatusStream" in source
    assert "status_stream_client" in source
    assert "if not status.objects:" in source
    assert "status_stream.gcodeResponseReceived.connect" in source
    assert 'notification_model.showToast("info", "Printer message", message)' in source
    assert "status_stream.start()" in source
    assert "engine.status_stream = status_stream" in source


def test_run_app_bootstraps_initial_moonraker_data_after_qml_load() -> None:
    source = app.Path(app.__file__).read_text(encoding="utf-8")

    assert "StartupDataLoader" in source
    assert "startup_loader.start()" in source
    assert source.index("engine.load(") < source.index("startup_loader.start()")
    assert "engine.startup_loader = startup_loader" in source
    assert "build_basic_status_from_client(self._client)" in app.Path(
        app.__file__
    ).with_name("moonraker").joinpath("startup_loader.py").read_text(encoding="utf-8")
    assert "startup_loader.finished.connect(status_model.markBootstrapComplete)" in source
    assert "status_model.statusRetryRequested.connect(startup_loader.start)" in source


def test_run_app_stops_background_loaders_when_app_exits() -> None:
    source = app.Path(app.__file__).read_text(encoding="utf-8")

    assert "try:\n        return app.exec()\n    finally:" in source
    assert "job_control_model.stop()" in source
    assert "status_stream.stop()" in source
    assert "startup_loader.stop()" in source
    assert "file_refresh.stop()" in source
