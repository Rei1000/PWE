"""In-Memory Identity-Adapter (Tests / Dev ohne DB)."""

from __future__ import annotations

from datetime import datetime

from domain.identity.benutzer import Benutzer
from ports.session_store import SessionDaten


class InMemoryBenutzerRepository:
    def __init__(self) -> None:
        self._by_id: dict[str, Benutzer] = {}
        self._by_login: dict[str, str] = {}

    def save(self, benutzer: Benutzer) -> None:
        self._by_id[benutzer.benutzer_id] = benutzer
        self._by_login[benutzer.login.lower()] = benutzer.benutzer_id

    def get(self, benutzer_id: str) -> Benutzer | None:
        return self._by_id.get(benutzer_id)

    def get_by_login(self, login: str) -> Benutzer | None:
        bid = self._by_login.get(login.strip().lower())
        if bid is None:
            return None
        return self._by_id.get(bid)


class InMemorySessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, SessionDaten] = {}

    def speichern(self, session: SessionDaten) -> None:
        self._sessions[session.session_id] = session

    def laden(self, session_id: str) -> SessionDaten | None:
        return self._sessions.get(session_id)

    def aktualisieren_zuletzt_gesehen(self, session_id: str, zeitpunkt: datetime) -> None:
        alt = self._sessions.get(session_id)
        if alt is None:
            return
        self._sessions[session_id] = SessionDaten(
            session_id=alt.session_id,
            benutzer_id=alt.benutzer_id,
            csrf_token=alt.csrf_token,
            erzeugt_am=alt.erzeugt_am,
            zuletzt_gesehen_am=zeitpunkt,
        )

    def loeschen(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)

    def loeschen_alle_fuer_benutzer(self, benutzer_id: str) -> None:
        for sid, s in list(self._sessions.items()):
            if s.benutzer_id == benutzer_id:
                del self._sessions[sid]
