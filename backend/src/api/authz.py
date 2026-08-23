"""API-Autorisierung — Rollenprüfung (Gate 8.1b, ADR-0025)."""

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
