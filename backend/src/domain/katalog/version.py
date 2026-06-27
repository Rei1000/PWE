"""Katalog — materialisierte ProduktdefinitionsVersion (Slice-V1).

Fachliche Referenz: docs/domain-model.md §4.7, §10
Materialisierung: docs/adr/0005-sollvorgaben-materialisierung.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class MaterialisierterProzedurSchritt:
    """Materialisierter ProzedurSchritt in einer Version."""

    schritt_id: str
    vorlage_id: str
    ist_pflicht: bool
    reihenfolge: int
    sollvorgaben: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ProduktdefinitionsVersion:
    """Veröffentlichte, unveränderliche Prüfvorgabe (Domain Model §4.7)."""

    version_id: str
    produktdefinition_id: str
    produktkodierung: str
    prozedur_schritte: tuple[MaterialisierterProzedurSchritt, ...]

    def schritt_by_id(self, schritt_id: str) -> MaterialisierterProzedurSchritt | None:
        for schritt in self.prozedur_schritte:
            if schritt.schritt_id == schritt_id:
                return schritt
        return None

    def aktive_schritte(self) -> tuple[MaterialisierterProzedurSchritt, ...]:
        """V1: alle materialisierten Schritte (Aktivierungsregeln später)."""
        return tuple(sorted(self.prozedur_schritte, key=lambda s: s.reihenfolge))
