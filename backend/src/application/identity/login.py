"""Use Case — Login (Gate 8.1a)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from secrets import token_urlsafe
from uuid import uuid4

from domain.identity.benutzer import Benutzer, LoginNichtErlaubt
from domain.shared.errors import DomainError
from ports.benutzer_repository import BenutzerRepository
from ports.passwort_hasher import PasswortHasher
from ports.session_store import SessionDaten, SessionStore


class UngueltigeAnmeldedaten(DomainError):
    """Login oder Passwort falsch — generische Meldung nach außen."""


@dataclass(frozen=True)
class LoginErgebnis:
    session_id: str
    csrf_token: str
    benutzer: Benutzer


@dataclass
class Login:
    benutzer_repo: BenutzerRepository
    hasher: PasswortHasher
    sessions: SessionStore

    def execute(self, *, login: str, passwort: str) -> LoginErgebnis:
        benutzer = self.benutzer_repo.get_by_login(login.strip())
        if benutzer is None:
            raise UngueltigeAnmeldedaten("Anmeldung fehlgeschlagen")
        if not self.hasher.verifizieren(passwort, benutzer.passwort_hash):
            raise UngueltigeAnmeldedaten("Anmeldung fehlgeschlagen")
        try:
            benutzer.assert_login_erlaubt()
        except LoginNichtErlaubt as exc:
            raise UngueltigeAnmeldedaten("Anmeldung fehlgeschlagen") from exc

        jetzt = datetime.now(UTC)
        session_id = str(uuid4())
        csrf_token = token_urlsafe(32)
        self.sessions.speichern(
            SessionDaten(
                session_id=session_id,
                benutzer_id=benutzer.benutzer_id,
                csrf_token=csrf_token,
                erzeugt_am=jetzt,
                zuletzt_gesehen_am=jetzt,
            )
        )
        return LoginErgebnis(session_id=session_id, csrf_token=csrf_token, benutzer=benutzer)
