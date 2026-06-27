"""Use Case: Schritt aus Sollvorgaben beurteilen (ADR-0007)."""

from __future__ import annotations

from dataclasses import dataclass

from domain.shared.errors import DomainError
from ports.katalog_repository import KatalogRepository
from ports.prueflauf_repository import PrueflaufRepository


class PrueflaufNichtGefunden(DomainError):
    pass


class VersionNichtAufloesbar(DomainError):
    pass


@dataclass
class SchrittBeurteilen:
    katalog: KatalogRepository
    prueflauf_repo: PrueflaufRepository

    def execute(self, prueflauf_id: str, prozedur_schritt_id: str) -> Beurteilung:
        prueflauf = self.prueflauf_repo.get(prueflauf_id)
        if prueflauf is None:
            raise PrueflaufNichtGefunden(prueflauf_id)

        version = self.katalog.get_version(prueflauf.version_id)
        if version is None:
            raise VersionNichtAufloesbar(prueflauf.produktkodierung)

        schritt = version.schritt_by_id(prozedur_schritt_id)
        if schritt is None:
            raise DomainError(f"ProzedurSchritt {prozedur_schritt_id} nicht in Version")

        beurteilung = prueflauf.beurteilen_schritt(prozedur_schritt_id, schritt.sollvorgaben)
        self.prueflauf_repo.save(prueflauf)
        return beurteilung
