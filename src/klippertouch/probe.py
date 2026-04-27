from dataclasses import asdict
from typing import Any, Protocol

from klippertouch.domain.printer import PrinterStatus

TEMPERATURE_OBJECT_PREFIXES = (
    "extruder",
    "heater_generic ",
    "temperature_host ",
    "temperature_sensor ",
    "temperature_fan ",
)
PRINT_STATUS_OBJECTS = ("print_stats", "display_status", "virtual_sdcard")
TOOLHEAD_STATUS_OBJECTS = ("toolhead", "gcode_move")
EXCLUDE_OBJECT_OBJECTS = ("exclude_object",)


class ReadOnlyProbeClient(Protocol):
    def get_server_info(self) -> dict[str, Any]: ...
    def get_printer_info(self) -> dict[str, Any]: ...
    def get_objects_list(self) -> dict[str, Any]: ...
    def get_printer_objects_query(self, objects: tuple[str, ...] = ()) -> dict[str, Any]: ...
    def get_printer_objects_query_fields(
        self,
        fields_by_object: dict[str, str],
    ) -> dict[str, Any]: ...
    def get_printer_objects_query_jsonrpc(
        self,
        objects: dict[str, list[str]],
    ) -> dict[str, Any]: ...
    def get_machine_update_status(self) -> dict[str, Any]: ...


def build_status_from_client(client: ReadOnlyProbeClient) -> PrinterStatus:
    server_info = client.get_server_info()
    objects = _safe_probe(client.get_objects_list)
    object_names = tuple(str(item) for item in objects.get("objects", ()))
    mcu_object_names = tuple(
        name for name in object_names if name == "mcu" or name.startswith("mcu ")
    )
    object_status = _safe_probe(
        lambda: client.get_printer_objects_query(_read_only_status_object_names(object_names))
    )
    object_status = _with_non_ascii_temperature_status(client, object_names, object_status)
    return PrinterStatus.from_probe(
        server_info=server_info,
        printer_info=_safe_probe(client.get_printer_info),
        objects=objects,
        object_status=object_status,
        mcu_status=_safe_probe(
            lambda: client.get_printer_objects_query_fields(
                {name: "mcu_version,mcu_build_versions" for name in mcu_object_names}
            )
        ),
        update_status=_safe_probe(client.get_machine_update_status),
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
    wanted.update(name for name in EXCLUDE_OBJECT_OBJECTS if name in object_names)
    return tuple(name for name in object_names if name in wanted)


def _with_non_ascii_temperature_status(
    client: ReadOnlyProbeClient,
    object_names: tuple[str, ...],
    object_status: dict[str, Any],
) -> dict[str, Any]:
    non_ascii_temperature_names = tuple(
        name for name in _temperature_object_names(object_names) if not name.isascii()
    )
    if not non_ascii_temperature_names:
        return object_status

    fallback = _safe_probe(
        lambda: client.get_printer_objects_query_jsonrpc(
            {name: ["temperature", "target"] for name in non_ascii_temperature_names}
        )
    )
    fallback_status = fallback.get("status", {})
    if not isinstance(fallback_status, dict):
        return object_status

    merged = dict(object_status)
    merged_status = dict(merged.get("status", {})) if isinstance(merged.get("status"), dict) else {}
    for name in non_ascii_temperature_names:
        values = fallback_status.get(name)
        if isinstance(values, dict):
            merged_status[name] = values
    merged["status"] = merged_status
    return merged
