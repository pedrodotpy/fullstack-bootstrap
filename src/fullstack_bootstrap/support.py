"""Install tailored agent support files into generated repositories."""

from __future__ import annotations

import shutil
from pathlib import Path

from fullstack_bootstrap.naming import ProjectNames
from fullstack_bootstrap.sources import package_data_root


class SupportError(RuntimeError):
    """Raised when agent support overlays cannot be installed."""


def install_support(backend_root: Path, frontend_root: Path, names: ProjectNames) -> None:
    """Copy specs, Cursor rules/skills, and repo-specific AGENTS.md into both repos."""
    data_root = package_data_root()
    specs_src = data_root / "specs"
    support_src = data_root / "support"
    if not specs_src.is_dir():
        raise SupportError(f"Missing packaged specs at {specs_src}")
    if not support_src.is_dir():
        raise SupportError(f"Missing packaged support at {support_src}")

    for root, kind in ((backend_root, "backend"), (frontend_root, "frontend")):
        _copy_tailored_specs(specs_src, root / "SPECS", names)
        _copy_cursor_support(support_src / "cursor", root / ".cursor", names)
        agents_template = support_src / "agents" / f"{kind}.md"
        if not agents_template.is_file():
            raise SupportError(f"Missing AGENTS overlay: {agents_template}")
        agents_text = _tailor_text(agents_template.read_text(encoding="utf-8"), names)
        (root / "AGENTS.md").write_text(agents_text, encoding="utf-8", newline="\n")


def _copy_tailored_specs(src: Path, dest: Path, names: ProjectNames) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    for path in sorted(src.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(src)
        target = dest / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        text = _tailor_text(path.read_text(encoding="utf-8"), names)
        target.write_text(text, encoding="utf-8", newline="\n")


def _copy_cursor_support(src: Path, dest: Path, names: ProjectNames) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    for path in sorted(src.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(src)
        target = dest / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix.lower() in {".md", ".mdc"}:
            text = _tailor_text(path.read_text(encoding="utf-8"), names)
            target.write_text(text, encoding="utf-8", newline="\n")
        else:
            shutil.copy2(path, target)


def _tailor_text(text: str, names: ProjectNames) -> str:
    """Rewrite boilerplate path/title tokens inside support/spec overlays."""
    updated = text
    replacements = (
        ("django-boilerplate", names.backend_repo),
        ("react-boilerplate", names.frontend_repo),
        ("Django Boilerplate API", names.api_title),
        ("Django Boilerplate", names.display_name),
        ("React Boilerplate", names.display_name),
        ("config.settings", f"{names.python_id}.settings"),
        ("config/settings", f"{names.python_id}/settings"),
        ("config/urls.py", f"{names.python_id}/urls.py"),
        ("config/", f"{names.python_id}/"),
        ("../SPECS/", "./SPECS/"),
        ("../SPECS", "./SPECS"),
        ("{{display_name}}", names.display_name),
        ("{{backend_repo}}", names.backend_repo),
        ("{{frontend_repo}}", names.frontend_repo),
        ("{{python_id}}", names.python_id),
        ("{{api_title}}", names.api_title),
        ("{{slug}}", names.slug),
    )
    for old, new in replacements:
        updated = updated.replace(old, new)
    return updated
