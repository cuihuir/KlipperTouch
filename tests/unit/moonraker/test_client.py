import pytest

from klippertouch.config.models import PrinterConfig
from klippertouch.moonraker.client import MoonrakerClient
from klippertouch.moonraker.safety import CommandPolicy, UnsafeCommandError


def test_client_builds_plain_http_endpoint() -> None:
    client = MoonrakerClient(PrinterConfig(name="p", moonraker_host="host", moonraker_port=7125))
    assert client.endpoint == "http://host:7125"
    assert client.websocket_endpoint == "ws://host:7125/websocket"


def test_client_builds_path_and_ssl_endpoint() -> None:
    client = MoonrakerClient(
        PrinterConfig(
            name="p",
            moonraker_host="host",
            moonraker_port=7130,
            moonraker_path="printer",
            moonraker_ssl=True,
        )
    )
    assert client.endpoint == "https://host:7130/printer"
    assert client.websocket_endpoint == "wss://host:7130/printer/websocket"


def test_client_normalizes_surrounding_endpoint_path_slashes() -> None:
    client = MoonrakerClient(
        PrinterConfig(
            name="p",
            moonraker_host="host",
            moonraker_port=7130,
            moonraker_path="/moonraker/",
        )
    )
    assert client.endpoint == "http://host:7130/moonraker"


def test_client_get_sends_request_and_unwraps_result(monkeypatch) -> None:
    captured: dict[str, object] = {}

    class FakeResponse:
        raise_called = False

        def raise_for_status(self) -> None:
            self.raise_called = True

        def json(self) -> dict[str, object]:
            return {"result": {"state": "ready"}}

    response = FakeResponse()

    def fake_get(
        url: str,
        *,
        headers: dict[str, str],
        params: dict[str, str] | None,
        timeout: float,
    ) -> FakeResponse:
        captured["url"] = url
        captured["headers"] = headers
        captured["params"] = params
        captured["timeout"] = timeout
        return response

    monkeypatch.setattr("klippertouch.moonraker.client.requests.get", fake_get)

    client = MoonrakerClient(
        PrinterConfig(
            name="p",
            moonraker_host="host",
            moonraker_port=7125,
            moonraker_api_key="secret",
        )
    )

    result = client.get("/server/info/", timeout=9.5)

    assert result == {"state": "ready"}
    assert captured == {
        "url": "http://host:7125/server/info",
        "headers": {"x-api-key": "secret"},
        "params": None,
        "timeout": 9.5,
    }
    assert response.raise_called is True


def test_client_gets_printer_objects_query(monkeypatch) -> None:
    captured: dict[str, object] = {}

    class FakeResponse:
        def raise_for_status(self) -> None:
            pass

        def json(self) -> dict[str, object]:
            return {"result": {"status": {"extruder": {"temperature": 24.3}}}}

    def fake_get(
        url: str,
        *,
        headers: dict[str, str],
        params: dict[str, str] | None,
        timeout: float,
    ) -> FakeResponse:
        captured["url"] = url
        captured["headers"] = headers
        captured["params"] = params
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr("klippertouch.moonraker.client.requests.get", fake_get)

    client = MoonrakerClient(PrinterConfig(name="p", moonraker_host="host"))

    assert client.get_printer_objects_query(("extruder", "heater_bed")) == {
        "status": {"extruder": {"temperature": 24.3}}
    }
    assert captured["url"] == "http://host:7125/printer/objects/query"
    assert captured["params"] == {
        "extruder": "temperature,target,pressure_advance,smooth_time",
        "heater_bed": "temperature,target",
    }


def test_client_queries_webhooks_state_fields(monkeypatch) -> None:
    captured: dict[str, object] = {}

    class FakeResponse:
        def raise_for_status(self) -> None:
            pass

        def json(self) -> dict[str, object]:
            return {"result": {"status": {"webhooks": {"state": "ready"}}}}

    def fake_get(
        _url: str,
        *,
        headers: dict[str, str],
        params: dict[str, str] | None,
        timeout: float,
    ) -> FakeResponse:
        captured["params"] = params
        return FakeResponse()

    monkeypatch.setattr("klippertouch.moonraker.client.requests.get", fake_get)

    client = MoonrakerClient(PrinterConfig(name="p", moonraker_host="host"))

    assert client.get_printer_objects_query(("webhooks",)) == {
        "status": {"webhooks": {"state": "ready"}}
    }
    assert captured["params"] == {"webhooks": "state,state_message"}


