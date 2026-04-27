from configparser import ConfigParser
from pathlib import Path

from klippertouch.config.models import AppSettings, PrinterConfig


def load_config(path: Path) -> AppSettings:
    parser = ConfigParser(interpolation=None)
    if path.exists():
        parser.read(path, encoding="utf-8")

    printer_sections = [
        section for section in parser.sections() if section.startswith("printer ")
    ]
    if not printer_sections:
        default = PrinterConfig(name="Printer")
        return AppSettings(
            default_printer="Printer",
            printers={"Printer": default},
            read_only=parser.getboolean("main", "read_only", fallback=True),
        )

    printers: dict[str, PrinterConfig] = {}
    for section in printer_sections:
        name = section.removeprefix("printer ").strip()
        printers[name] = PrinterConfig(
            name=name,
            moonraker_host=parser.get(section, "moonraker_host", fallback="127.0.0.1"),
            moonraker_port=parser.getint(section, "moonraker_port", fallback=7125),
            moonraker_path=parser.get(section, "moonraker_path", fallback="").strip("/"),
            moonraker_ssl=parser.getboolean(section, "moonraker_ssl", fallback=False),
            moonraker_api_key=parser.get(
                section, "moonraker_api_key", fallback=""
            ).replace('"', ""),
        )

    default_printer = parser.get(
        "main", "default_printer", fallback=next(iter(printers))
    )
    if default_printer not in printers:
        default_printer = next(iter(printers))

    return AppSettings(
        default_printer=default_printer,
        printers=printers,
        read_only=parser.getboolean("main", "read_only", fallback=True),
    )
