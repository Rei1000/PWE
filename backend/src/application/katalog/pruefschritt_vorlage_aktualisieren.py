"""Use Case — PrüfschrittVorlage aktualisieren."""

from __future__ import annotations

from dataclasses import dataclass

from domain.katalog.errors import VorlageNichtGefunden
from domain.katalog.pruefschritt_vorlage import PruefschrittVorlage
from ports.bibliothek_repository import BibliothekRepository


@dataclass
class PruefschrittVorlageAktualisieren:
    bibliothek: BibliothekRepository

    def execute(
        self,
        vorlage_id: str,
        *,
        bezeichnung: str,
        beschreibung: str | None = None,
    ) -> PruefschrittVorlage:
        vorlage = self.bibliothek.get_pruefschritt_vorlage(vorlage_id)
        if vorlage is None:
            raise VorlageNichtGefunden(f"PrüfschrittVorlage {vorlage_id} nicht gefunden")
        aktualisiert = vorlage.aktualisieren(
            bezeichnung=bezeichnung,
            beschreibung=beschreibung,
        )
        self.bibliothek.save_pruefschritt_vorlage(aktualisiert)
        return aktualisiert
