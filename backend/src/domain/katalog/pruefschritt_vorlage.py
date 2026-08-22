"""Katalog-Bibliothek — PrüfschrittVorlage (Domain Model §4.9, ADR-0020)."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from domain.shared.errors import InvariantViolation


@dataclass(frozen=True)
class MaterialisiertePruefschrittVorlage:
    """Unveränderlicher Vorlagen-Snapshot in der ProduktdefinitionsVersion."""

    vorlage_id: str
    bezeichnung: str
    beschreibung: str | None = None

    @classmethod
    def aus(cls, vorlage: PruefschrittVorlage) -> MaterialisiertePruefschrittVorlage:
        return cls(
            vorlage_id=vorlage.vorlage_id,
            bezeichnung=vorlage.bezeichnung,
            beschreibung=vorlage.beschreibung,
        )


@dataclass(frozen=True)
class PruefschrittVorlage:
    """Aggregate Root — Bibliotheksmodul Katalog."""

    vorlage_id: str
    bezeichnung: str
    beschreibung: str | None = None

    @classmethod
    def anlegen(
        cls,
        *,
        bezeichnung: str,
        beschreibung: str | None = None,
    ) -> PruefschrittVorlage:
        bezeichnung = bezeichnung.strip()
        if not bezeichnung:
            raise InvariantViolation("PrüfschrittVorlage erfordert eine nicht-leere Bezeichnung")
        beschreibung_normalized = beschreibung.strip() if beschreibung is not None else None
        if beschreibung_normalized == "":
            beschreibung_normalized = None
        return cls(
            vorlage_id=str(uuid4()),
            bezeichnung=bezeichnung,
            beschreibung=beschreibung_normalized,
        )

    def aktualisieren(
        self,
        *,
        bezeichnung: str,
        beschreibung: str | None = None,
    ) -> PruefschrittVorlage:
        bezeichnung = bezeichnung.strip()
        if not bezeichnung:
            raise InvariantViolation("PrüfschrittVorlage erfordert eine nicht-leere Bezeichnung")
        beschreibung_normalized = beschreibung.strip() if beschreibung is not None else None
        if beschreibung_normalized == "":
            beschreibung_normalized = None
        return PruefschrittVorlage(
            vorlage_id=self.vorlage_id,
            bezeichnung=bezeichnung,
            beschreibung=beschreibung_normalized,
        )
