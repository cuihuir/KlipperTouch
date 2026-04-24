import json
import sys
from pathlib import Path

from klippertouch.app import run_app
from klippertouch.cli import parse_args
from klippertouch.config.loader import load_config
from klippertouch.moonraker.client import MoonrakerClient
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

    if args.probe:
        printer = settings.printers[settings.default_printer]
        status = build_status_from_client(MoonrakerClient(printer))
        print(json.dumps(status_to_dict(status), ensure_ascii=False, indent=2))
        return 0

    if args.debug:
        print("Debug logging enabled", flush=True)
        print(f"Config path: {config_path}", flush=True)

    initial_status = None
    initial_temperature_store = None
    initial_files = None
    client = None
    try:
        printer = settings.printers[settings.default_printer]
        client = MoonrakerClient(printer)
        if args.debug:
            print(f"Moonraker endpoint: {client.endpoint}", flush=True)
        initial_status = build_status_from_client(client)
        initial_temperature_store = client.get_temperature_store()
        initial_files = client.get_gcode_file_list()
        if args.debug:
            print(f"Initial G-Code files: {len(initial_files)}", flush=True)
    except Exception as exc:
        if args.debug:
            print(f"Read-only startup probe failed: {exc}", flush=True)
    return run_app(
        sys.argv,
        initial_status=initial_status,
        initial_temperature_store=initial_temperature_store,
        initial_files=initial_files,
        status_stream_client=client,
        file_refresh_client=client,
    )


if __name__ == "__main__":
    raise SystemExit(main())
