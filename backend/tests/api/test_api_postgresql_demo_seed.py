"""PostgreSQL — Demo-Seed-Flow mit PWE_DEMO_MODE (Gate 6.3c)."""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

from api.app import create_app
from api.kommando_wiring import (
    DEMO_KOMMANDOCODE,
    KommandoAdapterSettings,
    configure_kommando_adapter,
    reset_kommando_adapter_cache_for_tests,
)
from api.persistence import postgres_deps
from helpers import vorlage_anlegen_http

SCHRITT_ID = "demo-schritt-1"
KODIERUNG = "9000000001"


@pytest.mark.postgresql
def test_postgresql_http_demo_seed_und_automatisierung(monkeypatch):
    url = os.environ.get("DATABASE_URL")
    if not url:
        pytest.skip("DATABASE_URL nicht gesetzt")

    monkeypatch.setenv("PWE_DEMO_MODE", "true")
    monkeypatch.setenv("EXTERNES_KOMMANDO_ADAPTER", "simulation")
    reset_kommando_adapter_cache_for_tests()
    configure_kommando_adapter(KommandoAdapterSettings.from_env())

    with TestClient(create_app(postgres_deps_factory=postgres_deps)) as client:
        kommando = client.post(
            "/katalog/bibliothek/kommandos",
            json={"bezeichnung": "Demo Messwert", "kommandocode": DEMO_KOMMANDOCODE},
        )
        assert kommando.status_code == 201
        kommando_id = kommando.json()["kommando_id"]

        vorlage_id = vorlage_anlegen_http(client, bezeichnung="Demo Vorlage")

        entwurf = client.post(
            "/katalog/entwuerfe",
            json={
                "produktkodierung": KODIERUNG,
                "prozedur_schritte": [
                    {
                        "schritt_id": SCHRITT_ID,
                        "vorlage_id": vorlage_id,
                        "ist_pflicht": True,
                        "reihenfolge": 1,
                        "sollvorgaben": {"messwert": {"min": 1, "max": 100}},
                    }
                ],
                "sollbestueckung": ["komponente-a"],
            },
        )
        assert entwurf.status_code == 201
        pd_id = entwurf.json()["produktdefinition_id"]

        assert (
            client.put(
                f"/katalog/entwuerfe/{pd_id}/schritte/{SCHRITT_ID}/automatisierung",
                json={"kommando_id": kommando_id},
            ).status_code
            == 200
        )
        assert client.post(f"/katalog/entwuerfe/{pd_id}/veroeffentlichen").status_code == 201

        start = client.post(
            "/prueflaeufe",
            json={
                "produktkodierung": KODIERUNG,
                "pruefobjekt_kennung": "DEMO-OBJ-PG",
            },
        )
        assert start.status_code == 201
        prueflauf_id = start.json()["prueflauf_id"]

        client.post(
            f"/prueflaeufe/{prueflauf_id}/komponenten",
            json={"komponenten_typ": "komponente-a", "seriennummer": "KA-PG"},
        )

        detail = client.get(f"/prueflaeufe/{prueflauf_id}")
        schritt = next(s for s in detail.json()["schritte"] if s["schritt_id"] == SCHRITT_ID)
        assert schritt["hat_automatisierung"] is True

        auto = client.post(
            f"/prueflaeufe/{prueflauf_id}/schritte/{SCHRITT_ID}/automatisierung/ausfuehren"
        )
        assert auto.status_code == 200
        assert auto.json()["fehlgeschlagen"] is False
        assert len(auto.json()["nachweise"]) >= 1

        detail2 = client.get(f"/prueflaeufe/{prueflauf_id}")
        nachweise = next(
            s for s in detail2.json()["schritte"] if s["schritt_id"] == SCHRITT_ID
        )["nachweise"]
        assert len(nachweise) >= 1

    reset_kommando_adapter_cache_for_tests()
from tests.support.auth import login_as_admin
