"""Use Case — aktueller Benutzer aus Session (Gate 8.1a)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from domain.identity.benutzer import Benutzer, LoginNichtErlaubt
from domain.shared.errors import DomainError
from ports.benutzer_repository import BenutzerRepository
from ports.session_store import SessionStore


class NichtAuthentifiziert(DomainError):
    pass


class SessionAbgelaufen(DomainError):
    pass


@dataclass
class SessionTimeouts:
    idle: timedelta
    absolute: timedelta


@dataclass
class AktuellerBenutzerLaden:
    benutzer_repo: BenutzerRepository
    sessions: SessionStore
    timeouts: SessionTimeouts

    def execute(self, *, session_id: str | None) -> Benutzer:
        if not session_id:
            raise NichtAuthentifiziert("Nicht angemeldet")
        session = self.sessions.laden(session_id)
        if session is None:
            raise NichtAuthentifiziert("Nicht angemeldet")

        jetzt = datetime.now(UTC)
        if jetzt - session.erzeugt_am > self.timeouts.absolute:
            self.sessions.loeschen(session_id)
            raise SessionAbgelaufen("Sitzung abgelaufen")
        if jetzt - session.zuletzt_gesehen_am > self.timeouts.idle:
            self.sessions.loeschen(session_id)
            raise SessionAbgelaufen("Sitzung abgelaufen")

        benutzer = self.benutzer_repo.get(session.benutzer_id)
        if benutzer is None:
            self.sessions.loeschen(session_id)
            raise NichtAuthentifiziert("Nicht angemeldet")
        try:
            benutzer.assert_login_erlaubt()
        except LoginNichtErlaubt as exc:
            self.sessions.loeschen(session_id)
            raise NichtAuthentifiziert("Nicht angemeldet") from exc

        self.sessions.aktualisieren_zuletzt_gesehen(session_id, jetzt)
        return benutzer
