"""Contract-Tests — BibliothekRepository (In-Memory / PostgreSQL)."""

from __future__ import annotations

import pytest

from adapters.persistence.in_memory import InMemoryBibliothekRepository
from adapters.persistence.postgresql.bibliothek_repository import PostgresBibliothekRepository
from domain.katalog.externes_kommando import ExternesKommando


def _sample_kommando(*, bezeichnung: str = "Test", kommandocode: str = "CMD") -> ExternesKommando:
    return ExternesKommando.anlegen(bezeichnung=bezeichnung, kommandocode=kommandocode)


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


def test_in_memory_bibliothek_contract():
    _run_bibliothek_contract(InMemoryBibliothekRepository)


@pytest.mark.postgresql
def test_postgresql_bibliothek_contract(pg_session):
    _run_bibliothek_contract(lambda: PostgresBibliothekRepository(pg_session))
