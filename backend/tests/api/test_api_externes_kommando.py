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


def test_api_kein_kommandocode_im_request(client: TestClient):
    prueflauf_id = _start_prueflauf(client)

    response = client.post(
        f"/prueflaeufe/{prueflauf_id}/schritte/schritt-a/kommandos/{KOMMANDO_ID}/ausfuehren",
        json={"kommandocode": "HACK"},
    )

    assert response.status_code == 201
    detail = client.get(f"/prueflaeufe/{prueflauf_id}").json()
    roh = next(n for n in detail["schritte"][0]["nachweise"] if n["art"] == "rohantwort")
    assert roh["payload"]["kommandocode"] == KOMMANDOCODE


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
    assert response.json()["code"] == "prozedur_schritt_nicht_gefunden"


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
    assert response.json()["code"] == "externes_kommando_adapter_fehler"
