"""Ports — Katalog-Bibliothek (Facade für Bibliotheksobjekte)."""

from __future__ import annotations

from typing import Protocol

from domain.katalog.externes_kommando import ExternesKommando
from domain.katalog.routine import Routine


class BibliothekRepository(Protocol):
    def save_externes_kommando(self, kommando: ExternesKommando) -> None: ...

    def get_externes_kommando(self, kommando_id: str) -> ExternesKommando | None: ...

    def save_routine(self, routine: Routine) -> None: ...

    def get_routine(self, routine_id: str) -> Routine | None: ...
