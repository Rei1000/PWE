"""API-Tests — Katalog-Setup für Automatisierung (Gate 6.3a, ADR-0017)."""

from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient

from adapters.persistence.in_memory import InMemoryBibliothekRepository, InMemoryKatalogRepository
from adapters.simulation.externes_kommando import SimuliertesExternesKommandoPort
from api.app import create_app
from api.deps import in_memory_deps
from application.katalog.entwurf_anlegen import EntwurfAnlegen
from application.katalog.routine_anlegen import RoutineAnlegen
from application.katalog.routine_zuweisen import RoutineProzedurSchrittZuweisen
from application.katalog.externes_kommando_anlegen import ExternesKommandoAnlegen
from domain.katalog.produktdefinition import ProzedurSchrittEntwurf
from domain.pruefausfuehrung.kommando_ausfuehrung import ExternesKommandoAntwort

KOMMANDOCODE = "READ_VOLTAGE"
SCHRIITT_ID = "schritt-a"


def _unique_kodierung() -> str:
    return str(10_000_000_000 + uuid.uuid4().int % 9_000_000_000)


@pytest.fixture
def client():
    deps = in_memory_deps()
    assert isinstance(deps.kommando_port, SimuliertesExternesKommandoPort)
    deps.kommando_port.registriere_antwort(
        KOMMANDOCODE,
        ExternesKommandoAntwort(
            rohdaten="RAW:230",
            extrahierte_werte={"spannung": 230},
        ),
    )
    with TestClient(create_app(deps)) as http_client:
        yield http_client


def _entwurf_anlegen(client: TestClient, produktkodierung: str) -> str:
    response = client.post(
        "/katalog/entwuerfe",
        json={
            "produktkodierung": produktkodierung,
            "prozedur_schritte": [
                {
                    "schritt_id": SCHRIITT_ID,
                    "vorlage_id": "vorlage-a",
                    "ist_pflicht": True,
                    "reihenfolge": 1,
                    "sollvorgaben": {"spannung": {"min": 220, "max": 240}},
                }
            ],
            "sollbestueckung": [],
        },
    )
    assert response.status_code == 201
    return response.json()["produktdefinition_id"]


def test_http_e2e_setup_und_automatisierung_ausfuehren(client: TestClient):
    kodierung = _unique_kodierung()

    kommando = client.post(
        "/katalog/bibliothek/kommandos",
        json={"bezeichnung": "Spannung messen", "kommandocode": KOMMANDOCODE},
    )
    assert kommando.status_code == 201
    kommando_body = kommando.json()
    assert kommando_body == {
        "kommando_id": kommando_body["kommando_id"],
        "bezeichnung": "Spannung messen",
    }
    assert "kommandocode" not in kommando_body
    kommando_id = kommando_body["kommando_id"]

    produktdefinition_id = _entwurf_anlegen(client, kodierung)

    zuweisung = client.put(
        f"/katalog/entwuerfe/{produktdefinition_id}/schritte/{SCHRIITT_ID}/automatisierung",
        json={"kommando_id": kommando_id},
    )
    assert zuweisung.status_code == 200
    assert zuweisung.json() == {
        "produktdefinition_id": produktdefinition_id,
        "schritt_id": SCHRIITT_ID,
        "kommando_id": kommando_id,
        "routine_id": None,
    }

    version = client.post(f"/katalog/entwuerfe/{produktdefinition_id}/veroeffentlichen")
    assert version.status_code == 201

    start = client.post(
        "/prueflaeufe",
        json={
            "produktkodierung": kodierung,
            "pruefobjekt_kennung": "GER-E2E-63A",
            "pruefer_id": "pruefer-1",
        },
    )
    assert start.status_code == 201
    prueflauf_id = start.json()["prueflauf_id"]

    detail = client.get(f"/prueflaeufe/{prueflauf_id}")
    assert detail.status_code == 200

    auto = client.post(
        f"/prueflaeufe/{prueflauf_id}/schritte/{SCHRIITT_ID}/automatisierung/ausfuehren"
    )
    assert auto.status_code == 200
    body = auto.json()
    assert body["fehlgeschlagen"] is False
    assert body["ausfuehrung_id"]
    assert len(body["nachweise"]) >= 1


