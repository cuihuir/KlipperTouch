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
    assert "job_control_model = JobControlModel(job_control_client)" in source
    assert 'setContextProperty("jobControlModel", job_control_model)' in source


def test_app_registers_notification_context() -> None:
    source = app.Path(app.__file__).read_text(encoding="utf-8")

    assert "NotificationModel" in source
    assert "notification_model = NotificationModel()" in source
    assert "notification_model.addMoonrakerWarnings(initial_status.moonraker_warnings)" in source
    assert 'setContextProperty("notificationModel", notification_model)' in source
    assert "engine.notification_model = notification_model" in source


def test_app_registers_material_system_context() -> None:
    source = app.Path(app.__file__).read_text(encoding="utf-8")

    assert "material_system_enabled: bool = False" in source
    assert 'setContextProperty(\n        "configuredMaterialSystemEnabled"' in source


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
    assert "status_stream.gcodeResponseReceived.connect" in source
    assert 'notification_model.showToast("info", "Printer message", message)' in source
    assert "status_stream.start()" in source
    assert "engine.status_stream = status_stream" in source
