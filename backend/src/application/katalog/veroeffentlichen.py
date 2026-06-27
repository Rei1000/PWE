"""Use Case: Produktdefinition veröffentlichen."""

from __future__ import annotations

from dataclasses import dataclass

from domain.katalog.produktdefinition import Produktdefinition
from domain.katalog.version import ProduktdefinitionsVersion
from domain.shared.errors import DomainError
from ports.katalog_repository import KatalogRepository


class EntwurfNichtGefunden(DomainError):
    pass


@dataclass
class ProduktdefinitionVeroeffentlichen:
    katalog: KatalogRepository

    def execute(self, produktdefinition_id: str) -> ProduktdefinitionsVersion:
        entwurf = self.katalog.get_entwurf(produktdefinition_id)
        if entwurf is None:
            raise EntwurfNichtGefunden(f"Kein Entwurf: {produktdefinition_id}")

        version = entwurf.veroeffentlichen()
        self.katalog.save_version(version)
        self.katalog.save_entwurf(entwurf)
        return version
