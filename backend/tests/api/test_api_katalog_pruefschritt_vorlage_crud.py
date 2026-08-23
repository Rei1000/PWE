"""API-Tests — PrüfschrittVorlage CRUD (Gate 8.2b1)."""

from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient

from api.app import create_app
from api.deps import in_memory_deps

SCHRIITT_ID = "schritt-a"


def _unique_kodierung() -> str:
    return str(10_000_000_000 + uuid.uuid4().int % 9_000_000_000)


@pytest.fixture
def client():
    with TestClient(create_app(in_memory_deps())) as http_client:
        yield http_client


def _vorlage_anlegen(client: TestClient, *, bezeichnung: str = "Vorlage") -> str:
    response = client.post(
        "/katalog/bibliothek/vorlagen",
        json={"bezeichnung": bezeichnung, "beschreibung": "Beschreibung"},
    )
    assert response.status_code == 201
    return response.json()["vorlage_id"]


def _entwurf_mit_vorlage(client: TestClient, vorlage_id: str, kodierung: str) -> str:
    response = client.post(
        "/katalog/entwuerfe",
        json={
            "produktkodierung": kodierung,
            "prozedur_schritte": [
                {
                    "schritt_id": SCHRIITT_ID,
                    "vorlage_id": vorlage_id,
                    "ist_pflicht": True,
                    "reihenfolge": 1,
                    "sollvorgaben": {},
                }
            ],
            "sollbestueckung": [],
        },
    )
    assert response.status_code == 201
    return response.json()["produktdefinition_id"]


def test_vorlage_crud_http(client: TestClient):
    vorlage_id = _vorlage_anlegen(client, bezeichnung="Messung")

    liste = client.get("/katalog/bibliothek/vorlagen")
    assert liste.status_code == 200
    assert liste.json()["vorlagen"] == [{"vorlage_id": vorlage_id, "bezeichnung": "Messung"}]

    detail = client.get(f"/katalog/bibliothek/vorlagen/{vorlage_id}")
    assert detail.status_code == 200
    assert detail.json() == {
        "vorlage_id": vorlage_id,
        "bezeichnung": "Messung",
        "beschreibung": "Beschreibung",
    }

    update = client.put(
        f"/katalog/bibliothek/vorlagen/{vorlage_id}",
        json={"bezeichnung": "Neu", "beschreibung": None},
    )
    assert update.status_code == 200
    assert update.json()["bezeichnung"] == "Neu"
    assert update.json()["beschreibung"] is None

    delete = client.delete(f"/katalog/bibliothek/vorlagen/{vorlage_id}")
    assert delete.status_code == 204
    assert client.get(f"/katalog/bibliothek/vorlagen/{vorlage_id}").status_code == 404


def test_vorlage_delete_in_verwendung_409(client: TestClient):
    vorlage_id = _vorlage_anlegen(client)
    _entwurf_mit_vorlage(client, vorlage_id, _unique_kodierung())
    response = client.delete(f"/katalog/bibliothek/vorlagen/{vorlage_id}")
    assert response.status_code == 409
    assert response.json()["code"] == "vorlage_in_verwendung"


def test_vorlage_anlegen_extra_feld_422(client: TestClient):
    response = client.post(
        "/katalog/bibliothek/vorlagen",
        json={"bezeichnung": "X", "vorlage_id": "client-id"},
    )
    assert response.status_code == 422
    assert response.json()["code"] == "validation"


def test_veroeffentlichen_unbekannte_vorlage_404(client: TestClient):
    pd_id = _entwurf_mit_vorlage(client, "fehlend", _unique_kodierung())
    response = client.post(f"/katalog/entwuerfe/{pd_id}/veroeffentlichen")
    assert response.status_code == 404
    assert response.json()["code"] == "vorlage_nicht_gefunden"


def test_veroeffentlichen_mit_vorlage_snapshot(client: TestClient):
    vorlage_id = _vorlage_anlegen(client, bezeichnung="Snapshot-V")
    pd_id = _entwurf_mit_vorlage(client, vorlage_id, _unique_kodierung())
    version = client.post(f"/katalog/entwuerfe/{pd_id}/veroeffentlichen")
    assert version.status_code == 201

    client.put(
        f"/katalog/bibliothek/vorlagen/{vorlage_id}",
        json={"bezeichnung": "Geändert"},
    )
    delete = client.delete(f"/katalog/bibliothek/vorlagen/{vorlage_id}")
    assert delete.status_code == 409
    assert delete.json()["code"] == "vorlage_in_verwendung"

    start = client.post(
        "/prueflaeufe",
        json={
            "produktkodierung": version.json()["produktkodierung"],
            "pruefobjekt_kennung": "GER-V",
        },
    )
    assert start.status_code == 201
from tests.support.auth import login_as_admin
