# Printer Read-Only Probe: 2026-04-23

Target: `orangepi@192.168.123.117`
Mode: read-only

## Commands Run

The probe used SSH and local Moonraker GET requests on the printer host. It did not send G-code, print-control commands, temperature commands, movement commands, restart commands, or service restarts.

Read-only checks performed:

- `hostname`
- `uname -a`
- `curl http://127.0.0.1:7125/server/info`
- `curl http://127.0.0.1:7125/printer/info`
- `curl http://127.0.0.1:7125/printer/objects/list`
- `systemctl is-active moonraker klipper`
- `ls ~/printer_data/logs`

## Environment

- Hostname: `orangepi3b`
- Kernel: `Linux orangepi3b 5.10.160-rockchip-rk356x #1.0.8 SMP Mon Nov 18 11:49:28 CST 2024 aarch64 GNU/Linux`
- Moonraker version: `v0.10.0-19-g1ed102e`
- Moonraker API version: `1.5.0`
- Klippy connected: `true`
- Klippy state: `ready`
- Klipper version: `v0.13.0-593-g2f05309d-dirty`
- Klipper state: `ready`
- Klipper config file: `/home/orangepi/printer_data/config/printer.cfg`
- Klipper log file: `/home/orangepi/printer_data/logs/klippy.log`
- `moonraker` service: active
- `klipper` service: active

## Moonraker Components

Moonraker reports these enabled components: `secrets`, `template`, `klippy_connection`, `jsonrpc`, `internal_transport`, `application`, `websockets`, `database`, `dbus_manager`, `file_manager`, `authorization`, `klippy_apis`, `shell_command`, `machine`, `data_store`, `proc_stats`, `job_state`, `job_queue`, `history`, `http_client`, `announcements`, `webcam`, `extensions`, `update_manager`, and `octoprint_compat`.

Registered directories: `config`, `logs`, `gcodes`, `config_examples`, and `docs`.

## Warnings

Moonraker reports update-manager warnings for missing Fluidd and KlipperScreen paths:

- `/home/orangepi/fluidd` does not exist.
- `/home/orangepi/KlipperScreen` does not exist.
- Several legacy or unparsed update-manager options remain in the Moonraker configuration.

These warnings do not block Klippy readiness, but they should be visible in any future diagnostics panel.

## Object Inventory Notes

The printer exposes standard objects and a non-trivial custom inventory:

- Multiple MCUs and CAN bus stats: `mcu`, `mcu EBB`, `mcu EZ`, `mcu cartographer`, `mcu afc`.
- Motion and print objects: `gcode_move`, `toolhead`, `motion_report`, `print_stats`, `virtual_sdcard`, `pause_resume`, `display_status`.
- Calibration objects: `bed_mesh`, `probe`, `cartographer`, `z_tilt`, `manual_probe`.
- Temperature objects: `extruder`, `heater_bed`, `heaters`, `temperature_sensor cartographer_coil`, `temperature_sensor cartographer`, `temperature_sensor E3`, `temperature_host FLY-π`, `temperature_sensor FLY-π`, `temperature_sensor Box`.
- Fans and LEDs: `fan`, `heater_fan hotend_fan`, `heater_fan hotend_fan1`, `controller_fan 驱动`, `heater_fan exhaust_fan`, `led my_led`.
- User macros include `CANCEL_PRINT`, `PAUSE`, `RESUME`, `UVW_*`, `Z_TILT_WITH_UVW_BASELINE`, and custom mode/homing helpers.

## Implementation Implications

- Unicode object names must be supported end-to-end.
- QML models must not assume English-only names.
- The device inventory should be discovered from `configfile.config` and object lists, not hardcoded.
- Macro display and execution must remain disabled during read-only mode.
- Diagnostics should surface Moonraker warnings without blocking connection.

