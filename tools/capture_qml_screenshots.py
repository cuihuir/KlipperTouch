#!/usr/bin/env python3
"""Capture offscreen QML screenshots for common touchscreen shapes."""

from __future__ import annotations

import argparse
import html
import os
import sys
from pathlib import Path

from PySide6.QtCore import QObject, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuick import QQuickWindow  # noqa: F401

from klippertouch.app import create_gcode_file_model, create_status_models
from klippertouch.domain.printer import (
    FilamentSensorStatus,
    McuStatus,
    PrinterStatus,
    ServiceVersionStatus,
    TemperatureDeviceStatus,
)

DEFAULT_SIZES = ("800x480", "1024x600", "480x800")
DEFAULT_PANELS = (
    "main",
    "print",
    "job_status",
    "temperature",
    "move",
    "extrude",
    "more",
    "notifications",
    "splash",
    "system",
    "network",
    "logs",
    "language",
    "update",
)
JOB_DETAIL_PAGES = ("summary", "advanced", "exclude", "time", "motion", "extrusion")
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
SAMPLE_METADATA = {
    "estimated_time": 1661.0,
    "filament_total": 2234.0,
    "object_height": 12.35,
    "layer_height": 0.2,
    "slicer": "OrcaSlicer",
    "slicer_version": "2.2.0",
    "nozzle_diameter": 0.4,
    "filament_type": "PLA",
    "filament_name": "Matte Black",
    "filament_weight_total": 12.35,
    "thumbnails": [
        {
            "width": 300,
            "height": 300,
            "relative_path": ".thumbs/OrcaCube_PLA_27m41s-300x300.svg",
        },
    ],
}
SAMPLE_STATUS = {
    "hostname": "orangepi3b",
    "klippy_state": "ready",
    "klipper_version": "v0.13.0",
    "moonraker_version": "v0.10.0",
    "mcu_statuses": (
        McuStatus(name="mcu", version="v0.13.0-main", build_versions="gcc 12.2.0"),
    ),
    "service_versions": (
        ServiceVersionStatus(name="klipper", version="v0.13.0", configured_type="git_repo"),
        ServiceVersionStatus(name="moonraker", version="v0.10.0", configured_type="git_repo"),
    ),
    "objects": (
        "extruder",
        "heater_bed",
        "print_stats",
        "display_status",
        "toolhead",
        "gcode_move",
        "exclude_object",
        "filament_switch_sensor runout",
    ),
    "temperature_devices": (
        TemperatureDeviceStatus(
            name="extruder",
            display_name="Extruder",
            icon="extruder",
            temperature=211.8,
            target=215.0,
        ),
        TemperatureDeviceStatus(
            name="heater_bed",
            display_name="Heater Bed",
            icon="bed",
            temperature=58.4,
            target=60.0,
        ),
    ),
    "print_state": "printing",
    "print_filename": "OrcaCube_PLA_27m41s.gcode",
    "print_progress": 42.0,
    "print_message": "Printing",
    "print_duration": 1035.0,
    "total_duration": 1661.0,
    "filament_used": 1856.0,
    "current_layer": 12,
    "total_layers": 36,
    "position_x": 10.1,
    "position_y": 20.2,
    "position_z": 3.3,
    "position_e": 40.4,
    "homed_axes": "xyz",
    "exclude_object_names": ("part_a", "part_b", "part_c"),
    "excluded_object_names": ("part_a",),
    "current_object": "part_b",
    "requested_speed": 125.0,
    "speed_factor": 100.0,
    "extrude_factor": 96.0,
    "z_offset": -0.02,
    "max_accel": 3000.0,
    "max_velocity": 250.0,
    "filament_sensors": (
        FilamentSensorStatus(
            name="filament_switch_sensor runout",
            display_name="Runout",
            sensor_type="switch",
            enabled=True,
            filament_detected=True,
        ),
    ),
}
SAMPLE_HISTORY = ((205.0, 56.0), (208.0, 57.0), (211.8, 58.4))
SAMPLE_STATES = ("printing", "paused", "complete", "cancelled", "error")


def make_sample_status(
    extruder_temperature: float,
    bed_temperature: float,
    *,
    state: str = "printing",
) -> PrinterStatus:
    status = dict(SAMPLE_STATUS)
    status["print_state"] = state
    if state == "paused":
        status["print_message"] = "Paused"
    elif state == "complete":
        status["print_message"] = "Complete"
        status["print_progress"] = 100.0
    elif state == "cancelled":
        status["print_message"] = "Cancelled"
    elif state == "error":
        status["print_message"] = "Error"
    status["temperature_devices"] = (
        TemperatureDeviceStatus(
            name="extruder",
            display_name="Extruder",
            icon="extruder",
            temperature=extruder_temperature,
            target=215.0,
        ),
        TemperatureDeviceStatus(
            name="heater_bed",
            display_name="Heater Bed",
            icon="bed",
            temperature=bed_temperature,
            target=60.0,
        ),
    )
    return PrinterStatus(**status)


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


