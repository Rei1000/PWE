"""API-Tests — Externes Kommando ausführen (Gate 7.3b)."""

import pytest
from fastapi.testclient import TestClient

from adapters.persistence.in_memory import InMemoryKatalogRepository
from adapters.simulation.externes_kommando import SimuliertesExternesKommandoPort
from api.app import create_app
from api.deps import in_memory_deps
from domain.katalog.externes_kommando import MaterialisiertesExternesKommando
from domain.katalog.version import MaterialisierterProzedurSchritt, ProduktdefinitionsVersion
from domain.pruefausfuehrung.kommando_ausfuehrung import ExternesKommandoAntwort

KOMMANDO_ID = "cmd-api-voltage"
KOMMANDOCODE = "READ_VOLTAGE"


@pytest.fixture
def client():
    deps = in_memory_deps()
    assert isinstance(deps.katalog, InMemoryKatalogRepository)
    deps.katalog.register_aktive_version(
        ProduktdefinitionsVersion(
            version_id="ver-1",
            produktdefinition_id="pd-1",
            produktkodierung="1234567890",
            prozedur_schritte=(
                MaterialisierterProzedurSchritt(
                    schritt_id="schritt-a",
                    vorlage_id="vorlage-a",
                    ist_pflicht=True,
                    reihenfolge=1,
                    sollvorgaben={"spannung": {"min": 220, "max": 240}},
                    externes_kommando=MaterialisiertesExternesKommando(
                        kommando_id=KOMMANDO_ID,
                        bezeichnung="Spannung messen",
                        kommandocode=KOMMANDOCODE,
                    ),
                ),
            ),
            sollbestueckung=("mainboard",),
        )
    )
    assert isinstance(deps.kommando_port, SimuliertesExternesKommandoPort)
    deps.kommando_port.registriere_antwort(
        KOMMANDOCODE,
        ExternesKommandoAntwort(
            rohdaten="RAW:230",
            extrahierte_werte={"spannung": 230},
        ),
    )
    app = create_app(deps)
    with TestClient(app) as http_client:
        yield http_client


def _start_prueflauf(client: TestClient) -> str:
    response = client.post(
        "/prueflaeufe",
        json={
            "produktkodierung": "1234567890",
            "pruefobjekt_kennung": "GER-API-1",
            "pruefer_id": "pruefer-1",
        },
    )
    assert response.status_code == 201
    return response.json()["prueflauf_id"]


def test_api_kommando_happy_path(client: TestClient):
    prueflauf_id = _start_prueflauf(client)

    response = client.post(
        f"/prueflaeufe/{prueflauf_id}/schritte/schritt-a/kommandos/{KOMMANDO_ID}/ausfuehren"
    )

    assert response.status_code == 201
    body = response.json()
    assert len(body["nachweise"]) == 2
    assert body["nachweise"][0]["art"] == "rohantwort"
    assert body["nachweise"][1]["art"] == "extrahierter_wert"


def test_api_leerer_body(client: TestClient):
    prueflauf_id = _start_prueflauf(client)

    ohne_body = client.post(
        f"/prueflaeufe/{prueflauf_id}/schritte/schritt-a/kommandos/{KOMMANDO_ID}/ausfuehren"
    )
    mit_leerem_json = client.post(
        f"/prueflaeufe/{prueflauf_id}/schritte/schritt-a/kommandos/{KOMMANDO_ID}/ausfuehren",
        json={},
    )

    assert ohne_body.status_code == 201
    assert mit_leerem_json.status_code == 201


def test_api_freier_kommandocode_wird_abgelehnt(client: TestClient):
    prueflauf_id = _start_prueflauf(client)

    response = client.post(
        f"/prueflaeufe/{prueflauf_id}/schritte/schritt-a/kommandos/{KOMMANDO_ID}/ausfuehren",
        json={"kommandocode": "HACK"},
    )

    assert response.status_code == 422
    assert response.json()["code"] == "validation"


def test_api_prueflauf_nicht_gefunden(client: TestClient):
    response = client.post(
        f"/prueflaeufe/fehlend/schritte/schritt-a/kommandos/{KOMMANDO_ID}/ausfuehren"
    )
    assert response.status_code == 404
    assert response.json()["code"] == "prueflauf_nicht_gefunden"


def test_api_falscher_schritt(client: TestClient):
    prueflauf_id = _start_prueflauf(client)
    response = client.post(
        f"/prueflaeufe/{prueflauf_id}/schritte/fehlend/kommandos/{KOMMANDO_ID}/ausfuehren"
    )
    assert response.status_code == 404
    assert response.json()["code"] == "materialisierter_prozedur_schritt_nicht_gefunden"


