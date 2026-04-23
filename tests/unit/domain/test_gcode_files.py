from klippertouch.domain.gcode_files import (
    GCodeFile,
    GCodeFileEntry,
    browser_entries_for_directory,
    files_from_moonraker,
)


def test_files_from_moonraker_normalizes_file_entries() -> None:
    files = files_from_moonraker(
        [
            {
                "path": "calibration/cube.gcode",
                "modified": 1710000000.5,
                "size": 2048,
                "permissions": "rw",
            },
            {"path": ""},
            "bad",
        ]
    )

    assert files == (
        GCodeFile(
            path="calibration/cube.gcode",
            display_name="cube.gcode",
            modified=1710000000.5,
            size=2048,
            permissions="rw",
        ),
    )
    assert files[0].size_label == "2.0 KB"


def test_browser_entries_for_directory_groups_immediate_dirs_and_files() -> None:
    files = (
        GCodeFile(path="cube.gcode", display_name="cube.gcode", modified=1710000100, size=2048),
        GCodeFile(path="calibration/flow.gcode", display_name="flow.gcode", size=4096),
        GCodeFile(path="calibration/pa/line.gcode", display_name="line.gcode", size=1024),
    )

    root_entries = browser_entries_for_directory(files)
    calibration_entries = browser_entries_for_directory(files, directory="calibration")

    assert root_entries == (
        GCodeFileEntry.directory(path="calibration"),
        GCodeFileEntry.file(files[0]),
    )
    assert calibration_entries == (
        GCodeFileEntry.directory(path="calibration/pa"),
        GCodeFileEntry.file(files[1]),
    )


def test_browser_entries_for_directory_sorts_files_by_name_date_or_size() -> None:
    files = (
        GCodeFile(path="b.gcode", display_name="b.gcode", modified=2, size=100),
        GCodeFile(path="a.gcode", display_name="a.gcode", modified=3, size=50),
    )

    assert [entry.display_name for entry in browser_entries_for_directory(files)] == [
        "a.gcode",
        "b.gcode",
    ]
    date_sorted = browser_entries_for_directory(files, sort_key="date")
    size_sorted = browser_entries_for_directory(files, sort_key="size")

    assert [entry.display_name for entry in date_sorted] == [
        "a.gcode",
        "b.gcode",
    ]
    assert [entry.display_name for entry in size_sorted] == [
        "b.gcode",
        "a.gcode",
    ]
