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
    position_u: float
    position_v: float
    position_w: float
    homed_axes: str
    requested_speed: float
    speed_factor: float
    extrude_factor: float
    z_offset: float
    bed_min_x: float
    bed_min_y: float
    bed_max_x: float
    bed_max_y: float
    max_accel: float
    max_velocity: float


class ExcludeObjectStatusFields(TypedDict, total=False):
    exclude_object_names: tuple[str, ...]
    exclude_objects: tuple["ExcludeObjectStatus", ...]
    excluded_object_names: tuple[str, ...]
    current_object: str


class WebhooksStatusFields(TypedDict, total=False):
    webhooks_state: str
    webhooks_message: str


FAN_PREFIXES = ("fan_generic ", "controller_fan ", "heater_fan ", "temperature_fan ")


@dataclass(frozen=True)
class TemperatureDeviceStatus:
    name: str
    display_name: str
    icon: str
    temperature: float | None = None
    target: float | None = None
    target_settable: bool | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", str(self.name))
        object.__setattr__(self, "display_name", str(self.display_name))
        object.__setattr__(self, "icon", str(self.icon))
        target_settable = (
            _temperature_device_supports_target(self.name)
            if self.target_settable is None
            else bool(self.target_settable)
        )
        object.__setattr__(self, "target_settable", target_settable)


@dataclass(frozen=True)
class FilamentSensorStatus:
    name: str
    display_name: str
    sensor_type: str
    enabled: bool | None = None
    filament_detected: bool | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", str(self.name))
        object.__setattr__(self, "display_name", str(self.display_name))
        object.__setattr__(self, "sensor_type", str(self.sensor_type))


@dataclass(frozen=True)
class FanStatus:
    name: str
    display_name: str
    speed: float = 0.0
    rpm: float | None = None
    speed_settable: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", str(self.name))
        object.__setattr__(self, "display_name", str(self.display_name))
        object.__setattr__(self, "speed", _fan_speed_to_percent(self.speed))
        object.__setattr__(self, "rpm", _optional_float(self.rpm))
        object.__setattr__(self, "speed_settable", bool(self.speed_settable))


