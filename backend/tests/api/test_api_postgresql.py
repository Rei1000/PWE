"""API-Integrationstests — PostgreSQL-Wiring (Gate 7.1)."""

from __future__ import annotations

import os
import uuid

import pytest
from fastapi.testclient import TestClient

from api.app import create_app
from api.persistence import PersistenceConfigurationError, PersistenceSettings

pytestmark = pytest.mark.postgresql


def _unique_kodierung() -> str:
    return str(10_000_000_000 + uuid.uuid4().int % 9_000_000_000)


def test_persistence_settings_in_memory_when_database_url_missing(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    settings = PersistenceSettings.from_env()
    assert settings.mode == "in-memory"
    assert settings.database_url is None


def test_persistence_settings_in_memory_when_database_url_empty(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "   ")
    settings = PersistenceSettings.from_env()
    assert settings.mode == "in-memory"


def test_create_app_in_memory_without_database_url(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with TestClient(create_app()) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_app_fails_on_invalid_database_url(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://invalid:invalid@127.0.0.1:1/nope")
    with pytest.raises(PersistenceConfigurationError):
        with TestClient(create_app()):
            pass


@pytest.fixture
def pg_api_client():
    if not os.environ.get("DATABASE_URL"):
        pytest.skip("DATABASE_URL nicht gesetzt — PostgreSQL-API-Tests übersprungen")
    with TestClient(create_app()) as client:
        yield client


def test_prueflauf_happy_path_over_postgresql(pg_api_client: TestClient):
    kodierung = _unique_kodierung()
    entwurf = pg_api_client.post(
        "/katalog/entwuerfe",
        json={
            "produktkodierung": kodierung,
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
        },
    )
    assert entwurf.status_code == 201
    produktdefinition_id = entwurf.json()["produktdefinition_id"]

    version = pg_api_client.post(f"/katalog/entwuerfe/{produktdefinition_id}/veroeffentlichen")
    assert version.status_code == 201

    start = pg_api_client.post(
        "/prueflaeufe",
        json={
            "produktkodierung": kodierung,
            "pruefobjekt_kennung": "GER-PG-API",
            "pruefer_id": "pruefer-pg",
        },
    )
    assert start.status_code == 201
    prueflauf_id = start.json()["prueflauf_id"]

    komponente = pg_api_client.post(
        f"/prueflaeufe/{prueflauf_id}/komponenten",
        json={"komponenten_typ": "mainboard", "seriennummer": "MB-PG-1"},
    )
    assert komponente.status_code == 201

    nachweis = pg_api_client.post(
        f"/prueflaeufe/{prueflauf_id}/schritte/schritt-a/nachweise",
        json={"art": "messwert", "payload": {"spannung": 230}},
    )
    assert nachweis.status_code == 201

    beurteilung = pg_api_client.post(
        f"/prueflaeufe/{prueflauf_id}/schritte/schritt-a/beurteilung"
    )
    assert beurteilung.status_code == 204

    abschluss = pg_api_client.post(f"/prueflaeufe/{prueflauf_id}/abschluss")
    assert abschluss.status_code == 200
    assert abschluss.json()["ist_gueltig"] is True

    detail = pg_api_client.get(f"/prueflaeufe/{prueflauf_id}")
    assert detail.status_code == 200
    assert detail.json()["ist_abgeschlossen"] is True

    pdf = pg_api_client.get(f"/prueflaeufe/{prueflauf_id}/protokoll/pdf")
    assert pdf.status_code == 200
    assert pdf.headers["content-type"] == "application/pdf"
