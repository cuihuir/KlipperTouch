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
    ) -> "PrinterStatus":
        return cls(
            hostname=str(printer_info.get("hostname", "unknown")),
            klippy_state=str(server_info.get("klippy_state", printer_info.get("state", "unknown"))),
            klipper_version=str(printer_info.get("software_version", "unknown")),
            moonraker_version=str(server_info.get("moonraker_version", "unknown")),
            objects=tuple(str(item) for item in objects.get("objects", ())),
        )


def _temperature_device_from_object(name: str) -> TemperatureDeviceStatus | None:
    if name == "extruder" or name.startswith("extruder"):
        return TemperatureDeviceStatus(
            name=name,
            display_name=_prettify_name(name),
            icon="extruder",
        )
    if name == "heater_bed":
        return TemperatureDeviceStatus(name=name, display_name="Heater Bed", icon="bed")
    if name.startswith(("heater_generic ", "temperature_sensor ", "temperature_fan ")):
        return TemperatureDeviceStatus(name=name, display_name=_prettify_name(name), icon="heat-up")
    return None


def _prettify_name(name: str) -> str:
    return name.replace("_", " ").replace("  ", " ").title()
