from dataclasses import dataclass
from typing import Any, TypedDict


class PrintStatusFields(TypedDict, total=False):
    print_state: str
    print_filename: str
    print_progress: float
    print_message: str
    print_duration: float
    total_duration: float
    filament_used: float
    current_layer: int
    total_layers: int


class ToolheadStatusFields(TypedDict, total=False):
    position_x: float
    position_y: float
    position_z: float
    position_e: float
    homed_axes: str
    requested_speed: float
    speed_factor: float
    extrude_factor: float
    z_offset: float
    max_accel: float
    max_velocity: float


class ExcludeObjectStatusFields(TypedDict, total=False):
    exclude_object_names: tuple[str, ...]
    excluded_object_names: tuple[str, ...]
    current_object: str


class WebhooksStatusFields(TypedDict, total=False):
    webhooks_state: str
    webhooks_message: str


@dataclass(frozen=True)
class TemperatureDeviceStatus:
    name: str
    display_name: str
    icon: str
    temperature: float | None = None
    target: float | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", str(self.name))
        object.__setattr__(self, "display_name", str(self.display_name))
        object.__setattr__(self, "icon", str(self.icon))


@dataclass(frozen=True)
class McuStatus:
    name: str
    version: str = "unknown"
    build_versions: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", str(self.name))
        object.__setattr__(self, "version", str(self.version or "unknown"))
        object.__setattr__(self, "build_versions", str(self.build_versions or ""))


@dataclass(frozen=True)
class ServiceVersionStatus:
    name: str
    version: str = "unknown"
    configured_type: str = "unknown"

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", str(self.name))
        object.__setattr__(self, "version", str(self.version or "unknown"))
        object.__setattr__(self, "configured_type", str(self.configured_type or "unknown"))


