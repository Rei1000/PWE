"""PostgreSQL-Implementierung — PrueflaufRepository."""

from __future__ import annotations

from sqlalchemy.orm import Session

from adapters.persistence.postgresql.mapping import prueflauf_from_payload, prueflauf_to_payload
from adapters.persistence.postgresql.schema import PrueflaufRow
from domain.pruefausfuehrung.prueflauf import Prueflauf


class PostgresPrueflaufRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, prueflauf: Prueflauf, *, commit: bool = False) -> None:
        row = self._session.get(PrueflaufRow, prueflauf.prueflauf_id)
        payload = prueflauf_to_payload(prueflauf)
        if row is None:
            self._session.add(
                PrueflaufRow(
                    prueflauf_id=prueflauf.prueflauf_id,
                    version_id=prueflauf.version_id,
                    produktkodierung=prueflauf.produktkodierung,
                    payload=payload,
                )
            )
        else:
            row.version_id = prueflauf.version_id
            row.produktkodierung = prueflauf.produktkodierung
            row.payload = payload
        if commit:
            self._session.commit()

    def get(self, prueflauf_id: str) -> Prueflauf | None:
        row = self._session.get(PrueflaufRow, prueflauf_id)
        if row is None:
            return None
        return prueflauf_from_payload(row.payload)
