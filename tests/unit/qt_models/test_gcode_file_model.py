from PySide6.QtCore import Qt

from klippertouch.domain.gcode_files import GCodeFile
from klippertouch.qt_models.gcode_file_model import GCodeFileListModel


def test_gcode_file_list_model_exposes_qml_roles(qtbot) -> None:
    model = GCodeFileListModel()
    files = (
        GCodeFile(
            path="calibration/cube.gcode",
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
    }
    assert model.data(first_index, roles["path"]) == "calibration/cube.gcode"
    assert model.data(first_index, roles["displayName"]) == "cube.gcode"
    assert model.data(first_index, roles["sizeLabel"]) == "2.0 KB"
