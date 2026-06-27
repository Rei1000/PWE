"""API-Integrationstests — Katalog (Entwurf → Veröffentlichen)."""

import pytest
from fastapi.testclient import TestClient

from api.app import create_app
from api.deps import in_memory_deps


@pytest.fixture
def client():
    app = create_app(in_memory_deps())
    with TestClient(app) as http_client:
        yield http_client


def _standard_entwurf_payload(produktkodierung: str = "1234567890") -> dict:
    return {
        "produktkodierung": produktkodierung,
        "prozedur_schritte": [
            {
                "schritt_id": "schritt-a",
                "vorlage_id": "vorlage-a",
                "ist_pflicht": True,
                "reihenfolge": 1,
                "sollvorgaben": {"spannung": {"min": 220, "max": 240}},
            }
        ],
        "sollbestueckung": ["mainboard"],
    }


def test_katalog_entwurf_und_veroeffentlichen(client: TestClient):
    entwurf = client.post("/katalog/entwuerfe", json=_standard_entwurf_payload())
    assert entwurf.status_code == 201
    body = entwurf.json()
    assert body["produktkodierung"] == "1234567890"
    pd_id = body["produktdefinition_id"]
    assert pd_id

    version = client.post(f"/katalog/entwuerfe/{pd_id}/veroeffentlichen")
    assert version.status_code == 201
    vbody = version.json()
    assert vbody["produktdefinition_id"] == pd_id
    assert vbody["produktkodierung"] == "1234567890"
    assert vbody["version_id"]


def test_katalog_veroeffentlichen_ohne_entwurf_404(client: TestClient):
    response = client.post("/katalog/entwuerfe/unbekannt/veroeffentlichen")
    assert response.status_code == 404
    body = response.json()
    assert body["code"] == "entwurf_nicht_gefunden"
    assert "detail" in body


def test_api_prueflauf_nach_katalog_setup(client: TestClient):
    """Frontend-relevanter Flow: Katalog anlegen, dann Prüflauf starten."""
    entwurf = client.post("/katalog/entwuerfe", json=_standard_entwurf_payload("9876543210"))
    pd_id = entwurf.json()["produktdefinition_id"]
    client.post(f"/katalog/entwuerfe/{pd_id}/veroeffentlichen")

    start = client.post(
        "/prueflaeufe",
        json={
            "produktkodierung": "9876543210",
            "pruefobjekt_kennung": "GER-900",
            "pruefer_id": "pruefer-1",
        },
    )
    assert start.status_code == 201
    assert start.json()["produktkodierung"] == "9876543210"
