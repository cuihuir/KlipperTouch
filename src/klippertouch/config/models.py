from dataclasses import dataclass


@dataclass(frozen=True)
class PrinterConfig:
    name: str
    moonraker_host: str = "127.0.0.1"
    moonraker_port: int = 7125
    moonraker_path: str = ""
    moonraker_ssl: bool = False
    moonraker_api_key: str = ""


@dataclass(frozen=True)
class AppSettings:
    default_printer: str
    printers: dict[str, PrinterConfig]
    read_only: bool = True
    material_system_enabled: bool = False
