from klippertouch.config.models import PrinterConfig
from klippertouch.moonraker.client import MoonrakerClient


def test_client_builds_plain_http_endpoint() -> None:
    client = MoonrakerClient(PrinterConfig(name="p", moonraker_host="host", moonraker_port=7125))
    assert client.endpoint == "http://host:7125"


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