def test_api_unbekannte_kommando_id(client: TestClient):
    prueflauf_id = _start_prueflauf(client)
    response = client.post(
        f"/prueflaeufe/{prueflauf_id}/schritte/schritt-a/kommandos/fehlend/ausfuehren"
    )
    assert response.status_code == 409
    assert response.json()["code"] == "kommando_nicht_freigegeben"


def test_api_abgeschlossener_prueflauf(client: TestClient):
    prueflauf_id = _start_prueflauf(client)
    client.post(
        f"/prueflaeufe/{prueflauf_id}/komponenten",
        json={"komponenten_typ": "mainboard", "seriennummer": "MB-1"},
    )
    client.post(
        f"/prueflaeufe/{prueflauf_id}/schritte/schritt-a/nachweise",
        json={"art": "messwert", "payload": {"spannung": 230}},
    )
    client.post(f"/prueflaeufe/{prueflauf_id}/schritte/schritt-a/beurteilung")
    client.post(f"/prueflaeufe/{prueflauf_id}/abschluss")

    response = client.post(
        f"/prueflaeufe/{prueflauf_id}/schritte/schritt-a/kommandos/{KOMMANDO_ID}/ausfuehren"
    )
    assert response.status_code == 409
    assert response.json()["code"] == "invariant_verletzt"


def test_api_adapterfehler(client: TestClient):
    prueflauf_id = _start_prueflauf(client)
    deps = client.app.state.deps
    assert isinstance(deps.kommando_port, SimuliertesExternesKommandoPort)
    deps.kommando_port._antworten.clear()

    response = client.post(
        f"/prueflaeufe/{prueflauf_id}/schritte/schritt-a/kommandos/{KOMMANDO_ID}/ausfuehren"
    )
    assert response.status_code == 409
    body = response.json()
    assert body["code"] == "externes_kommando_adapter_fehler"
    assert "nachweise" not in body


def test_api_geraete_err_persistiert_rohantwort(client: TestClient):
    prueflauf_id = _start_prueflauf(client)
    deps = client.app.state.deps
    assert isinstance(deps.kommando_port, SimuliertesExternesKommandoPort)
    deps.kommando_port.registriere_antwort(
        KOMMANDOCODE,
        ExternesKommandoAntwort(
            rohdaten="ERR OUT_OF_RANGE",
            erfolgreich=False,
        ),
    )

    response = client.post(
        f"/prueflaeufe/{prueflauf_id}/schritte/schritt-a/kommandos/{KOMMANDO_ID}/ausfuehren"
    )

    assert response.status_code == 409
    body = response.json()
    assert body["code"] == "externes_kommando_adapter_fehler"
    assert len(body["nachweise"]) == 1
    assert body["nachweise"][0]["art"] == "rohantwort"

    detail = client.get(f"/prueflaeufe/{prueflauf_id}").json()
    schritt = next(s for s in detail["schritte"] if s["schritt_id"] == "schritt-a")
    assert len(schritt["nachweise"]) == 1
    assert schritt["nachweise"][0]["art"] == "rohantwort"


@pytest.mark.postgresql
def test_api_kommando_ausfuehren_postgresql():
    import os
    import uuid

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
    from domain.pruefausfuehrung.prueflauf import NachweisArt

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
        pruefobjekt_kennung="GER-PG-API",
        pruefer_id="pruefer-pg",
    )
    session.commit()
    prueflauf_id = prueflauf.prueflauf_id
    kommando_id = kommando.kommando_id
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
            f"/prueflaeufe/{prueflauf_id}/schritte/schritt-a/kommandos/{kommando_id}/ausfuehren",
            json={},
        )

    assert response.status_code == 201
    body = response.json()
    assert len(body["nachweise"]) == 2

    verify_session = sessionmaker(bind=engine, expire_on_commit=False)()
    reloaded = PostgresPrueflaufRepository(verify_session).get(prueflauf_id)
    verify_session.close()
    assert reloaded is not None
    nachweise = reloaded.durchfuehrungen["schritt-a"].nachweise
    assert len(nachweise) == 2
    assert nachweise[0].art == NachweisArt.ROHANTWORT
    assert nachweise[0].payload["kommandocode"] == KOMMANDOCODE
    assert nachweise[1].art == NachweisArt.EXTRAHIERTER_WERT


