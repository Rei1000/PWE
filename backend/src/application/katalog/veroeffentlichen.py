"""Use Case: Produktdefinition veröffentlichen."""

from __future__ import annotations

from dataclasses import dataclass

from domain.katalog.errors import (
    EntwurfNichtGefunden,
    ExternesKommandoNichtGefunden,
    RoutineNichtGefunden,
)
from domain.katalog.externes_kommando import ExternesKommando
from domain.katalog.produktdefinition import Produktdefinition
from domain.katalog.routine import Routine
from domain.katalog.version import ProduktdefinitionsVersion
from ports.bibliothek_repository import BibliothekRepository
from ports.katalog_repository import KatalogRepository


@dataclass
class ProduktdefinitionVeroeffentlichen:
    katalog: KatalogRepository
    bibliothek: BibliothekRepository

    def execute(self, produktdefinition_id: str) -> ProduktdefinitionsVersion:
        entwurf = self.katalog.get_entwurf(produktdefinition_id)
        if entwurf is None:
            raise EntwurfNichtGefunden(f"Kein Entwurf: {produktdefinition_id}")

        for schritt in entwurf.prozedur_schritte:
            schritt.validiere_automatisierung()

        routinen = self._aufloesen_routinen(entwurf)
        externe_kommandos = self._aufloesen_kommandos(entwurf, routinen)
        version = entwurf.veroeffentlichen(
            externe_kommandos=externe_kommandos,
            routinen=routinen,
        )
        self.katalog.save_version(version)
        self.katalog.save_entwurf(entwurf)
        return version

    def _aufloesen_routinen(self, entwurf: Produktdefinition) -> dict[str, Routine]:
        aufgeloest: dict[str, Routine] = {}
        for schritt in entwurf.prozedur_schritte:
            if schritt.routine_id is None:
                continue
            if schritt.routine_id in aufgeloest:
                continue
            routine = self.bibliothek.get_routine(schritt.routine_id)
            if routine is None:
                raise RoutineNichtGefunden(f"Routine {schritt.routine_id} nicht gefunden")
            aufgeloest[schritt.routine_id] = routine
        return aufgeloest

    def _aufloesen_kommandos(
        self,
        entwurf: Produktdefinition,
        routinen: dict[str, Routine],
    ) -> dict[str, ExternesKommando]:
        aufgeloest: dict[str, ExternesKommando] = {}
        kommando_ids: set[str] = set()

        for schritt in entwurf.prozedur_schritte:
            if schritt.kommando_id is not None:
                kommando_ids.add(schritt.kommando_id)

        for routine in routinen.values():
            for aktion in routine.aktionen:
                kommando_ids.add(aktion.kommando_id)

        for kommando_id in kommando_ids:
            kommando = self.bibliothek.get_externes_kommando(kommando_id)
            if kommando is None:
                raise ExternesKommandoNichtGefunden(
                    f"Externes Kommando {kommando_id} nicht gefunden"
                )
            aufgeloest[kommando_id] = kommando
        return aufgeloest
