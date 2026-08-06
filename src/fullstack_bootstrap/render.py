"""Manifest-driven path/content rendering for extracted boilerplates."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from fullstack_bootstrap.naming import ProjectNames

# Files whose contents are rewritten (Vinta-style extension/basename allowlist).
RENDER_EXTENSIONS = frozenset(
    {
        ".py",
        ".pyi",
        ".toml",
        ".json",
        ".yml",
        ".yaml",
        ".md",
        ".mdc",
        ".ts",
        ".tsx",
        ".js",
        ".jsx",
        ".html",
        ".css",
        ".txt",
        ".example",
        ".env",
        ".sh",
    }
)
RENDER_BASENAMES = frozenset(
    {
        "Makefile",
        "Dockerfile",
        ".gitignore",
        ".dockerignore",
        ".env.example",
        ".npmrc",
        ".python-version",
        "AGENTS.md",
        "README.md",
        "uv.lock",
    }
)

# Paths that must never be content-rewritten (generated API client).
SKIP_CONTENT_PREFIXES = (
    "src/shared/api/",
)

BINARY_SUFFIXES = frozenset(
    {
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".webp",
        ".ico",
        ".woff",
        ".woff2",
        ".ttf",
        ".eot",
        ".zip",
        ".gz",
        ".whl",
        ".pyc",
    }
)


@dataclass(frozen=True, slots=True)
class Replacement:
    old: str
    new: str
    min_count: int = 0


class RenderError(RuntimeError):
    """Raised when branding/rendering fails or leaves residual template tokens."""


def render_backend(root: Path, names: ProjectNames) -> None:
    """Apply backend branding, including Django package rename ``config`` → python_id."""
    config_dir = root / "config"
    if not config_dir.is_dir():
        raise RenderError(f"Backend template missing config/ package at {config_dir}")

    target_dir = root / names.python_id
    if target_dir.exists():
        raise RenderError(f"Cannot rename config/ — destination exists: {target_dir}")
    config_dir.rename(target_dir)

    replacements = _backend_replacements(names)
    _rewrite_tree(root, replacements, repo_kind="backend")
    _assert_no_residuals(root, _backend_forbidden_residuals(names), repo_kind="backend")


def render_frontend(root: Path, names: ProjectNames) -> None:
    """Apply frontend branding and sibling-path rewrites."""
    replacements = _frontend_replacements(names)
    _rewrite_tree(root, replacements, repo_kind="frontend")
    _brand_ui_titles(root, names)
    _assert_no_residuals(root, _frontend_forbidden_residuals(names), repo_kind="frontend")


def _backend_replacements(names: ProjectNames) -> list[Replacement]:
    return [
        Replacement("Django Boilerplate API", names.api_title, min_count=1),
        Replacement("Django Boilerplate", names.display_name, min_count=1),
        Replacement("django-boilerplate", names.backend_repo, min_count=1),
        Replacement("react-boilerplate", names.frontend_repo, min_count=0),
        Replacement("config.settings", f"{names.python_id}.settings", min_count=1),
        Replacement('"config.urls"', f'"{names.python_id}.urls"', min_count=1),
        Replacement('"config.wsgi.application"', f'"{names.python_id}.wsgi.application"', min_count=1),
        Replacement("config/settings", f"{names.python_id}/settings", min_count=0),
        Replacement("config/urls.py", f"{names.python_id}/urls.py", min_count=0),
        Replacement("../SPECS/", "./SPECS/", min_count=0),
        Replacement("../SPECS", "./SPECS", min_count=0),
    ]


def _frontend_replacements(names: ProjectNames) -> list[Replacement]:
    return [
        Replacement("React Boilerplate", names.display_name, min_count=1),
        Replacement("react-boilerplate", names.frontend_repo, min_count=1),
        Replacement("django-boilerplate", names.backend_repo, min_count=1),
        Replacement("../SPECS/", "./SPECS/", min_count=0),
        Replacement("../SPECS", "./SPECS", min_count=0),
    ]


def _backend_forbidden_residuals(names: ProjectNames) -> tuple[str, ...]:
    del names
    return (
        "django-boilerplate",
        "Django Boilerplate",
        "react-boilerplate",
        "config.settings",
        '"config.urls"',
        '"config.wsgi.application"',
        "UNSET",
        "{{project_name}}",
    )


def _frontend_forbidden_residuals(names: ProjectNames) -> tuple[str, ...]:
    del names
    return (
        "django-boilerplate",
        "react-boilerplate",
        "React Boilerplate",
        "Django Boilerplate",
        "UNSET",
        "{{project_name}}",
    )


def _rewrite_tree(root: Path, replacements: Iterable[Replacement], *, repo_kind: str) -> None:
    counts = {item.old: 0 for item in replacements}
    for path in _iter_text_files(root):
        relative = path.relative_to(root).as_posix()
        if any(relative.startswith(prefix) for prefix in SKIP_CONTENT_PREFIXES):
            continue
        if not _should_render(path):
            continue

        original = path.read_text(encoding="utf-8")
        updated = original
        for item in replacements:
            if item.old in updated:
                occurrences = updated.count(item.old)
                updated = updated.replace(item.old, item.new)
                counts[item.old] += occurrences
        if updated != original:
            path.write_text(updated, encoding="utf-8", newline="\n")

    for item in replacements:
        if counts[item.old] < item.min_count:
            raise RenderError(
                f"{repo_kind}: expected at least {item.min_count} occurrence(s) of "
                f"{item.old!r}, found {counts[item.old]}. Template may have drifted."
            )


def _brand_ui_titles(root: Path, names: ProjectNames) -> None:
    """Replace the visible product title ``App`` in known UI locations only."""
    targets = (
        (root / "index.html", "<title>App</title>", f"<title>{names.display_name}</title>"),
        (
            root / "src" / "shared" / "layout" / "AppShell.tsx",
            "\n              App\n",
            f"\n              {names.display_name}\n",
        ),
        (
            root / "src" / "features" / "auth" / "pages" / "LoginPage.tsx",
            "\n            App\n",
            f"\n            {names.display_name}\n",
        ),
    )
    for path, old, new in targets:
        if not path.is_file():
            raise RenderError(f"Frontend branding target missing: {path}")
        text = path.read_text(encoding="utf-8")
        if old not in text:
            raise RenderError(
                f"Frontend branding token {old!r} missing in {path.relative_to(root)}"
            )
        path.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")


def _assert_no_residuals(root: Path, tokens: Iterable[str], *, repo_kind: str) -> None:
    forbidden = [token for token in tokens if token]
    offenders: list[str] = []
    for path in _iter_text_files(root):
        relative = path.relative_to(root).as_posix()
        if any(relative.startswith(prefix) for prefix in SKIP_CONTENT_PREFIXES):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for token in forbidden:
            if token in text:
                offenders.append(f"{relative}: contains {token!r}")
                break
    if offenders:
        preview = "\n".join(offenders[:20])
        raise RenderError(
            f"{repo_kind}: residual template tokens remain after rendering:\n{preview}"
        )


def _should_render(path: Path) -> bool:
    if path.suffix.lower() in BINARY_SUFFIXES:
        return False
    if path.name in RENDER_BASENAMES:
        return True
    if path.suffix.lower() in RENDER_EXTENSIONS:
        return True
    # Allowlist bare env example names already covered; skip unknown binaries.
    return False


def _iter_text_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() in BINARY_SUFFIXES:
            continue
        files.append(path)
    return files
