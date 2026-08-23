"""Port — Identity-Audit append-only."""

from __future__ import annotations

from typing import Protocol

from domain.identity.identity_audit import IdentityAuditEintrag


class IdentityAuditRepository(Protocol):
    def append(self, eintrag: IdentityAuditEintrag) -> None: ...

    def list_all(self) -> list[IdentityAuditEintrag]: ...

    def get(self, audit_id: str) -> IdentityAuditEintrag | None: ...
