"""Use Case: Produktdefinition veröffentlichen."""

from __future__ import annotations

from dataclasses import dataclass

from domain.katalog.errors import EntwurfNichtGefunden, ExternesKommandoNichtGefunden
from domain.katalog.externes_kommando import ExternesKommando
from domain.katalog.produktdefinition import Produktdefinition
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

        externe_kommandos = self._aufloesen_kommandos(entwurf)
        version = entwurf.veroeffentlichen(externe_kommandos=externe_kommandos)
        self.katalog.save_version(version)
        self.katalog.save_entwurf(entwurf)
        return version

    def _aufloesen_kommandos(self, entwurf: Produktdefinition) -> dict[str, ExternesKommando]:
        aufgeloest: dict[str, ExternesKommando] = {}
        for schritt in entwurf.prozedur_schritte:
            if schritt.kommando_id is None:
                continue
            if schritt.kommando_id in aufgeloest:
                continue
            kommando = self.bibliothek.get_externes_kommando(schritt.kommando_id)
            if kommando is None:
                raise ExternesKommandoNichtGefunden(
                    f"Externes Kommando {schritt.kommando_id} nicht gefunden"
                )
            aufgeloest[schritt.kommando_id] = kommando
        return aufgeloest
