"""PostgreSQL API-Tests — PrüfschrittVorlage CRUD (Gate 8.2b1)."""

from __future__ import annotations

import os
import uuid

import pytest
from fastapi.testclient import TestClient

from api.app import create_app

SCHRIITT_ID = "schritt-a"


def _unique_kodierung() -> str:
    return str(10_000_000_000 + uuid.uuid4().int % 9_000_000_000)


@pytest.fixture
def pg_api_client():
    if not os.environ.get("DATABASE_URL"):
        pytest.skip("DATABASE_URL nicht gesetzt")
    with TestClient(create_app()) as client:
        yield client


@pytest.mark.postgresql
def test_postgresql_pruefschritt_vorlage_crud_und_version_snapshot(pg_api_client: TestClient):
    client = pg_api_client
    kodierung = _unique_kodierung()

    vorlage = client.post(
        "/katalog/bibliothek/vorlagen",
        json={"bezeichnung": "PG-Vorlage", "beschreibung": "PG"},
    )
    assert vorlage.status_code == 201
    vorlage_id = vorlage.json()["vorlage_id"]

    assert client.get("/katalog/bibliothek/vorlagen").status_code == 200
    assert client.get(f"/katalog/bibliothek/vorlagen/{vorlage_id}").status_code == 200

    pd_id = client.post(
        "/katalog/entwuerfe",
        json={
            "produktkodierung": kodierung,
            "prozedur_schritte": [
                {
                    "schritt_id": SCHRIITT_ID,
                    "vorlage_id": vorlage_id,
                    "ist_pflicht": True,
                    "reihenfolge": 1,
                }
            ],
            "sollbestueckung": [],
        },
    ).json()["produktdefinition_id"]

    version = client.post(f"/katalog/entwuerfe/{pd_id}/veroeffentlichen")
    assert version.status_code == 201

    assert client.delete(f"/katalog/bibliothek/vorlagen/{vorlage_id}").status_code == 409

    start = client.post(
        "/prueflaeufe",
        json={
            "produktkodierung": kodierung,
            "pruefobjekt_kennung": "PG-OBJ",
            "pruefer_id": "pg",
        },
    )
    assert start.status_code == 201
