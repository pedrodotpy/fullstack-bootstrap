"""Archive extraction and checksum safety tests."""

from __future__ import annotations

import hashlib
import zipfile
from pathlib import Path

import pytest

from fullstack_bootstrap.download import DownloadError, verify_sha256
from fullstack_bootstrap.extract import ExtractError, extract_archive
from tests.helpers import backend_fixture_files, write_zip


def test_extract_strips_root_and_skips_local_artifacts(tmp_path: Path) -> None:
    archive = write_zip(tmp_path / "backend.zip", backend_fixture_files(), root_prefix="django-boilerplate-abc")
    dest = tmp_path / "out"
    root = extract_archive(archive, dest)

    assert (root / "manage.py").is_file()
    assert (root / "config" / "settings" / "base.py").is_file()
    assert not (root / ".venv").exists()
    assert not (root / "db.sqlite3").exists()
    assert not (root / ".env").exists()
    assert not (root / "config" / "settings" / "local.py").exists()
    assert (root / "config" / "settings" / "local.py.example").is_file()


def test_extract_rejects_path_traversal(tmp_path: Path) -> None:
    archive = tmp_path / "evil.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("../escape.txt", "nope")
    with pytest.raises(ExtractError, match="unsafe"):
        extract_archive(archive, tmp_path / "out")


def test_extract_rejects_symlink(tmp_path: Path) -> None:
    archive = tmp_path / "link.zip"
    info = zipfile.ZipInfo("project/link")
    info.create_system = 3
    info.external_attr = 0o120777 << 16
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr(info, "target")
    with pytest.raises(ExtractError, match="symlink"):
        extract_archive(archive, tmp_path / "out")


def test_verify_sha256_mismatch(tmp_path: Path) -> None:
    path = tmp_path / "file.bin"
    path.write_bytes(b"hello")
    with pytest.raises(DownloadError, match="Checksum mismatch"):
        verify_sha256(path, "0" * 64)


def test_verify_sha256_ok(tmp_path: Path) -> None:
    path = tmp_path / "file.bin"
    data = b"hello"
    path.write_bytes(data)
    digest = hashlib.sha256(data).hexdigest()
    verify_sha256(path, digest)
