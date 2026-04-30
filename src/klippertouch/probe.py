from concurrent.futures import Future, ThreadPoolExecutor
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
WEBHOOKS_OBJECTS = ("webhooks",)
CONFIG_STATUS_OBJECTS = ("configfile",)
FILAMENT_SENSOR_PREFIXES = ("filament_switch_sensor ", "filament_motion_sensor ")
FAN_PREFIXES = ("fan_generic ", "controller_fan ", "heater_fan ", "temperature_fan ")


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


def build_basic_status_from_client(client: ReadOnlyProbeClient) -> PrinterStatus:
    with ThreadPoolExecutor(max_workers=2) as executor:
        server_info_future = executor.submit(client.get_server_info)
        printer_info_future = executor.submit(client.get_printer_info)
        server_info = server_info_future.result()
        printer_info = _safe_future(printer_info_future)
    return PrinterStatus.from_probe(
        server_info=server_info,
        printer_info=printer_info,
        objects={},
        object_status={},
        mcu_status={},
        update_status={},
    )


def build_status_from_client(client: ReadOnlyProbeClient) -> PrinterStatus:
    with ThreadPoolExecutor(max_workers=4) as executor:
        server_info_future = executor.submit(client.get_server_info)
        objects_future = executor.submit(client.get_objects_list)
        printer_info_future = executor.submit(client.get_printer_info)
        update_status_future = executor.submit(client.get_machine_update_status)

        server_info = server_info_future.result()
        objects = _safe_future(objects_future)
        printer_info = _safe_future(printer_info_future)
        update_status = _safe_future(update_status_future)

    object_names = tuple(str(item) for item in objects.get("objects", ()))
    mcu_object_names = tuple(
        name for name in object_names if name == "mcu" or name.startswith("mcu ")
    )
    with ThreadPoolExecutor(max_workers=2) as executor:
        object_status_future = executor.submit(
            client.get_printer_objects_query,
            _read_only_status_object_names(object_names),
        )
        mcu_status_future = executor.submit(
            client.get_printer_objects_query_fields,
            {name: "mcu_version,mcu_build_versions" for name in mcu_object_names},
        )
        object_status = _safe_future(object_status_future)
        mcu_status = _safe_future(mcu_status_future)
        object_status = _with_non_ascii_status(client, object_names, object_status)

    return PrinterStatus.from_probe(
        server_info=server_info,
        printer_info=printer_info,
        objects=objects,
        object_status=object_status,
        mcu_status=mcu_status,
        update_status=update_status,
    )


def status_to_dict(status: PrinterStatus) -> dict[str, Any]:
    return asdict(status)


def _safe_probe(probe: Any) -> dict[str, Any]:
    try:
        result = probe()
    except Exception:
        return {}
    return result if isinstance(result, dict) else {}


def _safe_future(future: Future[dict[str, Any]]) -> dict[str, Any]:
    try:
        result = future.result()
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


def _fan_object_names(object_names: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(
        name
        for name in object_names
        if name == "fan" or name.startswith(FAN_PREFIXES)
    )


def _read_only_status_object_names(object_names: tuple[str, ...]) -> tuple[str, ...]:
    wanted = set(_temperature_object_names(object_names))
    wanted.update(_fan_object_names(object_names))
    wanted.update(name for name in PRINT_STATUS_OBJECTS if name in object_names)
    wanted.update(name for name in TOOLHEAD_STATUS_OBJECTS if name in object_names)
    wanted.update(name for name in EXCLUDE_OBJECT_OBJECTS if name in object_names)
    wanted.update(name for name in WEBHOOKS_OBJECTS if name in object_names)
    wanted.update(name for name in CONFIG_STATUS_OBJECTS if name in object_names)
    wanted.update(name for name in object_names if name.startswith(FILAMENT_SENSOR_PREFIXES))
    return tuple(name for name in object_names if name in wanted)


def _with_non_ascii_status(
    client: ReadOnlyProbeClient,
    object_names: tuple[str, ...],
    object_status: dict[str, Any],
) -> dict[str, Any]:
    fields_by_object = {
        name: fields
        for name in object_names
        if not name.isascii()
        for fields in (_non_ascii_status_fields(name),)
        if fields
    }
    if not fields_by_object:
        return object_status

    fallback = _safe_probe(lambda: client.get_printer_objects_query_jsonrpc(fields_by_object))
    fallback_status = fallback.get("status", {})
    if not isinstance(fallback_status, dict):
        return object_status

    merged = dict(object_status)
    merged_status = dict(merged.get("status", {})) if isinstance(merged.get("status"), dict) else {}
    for name in fields_by_object:
        values = fallback_status.get(name)
        if isinstance(values, dict):
            previous = (
                dict(merged_status.get(name, {}))
                if isinstance(merged_status.get(name), dict)
                else {}
            )
            previous.update(values)
            merged_status[name] = previous
    merged["status"] = merged_status
    return merged


def _non_ascii_status_fields(name: str) -> list[str]:
    fields: list[str] = []
    if name in _temperature_object_names((name,)):
        fields.extend(["temperature", "target"])
    if name in _fan_object_names((name,)):
        fields.append("speed")
    return fields
