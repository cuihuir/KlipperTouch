#!/usr/bin/env python3
"""Capture offscreen QML screenshots for common touchscreen shapes."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuick import QQuickWindow  # noqa: F401

from klippertouch.app import create_gcode_file_model

DEFAULT_SIZES = ("800x480", "1024x600", "480x800")
DEFAULT_PANELS = ("main", "print", "job_status", "temperature", "move", "extrude", "more")
SAMPLE_FILES = (
    {
        "path": "OrcaCube_PLA_27m41s.gcode",
        "modified": 1776411420,
        "size": 2_516_582,
        "permissions": "rw",
    },
    {
        "path": "calibration/flow/flow_cube.gcode",
        "modified": 1776411180,
        "size": 984_132,
        "permissions": "rw",
    },
)


def parse_size(value: str) -> tuple[int, int]:
    width, separator, height = value.lower().partition("x")
    if not separator:
        raise argparse.ArgumentTypeError(f"Invalid size {value!r}; expected WIDTHxHEIGHT")
    try:
        parsed = (int(width), int(height))
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"Invalid size {value!r}; expected integers") from exc
    if parsed[0] <= 0 or parsed[1] <= 0:
        raise argparse.ArgumentTypeError(f"Invalid size {value!r}; dimensions must be positive")
    return parsed


def capture(
    *,
    qml_path: Path,
    output_dir: Path,
    sizes: tuple[tuple[int, int], ...],
    panels: tuple[str, ...],
    sample_files: bool = False,
) -> list[Path]:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QGuiApplication.instance() or QGuiApplication([])
    output_dir.mkdir(parents=True, exist_ok=True)
    captured: list[Path] = []
    for width, height in sizes:
        for panel in panels:
            engine = QQmlApplicationEngine()
            if sample_files:
                file_model = create_gcode_file_model(list(SAMPLE_FILES))
                engine.rootContext().setContextProperty("gcodeFileModel", file_model)
                engine.gcode_file_model = file_model  # type: ignore[attr-defined]
            engine.load(QUrl.fromLocalFile(str(qml_path.resolve())))
            roots = engine.rootObjects()
            if not roots:
                raise RuntimeError(f"Failed to load QML root from {qml_path}")
            root = roots[0]
            root.setProperty("width", width)
            root.setProperty("height", height)
            root.setProperty("panelStack", [panel])
            root.setProperty("currentPanel", panel)
            app.processEvents()
            image = root.grabWindow()
            target = output_dir / f"{panel}-{width}x{height}.png"
            if not image.save(str(target)):
                raise RuntimeError(f"Failed to save screenshot {target}")
            captured.append(target)
    return captured


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--qml",
        type=Path,
        default=Path("src/klippertouch/qml/main.qml"),
        help="Path to the root QML file.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/screenshots"),
        help="Directory where PNG captures are written.",
    )
    parser.add_argument(
        "--sizes",
        nargs="+",
        type=parse_size,
        default=tuple(parse_size(value) for value in DEFAULT_SIZES),
        help="One or more screen sizes, for example 800x480 480x800.",
    )
    parser.add_argument(
        "--panels",
        nargs="+",
        default=DEFAULT_PANELS,
        help="Panel route names to capture.",
    )
    parser.add_argument(
        "--sample-files",
        action="store_true",
        help="Inject sample G-Code files into the QML context before capturing.",
    )
    args = parser.parse_args(argv)

    captured = capture(
        qml_path=args.qml,
        output_dir=args.output,
        sizes=tuple(args.sizes),
        panels=tuple(args.panels),
        sample_files=args.sample_files,
    )
    for path in captured:
        print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
