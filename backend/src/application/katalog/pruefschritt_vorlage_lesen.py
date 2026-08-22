"""Use Case — PrüfschrittVorlage lesen."""

from __future__ import annotations

from dataclasses import dataclass

from domain.katalog.errors import VorlageNichtGefunden
from domain.katalog.pruefschritt_vorlage import PruefschrittVorlage
from ports.bibliothek_repository import BibliothekRepository


@dataclass
class PruefschrittVorlageLesen:
    bibliothek: BibliothekRepository

    def execute(self, vorlage_id: str) -> PruefschrittVorlage:
        vorlage = self.bibliothek.get_pruefschritt_vorlage(vorlage_id)
        if vorlage is None:
            raise VorlageNichtGefunden(f"PrüfschrittVorlage {vorlage_id} nicht gefunden")
        return vorlage
