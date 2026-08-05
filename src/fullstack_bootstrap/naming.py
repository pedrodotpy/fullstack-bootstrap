"""Derive stable project identity values from a single client name."""

from __future__ import annotations

import re
from dataclasses import dataclass

_SLUG_RE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
_WHITESPACE_RE = re.compile(r"\s+")
_INVALID_CHARS_RE = re.compile(r"[^a-z0-9]+")


@dataclass(frozen=True, slots=True)
class ProjectNames:
    """All derived names for one client bootstrap."""

    display_name: str
    slug: str
    python_id: str
    backend_repo: str
    frontend_repo: str
    api_title: str


class NamingError(ValueError):
    """Raised when a client name cannot be converted into a safe project identity."""


def derive_names(client_name: str) -> ProjectNames:
    """Derive slug, Python identifier, and repo names from ``client_name``.

    Examples
    --------
    ``"Acme Corp"`` → slug ``acme-corp``, python ``acme_corp``,
    repos ``acme-corp-backend`` / ``acme-corp-frontend``.
    """
    display_name = _WHITESPACE_RE.sub(" ", client_name.strip())
    if not display_name:
        raise NamingError("Client name must not be empty.")

    slug = _INVALID_CHARS_RE.sub("-", display_name.lower()).strip("-")
    slug = re.sub(r"-{2,}", "-", slug)
    if not slug or not _SLUG_RE.fullmatch(slug):
        raise NamingError(
            f"Client name {client_name!r} does not produce a valid slug. "
            "Use letters/numbers (optionally separated by spaces or hyphens), "
            "starting with a letter."
        )

    python_id = slug.replace("-", "_")
    if python_id.isidentifier() is False or python_id[0].isdigit():
        raise NamingError(
            f"Derived Python package name {python_id!r} is not a valid identifier."
        )

    return ProjectNames(
        display_name=display_name,
        slug=slug,
        python_id=python_id,
        backend_repo=f"{slug}-backend",
        frontend_repo=f"{slug}-frontend",
        api_title=f"{display_name} API",
    )
