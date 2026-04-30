# Real Printer Read-Only Probe - 2026-04-30

Validation time: 2026-04-30 11:45 CST

Configuration: local `config/KlipperTouch.conf`, default printer pointing at the FRP
Moonraker endpoint for the Orange Pi test environment.

Commands used:

```bash
UV_INDEX_URL=https://pypi.org/simple uv run --locked python -m klippertouch --probe
```

Additional read-only checks used `MoonrakerClient.get_gcode_file_list()` and
`MoonrakerClient.get_gcode_file_metadata()` from the configured endpoint. No motion,
heating, extrusion, print-control, delete, restart, or emergency commands were sent.

Observed state:

- Klippy state: `ready`
- Hostname: `orangepi3b`
- Klipper version: `v0.13.0-593-g2f05309d5-dirty`
- Moonraker version: `v0.10.0-19-g1ed102e`
- Five-axis capability flags: `five_axis_available=true`,
  `accelerator_level_available=true`, `z_tilt_available=true`
- Warnings are readable from both Moonraker and Klipper, including the
  `cartographer` deprecated-code warning.

G-code file validation:

- File list returned 3 files.
- `fiveaxis_y_tube15_linear_flat_h100_lowfork.gcode` has metadata but no thumbnails.
- `OrcaCube_PLA_27m41s.gcode` and `OrcaCube_PLA_27m50s.gcode` each expose 32x32 and
  300x300 thumbnails.
- Generated thumbnail URLs for the OrcaCube file returned `200 image/png` for both
  small and preview images.

Implications:

- Files/Print lazy metadata and thumbnail selection match the live Moonraker data.
- Missing thumbnails for the five-axis file are source-data behavior, not a GUI URL
  construction failure.