@dataclass(frozen=True)
class PrinterStatus:
    hostname: str = "unknown"
    klippy_state: str = "disconnected"
    klipper_version: str = "unknown"
    moonraker_version: str = "unknown"
    mcu_statuses: tuple[McuStatus, ...] = ()
    service_versions: tuple[ServiceVersionStatus, ...] = ()
    objects: tuple[str, ...] = ()
    temperature_devices: tuple[TemperatureDeviceStatus, ...] = ()
    print_state: str = "standby"
    print_filename: str = ""
    print_progress: float = 0.0
    print_message: str = ""
    print_duration: float = 0.0
    total_duration: float = 0.0
    filament_used: float = 0.0
    current_layer: int = 0
    total_layers: int = 0
    exclude_object_names: tuple[str, ...] = ()
    excluded_object_names: tuple[str, ...] = ()
    current_object: str = ""
    position_x: float = 0.0
    position_y: float = 0.0
    position_z: float = 0.0
    position_e: float = 0.0
    homed_axes: str = ""
    requested_speed: float = 0.0
    speed_factor: float = 100.0
    extrude_factor: float = 100.0
    z_offset: float = 0.0
    max_accel: float = 0.0
    max_velocity: float = 0.0
    webhooks_state: str = ""
    webhooks_message: str = ""

    def __post_init__(self) -> None:
        objects = tuple(str(item) for item in self.objects)
        object.__setattr__(self, "objects", objects)
        if self.temperature_devices:
            temperature_devices = tuple(self.temperature_devices)
        else:
            derived_devices: list[TemperatureDeviceStatus] = []
            for item in objects:
                device = _temperature_device_from_object(item)
                if device is not None:
                    derived_devices.append(device)
            temperature_devices = tuple(derived_devices)
        object.__setattr__(self, "temperature_devices", temperature_devices)
        object.__setattr__(self, "print_state", str(self.print_state or "standby"))
        object.__setattr__(self, "print_filename", str(self.print_filename or ""))
        object.__setattr__(self, "print_message", str(self.print_message or ""))
        object.__setattr__(self, "print_progress", _clamped_percent(self.print_progress))
        object.__setattr__(self, "print_duration", _optional_float(self.print_duration) or 0.0)
        object.__setattr__(self, "total_duration", _optional_float(self.total_duration) or 0.0)
        object.__setattr__(self, "filament_used", _optional_float(self.filament_used) or 0.0)
        object.__setattr__(self, "current_layer", _optional_int(self.current_layer))
        object.__setattr__(self, "total_layers", _optional_int(self.total_layers))
        object.__setattr__(
            self,
            "exclude_object_names",
            tuple(str(item) for item in self.exclude_object_names if str(item)),
        )
        object.__setattr__(
            self,
            "excluded_object_names",
            tuple(str(item) for item in self.excluded_object_names if str(item)),
        )
        object.__setattr__(self, "current_object", str(self.current_object or ""))
        object.__setattr__(self, "position_x", _optional_float(self.position_x) or 0.0)
        object.__setattr__(self, "position_y", _optional_float(self.position_y) or 0.0)
        object.__setattr__(self, "position_z", _optional_float(self.position_z) or 0.0)
        object.__setattr__(self, "position_e", _optional_float(self.position_e) or 0.0)
        object.__setattr__(self, "homed_axes", str(self.homed_axes or ""))
        object.__setattr__(self, "requested_speed", _optional_float(self.requested_speed) or 0.0)
        object.__setattr__(self, "speed_factor", _clamped_factor_percent(self.speed_factor))
        object.__setattr__(self, "extrude_factor", _clamped_factor_percent(self.extrude_factor))
        object.__setattr__(self, "z_offset", _optional_float(self.z_offset) or 0.0)
        object.__setattr__(self, "max_accel", _optional_float(self.max_accel) or 0.0)
        object.__setattr__(self, "max_velocity", _optional_float(self.max_velocity) or 0.0)
        object.__setattr__(self, "webhooks_state", str(self.webhooks_state or ""))
        object.__setattr__(self, "webhooks_message", str(self.webhooks_message or ""))

    @property
    def object_count(self) -> int:
        return len(self.objects)

    @property
    def mcu_count(self) -> int:
        return len(self.mcu_statuses)

    @property
    def service_version_count(self) -> int:
        return len(self.service_versions)

    @property
    def temperature_device_count(self) -> int:
        return len(self.temperature_devices)

    @property
    def exclude_object_count(self) -> int:
        return len(self.exclude_object_names)

    @property
    def excluded_object_count(self) -> int:
        return len(self.excluded_object_names)

    @property
    def primary_extruder_temperature(self) -> float:
        return _optional_float(self._primary_extruder_device().temperature) or 0.0

    @property
    def primary_extruder_target(self) -> float:
        return _optional_float(self._primary_extruder_device().target) or 0.0

    def _primary_extruder_device(self) -> TemperatureDeviceStatus:
        for device in self.temperature_devices:
            if device.name == "extruder":
                return device
        for device in self.temperature_devices:
            if device.name.startswith("extruder"):
                return device
        return TemperatureDeviceStatus(name="extruder", display_name="Extruder", icon="extruder")

    @classmethod
    def from_probe(
        cls,
        server_info: dict[str, Any],
        printer_info: dict[str, Any],
        objects: dict[str, Any],
        object_status: dict[str, Any] | None = None,
        mcu_status: dict[str, Any] | None = None,
        update_status: dict[str, Any] | None = None,
    ) -> "PrinterStatus":
        object_names = tuple(str(item) for item in objects.get("objects", ()))
        return cls(
            hostname=str(printer_info.get("hostname", "unknown")),
            klippy_state=str(server_info.get("klippy_state", printer_info.get("state", "unknown"))),
            klipper_version=str(printer_info.get("software_version", "unknown")),
            moonraker_version=str(server_info.get("moonraker_version", "unknown")),
            mcu_statuses=_mcu_statuses_from_probe(mcu_status or {}),
            service_versions=_service_versions_from_update_status(update_status or {}),
            objects=object_names,
            temperature_devices=_temperature_devices_from_status(object_names, object_status or {}),
            **_print_fields_from_status(object_status or {}),
            **_exclude_object_fields_from_status(object_status or {}),
            **_toolhead_fields_from_status(object_status or {}),
            **_webhooks_fields_from_status(object_status or {}),
        )

    def with_temperature_status_update(self, status_update: dict[str, Any]) -> "PrinterStatus":
        return self.with_status_update(status_update)

    def with_status_update(self, status_update: dict[str, Any]) -> "PrinterStatus":
        previous_values = {
            device.name: {"temperature": device.temperature, "target": device.target}
            for device in self.temperature_devices
        }
        for name, values in status_update.items():
            if not isinstance(values, dict):
                continue
            previous = previous_values.setdefault(str(name), {})
            if "temperature" in values:
                previous["temperature"] = values["temperature"]
            if "target" in values:
                previous["target"] = values["target"]

        print_fields: PrintStatusFields = {
            "print_state": self.print_state,
            "print_filename": self.print_filename,
            "print_progress": self.print_progress,
            "print_message": self.print_message,
            "print_duration": self.print_duration,
            "total_duration": self.total_duration,
            "filament_used": self.filament_used,
            "current_layer": self.current_layer,
            "total_layers": self.total_layers,
        }
        print_fields.update(_print_fields_from_status({"status": status_update}))
        if _should_preserve_terminal_progress(print_fields, self.print_progress):
            print_fields["print_progress"] = self.print_progress
        exclude_object_fields: ExcludeObjectStatusFields = {
            "exclude_object_names": self.exclude_object_names,
            "excluded_object_names": self.excluded_object_names,
            "current_object": self.current_object,
        }
        exclude_object_fields.update(_exclude_object_fields_from_status({"status": status_update}))
        toolhead_fields: ToolheadStatusFields = {
            "position_x": self.position_x,
            "position_y": self.position_y,
            "position_z": self.position_z,
            "position_e": self.position_e,
            "homed_axes": self.homed_axes,
            "requested_speed": self.requested_speed,
            "speed_factor": self.speed_factor,
            "extrude_factor": self.extrude_factor,
            "z_offset": self.z_offset,
            "max_accel": self.max_accel,
            "max_velocity": self.max_velocity,
        }
        toolhead_fields.update(_toolhead_fields_from_status({"status": status_update}))
        webhooks_fields: WebhooksStatusFields = {
            "webhooks_state": self.webhooks_state,
            "webhooks_message": self.webhooks_message,
        }
        webhooks_fields.update(_webhooks_fields_from_status({"status": status_update}))
        klippy_state = self.klippy_state
        if webhooks_fields.get("webhooks_state") == "ready":
            klippy_state = "ready"
            if webhooks_fields.get("webhooks_message") != "Printer is ready":
                webhooks_fields["webhooks_message"] = "Printer is ready"
        elif webhooks_fields.get("webhooks_state") in {
            "startup",
            "shutdown",
            "error",
            "disconnected",
        }:
            klippy_state = str(webhooks_fields["webhooks_state"])

        return PrinterStatus(
            hostname=self.hostname,
            klippy_state=klippy_state,
            klipper_version=self.klipper_version,
            moonraker_version=self.moonraker_version,
            mcu_statuses=self.mcu_statuses,
            service_versions=self.service_versions,
            objects=self.objects,
            temperature_devices=_temperature_devices_from_status(
                self.objects,
                {"status": previous_values},
            ),
            **print_fields,
            **exclude_object_fields,
            **toolhead_fields,
            **webhooks_fields,
        )


