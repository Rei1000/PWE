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
    RoutineNichtGefunden,
)
from domain.katalog.externes_kommando import ExternesKommando, MaterialisiertesExternesKommando
from domain.katalog.materialisierung import (
    materialisiere_sollvorgaben,
    validiere_materialisierter_schritt_automatisierung,
)
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
    ) -> ProduktdefinitionsVersion:
        if not self.prozedur_schritte:
            raise InvariantViolation("Veröffentlichen erfordert mindestens einen ProzedurSchritt")

        aufgeloeste_kommandos = externe_kommandos or {}
        aufgeloeste_routinen = routinen or {}
        materialisierte: list[MaterialisierterProzedurSchritt] = []
        for schritt in self.prozedur_schritte:
            schritt.validiere_automatisierung()
            materialisierte.append(
                _materialisiere_schritt(
                    schritt,
                    self,
                    aufgeloeste_kommandos,
                    aufgeloeste_routinen,
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


def _materialisiere_schritt(
    schritt: ProzedurSchrittEntwurf,
    entwurf: Produktdefinition,
    kommandos: dict[str, ExternesKommando],
    routinen: dict[str, Routine],
) -> MaterialisierterProzedurSchritt:
    materialisierte_routine: MaterialisierteRoutine | None = None
    externes_kommando: MaterialisiertesExternesKommando | None = None

    if schritt.kommando_id is not None:
        kommando = kommandos.get(schritt.kommando_id)
        if kommando is None:
            raise ExternesKommandoNichtGefunden(
                f"Externes Kommando {schritt.kommando_id} nicht gefunden"
            )
        materialisierte_routine = MaterialisierteRoutine.aus_einzelkommando(kommando=kommando)
        externes_kommando = materialisierte_routine.erstes_kommando_snapshot()
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
        materialisierte_routine=materialisierte_routine,
        externes_kommando=externes_kommando,
    )


def _schritt_aus_automatisierung(
    *,
    schritt_id: str,
    vorlage_id: str,
    ist_pflicht: bool,
    reihenfolge: int,
    sollvorgaben: dict[str, Any],
    materialisierte_routine: MaterialisierteRoutine | None,
    externes_kommando: MaterialisiertesExternesKommando | None,
) -> MaterialisierterProzedurSchritt:
    schritt = MaterialisierterProzedurSchritt(
        schritt_id=schritt_id,
        vorlage_id=vorlage_id,
        ist_pflicht=ist_pflicht,
        reihenfolge=reihenfolge,
        sollvorgaben=sollvorgaben,
        materialisierte_routine=materialisierte_routine,
        externes_kommando=externes_kommando,
    )
    validiere_materialisierter_schritt_automatisierung(schritt)
    return schritt