@pytest.mark.postgresql
def test_api_kommando_postgresql_ohne_simulation_liefert_adapterfehler():
    import os
    import uuid

    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    from adapters.persistence.postgresql.bibliothek_repository import PostgresBibliothekRepository
    from adapters.persistence.postgresql.katalog_repository import PostgresKatalogRepository
    from adapters.persistence.postgresql.prueflauf_repository import PostgresPrueflaufRepository
    from adapters.persistence.postgresql.schema import init_schema
    from api.app import create_app
    from application.katalog.entwurf_anlegen import EntwurfAnlegen
    from application.katalog.externes_kommando_anlegen import ExternesKommandoAnlegen
    from application.katalog.kommando_zuweisen import KommandoProzedurSchrittZuweisen
    from application.katalog.veroeffentlichen import ProduktdefinitionVeroeffentlichen
    from application.pruefausfuehrung.pruefung_starten import PruefungStarten
    from domain.katalog.produktdefinition import ProzedurSchrittEntwurf

    url = os.environ.get("DATABASE_URL")
    if not url:
        pytest.skip("DATABASE_URL nicht gesetzt")

    engine = create_engine(url, future=True)
    init_schema(engine)
    session = sessionmaker(bind=engine, expire_on_commit=False)()

    katalog = PostgresKatalogRepository(session)
    bibliothek = PostgresBibliothekRepository(session)
    prueflauf_repo = PostgresPrueflaufRepository(session)

    kodierung = str(10_000_000_000 + uuid.uuid4().int % 9_000_000_000)
    kommando = ExternesKommandoAnlegen(bibliothek).execute(
        bezeichnung="Spannung",
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
        pruefobjekt_kennung="GER-PG-API-2",
        pruefer_id="pruefer-pg",
    )
    session.commit()
    prueflauf_id = prueflauf.prueflauf_id
    kommando_id = kommando.kommando_id
    session.close()

    with TestClient(create_app()) as client:
        response = client.post(
            f"/prueflaeufe/{prueflauf_id}/schritte/schritt-a/kommandos/{kommando_id}/ausfuehren",
            json={},
        )

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Die Anfrage konnte aus fachlichen Gründen nicht verarbeitet werden.",
        "code": "externes_kommando_adapter_fehler",
    }


@pytest.mark.postgresql
def test_api_postgresql_geraete_err_commit_rohantwort():
    import os
    import uuid

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

    url = os.environ.get("DATABASE_URL")
    if not url:
        pytest.skip("DATABASE_URL nicht gesetzt")

    engine = create_engine(url, future=True)
    init_schema(engine)
    session = sessionmaker(bind=engine, expire_on_commit=False)()

    katalog = PostgresKatalogRepository(session)
    bibliothek = PostgresBibliothekRepository(session)
    prueflauf_repo = PostgresPrueflaufRepository(session)

    kodierung = str(10_000_000_000 + uuid.uuid4().int % 9_000_000_000)
    kommando = ExternesKommandoAnlegen(bibliothek).execute(
        bezeichnung="Spannung",
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
        pruefobjekt_kennung="GER-PG-API-ERR",
        pruefer_id="pruefer-pg",
    )
    session.commit()
    prueflauf_id = prueflauf.prueflauf_id
    kommando_id = kommando.kommando_id
    session.close()

    def err_simulation_postgres_deps(pg_session):
        deps = postgres_deps(pg_session)
        assert isinstance(deps.kommando_port, SimuliertesExternesKommandoPort)
        deps.kommando_port.registriere_antwort(
            KOMMANDOCODE,
            ExternesKommandoAntwort(
                rohdaten="ERR OUT_OF_RANGE",
                erfolgreich=False,
            ),
        )
        return deps

    with TestClient(create_app(postgres_deps_factory=err_simulation_postgres_deps)) as client:
        response = client.post(
            f"/prueflaeufe/{prueflauf_id}/schritte/schritt-a/kommandos/{kommando_id}/ausfuehren",
            json={},
        )

    assert response.status_code == 409
    body = response.json()
    assert body["code"] == "externes_kommando_adapter_fehler"
    assert len(body["nachweise"]) == 1

    verify_session = sessionmaker(bind=engine, expire_on_commit=False)()
    reloaded = PostgresPrueflaufRepository(verify_session).get(prueflauf_id)
    verify_session.close()
    assert reloaded is not None
    nachweise = reloaded.durchfuehrungen["schritt-a"].nachweise
    assert len(nachweise) == 1
    assert nachweise[0].art == NachweisArt.ROHANTWORT
    assert nachweise[0].payload["rohdaten"] == "ERR OUT_OF_RANGE"
