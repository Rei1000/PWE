"""API-Tests — Entwurfs-Schrittbearbeitung (Gate 8.2b2)."""

from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient

from api.app import create_app
from api.deps import in_memory_deps


@pytest.fixture
def client():
    with TestClient(create_app(in_memory_deps())) as http_client:
        yield http_client


def _unique_kodierung() -> str:
    return str(10_000_000_000 + uuid.uuid4().int % 9_000_000_000)


def _vorlage_id(client: TestClient) -> str:
    response = client.post(
        "/katalog/bibliothek/vorlagen",
        json={"bezeichnung": "Testvorlage"},
    )
    assert response.status_code == 201
    return response.json()["vorlage_id"]


def _leerer_entwurf(client: TestClient) -> str:
    response = client.post(
        "/katalog/entwuerfe",
        json={"produktkodierung": _unique_kodierung(), "prozedur_schritte": []},
    )
    assert response.status_code == 201
    return response.json()["produktdefinition_id"]


def test_get_entwurf_mit_schritten(client: TestClient):
    pd_id = _leerer_entwurf(client)
    vorlage_id = _vorlage_id(client)
    post = client.post(
        f"/katalog/entwuerfe/{pd_id}/schritte",
        json={
            "schritt_id": "s1",
            "vorlage_id": vorlage_id,
            "ist_pflicht": True,
            "sollvorgaben": {"a": 1},
        },
    )
    assert post.status_code == 201
    get = client.get(f"/katalog/entwuerfe/{pd_id}")
    assert get.status_code == 200
    body = get.json()
    assert body["produktdefinition_id"] == pd_id
    assert len(body["prozedur_schritte"]) == 1
    assert body["prozedur_schritte"][0]["kommando_id"] is None


def test_post_schritt_404_entwurf(client: TestClient):
    vorlage_id = _vorlage_id(client)
    response = client.post(
        "/katalog/entwuerfe/unbekannt/schritte",
        json={
            "schritt_id": "s1",
            "vorlage_id": vorlage_id,
            "ist_pflicht": True,
        },
    )
    assert response.status_code == 404
    assert response.json()["code"] == "entwurf_nicht_gefunden"


def test_post_schritt_404_vorlage(client: TestClient):
    pd_id = _leerer_entwurf(client)
    response = client.post(
        f"/katalog/entwuerfe/{pd_id}/schritte",
        json={
            "schritt_id": "s1",
            "vorlage_id": "fehlt",
            "ist_pflicht": True,
        },
    )
    assert response.status_code == 404
    assert response.json()["code"] == "vorlage_nicht_gefunden"


def test_post_schritt_409_doppelte_id(client: TestClient):
    pd_id = _leerer_entwurf(client)
    vorlage_id = _vorlage_id(client)
    payload = {
        "schritt_id": "s1",
        "vorlage_id": vorlage_id,
        "ist_pflicht": True,
    }
    assert client.post(f"/katalog/entwuerfe/{pd_id}/schritte", json=payload).status_code == 201
    dup = client.post(f"/katalog/entwuerfe/{pd_id}/schritte", json=payload)
    assert dup.status_code == 409
    assert dup.json()["code"] == "schritt_id_bereits_vorhanden"


def test_put_schritt_erhaelt_automatisierung(client: TestClient):
    pd_id = _leerer_entwurf(client)
    vorlage_id = _vorlage_id(client)
    client.post(
        f"/katalog/entwuerfe/{pd_id}/schritte",
        json={"schritt_id": "s1", "vorlage_id": vorlage_id, "ist_pflicht": True},
    )
    kommando = client.post(
        "/katalog/bibliothek/kommandos",
        json={"bezeichnung": "K", "kommandocode": "CMD"},
    )
    kommando_id = kommando.json()["kommando_id"]
    client.put(
        f"/katalog/entwuerfe/{pd_id}/schritte/s1/automatisierung",
        json={"kommando_id": kommando_id},
    )
    put = client.put(
        f"/katalog/entwuerfe/{pd_id}/schritte/s1",
        json={"vorlage_id": vorlage_id, "ist_pflicht": False, "sollvorgaben": {"x": 2}},
    )
    assert put.status_code == 200
    assert put.json()["kommando_id"] == kommando_id
    assert put.json()["ist_pflicht"] is False


def test_put_schritt_422_extra_feld(client: TestClient):
    pd_id = _leerer_entwurf(client)
    vorlage_id = _vorlage_id(client)
    client.post(
        f"/katalog/entwuerfe/{pd_id}/schritte",
        json={"schritt_id": "s1", "vorlage_id": vorlage_id, "ist_pflicht": True},
    )
    response = client.put(
        f"/katalog/entwuerfe/{pd_id}/schritte/s1",
        json={
            "vorlage_id": vorlage_id,
            "ist_pflicht": True,
            "sollvorgaben": {},
            "kommando_id": "x",
        },
    )
    assert response.status_code == 422
    assert response.json()["code"] == "validation"


def test_delete_schritt_204(client: TestClient):
    pd_id = _leerer_entwurf(client)
    vorlage_id = _vorlage_id(client)
    client.post(
        f"/katalog/entwuerfe/{pd_id}/schritte",
        json={"schritt_id": "s1", "vorlage_id": vorlage_id, "ist_pflicht": True},
    )
    delete = client.delete(f"/katalog/entwuerfe/{pd_id}/schritte/s1")
    assert delete.status_code == 204
    get = client.get(f"/katalog/entwuerfe/{pd_id}")
    assert get.json()["prozedur_schritte"] == []


def test_put_reihenfolge_vollstaendig(client: TestClient):
    pd_id = _leerer_entwurf(client)
    vorlage_id = _vorlage_id(client)
    for sid in ("s1", "s2"):
        client.post(
            f"/katalog/entwuerfe/{pd_id}/schritte",
            json={"schritt_id": sid, "vorlage_id": vorlage_id, "ist_pflicht": True},
        )
    response = client.put(
        f"/katalog/entwuerfe/{pd_id}/schritte/reihenfolge",
        json={"schritt_ids": ["s2", "s1"]},
    )
    assert response.status_code == 200
    schritte = response.json()["prozedur_schritte"]
    assert schritte[0]["schritt_id"] == "s2"
    assert schritte[0]["reihenfolge"] == 1


def test_put_reihenfolge_409_unvollstaendig(client: TestClient):
    pd_id = _leerer_entwurf(client)
    vorlage_id = _vorlage_id(client)
    for sid in ("s1", "s2"):
        client.post(
            f"/katalog/entwuerfe/{pd_id}/schritte",
            json={"schritt_id": sid, "vorlage_id": vorlage_id, "ist_pflicht": True},
        )
    response = client.put(
        f"/katalog/entwuerfe/{pd_id}/schritte/reihenfolge",
        json={"schritt_ids": ["s1"]},
    )
    assert response.status_code == 409
    assert response.json()["code"] == "ungueltige_schritt_reihenfolge"
