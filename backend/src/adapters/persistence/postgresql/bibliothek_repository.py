"""PostgreSQL-Implementierung — BibliothekRepository."""

from __future__ import annotations

from sqlalchemy.orm import Session

from adapters.persistence.postgresql.schema import ExternesKommandoRow
from domain.katalog.externes_kommando import ExternesKommando


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
