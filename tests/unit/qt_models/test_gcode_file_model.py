from PySide6.QtCore import Qt

from klippertouch.domain.gcode_files import GCodeFile
from klippertouch.qt_models.gcode_file_model import GCodeFileListModel


def test_gcode_file_list_model_exposes_qml_roles(qtbot) -> None:
    model = GCodeFileListModel()
    files = (
        GCodeFile(
            path="cube.gcode",
            display_name="cube.gcode",
            modified=1710000000.5,
            size=2048,
            permissions="rw",
        ),
    )

    with qtbot.waitSignal(model.modelReset, timeout=1000):
        model.set_files(files)

    roles = {bytes(value).decode(): key for key, value in model.roleNames().items()}
    first_index = model.index(0, 0)

    assert model.rowCount() == 1
    assert roles == {
        "path": Qt.ItemDataRole.UserRole + 1,
        "displayName": Qt.ItemDataRole.UserRole + 2,
        "sizeLabel": Qt.ItemDataRole.UserRole + 3,
        "modified": Qt.ItemDataRole.UserRole + 4,
        "permissions": Qt.ItemDataRole.UserRole + 5,
        "isDirectory": Qt.ItemDataRole.UserRole + 6,
        "modifiedLabel": Qt.ItemDataRole.UserRole + 7,
    }
    assert model.data(first_index, roles["path"]) == "cube.gcode"
    assert model.data(first_index, roles["displayName"]) == "cube.gcode"
    assert model.data(first_index, roles["sizeLabel"]) == "2.0 KB"
    assert model.data(first_index, roles["isDirectory"]) is False
    assert model.data(first_index, roles["modifiedLabel"]) == "2024-03-09 16:00"


def test_gcode_file_list_model_exposes_directory_entries_and_sorting(qtbot) -> None:
    model = GCodeFileListModel()
    files = (
        GCodeFile(path="cube.gcode", display_name="cube.gcode", modified=2, size=200),
        GCodeFile(path="calibration/flow.gcode", display_name="flow.gcode", modified=3, size=100),
    )

    with qtbot.waitSignal(model.modelReset, timeout=1000):
        model.set_files(files)

    roles = {bytes(value).decode(): key for key, value in model.roleNames().items()}
    assert model.currentPath == ""
    assert model.canGoUp is False
    assert model.rowCount() == 2
    assert model.data(model.index(0, 0), roles["isDirectory"]) is True
    assert model.data(model.index(0, 0), roles["displayName"]) == "calibration"

    with qtbot.waitSignal(model.currentPathChanged, timeout=1000):
        model.setCurrentPath("calibration")

    assert model.currentPath == "calibration"
    assert model.breadcrumbs == ["gcodes", "calibration"]
    assert model.canGoUp is True
    assert model.rowCount() == 1
    assert model.data(model.index(0, 0), roles["displayName"]) == "flow.gcode"

    with qtbot.waitSignal(model.sortKeyChanged, timeout=1000):
        model.setSortKey("size")

    assert model.sortKey == "size"

    with qtbot.waitSignal(model.currentPathChanged, timeout=1000):
        model.goUp()

    assert model.currentPath == ""
    assert model.breadcrumbs == ["gcodes"]
    assert model.canGoUp is False


def test_gcode_file_list_model_skips_reset_when_file_snapshot_is_unchanged(qtbot) -> None:
    model = GCodeFileListModel()
    files = (
        GCodeFile(path="cube.gcode", display_name="cube.gcode", modified=2, size=200),
    )
    model.set_files(files)
    resets: list[bool] = []
    model.modelReset.connect(lambda: resets.append(True))

    model.set_files(files)

    assert resets == []
    assert model.rowCount() == 1


def test_gcode_file_list_model_skips_reset_when_file_snapshot_order_changes(qtbot) -> None:
    model = GCodeFileListModel()
    files = (
        GCodeFile(path="cube.gcode", display_name="cube.gcode", modified=2, size=200),
        GCodeFile(path="calibration/flow.gcode", display_name="flow.gcode", modified=3, size=100),
    )
    model.set_files(files)
    resets: list[bool] = []
    model.modelReset.connect(lambda: resets.append(True))

    model.set_files(tuple(reversed(files)))

    assert resets == []
    assert model.rowCount() == 2


