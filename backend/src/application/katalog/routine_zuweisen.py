"""Use Case — routine_id an einen ProzedurSchrittEntwurf zuweisen."""

from __future__ import annotations

from dataclasses import dataclass

from domain.katalog.errors import (
    EntwurfNichtGefunden,
    ProzedurSchrittNichtGefunden,
    RoutineNichtGefunden,
)
from domain.katalog.produktdefinition import Produktdefinition
from ports.bibliothek_repository import BibliothekRepository
from ports.katalog_repository import KatalogRepository


@dataclass
class RoutineProzedurSchrittZuweisen:
    katalog: KatalogRepository
    bibliothek: BibliothekRepository

    def execute(
        self,
        produktdefinition_id: str,
        schritt_id: str,
        routine_id: str | None,
    ) -> Produktdefinition:
        entwurf = self.katalog.get_entwurf(produktdefinition_id)
        if entwurf is None:
            raise EntwurfNichtGefunden(f"Entwurf {produktdefinition_id} nicht gefunden")

        if routine_id is not None and self.bibliothek.get_routine(routine_id) is None:
            raise RoutineNichtGefunden(f"Routine {routine_id} nicht gefunden")

        schritt = next((s for s in entwurf.prozedur_schritte if s.schritt_id == schritt_id), None)
        if schritt is None:
            raise ProzedurSchrittNichtGefunden(f"ProzedurSchritt {schritt_id} nicht gefunden")

        schritt.pruefe_routine_zuweisung(routine_id)
        schritt.routine_id = routine_id
        schritt.validiere_automatisierung()
        self.katalog.save_entwurf(entwurf)
        return entwurf