def _write_sample_thumbnail(output_dir: Path) -> Path:
    thumbnail_root = output_dir / "sample_files" / "gcodes"
    thumbnail_dir = thumbnail_root / ".thumbs"
    thumbnail_dir.mkdir(parents=True, exist_ok=True)
    thumbnail_path = thumbnail_dir / "OrcaCube_PLA_27m41s-300x300.svg"
    if not thumbnail_path.exists():
        thumbnail_path.write_text(
            """<svg xmlns="http://www.w3.org/2000/svg"
    width="300" height="300" viewBox="0 0 300 300">
<rect width="300" height="300" rx="18" fill="#111819"/>
<path d="M74 211h152l-19-101-35 24-23-50-28 63-28-17z" fill="#5c6b6f"/>
<rect x="82" y="219" width="136" height="12" rx="6" fill="#8b9496"/>
</svg>
""",
            encoding="utf-8",
        )
    return thumbnail_root


def capture(
    *,
    qml_path: Path,
    output_dir: Path,
    sizes: tuple[tuple[int, int], ...],
    panels: tuple[str, ...],
    sample_files: bool = False,
    sample_status: bool = False,
    sample_state: str = "printing",
    job_detail_pages: tuple[str, ...] = (),
    job_action_previews: tuple[str, ...] = (),
    file_detail_pages: tuple[str, ...] = (),
    file_action_previews: tuple[str, ...] = (),
) -> list[Path]:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QGuiApplication.instance() or QGuiApplication([])
    output_dir.mkdir(parents=True, exist_ok=True)
    thumbnail_base = _write_sample_thumbnail(output_dir).as_uri()
    captured: list[Path] = []
    for width, height in sizes:
        for panel in panels:
            engine = QQmlApplicationEngine()
            if sample_files:
                file_model = create_gcode_file_model(list(SAMPLE_FILES))
                file_model.setFileMetadata(
                    "OrcaCube_PLA_27m41s.gcode",
                    SAMPLE_METADATA,
                    thumbnail_base,
                )
                engine.rootContext().setContextProperty("gcodeFileModel", file_model)
                engine.gcode_file_model = file_model  # type: ignore[attr-defined]
            if sample_status:
                first_extruder, first_bed = SAMPLE_HISTORY[0]
                status_model, temperature_model = create_status_models(
                    make_sample_status(first_extruder, first_bed, state=sample_state)
                )
                for extruder_temperature, bed_temperature in SAMPLE_HISTORY[1:]:
                    status_model.set_status(
                        make_sample_status(
                            extruder_temperature,
                            bed_temperature,
                            state=sample_state,
                        )
                    )
                engine.rootContext().setContextProperty("statusModel", status_model)
                engine.rootContext().setContextProperty(
                    "temperatureDeviceModel",
                    temperature_model,
                )
                engine.status_model = status_model  # type: ignore[attr-defined]
                engine.temperature_model = temperature_model  # type: ignore[attr-defined]
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
            for detail_page in _detail_pages_for_panel(panel, job_detail_pages, file_detail_pages):
                if detail_page:
                    if panel == "job_status":
                        _set_job_status_detail_page(root, detail_page)
                    elif panel == "print":
                        _set_files_detail_page(root, detail_page)
                    app.processEvents()
                for action_preview in _action_previews_for_panel(
                    panel,
                    detail_page,
                    job_action_previews,
                    file_action_previews,
                ):
                    if action_preview:
                        if panel == "job_status":
                            _set_job_status_action_preview(root, action_preview)
                        elif panel == "print":
                            _set_files_action_preview(root, action_preview)
                        app.processEvents()
                    image = root.grabWindow()
                    target_name = f"{panel}_{detail_page}" if detail_page else panel
                    if action_preview:
                        target_name = f"{target_name}_{action_preview}"
                    target = output_dir / f"{target_name}-{width}x{height}.png"
                    if not image.save(str(target)):
                        raise RuntimeError(f"Failed to save screenshot {target}")
                    captured.append(target)
    return captured


def _detail_pages_for_panel(
    panel: str,
    job_detail_pages: tuple[str, ...],
    file_detail_pages: tuple[str, ...],
) -> tuple[str, ...]:
    if panel == "job_status" and job_detail_pages:
        return job_detail_pages
    if panel == "print" and file_detail_pages:
        return file_detail_pages
    return ("",)


def _action_previews_for_panel(
    panel: str,
    detail_page: str,
    job_action_previews: tuple[str, ...],
    file_action_previews: tuple[str, ...],
) -> tuple[str, ...]:
    if panel == "job_status" and detail_page == "summary" and job_action_previews:
        return job_action_previews
    if panel == "print" and detail_page == "detail" and file_action_previews:
        return file_action_previews
    return ("",)


