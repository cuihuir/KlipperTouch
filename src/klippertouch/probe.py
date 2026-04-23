from typing import Any, Protocol

from klippertouch.domain.printer import PrinterStatus


class ReadOnlyProbeClient(Protocol):
    def get_server_info(self) -> dict[str, Any]: ...
    def get_printer_info(self) -> dict[str, Any]: ...
    def get_objects_list(self) -> dict[str, Any]: ...


def build_status_from_client(client: ReadOnlyProbeClient) -> PrinterStatus:
    return PrinterStatus.from_probe(
        server_info=client.get_server_info(),
        printer_info=client.get_printer_info(),
        objects=client.get_objects_list(),
    )
