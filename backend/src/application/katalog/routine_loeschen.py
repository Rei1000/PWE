"""Use Case — Routine löschen."""

from __future__ import annotations

from dataclasses import dataclass

from application.katalog.bibliothek_referenzen import ist_routine_in_verwendung
from domain.katalog.errors import RoutineInVerwendung, RoutineNichtGefunden
from ports.bibliothek_repository import BibliothekRepository
from ports.katalog_repository import KatalogRepository


@dataclass
class RoutineLoeschen:
    katalog: KatalogRepository
    bibliothek: BibliothekRepository

    def execute(self, routine_id: str) -> None:
        if self.bibliothek.get_routine(routine_id) is None:
            raise RoutineNichtGefunden(f"Routine {routine_id} nicht gefunden")
        if ist_routine_in_verwendung(self.katalog, routine_id):
            raise RoutineInVerwendung(f"Routine {routine_id} wird noch referenziert")
        self.bibliothek.delete_routine(routine_id)
