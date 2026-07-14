"""Use Case — Routine in der Bibliothek anlegen."""

from __future__ import annotations

from dataclasses import dataclass

from domain.katalog.errors import ExternesKommandoNichtGefunden
from domain.katalog.routine import Routine, RoutineAktion, RoutineAktionsart
from ports.bibliothek_repository import BibliothekRepository


@dataclass
class RoutineAnlegen:
    bibliothek: BibliothekRepository

    def execute(
        self,
        *,
        bezeichnung: str,
        kommando_ids: tuple[str, ...],
    ) -> Routine:
        aktionen: list[RoutineAktion] = []
        for position, kommando_id in enumerate(kommando_ids, start=1):
            if self.bibliothek.get_externes_kommando(kommando_id) is None:
                raise ExternesKommandoNichtGefunden(
                    f"Externes Kommando {kommando_id} nicht gefunden"
                )
            aktionen.append(
                RoutineAktion(
                    aktionsart=RoutineAktionsart.EXTERNES_KOMMANDO_AUSFUEHREN,
                    kommando_id=kommando_id,
                    position=position,
                )
            )
        routine = Routine.anlegen(bezeichnung=bezeichnung, aktionen=tuple(aktionen))
        self.bibliothek.save_routine(routine)
        return routine
