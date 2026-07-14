"""Use Case: Materialisierte Routine sequenziell ausführen (Gate 7.3e, ADR-0015)."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from application.pruefausfuehrung.automatisierung_audit import AutomatisierungAuditKontext
from application.pruefausfuehrung.kommando_ausfuehrung_kern import (
    KommandoFehlerart,
    kommandoausfuehrung_kern,
)
from domain.katalog.errors import LeereRoutine
from domain.katalog.externes_kommando import MaterialisiertesExternesKommando
from domain.katalog.materialisierung import aufgeloeste_materialisierte_routine
from domain.pruefausfuehrung.errors import (
    MaterialisierterProzedurSchrittNichtGefunden,
    PrueflaufNichtGefunden,
    VersionNichtGefunden,
)
from domain.pruefausfuehrung.prueflauf import Nachweis
from ports.externes_kommando_port import ExternesKommandoPort
from ports.katalog_repository import KatalogRepository
from ports.prueflauf_repository import PrueflaufRepository


@dataclass(frozen=True)
class RoutineAusfuehrungErgebnis:
    ausfuehrung_id: str
    nachweise: list[Nachweis]
    fehlgeschlagen: bool
    abgebrochen_bei_aktion_position: int | None
    ausgefuehrte_aktionen: int
    fehlerart: KommandoFehlerart | None = None


@dataclass
class RoutineAusfuehren:
    katalog: KatalogRepository
    prueflauf_repo: PrueflaufRepository
    kommando_port: ExternesKommandoPort

    def execute(
        self,
        prueflauf_id: str,
        prozedur_schritt_id: str,
    ) -> RoutineAusfuehrungErgebnis:
        prueflauf = self.prueflauf_repo.get(prueflauf_id)
        if prueflauf is None:
            raise PrueflaufNichtGefunden(f"Kein Prüflauf: {prueflauf_id}")

        version = self.katalog.get_version(prueflauf.version_id)
        if version is None:
            raise VersionNichtGefunden(
                f"ProduktdefinitionsVersion {prueflauf.version_id} nicht gefunden"
            )

        schritt = version.schritt_by_id(prozedur_schritt_id)
        if schritt is None:
            raise MaterialisierterProzedurSchrittNichtGefunden(
                f"Materialisierter ProzedurSchritt {prozedur_schritt_id} nicht in Version"
            )

        routine = aufgeloeste_materialisierte_routine(schritt)
        if not routine.aktionen:
            raise LeereRoutine(
                f"ProzedurSchritt {prozedur_schritt_id}: materialisierte Routine ohne Aktionen"
            )

        prueflauf.stelle_offen_sicher()

        ausfuehrung_id = str(uuid4())
        neue_nachweise: list[Nachweis] = []
        ausgefuehrte = 0

        for aktion in sorted(routine.aktionen, key=lambda a: a.position):
            audit = AutomatisierungAuditKontext(
                ausfuehrung_id=ausfuehrung_id,
                herkunft=routine.herkunft,
                aktion_position=aktion.position,
                kommando_id=aktion.kommando_id,
                routine_id=routine.routine_id,
            )
            snapshot = MaterialisiertesExternesKommando(
                kommando_id=aktion.kommando_id,
                bezeichnung=aktion.bezeichnung,
                kommandocode=aktion.kommandocode,
            )
            kern = kommandoausfuehrung_kern(
                prueflauf,
                prozedur_schritt_id,
                snapshot,
                self.kommando_port,
                audit,
            )
            neue_nachweise.extend(kern.nachweise)

            if kern.fehlgeschlagen:
                self.prueflauf_repo.save(prueflauf)
                return RoutineAusfuehrungErgebnis(
                    ausfuehrung_id=ausfuehrung_id,
                    nachweise=neue_nachweise,
                    fehlgeschlagen=True,
                    abgebrochen_bei_aktion_position=aktion.position,
                    ausgefuehrte_aktionen=ausgefuehrte,
                    fehlerart=kern.fehlerart,
                )

            ausgefuehrte += 1

        self.prueflauf_repo.save(prueflauf)
        return RoutineAusfuehrungErgebnis(
            ausfuehrung_id=ausfuehrung_id,
            nachweise=neue_nachweise,
            fehlgeschlagen=False,
            abgebrochen_bei_aktion_position=None,
            ausgefuehrte_aktionen=ausgefuehrte,
        )


