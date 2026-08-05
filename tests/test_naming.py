"""Tests for client-name → identity derivation."""

import pytest

from fullstack_bootstrap.naming import NamingError, derive_names


def test_derive_names_acme_corp() -> None:
    names = derive_names("Acme Corp")
    assert names.display_name == "Acme Corp"
    assert names.slug == "acme-corp"
    assert names.python_id == "acme_corp"
    assert names.backend_repo == "acme-corp-backend"
    assert names.frontend_repo == "acme-corp-frontend"
    assert names.api_title == "Acme Corp API"


def test_derive_names_collapses_whitespace() -> None:
    names = derive_names("  Acme   Corp  ")
    assert names.display_name == "Acme Corp"
    assert names.slug == "acme-corp"


def test_derive_names_rejects_empty() -> None:
    with pytest.raises(NamingError, match="empty"):
        derive_names("   ")


def test_derive_names_rejects_leading_digit_slug() -> None:
    with pytest.raises(NamingError):
        derive_names("123 Corp")
