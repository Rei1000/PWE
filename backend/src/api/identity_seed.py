"""Seed Administrator für Dev/Demo (Gate 8.1a, ADR-0024).

Bekanntes Default-Passwort nur bei eindeutigem Development/Demo-Betrieb.
Idempotent: existierender Benutzer wird nicht überschrieben.
"""

from __future__ import annotations

import os

from domain.identity.benutzer import Benutzer
from domain.identity.typen import BenutzerStatus, Systemrolle
from ports.benutzer_repository import BenutzerRepository
from ports.passwort_hasher import PasswortHasher

DEFAULT_ADMIN_LOGIN = "admin"
DEFAULT_ADMIN_PASSWORD = "admin-change-me"
DEFAULT_ADMIN_NAME = "Administrator"

_TRUTHY = frozenset({"1", "true", "yes", "on"})
_FALSY = frozenset({"0", "false", "no", "off"})
_DEV_ENVS = frozenset({"development", "dev", "test"})


class SeedAdminConfigurationError(RuntimeError):
    """Seed-Konfiguration unzulässig — Fail-Fast beim Start."""


def _env_flag(name: str) -> bool | None:
    raw = os.environ.get(name)
    if raw is None:
        return None
    value = raw.strip().lower()
    if value in _TRUTHY:
        return True
    if value in _FALSY:
        return False
    raise SeedAdminConfigurationError(
        f"Ungültiger {name}: {raw!r}. Erlaubt: true/false, 1/0, yes/no, on/off."
    )


def seed_admin_enabled() -> bool:
    """PWE_SEED_ADMIN — Default true; false deaktiviert den Seed vollständig."""
    flag = _env_flag("PWE_SEED_ADMIN")
    return True if flag is None else flag


def insecure_default_password_allowed() -> bool:
    """Default-Passwort nur in Dev/Demo oder bei explizitem Override."""
    if _env_flag("PWE_DEMO_MODE") is True:
        return True
    if _env_flag("PWE_ALLOW_DEFAULT_ADMIN_PASSWORD") is True:
        return True
    env = os.environ.get("ENV", "").strip().lower()
    return env in _DEV_ENVS


def seed_admin_login() -> str:
    login = os.environ.get("PWE_SEED_ADMIN_LOGIN", DEFAULT_ADMIN_LOGIN).strip()
    return login or DEFAULT_ADMIN_LOGIN


def seed_admin_name() -> str:
    name = os.environ.get("PWE_SEED_ADMIN_NAME", DEFAULT_ADMIN_NAME).strip()
    return name or DEFAULT_ADMIN_NAME


def resolve_seed_password() -> str:
    """Liefert Seed-Passwort oder bricht fail-fast ab (nie loggen)."""
    raw = os.environ.get("PWE_SEED_ADMIN_PASSWORD")
    if raw is None or not raw.strip():
        if insecure_default_password_allowed():
            return DEFAULT_ADMIN_PASSWORD
        raise SeedAdminConfigurationError(
            "PWE_SEED_ADMIN_PASSWORD ist außerhalb von Development/Demo erforderlich "
            "(ENV=development|dev|test, PWE_DEMO_MODE=true oder "
            "PWE_ALLOW_DEFAULT_ADMIN_PASSWORD=true). "
            "Alternativ Seed deaktivieren: PWE_SEED_ADMIN=false."
        )
    password = raw.strip()
    if password == DEFAULT_ADMIN_PASSWORD and not insecure_default_password_allowed():
        raise SeedAdminConfigurationError(
            "Bekanntes Default-Passwort ist nur in Development/Demo zulässig. "
            "Setze ein eigenes PWE_SEED_ADMIN_PASSWORD oder PWE_SEED_ADMIN=false."
        )
    return password


def ensure_seed_administrator(
    repo: BenutzerRepository,
    hasher: PasswortHasher,
) -> Benutzer | None:
    """Legt Admin an, falls Seed aktiv und Login noch nicht existiert.

    Existierende Benutzer werden unverändert belassen (kein Passwort-Reset).
    """
    if not seed_admin_enabled():
        return None

    login = seed_admin_login()
    name = seed_admin_name()
    password = resolve_seed_password()

    existing = repo.get_by_login(login)
    if existing is not None:
        return existing

    # Rollen ausdrücklich gesetzt — keine Vererbung Admin→Prüfer (ADR-0025).
    admin = Benutzer.anlegen(
        login=login,
        anzeigename=name,
        passwort_hash=hasher.hash(password),
        rollen=frozenset({Systemrolle.ADMINISTRATOR, Systemrolle.PRUEFER}),
        status=BenutzerStatus.AKTIV,
    )
    repo.save(admin)
    return admin
