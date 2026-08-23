"""Use Case: Produktdefinition veröffentlichen."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from domain.katalog.errors import (
    EntwurfNichtGefunden,
    ExternesKommandoNichtGefunden,
    RoutineNichtGefunden,
    VorlageNichtGefunden,
)
from domain.katalog.externes_kommando import ExternesKommando
from domain.katalog.produktdefinition import Produktdefinition
from domain.katalog.pruefschritt_vorlage import PruefschrittVorlage
from domain.katalog.routine import Routine
from domain.katalog.version import ProduktdefinitionsVersion
from domain.shared.errors import InvariantViolation
from ports.bibliothek_repository import BibliothekRepository
from ports.einweisungsnachweis_repository import EinweisungsnachweisRepository
from ports.katalog_repository import KatalogRepository


@dataclass
class ProduktdefinitionVeroeffentlichen:
    katalog: KatalogRepository
    bibliothek: BibliothekRepository

    def execute(
        self,
        produktdefinition_id: str,
        *,
        einweisung_uebernehmen: bool = False,
        eingewiesen_durch: str | None = None,
        einweisungen: EinweisungsnachweisRepository | None = None,
    ) -> ProduktdefinitionsVersion:
        entwurf = self.katalog.get_entwurf(produktdefinition_id)
        if entwurf is None:
            raise EntwurfNichtGefunden(f"Kein Entwurf: {produktdefinition_id}")

        if einweisung_uebernehmen:
            if not eingewiesen_durch or not eingewiesen_durch.strip():
                raise InvariantViolation(
                    "eingewiesen_durch ist bei Einweisungsübernahme erforderlich"
                )
            if einweisungen is None:
                raise InvariantViolation(
                    "einweisungen-Repository ist bei Einweisungsübernahme erforderlich"
                )

        v_alt = entwurf.aktive_version_id

        for schritt in entwurf.prozedur_schritte:
            schritt.validiere_automatisierung()

        routinen = self._aufloesen_routinen(entwurf)
        externe_kommandos = self._aufloesen_kommandos(entwurf, routinen)
        vorlagen = self._aufloesen_vorlagen(entwurf)
        version = entwurf.veroeffentlichen(
            externe_kommandos=externe_kommandos,
            routinen=routinen,
            vorlagen=vorlagen,
        )
        self.katalog.save_version(version)
        self.katalog.save_entwurf(entwurf)

        if (
            einweisung_uebernehmen
            and v_alt
            and einweisungen is not None
            and eingewiesen_durch
        ):
            jetzt = datetime.now(UTC)
            for alt in einweisungen.list_gueltige_fuer_version(v_alt):
                if not alt.ist_gueltig(jetzt=jetzt):
                    continue
                neu = alt.uebernehmen_auf_version(
                    neue_version_id=version.version_id,
                    eingewiesen_durch=eingewiesen_durch,
                    datum=jetzt,
                )
                einweisungen.save(neu)

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

    def _aufloesen_vorlagen(self, entwurf: Produktdefinition) -> dict[str, PruefschrittVorlage]:
        aufgeloest: dict[str, PruefschrittVorlage] = {}
        for schritt in entwurf.prozedur_schritte:
            if schritt.vorlage_id in aufgeloest:
                continue
            vorlage = self.bibliothek.get_pruefschritt_vorlage(schritt.vorlage_id)
            if vorlage is None:
                raise VorlageNichtGefunden(
                    f"PrüfschrittVorlage {schritt.vorlage_id} nicht gefunden"
                )
            aufgeloest[schritt.vorlage_id] = vorlage
        return aufgeloest
