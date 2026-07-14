"""PostgreSQL-API — Katalog-Setup E2E (Gate 6.3a)."""

from __future__ import annotations

import os
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from adapters.persistence.postgresql.bibliothek_repository import PostgresBibliothekRepository
from adapters.persistence.postgresql.katalog_repository import PostgresKatalogRepository
from adapters.persistence.postgresql.prueflauf_repository import PostgresPrueflaufRepository
from adapters.persistence.postgresql.schema import init_schema
from adapters.simulation.externes_kommando import SimuliertesExternesKommandoPort
from api.app import create_app
from api.persistence import postgres_deps
from domain.katalog.routine import MaterialisierteRoutineHerkunft
from domain.pruefausfuehrung.kommando_ausfuehrung import ExternesKommandoAntwort

KOMMANDOCODE = "READ_VOLTAGE_PG"
SCHRIITT_ID = "schritt-a"


@pytest.mark.postgresql
def test_postgresql_http_katalog_setup_und_automatisierung():
    url = os.environ.get("DATABASE_URL")
    if not url:
        pytest.skip("DATABASE_URL nicht gesetzt")

    engine = create_engine(url, future=True)
    init_schema(engine)

    kodierung = str(10_000_000_000 + uuid.uuid4().int % 9_000_000_000)

    def simulation_postgres_deps(pg_session):
        deps = postgres_deps(pg_session)
        assert isinstance(deps.kommando_port, SimuliertesExternesKommandoPort)
        deps.kommando_port.registriere_antwort(
            KOMMANDOCODE,
            ExternesKommandoAntwort(
                rohdaten="RAW:230",
                extrahierte_werte={"spannung": 230},
            ),
        )
        return deps

    with TestClient(create_app(postgres_deps_factory=simulation_postgres_deps)) as client:
        kommando = client.post(
            "/katalog/bibliothek/kommandos",
            json={"bezeichnung": "Spannung PG", "kommandocode": KOMMANDOCODE},
        )
        assert kommando.status_code == 201
        kommando_id = kommando.json()["kommando_id"]

        entwurf = client.post(
            "/katalog/entwuerfe",
            json={
                "produktkodierung": kodierung,
                "prozedur_schritte": [
                    {
                        "schritt_id": SCHRIITT_ID,
                        "vorlage_id": "vorlage-a",
                        "ist_pflicht": True,
                        "reihenfolge": 1,
                    }
                ],
            },
        )
        assert entwurf.status_code == 201
        pd_id = entwurf.json()["produktdefinition_id"]

        zuweisung = client.put(
            f"/katalog/entwuerfe/{pd_id}/schritte/{SCHRIITT_ID}/automatisierung",
            json={"kommando_id": kommando_id},
        )
        assert zuweisung.status_code == 200

        version = client.post(f"/katalog/entwuerfe/{pd_id}/veroeffentlichen")
        assert version.status_code == 201
        version_id = version.json()["version_id"]

        start = client.post(
            "/prueflaeufe",
            json={
                "produktkodierung": kodierung,
                "pruefobjekt_kennung": "GER-PG-63A",
                "pruefer_id": "pruefer-pg",
            },
        )
        assert start.status_code == 201
        prueflauf_id = start.json()["prueflauf_id"]

        auto = client.post(
            f"/prueflaeufe/{prueflauf_id}/schritte/{SCHRIITT_ID}/automatisierung/ausfuehren"
        )
        assert auto.status_code == 200
        assert auto.json()["fehlgeschlagen"] is False

    verify_session = sessionmaker(bind=engine, expire_on_commit=False)()
    katalog = PostgresKatalogRepository(verify_session)
    version_obj = katalog.get_version(version_id)
    verify_session.close()
    assert version_obj is not None
    schritt = version_obj.schritt_by_id(SCHRIITT_ID)
    assert schritt is not None
    assert schritt.materialisierte_routine is not None
    assert schritt.materialisierte_routine.herkunft == MaterialisierteRoutineHerkunft.EINZELKOMMANDO
