from klippertouch import __version__


def test_package_version_is_defined() -> None:
    assert __version__ == "0.1.0"


def test_runtime_depends_on_full_pyside6_for_qt_websockets() -> None:
    pyproject = __import__("pathlib").Path("pyproject.toml").read_text(encoding="utf-8")

    assert '"PySide6>=6.5"' in pyproject
    assert '"PySide6-Essentials>=6.5"' not in pyproject
