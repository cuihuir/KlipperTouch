from pathlib import Path

from klippertouch.config.loader import load_config


def test_load_config_reads_default_printer(tmp_path: Path) -> None:
    config = tmp_path / "KlipperTouch.conf"
    config.write_text(
        "[main]\n"
        "default_printer = TestPrinter\n"
        "\n"
        "[printer TestPrinter]\n"
        "moonraker_host = 192.168.123.117\n"
        "moonraker_port = 7125\n",
        encoding="utf-8",
    )

    settings = load_config(config)

    assert settings.default_printer == "TestPrinter"
    assert settings.printers["TestPrinter"].moonraker_host == "192.168.123.117"
    assert settings.printers["TestPrinter"].moonraker_port == 7125
    assert settings.read_only is True


def test_load_config_parses_read_only_control_switch(tmp_path: Path) -> None:
    config = tmp_path / "KlipperTouch.conf"
    config.write_text(
        "[main]\n"
        "default_printer = TestPrinter\n"
        "read_only = false\n"
        "\n"
        "[printer TestPrinter]\n"
        "moonraker_host = printer.local\n",
        encoding="utf-8",
    )

    settings = load_config(config)

    assert settings.read_only is False


def test_load_config_provides_local_default_when_missing(tmp_path: Path) -> None:
    missing = tmp_path / "missing.conf"

    settings = load_config(missing)

    assert settings.default_printer == "Printer"
    assert settings.printers["Printer"].moonraker_host == "127.0.0.1"
    assert settings.printers["Printer"].moonraker_port == 7125


def test_load_config_parses_optional_printer_fields(tmp_path: Path) -> None:
    config = tmp_path / "KlipperTouch.conf"
    config.write_text(
        "[main]\n"
        "default_printer = SecurePrinter\n"
        "\n"
        "[printer SecurePrinter]\n"
        "moonraker_host = printer.local\n"
        "moonraker_port = 7130\n"
        "moonraker_path = /moonraker/\n"
        "moonraker_ssl = true\n"
        "moonraker_api_key = \"abc%def\"\n",
        encoding="utf-8",
    )

    settings = load_config(config)
    printer = settings.printers["SecurePrinter"]

    assert printer.moonraker_path == "moonraker"
    assert printer.moonraker_ssl is True
    assert printer.moonraker_api_key == "abc%def"


def test_load_config_falls_back_when_default_printer_is_invalid(
    tmp_path: Path,
) -> None:
    config = tmp_path / "KlipperTouch.conf"
    config.write_text(
        "[main]\n"
        "default_printer = MissingPrinter\n"
        "\n"
        "[printer FirstPrinter]\n"
        "moonraker_host = first.local\n"
        "\n"
        "[printer SecondPrinter]\n"
        "moonraker_host = second.local\n",
        encoding="utf-8",
    )

    settings = load_config(config)

    assert settings.default_printer == "FirstPrinter"
