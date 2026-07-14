"""PostgreSQL-API — Automatisierung ausführen (Gate 7.3f)."""

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
from application.katalog.entwurf_anlegen import EntwurfAnlegen
from application.katalog.externes_kommando_anlegen import ExternesKommandoAnlegen
from application.katalog.kommando_zuweisen import KommandoProzedurSchrittZuweisen
from application.katalog.veroeffentlichen import ProduktdefinitionVeroeffentlichen
from application.pruefausfuehrung.pruefung_starten import PruefungStarten
from domain.katalog.produktdefinition import ProzedurSchrittEntwurf
from domain.pruefausfuehrung.kommando_ausfuehrung import ExternesKommandoAntwort
from domain.pruefausfuehrung.prueflauf import NachweisArt

KOMMANDOCODE = "READ_VOLTAGE"


@pytest.mark.postgresql
def test_api_automatisierung_postgresql_happy_path():
    url = os.environ.get("DATABASE_URL")
    if not url:
        pytest.skip("DATABASE_URL nicht gesetzt — PostgreSQL-API-Test übersprungen")

    engine = create_engine(url, future=True)
    init_schema(engine)
    session = sessionmaker(bind=engine, expire_on_commit=False)()

    katalog = PostgresKatalogRepository(session)
    bibliothek = PostgresBibliothekRepository(session)
    prueflauf_repo = PostgresPrueflaufRepository(session)

    kodierung = str(10_000_000_000 + uuid.uuid4().int % 9_000_000_000)
    kommando = ExternesKommandoAnlegen(bibliothek).execute(
        bezeichnung="Spannung messen",
        kommandocode=KOMMANDOCODE,
    )
    entwurf = EntwurfAnlegen(katalog).execute(
        produktkodierung=kodierung,
        prozedur_schritte=(
            ProzedurSchrittEntwurf(
                schritt_id="schritt-a",
                vorlage_id="vorlage-a",
                ist_pflicht=True,
                reihenfolge=1,
            ),
        ),
    )
    KommandoProzedurSchrittZuweisen(katalog, bibliothek).execute(
        entwurf.produktdefinition_id,
        "schritt-a",
        kommando.kommando_id,
    )
    ProduktdefinitionVeroeffentlichen(katalog, bibliothek).execute(entwurf.produktdefinition_id)
    prueflauf = PruefungStarten(katalog, prueflauf_repo).execute(
        produktkodierung=kodierung,
        pruefobjekt_kennung="GER-PG-AUTO",
        pruefer_id="pruefer-pg",
    )
    session.commit()
    prueflauf_id = prueflauf.prueflauf_id
    session.close()

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
        response = client.post(
            f"/prueflaeufe/{prueflauf_id}/schritte/schritt-a/automatisierung/ausfuehren",
            json={},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["fehlgeschlagen"] is False
    assert body["ausfuehrung_id"]
    assert body["ausgefuehrte_aktionen"] == 1
    assert len(body["nachweise"]) == 2
    assert "detail" not in body

    verify_session = sessionmaker(bind=engine, expire_on_commit=False)()
    reloaded = PostgresPrueflaufRepository(verify_session).get(prueflauf_id)
    verify_session.close()
    assert reloaded is not None
    nachweise = reloaded.durchfuehrungen["schritt-a"].nachweise
    assert len(nachweise) == 2
    assert nachweise[0].art == NachweisArt.ROHANTWORT
    assert nachweise[0].payload["kommandocode"] == KOMMANDOCODE
    assert nachweise[1].art == NachweisArt.EXTRAHIERTER_WERT
