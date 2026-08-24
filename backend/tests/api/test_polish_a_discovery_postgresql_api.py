"""PostgreSQL API-Integration — V1 Operational Polish A Discovery Reads."""

from __future__ import annotations

import os
import uuid

import pytest
from fastapi.testclient import TestClient

from api.app import create_app

pytestmark = pytest.mark.postgresql


def _unique_kodierung() -> str:
    return str(10_000_000_000 + uuid.uuid4().int % 9_000_000_000)


@pytest.fixture
def pg_api_client():
    if not os.environ.get("DATABASE_URL"):
        pytest.skip("DATABASE_URL nicht gesetzt")
    with TestClient(create_app()) as client:
        yield client


def test_postgresql_startbar_und_aktive_produkte_api(pg_api_client: TestClient):
    kodierung = _unique_kodierung()
    vorlage = pg_api_client.post(
        "/katalog/bibliothek/vorlagen",
        json={"bezeichnung": "V", "beschreibung": None},
    )
    assert vorlage.status_code == 201
    vorlage_id = vorlage.json()["vorlage_id"]

    entwurf = pg_api_client.post(
        "/katalog/entwuerfe",
        json={
            "produktkodierung": kodierung,
            "prozedur_schritte": [
                {
                    "schritt_id": "s1",
                    "vorlage_id": vorlage_id,
                    "ist_pflicht": True,
                    "reihenfolge": 1,
                }
            ],
        },
    )
    assert entwurf.status_code == 201
    pd_id = entwurf.json()["produktdefinition_id"]
    pub = pg_api_client.post(f"/katalog/entwuerfe/{pd_id}/veroeffentlichen", json={})
    assert pub.status_code == 201
    version_id = pub.json()["version_id"]

    aktive = pg_api_client.get("/katalog/aktive-produkte")
    assert aktive.status_code == 200
    match = next(p for p in aktive.json()["produkte"] if p["produktkodierung"] == kodierung)
    assert match["version_id"] == version_id

    me = pg_api_client.get("/auth/me").json()
    before = pg_api_client.get("/prueflaeufe/startbar").json()["pruefungen"]
    assert not any(p["produktkodierung"] == kodierung for p in before)

    profil = pg_api_client.post(
        "/identity/profile",
        json={"bezeichnung": "P", "produktdefinition_ids": [pd_id]},
    )
    assert profil.status_code == 201
    profil_id = profil.json()["profil_id"]
    assert (
        pg_api_client.put(f"/identity/profile/{profil_id}/benutzer/{me['benutzer_id']}").status_code
        == 204
    )
    einw = pg_api_client.post(
        "/identity/einweisungen",
        json={"benutzer_id": me["benutzer_id"], "version_id": version_id},
    )
    assert einw.status_code == 201

    after = pg_api_client.get("/prueflaeufe/startbar").json()["pruefungen"]
    assert any(p["produktkodierung"] == kodierung for p in after)

    detail = pg_api_client.get(f"/identity/benutzer/{me['benutzer_id']}")
    assert profil_id in detail.json()["profil_ids"]
