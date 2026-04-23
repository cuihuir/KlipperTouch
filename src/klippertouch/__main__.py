import sys

from klippertouch.app import run_app
from klippertouch.cli import parse_args


def main() -> int:
    args = parse_args()
    if args.debug:
        print("Debug logging enabled")
    return run_app(sys.argv)


if __name__ == "__main__":
    raise SystemExit(main())
