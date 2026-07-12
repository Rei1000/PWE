"""Use Case: Materialisiertes Externes Kommando ausführen und Nachweise erfassen."""

from __future__ import annotations

from dataclasses import dataclass

from domain.pruefausfuehrung.kommando_ausfuehrung import ExternesKommandoAnfrage
from domain.pruefausfuehrung.errors import (
    ExternesKommandoAdapterFehler,
    KommandoNichtFreigegeben,
    MaterialisierterProzedurSchrittNichtGefunden,
    PrueflaufNichtGefunden,
    VersionNichtGefunden,
)
from domain.pruefausfuehrung.prueflauf import Nachweis, NachweisArt
from ports.externes_kommando_port import ExternesKommandoPort
from ports.katalog_repository import KatalogRepository
from ports.prueflauf_repository import PrueflaufRepository


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
    ) -> list[Nachweis]:
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

        kommandocode = snapshot.kommandocode
        antwort = self.kommando_port.ausfuehren(
            ExternesKommandoAnfrage(kommandocode=kommandocode)
        )
        if not antwort.erfolgreich:
            raise ExternesKommandoAdapterFehler(
                f"Ausführung des Kommandos {kommando_id} fehlgeschlagen"
            )

        roh_nachweis = prueflauf.add_nachweis(
            prozedur_schritt_id,
            NachweisArt.ROHANTWORT,
            {
                "kommando_id": kommando_id,
                "kommandocode": kommandocode,
                "rohdaten": antwort.rohdaten,
                "erfolgreich": antwort.erfolgreich,
            },
            ist_automatisch=True,
        )
        nachweise: list[Nachweis] = [roh_nachweis]

        for feld, wert in antwort.extrahierte_werte.items():
            nachweise.append(
                prueflauf.add_nachweis(
                    prozedur_schritt_id,
                    NachweisArt.EXTRAHIERTER_WERT,
                    {
                        "kommando_id": kommando_id,
                        "feld": feld,
                        "wert": wert,
                    },
                    ist_automatisch=True,
                    bezug_nachweis_id=roh_nachweis.nachweis_id,
                )
            )

        self.prueflauf_repo.save(prueflauf)
        return nachweise
