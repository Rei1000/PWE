"""API-Tests — Foto-Nachweis und Download (Gate 8.3a)."""

from __future__ import annotations

import io
import os
import uuid

import pytest
from fastapi.testclient import TestClient

from adapters.persistence.in_memory import InMemoryKatalogRepository
from adapters.storage.in_memory import InMemoryDateiSpeicher
from api.app import create_app
from api.deps import in_memory_deps
from api.schemas import NACHWEIS_ART_API_WERTE
from domain.katalog.version import MaterialisierterProzedurSchritt, ProduktdefinitionsVersion
from domain.pruefausfuehrung.foto_regeln import MAX_FOTO_GROESSE_BYTES
from foto_fixtures import JPEG_BYTES, PNG_BYTES
from helpers import vorlage_anlegen_http


def _unique_kodierung() -> str:
    return str(10_000_000_000 + uuid.uuid4().int % 9_000_000_000)


@pytest.fixture
def memory_client() -> TestClient:
    storage = InMemoryDateiSpeicher()
    deps = in_memory_deps(datei_speicher=storage)
    assert isinstance(deps.katalog, InMemoryKatalogRepository)
    deps.katalog.register_aktive_version(
        ProduktdefinitionsVersion(
            version_id="ver-foto",
            produktdefinition_id="pd-foto",
            produktkodierung="1234567890",
            prozedur_schritte=(
                MaterialisierterProzedurSchritt(
                    schritt_id="schritt-a",
                    vorlage_id="vorlage-a",
                    ist_pflicht=True,
                    reihenfolge=1,
                    sollvorgaben={},
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
            "pruefobjekt_kennung": "GER-FOTO",
            "pruefer_id": "pruefer-1",
        },
    )
    assert response.status_code == 201
    return response.json()["prueflauf_id"]


def _prepare_foto_endpoint(
    client: TestClient, *, produktkodierung: str = "1234567890"
) -> tuple[str, str]:
    prueflauf_id = _start_prueflauf(client, produktkodierung=produktkodierung)
    komponente = client.post(
        f"/prueflaeufe/{prueflauf_id}/komponenten",
        json={"komponenten_typ": "mainboard", "seriennummer": "MB-F"},
    )
    assert komponente.status_code == 201
    return prueflauf_id, "schritt-a"


def _bootstrap_postgresql_katalog(client: TestClient) -> str:
    kodierung = _unique_kodierung()
    vorlage_id = vorlage_anlegen_http(client)
    entwurf = client.post(
        "/katalog/entwuerfe",
        json={
            "produktkodierung": kodierung,
            "prozedur_schritte": [
                {
                    "schritt_id": "schritt-a",
                    "vorlage_id": vorlage_id,
                    "ist_pflicht": True,
                    "reihenfolge": 1,
                    "sollvorgaben": {},
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


def test_multipart_jpeg_201(memory_client: TestClient):
    prueflauf_id, schritt_id = _prepare_foto_endpoint(memory_client)
    response = memory_client.post(
        f"/prueflaeufe/{prueflauf_id}/schritte/{schritt_id}/nachweise/foto",
        files={"datei": ("foto.jpg", io.BytesIO(JPEG_BYTES), "image/jpeg")},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["art"] == "foto"
    assert body["mime_type"] == "image/jpeg"
    assert body["groesse_bytes"] == len(JPEG_BYTES)


def test_multipart_png_201(memory_client: TestClient):
    prueflauf_id, schritt_id = _prepare_foto_endpoint(memory_client)
    response = memory_client.post(
        f"/prueflaeufe/{prueflauf_id}/schritte/{schritt_id}/nachweise/foto",
        files={"datei": ("foto.png", io.BytesIO(PNG_BYTES), "image/png")},
    )
    assert response.status_code == 201
    assert response.json()["mime_type"] == "image/png"


def test_multipart_415_ungueltiger_typ(memory_client: TestClient):
    prueflauf_id, schritt_id = _prepare_foto_endpoint(memory_client)
    response = memory_client.post(
        f"/prueflaeufe/{prueflauf_id}/schritte/{schritt_id}/nachweise/foto",
        files={"datei": ("foto.gif", io.BytesIO(JPEG_BYTES), "image/gif")},
    )
    assert response.status_code == 415
    assert response.json()["code"] == "ungueltiger_dateityp"


def test_multipart_413_zu_gross(memory_client: TestClient):
    prueflauf_id, schritt_id = _prepare_foto_endpoint(memory_client)
    zu_gross = JPEG_BYTES + b"\x00" * MAX_FOTO_GROESSE_BYTES
    response = memory_client.post(
        f"/prueflaeufe/{prueflauf_id}/schritte/{schritt_id}/nachweise/foto",
        files={"datei": ("foto.jpg", io.BytesIO(zu_gross), "image/jpeg")},
    )
    assert response.status_code == 413
    assert response.json()["code"] == "datei_zu_gross"


def test_download_jpeg_content_type(memory_client: TestClient):
    prueflauf_id, schritt_id = _prepare_foto_endpoint(memory_client)
    upload = memory_client.post(
        f"/prueflaeufe/{prueflauf_id}/schritte/{schritt_id}/nachweise/foto",
        files={"datei": ("foto.jpg", io.BytesIO(JPEG_BYTES), "image/jpeg")},
    )
    nachweis_id = upload.json()["nachweis_id"]
    download = memory_client.get(f"/prueflaeufe/{prueflauf_id}/nachweise/{nachweis_id}/datei")
    assert download.status_code == 200
    assert download.headers["content-type"].startswith("image/jpeg")
    assert download.content == JPEG_BYTES


def test_json_nachweis_foto_409(memory_client: TestClient):
    prueflauf_id, schritt_id = _prepare_foto_endpoint(memory_client)
    response = memory_client.post(
        f"/prueflaeufe/{prueflauf_id}/schritte/{schritt_id}/nachweise",
        json={"art": "foto", "payload": {"datei_id": "fake"}},
    )
    assert response.status_code == 409
    assert response.json()["code"] == "foto_nur_per_multipart"


@pytest.mark.parametrize("art", [a for a in NACHWEIS_ART_API_WERTE if a != "foto"])
def test_andere_nachweisarten_weiterhin_json(memory_client: TestClient, art: str):
    prueflauf_id, schritt_id = _prepare_foto_endpoint(memory_client)
    response = memory_client.post(
        f"/prueflaeufe/{prueflauf_id}/schritte/{schritt_id}/nachweise",
        json={"art": art, "payload": {"spannung": 230}},
    )
    assert response.status_code == 201


@pytest.mark.postgresql
def test_postgresql_foto_roundtrip(pg_client: TestClient):
    kodierung = _bootstrap_postgresql_katalog(pg_client)
    prueflauf_id, schritt_id = _prepare_foto_endpoint(pg_client, produktkodierung=kodierung)
    upload = pg_client.post(
        f"/prueflaeufe/{prueflauf_id}/schritte/{schritt_id}/nachweise/foto",
        files={"datei": ("foto.jpg", io.BytesIO(JPEG_BYTES), "image/jpeg")},
    )
    assert upload.status_code == 201
    nachweis_id = upload.json()["nachweis_id"]
    detail = pg_client.get(f"/prueflaeufe/{prueflauf_id}")
    assert detail.status_code == 200
    payload = detail.json()["schritte"][0]["nachweise"][0]["payload"]
    assert payload["mime_type"] == "image/jpeg"
    download = pg_client.get(f"/prueflaeufe/{prueflauf_id}/nachweise/{nachweis_id}/datei")
    assert download.status_code == 200
    assert download.content == JPEG_BYTES


@pytest.mark.postgresql
def test_postgresql_abschluss_mit_foto_snapshot_nur_nachweis_id(pg_client: TestClient):
    kodierung = _bootstrap_postgresql_katalog(pg_client)
    prueflauf_id, schritt_id = _prepare_foto_endpoint(pg_client, produktkodierung=kodierung)
    upload = pg_client.post(
        f"/prueflaeufe/{prueflauf_id}/schritte/{schritt_id}/nachweise/foto",
        files={"datei": ("foto.jpg", io.BytesIO(JPEG_BYTES), "image/jpeg")},
    )
    assert upload.status_code == 201
    beurteilung = pg_client.post(f"/prueflaeufe/{prueflauf_id}/schritte/{schritt_id}/beurteilung")
    assert beurteilung.status_code == 204
    abschluss = pg_client.post(f"/prueflaeufe/{prueflauf_id}/abschluss")
    assert abschluss.status_code == 200
    assert "snapshot_id" in abschluss.json()
