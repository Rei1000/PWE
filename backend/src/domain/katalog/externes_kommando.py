"""Katalog-Bibliothek — ExternesKommando (Domain Model §4.11)."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from domain.shared.errors import InvariantViolation


@dataclass(frozen=True)
class MaterialisiertesExternesKommando:
    """Unveränderlicher Snapshot in der ProduktdefinitionsVersion."""

    kommando_id: str
    bezeichnung: str
    kommandocode: str

    @classmethod
    def aus(cls, kommando: ExternesKommando) -> MaterialisiertesExternesKommando:
        return cls(
            kommando_id=kommando.kommando_id,
            bezeichnung=kommando.bezeichnung,
            kommandocode=kommando.kommandocode,
        )


@dataclass(frozen=True)
class ExternesKommando:
    """Aggregate Root — Bibliotheksmodul Katalog."""

    kommando_id: str
    bezeichnung: str
    kommandocode: str

    @classmethod
    def anlegen(cls, *, bezeichnung: str, kommandocode: str) -> ExternesKommando:
        bezeichnung = bezeichnung.strip()
        kommandocode = kommandocode.strip()
        if not bezeichnung:
            raise InvariantViolation("Bezeichnung des externen Kommandos darf nicht leer sein")
        if not kommandocode:
            raise InvariantViolation("Kommandocode darf nicht leer sein")
        return cls(
            kommando_id=str(uuid4()),
            bezeichnung=bezeichnung,
            kommandocode=kommandocode,
        )