def _temperature_devices_from_status(
    object_names: tuple[str, ...],
    object_status: dict[str, Any],
) -> tuple[TemperatureDeviceStatus, ...]:
    status = object_status.get("status", {})
    if not isinstance(status, dict):
        status = {}

    devices: list[TemperatureDeviceStatus] = []
    for name in object_names:
        values = status.get(name, {})
        if not isinstance(values, dict):
            values = {}
        device = _temperature_device_from_object(name, values)
        if device is not None:
            devices.append(device)
    return tuple(sorted(devices, key=_temperature_device_sort_key))


def _mcu_statuses_from_probe(mcu_status: dict[str, Any]) -> tuple[McuStatus, ...]:
    status = mcu_status.get("status", {})
    if not isinstance(status, dict):
        return ()

    mcus: list[McuStatus] = []
    for name, values in sorted(status.items()):
        if not isinstance(values, dict):
            continue
        mcus.append(
            McuStatus(
                name=str(name),
                version=str(values.get("mcu_version", "unknown")),
                build_versions=str(values.get("mcu_build_versions", "")),
            )
        )
    return tuple(mcus)


def _service_versions_from_update_status(
    update_status: dict[str, Any],
) -> tuple[ServiceVersionStatus, ...]:
    version_info = update_status.get("version_info", {})
    if not isinstance(version_info, dict):
        return ()

    services: list[ServiceVersionStatus] = []
    for key, values in sorted(version_info.items()):
        if key == "system" or not isinstance(values, dict):
            continue
        services.append(
            ServiceVersionStatus(
                name=str(values.get("name", key)),
                version=str(
                    values.get("version")
                    or values.get("full_version_string")
                    or values.get("package_version")
                    or "unknown"
                ),
                configured_type=str(values.get("configured_type", "unknown")),
            )
        )
    return tuple(services)