@dataclass(frozen=True)
class ExcludeObjectStatus:
    name: str
    center: tuple[float, float] | None = None
    polygon: tuple[tuple[float, float], ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", str(self.name).strip())
        object.__setattr__(self, "center", _point_pair(self.center))
        object.__setattr__(
            self,
            "polygon",
            tuple(
                point
                for point in (_point_pair(item) for item in self.polygon)
                if point is not None
            ),
        )


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
    moonraker_warnings: tuple[str, ...] = ()
    klipper_warnings: tuple[str, ...] = ()
    mcu_statuses: tuple[McuStatus, ...] = ()
    service_versions: tuple[ServiceVersionStatus, ...] = ()
    objects: tuple[str, ...] = ()
    temperature_devices: tuple[TemperatureDeviceStatus, ...] = ()
    filament_sensors: tuple[FilamentSensorStatus, ...] = ()
    fan_devices: tuple[FanStatus, ...] = ()
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
    exclude_objects: tuple[ExcludeObjectStatus, ...] = ()
    excluded_object_names: tuple[str, ...] = ()
    current_object: str = ""
    position_x: float = 0.0
    position_y: float = 0.0
    position_z: float = 0.0
    position_e: float = 0.0
    position_u: float = 0.0
    position_v: float = 0.0
    position_w: float = 0.0
    homed_axes: str = ""
    requested_speed: float = 0.0
    speed_factor: float = 100.0
    extrude_factor: float = 100.0
    z_offset: float = 0.0
    bed_min_x: float = 0.0
    bed_min_y: float = 0.0
    bed_max_x: float = 0.0
    bed_max_y: float = 0.0
    max_accel: float = 0.0
    max_velocity: float = 0.0
    extruder_can_extrude: bool = False
    extruder_pressure_advance: float = 0.0
    extruder_smooth_time: float = 0.0
    webhooks_state: str = ""
    webhooks_message: str = ""
    five_axis_available: bool = False
    accelerator_level_available: bool = False
    z_tilt_available: bool = False

    def __post_init__(self) -> None:
        objects = tuple(str(item) for item in self.objects)
        object.__setattr__(self, "objects", objects)
        object_set = set(objects)
        object.__setattr__(
            self,
            "five_axis_available",
            bool(self.five_axis_available or "independent_3z" in object_set),
        )
        object.__setattr__(
            self,
            "accelerator_level_available",
            bool(self.accelerator_level_available or "accelerator_level" in object_set),
        )
        object.__setattr__(
            self,
            "z_tilt_available",
            bool(self.z_tilt_available or "z_tilt" in object_set),
        )
        object.__setattr__(
            self,
            "moonraker_warnings",
            tuple(str(item).strip() for item in self.moonraker_warnings if str(item).strip()),
        )
        object.__setattr__(
            self,
            "klipper_warnings",
            tuple(str(item).strip() for item in self.klipper_warnings if str(item).strip()),
        )
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
        if self.filament_sensors:
            filament_sensors = tuple(self.filament_sensors)
        else:
            derived_sensors: list[FilamentSensorStatus] = []
            for item in objects:
                sensor = _filament_sensor_from_object(item)
                if sensor is not None:
                    derived_sensors.append(sensor)
            filament_sensors = tuple(sorted(derived_sensors, key=_filament_sensor_sort_key))
        object.__setattr__(self, "filament_sensors", filament_sensors)
        if self.fan_devices:
            fan_devices = tuple(self.fan_devices)
        else:
            derived_fans: list[FanStatus] = []
            for item in objects:
                fan = _fan_from_object(item)
                if fan is not None:
                    derived_fans.append(fan)
            fan_devices = tuple(derived_fans)
        object.__setattr__(self, "fan_devices", fan_devices)
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
        exclude_objects = _exclude_object_definitions(self.exclude_objects)
        object.__setattr__(self, "exclude_objects", exclude_objects)
        if exclude_objects and not self.exclude_object_names:
            object.__setattr__(
                self,
                "exclude_object_names",
                tuple(item.name for item in exclude_objects),
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
        object.__setattr__(self, "position_u", _optional_float(self.position_u) or 0.0)
        object.__setattr__(self, "position_v", _optional_float(self.position_v) or 0.0)
        object.__setattr__(self, "position_w", _optional_float(self.position_w) or 0.0)
        object.__setattr__(self, "homed_axes", str(self.homed_axes or ""))
        object.__setattr__(self, "requested_speed", _optional_float(self.requested_speed) or 0.0)
        object.__setattr__(self, "speed_factor", _clamped_factor_percent(self.speed_factor))
        object.__setattr__(self, "extrude_factor", _clamped_factor_percent(self.extrude_factor))
        object.__setattr__(self, "z_offset", _optional_float(self.z_offset) or 0.0)
        object.__setattr__(self, "bed_min_x", _optional_float(self.bed_min_x) or 0.0)
        object.__setattr__(self, "bed_min_y", _optional_float(self.bed_min_y) or 0.0)
        object.__setattr__(self, "bed_max_x", _optional_float(self.bed_max_x) or 0.0)
        object.__setattr__(self, "bed_max_y", _optional_float(self.bed_max_y) or 0.0)
        object.__setattr__(self, "max_accel", _optional_float(self.max_accel) or 0.0)
        object.__setattr__(self, "max_velocity", _optional_float(self.max_velocity) or 0.0)
        object.__setattr__(self, "extruder_can_extrude", bool(self.extruder_can_extrude))
        object.__setattr__(
            self,
            "extruder_pressure_advance",
            _optional_float(self.extruder_pressure_advance) or 0.0,
        )
        object.__setattr__(
            self,
            "extruder_smooth_time",
            _optional_float(self.extruder_smooth_time) or 0.0,
        )
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
    def filament_sensor_count(self) -> int:
        return len(self.filament_sensors)

    @property
    def fan_device_count(self) -> int:
        return len(self.fan_devices)

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
        webhooks_fields = _webhooks_fields_from_status(object_status or {})
        klippy_state = str(server_info.get("klippy_state", printer_info.get("state", "unknown")))
        if webhooks_fields.get("webhooks_state") == "ready":
            klippy_state = "ready"
            if not webhooks_fields.get("webhooks_message"):
                webhooks_fields["webhooks_message"] = "Printer is ready"
        elif webhooks_fields.get("webhooks_state") in {
            "startup",
            "shutdown",
            "error",
            "disconnected",
        }:
            klippy_state = str(webhooks_fields["webhooks_state"])
        capabilities = _capabilities_from_probe(object_names, object_status or {})
        return cls(
            hostname=str(printer_info.get("hostname", "unknown")),
            klippy_state=klippy_state,
            klipper_version=str(printer_info.get("software_version", "unknown")),
            moonraker_version=str(server_info.get("moonraker_version", "unknown")),
            moonraker_warnings=_moonraker_warnings_from_server_info(server_info),
            klipper_warnings=_klipper_warnings_from_status(object_status or {}),
            mcu_statuses=_mcu_statuses_from_probe(mcu_status or {}),
            service_versions=_service_versions_from_update_status(update_status or {}),
            objects=object_names,
            temperature_devices=_temperature_devices_from_status(object_names, object_status or {}),
            filament_sensors=_filament_sensors_from_status(object_names, object_status or {}),
            fan_devices=_fan_devices_from_status(object_names, object_status or {}),
            **_print_fields_from_status(object_status or {}),
            **_exclude_object_fields_from_status(object_status or {}),
            **_toolhead_fields_from_status(object_status or {}),
            **_extruder_fields_from_status(object_status or {}),
            **webhooks_fields,
            **capabilities,
        )

    def with_temperature_status_update(self, status_update: dict[str, Any]) -> "PrinterStatus":
        return self.with_status_update(status_update)

    def with_status_update(self, status_update: dict[str, Any]) -> "PrinterStatus":
        previous_values: dict[str, dict[str, Any]] = {
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
        previous_sensor_values: dict[str, dict[str, Any]] = {
            sensor.name: {
                "enabled": sensor.enabled,
                "filament_detected": sensor.filament_detected,
            }
            for sensor in self.filament_sensors
        }
        for name, values in status_update.items():
            if not isinstance(values, dict):
                continue
            previous = previous_sensor_values.setdefault(str(name), {})
            if "enabled" in values:
                previous["enabled"] = values["enabled"]
            if "filament_detected" in values:
                previous["filament_detected"] = values["filament_detected"]
        previous_fan_values: dict[str, dict[str, Any]] = {
            fan.name: {"speed": fan.speed, "rpm": fan.rpm} for fan in self.fan_devices
        }
        for name, values in status_update.items():
            if not isinstance(values, dict):
                continue
            previous = previous_fan_values.setdefault(str(name), {})
            if "speed" in values:
                previous["speed"] = values["speed"]
            if "rpm" in values:
                previous["rpm"] = values["rpm"]

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
            "exclude_objects": self.exclude_objects,
            "excluded_object_names": self.excluded_object_names,
            "current_object": self.current_object,
        }
        exclude_object_fields.update(_exclude_object_fields_from_status({"status": status_update}))
        toolhead_fields: ToolheadStatusFields = {
            "position_x": self.position_x,
            "position_y": self.position_y,
            "position_z": self.position_z,
            "position_e": self.position_e,
            "position_u": self.position_u,
            "position_v": self.position_v,
            "position_w": self.position_w,
            "homed_axes": self.homed_axes,
            "requested_speed": self.requested_speed,
            "speed_factor": self.speed_factor,
            "extrude_factor": self.extrude_factor,
            "z_offset": self.z_offset,
            "bed_min_x": self.bed_min_x,
            "bed_min_y": self.bed_min_y,
            "bed_max_x": self.bed_max_x,
            "bed_max_y": self.bed_max_y,
            "max_accel": self.max_accel,
            "max_velocity": self.max_velocity,
        }
        toolhead_fields.update(_toolhead_fields_from_status({"status": status_update}))
        extruder_fields: dict[str, Any] = {
            "extruder_can_extrude": self.extruder_can_extrude,
            "extruder_pressure_advance": self.extruder_pressure_advance,
            "extruder_smooth_time": self.extruder_smooth_time,
        }
        extruder_fields.update(_extruder_fields_from_status({"status": status_update}))
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
            moonraker_warnings=self.moonraker_warnings,
            klipper_warnings=self.klipper_warnings,
            mcu_statuses=self.mcu_statuses,
            service_versions=self.service_versions,
            objects=self.objects,
            temperature_devices=_temperature_devices_from_status(
                self.objects,
                {"status": previous_values},
            ),
            filament_sensors=_filament_sensors_from_status(
                self.objects,
                {"status": previous_sensor_values},
            ),
            fan_devices=_fan_devices_from_status(
                self.objects,
                {"status": previous_fan_values},
            ),
            **print_fields,
            **exclude_object_fields,
            **toolhead_fields,
            **extruder_fields,
            **webhooks_fields,
            five_axis_available=self.five_axis_available,
            accelerator_level_available=self.accelerator_level_available,
            z_tilt_available=self.z_tilt_available,
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


def _capabilities_from_probe(
    object_names: tuple[str, ...],
    object_status: dict[str, Any],
) -> dict[str, bool]:
    object_set = set(object_names)
    config_sections = _configfile_sections_from_status(object_status)
    pre_level = config_sections.get("pre_level", {})
    if not isinstance(pre_level, dict):
        pre_level = {}
    return {
        "five_axis_available": "independent_3z" in object_set
        or "independent_3z" in config_sections,
        "accelerator_level_available": "accelerator_level" in object_set
        or "accelerator_level" in config_sections
        or _truthy_config_value(pre_level.get("accelerator_level")),
        "z_tilt_available": "z_tilt" in object_set or "z_tilt" in config_sections,
    }


def _configfile_sections_from_status(object_status: dict[str, Any]) -> dict[str, Any]:
    status = object_status.get("status", {})
    if not isinstance(status, dict):
        return {}
    configfile = status.get("configfile", {})
    if not isinstance(configfile, dict):
        return {}
    sections: dict[str, Any] = {}
    for key in ("config", "settings"):
        values = configfile.get(key, {})
        if isinstance(values, dict):
            sections.update({str(name): value for name, value in values.items()})
    return sections


def _truthy_config_value(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)


def _filament_sensors_from_status(
    object_names: tuple[str, ...],
    object_status: dict[str, Any],
) -> tuple[FilamentSensorStatus, ...]:
    status = object_status.get("status", {})
    if not isinstance(status, dict):
        status = {}

    sensors: list[FilamentSensorStatus] = []
    for name in object_names:
        values = status.get(name, {})
        if not isinstance(values, dict):
            values = {}
        sensor = _filament_sensor_from_object(name, values)
        if sensor is not None:
            sensors.append(sensor)
    return tuple(sorted(sensors, key=_filament_sensor_sort_key))


def _fan_devices_from_status(
    object_names: tuple[str, ...],
    object_status: dict[str, Any],
) -> tuple[FanStatus, ...]:
    status = object_status.get("status", {})
    if not isinstance(status, dict):
        status = {}

    fans: list[FanStatus] = []
    for name in _fan_names_from_status(object_names, object_status):
        values = status.get(name, {})
        if not isinstance(values, dict):
            values = {}
        fan = _fan_from_object(name, values)
        if fan is not None:
            fans.append(fan)
    return tuple(fans)


def _fan_names_from_status(
    object_names: tuple[str, ...],
    object_status: dict[str, Any],
) -> tuple[str, ...]:
    names: list[str] = []
    seen: set[str] = set()

    def add_name(name: str) -> None:
        if not _is_fan_object_name(name):
            return
        key = _normalized_fan_name_key(name)
        if key in seen:
            return
        seen.add(key)
        names.append(name)

    for name in object_names:
        add_name(name)
    for name in _configfile_sections_from_status(object_status):
        add_name(name)
    return tuple(names)


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


def _temperature_device_supports_target(name: str) -> bool:
    return (
        name == "extruder"
        or name.startswith("extruder")
        or name == "heater_bed"
        or name.startswith("heater_generic ")
        or name.startswith("temperature_fan ")
    )


def _filament_sensor_sort_key(sensor: FilamentSensorStatus) -> tuple[str, str]:
    return (sensor.display_name, sensor.name)


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


def _filament_sensor_from_object(
    name: str,
    values: dict[str, Any] | None = None,
) -> FilamentSensorStatus | None:
    values = values or {}
    if name.startswith("filament_switch_sensor "):
        return FilamentSensorStatus(
            name=name,
            display_name=_prettify_name(name),
            sensor_type="switch",
            enabled=_optional_bool(values.get("enabled")),
            filament_detected=_optional_bool(values.get("filament_detected")),
        )
    if name.startswith("filament_motion_sensor "):
        return FilamentSensorStatus(
            name=name,
            display_name=_prettify_name(name),
            sensor_type="motion",
            enabled=_optional_bool(values.get("enabled")),
            filament_detected=_optional_bool(values.get("filament_detected")),
        )
    return None


def _fan_from_object(
    name: str,
    values: dict[str, Any] | None = None,
) -> FanStatus | None:
    values = values or {}
    speed = _fan_speed_to_percent(values.get("speed"))
    rpm = _optional_float(values.get("rpm"))
    if name == "fan":
        return FanStatus(
            name=name,
            display_name="Part Fan",
            speed=speed,
            rpm=rpm,
            speed_settable=True,
        )
    if name.startswith("fan_generic "):
        return FanStatus(
            name=name,
            display_name=_prettify_name(name),
            speed=speed,
            rpm=rpm,
            speed_settable=True,
        )
    if name.startswith(("controller_fan ", "heater_fan ")):
        return FanStatus(
            name=name,
            display_name=_prettify_name(name),
            speed=speed,
            rpm=rpm,
            speed_settable=False,
        )
    if name.startswith("temperature_fan "):
        return FanStatus(
            name=name,
            display_name=_prettify_name(name),
            speed=speed,
            rpm=rpm,
            speed_settable=False,
        )
    return None


def _is_fan_object_name(name: str) -> bool:
    return name == "fan" or name.startswith(FAN_PREFIXES)


def _normalized_fan_name_key(name: str) -> str:
    return name.casefold()


def _extruder_fields_from_status(object_status: dict[str, Any]) -> dict[str, Any]:
    status = object_status.get("status", {})
    if not isinstance(status, dict):
        return {}
    extruder = status.get("extruder", {})
    if not isinstance(extruder, dict):
        return {}

    fields: dict[str, Any] = {}
    if "can_extrude" in extruder:
        fields["extruder_can_extrude"] = _optional_bool(extruder["can_extrude"]) is True
    if "pressure_advance" in extruder:
        fields["extruder_pressure_advance"] = _optional_float(extruder["pressure_advance"]) or 0.0
    if "smooth_time" in extruder:
        fields["extruder_smooth_time"] = _optional_float(extruder["smooth_time"]) or 0.0
    return fields


def _prettify_name(name: str) -> str:
    suffix = ""
    for prefix, type_suffix in (
        ("heater_generic ", ""),
        ("temperature_host ", " Host"),
        ("temperature_sensor ", ""),
        ("temperature_fan ", " Fan"),
        ("filament_switch_sensor ", ""),
        ("filament_motion_sensor ", ""),
        ("fan_generic ", ""),
        ("controller_fan ", " Fan"),
        ("heater_fan ", " Fan"),
    ):
        if name.startswith(prefix):
            name = name.removeprefix(prefix)
            suffix = type_suffix
            break
    display_name = _title_words(name.replace("_", " ").replace("  ", " "))
    if suffix and display_name.endswith(suffix):
        return display_name
    return display_name + suffix


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
        fields["exclude_objects"] = _exclude_object_definitions(exclude_object["objects"])
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


def _exclude_object_definitions(objects: Any) -> tuple[ExcludeObjectStatus, ...]:
    if not isinstance(objects, list | tuple):
        return ()
    definitions: list[ExcludeObjectStatus] = []
    for item in objects:
        if isinstance(item, ExcludeObjectStatus):
            if item.name:
                definitions.append(item)
            continue
        if isinstance(item, dict):
            name = str(item.get("name", "")).strip()
            if not name:
                continue
            definitions.append(
                ExcludeObjectStatus(
                    name=name,
                    center=_point_pair(item.get("center")),
                    polygon=tuple(
                        point
                        for point in (_point_pair(point) for point in item.get("polygon", ()))
                        if point is not None
                    ),
                )
            )
            continue
        name = str(item).strip()
        if name:
            definitions.append(ExcludeObjectStatus(name=name))
    return tuple(definitions)


def _exclude_object_names(objects: Any) -> tuple[str, ...]:
    definitions = _exclude_object_definitions(objects)
    if definitions:
        return tuple(item.name for item in definitions)
    if not isinstance(objects, list | tuple):
        return ()
    names: list[str] = []
    for item in objects:
        name = str(item).strip()
        if name:
            names.append(name)
    return tuple(names)


def _point_pair(value: Any) -> tuple[float, float] | None:
    if not isinstance(value, list | tuple) or len(value) < 2:
        return None
    x = _optional_float(value[0])
    y = _optional_float(value[1])
    if x is None or y is None:
        return None
    return (x, y)


def _string_tuple(values: Any) -> tuple[str, ...]:
    if not isinstance(values, list | tuple):
        return ()
    return tuple(str(item) for item in values if str(item))


def _moonraker_warnings_from_server_info(server_info: dict[str, Any]) -> tuple[str, ...]:
    return _warning_messages(server_info.get("warnings", ()))


def _klipper_warnings_from_status(object_status: dict[str, Any]) -> tuple[str, ...]:
    status = object_status.get("status", {})
    if not isinstance(status, dict):
        return ()
    configfile = status.get("configfile", {})
    if not isinstance(configfile, dict):
        return ()
    return _warning_messages(configfile.get("warnings", ()))


def _warning_messages(warnings: Any) -> tuple[str, ...]:
    if not isinstance(warnings, list | tuple):
        return ()
    parsed: list[str] = []
    for warning in warnings:
        if isinstance(warning, dict):
            message = str(warning.get("message") or warning.get("warning") or "").strip()
        else:
            message = str(warning).strip()
        if message:
            parsed.append(message)
    return tuple(parsed)


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
        if len(position) >= 7:
            fields["position_u"] = _optional_float(position[4]) or 0.0
            fields["position_v"] = _optional_float(position[5]) or 0.0
            fields["position_w"] = _optional_float(position[6]) or 0.0
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
    axis_minimum = toolhead.get("axis_minimum")
    if isinstance(axis_minimum, list | tuple) and len(axis_minimum) >= 2:
        fields["bed_min_x"] = _optional_float(axis_minimum[0]) or 0.0
        fields["bed_min_y"] = _optional_float(axis_minimum[1]) or 0.0
    axis_maximum = toolhead.get("axis_maximum")
    if isinstance(axis_maximum, list | tuple) and len(axis_maximum) >= 2:
        fields["bed_max_x"] = _optional_float(axis_maximum[0]) or 0.0
        fields["bed_max_y"] = _optional_float(axis_maximum[1]) or 0.0
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


def _fan_speed_to_percent(value: Any) -> float:
    number = _optional_float(value)
    if number is None:
        return 0.0
    if 0.0 <= number <= 1.0:
        return round(number * 100.0, 1)
    return round(_clamped_percent(number), 1)


def _optional_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _optional_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if value is None:
        return None
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes", "on"}:
            return True
        if normalized in {"false", "0", "no", "off"}:
            return False
        return None
    if isinstance(value, int | float):
        return bool(value)
    return None


def _optional_int(value: Any) -> int:
    number = _optional_float(value)
    if number is None:
        return 0
    return max(0, int(number))
