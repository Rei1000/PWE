"""Use Case: Materialisiertes Externes Kommando ausführen und Nachweise erfassen."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from application.pruefausfuehrung.automatisierung_audit import AutomatisierungAuditKontext
from application.pruefausfuehrung.kommando_ausfuehrung_kern import kommandoausfuehrung_kern
from domain.katalog.routine import MaterialisierteRoutineHerkunft
from domain.pruefausfuehrung.errors import (
    ExternesKommandoAdapterFehler,
    KommandoNichtFreigegeben,
    MaterialisierterProzedurSchrittNichtGefunden,
    PrueflaufNichtGefunden,
    VersionNichtGefunden,
)
from domain.pruefausfuehrung.prueflauf import Nachweis
from ports.externes_kommando_port import ExternesKommandoPort
from ports.katalog_repository import KatalogRepository
from ports.prueflauf_repository import PrueflaufRepository


@dataclass(frozen=True)
class ExternesKommandoAusfuehrungErgebnis:
    """Ergebnis der Kommandoausführung — Nachweise und fachlicher Ausführungsstatus."""

    nachweise: list[Nachweis]
    fehlgeschlagen: bool


@dataclass
class ExternesKommandoAusfuehren:
    katalog: KatalogRepository
    prueflauf_repo: PrueflaufRepository
    kommando_port: ExternesKommandoPort

    def execute(
        self,
        prueflauf_id: str,
        prozedur_schritt_id: str,
        kommando_id: str,
    ) -> ExternesKommandoAusfuehrungErgebnis:
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

        snapshot = schritt.externes_kommando
        if snapshot is None or snapshot.kommando_id != kommando_id:
            raise KommandoNichtFreigegeben(
                f"Kommando {kommando_id} ist für ProzedurSchritt {prozedur_schritt_id} nicht freigegeben"
            )

        audit = AutomatisierungAuditKontext(
            ausfuehrung_id=str(uuid4()),
            herkunft=MaterialisierteRoutineHerkunft.EINZELKOMMANDO,
            aktion_position=1,
            kommando_id=kommando_id,
        )
        kern = kommandoausfuehrung_kern(
            prueflauf,
            prozedur_schritt_id,
            snapshot,
            self.kommando_port,
            audit,
        )

        if kern.fehlgeschlagen and not kern.nachweise:
            raise ExternesKommandoAdapterFehler(
                f"Ausführung des Kommandos {kommando_id} fehlgeschlagen"
            )

        self.prueflauf_repo.save(prueflauf)
        return ExternesKommandoAusfuehrungErgebnis(
            nachweise=kern.nachweise,
            fehlgeschlagen=kern.fehlgeschlagen,
        )
