# KlipperScreen Architecture Map

This document records source-derived observations from `/home/tope/project_py/KlipperScreen`. It is not a line-by-line porting plan. Its purpose is to preserve the behavioral contracts KlipperTouch must reproduce with PySide6/QML.

## Runtime Entry

`screen.py` defines the GTK window, loads config, determines display size and orientation, initializes theme assets, creates `BasePanel`, and starts the initial Moonraker connection flow.

Key behavior to preserve:

- Windowed mode is selected when width or height is configured; otherwise fullscreen is used.
- Orientation is derived from aspect ratio.
- Configuration is loaded before UI activation.
- Invalid configuration blocks startup and shows an error.
- Multi-printer configurations show printer selection unless a valid default printer exists.

## Connection Model

KlipperScreen uses REST for startup checks and WebSocket for ongoing updates.

REST responsibilities in `KlippyRest.py`:

- Build the endpoint from host, port, optional path, SSL, and API key.
- Read `server/info`, `printer/info`, G-code help, one-shot token, and thumbnails.
- Convert Moonraker responses by returning `result` when present.
- Capture connection status text for UI display.

WebSocket responsibilities in `KlippyWebsocket.py`:

- Create a JSON-RPC WebSocket connection to `/websocket`.
- Track request IDs and callback handlers.
- Dispatch notifications by method name.
- Reconnect up to a fixed retry count.
- Provide a Moonraker API wrapper for both read-only methods and state-changing commands.

## State Model

`ks_includes/printer.py` stores the current printer data and derives capabilities from `configfile.config`.

Important derived concepts:

- Extruders and heater devices.
- Temperature sensors and temperature fans.
- Fans, output pins, PWM tools, LEDs, filament sensors, probes, cameras, and power devices.
- Print state, including `ready`, `printing`, `paused`, `startup`, `shutdown`, `error`, and `disconnected`.
- Available macros, with hidden and renamed macros filtered out.

KlipperTouch should keep raw Moonraker data separate from derived UI models so QML screens do not depend on raw object dictionaries.

## Subscription Model

`screen.py` builds a broad object subscription including:

- Core status: `webhooks`, `print_stats`, `idle_timeout`, `pause_resume`, `display_status`, `virtual_sdcard`.
- Motion: `toolhead`, `gcode_move`, `motion_report`.
- Configuration: `configfile`.
- Calibration and mesh: `bed_mesh`, `manual_probe`, `screws_tilt_adjust`, `exclude_object`.
- Firmware retraction.
- Dynamically discovered extruders, heaters, sensors, fans, filament sensors, pins, PWM tools, and LEDs.

KlipperTouch should implement subscription construction as a testable domain service.

## Navigation And Shell

`panels/base_panel.py` owns the persistent outer shell:

- Action bar with back, home, printer select, macro shortcut, emergency stop, and shutdown.
- Title bar with heater summaries, title, time, and battery state.
- Content slot where dynamically loaded panels are attached.
- Vertical mode moves the action bar below content; landscape mode places it on the left.

`screen.py` owns panel stack behavior:

- Panels are loaded dynamically from `panels/<name>.py`.
- The current panel hierarchy is logged.
- Existing panel instances can be reused or reinitialized.
- Panels can implement `process_update` and `activate`.

KlipperTouch should model this as a QML shell plus a Python navigation controller. Panel names should remain traceable to KlipperScreen names.

## Configuration Model

`ks_includes/config.py` uses `configparser` with default config, includes, user config, generated saved config, validation, and translation setup.

Important sections:

- `[main]`: printer defaults, language, theme, screen blanking, sizing, cursor, movement defaults, print estimate behavior.
- `[printer ...]`: Moonraker host, port, path, SSL, API key, axis inversion, titlebar items, movement and extrusion defaults.
- `[preheat ...]`: preheat targets and optional G-code.
- `[menu ...]`: configurable menu entries, panels, methods, params, enable conditions, confirmation text, and style.

KlipperTouch should load a compatible subset first and reject unknown or unsafe command entries when running in read-only mode.

## Panel Inventory

Local KlipperScreen panels include:

- Core daily-use panels: `main_menu`, `menu`, `move`, `temperature`, `extrude`, `gcodes`, `job_status`, `fine_tune`, `fan`.
- Printer and system panels: `printer_select`, `settings`, `system`, `network`, `power`, `shutdown`, `updater`.
- Calibration and tuning panels: `bed_mesh`, `bed_level`, `zcalibrate`, `input_shaper`, `limits`, `retraction`, `pressure_advance`, `exclude`.
- Extension panels: `camera`, `console`, `gcode_macros`, `led`, `notifications`, `pins`, `spoolman`.
- Startup and examples: `splash_screen`, `example`.

The first QML implementation phase should not attempt all panels. It should build the shell, data contracts, and read-only status surfaces before enabling control panels.

## Porting Principles

- Preserve behavior and information architecture before visual polish.
- Avoid direct Python-to-QML exposure of mutable raw dictionaries.
- Keep command methods separate from status methods.
- Make read-only mode enforceable in the Moonraker layer, not just hidden in QML.
- Treat Unicode names and custom macros as normal cases.
- Prefer fixtures captured from the real printer for reducer and UI model tests.