def _temperature_device_sort_key(device: TemperatureDeviceStatus) -> tuple[int, str]:
    if device.name == "extruder":
        return (0, device.name)
    if device.name.startswith("extruder"):
        return (1, device.name)
    if device.name == "heater_bed":
        return (2, device.name)
    return (3, device.display_name)


def _temperature_device_from_object(
    name: str,
    values: dict[str, Any] | None = None,
) -> TemperatureDeviceStatus | None:
    values = values or {}
    temperature = _optional_float(values.get("temperature"))
    target = _optional_float(values.get("target"))
    if name == "extruder" or name.startswith("extruder"):
        return TemperatureDeviceStatus(
            name=name,
            display_name=_prettify_name(name),
            icon="extruder",
            temperature=temperature,
            target=target,
        )
    if name == "heater_bed":
        return TemperatureDeviceStatus(
            name=name,
            display_name="Heater Bed",
            icon="bed",
            temperature=temperature,
            target=target,
        )
    if name.startswith(
        ("heater_generic ", "temperature_host ", "temperature_sensor ", "temperature_fan ")
    ):
        return TemperatureDeviceStatus(
            name=name,
            display_name=_prettify_name(name),
            icon="heat-up",
            temperature=temperature,
            target=target,
        )
    return None


def _prettify_name(name: str) -> str:
    suffix = ""
    for prefix, type_suffix in (
        ("heater_generic ", ""),
        ("temperature_host ", " Host"),
        ("temperature_sensor ", ""),
        ("temperature_fan ", " Fan"),
    ):
        if name.startswith(prefix):
            name = name.removeprefix(prefix)
            suffix = type_suffix
            break
    return _title_words(name.replace("_", " ").replace("  ", " ")) + suffix


def _title_words(name: str) -> str:
    words = []
    for word in name.split(" "):
        words.append(word.title() if word.islower() else word)
    return " ".join(words)


def _print_fields_from_status(object_status: dict[str, Any]) -> PrintStatusFields:
    status = object_status.get("status", {})
    if not isinstance(status, dict):
        status = {}

    print_stats = status.get("print_stats", {})
    if not isinstance(print_stats, dict):
        print_stats = {}
    display_status = status.get("display_status", {})
    if not isinstance(display_status, dict):
        display_status = {}
    virtual_sdcard = status.get("virtual_sdcard", {})
    if not isinstance(virtual_sdcard, dict):
        virtual_sdcard = {}

    filename = print_stats.get("filename") or virtual_sdcard.get("file_path") or ""
    progress = display_status.get("progress")
    if progress is None:
        progress = virtual_sdcard.get("progress")

    fields = PrintStatusFields()
    if "state" in print_stats:
        fields["print_state"] = str(print_stats["state"])
    if filename:
        fields["print_filename"] = str(filename)
    if progress is not None:
        fields["print_progress"] = _progress_to_percent(progress)
    message = display_status.get("message")
    if message is not None:
        fields["print_message"] = str(message)
    if "print_duration" in print_stats:
        fields["print_duration"] = _optional_float(print_stats["print_duration"]) or 0.0
    if "total_duration" in print_stats:
        fields["total_duration"] = _optional_float(print_stats["total_duration"]) or 0.0
    if "filament_used" in print_stats:
        fields["filament_used"] = _optional_float(print_stats["filament_used"]) or 0.0
    info = print_stats.get("info", {})
    if isinstance(info, dict):
        if "current_layer" in info:
            fields["current_layer"] = _optional_int(info["current_layer"])
        if "total_layer" in info:
            fields["total_layers"] = _optional_int(info["total_layer"])
    return fields


def _exclude_object_fields_from_status(
    object_status: dict[str, Any],
) -> ExcludeObjectStatusFields:
    status = object_status.get("status", {})
    if not isinstance(status, dict):
        status = {}
    exclude_object = status.get("exclude_object", {})
    if not isinstance(exclude_object, dict):
        return ExcludeObjectStatusFields()

    fields = ExcludeObjectStatusFields()
    if "objects" in exclude_object:
        fields["exclude_object_names"] = _exclude_object_names(exclude_object["objects"])
    if "excluded_objects" in exclude_object:
        fields["excluded_object_names"] = _string_tuple(exclude_object["excluded_objects"])
    if "current_object" in exclude_object:
        fields["current_object"] = str(exclude_object.get("current_object") or "")
    return fields


