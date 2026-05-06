# 1920x440 Ultrawide UI Design

## Goal
Adapt KlipperTouch for a 1920x440 11.3-inch touch display by making the UI use width instead of vertical stacking, while preserving reliable touch targets.

## Target Display
The target layout is landscape, 1920x440, with a very wide content area and limited vertical room. `Metrics.qml` already exposes `ultraWide` for landscape viewports with height at or below 520 and a width-to-height ratio of at least 3.0. This adaptation should build on that existing hook.

The available height after `StatusBar` is roughly three compact rows. Panels must avoid vertical flows that require users to scan or tap through many stacked rows.

## Layout Direction
Use the confirmed balanced three-column direction:

1. Left column: primary operation controls.
2. Middle column: status, graph, preview, or spatial visualization.
3. Right column: secondary controls, parameters, confirmation, or compact details.

Panels may use four columns only when the content is naturally tabular and each touch target can stay large enough. A four-column layout is acceptable for file metadata, job metrics, and fan/system lists, but not for motion or high-risk controls.

## Touch Rules
The ultrawide layout must keep touch targets practical for finger use:

- Normal tappable controls should be at least 48 px tall.
- Motion, extrusion, heating, print control, and restart-adjacent controls should target at least 56 px.
- Destructive or risky actions must keep existing confirmation behavior and should have larger visual weight than adjacent dismiss actions.
- Numeric chips can be compact, but the hit area must remain at least 44 px in the shorter axis.

Text must elide or wrap within fixed-height controls instead of growing the row. The ultrawide layout should not depend on font scaling with viewport width.

## Panel Requirements

### Shell
`BaseShell.qml` should keep the current left-side `ActionBar` and top `StatusBar` in ultrawide mode. The action bar should not grow to 10 percent of a 1920 px screen, because that wastes horizontal space; it should use a bounded width while keeping four large vertical buttons.

`Metrics.qml` should provide reusable ultrawide dimensions such as bounded action bar width, minimum touch size, safe touch size, compact row height, and panel column gap.

### Main Menu
The main menu should preserve the temperature summary but avoid a tall menu stack. In ultrawide mode, temperature summary and menu tiles should sit side by side. Menu tiles should use additional columns so the five current entries fit in two rows or fewer.

### Temperature
The temperature panel should use three horizontal regions in ultrawide mode: graph, device cards, and target controls or compact device actions. The graph should remain visible but not consume so much width that controls become narrow. Device controls should avoid pagination when two to four temperature devices are present.

### Move
The move panel already contains ultrawide-specific behavior and should be tightened rather than rewritten. The main screen should fit XY controls, Z controls, action controls, position feedback, and distance/speed choices on one page. Bed tilt can remain a detail page on smaller layouts, but in ultrawide mode it may be shown alongside the main movement controls when five-axis controls are available.

Movement controls must use the safer touch target size. Disabled or unavailable motion commands should remain visibly disabled with the existing guard text behavior.

### Extrude
The extrude panel should keep nozzle temperature, pressure advance, filament sensor status, feed setup, and extrusion actions visible on one ultrawide page. Length and speed selections should be displayed as horizontal or two-row chip groups instead of vertical lists. Load/unload and material-system controls should remain secondary to extrude/retract.

Extrusion must still respect the existing ready and can-extrude guards.

### Files
The files panel should use width to reduce mode switching. In ultrawide mode, the file list should remain visible while selected file details appear in a right-side detail column. Selecting a file should not force a full-page detail view on 1920x440.

Rows should be compact but remain easy to tap. Metadata should be grouped into small sections, with preview thumbnail and file actions in the detail column.

### Job Status
The job status panel should use a spacious minimalist design instead of an information-dense dashboard. In ultrawide mode, the primary screen should show only the most important print information:

- current layer / total layers
- estimated remaining time
- elapsed print time

Secondary metrics such as speed factor, extrusion factor, Z offset, position, acceleration, velocity, file metadata, and object details should stay out of the primary ultrawide job screen unless the user opens a detail view.

Print controls should use an icon-only, music-player-like control cluster. Buttons should rely on familiar icons such as pause, resume, cancel, skip, and clear instead of visible text labels. Touch targets must remain large enough for confident operation, and risky actions should still require confirmation.

Pause/resume, cancel, skip object, and clear behavior must keep current staged or confirmed action flow.

### More, Fans, Info, Notifications, Placeholders
Secondary list pages should prefer 3-4 columns in ultrawide mode and avoid long vertical stacks. Fan cards, system status rows, notification entries, and placeholder menu entries should use compact cards with fixed touch heights.

## Safety Boundaries
This work is layout adaptation only. It must not add new movement, heating, extrusion, print-control, restart, or raw G-code commands. Existing command guards and read-only defaults remain in force.

## Testing And Validation
Add QML structure tests for the ultrawide metrics and panel-specific layout hooks. Existing tests should continue to verify responsive orientation behavior.

Use the screenshot tool to capture at least these sizes:

- `1920x440`
- `800x480`
- `1024x600`
- `480x800`

The 1920x440 screenshots should be inspected for:

- no overlapping text or controls
- no primary panel requiring more than three vertical rows of controls
- job status primary view showing only layer, remaining time, elapsed time, and player-style icon controls
- touch targets matching the minimums above
- left action bar and top status bar still usable
- detail-heavy panels using width instead of forcing full-page drill-downs

Run `pytest`, `ruff`, `mypy`, and `git diff --check` before considering implementation complete.

## Out Of Scope
This design does not implement new KlipperScreen panels, new command capabilities, new theme art, or new real-printer behavior. It also does not replace existing portrait or 800x480 behavior; those layouts must remain functional.
