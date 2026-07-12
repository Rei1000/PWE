"""PostgreSQL-Implementierung — ProtokollRepository."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from adapters.persistence.postgresql.mapping import snapshot_from_payload, snapshot_to_payload
from adapters.persistence.postgresql.schema import ProtokollSnapshotRow
from domain.protokoll.snapshot import ProtokollSnapshot
from domain.shared.errors import UnveraenderlichesObjektBereitsVorhanden


class PostgresProtokollRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, snapshot: ProtokollSnapshot, *, commit: bool = False) -> None:
        existing_id = self._session.get(ProtokollSnapshotRow, snapshot.snapshot_id)
        if existing_id is not None:
            raise UnveraenderlichesObjektBereitsVorhanden(
                f"ProtokollSnapshot {snapshot.snapshot_id} existiert bereits"
            )
        existing_run = self._session.execute(
            select(ProtokollSnapshotRow).where(
                ProtokollSnapshotRow.prueflauf_id == snapshot.prueflauf_id
            )
        ).scalar_one_or_none()
        if existing_run is not None:
            raise UnveraenderlichesObjektBereitsVorhanden(
                f"ProtokollSnapshot für Prüflauf {snapshot.prueflauf_id} existiert bereits"
            )
        self._session.add(
            ProtokollSnapshotRow(
                snapshot_id=snapshot.snapshot_id,
                prueflauf_id=snapshot.prueflauf_id,
                payload=snapshot_to_payload(snapshot),
            )
        )
        if commit:
            self._session.commit()

    def get_by_prueflauf(self, prueflauf_id: str) -> ProtokollSnapshot | None:
        row = self._session.execute(
            select(ProtokollSnapshotRow).where(ProtokollSnapshotRow.prueflauf_id == prueflauf_id)
        ).scalar_one_or_none()
        if row is None:
            return None
        return snapshot_from_payload(row.payload)
