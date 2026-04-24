from pathlib import Path


def test_screenshot_tool_captures_common_panels_and_sizes() -> None:
    source = Path("tools/capture_qml_screenshots.py").read_text(encoding="utf-8")

    assert "DEFAULT_SIZES = " in source
    assert '"800x480"' in source
    assert '"1024x600"' in source
    assert '"480x800"' in source
    assert "DEFAULT_PANELS = " in source
    assert '"print"' in source
    assert '"more"' in source
    assert '"system"' in source
    assert '"network"' in source
    assert '"logs"' in source
    assert '"language"' in source
    assert '"update"' in source
    assert '"job_status"' in source
    assert "root.grabWindow()" in source
    assert "QT_QPA_PLATFORM" in source
    assert "artifacts/screenshots" in source
    assert "--sample-files" in source
    assert "--sample-status" in source
    assert "--sample-state" in source
    assert "create_gcode_file_model" in source
    assert "create_status_models" in source
    assert "SAMPLE_STATUS" in source
    assert '"hostname": "orangepi3b"' in source
    assert '"print_state": "printing"' in source
    assert '"cancelled"' in source
    assert '"paused"' in source
    assert '"complete"' in source
    assert '"error"' in source
    assert "setContextProperty(\"gcodeFileModel\"" in source
    assert "setContextProperty(\"statusModel\"" in source
    assert "OrcaCube_PLA_27m41s.gcode" in source
    assert "write_index" in source
    assert "index.html" in source
    assert "--no-index" in source
