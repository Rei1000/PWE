"""Use Case — Aktive veröffentlichte Produkte auflisten (Polish A)."""

from __future__ import annotations

from dataclasses import dataclass

from ports.katalog_repository import KatalogRepository


@dataclass(frozen=True)
class AktivesProdukt:
    produktkodierung: str
    produktdefinition_id: str
    version_id: str


@dataclass
class AktiveProdukteListen:
    katalog: KatalogRepository

    def execute(self) -> list[AktivesProdukt]:
        return [
            AktivesProdukt(
                produktkodierung=version.produktkodierung,
                produktdefinition_id=version.produktdefinition_id,
                version_id=version.version_id,
            )
            for version in self.katalog.list_aktive_versionen()
        ]