def test_client_gets_printer_objects_query_with_jsonrpc(monkeypatch) -> None:
    captured: dict[str, object] = {}

    class FakeResponse:
        def raise_for_status(self) -> None:
            pass

        def json(self) -> dict[str, object]:
            return {
                "result": {
                    "status": {
                        "temperature_fan SOC散热": {"temperature": 42.5, "target": 40.0}
                    }
                }
            }

    def fake_post(
        url: str,
        *,
        headers: dict[str, str],
        json: dict[str, object],
        timeout: float,
    ) -> FakeResponse:
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr("klippertouch.moonraker.client.requests.post", fake_post)

    client = MoonrakerClient(
        PrinterConfig(name="p", moonraker_host="host", moonraker_api_key="secret")
    )

    assert client.get_printer_objects_query_jsonrpc(
        {"temperature_fan SOC散热": ["temperature", "target"]}
    ) == {
        "status": {"temperature_fan SOC散热": {"temperature": 42.5, "target": 40.0}}
    }
    assert captured == {
        "url": "http://host:7125/server/jsonrpc",
        "headers": {"x-api-key": "secret"},
        "json": {
            "jsonrpc": "2.0",
            "method": "printer.objects.query",
            "params": {"objects": {"temperature_fan SOC散热": ["temperature", "target"]}},
            "id": 1,
        },
        "timeout": 4.0,
    }


def test_client_blocks_unsafe_jsonrpc_before_network(monkeypatch) -> None:
    calls: list[bool] = []

    def fake_post(*_args: object, **_kwargs: object) -> object:
        calls.append(True)
        raise AssertionError("network should not be called")

    monkeypatch.setattr("klippertouch.moonraker.client.requests.post", fake_post)

    client = MoonrakerClient(PrinterConfig(name="p", moonraker_host="host"))

    with pytest.raises(UnsafeCommandError):
        client.post_jsonrpc("printer.gcode.script", params={"script": "M112"})

    assert calls == []


def test_client_starts_gcode_print_when_controls_enabled(monkeypatch) -> None:
    captured: dict[str, object] = {}

    class FakeResponse:
        def raise_for_status(self) -> None:
            pass

        def json(self) -> dict[str, object]:
            return {"result": {"ok": True}}

    def fake_post(
        url: str,
        *,
        headers: dict[str, str],
        json: dict[str, object],
        timeout: float,
    ) -> FakeResponse:
        captured["url"] = url
        captured["json"] = json
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr("klippertouch.moonraker.client.requests.post", fake_post)

    client = MoonrakerClient(
        PrinterConfig(name="p", moonraker_host="host"),
        policy=CommandPolicy(read_only=False),
    )

    assert client.start_print("cube.gcode") == {"ok": True}
    assert captured["url"] == "http://host:7125/server/jsonrpc"
    assert captured["json"] == {
        "jsonrpc": "2.0",
        "method": "printer.print.start",
        "params": {"filename": "cube.gcode"},
        "id": 1,
    }
    assert captured["timeout"] == 4.0


