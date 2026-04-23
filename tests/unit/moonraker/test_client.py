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
