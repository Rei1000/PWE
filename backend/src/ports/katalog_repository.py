"""Ports — Katalog."""

from __future__ import annotations

from typing import Protocol

from domain.katalog.version import ProduktdefinitionsVersion


class KatalogRepository(Protocol):
    def get_aktive_version_fuer_kodierung(
        self, produktkodierung: str
    ) -> ProduktdefinitionsVersion | None: ...

    def save_version(self, version: ProduktdefinitionsVersion) -> None: ...
