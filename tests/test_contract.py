"""Contract test for real pinned archives — skipped until sources are configured."""

from __future__ import annotations

from pathlib import Path

import pytest

from fullstack_bootstrap.bootstrap import bootstrap
from fullstack_bootstrap.sources import UNSET, load_sources


@pytest.mark.skipif(
    load_sources().backend.url == UNSET or load_sources().frontend.url == UNSET,
    reason="template-sources.toml still has UNSET placeholders",
)
def test_real_archive_contract(tmp_path: Path) -> None:
    result = bootstrap("Contract Client", output_dir=tmp_path)
    assert (result.backend_path / result.names.python_id / "settings" / "base.py").is_file()
    assert (result.frontend_path / "package.json").is_file()
    assert (result.backend_path / "SPECS" / "04-crud-pattern.md").is_file()
    assert "django-boilerplate" not in (result.backend_path / "pyproject.toml").read_text(
        encoding="utf-8"
    )
