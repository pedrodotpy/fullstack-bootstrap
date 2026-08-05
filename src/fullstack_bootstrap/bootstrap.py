"""Orchestrate download → extract → render → support → git init."""

from __future__ import annotations

import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path

from fullstack_bootstrap.download import DownloadError, fetch_archive, sha256_file, verify_sha256
from fullstack_bootstrap.extract import ExtractError, extract_archive
from fullstack_bootstrap.gitutil import GitError, init_repository
from fullstack_bootstrap.naming import NamingError, ProjectNames, derive_names
from fullstack_bootstrap.render import RenderError, render_backend, render_frontend
from fullstack_bootstrap.sources import SourcesError, TemplateSources, load_sources
from fullstack_bootstrap.support import SupportError, install_support


@dataclass(frozen=True, slots=True)
class BootstrapResult:
    names: ProjectNames
    backend_path: Path
    frontend_path: Path


@dataclass(frozen=True, slots=True)
class LocalArchives:
    """Test/dev override: use pre-built zip files instead of downloading."""

    backend: Path
    frontend: Path
    backend_sha256: str | None = None
    frontend_sha256: str | None = None


class BootstrapError(RuntimeError):
    """Raised when bootstrap fails after naming succeeds."""


def bootstrap(
    client_name: str,
    *,
    output_dir: Path | None = None,
    sources: TemplateSources | None = None,
    archives: LocalArchives | None = None,
) -> BootstrapResult:
    """Create two branded sibling repositories from pinned (or local) archives.

    Parameters
    ----------
    client_name:
        Sole runtime parameter for the CLI (e.g. ``\"Acme Corp\"``).
    output_dir:
        Parent directory for the generated repos (default: cwd).
    sources:
        Optional pre-loaded template sources. Ignored when ``archives`` is set,
        except the CLI still loads/validates sources when archives are absent.
    archives:
        Optional local zip paths for tests. When provided, network download is skipped.
    """
    try:
        names = derive_names(client_name)
    except NamingError:
        raise

    parent = (output_dir or Path.cwd()).resolve()
    backend_dest = parent / names.backend_repo
    frontend_dest = parent / names.frontend_repo

    collisions = [p for p in (backend_dest, frontend_dest) if p.exists()]
    if collisions:
        joined = ", ".join(str(p) for p in collisions)
        raise BootstrapError(f"Refusing to overwrite existing path(s): {joined}")

    if archives is None:
        resolved_sources = sources or load_sources()
        try:
            resolved_sources.assert_configured()
        except SourcesError:
            raise
    else:
        resolved_sources = None

    staging = Path(tempfile.mkdtemp(prefix="fullstack-bootstrap-"))
    backend_stage = staging / "backend"
    frontend_stage = staging / "frontend"
    published = False
    try:
        backend_zip = staging / "backend.zip"
        frontend_zip = staging / "frontend.zip"

        if archives is not None:
            _stage_local_archive(archives.backend, backend_zip, archives.backend_sha256)
            _stage_local_archive(archives.frontend, frontend_zip, archives.frontend_sha256)
        else:
            assert resolved_sources is not None
            fetch_archive(resolved_sources.backend, backend_zip)
            fetch_archive(resolved_sources.frontend, frontend_zip)

        extract_archive(backend_zip, backend_stage)
        extract_archive(frontend_zip, frontend_stage)

        render_backend(backend_stage, names)
        render_frontend(frontend_stage, names)
        install_support(backend_stage, frontend_stage, names)

        # Atomic-ish publish: move staged trees into place, then init git.
        shutil.move(str(backend_stage), str(backend_dest))
        try:
            shutil.move(str(frontend_stage), str(frontend_dest))
        except Exception:
            shutil.rmtree(backend_dest, ignore_errors=True)
            raise
        published = True

        try:
            init_repository(backend_dest)
            init_repository(frontend_dest)
        except GitError:
            shutil.rmtree(backend_dest, ignore_errors=True)
            shutil.rmtree(frontend_dest, ignore_errors=True)
            raise

        return BootstrapResult(
            names=names,
            backend_path=backend_dest,
            frontend_path=frontend_dest,
        )
    except (DownloadError, ExtractError, RenderError, SupportError, SourcesError, GitError) as exc:
        if published:
            shutil.rmtree(backend_dest, ignore_errors=True)
            shutil.rmtree(frontend_dest, ignore_errors=True)
        raise BootstrapError(str(exc)) from exc
    finally:
        shutil.rmtree(staging, ignore_errors=True)


def _stage_local_archive(source: Path, destination: Path, expected_sha256: str | None) -> None:
    if not source.is_file():
        raise BootstrapError(f"Local archive not found: {source}")
    shutil.copy2(source, destination)
    if expected_sha256:
        verify_sha256(destination, expected_sha256)
    else:
        # Touch the helper so checksum tooling stays imported/used in tests.
        sha256_file(destination)
