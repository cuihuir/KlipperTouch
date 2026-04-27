# Job Status Redesign Design

## Goal
Make `JobStatusPanel.qml` feel like a coherent consumer-facing print status screen instead of a grid of unrelated tappable metrics.

## Root Cause
The current panel maps individual metrics directly to detail pages. `Elapsed`, `Remaining`, `Layer`, `Speed`, `Flow`, and `Z offset` all look like peer actions, so users cannot distinguish primary status, print controls, and secondary information.

KlipperScreen uses a clearer model: one primary job status area, a small set of print actions, and a status grid where a few semantic areas open secondary detail views. KlipperTouch should follow that hierarchy while keeping QML layouts responsive.

## Information Architecture
The summary screen has four visual regions:

1. Hero region: file name, print state, thumbnail, progress, remaining time, and compact tuning values.
2. Action region: `Pause/Resume`, `Cancel`, `Skip Object`, and `Advanced`.
3. Summary zones: `Time`, `Motion`, and `Material`, where each zone is one tappable detail entry.
4. Temperature strip: visible only where space allows and backed by the existing temperature model.

Individual values inside summary zones are not separate navigation controls.

## Detail Pages
`Time`, `Motion`, and `Material` keep the existing read-only detail data. `Advanced` remains the only tuning page for `Z offset`, `Speed factor`, and `Extrude factor`. `Skip Object` remains an explicit entry to the object exclusion page. All child pages use the global back button.

## Safety
Print-control commands stay read-only or staged. This change must not add movement, heating, extrusion, print control, restart, or G-code execution calls.

## Validation
Add QML structure tests that reject per-metric navigation and require the three grouped summary zones. Capture screenshots for `800x480`, `480x800`, `1024x600`, and `1920x440`, then run `pytest`, `ruff`, `mypy`, and `git diff --check`.
