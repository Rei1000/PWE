"""HTTP-E2E — Demo-Seed-Flow mit PWE_DEMO_MODE (Gate 6.3c)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from api.app import create_app
from api.deps import in_memory_deps
from tests.support.qualification import qualify_client_for_kodierung
from api.kommando_wiring import (
    DEMO_KOMMANDOCODE,
    KommandoAdapterSettings,
    configure_kommando_adapter,
    reset_kommando_adapter_cache_for_tests,
)

SCHRITT_ID = "demo-schritt-1"
KODIERUNG = "9000000001"


@pytest.fixture
def demo_client(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("PWE_DEMO_MODE", "true")
    monkeypatch.setenv("EXTERNES_KOMMANDO_ADAPTER", "simulation")
    reset_kommando_adapter_cache_for_tests()
    configure_kommando_adapter(KommandoAdapterSettings.from_env())
    with TestClient(create_app(in_memory_deps())) as client:
        yield client
    reset_kommando_adapter_cache_for_tests()


def test_http_e2e_demo_seed_und_automatisierung(demo_client: TestClient):
    client = demo_client

    kommando = client.post(
        "/katalog/bibliothek/kommandos",
        json={"bezeichnung": "Demo Messwert", "kommandocode": DEMO_KOMMANDOCODE},
    )
    assert kommando.status_code == 201
    kommando_id = kommando.json()["kommando_id"]

    vorlage = client.post(
        "/katalog/bibliothek/vorlagen",
        json={"bezeichnung": "Demo Vorlage"},
    )
    assert vorlage.status_code == 201
    vorlage_id = vorlage.json()["vorlage_id"]

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

    zuweisung = client.put(
        f"/katalog/entwuerfe/{pd_id}/schritte/{SCHRITT_ID}/automatisierung",
        json={"kommando_id": kommando_id},
    )
    assert zuweisung.status_code == 200

    version = client.post(f"/katalog/entwuerfe/{pd_id}/veroeffentlichen")
    assert version.status_code == 201

    qualify_client_for_kodierung(client, KODIERUNG)
    start = client.post(
        "/prueflaeufe",
        json={
            "produktkodierung": KODIERUNG,
            "pruefobjekt_kennung": "DEMO-OBJ-1",
        },
    )
    assert start.status_code == 201
    prueflauf_id = start.json()["prueflauf_id"]

    komp = client.post(
        f"/prueflaeufe/{prueflauf_id}/komponenten",
        json={"komponenten_typ": "komponente-a", "seriennummer": "KA-1"},
    )
    assert komp.status_code in (200, 201)

    detail = client.get(f"/prueflaeufe/{prueflauf_id}")
    assert detail.status_code == 200
    body = detail.json()
    schritt = next(s for s in body["schritte"] if s["schritt_id"] == SCHRITT_ID)
    assert schritt["hat_automatisierung"] is True
    assert schritt["kann_automatisierung_ausfuehren"] is True

    auto = client.post(
        f"/prueflaeufe/{prueflauf_id}/schritte/{SCHRITT_ID}/automatisierung/ausfuehren"
    )
    assert auto.status_code == 200
    ergebnis = auto.json()
    assert ergebnis["fehlgeschlagen"] is False
    assert len(ergebnis["nachweise"]) >= 1

    detail2 = client.get(f"/prueflaeufe/{prueflauf_id}")
    nachweise = next(
        s for s in detail2.json()["schritte"] if s["schritt_id"] == SCHRITT_ID
    )["nachweise"]
    assert len(nachweise) >= 1
