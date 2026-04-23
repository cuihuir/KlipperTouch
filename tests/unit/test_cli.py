from pathlib import Path

from klippertouch.cli import parse_args


def test_parse_args_defaults_to_read_only() -> None:
    args = parse_args([])
    assert args.read_only is True
    assert args.config is None
    assert args.debug is False
    assert args.probe is False


def test_parse_args_accepts_config_and_debug() -> None:
    args = parse_args(["--config", "/tmp/KlipperTouch.conf", "--debug"])
    assert args.config == Path("/tmp/KlipperTouch.conf")
    assert args.debug is True


def test_main_attempts_read_only_status_before_gui() -> None:
    source = Path("src/klippertouch/__main__.py").read_text(encoding="utf-8")

    assert "initial_status = None" in source
    assert "client = MoonrakerClient(printer)" in source
    assert "initial_status = build_status_from_client(client)" in source
    assert "initial_files = client.get_gcode_file_list()" in source
    assert "status_stream_client=client" in source
    assert "initial_files=initial_files" in source
