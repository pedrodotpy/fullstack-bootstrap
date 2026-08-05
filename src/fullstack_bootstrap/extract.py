"""Secure zip extraction with path traversal and symlink rejection."""

from __future__ import annotations

import stat
import zipfile
from pathlib import Path, PurePosixPath


class ExtractError(RuntimeError):
    """Raised when an archive cannot be extracted safely."""


SKIP_DIR_NAMES = frozenset(
    {
        ".git",
        ".venv",
        "node_modules",
        "__pycache__",
        ".pytest_cache",
        "dist",
        "test-results",
        "playwright-report",
        "blob-report",
        ".mypy_cache",
        ".ruff_cache",
        ".tox",
    }
)

SKIP_FILE_NAMES = frozenset(
    {
        ".env",
        "db.sqlite3",
        ".DS_Store",
    }
)


def should_skip_relative(relative: PurePosixPath) -> bool:
    """Return True when a relative archive path should be omitted."""
    parts = relative.parts
    if any(part in SKIP_DIR_NAMES for part in parts):
        return True
    name = relative.name
    if name in SKIP_FILE_NAMES:
        return True
    if name == "local.py" and relative.parts[-2:] == ("settings", "local.py"):
        return True
    if name.endswith(".pyc") or name.endswith(".pyo"):
        return True
    if name == ".gitkeep":
        return False
    return False


def extract_archive(archive: Path, destination: Path) -> Path:
    """Extract ``archive`` into ``destination`` and return the project root.

    GitHub-style zips wrap contents in a single top-level directory; that wrapper
    is stripped. Symlinks and path traversal are rejected.
    """
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as zf:
        members = [info for info in zf.infolist() if info.filename and not info.filename.endswith("/")]
        if not members:
            raise ExtractError(f"Archive is empty: {archive}")

        root_prefix = _detect_single_root(zf.namelist())
        written: list[Path] = []

        for info in sorted(members, key=lambda item: item.filename):
            if _is_symlink(info):
                raise ExtractError(f"Refusing symlink in archive: {info.filename}")

            relative = _safe_relative(info.filename, root_prefix)
            if should_skip_relative(relative):
                continue

            target = destination.joinpath(*relative.parts)
            try:
                target.resolve().relative_to(destination.resolve())
            except ValueError as exc:
                raise ExtractError(f"Refusing path escape: {info.filename}") from exc

            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(info, "r") as src, target.open("wb") as out:
                out.write(src.read())

            # Normalize executable bit from zip external attrs when present.
            mode = (info.external_attr >> 16) & 0o777
            if mode & stat.S_IXUSR:
                target.chmod(0o755)
            else:
                target.chmod(0o644)
            written.append(target)

        if not written:
            raise ExtractError(f"Archive produced no files after filtering: {archive}")

    return destination


def _detect_single_root(names: list[str]) -> str | None:
    tops = {name.split("/", 1)[0] for name in names if name and name != "/"}
    # Ignore macOS metadata directory when detecting the project root.
    tops.discard("__MACOSX")
    if len(tops) == 1:
        root = next(iter(tops))
        # Only strip if everything lives under that directory.
        if all(n == root or n.startswith(root + "/") or n.startswith("__MACOSX/") for n in names if n):
            return root
    return None


def _safe_relative(filename: str, root_prefix: str | None) -> PurePosixPath:
    posix = PurePosixPath(filename)
    if posix.is_absolute() or ".." in posix.parts:
        raise ExtractError(f"Refusing unsafe archive path: {filename}")
    if root_prefix and (filename == root_prefix or filename.startswith(root_prefix + "/")):
        stripped = filename[len(root_prefix) :].lstrip("/")
        if not stripped:
            raise ExtractError(f"Refusing empty path after stripping root: {filename}")
        posix = PurePosixPath(stripped)
        if posix.is_absolute() or ".." in posix.parts:
            raise ExtractError(f"Refusing unsafe archive path: {filename}")
    if posix.parts and posix.parts[0] == "__MACOSX":
        raise ExtractError(f"Unexpected macOS metadata path: {filename}")
    return posix


def _is_symlink(info: zipfile.ZipInfo) -> bool:
    # Unix symlink: high bytes of external_attr include S_IFLNK (0o120000).
    return ((info.external_attr >> 16) & 0o170000) == 0o120000
