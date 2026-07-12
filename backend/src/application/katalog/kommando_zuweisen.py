"""Use Case — kommando_id an einen ProzedurSchrittEntwurf zuweisen."""

from __future__ import annotations

from dataclasses import dataclass

from domain.katalog.errors import (
    EntwurfNichtGefunden,
    ExternesKommandoNichtGefunden,
    ProzedurSchrittNichtGefunden,
)
from domain.katalog.produktdefinition import Produktdefinition
from ports.bibliothek_repository import BibliothekRepository
from ports.katalog_repository import KatalogRepository


@dataclass
class KommandoProzedurSchrittZuweisen:
    katalog: KatalogRepository
    bibliothek: BibliothekRepository

    def execute(
        self,
        produktdefinition_id: str,
        schritt_id: str,
        kommando_id: str | None,
    ) -> Produktdefinition:
        entwurf = self.katalog.get_entwurf(produktdefinition_id)
        if entwurf is None:
            raise EntwurfNichtGefunden(f"Entwurf {produktdefinition_id} nicht gefunden")

        if kommando_id is not None and self.bibliothek.get_externes_kommando(kommando_id) is None:
            raise ExternesKommandoNichtGefunden(f"Externes Kommando {kommando_id} nicht gefunden")

        schritt = next((s for s in entwurf.prozedur_schritte if s.schritt_id == schritt_id), None)
        if schritt is None:
            raise ProzedurSchrittNichtGefunden(f"ProzedurSchritt {schritt_id} nicht gefunden")

        schritt.kommando_id = kommando_id
        self.katalog.save_entwurf(entwurf)
        return entwurf
