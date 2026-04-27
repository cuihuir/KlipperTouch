from pathlib import Path


def test_control_smoke_tool_requires_explicit_control_flag() -> None:
    source = Path("tools/control_smoke.py").read_text(encoding="utf-8")

    assert "--allow-controls" in source
    assert "CommandPolicy(read_only=False)" in source
    assert "upload_gcode_file" in source
    assert "delete_gcode_file" in source
    assert "clear_sdcard_file" in source
    assert "start_print" in source
    assert "cancel_print" in source
