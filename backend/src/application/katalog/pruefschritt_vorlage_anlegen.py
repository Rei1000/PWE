"""Use Case — PrüfschrittVorlage in der Bibliothek anlegen."""

from __future__ import annotations

from dataclasses import dataclass

from domain.katalog.pruefschritt_vorlage import PruefschrittVorlage
from ports.bibliothek_repository import BibliothekRepository


@dataclass
class PruefschrittVorlageAnlegen:
    bibliothek: BibliothekRepository

    def execute(
        self,
        *,
        bezeichnung: str,
        beschreibung: str | None = None,
    ) -> PruefschrittVorlage:
        vorlage = PruefschrittVorlage.anlegen(
            bezeichnung=bezeichnung,
            beschreibung=beschreibung,
        )
        self.bibliothek.save_pruefschritt_vorlage(vorlage)
        return vorlage
