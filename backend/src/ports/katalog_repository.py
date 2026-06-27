"""Ports — Katalog."""

from __future__ import annotations

from typing import Protocol

from domain.katalog.produktdefinition import Produktdefinition
from domain.katalog.version import ProduktdefinitionsVersion


class KatalogRepository(Protocol):
    def get_aktive_version_fuer_kodierung(
        self, produktkodierung: str
    ) -> ProduktdefinitionsVersion | None: ...

    def get_version(self, version_id: str) -> ProduktdefinitionsVersion | None: ...

    def save_version(self, version: ProduktdefinitionsVersion) -> None: ...

    def get_entwurf(self, produktdefinition_id: str) -> Produktdefinition | None: ...

    def save_entwurf(self, entwurf: Produktdefinition) -> None: ...
