"""API-Tests — Prüflauf lesen (Read-Slice)."""

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
            version_id="ver-read",
            produktdefinition_id="pd-read",
            produktkodierung="1234567890",
            prozedur_schritte=(
                MaterialisierterProzedurSchritt(
                    schritt_id="schritt-a",
                    vorlage_id="vorlage-a",
                    ist_pflicht=True,
                    reihenfolge=1,
                    sollvorgaben={"spannung": {"min": 220, "max": 240}},
                ),
                MaterialisierterProzedurSchritt(
                    schritt_id="schritt-b",
                    vorlage_id="vorlage-b",
                    ist_pflicht=False,
                    reihenfolge=2,
                    sollvorgaben={},
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
            "pruefobjekt_kennung": "GER-100",
            "pruefer_id": "pruefer-1",
        },
    )
    assert response.status_code == 201
    return response.json()["prueflauf_id"]


def test_get_prueflauf_nach_start(client: TestClient):
    prueflauf_id = _start_prueflauf(client)

    detail = client.get(f"/prueflaeufe/{prueflauf_id}")
    assert detail.status_code == 200
    body = detail.json()

    assert body["prueflauf_id"] == prueflauf_id
    assert body["status"] == "gestartet"
    assert body["produktkodierung"] == "1234567890"
    assert body["sollbestueckung"] == ["mainboard"]
    assert len(body["schritte"]) == 2

    schritt_a = body["schritte"][0]
    assert schritt_a["schritt_id"] == "schritt-a"
    assert schritt_a["ist_pflicht"] is True
    assert schritt_a["sollvorgaben"]["spannung"]["min"] == 220
    assert schritt_a["nachweise"] == []
    assert schritt_a["beurteilung"] is None


def test_get_prueflauf_mit_nachweis_und_beurteilung(client: TestClient):
    prueflauf_id = _start_prueflauf(client)

    client.post(
        f"/prueflaeufe/{prueflauf_id}/schritte/schritt-a/nachweise",
        json={"art": "messwert", "payload": {"spannung": 230}},
    )
    client.post(f"/prueflaeufe/{prueflauf_id}/schritte/schritt-a/beurteilung")

    detail = client.get(f"/prueflaeufe/{prueflauf_id}")
    assert detail.status_code == 200
    body = detail.json()

    schritt_a = next(s for s in body["schritte"] if s["schritt_id"] == "schritt-a")
    assert len(schritt_a["nachweise"]) == 1
    assert schritt_a["nachweise"][0]["art"] == "messwert"
    assert schritt_a["beurteilung"]["ergebnis"] == "bestanden"
    assert body["status"] == "in_bearbeitung"


def test_get_prueflauf_nicht_gefunden_404(client: TestClient):
    response = client.get("/prueflaeufe/unbekannt")
    assert response.status_code == 404
    assert response.json()["code"] == "prueflauf_nicht_gefunden"
