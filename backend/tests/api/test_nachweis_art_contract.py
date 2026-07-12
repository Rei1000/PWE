"""API-Contract-Tests — NachweisArt (Transport unabhängig von Domain-Enum-Namen)."""

from __future__ import annotations

import os
import uuid

import pytest
from fastapi.testclient import TestClient

from adapters.persistence.in_memory import InMemoryKatalogRepository
from api.app import create_app
from api.deps import in_memory_deps
from api.schemas import NACHWEIS_ART_API_WERTE
from domain.katalog.version import MaterialisierterProzedurSchritt, ProduktdefinitionsVersion


def _unique_kodierung() -> str:
    return str(10_000_000_000 + uuid.uuid4().int % 9_000_000_000)


@pytest.fixture
def memory_client() -> TestClient:
    deps = in_memory_deps()
    assert isinstance(deps.katalog, InMemoryKatalogRepository)
    deps.katalog.register_aktive_version(
        ProduktdefinitionsVersion(
            version_id="ver-contract",
            produktdefinition_id="pd-contract",
            produktkodierung="1234567890",
            prozedur_schritte=(
                MaterialisierterProzedurSchritt(
                    schritt_id="schritt-a",
                    vorlage_id="vorlage-a",
                    ist_pflicht=True,
                    reihenfolge=1,
                    sollvorgaben={"spannung": {"min": 220, "max": 240}},
                ),
            ),
            sollbestueckung=("mainboard",),
        )
    )
    with TestClient(create_app(deps)) as client:
        yield client


@pytest.fixture
def pg_client() -> TestClient:
    if not os.environ.get("DATABASE_URL"):
        pytest.skip("DATABASE_URL nicht gesetzt — PostgreSQL-Contract-Tests übersprungen")
    with TestClient(create_app()) as client:
        yield client


def _start_prueflauf(client: TestClient, *, produktkodierung: str = "1234567890") -> str:
    response = client.post(
        "/prueflaeufe",
        json={
            "produktkodierung": produktkodierung,
            "pruefobjekt_kennung": "GER-CONTRACT",
            "pruefer_id": "pruefer-1",
        },
    )
    assert response.status_code == 201
    return response.json()["prueflauf_id"]


def _bootstrap_postgresql_katalog(client: TestClient) -> str:
    kodierung = _unique_kodierung()
    entwurf = client.post(
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
    version = client.post(f"/katalog/entwuerfe/{produktdefinition_id}/veroeffentlichen")
    assert version.status_code == 201
    return kodierung


def _prepare_nachweis_endpoint(
    client: TestClient, *, produktkodierung: str = "1234567890"
) -> tuple[str, str]:
    prueflauf_id = _start_prueflauf(client, produktkodierung=produktkodierung)
    komponente = client.post(
        f"/prueflaeufe/{prueflauf_id}/komponenten",
        json={"komponenten_typ": "mainboard", "seriennummer": "MB-C"},
    )
    assert komponente.status_code == 201
    return prueflauf_id, "schritt-a"


def _post_nachweis(client: TestClient, prueflauf_id: str, schritt_id: str, art: str):
    return client.post(
        f"/prueflaeufe/{prueflauf_id}/schritte/{schritt_id}/nachweise",
        json={"art": art, "payload": {"spannung": 230}},
    )


@pytest.mark.parametrize("art", NACHWEIS_ART_API_WERTE)
def test_gueltige_nachweis_art_in_memory(memory_client: TestClient, art: str):
    prueflauf_id, schritt_id = _prepare_nachweis_endpoint(memory_client)
    response = _post_nachweis(memory_client, prueflauf_id, schritt_id, art)
    assert response.status_code == 201
    assert response.json()["art"] == art


@pytest.mark.postgresql
@pytest.mark.parametrize("art", NACHWEIS_ART_API_WERTE)
def test_gueltige_nachweis_art_postgresql(pg_client: TestClient, art: str):
    kodierung = _bootstrap_postgresql_katalog(pg_client)
    prueflauf_id, schritt_id = _prepare_nachweis_endpoint(pg_client, produktkodierung=kodierung)
    response = _post_nachweis(pg_client, prueflauf_id, schritt_id, art)
    assert response.status_code == 201
    assert response.json()["art"] == art


@pytest.mark.parametrize(
    "ungueltige_art",
    ["MESSWERT", "Messwert", "unbekannt", ""],
)
def test_ungueltige_nachweis_art_422(memory_client: TestClient, ungueltige_art: str):
    prueflauf_id, schritt_id = _prepare_nachweis_endpoint(memory_client)
    response = _post_nachweis(memory_client, prueflauf_id, schritt_id, ungueltige_art)
    assert response.status_code == 422
    body = response.json()
    assert body == {"detail": "Validierungsfehler", "code": "validation"}


@pytest.mark.postgresql
def test_contract_parity_in_memory_und_postgresql(memory_client: TestClient, pg_client: TestClient):
    kodierung = _bootstrap_postgresql_katalog(pg_client)
    for art in ("messwert", "kommentar"):
        mem_id, mem_schritt = _prepare_nachweis_endpoint(memory_client)
        pg_id, pg_schritt = _prepare_nachweis_endpoint(pg_client, produktkodierung=kodierung)

        mem_response = _post_nachweis(memory_client, mem_id, mem_schritt, art)
        pg_response = _post_nachweis(pg_client, pg_id, pg_schritt, art)

        assert mem_response.status_code == pg_response.status_code == 201
        assert mem_response.json()["art"] == pg_response.json()["art"] == art
