from dataclasses import dataclass
from typing import Any


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

    @property
    def object_count(self) -> int:
        return len(self.objects)

    @property
    def temperature_device_count(self) -> int:
        return len(self.temperature_devices)

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
        )

    def with_temperature_status_update(self, status_update: dict[str, Any]) -> "PrinterStatus":
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


def _optional_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
