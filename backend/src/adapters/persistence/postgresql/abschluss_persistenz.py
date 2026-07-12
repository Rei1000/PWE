"""PostgreSQL-Implementierung — PrueflaufAbschlussPersistenz (Request-Transaktion)."""

from __future__ import annotations

from sqlalchemy.orm import Session

from adapters.persistence.postgresql.protokoll_repository import PostgresProtokollRepository
from adapters.persistence.postgresql.prueflauf_repository import PostgresPrueflaufRepository
from domain.pruefausfuehrung.prueflauf import Prueflauf
from domain.protokoll.snapshot import ProtokollSnapshot


class PostgresPrueflaufAbschlussPersistenz:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._prueflauf_repo = PostgresPrueflaufRepository(session)
        self._protokoll_repo = PostgresProtokollRepository(session)

    def speichern(self, prueflauf: Prueflauf, snapshot: ProtokollSnapshot) -> None:
        self._prueflauf_repo.save(prueflauf, commit=False)
        self._protokoll_repo.save(snapshot, commit=False)
