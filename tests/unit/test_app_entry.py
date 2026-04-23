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


def test_create_status_models_applies_initial_status(qtbot) -> None:
    status = PrinterStatus(objects=("extruder", "heater_bed"))

    status_model, temperature_model = app.create_status_models(status)

    assert status_model.temperatureDeviceCount == 2
    assert temperature_model.rowCount() == 2
