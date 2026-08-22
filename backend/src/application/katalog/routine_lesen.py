"""Use Case — eine Routine lesen."""

from __future__ import annotations

from dataclasses import dataclass

from domain.katalog.errors import RoutineNichtGefunden
from domain.katalog.routine import Routine
from ports.bibliothek_repository import BibliothekRepository


@dataclass
class RoutineLesen:
    bibliothek: BibliothekRepository

    def execute(self, routine_id: str) -> Routine:
        routine = self.bibliothek.get_routine(routine_id)
        if routine is None:
            raise RoutineNichtGefunden(f"Routine {routine_id} nicht gefunden")
        return routine
