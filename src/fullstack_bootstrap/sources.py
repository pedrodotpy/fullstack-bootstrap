"""Locate packaged data files and resolve template source pins."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

UNSET = "UNSET"


@dataclass(frozen=True, slots=True)
class TemplateSource:
    """Pinned archive location for one boilerplate repository."""

    name: str
    url: str
    commit: str
    sha256: str

    def assert_configured(self) -> None:
        missing = [
            field
            for field, value in (
                ("url", self.url),
                ("commit", self.commit),
                ("sha256", self.sha256),
            )
            if not value or value == UNSET
        ]
        if missing:
            raise SourcesError(
                f"Template source [{self.name}] is not configured "
                f"(unset: {', '.join(missing)}). "
                "Edit template-sources.toml with published archive URL, "
                "immutable commit SHA, and SHA-256 checksum."
            )


@dataclass(frozen=True, slots=True)
class TemplateSources:
    backend: TemplateSource
    frontend: TemplateSource

    def assert_configured(self) -> None:
        self.backend.assert_configured()
        self.frontend.assert_configured()


class SourcesError(ValueError):
    """Raised when template source configuration is missing or invalid."""


def package_data_root() -> Path:
    """Return the directory that holds packaged specs, support, and sources.

    During editable/dev checkouts this prefers the repository root so edits to
    ``specs/`` and ``support/`` are picked up without rebuilding the wheel.
    """
    repo_root = Path(__file__).resolve().parents[2]
    if (repo_root / "template-sources.toml").is_file() and (repo_root / "specs").is_dir():
        return repo_root

    installed = Path(__file__).resolve().parent / "data"
    if (installed / "template-sources.toml").is_file():
        return installed

    raise SourcesError(
        "Could not locate fullstack-bootstrap data files "
        "(template-sources.toml / specs / support)."
    )


def default_sources_path() -> Path:
    return package_data_root() / "template-sources.toml"


def load_sources(path: Path | None = None) -> TemplateSources:
    """Load and validate template-sources.toml structure (placeholders allowed)."""
    sources_path = path or default_sources_path()
    if not sources_path.is_file():
        raise SourcesError(f"Template sources file not found: {sources_path}")

    with sources_path.open("rb") as handle:
        raw = tomllib.load(handle)

    backend = _parse_source("backend", raw.get("backend"))
    frontend = _parse_source("frontend", raw.get("frontend"))
    return TemplateSources(backend=backend, frontend=frontend)


def _parse_source(name: str, section: object) -> TemplateSource:
    if not isinstance(section, dict):
        raise SourcesError(f"Missing [{name}] section in template-sources.toml")
    try:
        url = str(section["url"]).strip()
        commit = str(section["commit"]).strip()
        sha256_raw = str(section["sha256"]).strip()
    except KeyError as exc:
        raise SourcesError(f"[{name}] missing required key: {exc.args[0]}") from exc
    sha256 = sha256_raw if sha256_raw == UNSET else sha256_raw.lower()
    return TemplateSource(name=name, url=url, commit=commit, sha256=sha256)
