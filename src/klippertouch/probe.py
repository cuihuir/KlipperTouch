from dataclasses import asdict
from typing import Any, Protocol

from klippertouch.domain.printer import PrinterStatus

TEMPERATURE_OBJECT_PREFIXES = (
    "extruder",
    "heater_generic ",
    "temperature_sensor ",
    "temperature_fan ",
)
PRINT_STATUS_OBJECTS = ("print_stats", "display_status", "virtual_sdcard")
TOOLHEAD_STATUS_OBJECTS = ("toolhead", "gcode_move")


class ReadOnlyProbeClient(Protocol):
    def get_server_info(self) -> dict[str, Any]: ...
    def get_printer_info(self) -> dict[str, Any]: ...
    def get_objects_list(self) -> dict[str, Any]: ...
    def get_printer_objects_query(self, objects: tuple[str, ...] = ()) -> dict[str, Any]: ...


def build_status_from_client(client: ReadOnlyProbeClient) -> PrinterStatus:
    server_info = client.get_server_info()
    objects = _safe_probe(client.get_objects_list)
    object_names = tuple(str(item) for item in objects.get("objects", ()))
    return PrinterStatus.from_probe(
        server_info=server_info,
        printer_info=_safe_probe(client.get_printer_info),
        objects=objects,
        object_status=_safe_probe(
            lambda: client.get_printer_objects_query(_read_only_status_object_names(object_names))
        ),
    )


def status_to_dict(status: PrinterStatus) -> dict[str, Any]:
    return asdict(status)


def _safe_probe(probe: Any) -> dict[str, Any]:
    try:
        result = probe()
    except Exception:
        return {}
    return result if isinstance(result, dict) else {}


def _temperature_object_names(object_names: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(
        name
        for name in object_names
        if name == "extruder"
        or name.startswith(TEMPERATURE_OBJECT_PREFIXES)
        or name == "heater_bed"
    )


def _read_only_status_object_names(object_names: tuple[str, ...]) -> tuple[str, ...]:
    wanted = set(_temperature_object_names(object_names))
    wanted.update(name for name in PRINT_STATUS_OBJECTS if name in object_names)
    wanted.update(name for name in TOOLHEAD_STATUS_OBJECTS if name in object_names)
    return tuple(name for name in object_names if name in wanted)
