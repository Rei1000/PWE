"""Use Case — PrüfschrittVorlage löschen."""

from __future__ import annotations

from dataclasses import dataclass

from application.katalog.bibliothek_referenzen import ist_vorlage_in_verwendung
from domain.katalog.errors import VorlageInVerwendung, VorlageNichtGefunden
from ports.bibliothek_repository import BibliothekRepository
from ports.katalog_repository import KatalogRepository


@dataclass
class PruefschrittVorlageLoeschen:
    katalog: KatalogRepository
    bibliothek: BibliothekRepository

    def execute(self, vorlage_id: str) -> None:
        if self.bibliothek.get_pruefschritt_vorlage(vorlage_id) is None:
            raise VorlageNichtGefunden(f"PrüfschrittVorlage {vorlage_id} nicht gefunden")
        if ist_vorlage_in_verwendung(self.katalog, vorlage_id):
            raise VorlageInVerwendung(
                f"PrüfschrittVorlage {vorlage_id} wird noch referenziert"
            )
        self.bibliothek.delete_pruefschritt_vorlage(vorlage_id)