def _set_job_status_detail_page(root: QObject, page: str) -> None:
    panel = root.findChild(QObject, "jobStatusPanel")
    if panel is None:
        loader = root.findChild(QObject, "panelLoader")
        panel = loader.property("item") if loader is not None else None
    if panel is None:
        raise RuntimeError("Failed to find jobStatusPanel for detail screenshot")
    panel.setProperty("detailPage", page)


def _set_job_status_action_preview(root: QObject, action: str) -> None:
    panel = root.findChild(QObject, "jobStatusPanel")
    if panel is None:
        loader = root.findChild(QObject, "panelLoader")
        panel = loader.property("item") if loader is not None else None
    if panel is None:
        raise RuntimeError("Failed to find jobStatusPanel for action preview screenshot")
    panel.setProperty("pendingJobAction", action)
    if action == "skip":
        panel.setProperty("pendingJobObject", "part_b")


def _set_files_detail_page(root: QObject, page: str) -> None:
    panel = root.findChild(QObject, "filesPanel")
    if panel is None:
        loader = root.findChild(QObject, "panelLoader")
        panel = loader.property("item") if loader is not None else None
    if panel is None:
        raise RuntimeError("Failed to find filesPanel for detail screenshot")
    panel.setProperty("detailPage", page == "detail")


def _set_files_action_preview(root: QObject, action: str) -> None:
    panel = root.findChild(QObject, "filesPanel")
    if panel is None:
        loader = root.findChild(QObject, "panelLoader")
        panel = loader.property("item") if loader is not None else None
    if panel is None:
        raise RuntimeError("Failed to find filesPanel for action preview screenshot")
    panel.setProperty("pendingFileAction", action)


def write_index(output_dir: Path, captured: list[Path]) -> Path:
    index_path = output_dir / "index.html"
    items = []
    for path in captured:
        relative = path.relative_to(output_dir)
        label = html.escape(relative.stem)
        src = html.escape(relative.as_posix())
        items.append(
            f'<figure><img src="{src}" alt="{label}"><figcaption>{label}</figcaption></figure>'
        )
    index_path.write_text(
        "\n".join(
            [
                "<!doctype html>",
                '<html lang="en">',
                "<head>",
                '<meta charset="utf-8">',
                "<title>KlipperTouch Screenshots</title>",
                "<style>",
                "body{background:#111;color:#ddd;font-family:sans-serif;margin:24px}",
                ".grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:18px}",
                "figure{margin:0;background:#1b1b1b;border:1px solid #333;padding:10px}",
                "img{width:100%;height:auto;display:block}",
                "figcaption{margin-top:8px;font-size:14px;color:#aaa}",
                "</style>",
                "</head>",
                "<body>",
                "<h1>KlipperTouch Screenshots</h1>",
                '<div class="grid">',
                *items,
                "</div>",
                "</body>",
                "</html>",
            ]
        ),
        encoding="utf-8",
    )
    return index_path


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
    parser.add_argument(
        "--sample-status",
        action="store_true",
        help="Inject sample printer/job status into the QML context before capturing.",
    )
    parser.add_argument(
        "--sample-state",
        choices=SAMPLE_STATES,
        default="printing",
        help="Choose the sample print state used with --sample-status.",
    )
    parser.add_argument(
        "--job-detail-pages",
        nargs="+",
        choices=JOB_DETAIL_PAGES,
        default=(),
        help="Capture specific Job Status subpages, for example summary time motion extrusion.",
    )
    parser.add_argument(
        "--job-action-previews",
        nargs="+",
        choices=("pause", "resume", "cancel", "skip"),
        default=(),
        help="Capture specific read-only Job Status action preview states.",
    )
    parser.add_argument(
        "--file-detail-pages",
        nargs="+",
        choices=("detail",),
        default=(),
        help='Capture specific Print subpages, for example "detail".',
    )
    parser.add_argument(
        "--file-action-previews",
        nargs="+",
        choices=("print", "delete"),
        default=(),
        help="Capture specific read-only Print action preview states.",
    )
    parser.add_argument(
        "--no-index",
        action="store_true",
        help="Do not write index.html next to the captured screenshots.",
    )
    args = parser.parse_args(argv)

    captured = capture(
        qml_path=args.qml,
        output_dir=args.output,
        sizes=tuple(args.sizes),
        panels=tuple(args.panels),
        sample_files=args.sample_files,
        sample_status=args.sample_status,
        sample_state=args.sample_state,
        job_detail_pages=tuple(args.job_detail_pages),
        job_action_previews=tuple(args.job_action_previews),
        file_detail_pages=tuple(args.file_detail_pages),
        file_action_previews=tuple(args.file_action_previews),
    )
    if not args.no_index:
        print(write_index(args.output, captured))
    for path in captured:
        print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
