"""Template source configuration loading."""

from pathlib import Path

import pytest

from fullstack_bootstrap.sources import SourcesError, UNSET, load_sources


def test_default_sources_are_configured() -> None:
    sources = load_sources()
    assert sources.backend.url != UNSET
    assert sources.frontend.url != UNSET
    assert sources.backend.commit != UNSET
    assert sources.frontend.sha256 != UNSET
    sources.assert_configured()
    assert "backend-boilerplate" in sources.backend.url
    assert "frontend-boilerplate" in sources.frontend.url


def test_unset_sources_fail_assert_configured(tmp_path: Path) -> None:
    path = tmp_path / "sources.toml"
    path.write_text(
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
    sources = load_sources(path)
    with pytest.raises(SourcesError, match="not configured"):
        sources.assert_configured()


def test_load_sources_from_custom_file(tmp_path: Path) -> None:
    path = tmp_path / "sources.toml"
    path.write_text(
        """
[backend]
url = "https://example.com/backend.zip"
commit = "abc123"
sha256 = "deadbeef"

[frontend]
url = "https://example.com/frontend.zip"
commit = "def456"
sha256 = "cafebabe"
""".strip()
        + "\n",
        encoding="utf-8",
    )
    sources = load_sources(path)
    assert sources.backend.url.endswith("backend.zip")
    assert sources.frontend.sha256 == "cafebabe"
    sources.assert_configured()
