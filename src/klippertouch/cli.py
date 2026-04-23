from argparse import ArgumentParser, Namespace
from pathlib import Path


def parse_args(argv: list[str] | None = None) -> Namespace:
    parser = ArgumentParser(prog="klippertouch")
    parser.add_argument("--config", type=Path, default=None)
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--read-only", action="store_true", default=True)
    parser.add_argument(
        "--probe",
        action="store_true",
        help="Run read-only Moonraker probe and exit",
    )
    return parser.parse_args(argv)
