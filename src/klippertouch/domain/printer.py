from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PrinterStatus:
    hostname: str = "unknown"
    klippy_state: str = "disconnected"
    klipper_version: str = "unknown"
    moonraker_version: str = "unknown"
    objects: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "objects", tuple(str(item) for item in self.objects))

    @property
    def object_count(self) -> int:
        return len(self.objects)

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
