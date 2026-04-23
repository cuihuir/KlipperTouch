from dataclasses import dataclass
from datetime import datetime, timezone
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

    @property
    def modified_label(self) -> str:
        if self.modified <= 0:
            return "-"
        return datetime.fromtimestamp(self.modified, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")


@dataclass(frozen=True)
class GCodeFileEntry:
    path: str
    display_name: str
    is_directory: bool = False
    modified: float = 0.0
    size: int = 0
    permissions: str = ""

    @classmethod
    def directory(cls, path: str) -> "GCodeFileEntry":
        clean_path = _normalize_directory(path)
        return cls(path=clean_path, display_name=PurePosixPath(clean_path).name, is_directory=True)

    @classmethod
    def file(cls, file: GCodeFile) -> "GCodeFileEntry":
        return cls(
            path=file.path,
            display_name=file.display_name,
            modified=file.modified,
            size=file.size,
            permissions=file.permissions,
        )

    @property
    def size_label(self) -> str:
        if self.is_directory:
            return "Folder"
        return GCodeFile(
            path=self.path,
            display_name=self.display_name,
            modified=self.modified,
            size=self.size,
            permissions=self.permissions,
        ).size_label

    @property
    def modified_label(self) -> str:
        if self.is_directory:
            return "-"
        return GCodeFile(
            path=self.path,
            display_name=self.display_name,
            modified=self.modified,
            size=self.size,
            permissions=self.permissions,
        ).modified_label


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


def browser_entries_for_directory(
    files: tuple[GCodeFile, ...],
    directory: str = "",
    sort_key: str = "name",
    filter_text: str = "",
) -> tuple[GCodeFileEntry, ...]:
    current = _normalize_directory(directory)
    normalized_filter = filter_text.strip().casefold()
    directories: dict[str, GCodeFileEntry] = {}
    direct_files: list[GCodeFile] = []

    for file in files:
        path = PurePosixPath(file.path)
        parts = path.parts
        current_parts = PurePosixPath(current).parts if current else ()
        if parts[: len(current_parts)] != current_parts:
            continue
        remaining = parts[len(current_parts) :]
        if len(remaining) == 1:
            if _matches_filter(file.path, file.display_name, normalized_filter):
                direct_files.append(file)
        elif remaining:
            if normalized_filter and not _matches_filter(
                file.path,
                remaining[0],
                normalized_filter,
            ):
                continue
            child_path = str(PurePosixPath(current, remaining[0])) if current else remaining[0]
            directories[child_path] = GCodeFileEntry.directory(child_path)

    sorted_directories = tuple(
        sorted(directories.values(), key=lambda entry: entry.display_name.casefold())
    )
    sorted_files = tuple(
        GCodeFileEntry.file(file) for file in _sorted_files(direct_files, sort_key)
    )
    return sorted_directories + sorted_files


def _matches_filter(path: str, display_name: str, filter_text: str) -> bool:
    if not filter_text:
        return True
    return filter_text in path.casefold() or filter_text in display_name.casefold()


def _sorted_files(files: list[GCodeFile], sort_key: str) -> list[GCodeFile]:
    if sort_key == "date":
        return sorted(files, key=lambda file: (-file.modified, file.display_name.casefold()))
    if sort_key == "size":
        return sorted(files, key=lambda file: (-file.size, file.display_name.casefold()))
    return sorted(files, key=lambda file: file.display_name.casefold())


def _normalize_directory(path: str) -> str:
    clean = str(PurePosixPath(str(path).strip().strip("/")))
    return "" if clean == "." else clean


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
