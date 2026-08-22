"""Use Case — Automatisierung von einem Entwurfsschritt entfernen."""

from __future__ import annotations

from dataclasses import dataclass

from domain.katalog.errors import EntwurfNichtGefunden, ProzedurSchrittNichtGefunden
from domain.katalog.produktdefinition import Produktdefinition
from ports.katalog_repository import KatalogRepository


@dataclass
class AutomatisierungEntfernen:
    katalog: KatalogRepository

    def execute(self, produktdefinition_id: str, schritt_id: str) -> Produktdefinition:
        entwurf = self.katalog.get_entwurf(produktdefinition_id)
        if entwurf is None:
            raise EntwurfNichtGefunden(f"Entwurf {produktdefinition_id} nicht gefunden")

        schritt = next((s for s in entwurf.prozedur_schritte if s.schritt_id == schritt_id), None)
        if schritt is None:
            raise ProzedurSchrittNichtGefunden(f"ProzedurSchritt {schritt_id} nicht gefunden")

        schritt.kommando_id = None
        schritt.routine_id = None
        schritt.validiere_automatisierung()
        self.katalog.save_entwurf(entwurf)
        return entwurf
