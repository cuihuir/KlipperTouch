#!/usr/bin/env python3
"""Run explicit Moonraker control smoke checks against a configured printer."""

from __future__ import annotations

import argparse
from pathlib import Path

from klippertouch.__main__ import resolve_config_path
from klippertouch.config.loader import load_config
from klippertouch.moonraker.client import MoonrakerClient
from klippertouch.moonraker.safety import CommandPolicy

SMOKE_CONTENT = b"; KlipperTouch control smoke\nM117 KlipperTouch smoke\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=None)
    parser.add_argument("--printer", default="")
    parser.add_argument("--allow-controls", action="store_true")
    parser.add_argument("--file", default="", help="Existing relative G-Code file to start/cancel.")
    parser.add_argument("--upload-name", default="klippertouch_control_smoke.gcode")
    parser.add_argument("--upload-path", default="_klippertouch_smoke")
    parser.add_argument("--skip-upload", action="store_true")
    parser.add_argument("--skip-delete", action="store_true")
    parser.add_argument("--skip-clear", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.allow_controls:
        print("Refusing to send controls without --allow-controls.")
        return 2

    settings = load_config(resolve_config_path(args.config))
    printer_name = args.printer or settings.default_printer
    printer = settings.printers[printer_name]
    client = MoonrakerClient(printer, policy=CommandPolicy(read_only=False))

    print(f"Endpoint: {client.endpoint}")
    print(f"Files before: {len(client.get_gcode_file_list())}")

    uploaded_path = f"{args.upload_path.strip('/')}/{args.upload_name.strip('/')}"
    if not args.skip_upload:
        result = client.upload_gcode_file(
            args.upload_name,
            SMOKE_CONTENT,
            path=args.upload_path,
            print_after_upload=False,
        )
        print(f"Upload: {result}")

    if args.file:
        filename = _normalize_gcode_filename(args.file)
        print(f"Start print: {filename}")
        print(client.start_print(filename))
        print("Cancel print")
        print(client.cancel_print())

    if not args.skip_clear:
        print("Clear status")
        print(client.clear_sdcard_file())

    if not args.skip_upload and not args.skip_delete:
        print(f"Delete upload: {uploaded_path}")
        print(client.delete_gcode_file(uploaded_path))

    print("Control smoke complete.")
    return 0


def _normalize_gcode_filename(filename: str) -> str:
    clean_filename = filename.strip().replace("\\", "/")
    marker = "/gcodes/"
    if marker in clean_filename:
        clean_filename = clean_filename.rsplit(marker, 1)[1]
    return clean_filename.strip("/")


if __name__ == "__main__":
    raise SystemExit(main())
