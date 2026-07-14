"""Contract-Tests — BibliothekRepository (In-Memory / PostgreSQL)."""

from __future__ import annotations

import pytest

from adapters.persistence.in_memory import InMemoryBibliothekRepository
from adapters.persistence.postgresql.bibliothek_repository import PostgresBibliothekRepository
from domain.katalog.externes_kommando import ExternesKommando
from domain.katalog.routine import Routine, RoutineAktion, RoutineAktionsart


def _sample_kommando(*, bezeichnung: str = "Test", kommandocode: str = "CMD") -> ExternesKommando:
    return ExternesKommando.anlegen(bezeichnung=bezeichnung, kommandocode=kommandocode)


def _sample_routine(kommando_id: str) -> Routine:
    return Routine.anlegen(
        bezeichnung="Test-Routine",
        aktionen=(
            RoutineAktion(
                aktionsart=RoutineAktionsart.EXTERNES_KOMMANDO_AUSFUEHREN,
                kommando_id=kommando_id,
                position=1,
            ),
        ),
    )


def _run_bibliothek_contract(repo_factory):
    repo = repo_factory()
    kommando = _sample_kommando()
    assert repo.get_externes_kommando(kommando.kommando_id) is None

    repo.save_externes_kommando(kommando)
    loaded = repo.get_externes_kommando(kommando.kommando_id)
    assert loaded == kommando

    updated = ExternesKommando(
        kommando_id=kommando.kommando_id,
        bezeichnung="Geändert",
        kommandocode="CMD2",
    )
    repo.save_externes_kommando(updated)
    reloaded = repo.get_externes_kommando(kommando.kommando_id)
    assert reloaded == updated

    routine = _sample_routine(kommando.kommando_id)
    assert repo.get_routine(routine.routine_id) is None
    repo.save_routine(routine)
    loaded_routine = repo.get_routine(routine.routine_id)
    assert loaded_routine == routine

    updated_routine = Routine(
        routine_id=routine.routine_id,
        bezeichnung="Geänderte Routine",
        aktionen=routine.aktionen,
    )
    repo.save_routine(updated_routine)
    reloaded_routine = repo.get_routine(routine.routine_id)
    assert reloaded_routine == updated_routine


def test_in_memory_bibliothek_contract():
    _run_bibliothek_contract(InMemoryBibliothekRepository)


@pytest.mark.postgresql
def test_postgresql_bibliothek_contract(pg_session):
    _run_bibliothek_contract(lambda: PostgresBibliothekRepository(pg_session))