def _webhooks_fields_from_status(object_status: dict[str, Any]) -> WebhooksStatusFields:
    status = object_status.get("status", {})
    if not isinstance(status, dict):
        status = {}
    webhooks = status.get("webhooks", {})
    if not isinstance(webhooks, dict):
        return WebhooksStatusFields()

    fields = WebhooksStatusFields()
    if "state" in webhooks:
        fields["webhooks_state"] = str(webhooks.get("state") or "")
    if "state_message" in webhooks:
        fields["webhooks_message"] = str(webhooks.get("state_message") or "")
    return fields


def _exclude_object_names(objects: Any) -> tuple[str, ...]:
    if not isinstance(objects, list | tuple):
        return ()
    names: list[str] = []
    for item in objects:
        if isinstance(item, dict):
            name = str(item.get("name", "")).strip()
        else:
            name = str(item).strip()
        if name:
            names.append(name)
    return tuple(names)


def _string_tuple(values: Any) -> tuple[str, ...]:
    if not isinstance(values, list | tuple):
        return ()
    return tuple(str(item) for item in values if str(item))


def _progress_to_percent(value: Any) -> float:
    number = _optional_float(value)
    if number is None:
        return 0.0
    if 0.0 <= number <= 1.0:
        return round(number * 100.0, 1)
    return _clamped_percent(number)


def _should_preserve_terminal_progress(
    print_fields: PrintStatusFields,
    previous_progress: float,
) -> bool:
    state = print_fields.get("print_state")
    progress = print_fields.get("print_progress")
    return (
        state in {"complete", "cancelled", "error"}
        and previous_progress > 0
        and (progress is None or progress <= 0)
    )


def _toolhead_fields_from_status(object_status: dict[str, Any]) -> ToolheadStatusFields:
    status = object_status.get("status", {})
    if not isinstance(status, dict):
        status = {}

    toolhead = status.get("toolhead", {})
    if not isinstance(toolhead, dict):
        toolhead = {}
    gcode_move = status.get("gcode_move", {})
    if not isinstance(gcode_move, dict):
        gcode_move = {}

    position = gcode_move.get("gcode_position")
    if not isinstance(position, list | tuple):
        position = toolhead.get("position")

    fields = ToolheadStatusFields()
    if isinstance(position, list | tuple) and len(position) >= 4:
        fields["position_x"] = _optional_float(position[0]) or 0.0
        fields["position_y"] = _optional_float(position[1]) or 0.0
        fields["position_z"] = _optional_float(position[2]) or 0.0
        fields["position_e"] = _optional_float(position[3]) or 0.0
    if "homed_axes" in toolhead:
        fields["homed_axes"] = str(toolhead["homed_axes"])
    if "speed" in gcode_move:
        fields["requested_speed"] = _feedrate_to_speed(gcode_move["speed"])
    if "speed_factor" in gcode_move:
        fields["speed_factor"] = _factor_to_percent(gcode_move["speed_factor"])
    if "extrude_factor" in gcode_move:
        fields["extrude_factor"] = _factor_to_percent(gcode_move["extrude_factor"])
    homing_origin = gcode_move.get("homing_origin")
    if isinstance(homing_origin, list | tuple) and len(homing_origin) >= 3:
        fields["z_offset"] = _optional_float(homing_origin[2]) or 0.0
    if "max_accel" in toolhead:
        fields["max_accel"] = _optional_float(toolhead["max_accel"]) or 0.0
    if "max_velocity" in toolhead:
        fields["max_velocity"] = _optional_float(toolhead["max_velocity"]) or 0.0
    return fields


def _feedrate_to_speed(value: Any) -> float:
    feedrate = _optional_float(value)
    if feedrate is None:
        return 0.0
    return max(0.0, feedrate / 60.0)


def _factor_to_percent(value: Any) -> float:
    number = _optional_float(value)
    if number is None:
        return 100.0
    return _clamped_factor_percent(round(number * 100.0, 1))


def _clamped_factor_percent(value: Any) -> float:
    number = _optional_float(value)
    if number is None:
        return 100.0
    return max(0.0, float(number))


def _clamped_percent(value: Any) -> float:
    number = _optional_float(value)
    if number is None:
        return 0.0
    return max(0.0, min(100.0, float(number)))


def _optional_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _optional_int(value: Any) -> int:
    number = _optional_float(value)
    if number is None:
        return 0
    return max(0, int(number))
