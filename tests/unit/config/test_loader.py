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


def test_load_config_provides_local_default_when_missing(tmp_path: Path) -> None:
    missing = tmp_path / "missing.conf"

    settings = load_config(missing)

    assert settings.default_printer == "Printer"
    assert settings.printers["Printer"].moonraker_host == "127.0.0.1"
    assert settings.printers["Printer"].moonraker_port == 7125
