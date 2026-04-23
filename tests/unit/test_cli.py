from pathlib import Path

from klippertouch.cli import parse_args


def test_parse_args_defaults_to_read_only() -> None:
    args = parse_args([])
    assert args.read_only is True
    assert args.config is None
    assert args.debug is False


def test_parse_args_accepts_config_and_debug() -> None:
    args = parse_args(["--config", "/tmp/KlipperTouch.conf", "--debug"])
    assert args.config == Path("/tmp/KlipperTouch.conf")
    assert args.debug is True
