#!/usr/bin/env python3
"""Capture offscreen QML screenshots for common touchscreen shapes."""

from __future__ import annotations

import argparse
import html
import os
import sys
from pathlib import Path

from PySide6.QtCore import QEventLoop, QObject, QTimer, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuick import QQuickWindow  # noqa: F401

from klippertouch.app import create_gcode_file_model, create_status_models
from klippertouch.config.loader import load_config
from klippertouch.domain.printer import (
    FanStatus,
    FilamentSensorStatus,
    McuStatus,
    PrinterStatus,
    ServiceVersionStatus,
    TemperatureDeviceStatus,
)
from klippertouch.moonraker.client import MoonrakerClient
from klippertouch.moonraker.safety import CommandPolicy
from klippertouch.probe import build_status_from_client

DEFAULT_SIZES = ("800x480", "1024x600", "480x800")
LIVE_METADATA_PREFETCH_LIMIT = 12
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
EXTRUDE_DETAIL_PAGES = ("feed", "materials")
MOVE_DETAIL_PAGES = ("more", "bed_tilt")
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
        "fan",
        "fan_generic chamber",
        "controller_fan 驱动",
        "independent_3z",
        "z_tilt",
        "configfile",
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
    "position_u": 0.02,
    "position_v": -0.04,
    "position_w": 0.01,
    "bed_max_x": 180.0,
    "bed_max_y": 120.0,
    "accelerator_level_available": True,
    "homed_axes": "xyz",
    "exclude_object_names": ("part_a", "part_b", "part_c"),
    "exclude_objects": (
        {
            "name": "part_a",
            "center": [40.0, 35.0],
            "polygon": [[28.0, 25.0], [52.0, 25.0], [54.0, 45.0], [30.0, 47.0]],
        },
        {
            "name": "part_b",
            "center": [88.0, 58.0],
            "polygon": [[76.0, 46.0], [100.0, 45.0], [104.0, 68.0], [82.0, 72.0]],
        },
        {
            "name": "part_c",
            "center": [132.0, 34.0],
            "polygon": [[120.0, 24.0], [144.0, 24.0], [148.0, 44.0], [124.0, 48.0]],
        },
    ),
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
    "fan_devices": (
        FanStatus(name="fan", display_name="Part Fan", speed=45.0, speed_settable=True),
        FanStatus(
            name="fan_generic chamber",
            display_name="Chamber",
            speed=25.0,
            rpm=3180.0,
            speed_settable=True,
        ),
        FanStatus(
            name="controller_fan 驱动",
            display_name="驱动 Fan",
            speed=100.0,
            speed_settable=False,
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
    sample_many_sensors: bool = False,
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
    temperature_devices = [
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
    ]
    if sample_many_sensors:
        temperature_devices.extend(
            (
                TemperatureDeviceStatus(
                    name="temperature_sensor Box",
                    display_name="Box",
                    icon="heat-up",
                    temperature=51.2,
                ),
                TemperatureDeviceStatus(
                    name="temperature_sensor cartographer",
                    display_name="Cartographer",
                    icon="heat-up",
                    temperature=40.7,
                ),
                TemperatureDeviceStatus(
                    name="temperature_sensor cartographer_coil",
                    display_name="Cartographer Coil",
                    icon="heat-up",
                    temperature=25.7,
                ),
                TemperatureDeviceStatus(
                    name="temperature_sensor E3",
                    display_name="E3",
                    icon="heat-up",
                    temperature=44.8,
                ),
                TemperatureDeviceStatus(
                    name="temperature_sensor FLY-π",
                    display_name="FLY-π",
                    icon="heat-up",
                    temperature=34.4,
                ),
                TemperatureDeviceStatus(
                    name="temperature_host FLY-π",
                    display_name="FLY-π Host",
                    icon="heat-up",
                    temperature=34.4,
                ),
            )
        )
    status["temperature_devices"] = tuple(temperature_devices)
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
    sample_files_loading: bool = False,
    sample_files_error: str = "",
    file_current_path: str = "",
    sample_status: bool = False,
    live_status: PrinterStatus | None = None,
    live_temperature_store: dict[str, object] | None = None,
    live_files: list[dict[str, object]] | None = None,
    metadata_by_path: dict[str, dict[str, object]] | None = None,
    metadata_thumbnail_base_url: str = "",
    sample_state: str = "printing",
    sample_many_sensors: bool = False,
    job_detail_pages: tuple[str, ...] = (),
    extrude_detail_pages: tuple[str, ...] = (),
    move_detail_pages: tuple[str, ...] = (),
    job_action_previews: tuple[str, ...] = (),
    file_detail_pages: tuple[str, ...] = (),
    file_action_previews: tuple[str, ...] = (),
    material_system: bool = False,
    read_only: bool = True,
) -> list[Path]:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QGuiApplication.instance() or QGuiApplication([])
    output_dir.mkdir(parents=True, exist_ok=True)
    thumbnail_base = _write_sample_thumbnail(output_dir).as_uri()
    captured: list[Path] = []
    for width, height in sizes:
        for panel in panels:
            engine = QQmlApplicationEngine()
            engine.rootContext().setContextProperty(
                "configuredMaterialSystemEnabled",
                material_system,
            )
            engine.rootContext().setContextProperty("configuredReadOnly", read_only)
            if live_files is not None or sample_files:
                file_model = create_gcode_file_model(
                    live_files if live_files is not None else list(SAMPLE_FILES)
                )
                metadata_base = metadata_thumbnail_base_url or thumbnail_base
                file_model.setFileMetadata(
                    "OrcaCube_PLA_27m41s.gcode",
                    SAMPLE_METADATA,
                    metadata_base,
                )
                for path, metadata in (metadata_by_path or {}).items():
                    file_model.setFileMetadata(path, metadata, metadata_base)
                engine.rootContext().setContextProperty("gcodeFileModel", file_model)
                engine.gcode_file_model = file_model  # type: ignore[attr-defined]
            if live_status is not None:
                status_model, temperature_model = create_status_models(
                    live_status,
                    initial_temperature_store=live_temperature_store,
                )
                engine.rootContext().setContextProperty("statusModel", status_model)
                engine.rootContext().setContextProperty(
                    "temperatureDeviceModel",
                    temperature_model,
                )
                engine.status_model = status_model  # type: ignore[attr-defined]
                engine.temperature_model = temperature_model  # type: ignore[attr-defined]
            elif sample_status:
                first_extruder, first_bed = SAMPLE_HISTORY[0]
                status_model, temperature_model = create_status_models(
                    make_sample_status(
                        first_extruder,
                        first_bed,
                        state=sample_state,
                        sample_many_sensors=sample_many_sensors,
                    )
                )
                for extruder_temperature, bed_temperature in SAMPLE_HISTORY[1:]:
                    status_model.set_status(
                        make_sample_status(
                            extruder_temperature,
                            bed_temperature,
                            state=sample_state,
                            sample_many_sensors=sample_many_sensors,
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
            _prepare_panel_capture(root, panel)
            if panel == "print":
                _prepare_files_panel(
                    root,
                    sample_files_loading=sample_files_loading,
                    sample_files_error=sample_files_error,
                    file_current_path=file_current_path,
                )
            app.processEvents()
            for detail_page in _detail_pages_for_panel(
                panel,
                job_detail_pages,
                extrude_detail_pages,
                move_detail_pages,
                file_detail_pages,
            ):
                if detail_page:
                    if panel == "job_status":
                        _set_job_status_detail_page(root, detail_page)
                    elif panel == "extrude":
                        _set_extrude_detail_page(root, detail_page)
                    elif panel == "move":
                        _set_move_detail_page(root, detail_page)
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
                    _prepare_panel_capture(root, panel)
                    app.processEvents()
                    _settle_qml(app)
                    image = root.grabWindow()
                    target_name = f"{panel}_{detail_page}" if detail_page else panel
                    if action_preview:
                        target_name = f"{target_name}_{action_preview}"
                    target = output_dir / f"{target_name}-{width}x{height}.png"
                    if not image.save(str(target)):
                        raise RuntimeError(f"Failed to save screenshot {target}")
                    captured.append(target)
    return captured


def _prepare_panel_capture(root: QObject, panel: str) -> None:
    if panel == "splash":
        return
    root.setProperty("klippyState", "ready")
    root.setProperty("webhooksState", "ready")
    root.setProperty("moonrakerVersion", "screenshot")
    root.setProperty("startupSplashHoldComplete", True)
    root.setProperty("startupSplashVisible", False)
    root.setProperty("systemFaultVisible", False)


def _settle_qml(app: QGuiApplication, milliseconds: int = 120) -> None:
    loop = QEventLoop()
    QTimer.singleShot(milliseconds, loop.quit)
    loop.exec()
    app.processEvents()


def _prepare_files_panel(
    root: QObject,
    *,
    sample_files_loading: bool,
    sample_files_error: str,
    file_current_path: str,
) -> None:
    panel = _loaded_panel(root, "filesPanel")
    if panel is None:
        return
    panel.setProperty("loading", sample_files_loading)
    panel.setProperty("loadError", sample_files_error)
    active_model = panel.property("activeFileModel")
    if file_current_path and hasattr(active_model, "setCurrentPath"):
        active_model.setCurrentPath(file_current_path)


def _detail_pages_for_panel(
    panel: str,
    job_detail_pages: tuple[str, ...],
    extrude_detail_pages: tuple[str, ...],
    move_detail_pages: tuple[str, ...],
    file_detail_pages: tuple[str, ...],
) -> tuple[str, ...]:
    if panel == "job_status" and job_detail_pages:
        return job_detail_pages
    if panel == "extrude" and extrude_detail_pages:
        return extrude_detail_pages
    if panel == "move" and move_detail_pages:
        return move_detail_pages
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
    panel = _loaded_panel(root, "jobStatusPanel")
    if panel is None:
        raise RuntimeError("Failed to find jobStatusPanel for detail screenshot")
    panel.setProperty("detailPage", page)


def _set_job_status_action_preview(root: QObject, action: str) -> None:
    panel = _loaded_panel(root, "jobStatusPanel")
    if panel is None:
        raise RuntimeError("Failed to find jobStatusPanel for action preview screenshot")
    panel.setProperty("pendingJobAction", action)
    if action == "skip":
        panel.setProperty("pendingJobObject", "part_b")


def _set_files_detail_page(root: QObject, page: str) -> None:
    panel = _loaded_panel(root, "filesPanel")
    if panel is None:
        raise RuntimeError("Failed to find filesPanel for detail screenshot")
    panel.setProperty("detailPage", page == "detail")


def _set_extrude_detail_page(root: QObject, page: str) -> None:
    panel = _loaded_panel(root, "extrudePanel")
    if panel is None:
        raise RuntimeError("Failed to find extrudePanel for detail screenshot")
    panel.setProperty("detailPage", page)


def _set_move_detail_page(root: QObject, page: str) -> None:
    panel = _loaded_panel(root, "movePanel")
    if panel is None:
        raise RuntimeError("Failed to find movePanel for detail screenshot")
    panel.setProperty("detailPage", page)


def _set_files_action_preview(root: QObject, action: str) -> None:
    panel = _loaded_panel(root, "filesPanel")
    if panel is None:
        raise RuntimeError("Failed to find filesPanel for action preview screenshot")
    panel.setProperty("pendingFileAction", action)


def _loaded_panel(root: QObject, object_name: str) -> QObject | None:
    panel = root.findChild(QObject, object_name)
    if panel is not None:
        return panel
    loader = root.findChild(QObject, "panelLoader")
    item = loader.property("item") if loader is not None else None
    if isinstance(item, QObject) and item.objectName() == object_name:
        return item
    return None


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
        "--sample-files-loading",
        action="store_true",
        help="Show the Print panel loading state in sample captures.",
    )
    parser.add_argument(
        "--sample-files-error",
        default="",
        help="Show the Print panel file-load error state with this message.",
    )
    parser.add_argument(
        "--file-current-path",
        default="",
        help="Set the sample Print panel current directory, for example calibration/flow.",
    )
    parser.add_argument(
        "--sample-status",
        action="store_true",
        help="Inject sample printer/job status into the QML context before capturing.",
    )
    parser.add_argument(
        "--live-config",
        type=Path,
        default=None,
        help="Read a KlipperTouch config, run a read-only Moonraker probe, and capture live UI.",
    )
    parser.add_argument(
        "--sample-many-sensors",
        action="store_true",
        help="Include additional read-only temperature sensors in --sample-status captures.",
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
        "--extrude-detail-pages",
        nargs="+",
        choices=EXTRUDE_DETAIL_PAGES,
        default=(),
        help="Capture specific Extrude subpages, for example materials.",
    )
    parser.add_argument(
        "--move-detail-pages",
        nargs="+",
        choices=MOVE_DETAIL_PAGES,
        default=(),
        help="Capture specific Move subpages, for example more.",
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
    parser.add_argument(
        "--material-system",
        action="store_true",
        help="Inject a configured AFC/AMS material-system flag for Extrude screenshots.",
    )
    args = parser.parse_args(argv)
    live_status = None
    live_temperature_store = None
    live_files = None
    live_metadata_by_path: dict[str, dict[str, object]] = {}
    live_metadata_thumbnail_base_url = ""
    live_read_only = True
    if args.live_config is not None:
        settings = load_config(args.live_config)
        printer = settings.printers[settings.default_printer]
        live_read_only = settings.read_only
        live_client = MoonrakerClient(printer, policy=CommandPolicy(read_only=True))
        live_status = build_status_from_client(live_client)
        live_temperature_store = live_client.get_temperature_store()
        live_files = live_client.get_gcode_file_list()
        live_metadata_thumbnail_base_url = f"{live_client.endpoint}/server/files/gcodes/"
        current_path = args.file_current_path.strip().strip("/")
        live_metadata_paths = sorted(
            path
            for item in live_files
            for path in (str(item.get("path", "")).strip().strip("/"),)
            if path and (not current_path or path.startswith(f"{current_path}/"))
        )
        for path in live_metadata_paths[:LIVE_METADATA_PREFETCH_LIMIT]:
            live_metadata_by_path[path] = live_client.get_gcode_file_metadata(path)

    captured = capture(
        qml_path=args.qml,
        output_dir=args.output,
        sizes=tuple(args.sizes),
        panels=tuple(args.panels),
        sample_files=args.sample_files,
        sample_files_loading=args.sample_files_loading,
        sample_files_error=args.sample_files_error,
        file_current_path=args.file_current_path,
        sample_status=args.sample_status or live_status is not None,
        live_status=live_status,
        live_temperature_store=live_temperature_store,
        live_files=live_files,
        metadata_by_path=live_metadata_by_path,
        metadata_thumbnail_base_url=live_metadata_thumbnail_base_url,
        sample_state=args.sample_state,
        sample_many_sensors=args.sample_many_sensors,
        job_detail_pages=tuple(args.job_detail_pages),
        extrude_detail_pages=tuple(args.extrude_detail_pages),
        move_detail_pages=tuple(args.move_detail_pages),
        job_action_previews=tuple(args.job_action_previews),
        file_detail_pages=tuple(args.file_detail_pages),
        file_action_previews=tuple(args.file_action_previews),
        material_system=args.material_system,
        read_only=live_read_only,
    )
    if not args.no_index:
        print(write_index(args.output, captured))
    for path in captured:
        print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
