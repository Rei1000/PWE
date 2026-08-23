"""Seed Administrator für Dev/Demo (Gate 8.1a)."""

from __future__ import annotations

import os

from domain.identity.benutzer import Benutzer
from domain.identity.typen import BenutzerStatus, Systemrolle
from ports.benutzer_repository import BenutzerRepository
from ports.passwort_hasher import PasswortHasher

DEFAULT_ADMIN_LOGIN = "admin"
DEFAULT_ADMIN_PASSWORD = "admin-change-me"
DEFAULT_ADMIN_NAME = "Administrator"


def seed_admin_settings() -> tuple[str, str, str]:
    login = os.environ.get("PWE_SEED_ADMIN_LOGIN", DEFAULT_ADMIN_LOGIN).strip() or DEFAULT_ADMIN_LOGIN
    password = (
        os.environ.get("PWE_SEED_ADMIN_PASSWORD", DEFAULT_ADMIN_PASSWORD).strip()
        or DEFAULT_ADMIN_PASSWORD
    )
    name = os.environ.get("PWE_SEED_ADMIN_NAME", DEFAULT_ADMIN_NAME).strip() or DEFAULT_ADMIN_NAME
    return login, password, name


def ensure_seed_administrator(
    repo: BenutzerRepository,
    hasher: PasswortHasher,
) -> Benutzer:
    """Legt Admin an, falls Login noch nicht existiert."""
    login, password, name = seed_admin_settings()
    existing = repo.get_by_login(login)
    if existing is not None:
        return existing
    admin = Benutzer.anlegen(
        login=login,
        anzeigename=name,
        passwort_hash=hasher.hash(password),
        rollen=frozenset({Systemrolle.ADMINISTRATOR, Systemrolle.PRUEFER}),
        status=BenutzerStatus.AKTIV,
    )
    repo.save(admin)
    return admin
