import pytest

from klippertouch.config.models import PrinterConfig
from klippertouch.moonraker.client import MoonrakerClient
from klippertouch.moonraker.safety import UnsafeCommandError


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
        "extruder": "temperature,target",
        "heater_bed": "temperature,target",
    }


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