@pytest.mark.parametrize(
    ("client_method", "jsonrpc_method"),
    [
        ("pause_print", "printer.print.pause"),
        ("resume_print", "printer.print.resume"),
        ("cancel_print", "printer.print.cancel"),
        ("firmware_restart", "printer.firmware_restart"),
        ("restart_klipper", "printer.restart"),
        ("emergency_stop", "printer.emergency_stop"),
    ],
)
def test_client_sends_print_control_when_controls_enabled(
    monkeypatch,
    client_method: str,
    jsonrpc_method: str,
) -> None:
    captured: dict[str, object] = {}

    class FakeResponse:
        def raise_for_status(self) -> None:
            pass

        def json(self) -> dict[str, object]:
            return {"result": {"ok": True}}

    def fake_post(
        _url: str,
        *,
        headers: dict[str, str],
        json: dict[str, object],
        timeout: float,
    ) -> FakeResponse:
        captured["json"] = json
        return FakeResponse()

    monkeypatch.setattr("klippertouch.moonraker.client.requests.post", fake_post)

    client = MoonrakerClient(
        PrinterConfig(name="p", moonraker_host="host"),
        policy=CommandPolicy(read_only=False),
    )

    assert getattr(client, client_method)() == {"ok": True}
    assert captured["json"] == {
        "jsonrpc": "2.0",
        "method": jsonrpc_method,
        "params": {},
        "id": 1,
    }


@pytest.mark.parametrize(
    ("client_method", "argument", "script"),
    [
        ("adjust_z_offset", 0.05, "SET_GCODE_OFFSET Z_ADJUST=0.050 MOVE=1"),
        ("adjust_z_offset", -0.05, "SET_GCODE_OFFSET Z_ADJUST=-0.050 MOVE=1"),
        ("set_speed_factor", 95.0, "M220 S95"),
        ("set_extrude_factor", 105.0, "M221 S105"),
        ("exclude_object", "part_a", "EXCLUDE_OBJECT NAME=part_a"),
        ("clear_sdcard_file", None, "SDCARD_RESET_FILE"),
        ("disable_motors", None, "M84"),
        (
            "jog_toolhead",
            ("x", -10.0),
            "_CLIENT_LINEAR_MOVE X=-10.000 F=6000",
        ),
        (
            "jog_toolhead",
            ("z", 0.5),
            "_CLIENT_LINEAR_MOVE Z=0.500 F=600",
        ),
        ("home_axes", ("x", "y"), "G28 X Y"),
        ("home_axes", ("z",), "G28 Z"),
        ("home_axes", (), "G28"),
        (
            "extrude_filament",
            (10.0, 5.0),
            "_CLIENT_LINEAR_MOVE E=10.000 F=300",
        ),
        (
            "extrude_filament",
            (-5.0, 2.0),
            "_CLIENT_LINEAR_MOVE E=-5.000 F=120",
        ),
        ("load_filament", 5.0, "LOAD_FILAMENT SPEED=300"),
        ("unload_filament", 2.0, "UNLOAD_FILAMENT SPEED=120"),
        (
            "set_temperature_target",
            ("extruder", 0.0),
            'SET_HEATER_TEMPERATURE heater="extruder" target=0',
        ),
        (
            "set_temperature_target",
            ("heater_bed", 60.0),
            'SET_HEATER_TEMPERATURE heater="heater_bed" target=60',
        ),
        (
            "set_temperature_target",
            ("temperature_fan SOC散热", 40.0),
            'SET_TEMPERATURE_FAN_TARGET temperature_fan="SOC散热" target=40',
        ),
        (
            "set_pressure_advance",
            (0.045, 0.04),
            "SET_PRESSURE_ADVANCE ADVANCE=0.045 SMOOTH_TIME=0.040",
        ),
    ],
)
def test_client_sends_gcode_control_scripts_when_controls_enabled(
    monkeypatch,
    client_method: str,
    argument: float | str | tuple[object, ...],
    script: str,
) -> None:
    captured: dict[str, object] = {}

    class FakeResponse:
        def raise_for_status(self) -> None:
            pass

        def json(self) -> dict[str, object]:
            return {"result": {"ok": True}}

    def fake_post(
        _url: str,
        *,
        headers: dict[str, str],
        json: dict[str, object],
        timeout: float,
    ) -> FakeResponse:
        captured["json"] = json
        return FakeResponse()

    monkeypatch.setattr("klippertouch.moonraker.client.requests.post", fake_post)

    client = MoonrakerClient(
        PrinterConfig(name="p", moonraker_host="host"),
        policy=CommandPolicy(read_only=False),
    )

    if isinstance(argument, tuple):
        assert getattr(client, client_method)(*argument) == {"ok": True}
    elif argument is None:
        assert getattr(client, client_method)() == {"ok": True}
    else:
        assert getattr(client, client_method)(argument) == {"ok": True}
    assert captured["json"] == {
        "jsonrpc": "2.0",
        "method": "printer.gcode.script",
        "params": {"script": script},
        "id": 1,
    }


