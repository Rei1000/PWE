"""Identity — Aggregate Berechtigungsprofil (Gate 8.1b, ADR-0023/0026)."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from domain.shared.errors import InvariantViolation


@dataclass(frozen=True)
class Berechtigungsprofil:
    """Aggregate Root — Produktlinien-Zugang (Profil ↔ Produktdefinition-IDs)."""

    profil_id: str
    bezeichnung: str
    beschreibung: str | None
    produktdefinition_ids: frozenset[str]

    @classmethod
    def anlegen(
        cls,
        *,
        bezeichnung: str,
        beschreibung: str | None = None,
        produktdefinition_ids: frozenset[str] | set[str] | None = None,
        profil_id: str | None = None,
    ) -> Berechtigungsprofil:
        name = bezeichnung.strip()
        if not name:
            raise InvariantViolation("Bezeichnung darf nicht leer sein")
        desc = beschreibung.strip() if beschreibung and beschreibung.strip() else None
        ids = frozenset(i.strip() for i in (produktdefinition_ids or ()) if i and i.strip())
        return cls(
            profil_id=profil_id or str(uuid4()),
            bezeichnung=name,
            beschreibung=desc,
            produktdefinition_ids=ids,
        )

    def mit_bezeichnung(self, bezeichnung: str, beschreibung: str | None = None) -> Berechtigungsprofil:
        return Berechtigungsprofil.anlegen(
            bezeichnung=bezeichnung,
            beschreibung=beschreibung if beschreibung is not None else self.beschreibung,
            produktdefinition_ids=self.produktdefinition_ids,
            profil_id=self.profil_id,
        )

    def mit_produktdefinitionen(
        self, produktdefinition_ids: frozenset[str] | set[str]
    ) -> Berechtigungsprofil:
        ids = frozenset(i.strip() for i in produktdefinition_ids if i and i.strip())
        return Berechtigungsprofil(
            profil_id=self.profil_id,
            bezeichnung=self.bezeichnung,
            beschreibung=self.beschreibung,
            produktdefinition_ids=ids,
        )

    def deckt_produktdefinition(self, produktdefinition_id: str) -> bool:
        return produktdefinition_id in self.produktdefinition_ids
