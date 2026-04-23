import json
import sys
from pathlib import Path

from klippertouch.app import run_app
from klippertouch.cli import parse_args
from klippertouch.config.loader import load_config
from klippertouch.moonraker.client import MoonrakerClient
from klippertouch.probe import build_status_from_client, status_to_dict


def main() -> int:
    args = parse_args()
    config_path = args.config or Path.home() / "printer_data" / "config" / "KlipperTouch.conf"
    settings = load_config(config_path)

    if args.probe:
        printer = settings.printers[settings.default_printer]
        status = build_status_from_client(MoonrakerClient(printer))
        print(json.dumps(status_to_dict(status), ensure_ascii=False, indent=2))
        return 0

    if args.debug:
        print("Debug logging enabled", flush=True)

    initial_status = None
    client = None
    try:
        printer = settings.printers[settings.default_printer]
        client = MoonrakerClient(printer)
        initial_status = build_status_from_client(client)
    except Exception as exc:
        if args.debug:
            print(f"Read-only startup probe failed: {exc}", flush=True)
    return run_app(sys.argv, initial_status=initial_status, status_stream_client=client)


if __name__ == "__main__":
    raise SystemExit(main())