def test_kommando_anlegen_201(client: TestClient):
    response = client.post(
        "/katalog/bibliothek/kommandos",
        json={"bezeichnung": "Test", "kommandocode": "CMD1"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["kommando_id"]
    assert body["bezeichnung"] == "Test"
    assert "kommandocode" not in body


def test_kommando_anlegen_zwei_posts_unterschiedliche_ids(client: TestClient):
    r1 = client.post(
        "/katalog/bibliothek/kommandos",
        json={"bezeichnung": "A", "kommandocode": "A"},
    )
    r2 = client.post(
        "/katalog/bibliothek/kommandos",
        json={"bezeichnung": "B", "kommandocode": "B"},
    )
    assert r1.json()["kommando_id"] != r2.json()["kommando_id"]


def test_kommando_anlegen_extra_feld_422(client: TestClient):
    response = client.post(
        "/katalog/bibliothek/kommandos",
        json={
            "bezeichnung": "X",
            "kommandocode": "X",
            "kommando_id": "client-id",
        },
    )
    assert response.status_code == 422
    assert response.json()["code"] == "validation"


def test_kommando_anlegen_ungueltig_422(client: TestClient):
    response = client.post(
        "/katalog/bibliothek/kommandos",
        json={"bezeichnung": "X"},
    )
    assert response.status_code == 422
    assert response.json()["code"] == "validation"


def test_zuweisung_happy_path_200(client: TestClient):
    kodierung = _unique_kodierung()
    kommando = client.post(
        "/katalog/bibliothek/kommandos",
        json={"bezeichnung": "M", "kommandocode": KOMMANDOCODE},
    ).json()
    pd_id = _entwurf_anlegen(client, kodierung)
    response = client.put(
        f"/katalog/entwuerfe/{pd_id}/schritte/{SCHRIITT_ID}/automatisierung",
        json={"kommando_id": kommando["kommando_id"]},
    )
    assert response.status_code == 200
    assert response.json()["routine_id"] is None


def test_zuweisung_idempotent_gleiche_kommando_id(client: TestClient):
    kodierung = _unique_kodierung()
    kommando_id = client.post(
        "/katalog/bibliothek/kommandos",
        json={"bezeichnung": "M", "kommandocode": KOMMANDOCODE},
    ).json()["kommando_id"]
    pd_id = _entwurf_anlegen(client, kodierung)
    url = f"/katalog/entwuerfe/{pd_id}/schritte/{SCHRIITT_ID}/automatisierung"
    r1 = client.put(url, json={"kommando_id": kommando_id})
    r2 = client.put(url, json={"kommando_id": kommando_id})
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json() == r2.json()


def test_zuweisung_anderes_kommando_409(client: TestClient):
    kodierung = _unique_kodierung()
    k1 = client.post(
        "/katalog/bibliothek/kommandos",
        json={"bezeichnung": "K1", "kommandocode": "K1"},
    ).json()["kommando_id"]
    k2 = client.post(
        "/katalog/bibliothek/kommandos",
        json={"bezeichnung": "K2", "kommandocode": "K2"},
    ).json()["kommando_id"]
    pd_id = _entwurf_anlegen(client, kodierung)
    url = f"/katalog/entwuerfe/{pd_id}/schritte/{SCHRIITT_ID}/automatisierung"
    assert client.put(url, json={"kommando_id": k1}).status_code == 200
    response = client.put(url, json={"kommando_id": k2})
    assert response.status_code == 409
    assert response.json()["code"] == "automatisierung_doppelt_zugewiesen"


def test_zuweisung_entwurf_fehlt_404(client: TestClient):
    kommando_id = client.post(
        "/katalog/bibliothek/kommandos",
        json={"bezeichnung": "M", "kommandocode": "M"},
    ).json()["kommando_id"]
    response = client.put(
        f"/katalog/entwuerfe/fehlend/schritte/{SCHRIITT_ID}/automatisierung",
        json={"kommando_id": kommando_id},
    )
    assert response.status_code == 404
    assert response.json()["code"] == "entwurf_nicht_gefunden"


def test_zuweisung_schritt_fehlt_404(client: TestClient):
    kodierung = _unique_kodierung()
    kommando_id = client.post(
        "/katalog/bibliothek/kommandos",
        json={"bezeichnung": "M", "kommandocode": "M"},
    ).json()["kommando_id"]
    pd_id = _entwurf_anlegen(client, kodierung)
    response = client.put(
        f"/katalog/entwuerfe/{pd_id}/schritte/fehlend/automatisierung",
        json={"kommando_id": kommando_id},
    )
    assert response.status_code == 404
    assert response.json()["code"] == "prozedur_schritt_nicht_gefunden"


def test_zuweisung_kommando_fehlt_404(client: TestClient):
    kodierung = _unique_kodierung()
    pd_id = _entwurf_anlegen(client, kodierung)
    response = client.put(
        f"/katalog/entwuerfe/{pd_id}/schritte/{SCHRIITT_ID}/automatisierung",
        json={"kommando_id": "fehlend"},
    )
    assert response.status_code == 404
    assert response.json()["code"] == "externes_kommando_nicht_gefunden"


def test_zuweisung_bei_vorhandener_routine_409():
    deps = in_memory_deps()
    katalog = deps.katalog
    bibliothek = deps.bibliothek
    assert isinstance(katalog, InMemoryKatalogRepository)
    assert isinstance(bibliothek, InMemoryBibliothekRepository)

    k1 = ExternesKommandoAnlegen(bibliothek).execute(bezeichnung="K1", kommandocode="K1")
    routine = RoutineAnlegen(bibliothek).execute(bezeichnung="R", kommando_ids=(k1.kommando_id,))
    entwurf = EntwurfAnlegen(katalog).execute(
        produktkodierung=_unique_kodierung(),
        prozedur_schritte=(
            ProzedurSchrittEntwurf(
                schritt_id=SCHRIITT_ID,
                vorlage_id="v",
                ist_pflicht=True,
                reihenfolge=1,
            ),
        ),
    )
    RoutineProzedurSchrittZuweisen(katalog, bibliothek).execute(
        entwurf.produktdefinition_id,
        SCHRIITT_ID,
        routine.routine_id,
    )
    k2 = ExternesKommandoAnlegen(bibliothek).execute(bezeichnung="K2", kommandocode="K2")

    with TestClient(create_app(deps)) as client:
        response = client.put(
            f"/katalog/entwuerfe/{entwurf.produktdefinition_id}/schritte/{SCHRIITT_ID}/automatisierung",
            json={"kommando_id": k2.kommando_id},
        )
    assert response.status_code == 409
    assert response.json()["code"] == "automatisierung_doppelt_zugewiesen"


def test_zuweisung_routine_id_im_request_422(client: TestClient):
    kodierung = _unique_kodierung()
    pd_id = _entwurf_anlegen(client, kodierung)
    response = client.put(
        f"/katalog/entwuerfe/{pd_id}/schritte/{SCHRIITT_ID}/automatisierung",
        json={"kommando_id": "x", "routine_id": "y"},
    )
    assert response.status_code == 422


def test_zuweisung_kommandocode_im_request_422(client: TestClient):
    kodierung = _unique_kodierung()
    pd_id = _entwurf_anlegen(client, kodierung)
    response = client.put(
        f"/katalog/entwuerfe/{pd_id}/schritte/{SCHRIITT_ID}/automatisierung",
        json={"kommandocode": "HACK"},
    )
    assert response.status_code == 422


def test_zuweisung_extra_feld_422(client: TestClient):
    kodierung = _unique_kodierung()
    pd_id = _entwurf_anlegen(client, kodierung)
    response = client.put(
        f"/katalog/entwuerfe/{pd_id}/schritte/{SCHRIITT_ID}/automatisierung",
        json={"kommando_id": "x", "adapter": "com"},
    )
    assert response.status_code == 422
