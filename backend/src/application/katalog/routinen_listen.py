"""Use Case — alle Routinen der Bibliothek listen."""

from __future__ import annotations

from dataclasses import dataclass

from domain.katalog.routine import Routine
from ports.bibliothek_repository import BibliothekRepository


@dataclass
class RoutinenListen:
    bibliothek: BibliothekRepository

    def execute(self) -> list[Routine]:
        return self.bibliothek.list_routinen()
