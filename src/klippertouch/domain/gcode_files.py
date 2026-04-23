from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Any


@dataclass(frozen=True)
class GCodeFile:
    path: str
    display_name: str
    modified: float = 0.0
    size: int = 0
    permissions: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "path", str(self.path))
        object.__setattr__(self, "display_name", str(self.display_name))
        object.__setattr__(self, "modified", float(self.modified))
        object.__setattr__(self, "size", max(0, int(self.size)))
        object.__setattr__(self, "permissions", str(self.permissions))

    @property
    def size_label(self) -> str:
        if self.size < 1024:
            return f"{self.size} B"
        if self.size < 1024 * 1024:
            return f"{self.size / 1024:.1f} KB"
        return f"{self.size / (1024 * 1024):.1f} MB"


def files_from_moonraker(items: Any) -> tuple[GCodeFile, ...]:
    if not isinstance(items, list):
        return ()

    files: list[GCodeFile] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        path = str(item.get("path", "")).strip()
        if not path:
            continue
        files.append(
            GCodeFile(
                path=path,
                display_name=PurePosixPath(path).name,
                modified=_float_or_default(item.get("modified")),
                size=_int_or_default(item.get("size")),
                permissions=str(item.get("permissions", "")),
            )
        )
    return tuple(files)


def _float_or_default(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _int_or_default(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0
