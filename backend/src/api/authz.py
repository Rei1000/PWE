"""API-Autorisierung — Rollenprüfung (Gate 8.1b/8.1c1, ADR-0025)."""

from __future__ import annotations

from domain.identity.benutzer import Benutzer
from domain.identity.typen import Systemrolle
from domain.shared.errors import DomainError


class NichtBerechtigt(DomainError):
    """Benutzer hat keine der erforderlichen Systemrollen."""


def require_rollen(benutzer: Benutzer, *rollen: Systemrolle) -> None:
    """Wirft NichtBerechtigt, wenn keine der geforderten Rollen in der Rollenmenge ist."""
    if not rollen:
        return
    if not any(r in benutzer.rollen for r in rollen):
        raise NichtBerechtigt("Keine Berechtigung für diese Aktion")


def require_katalog_bearbeiten(benutzer: Benutzer) -> None:
    """Bibliothek CRUD und Entwurfsbearbeitung (ADR-0025)."""
    require_rollen(
        benutzer,
        Systemrolle.ADMINISTRATOR,
        Systemrolle.QM,
        Systemrolle.ABTEILUNGSLEITER,
    )


def require_katalog_veroeffentlichen(benutzer: Benutzer) -> None:
    """Publish und Einweisungsübernahme-Flag (ADR-0025)."""
    require_rollen(benutzer, Systemrolle.ADMINISTRATOR, Systemrolle.QM)


def require_identity_lesen(benutzer: Benutzer) -> None:
    """Benutzer/Profile/Einweisungen lesen — Admin, QM, Abteilungsleiter."""
    require_rollen(
        benutzer,
        Systemrolle.ADMINISTRATOR,
        Systemrolle.QM,
        Systemrolle.ABTEILUNGSLEITER,
    )


def require_administrator(benutzer: Benutzer) -> None:
    require_rollen(benutzer, Systemrolle.ADMINISTRATOR)
