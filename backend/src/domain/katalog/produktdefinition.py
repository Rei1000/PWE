"""Katalog — Produktdefinition (Entwurf).

Fachliche Referenz: docs/domain-model.md §4.4
Materialisierung: docs/adr/0005-sollvorgaben-materialisierung.md, ADR-0014
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from domain.katalog.errors import (
    AutomatisierungDoppeltZugewiesen,
    ExternesKommandoNichtGefunden,
    ProzedurSchrittNichtGefunden,
    RoutineNichtGefunden,
    SchrittIdBereitsVorhanden,
    UngueltigeSchrittReihenfolge,
    VorlageNichtGefunden,
)
from domain.katalog.externes_kommando import ExternesKommando
from domain.katalog.materialisierung import (
    materialisiere_sollvorgaben,
    validiere_materialisierter_schritt_automatisierung,
)
from domain.katalog.pruefschritt_vorlage import MaterialisiertePruefschrittVorlage, PruefschrittVorlage
from domain.katalog.routine import MaterialisierteRoutine, Routine
from domain.katalog.version import MaterialisierterProzedurSchritt, ProduktdefinitionsVersion
from domain.shared.errors import InvariantViolation


@dataclass
class ProzedurSchrittEntwurf:
    """ProzedurSchritt im Entwurf — noch nicht materialisiert."""

    schritt_id: str
    vorlage_id: str
    ist_pflicht: bool
    reihenfolge: int
    sollvorgaben: dict[str, Any] = field(default_factory=dict)
    kommando_id: str | None = None
    routine_id: str | None = None

    def validiere_automatisierung(self) -> None:
        if self.kommando_id is not None and self.routine_id is not None:
            raise AutomatisierungDoppeltZugewiesen(
                f"ProzedurSchritt {self.schritt_id}: kommando_id und routine_id sind gegenseitig exklusiv"
            )

    def pruefe_kommando_zuweisung(self, kommando_id: str | None) -> None:
        if kommando_id is not None and self.routine_id is not None:
            raise AutomatisierungDoppeltZugewiesen(
                f"ProzedurSchritt {self.schritt_id}: Routine ist gesetzt — "
                "Kommando-Zuweisung erfordert vorheriges Entfernen der Routine"
            )
        if (
            kommando_id is not None
            and self.kommando_id is not None
            and self.kommando_id != kommando_id
        ):
            raise AutomatisierungDoppeltZugewiesen(
                f"ProzedurSchritt {self.schritt_id}: Kommando ist gesetzt — "
                "Wechsel erfordert vorheriges Entfernen der Automatisierung"
            )

    def pruefe_routine_zuweisung(self, routine_id: str | None) -> None:
        if routine_id is not None and self.kommando_id is not None:
            raise AutomatisierungDoppeltZugewiesen(
                f"ProzedurSchritt {self.schritt_id}: Kommando ist gesetzt — "
                "Routine-Zuweisung erfordert vorheriges Entfernen des Kommandos"
            )


@dataclass
class Produktdefinition:
    """Editierbarer Entwurf — wird durch Veröffentlichen zur Version."""

    produktdefinition_id: str
    produktkodierung: str
    basisprodukt_sollvorgaben: dict[str, Any] = field(default_factory=dict)
    kundenprofil_sollvorgaben: dict[str, Any] = field(default_factory=dict)
    definition_sollvorgaben: dict[str, Any] = field(default_factory=dict)
    prozedur_schritte: list[ProzedurSchrittEntwurf] = field(default_factory=list)
    sollbestueckung: tuple[str, ...] = ()
    aktive_version_id: str | None = None

    @classmethod
    def anlegen(cls, *, produktkodierung: str) -> Produktdefinition:
        return cls(
            produktdefinition_id=str(uuid4()),
            produktkodierung=produktkodierung,
        )

    def veroeffentlichen(
        self,
        *,
        externe_kommandos: dict[str, ExternesKommando] | None = None,
        routinen: dict[str, Routine] | None = None,
        vorlagen: dict[str, PruefschrittVorlage] | None = None,
    ) -> ProduktdefinitionsVersion:
        if not self.prozedur_schritte:
            raise InvariantViolation("Veröffentlichen erfordert mindestens einen ProzedurSchritt")

        aufgeloeste_kommandos = externe_kommandos or {}
        aufgeloeste_routinen = routinen or {}
        aufgeloeste_vorlagen = vorlagen or {}
        materialisierte: list[MaterialisierterProzedurSchritt] = []
        for schritt in self.prozedur_schritte:
            schritt.validiere_automatisierung()
            materialisierte.append(
                _materialisiere_schritt(
                    schritt,
                    self,
                    aufgeloeste_kommandos,
                    aufgeloeste_routinen,
                    aufgeloeste_vorlagen,
                )
            )
        materialisierte_tuple = tuple(materialisierte)

        version = ProduktdefinitionsVersion(
            version_id=str(uuid4()),
            produktdefinition_id=self.produktdefinition_id,
            produktkodierung=self.produktkodierung,
            prozedur_schritte=materialisierte_tuple,
            sollbestueckung=self.sollbestueckung,
        )
        self.aktive_version_id = version.version_id
        return version

    def schritt_hinzufuegen(self, schritt: ProzedurSchrittEntwurf) -> ProzedurSchrittEntwurf:
        schritt_id = schritt.schritt_id.strip()
        if not schritt_id:
            raise InvariantViolation("ProzedurSchritt erfordert eine nicht-leere schritt_id")
        if any(s.schritt_id == schritt_id for s in self.prozedur_schritte):
            raise SchrittIdBereitsVorhanden(
                f"ProzedurSchritt {schritt_id} existiert bereits im Entwurf"
            )
        naechste_reihenfolge = (
            max((s.reihenfolge for s in self.prozedur_schritte), default=0) + 1
        )
        neu = ProzedurSchrittEntwurf(
            schritt_id=schritt_id,
            vorlage_id=schritt.vorlage_id,
            ist_pflicht=schritt.ist_pflicht,
            reihenfolge=naechste_reihenfolge,
            sollvorgaben=dict(schritt.sollvorgaben),
        )
        self.prozedur_schritte.append(neu)
        return neu

    def schritt_aktualisieren(
        self,
        schritt_id: str,
        *,
        vorlage_id: str,
        ist_pflicht: bool,
        sollvorgaben: dict[str, Any],
    ) -> ProzedurSchrittEntwurf:
        schritt = self._schritt_oder_fehler(schritt_id)
        aktualisiert = ProzedurSchrittEntwurf(
            schritt_id=schritt.schritt_id,
            vorlage_id=vorlage_id,
            ist_pflicht=ist_pflicht,
            reihenfolge=schritt.reihenfolge,
            sollvorgaben=dict(sollvorgaben),
            kommando_id=schritt.kommando_id,
            routine_id=schritt.routine_id,
        )
        idx = self.prozedur_schritte.index(schritt)
        self.prozedur_schritte[idx] = aktualisiert
        return aktualisiert

    def schritt_entfernen(self, schritt_id: str) -> None:
        schritt = self._schritt_oder_fehler(schritt_id)
        self.prozedur_schritte.remove(schritt)
        self._reihenfolge_normalisieren()

    def schritte_neu_ordnen(self, schritt_ids: list[str]) -> None:
        if len(schritt_ids) != len(self.prozedur_schritte):
            raise UngueltigeSchrittReihenfolge(
                "Reihenfolge muss alle Schritt-IDs des Entwurfs exakt einmal enthalten"
            )
        if len(set(schritt_ids)) != len(schritt_ids):
            raise UngueltigeSchrittReihenfolge("Schritt-IDs in der Reihenfolge müssen eindeutig sein")
        nach_id = {s.schritt_id: s for s in self.prozedur_schritte}
        for schritt_id in schritt_ids:
            if schritt_id not in nach_id:
                raise ProzedurSchrittNichtGefunden(f"ProzedurSchritt {schritt_id} nicht gefunden")
        self.prozedur_schritte = [
            ProzedurSchrittEntwurf(
                schritt_id=nach_id[sid].schritt_id,
                vorlage_id=nach_id[sid].vorlage_id,
                ist_pflicht=nach_id[sid].ist_pflicht,
                reihenfolge=position,
                sollvorgaben=dict(nach_id[sid].sollvorgaben),
                kommando_id=nach_id[sid].kommando_id,
                routine_id=nach_id[sid].routine_id,
            )
            for position, sid in enumerate(schritt_ids, start=1)
        ]

    def _schritt_oder_fehler(self, schritt_id: str) -> ProzedurSchrittEntwurf:
        schritt = next((s for s in self.prozedur_schritte if s.schritt_id == schritt_id), None)
        if schritt is None:
            raise ProzedurSchrittNichtGefunden(f"ProzedurSchritt {schritt_id} nicht gefunden")
        return schritt

    def _reihenfolge_normalisieren(self) -> None:
        sortiert = sorted(self.prozedur_schritte, key=lambda s: s.reihenfolge)
        self.prozedur_schritte = [
            ProzedurSchrittEntwurf(
                schritt_id=s.schritt_id,
                vorlage_id=s.vorlage_id,
                ist_pflicht=s.ist_pflicht,
                reihenfolge=position,
                sollvorgaben=dict(s.sollvorgaben),
                kommando_id=s.kommando_id,
                routine_id=s.routine_id,
            )
            for position, s in enumerate(sortiert, start=1)
        ]


def _materialisiere_schritt(
    schritt: ProzedurSchrittEntwurf,
    entwurf: Produktdefinition,
    kommandos: dict[str, ExternesKommando],
    routinen: dict[str, Routine],
    vorlagen: dict[str, PruefschrittVorlage],
) -> MaterialisierterProzedurSchritt:
    vorlage = vorlagen.get(schritt.vorlage_id)
    if vorlage is None:
        raise VorlageNichtGefunden(f"PrüfschrittVorlage {schritt.vorlage_id} nicht gefunden")

    materialisierte_routine: MaterialisierteRoutine | None = None

    if schritt.kommando_id is not None:
        kommando = kommandos.get(schritt.kommando_id)
        if kommando is None:
            raise ExternesKommandoNichtGefunden(
                f"Externes Kommando {schritt.kommando_id} nicht gefunden"
            )
        materialisierte_routine = MaterialisierteRoutine.aus_einzelkommando(kommando=kommando)
    elif schritt.routine_id is not None:
        routine = routinen.get(schritt.routine_id)
        if routine is None:
            raise RoutineNichtGefunden(f"Routine {schritt.routine_id} nicht gefunden")
        materialisierte_routine = MaterialisierteRoutine.aus_bibliothek(
            routine=routine,
            kommandos=kommandos,
        )

    return _schritt_aus_automatisierung(
        schritt_id=schritt.schritt_id,
        vorlage_id=schritt.vorlage_id,
        ist_pflicht=schritt.ist_pflicht,
        reihenfolge=schritt.reihenfolge,
        sollvorgaben=materialisiere_sollvorgaben(
            entwurf.basisprodukt_sollvorgaben,
            entwurf.kundenprofil_sollvorgaben,
            entwurf.definition_sollvorgaben,
            schritt.sollvorgaben,
        ),
        materialisierte_vorlage=MaterialisiertePruefschrittVorlage.aus(vorlage),
        materialisierte_routine=materialisierte_routine,
    )


def _schritt_aus_automatisierung(
    *,
    schritt_id: str,
    vorlage_id: str,
    ist_pflicht: bool,
    reihenfolge: int,
    sollvorgaben: dict[str, Any],
    materialisierte_vorlage: MaterialisiertePruefschrittVorlage,
    materialisierte_routine: MaterialisierteRoutine | None,
) -> MaterialisierterProzedurSchritt:
    # Gate 7.4b Write Exit: kein Legacy-Snapshot mehr; Lesen alter Daten bleibt.
    schritt = MaterialisierterProzedurSchritt(
        schritt_id=schritt_id,
        vorlage_id=vorlage_id,
        ist_pflicht=ist_pflicht,
        reihenfolge=reihenfolge,
        sollvorgaben=sollvorgaben,
        materialisierte_vorlage=materialisierte_vorlage,
        materialisierte_routine=materialisierte_routine,
        externes_kommando=None,
    )
    validiere_materialisierter_schritt_automatisierung(schritt)
    return schritt
