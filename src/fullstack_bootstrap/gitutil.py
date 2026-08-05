"""Git repository initialization helpers."""

from __future__ import annotations

import subprocess
from pathlib import Path


class GitError(RuntimeError):
    """Raised when git initialization fails."""


def init_repository(path: Path) -> None:
    """Initialize a new Git repository on branch ``main`` without committing."""
    try:
        subprocess.run(
            ["git", "init", "-b", "main"],
            cwd=path,
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise GitError("git executable not found on PATH") from exc
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "").strip()
        raise GitError(f"git init failed in {path}: {detail}") from exc
