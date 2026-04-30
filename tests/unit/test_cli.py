from pathlib import Path

from klippertouch.__main__ import resolve_config_path
from klippertouch.cli import parse_args


def test_parse_args_defaults_to_configured_control_policy() -> None:
    args = parse_args([])
    assert args.read_only is False
    assert args.allow_controls is False
    assert args.config is None
    assert args.debug is False
    assert args.fullscreen is False
    assert args.probe is False


def test_parse_args_accepts_control_policy_overrides() -> None:
    assert parse_args(["--read-only"]).read_only is True
    assert parse_args(["--allow-controls"]).allow_controls is True


def test_parse_args_accepts_config_and_debug() -> None:
    args = parse_args(["--config", "/tmp/KlipperTouch.conf", "--debug"])
    assert args.config == Path("/tmp/KlipperTouch.conf")
    assert args.debug is True


def test_parse_args_accepts_fullscreen_launch_mode() -> None:
    args = parse_args(["--fullscreen"])

    assert args.fullscreen is True


def test_main_starts_gui_without_blocking_on_initial_status_probe() -> None:
    source = Path("src/klippertouch/__main__.py").read_text(encoding="utf-8")

    assert "Config path:" in source
    assert "Control mode:" in source
    assert "Moonraker endpoint:" in source
    assert "policy = CommandPolicy(read_only=settings.read_only)" in source
    assert "settings = _apply_control_override(settings, args)" in source
    assert "client = MoonrakerClient(printer, policy=policy)" in source
    assert "initial_status = build_status_from_client(client)" not in source
    assert "initial_temperature_store = client.get_temperature_store()" not in source
    assert "initial_files = client.get_gcode_file_list()" not in source
    assert "status_stream_client=client" in source
    assert "file_refresh_client=client" in source
    assert "job_control_client=client" in source
    assert "full_screen=args.fullscreen" in source
    assert "initial_status=" not in source
    assert "initial_files=" not in source
    assert "material_system_enabled=settings.material_system_enabled" in source


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
