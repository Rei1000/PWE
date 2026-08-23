"""PostgreSQL — Benutzer + Session (Gate 8.1a)."""

from __future__ import annotations

import json
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from adapters.persistence.postgresql.schema import BenutzerRow, IdentitySessionRow
from domain.identity.benutzer import Benutzer, PasswortHash
from domain.identity.typen import BenutzerStatus, Systemrolle
from ports.session_store import SessionDaten


def _benutzer_to_row(b: Benutzer) -> BenutzerRow:
    return BenutzerRow(
        benutzer_id=b.benutzer_id,
        login=b.login,
        anzeigename=b.anzeigename,
        status=b.status.value,
        passwort_hash=b.passwort_hash.wert,
        rollen_json=json.dumps(sorted(r.value for r in b.rollen)),
    )


def _row_to_benutzer(row: BenutzerRow) -> Benutzer:
    rollen = frozenset(Systemrolle(r) for r in json.loads(row.rollen_json))
    return Benutzer(
        benutzer_id=row.benutzer_id,
        login=row.login,
        anzeigename=row.anzeigename,
        status=BenutzerStatus(row.status),
        rollen=rollen,
        passwort_hash=PasswortHash(row.passwort_hash),
    )


class PostgresBenutzerRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, benutzer: Benutzer) -> None:
        existing = self._session.get(BenutzerRow, benutzer.benutzer_id)
        row = _benutzer_to_row(benutzer)
        if existing is None:
            self._session.add(row)
        else:
            existing.login = row.login
            existing.anzeigename = row.anzeigename
            existing.status = row.status
            existing.passwort_hash = row.passwort_hash
            existing.rollen_json = row.rollen_json

    def get(self, benutzer_id: str) -> Benutzer | None:
        row = self._session.get(BenutzerRow, benutzer_id)
        return _row_to_benutzer(row) if row else None

    def get_by_login(self, login: str) -> Benutzer | None:
        stmt = select(BenutzerRow).where(BenutzerRow.login == login.strip())
        row = self._session.scalars(stmt).first()
        return _row_to_benutzer(row) if row else None


class PostgresSessionStore:
    def __init__(self, session: Session) -> None:
        self._session = session

    def speichern(self, session_daten: SessionDaten) -> None:
        existing = self._session.get(IdentitySessionRow, session_daten.session_id)
        if existing is None:
            self._session.add(
                IdentitySessionRow(
                    session_id=session_daten.session_id,
                    benutzer_id=session_daten.benutzer_id,
                    csrf_token=session_daten.csrf_token,
                    erzeugt_am=session_daten.erzeugt_am.isoformat(),
                    zuletzt_gesehen_am=session_daten.zuletzt_gesehen_am.isoformat(),
                )
            )
        else:
            existing.benutzer_id = session_daten.benutzer_id
            existing.csrf_token = session_daten.csrf_token
            existing.erzeugt_am = session_daten.erzeugt_am.isoformat()
            existing.zuletzt_gesehen_am = session_daten.zuletzt_gesehen_am.isoformat()

    def laden(self, session_id: str) -> SessionDaten | None:
        row = self._session.get(IdentitySessionRow, session_id)
        if row is None:
            return None
        return SessionDaten(
            session_id=row.session_id,
            benutzer_id=row.benutzer_id,
            csrf_token=row.csrf_token,
            erzeugt_am=datetime.fromisoformat(row.erzeugt_am),
            zuletzt_gesehen_am=datetime.fromisoformat(row.zuletzt_gesehen_am),
        )

    def aktualisieren_zuletzt_gesehen(self, session_id: str, zeitpunkt: datetime) -> None:
        row = self._session.get(IdentitySessionRow, session_id)
        if row is None:
            return
        row.zuletzt_gesehen_am = zeitpunkt.isoformat()

    def loeschen(self, session_id: str) -> None:
        row = self._session.get(IdentitySessionRow, session_id)
        if row is not None:
            self._session.delete(row)

    def loeschen_alle_fuer_benutzer(self, benutzer_id: str) -> None:
        stmt = select(IdentitySessionRow).where(IdentitySessionRow.benutzer_id == benutzer_id)
        for row in self._session.scalars(stmt).all():
            self._session.delete(row)
