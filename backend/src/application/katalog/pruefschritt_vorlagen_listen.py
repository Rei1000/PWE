"""Use Case — PrüfschrittVorlagen listen."""

from __future__ import annotations

from dataclasses import dataclass

from domain.katalog.pruefschritt_vorlage import PruefschrittVorlage
from ports.bibliothek_repository import BibliothekRepository


@dataclass
class PruefschrittVorlagenListen:
    bibliothek: BibliothekRepository

    def execute(self) -> list[PruefschrittVorlage]:
        return self.bibliothek.list_pruefschritt_vorlagen()
