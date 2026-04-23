from klippertouch import app


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
    assert 'setContextProperty("temperatureDeviceModel", temperature_device_model)' in source
