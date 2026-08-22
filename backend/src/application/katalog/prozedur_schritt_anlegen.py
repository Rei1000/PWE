"""Use Case — ProzedurSchritt an Entwurf anlegen."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from domain.katalog.errors import EntwurfNichtGefunden, VorlageNichtGefunden
from domain.katalog.produktdefinition import ProzedurSchrittEntwurf
from ports.bibliothek_repository import BibliothekRepository
from ports.katalog_repository import KatalogRepository


@dataclass
class ProzedurSchrittAnlegen:
    katalog: KatalogRepository
    bibliothek: BibliothekRepository

    def execute(
        self,
        produktdefinition_id: str,
        *,
        schritt_id: str,
        vorlage_id: str,
        ist_pflicht: bool,
        sollvorgaben: dict[str, Any] | None = None,
    ) -> ProzedurSchrittEntwurf:
        entwurf = self.katalog.get_entwurf(produktdefinition_id)
        if entwurf is None:
            raise EntwurfNichtGefunden(f"Entwurf {produktdefinition_id} nicht gefunden")

        if self.bibliothek.get_pruefschritt_vorlage(vorlage_id) is None:
            raise VorlageNichtGefunden(f"PrüfschrittVorlage {vorlage_id} nicht gefunden")

        schritt = entwurf.schritt_hinzufuegen(
            ProzedurSchrittEntwurf(
                schritt_id=schritt_id,
                vorlage_id=vorlage_id,
                ist_pflicht=ist_pflicht,
                reihenfolge=0,
                sollvorgaben=sollvorgaben or {},
            )
        )
        self.katalog.save_entwurf(entwurf)
        return schritt
