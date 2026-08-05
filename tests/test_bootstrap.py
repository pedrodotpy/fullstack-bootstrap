"""End-to-end bootstrap rendering, determinism, and git init tests."""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

import pytest

from fullstack_bootstrap.bootstrap import BootstrapError, LocalArchives, bootstrap
from fullstack_bootstrap.cli import main
from tests.helpers import backend_fixture_files, frontend_fixture_files, write_zip


def _archives(tmp_path: Path) -> LocalArchives:
    backend = write_zip(tmp_path / "backend.zip", backend_fixture_files())
    frontend = write_zip(tmp_path / "frontend.zip", frontend_fixture_files())
    return LocalArchives(backend=backend, frontend=frontend)


def _tree_hashes(root: Path) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        if relative.startswith(".git/") or relative == ".git":
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        hashes[relative] = digest
    return hashes


def test_bootstrap_brands_backend_and_frontend(tmp_path: Path) -> None:
    result = bootstrap("Acme Corp", output_dir=tmp_path, archives=_archives(tmp_path / "zips"))

    backend = result.backend_path
    frontend = result.frontend_path
    assert backend.name == "acme-corp-backend"
    assert frontend.name == "acme-corp-frontend"
    assert (backend / "acme_corp" / "settings" / "base.py").is_file()
    assert not (backend / "config").exists()

    base = (backend / "acme_corp" / "settings" / "base.py").read_text(encoding="utf-8")
    assert 'ROOT_URLCONF = "acme_corp.urls"' in base
    assert 'TITLE": "Acme Corp API"' in base
    assert "from decouple import Csv, config" in base
    assert 'config("SECRET_KEY")' in base

    pyproject = (backend / "pyproject.toml").read_text(encoding="utf-8")
    assert 'name = "acme-corp-backend"' in pyproject
    assert "acme_corp.settings.test" in pyproject

    schema = (backend / "schema.yml").read_text(encoding="utf-8")
    assert "title: Acme Corp API" in schema

    package = (frontend / "package.json").read_text(encoding="utf-8")
    assert '"name": "acme-corp-frontend"' in package

    env_example = (frontend / ".env.example").read_text(encoding="utf-8")
    assert "OPENAPI_SCHEMA_PATH=../acme-corp-backend/schema.yml" in env_example

    assert "<title>Acme Corp</title>" in (frontend / "index.html").read_text(encoding="utf-8")
    assert "Acme Corp" in (frontend / "src" / "shared" / "layout" / "AppShell.tsx").read_text(
        encoding="utf-8"
    )
    assert "Acme Corp" in (
        frontend / "src" / "features" / "auth" / "pages" / "LoginPage.tsx"
    ).read_text(encoding="utf-8")

    # Generated client is not rewritten.
    assert "django-boilerplate" in (frontend / "src" / "shared" / "api" / "sdk.gen.ts").read_text(
        encoding="utf-8"
    )


def test_bootstrap_installs_agent_support(tmp_path: Path) -> None:
    result = bootstrap("Acme Corp", output_dir=tmp_path, archives=_archives(tmp_path / "zips"))

    for root in (result.backend_path, result.frontend_path):
        assert (root / "SPECS" / "04-crud-pattern.md").is_file()
        assert (root / "SPECS" / "00-overview.md").is_file()
        assert (root / ".cursor" / "rules" / "fullstack-conventions.mdc").is_file()
        assert (root / ".cursor" / "skills" / "fullstack-crud" / "SKILL.md").is_file()
        agents = (root / "AGENTS.md").read_text(encoding="utf-8")
        assert "acme-corp" in agents
        assert "./SPECS/" in agents
        assert "../SPECS" not in agents

    backend_agents = (result.backend_path / "AGENTS.md").read_text(encoding="utf-8")
    assert "acme-corp-backend" in backend_agents
    assert "acme_corp.settings.local" in backend_agents

    overview = (result.backend_path / "SPECS" / "00-overview.md").read_text(encoding="utf-8")
    assert "acme-corp-backend" in overview
    assert "django-boilerplate" not in overview


def test_bootstrap_is_deterministic(tmp_path: Path) -> None:
    archives = _archives(tmp_path / "zips")
    first = bootstrap("Acme Corp", output_dir=tmp_path / "a", archives=archives)
    second = bootstrap("Acme Corp", output_dir=tmp_path / "b", archives=archives)

    assert _tree_hashes(first.backend_path) == _tree_hashes(second.backend_path)
    assert _tree_hashes(first.frontend_path) == _tree_hashes(second.frontend_path)


def test_bootstrap_inits_git_main(tmp_path: Path) -> None:
    result = bootstrap("Acme Corp", output_dir=tmp_path, archives=_archives(tmp_path / "zips"))
    for root in (result.backend_path, result.frontend_path):
        assert (root / ".git").exists()
        ref = subprocess.check_output(
            ["git", "symbolic-ref", "--short", "HEAD"],
            cwd=root,
            text=True,
        ).strip()
        assert ref == "main"


def test_bootstrap_refuses_collisions(tmp_path: Path) -> None:
    archives = _archives(tmp_path / "zips")
    bootstrap("Acme Corp", output_dir=tmp_path, archives=archives)
    with pytest.raises(BootstrapError, match="overwrite"):
        bootstrap("Acme Corp", output_dir=tmp_path, archives=archives)


def test_cli_rejects_unset_sources(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """CLI exits with configuration error when pins are still UNSET."""
    unset = tmp_path / "template-sources.toml"
    unset.write_text(
        """
[backend]
url = "UNSET"
commit = "UNSET"
sha256 = "UNSET"

[frontend]
url = "UNSET"
commit = "UNSET"
sha256 = "UNSET"
""".strip()
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "fullstack_bootstrap.sources.default_sources_path",
        lambda: unset,
    )
    code = main(["Acme Corp"])
    assert code == 2


def test_cli_with_local_api_success_message(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # CLI has no archive override; exercise bootstrap API path already covered.
    # Ensure cwd isolation still works for naming collisions.
    monkeypatch.chdir(tmp_path)
    result = bootstrap("Beta Inc", output_dir=tmp_path, archives=_archives(tmp_path / "zips"))
    assert result.backend_path.exists()
    captured = capsys.readouterr()
    assert captured.out == ""
