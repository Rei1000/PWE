"""Use Case: Externes Kommando ausführen und Nachweise erfassen."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from domain.pruefausfuehrung.kommando_ausfuehrung import ExternesKommandoAnfrage
from domain.pruefausfuehrung.prueflauf import Nachweis, NachweisArt
from domain.shared.errors import DomainError
from ports.externes_kommando_port import ExternesKommandoPort
from ports.prueflauf_repository import PrueflaufRepository


class PrueflaufNichtGefunden(DomainError):
    pass


@dataclass
class ExternesKommandoAusfuehren:
    prueflauf_repo: PrueflaufRepository
    kommando_port: ExternesKommandoPort

    def execute(
        self,
        prueflauf_id: str,
        prozedur_schritt_id: str,
        kommandocode: str,
        *,
        parameter: dict[str, Any] | None = None,
    ) -> list[Nachweis]:
        prueflauf = self.prueflauf_repo.get(prueflauf_id)
        if prueflauf is None:
            raise PrueflaufNichtGefunden(prueflauf_id)

        antwort = self.kommando_port.ausfuehren(
            ExternesKommandoAnfrage(
                kommandocode=kommandocode,
                parameter=dict(parameter or {}),
            )
        )

        roh_nachweis = prueflauf.add_nachweis(
            prozedur_schritt_id,
            NachweisArt.ROHANTWORT,
            {
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
                    {"feld": feld, "wert": wert},
                    ist_automatisch=True,
                    bezug_nachweis_id=roh_nachweis.nachweis_id,
                )
            )

        self.prueflauf_repo.save(prueflauf)
        return nachweise
