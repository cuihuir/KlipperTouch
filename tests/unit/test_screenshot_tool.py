from pathlib import Path


def test_screenshot_tool_captures_common_panels_and_sizes() -> None:
    source = Path("tools/capture_qml_screenshots.py").read_text(encoding="utf-8")

    assert "DEFAULT_SIZES = " in source
    assert '"800x480"' in source
    assert '"1024x600"' in source
    assert '"480x800"' in source
    assert "DEFAULT_PANELS = " in source
    assert '"print"' in source
    assert '"job_status"' in source
    assert "root.grabWindow()" in source
    assert "QT_QPA_PLATFORM" in source
    assert "artifacts/screenshots" in source
