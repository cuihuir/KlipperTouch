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
class PrinterStatus:
    hostname: str = "unknown"
    klippy_state: str = "disconnected"
    klipper_version: str = "unknown"
    moonraker_version: str = "unknown"
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
    position_x: float = 0.0
    position_y: float = 0.0
    position_z: float = 0.0
    position_e: float = 0.0
    homed_axes: str = ""

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
        object.__setattr__(self, "position_x", _optional_float(self.position_x) or 0.0)
        object.__setattr__(self, "position_y", _optional_float(self.position_y) or 0.0)
        object.__setattr__(self, "position_z", _optional_float(self.position_z) or 0.0)
        object.__setattr__(self, "position_e", _optional_float(self.position_e) or 0.0)
        object.__setattr__(self, "homed_axes", str(self.homed_axes or ""))

    @property
    def object_count(self) -> int:
        return len(self.objects)

    @property
    def temperature_device_count(self) -> int:
        return len(self.temperature_devices)

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
    ) -> "PrinterStatus":
        object_names = tuple(str(item) for item in objects.get("objects", ()))
        return cls(
            hostname=str(printer_info.get("hostname", "unknown")),
            klippy_state=str(server_info.get("klippy_state", printer_info.get("state", "unknown"))),
            klipper_version=str(printer_info.get("software_version", "unknown")),
            moonraker_version=str(server_info.get("moonraker_version", "unknown")),
            objects=object_names,
            temperature_devices=_temperature_devices_from_status(object_names, object_status or {}),
            **_print_fields_from_status(object_status or {}),
            **_toolhead_fields_from_status(object_status or {}),
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
        toolhead_fields: ToolheadStatusFields = {
            "position_x": self.position_x,
            "position_y": self.position_y,
            "position_z": self.position_z,
            "position_e": self.position_e,
            "homed_axes": self.homed_axes,
        }
        toolhead_fields.update(_toolhead_fields_from_status({"status": status_update}))

        return PrinterStatus(
            hostname=self.hostname,
            klippy_state=self.klippy_state,
            klipper_version=self.klipper_version,
            moonraker_version=self.moonraker_version,
            objects=self.objects,
            temperature_devices=_temperature_devices_from_status(
                self.objects,
                {"status": previous_values},
            ),
            **print_fields,
            **toolhead_fields,
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
    return tuple(devices)


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
    if name.startswith(("heater_generic ", "temperature_sensor ", "temperature_fan ")):
        return TemperatureDeviceStatus(
            name=name,
            display_name=_prettify_name(name),
            icon="heat-up",
            temperature=temperature,
            target=target,
        )
    return None


def _prettify_name(name: str) -> str:
    return name.replace("_", " ").replace("  ", " ").title()


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
    if "message" in display_status:
        fields["print_message"] = str(display_status["message"])
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


def _progress_to_percent(value: Any) -> float:
    number = _optional_float(value)
    if number is None:
        return 0.0
    if 0.0 <= number <= 1.0:
        return round(number * 100.0, 1)
    return _clamped_percent(number)


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
    return fields


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
