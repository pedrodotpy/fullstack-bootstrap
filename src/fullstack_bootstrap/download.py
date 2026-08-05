"""Download pinned template archives and verify checksums."""

from __future__ import annotations

import hashlib
import urllib.error
import urllib.request
from pathlib import Path

from fullstack_bootstrap.sources import TemplateSource


class DownloadError(RuntimeError):
    """Raised when an archive cannot be downloaded or fails checksum verification."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def verify_sha256(path: Path, expected: str) -> None:
    actual = sha256_file(path)
    if actual != expected.lower():
        raise DownloadError(
            f"Checksum mismatch for {path.name}: expected {expected}, got {actual}"
        )


def fetch_archive(source: TemplateSource, destination: Path) -> Path:
    """Download ``source.url`` to ``destination`` and verify SHA-256."""
    source.assert_configured()
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        urllib.request.urlretrieve(source.url, destination)  # noqa: S310 — pinned URL from config
    except urllib.error.URLError as exc:
        raise DownloadError(f"Failed to download {source.name} archive: {exc}") from exc
    except OSError as exc:
        raise DownloadError(f"Failed to write {source.name} archive: {exc}") from exc

    verify_sha256(destination, source.sha256)
    return destination
