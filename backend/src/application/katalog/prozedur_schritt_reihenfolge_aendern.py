"""Use Case — Reihenfolge der ProzedurSchritte im Entwurf ändern."""

from __future__ import annotations

from dataclasses import dataclass

from domain.katalog.errors import EntwurfNichtGefunden
from domain.katalog.produktdefinition import Produktdefinition
from ports.katalog_repository import KatalogRepository


@dataclass
class ProzedurSchrittReihenfolgeAendern:
    katalog: KatalogRepository

    def execute(
        self,
        produktdefinition_id: str,
        schritt_ids: list[str],
    ) -> Produktdefinition:
        entwurf = self.katalog.get_entwurf(produktdefinition_id)
        if entwurf is None:
            raise EntwurfNichtGefunden(f"Entwurf {produktdefinition_id} nicht gefunden")

        entwurf.schritte_neu_ordnen(schritt_ids)
        self.katalog.save_entwurf(entwurf)
        return entwurf
