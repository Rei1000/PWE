"""PostgreSQL-API — Entwurfsbearbeitung E2E (Gate 8.2b2)."""

from __future__ import annotations

import os
import uuid

import pytest
from fastapi.testclient import TestClient

from api.app import create_app


@pytest.mark.postgresql
def test_postgresql_entwurf_bearbeitung_und_publish():
    if not os.environ.get("DATABASE_URL"):
        pytest.skip("DATABASE_URL nicht gesetzt")

    kodierung = str(10_000_000_000 + uuid.uuid4().int % 9_000_000_000)

    with TestClient(create_app()) as client:
        vorlage = client.post(
            "/katalog/bibliothek/vorlagen",
            json={"bezeichnung": "PG Vorlage"},
        )
        assert vorlage.status_code == 201
        vorlage_id = vorlage.json()["vorlage_id"]

        entwurf = client.post(
            "/katalog/entwuerfe",
            json={"produktkodierung": kodierung, "prozedur_schritte": []},
        )
        assert entwurf.status_code == 201
        pd_id = entwurf.json()["produktdefinition_id"]

        schritt = client.post(
            f"/katalog/entwuerfe/{pd_id}/schritte",
            json={
                "schritt_id": "s1",
                "vorlage_id": vorlage_id,
                "ist_pflicht": True,
                "sollvorgaben": {"spannung": {"min": 1, "max": 9}},
            },
        )
        assert schritt.status_code == 201

        update = client.put(
            f"/katalog/entwuerfe/{pd_id}/schritte/s1",
            json={
                "vorlage_id": vorlage_id,
                "ist_pflicht": True,
                "sollvorgaben": {"spannung": {"min": 2, "max": 8}},
            },
        )
        assert update.status_code == 200

        version = client.post(f"/katalog/entwuerfe/{pd_id}/veroeffentlichen")
        assert version.status_code == 201

        delete = client.delete(f"/katalog/entwuerfe/{pd_id}/schritte/s1")
        assert delete.status_code == 204

        get = client.get(f"/katalog/entwuerfe/{pd_id}")
        assert get.status_code == 200
        assert get.json()["prozedur_schritte"] == []
