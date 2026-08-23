"""Tests — Seed-Administrator-Konfiguration (Gate 8.1a Security)."""

from __future__ import annotations

import pytest

from adapters.persistence.in_memory_identity import InMemoryBenutzerRepository
from adapters.security.argon2_hasher import Argon2PasswortHasher
from api import identity_seed as seed
from domain.identity.typen import Systemrolle


@pytest.fixture(autouse=True)
def _clean_seed_env(monkeypatch: pytest.MonkeyPatch):
    for key in (
        "PWE_SEED_ADMIN",
        "PWE_SEED_ADMIN_PASSWORD",
        "PWE_SEED_ADMIN_LOGIN",
        "PWE_SEED_ADMIN_NAME",
        "PWE_DEMO_MODE",
        "PWE_ALLOW_DEFAULT_ADMIN_PASSWORD",
        "ENV",
    ):
        monkeypatch.delenv(key, raising=False)


def test_default_password_forbidden_outside_dev_demo(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("ENV", "production")
    with pytest.raises(seed.SeedAdminConfigurationError, match="PWE_SEED_ADMIN_PASSWORD"):
        seed.resolve_seed_password()


def test_explicit_default_password_forbidden_outside_dev(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("ENV", "production")
    monkeypatch.setenv("PWE_SEED_ADMIN_PASSWORD", seed.DEFAULT_ADMIN_PASSWORD)
    with pytest.raises(seed.SeedAdminConfigurationError, match="Default-Passwort"):
        seed.resolve_seed_password()


def test_default_password_allowed_when_env_development(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("ENV", "development")
    assert seed.resolve_seed_password() == seed.DEFAULT_ADMIN_PASSWORD


def test_default_password_allowed_when_demo_mode(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("PWE_DEMO_MODE", "true")
    assert seed.resolve_seed_password() == seed.DEFAULT_ADMIN_PASSWORD


def test_seed_disabled(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("PWE_SEED_ADMIN", "false")
    monkeypatch.setenv("ENV", "production")
    repo = InMemoryBenutzerRepository()
    assert seed.ensure_seed_administrator(repo, Argon2PasswortHasher()) is None
    assert repo.get_by_login(seed.DEFAULT_ADMIN_LOGIN) is None


def test_seed_idempotent_does_not_overwrite_password(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("ENV", "test")
    monkeypatch.setenv("PWE_SEED_ADMIN_PASSWORD", "first-secret")
    repo = InMemoryBenutzerRepository()
    hasher = Argon2PasswortHasher()
    first = seed.ensure_seed_administrator(repo, hasher)
    assert first is not None
    hash_before = first.passwort_hash.wert

    monkeypatch.setenv("PWE_SEED_ADMIN_PASSWORD", "second-secret")
    second = seed.ensure_seed_administrator(repo, hasher)
    assert second is not None
    assert second.benutzer_id == first.benutzer_id
    assert second.passwort_hash.wert == hash_before
    assert hasher.verifizieren("first-secret", second.passwort_hash)
    assert not hasher.verifizieren("second-secret", second.passwort_hash)


def test_seed_roles_explicit_admin_and_pruefer(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("ENV", "test")
    repo = InMemoryBenutzerRepository()
    admin = seed.ensure_seed_administrator(repo, Argon2PasswortHasher())
    assert admin is not None
    assert admin.rollen == frozenset({Systemrolle.ADMINISTRATOR, Systemrolle.PRUEFER})


def test_explicit_custom_password_in_production(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("ENV", "production")
    monkeypatch.setenv("PWE_SEED_ADMIN_PASSWORD", "prod-only-secret")
    assert seed.resolve_seed_password() == "prod-only-secret"
