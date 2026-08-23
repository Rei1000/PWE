"""Port — serverseitige Session (ADR-0024)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True)
class SessionDaten:
    session_id: str
    benutzer_id: str
    csrf_token: str
    erzeugt_am: datetime
    zuletzt_gesehen_am: datetime


class SessionStore(Protocol):
    def speichern(self, session: SessionDaten) -> None: ...

    def laden(self, session_id: str) -> SessionDaten | None: ...

    def aktualisieren_zuletzt_gesehen(self, session_id: str, zeitpunkt: datetime) -> None: ...

    def loeschen(self, session_id: str) -> None: ...

    def loeschen_alle_fuer_benutzer(self, benutzer_id: str) -> None: ...