def test_client_blocks_print_control_in_read_only_mode(monkeypatch) -> None:
    calls: list[str] = []

    def fake_post(*_args: object, **_kwargs: object) -> object:
        calls.append("post")
        raise AssertionError("network should not be called")

    def fake_delete(*_args: object, **_kwargs: object) -> object:
        calls.append("delete")
        raise AssertionError("network should not be called")

    monkeypatch.setattr("klippertouch.moonraker.client.requests.post", fake_post)
    monkeypatch.setattr("klippertouch.moonraker.client.requests.delete", fake_delete)

    client = MoonrakerClient(PrinterConfig(name="p", moonraker_host="host"))

    with pytest.raises(UnsafeCommandError):
        client.start_print("cube.gcode")
    with pytest.raises(UnsafeCommandError):
        client.pause_print()
    with pytest.raises(UnsafeCommandError):
        client.resume_print()
    with pytest.raises(UnsafeCommandError):
        client.cancel_print()
    with pytest.raises(UnsafeCommandError):
        client.firmware_restart()
    with pytest.raises(UnsafeCommandError):
        client.restart_klipper()
    with pytest.raises(UnsafeCommandError):
        client.emergency_stop()
    with pytest.raises(UnsafeCommandError):
        client.adjust_z_offset(0.05)
    with pytest.raises(UnsafeCommandError):
        client.set_speed_factor(95)
    with pytest.raises(UnsafeCommandError):
        client.set_extrude_factor(105)
    with pytest.raises(UnsafeCommandError):
        client.exclude_object("part_a")
    with pytest.raises(UnsafeCommandError):
        client.delete_gcode_file("cube.gcode")
    with pytest.raises(UnsafeCommandError):
        client.clear_sdcard_file()

    assert calls == []


def test_client_deletes_gcode_file_when_controls_enabled(monkeypatch) -> None:
    captured: dict[str, object] = {}

    class FakeResponse:
        def raise_for_status(self) -> None:
            pass

        def json(self) -> dict[str, object]:
            return {"result": {"item": {"path": "folder/cube.gcode"}}}

    def fake_delete(
        url: str,
        *,
        headers: dict[str, str],
        timeout: float,
    ) -> FakeResponse:
        captured["url"] = url
        captured["headers"] = headers
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr("klippertouch.moonraker.client.requests.delete", fake_delete)

    client = MoonrakerClient(
        PrinterConfig(name="p", moonraker_host="host", moonraker_api_key="secret"),
        policy=CommandPolicy(read_only=False),
    )

    assert client.delete_gcode_file("folder/cube.gcode") == {
        "item": {"path": "folder/cube.gcode"}
    }
    assert captured == {
        "url": "http://host:7125/server/files/gcodes/folder/cube.gcode",
        "headers": {"x-api-key": "secret"},
        "timeout": 4.0,
    }


def test_client_uploads_gcode_file_when_controls_enabled(monkeypatch) -> None:
    captured: dict[str, object] = {}

    class FakeResponse:
        def raise_for_status(self) -> None:
            pass

        def json(self) -> dict[str, object]:
            return {"result": {"item": {"path": "smoke/kt_smoke.gcode"}}}

    def fake_post(
        url: str,
        *,
        headers: dict[str, str],
        data: dict[str, str],
        files: dict[str, tuple[str, bytes, str]],
        timeout: float,
    ) -> FakeResponse:
        captured["url"] = url
        captured["headers"] = headers
        captured["data"] = data
        captured["files"] = files
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr("klippertouch.moonraker.client.requests.post", fake_post)

    client = MoonrakerClient(
        PrinterConfig(name="p", moonraker_host="host", moonraker_api_key="secret"),
        policy=CommandPolicy(read_only=False),
    )

    assert client.upload_gcode_file(
        "kt_smoke.gcode",
        b"; smoke\nM117 KT\n",
        path="smoke",
        print_after_upload=False,
    ) == {"item": {"path": "smoke/kt_smoke.gcode"}}
    assert captured == {
        "url": "http://host:7125/server/files/upload",
        "headers": {"x-api-key": "secret"},
        "data": {"root": "gcodes", "path": "smoke", "print": "false"},
        "files": {"file": ("kt_smoke.gcode", b"; smoke\nM117 KT\n", "text/plain")},
        "timeout": 8.0,
    }


