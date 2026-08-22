"""Use Case — Routine aktualisieren."""

from __future__ import annotations

from dataclasses import dataclass

from domain.katalog.errors import ExternesKommandoNichtGefunden, RoutineNichtGefunden
from domain.katalog.routine import (
    Routine,
    RoutineAktion,
    RoutineAktionsart,
    _validiere_aktionen,
)
from domain.shared.errors import InvariantViolation
from ports.bibliothek_repository import BibliothekRepository


@dataclass
class RoutineAktualisieren:
    bibliothek: BibliothekRepository

    def execute(
        self,
        routine_id: str,
        *,
        bezeichnung: str,
        kommando_ids: tuple[str, ...],
    ) -> Routine:
        if self.bibliothek.get_routine(routine_id) is None:
            raise RoutineNichtGefunden(f"Routine {routine_id} nicht gefunden")

        bezeichnung = bezeichnung.strip()
        if not bezeichnung:
            raise InvariantViolation("Bezeichnung der Routine darf nicht leer sein")

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

        aktionen_tuple = tuple(aktionen)
        _validiere_aktionen(aktionen_tuple)

        routine = Routine(
            routine_id=routine_id,
            bezeichnung=bezeichnung,
            aktionen=aktionen_tuple,
        )
        self.bibliothek.save_routine(routine)
        return routine
