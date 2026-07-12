"""API-Negativtests — Fehlercodes und Status."""

import pytest
from fastapi.testclient import TestClient

from adapters.persistence.in_memory import InMemoryKatalogRepository
from api.app import create_app
from api.deps import in_memory_deps
from domain.katalog.version import MaterialisierterProzedurSchritt, ProduktdefinitionsVersion


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
                ),
            ),
            sollbestueckung=("mainboard",),
        )
    )
    app = create_app(deps)
    with TestClient(app) as http_client:
        yield http_client


def _start_prueflauf(client: TestClient) -> str:
    response = client.post(
        "/prueflaeufe",
        json={
            "produktkodierung": "1234567890",
            "pruefobjekt_kennung": "GER-800",
            "pruefer_id": "pruefer-1",
        },
    )
    assert response.status_code == 201
    return response.json()["prueflauf_id"]


def _complete_happy_path(client: TestClient, prueflauf_id: str) -> None:
    client.post(
        f"/prueflaeufe/{prueflauf_id}/komponenten",
        json={"komponenten_typ": "mainboard", "seriennummer": "MB-8"},
    )
    client.post(
        f"/prueflaeufe/{prueflauf_id}/schritte/schritt-a/nachweise",
        json={"art": "messwert", "payload": {"spannung": 230}},
    )
    client.post(f"/prueflaeufe/{prueflauf_id}/schritte/schritt-a/beurteilung")
    client.post(f"/prueflaeufe/{prueflauf_id}/abschluss")


def test_ungueltige_nachweis_art_422(client: TestClient):
    prueflauf_id = _start_prueflauf(client)
    response = client.post(
        f"/prueflaeufe/{prueflauf_id}/schritte/schritt-a/nachweise",
        json={"art": "unbekannt", "payload": {}},
    )
    assert response.status_code == 422
    body = response.json()
    assert body["code"] in {"validation", "ungueltiger_wert"}


def test_pdf_vor_abschluss_404(client: TestClient):
    prueflauf_id = _start_prueflauf(client)
    response = client.get(f"/prueflaeufe/{prueflauf_id}/protokoll/pdf")
    assert response.status_code == 404
    assert "code" in response.json()


def test_mutation_nach_abschluss_409(client: TestClient):
    prueflauf_id = _start_prueflauf(client)
    _complete_happy_path(client, prueflauf_id)

    response = client.post(
        f"/prueflaeufe/{prueflauf_id}/schritte/schritt-a/nachweise",
        json={"art": "messwert", "payload": {"spannung": 230}},
    )
    assert response.status_code == 409
    body = response.json()
    assert body["code"] == "invariant_verletzt"
    assert body["detail"] == "Die Aktion ist im aktuellen Zustand nicht zulässig."


def test_read_model_enthält_fortschritt(client: TestClient):
    prueflauf_id = _start_prueflauf(client)
    response = client.get(f"/prueflaeufe/{prueflauf_id}")
    assert response.status_code == 200
    body = response.json()
    assert body["ist_abgeschlossen"] is False
    assert body["kann_komponente_erfassen"] is True
    assert body["fehlende_komponenten"] == ["mainboard"]
    assert body["schritte"][0]["kann_nachweis_erfassen"] is False
