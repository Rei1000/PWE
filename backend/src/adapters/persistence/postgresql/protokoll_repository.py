"""PostgreSQL-Implementierung — ProtokollRepository."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from adapters.persistence.postgresql.mapping import snapshot_from_payload, snapshot_to_payload
from adapters.persistence.postgresql.schema import ProtokollSnapshotRow
from domain.protokoll.snapshot import ProtokollSnapshot


class PostgresProtokollRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, snapshot: ProtokollSnapshot) -> None:
        existing = self._session.get(ProtokollSnapshotRow, snapshot.snapshot_id)
        if existing is not None:
            return
        self._session.add(
            ProtokollSnapshotRow(
                snapshot_id=snapshot.snapshot_id,
                prueflauf_id=snapshot.prueflauf_id,
                payload=snapshot_to_payload(snapshot),
            )
        )
        self._session.commit()

    def get_by_prueflauf(self, prueflauf_id: str) -> ProtokollSnapshot | None:
        row = self._session.execute(
            select(ProtokollSnapshotRow).where(ProtokollSnapshotRow.prueflauf_id == prueflauf_id)
        ).scalar_one_or_none()
        if row is None:
            return None
        return snapshot_from_payload(row.payload)
