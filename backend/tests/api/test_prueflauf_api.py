"""API-Integrationstests — Prüflauf-Happy-Path über HTTP."""

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


def test_health(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_api_prueflauf_happy_path_mit_pdf(client: TestClient):
    start = client.post(
        "/prueflaeufe",
        json={
            "produktkodierung": "1234567890",
            "pruefobjekt_kennung": "GER-800",
            "pruefer_id": "pruefer-1",
        },
    )
    assert start.status_code == 201
    prueflauf_id = start.json()["prueflauf_id"]

    komp = client.post(
        f"/prueflaeufe/{prueflauf_id}/komponenten",
        json={"komponenten_typ": "mainboard", "seriennummer": "MB-8"},
    )
    assert komp.status_code == 201

    nachweis = client.post(
        f"/prueflaeufe/{prueflauf_id}/schritte/schritt-a/nachweise",
        json={"art": "messwert", "payload": {"spannung": 230}},
    )
    assert nachweis.status_code == 201

    beurteilung = client.post(f"/prueflaeufe/{prueflauf_id}/schritte/schritt-a/beurteilung")
    assert beurteilung.status_code == 204

    abschluss = client.post(f"/prueflaeufe/{prueflauf_id}/abschluss")
    assert abschluss.status_code == 200
    assert abschluss.json()["ist_gueltig"] is True

    pdf = client.get(f"/prueflaeufe/{prueflauf_id}/protokoll/pdf")
    assert pdf.status_code == 200
    assert pdf.headers["content-type"] == "application/pdf"
    assert pdf.content.startswith(b"%PDF")


def test_api_start_ohne_version_404(client: TestClient):
    response = client.post(
        "/prueflaeufe",
        json={
            "produktkodierung": "UNKNOWN",
            "pruefobjekt_kennung": "GER-1",
            "pruefer_id": "pruefer-1",
        },
    )
    assert response.status_code == 404
