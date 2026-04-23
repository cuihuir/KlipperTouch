from klippertouch.domain.gcode_files import GCodeFile, files_from_moonraker


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
