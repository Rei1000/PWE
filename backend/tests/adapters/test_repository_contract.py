"""Contract-Tests — In-Memory- und PostgreSQL-Repositories (Parität)."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from adapters.persistence.in_memory import (
    InMemoryKatalogRepository,
    InMemoryProtokollRepository,
)
from adapters.persistence.postgresql.katalog_repository import PostgresKatalogRepository
from adapters.persistence.postgresql.protokoll_repository import PostgresProtokollRepository
from domain.katalog.version import MaterialisierterProzedurSchritt, ProduktdefinitionsVersion
from domain.protokoll.snapshot import ProtokollSnapshot
from domain.pruefausfuehrung.abschluss_view import PrueflaufAbschlussView
from domain.shared.errors import UnveraenderlichesObjektBereitsVorhanden

_NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def _sample_version(version_id: str = "ver-contract") -> ProduktdefinitionsVersion:
    return ProduktdefinitionsVersion(
        version_id=version_id,
        produktdefinition_id="pd-1",
        produktkodierung="9999999999",
        prozedur_schritte=(
            MaterialisierterProzedurSchritt(
                schritt_id="schritt-a",
                vorlage_id="vorlage-a",
                ist_pflicht=True,
                reihenfolge=1,
                sollvorgaben={"spannung": {"min": 220, "max": 240}},
            ),
        ),
        sollbestueckung=("mainboard",),
    )


def _sample_snapshot(
    *, snapshot_id: str = "snap-1", prueflauf_id: str = "run-1"
) -> ProtokollSnapshot:
    view = PrueflaufAbschlussView(
        prueflauf_id=prueflauf_id,
        version_id="ver-contract",
        pruefobjekt_kennung="GER-1",
        produktkodierung="9999999999",
        pruefer_id="p1",
        gestartet_am=_NOW,
        abgeschlossen_am=_NOW,
        ist_gueltig=True,
        schritte=(),
        fehlende_sollbestueckung=(),
    )
    return ProtokollSnapshot.aus_abschluss(snapshot_id, view)


def test_in_memory_version_insert_only():
    katalog = InMemoryKatalogRepository()
    version = _sample_version()
    katalog.save_version(version)
    with pytest.raises(UnveraenderlichesObjektBereitsVorhanden):
        katalog.save_version(version)


def test_in_memory_protokoll_insert_only():
    protokoll = InMemoryProtokollRepository()
    snapshot = _sample_snapshot()
    protokoll.save(snapshot)
    with pytest.raises(UnveraenderlichesObjektBereitsVorhanden):
        protokoll.save(snapshot)


@pytest.mark.postgresql
def test_postgresql_version_insert_only(pg_session):
    katalog = PostgresKatalogRepository(pg_session)
    version = _sample_version(version_id="ver-pg-contract")
    katalog.save_version(version)
    with pytest.raises(UnveraenderlichesObjektBereitsVorhanden):
        katalog.save_version(version)


@pytest.mark.postgresql
def test_postgresql_protokoll_insert_only(pg_session):
    protokoll = PostgresProtokollRepository(pg_session)
    snapshot = _sample_snapshot(snapshot_id="snap-pg", prueflauf_id="run-pg")
    protokoll.save(snapshot)
    duplicate = _sample_snapshot(snapshot_id="snap-pg-2", prueflauf_id="run-pg")
    with pytest.raises(UnveraenderlichesObjektBereitsVorhanden):
        protokoll.save(duplicate)
