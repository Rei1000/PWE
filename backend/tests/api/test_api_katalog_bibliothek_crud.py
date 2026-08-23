"""API-Tests — Bibliothek CRUD (Gate 8.2a)."""

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


def _entwurf_anlegen(client: TestClient, produktkodierung: str) -> str:
    response = client.post(
        "/katalog/entwuerfe",
        json={
            "produktkodierung": produktkodierung,
            "prozedur_schritte": [
                {
                    "schritt_id": SCHRIITT_ID,
                    "vorlage_id": "vorlage-a",
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


def _kommando_anlegen(client: TestClient, *, bezeichnung: str = "K", code: str = "CMD") -> str:
    response = client.post(
        "/katalog/bibliothek/kommandos",
        json={"bezeichnung": bezeichnung, "kommandocode": code},
    )
    assert response.status_code == 201
    return response.json()["kommando_id"]


def test_kommando_crud_http(client: TestClient):
    kommando_id = _kommando_anlegen(client, bezeichnung="Messung", code="MEAS")

    liste = client.get("/katalog/bibliothek/kommandos")
    assert liste.status_code == 200
    body = liste.json()
    assert len(body["kommandos"]) == 1
    assert body["kommandos"][0] == {"kommando_id": kommando_id, "bezeichnung": "Messung"}
    assert "kommandocode" not in body["kommandos"][0]

    detail = client.get(f"/katalog/bibliothek/kommandos/{kommando_id}")
    assert detail.status_code == 200
    assert detail.json() == {
        "kommando_id": kommando_id,
        "bezeichnung": "Messung",
        "kommandocode": "MEAS",
    }

    update = client.put(
        f"/katalog/bibliothek/kommandos/{kommando_id}",
        json={"bezeichnung": "Neu", "kommandocode": "NEW"},
    )
    assert update.status_code == 200
    assert update.json()["kommandocode"] == "NEW"

    delete = client.delete(f"/katalog/bibliothek/kommandos/{kommando_id}")
    assert delete.status_code == 204
    assert client.get(f"/katalog/bibliothek/kommandos/{kommando_id}").status_code == 404


def test_kommando_delete_in_verwendung_409(client: TestClient):
    kommando_id = _kommando_anlegen(client)
    pd_id = _entwurf_anlegen(client, _unique_kodierung())
    client.put(
        f"/katalog/entwuerfe/{pd_id}/schritte/{SCHRIITT_ID}/automatisierung",
        json={"kommando_id": kommando_id},
    )
    response = client.delete(f"/katalog/bibliothek/kommandos/{kommando_id}")
    assert response.status_code == 409
    assert response.json()["code"] == "kommando_in_verwendung"


def test_kommando_update_extra_feld_422(client: TestClient):
    kommando_id = _kommando_anlegen(client)
    response = client.put(
        f"/katalog/bibliothek/kommandos/{kommando_id}",
        json={"bezeichnung": "X", "kommandocode": "X", "adapter": "com"},
    )
    assert response.status_code == 422


def test_routine_crud_http(client: TestClient):
    k1 = _kommando_anlegen(client, bezeichnung="K1", code="K1")
    k2 = _kommando_anlegen(client, bezeichnung="K2", code="K2")

    create = client.post(
        "/katalog/bibliothek/routinen",
        json={"bezeichnung": "Routine A", "kommando_ids": [k1, k2]},
    )
    assert create.status_code == 201
    body = create.json()
    routine_id = body["routine_id"]
    assert body["bezeichnung"] == "Routine A"
    assert len(body["aktionen"]) == 2

    liste = client.get("/katalog/bibliothek/routinen")
    assert liste.status_code == 200
    assert liste.json()["routinen"][0]["anzahl_aktionen"] == 2

    detail = client.get(f"/katalog/bibliothek/routinen/{routine_id}")
    assert detail.status_code == 200
    assert detail.json()["routine_id"] == routine_id

    update = client.put(
        f"/katalog/bibliothek/routinen/{routine_id}",
        json={"bezeichnung": "Routine B", "kommando_ids": [k1]},
    )
    assert update.status_code == 200
    assert update.json()["bezeichnung"] == "Routine B"
    assert len(update.json()["aktionen"]) == 1

    delete = client.delete(f"/katalog/bibliothek/routinen/{routine_id}")
    assert delete.status_code == 204


def test_routine_zuweisung_und_entfernen(client: TestClient):
    k1 = _kommando_anlegen(client)
    routine_id = client.post(
        "/katalog/bibliothek/routinen",
        json={"bezeichnung": "R", "kommando_ids": [k1]},
    ).json()["routine_id"]
    pd_id = _entwurf_anlegen(client, _unique_kodierung())

    zuweisung = client.put(
        f"/katalog/entwuerfe/{pd_id}/schritte/{SCHRIITT_ID}/automatisierung",
        json={"routine_id": routine_id},
    )
    assert zuweisung.status_code == 200
    assert zuweisung.json()["routine_id"] == routine_id
    assert zuweisung.json()["kommando_id"] is None

    entfernen = client.put(
        f"/katalog/entwuerfe/{pd_id}/schritte/{SCHRIITT_ID}/automatisierung",
        json={"kommando_id": None, "routine_id": None},
    )
    assert entfernen.status_code == 200
    assert entfernen.json()["routine_id"] is None
    assert entfernen.json()["kommando_id"] is None


def test_automatisierung_leerer_body_422(client: TestClient):
    pd_id = _entwurf_anlegen(client, _unique_kodierung())
    response = client.put(
        f"/katalog/entwuerfe/{pd_id}/schritte/{SCHRIITT_ID}/automatisierung",
        json={},
    )
    assert response.status_code == 422


def test_automatisierung_beide_ids_422(client: TestClient):
    pd_id = _entwurf_anlegen(client, _unique_kodierung())
    response = client.put(
        f"/katalog/entwuerfe/{pd_id}/schritte/{SCHRIITT_ID}/automatisierung",
        json={"kommando_id": "a", "routine_id": "b"},
    )
    assert response.status_code == 422
from tests.support.auth import login_as_admin