def test_gcode_file_list_model_filters_entries_and_navigates_breadcrumbs(qtbot) -> None:
    model = GCodeFileListModel()
    files = (
        GCodeFile(path="cube.gcode", display_name="cube.gcode", modified=2, size=200),
        GCodeFile(path="calibration/flow.gcode", display_name="flow.gcode", modified=3, size=100),
        GCodeFile(path="calibration/pa/line.gcode", display_name="line.gcode", size=100),
    )

    model.set_files(files)
    roles = {bytes(value).decode(): key for key, value in model.roleNames().items()}

    with qtbot.waitSignal(model.filterTextChanged, timeout=1000):
        model.setFilterText("cube")

    assert model.filterText == "cube"
    assert model.rowCount() == 1
    assert model.data(model.index(0, 0), roles["displayName"]) == "cube.gcode"

    with qtbot.waitSignal(model.filterTextChanged, timeout=1000):
        model.setFilterText("")
    with qtbot.waitSignal(model.currentPathChanged, timeout=1000):
        model.setCurrentPath("calibration/pa")

    assert model.breadcrumbs == ["gcodes", "calibration", "pa"]

    with qtbot.waitSignal(model.currentPathChanged, timeout=1000):
        model.setBreadcrumbIndex(1)

    assert model.currentPath == "calibration"
    assert model.breadcrumbs == ["gcodes", "calibration"]

    with qtbot.waitSignal(model.currentPathChanged, timeout=1000):
        model.setBreadcrumbIndex(0)

    assert model.currentPath == ""


def test_gcode_file_list_model_skips_reset_for_equivalent_current_path(qtbot) -> None:
    model = GCodeFileListModel()
    model.set_files(
        (
            GCodeFile(path="calibration/flow.gcode", display_name="flow.gcode", size=100),
        )
    )
    model.setCurrentPath("calibration")
    resets: list[bool] = []
    path_changes: list[bool] = []
    model.modelReset.connect(lambda: resets.append(True))
    model.currentPathChanged.connect(lambda: path_changes.append(True))

    model.setCurrentPath("/calibration/")

    assert resets == []
    assert path_changes == []
    assert model.currentPath == "calibration"


def test_gcode_file_list_model_returns_metadata_for_print_filename() -> None:
    model = GCodeFileListModel()
    model.set_files(
        (
            GCodeFile(
                path="calibration/cube.gcode",
                display_name="cube.gcode",
                modified=1710000000.5,
                size=2048,
                permissions="rw",
            ),
        )
    )

    assert model.fileSizeLabelFor("calibration/cube.gcode") == "2.0 KB"
    assert model.fileSizeLabelFor("cube.gcode") == "2.0 KB"
    assert model.fileModifiedLabelFor("cube.gcode") == "2024-03-09 16:00"
    assert model.filePathFor("cube.gcode") == "calibration/cube.gcode"
    assert model.fileSizeLabelFor("missing.gcode") == "-"


def test_gcode_file_list_model_tracks_read_only_selected_file(qtbot) -> None:
    model = GCodeFileListModel()
    model.set_files(
        (
            GCodeFile(
                path="calibration/cube.gcode",
                display_name="cube.gcode",
                modified=1710000000.5,
                size=2048,
                permissions="rw",
            ),
            GCodeFile(path="calibration", display_name="calibration", size=0),
        )
    )

    with qtbot.waitSignal(model.selectedPathChanged, timeout=1000):
        model.selectPath("calibration/cube.gcode", False)

    assert model.selectedPath == "calibration/cube.gcode"
    assert model.selectedDisplayName == "cube.gcode"
    assert model.selectedSizeLabel == "2.0 KB"
    assert model.selectedModifiedLabel == "2024-03-09 16:00"
    assert model.selectedPermissions == "rw"

    model.selectPath("calibration", True)

    assert model.selectedPath == "calibration/cube.gcode"

    with qtbot.waitSignal(model.selectedPathChanged, timeout=1000):
        model.clearSelection()

    assert model.selectedPath == ""
    assert model.selectedDisplayName == ""


def test_gcode_file_list_model_clears_selected_file_when_snapshot_removes_it(qtbot) -> None:
    model = GCodeFileListModel()
    model.set_files(
        (
            GCodeFile(path="cube.gcode", display_name="cube.gcode", size=2048),
        )
    )
    model.selectPath("cube.gcode", False)

    with qtbot.waitSignal(model.selectedPathChanged, timeout=1000):
        model.set_files(())

    assert model.selectedPath == ""
    assert model.selectedSizeLabel == "-"
