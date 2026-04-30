import json
import sys
from argparse import Namespace
from dataclasses import replace
from pathlib import Path

from klippertouch.app import run_app
from klippertouch.cli import parse_args
from klippertouch.config.loader import load_config
from klippertouch.config.models import AppSettings
from klippertouch.moonraker.client import MoonrakerClient
from klippertouch.moonraker.safety import CommandPolicy
from klippertouch.probe import build_status_from_client, status_to_dict


def resolve_config_path(explicit_path: Path | None = None) -> Path:
    if explicit_path is not None:
        return explicit_path

    candidates = (
        Path.cwd() / "config" / "KlipperTouch.conf",
        Path.cwd() / "KlipperTouch.conf",
        Path.home() / "printer_data" / "config" / "KlipperTouch.conf",
        Path.home() / ".config" / "KlipperTouch" / "KlipperTouch.conf",
    )
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def main() -> int:
    args = parse_args()
    config_path = resolve_config_path(args.config)
    settings = load_config(config_path)
    settings = _apply_control_override(settings, args)

    if args.probe:
        printer = settings.printers[settings.default_printer]
        policy = CommandPolicy(read_only=settings.read_only)
        status = build_status_from_client(MoonrakerClient(printer, policy=policy))
        print(json.dumps(status_to_dict(status), ensure_ascii=False, indent=2))
        return 0

    if args.debug:
        print("Debug logging enabled", flush=True)
        print(f"Config path: {config_path}", flush=True)
        print(
            f"Control mode: {'read-only' if settings.read_only else 'controls enabled'}",
            flush=True,
        )

    client = None
    try:
        printer = settings.printers[settings.default_printer]
        policy = CommandPolicy(read_only=settings.read_only)
        client = MoonrakerClient(printer, policy=policy)
        if args.debug:
            print(f"Moonraker endpoint: {client.endpoint}", flush=True)
    except Exception as exc:
        if args.debug:
            print(f"Moonraker client setup failed: {exc}", flush=True)
    return run_app(
        sys.argv,
        status_stream_client=client,
        file_refresh_client=client,
        job_control_client=client,
        material_system_enabled=settings.material_system_enabled,
        full_screen=args.fullscreen,
    )


def _apply_control_override(settings: AppSettings, args: Namespace) -> AppSettings:
    if getattr(args, "allow_controls", False):
        return replace(settings, read_only=False)
    if getattr(args, "read_only", False):
        return replace(settings, read_only=True)
    return settings


if __name__ == "__main__":
    raise SystemExit(main())
