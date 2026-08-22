"""PostgreSQL-Implementierung — BibliothekRepository."""

from __future__ import annotations

from sqlalchemy.orm import Session

from adapters.persistence.postgresql.mapping import routine_from_payload, routine_to_payload
from adapters.persistence.postgresql.schema import ExternesKommandoRow, PruefschrittVorlageRow, RoutineRow
from domain.katalog.externes_kommando import ExternesKommando
from domain.katalog.pruefschritt_vorlage import PruefschrittVorlage
from domain.katalog.routine import Routine


class PostgresBibliothekRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def save_externes_kommando(self, kommando: ExternesKommando, *, commit: bool = False) -> None:
        row = self._session.get(ExternesKommandoRow, kommando.kommando_id)
        if row is None:
            self._session.add(
                ExternesKommandoRow(
                    kommando_id=kommando.kommando_id,
                    bezeichnung=kommando.bezeichnung,
                    kommandocode=kommando.kommandocode,
                )
            )
        else:
            row.bezeichnung = kommando.bezeichnung
            row.kommandocode = kommando.kommandocode
        if commit:
            self._session.commit()

    def get_externes_kommando(self, kommando_id: str) -> ExternesKommando | None:
        row = self._session.get(ExternesKommandoRow, kommando_id)
        if row is None:
            return None
        return ExternesKommando(
            kommando_id=row.kommando_id,
            bezeichnung=row.bezeichnung,
            kommandocode=row.kommandocode,
        )

    def save_routine(self, routine: Routine, *, commit: bool = False) -> None:
        payload = routine_to_payload(routine)
        row = self._session.get(RoutineRow, routine.routine_id)
        if row is None:
            self._session.add(
                RoutineRow(
                    routine_id=routine.routine_id,
                    bezeichnung=routine.bezeichnung,
                    payload=payload,
                )
            )
        else:
            row.bezeichnung = routine.bezeichnung
            row.payload = payload
        if commit:
            self._session.commit()

    def get_routine(self, routine_id: str) -> Routine | None:
        row = self._session.get(RoutineRow, routine_id)
        if row is None:
            return None
        return routine_from_payload(row.routine_id, row.bezeichnung, row.payload)

    def list_externe_kommandos(self) -> list[ExternesKommando]:
        rows = self._session.query(ExternesKommandoRow).all()
        return [
            ExternesKommando(
                kommando_id=row.kommando_id,
                bezeichnung=row.bezeichnung,
                kommandocode=row.kommandocode,
            )
            for row in rows
        ]

    def list_routinen(self) -> list[Routine]:
        rows = self._session.query(RoutineRow).all()
        return [routine_from_payload(row.routine_id, row.bezeichnung, row.payload) for row in rows]

    def delete_externes_kommando(self, kommando_id: str, *, commit: bool = False) -> None:
        row = self._session.get(ExternesKommandoRow, kommando_id)
        if row is not None:
            self._session.delete(row)
            self._session.flush()
        if commit:
            self._session.commit()

    def delete_routine(self, routine_id: str, *, commit: bool = False) -> None:
        row = self._session.get(RoutineRow, routine_id)
        if row is not None:
            self._session.delete(row)
            self._session.flush()
        if commit:
            self._session.commit()

    def save_pruefschritt_vorlage(
        self, vorlage: PruefschrittVorlage, *, commit: bool = False
    ) -> None:
        row = self._session.get(PruefschrittVorlageRow, vorlage.vorlage_id)
        if row is None:
            self._session.add(
                PruefschrittVorlageRow(
                    vorlage_id=vorlage.vorlage_id,
                    bezeichnung=vorlage.bezeichnung,
                    beschreibung=vorlage.beschreibung,
                )
            )
        else:
            row.bezeichnung = vorlage.bezeichnung
            row.beschreibung = vorlage.beschreibung
        if commit:
            self._session.commit()

    def get_pruefschritt_vorlage(self, vorlage_id: str) -> PruefschrittVorlage | None:
        row = self._session.get(PruefschrittVorlageRow, vorlage_id)
        if row is None:
            return None
        return PruefschrittVorlage(
            vorlage_id=row.vorlage_id,
            bezeichnung=row.bezeichnung,
            beschreibung=row.beschreibung,
        )

    def list_pruefschritt_vorlagen(self) -> list[PruefschrittVorlage]:
        rows = self._session.query(PruefschrittVorlageRow).all()
        return [
            PruefschrittVorlage(
                vorlage_id=row.vorlage_id,
                bezeichnung=row.bezeichnung,
                beschreibung=row.beschreibung,
            )
            for row in rows
        ]

    def delete_pruefschritt_vorlage(self, vorlage_id: str, *, commit: bool = False) -> None:
        row = self._session.get(PruefschrittVorlageRow, vorlage_id)
        if row is not None:
            self._session.delete(row)
            self._session.flush()
        if commit:
            self._session.commit()
