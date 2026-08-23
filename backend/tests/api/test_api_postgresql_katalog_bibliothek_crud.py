"""PostgreSQL API-Tests — Bibliothek CRUD (Gate 8.2a)."""

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
def test_postgresql_kommando_und_routine_crud(pg_api_client: TestClient):
    kodierung = _unique_kodierung()

    kommando = pg_api_client.post(
        "/katalog/bibliothek/kommandos",
        json={"bezeichnung": "PG-K", "kommandocode": "PG_CMD"},
    )
    assert kommando.status_code == 201
    kommando_id = kommando.json()["kommando_id"]

    assert pg_api_client.get("/katalog/bibliothek/kommandos").status_code == 200
    assert pg_api_client.get(f"/katalog/bibliothek/kommandos/{kommando_id}").status_code == 200

    routine = pg_api_client.post(
        "/katalog/bibliothek/routinen",
        json={"bezeichnung": "PG-R", "kommando_ids": [kommando_id]},
    )
    assert routine.status_code == 201
    routine_id = routine.json()["routine_id"]

    vorlage = pg_api_client.post(
        "/katalog/bibliothek/vorlagen",
        json={"bezeichnung": "PG-V"},
    )
    assert vorlage.status_code == 201
    vorlage_id = vorlage.json()["vorlage_id"]

    pd_id = pg_api_client.post(
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

    zuweisung = pg_api_client.put(
        f"/katalog/entwuerfe/{pd_id}/schritte/{SCHRIITT_ID}/automatisierung",
        json={"routine_id": routine_id},
    )
    assert zuweisung.status_code == 200

    assert pg_api_client.get("/katalog/bibliothek/routinen").status_code == 200
    assert pg_api_client.get(f"/katalog/bibliothek/routinen/{routine_id}").status_code == 200

    assert pg_api_client.delete(f"/katalog/bibliothek/routinen/{routine_id}").status_code == 409

    pg_api_client.put(
        f"/katalog/entwuerfe/{pd_id}/schritte/{SCHRIITT_ID}/automatisierung",
        json={"kommando_id": None, "routine_id": None},
    )
    assert pg_api_client.delete(f"/katalog/bibliothek/routinen/{routine_id}").status_code == 204
    assert pg_api_client.delete(f"/katalog/bibliothek/kommandos/{kommando_id}").status_code == 204
from tests.support.auth import login_as_admin
