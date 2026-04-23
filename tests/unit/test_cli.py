from pathlib import Path

from klippertouch.__main__ import resolve_config_path
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
    assert "file_refresh_client=client" in source
    assert "initial_files=initial_files" in source


def test_resolve_config_path_prefers_explicit_path(tmp_path: Path) -> None:
    explicit = tmp_path / "custom.conf"

    assert resolve_config_path(explicit) == explicit


def test_resolve_config_path_prefers_local_config(monkeypatch, tmp_path: Path) -> None:
    home = tmp_path / "home"
    project = tmp_path / "project"
    config = project / "config" / "KlipperTouch.conf"
    config.parent.mkdir(parents=True)
    config.write_text("[main]\n", encoding="utf-8")
    home_config = home / ".config" / "KlipperTouch" / "KlipperTouch.conf"
    home_config.parent.mkdir(parents=True)
    home_config.write_text("[main]\n", encoding="utf-8")
    project.mkdir(exist_ok=True)
    monkeypatch.chdir(project)
    monkeypatch.setattr(Path, "home", lambda: home)

    assert resolve_config_path(None) == config
