"""Use Case: Produktdefinition (Entwurf) anlegen."""

from __future__ import annotations

from dataclasses import dataclass

from domain.katalog.produktdefinition import Produktdefinition, ProzedurSchrittEntwurf
from ports.katalog_repository import KatalogRepository


@dataclass
class EntwurfAnlegen:
    katalog: KatalogRepository

    def execute(
        self,
        *,
        produktkodierung: str,
        prozedur_schritte: tuple[ProzedurSchrittEntwurf, ...],
        sollbestueckung: tuple[str, ...] = (),
        basisprodukt_sollvorgaben: dict | None = None,
        kundenprofil_sollvorgaben: dict | None = None,
        definition_sollvorgaben: dict | None = None,
    ) -> Produktdefinition:
        entwurf = Produktdefinition.anlegen(produktkodierung=produktkodierung)
        entwurf.prozedur_schritte = list(prozedur_schritte)
        entwurf.sollbestueckung = sollbestueckung
        if basisprodukt_sollvorgaben:
            entwurf.basisprodukt_sollvorgaben = dict(basisprodukt_sollvorgaben)
        if kundenprofil_sollvorgaben:
            entwurf.kundenprofil_sollvorgaben = dict(kundenprofil_sollvorgaben)
        if definition_sollvorgaben:
            entwurf.definition_sollvorgaben = dict(definition_sollvorgaben)

        self.katalog.save_entwurf(entwurf)
        return entwurf
