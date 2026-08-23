"""Use Cases — Passwort (Gate 8.1c1)."""

from __future__ import annotations

from dataclasses import dataclass

from domain.identity.benutzer import Benutzer
from domain.identity.identity_audit import IdentityAuditEintrag
from domain.identity.typen import BenutzerStatus
from domain.shared.errors import DomainError, InvariantViolation
from ports.benutzer_repository import BenutzerRepository
from ports.identity_audit_repository import IdentityAuditRepository
from ports.passwort_hasher import PasswortHasher
from ports.session_store import SessionStore


class BenutzerNichtGefundenFuerPasswort(DomainError):
    pass


class AltesPasswortUngueltig(DomainError):
    pass


@dataclass
class PasswortZuruecksetzen:
    """Admin-Reset: neues Passwort + Force-Change + Sessions invalidieren."""

    benutzer: BenutzerRepository
    hasher: PasswortHasher
    sessions: SessionStore
    audit: IdentityAuditRepository

    def execute(
        self, *, akteur_id: str, benutzer_id: str, neues_passwort: str
    ) -> Benutzer:
        if not neues_passwort or not neues_passwort.strip():
            raise InvariantViolation("Passwort darf nicht leer sein")
        existing = self.benutzer.get(benutzer_id)
        if existing is None:
            raise BenutzerNichtGefundenFuerPasswort(f"Benutzer {benutzer_id} nicht gefunden")
        if existing.status == BenutzerStatus.ARCHIVIERT:
            raise InvariantViolation("Passwort archivierter Benutzer kann nicht gesetzt werden")
        geaendert = existing.mit_passwort(
            self.hasher.hash(neues_passwort),
            passwortwechsel_erforderlich=True,
        )
        self.benutzer.save(geaendert)
        self.sessions.loeschen_alle_fuer_benutzer(benutzer_id)
        self.audit.append(
            IdentityAuditEintrag.erzeugen(
                akteur_benutzer_id=akteur_id,
                aktion="passwort_admin_reset",
                ziel_benutzer_id=benutzer_id,
                details={"passwortwechsel_erforderlich": True},
            )
        )
        return geaendert


@dataclass
class PasswortAendern:
    """Self-Change: altes prüfen, Flag löschen, alle Sessions invalidieren."""

    benutzer: BenutzerRepository
    hasher: PasswortHasher
    sessions: SessionStore
    audit: IdentityAuditRepository

    def execute(
        self, *, benutzer_id: str, altes_passwort: str, neues_passwort: str
    ) -> Benutzer:
        if not neues_passwort or not neues_passwort.strip():
            raise InvariantViolation("Passwort darf nicht leer sein")
        existing = self.benutzer.get(benutzer_id)
        if existing is None:
            raise BenutzerNichtGefundenFuerPasswort(f"Benutzer {benutzer_id} nicht gefunden")
        if existing.status != BenutzerStatus.AKTIV:
            raise InvariantViolation("Passwort ändern nur für aktive Benutzer")
        if not self.hasher.verifizieren(altes_passwort, existing.passwort_hash):
            raise AltesPasswortUngueltig("Altes Passwort ist ungültig")
        geaendert = existing.mit_passwort(
            self.hasher.hash(neues_passwort),
            passwortwechsel_erforderlich=False,
        )
        self.benutzer.save(geaendert)
        self.sessions.loeschen_alle_fuer_benutzer(benutzer_id)
        self.audit.append(
            IdentityAuditEintrag.erzeugen(
                akteur_benutzer_id=benutzer_id,
                aktion="passwort_geaendert",
                ziel_benutzer_id=benutzer_id,
                details={"passwortwechsel_erforderlich": False},
            )
        )
        return geaendert
