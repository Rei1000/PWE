"""PostgreSQL — Identity Audit append-only (Gate 8.1c1)."""

from __future__ import annotations

import json
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from adapters.persistence.postgresql.schema import IdentityAuditRow
from domain.identity.identity_audit import IdentityAuditEintrag


class PostgresIdentityAuditRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def append(self, eintrag: IdentityAuditEintrag) -> None:
        self._session.add(
            IdentityAuditRow(
                audit_id=eintrag.audit_id,
                akteur_benutzer_id=eintrag.akteur_benutzer_id,
                ziel_benutzer_id=eintrag.ziel_benutzer_id,
                aktion=eintrag.aktion,
                zeitpunkt=eintrag.zeitpunkt.isoformat(),
                referenz_id=eintrag.referenz_id,
                details_json=json.dumps(eintrag.details, ensure_ascii=False),
            )
        )

    def get(self, audit_id: str) -> IdentityAuditEintrag | None:
        row = self._session.get(IdentityAuditRow, audit_id)
        return _row_to_audit(row) if row else None

    def list_all(self) -> list[IdentityAuditEintrag]:
        rows = self._session.scalars(
            select(IdentityAuditRow).order_by(IdentityAuditRow.zeitpunkt.desc())
        ).all()
        return [_row_to_audit(r) for r in rows]


def _row_to_audit(row: IdentityAuditRow) -> IdentityAuditEintrag:
    return IdentityAuditEintrag(
        audit_id=row.audit_id,
        akteur_benutzer_id=row.akteur_benutzer_id,
        aktion=row.aktion,
        zeitpunkt=datetime.fromisoformat(row.zeitpunkt),
        ziel_benutzer_id=row.ziel_benutzer_id,
        referenz_id=row.referenz_id,
        details=json.loads(row.details_json),
    )
