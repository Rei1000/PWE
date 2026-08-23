"""Identity — immutable Audit-Eintrag (Gate 8.1c1)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from domain.shared.errors import InvariantViolation


@dataclass(frozen=True)
class IdentityAuditEintrag:
    """Append-only Audit — nie Update/Delete fachlich."""

    audit_id: str
    akteur_benutzer_id: str
    aktion: str
    zeitpunkt: datetime
    ziel_benutzer_id: str | None = None
    referenz_id: str | None = None
    details: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def erzeugen(
        cls,
        *,
        akteur_benutzer_id: str,
        aktion: str,
        ziel_benutzer_id: str | None = None,
        referenz_id: str | None = None,
        details: dict[str, Any] | None = None,
        zeitpunkt: datetime | None = None,
        audit_id: str | None = None,
    ) -> IdentityAuditEintrag:
        akteur = akteur_benutzer_id.strip()
        code = aktion.strip()
        if not akteur:
            raise InvariantViolation("akteur_benutzer_id darf nicht leer sein")
        if not code:
            raise InvariantViolation("aktion darf nicht leer sein")
        safe = dict(details or {})
        for verboten in ("passwort", "passwort_hash", "password", "hash"):
            safe.pop(verboten, None)
        return cls(
            audit_id=audit_id or str(uuid4()),
            akteur_benutzer_id=akteur,
            aktion=code,
            zeitpunkt=zeitpunkt or datetime.now(UTC),
            ziel_benutzer_id=ziel_benutzer_id.strip() if ziel_benutzer_id else None,
            referenz_id=referenz_id.strip() if referenz_id else None,
            details=safe,
        )