def test_client_blocks_gcode_upload_in_read_only_mode(monkeypatch) -> None:
    calls: list[str] = []

    def fake_post(*_args: object, **_kwargs: object) -> object:
        calls.append("post")
        raise AssertionError("network should not be called")

    monkeypatch.setattr("klippertouch.moonraker.client.requests.post", fake_post)

    client = MoonrakerClient(PrinterConfig(name="p", moonraker_host="host"))

    with pytest.raises(UnsafeCommandError):
        client.upload_gcode_file("kt_smoke.gcode", b"; smoke\n")

    assert calls == []


def test_client_raises_on_jsonrpc_error(monkeypatch) -> None:
    class FakeResponse:
        def raise_for_status(self) -> None:
            pass

        def json(self) -> dict[str, object]:
            return {"error": {"code": -32602, "message": "invalid params"}}

    def fake_post(*_args: object, **_kwargs: object) -> FakeResponse:
        return FakeResponse()

    monkeypatch.setattr("klippertouch.moonraker.client.requests.post", fake_post)

    client = MoonrakerClient(PrinterConfig(name="p", moonraker_host="host"))

    with pytest.raises(RuntimeError, match="invalid params"):
        client.post_jsonrpc("printer.objects.query", params={"objects": {}})


def test_client_gets_gcode_file_list(monkeypatch) -> None:
    captured: dict[str, object] = {}

    class FakeResponse:
        def raise_for_status(self) -> None:
            pass

        def json(self) -> dict[str, object]:
            return {"result": [{"path": "cube.gcode", "size": 1234}]}

    def fake_get(
        url: str,
        *,
        headers: dict[str, str],
        params: dict[str, str] | None,
        timeout: float,
    ) -> FakeResponse:
        captured["url"] = url
        captured["params"] = params
        return FakeResponse()

    monkeypatch.setattr("klippertouch.moonraker.client.requests.get", fake_get)

    client = MoonrakerClient(PrinterConfig(name="p", moonraker_host="host"))

    assert client.get_gcode_file_list() == [{"path": "cube.gcode", "size": 1234}]
    assert captured["url"] == "http://host:7125/server/files/list"
    assert captured["params"] == {"root": "gcodes"}


def test_client_gets_gcode_file_metadata(monkeypatch) -> None:
    captured: dict[str, object] = {}

    class FakeResponse:
        def raise_for_status(self) -> None:
            pass

        def json(self) -> dict[str, object]:
            return {
                "result": {
                    "filename": "cube.gcode",
                    "thumbnails": [
                        {
                            "width": 32,
                            "height": 32,
                            "size": 1234,
                            "relative_path": ".thumbs/cube-32x32.png",
                        }
                    ],
                }
            }

    def fake_get(
        url: str,
        *,
        headers: dict[str, str],
        params: dict[str, str] | None,
        timeout: float,
    ) -> FakeResponse:
        captured["url"] = url
        captured["params"] = params
        return FakeResponse()

    monkeypatch.setattr("klippertouch.moonraker.client.requests.get", fake_get)

    client = MoonrakerClient(PrinterConfig(name="p", moonraker_host="host"))

    assert client.get_gcode_file_metadata("cube.gcode") == {
        "filename": "cube.gcode",
        "thumbnails": [
            {
                "width": 32,
                "height": 32,
                "size": 1234,
                "relative_path": ".thumbs/cube-32x32.png",
            }
        ],
    }
    assert captured["url"] == "http://host:7125/server/files/metadata"
    assert captured["params"] == {"filename": "cube.gcode"}
