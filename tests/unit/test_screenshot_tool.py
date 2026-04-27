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
    assert '"notifications"' in source
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
    assert '"position_x": 10.1' in source
    assert '"homed_axes": "xyz"' in source
    assert '"cancelled"' in source
    assert '"paused"' in source
    assert '"complete"' in source
    assert '"error"' in source
    assert "setContextProperty(\"gcodeFileModel\"" in source
    assert "setContextProperty(\"statusModel\"" in source
    assert "OrcaCube_PLA_27m41s.gcode" in source
    assert "SAMPLE_METADATA" in source
    assert '"estimated_time": 1661.0' in source
    assert '"relative_path": ".thumbs/OrcaCube_PLA_27m41s-300x300.svg"' in source
    assert "_write_sample_thumbnail" in source
    assert "thumbnail_base = _write_sample_thumbnail(output_dir).as_uri()" in source
    assert "setFileMetadata" in source
    assert "write_index" in source
    assert "index.html" in source
    assert "--no-index" in source
    assert "--job-detail-pages" in source
    assert "--job-action-previews" in source
    assert "--file-detail-pages" in source
    assert "--file-action-previews" in source
    assert "JOB_DETAIL_PAGES" in source
    assert '"time"' in source
    assert '"motion"' in source
    assert '"extrusion"' in source
    assert "_set_job_status_detail_page" in source
    assert "_set_job_status_action_preview" in source
    assert "_set_files_detail_page" in source
    assert "_set_files_action_preview" in source
    assert 'panel.setProperty("detailPage", page)' in source
    assert 'panel.setProperty("pendingJobAction", action)' in source
    assert 'panel.setProperty("detailPage", page == "detail")' in source
    assert 'panel.setProperty("pendingFileAction", action)' in source
    assert 'f"{panel}_{detail_page}"' in source
