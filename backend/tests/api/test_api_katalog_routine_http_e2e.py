"""HTTP-E2E — Routine-Bibliothek über Gate 8.2a bis Automatisierung ausführen (Gate 8.2b1 Regression)."""

from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient

from adapters.simulation.externes_kommando import SimuliertesExternesKommandoPort
from api.app import create_app
from api.deps import in_memory_deps
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


def test_http_e2e_routine_anlegen_zuweisen_veroeffentlichen_prueflauf_ausfuehren(
    client: TestClient,
):
    kodierung = _unique_kodierung()

    kommando = client.post(
        "/katalog/bibliothek/kommandos",
        json={"bezeichnung": "Spannung messen", "kommandocode": KOMMANDOCODE},
    )
    assert kommando.status_code == 201
    kommando_id = kommando.json()["kommando_id"]

    routine = client.post(
        "/katalog/bibliothek/routinen",
        json={"bezeichnung": "Spannungs-Routine", "kommando_ids": [kommando_id]},
    )
    assert routine.status_code == 201
    routine_body = routine.json()
    routine_id = routine_body["routine_id"]
    assert routine_body["bezeichnung"] == "Spannungs-Routine"

    vorlage = client.post(
        "/katalog/bibliothek/vorlagen",
        json={"bezeichnung": "Spannungsmessung", "beschreibung": "Manuelle Eingabe"},
    )
    assert vorlage.status_code == 201
    vorlage_id = vorlage.json()["vorlage_id"]

    entwurf = client.post(
        "/katalog/entwuerfe",
        json={
            "produktkodierung": kodierung,
            "prozedur_schritte": [
                {
                    "schritt_id": SCHRIITT_ID,
                    "vorlage_id": vorlage_id,
                    "ist_pflicht": True,
                    "reihenfolge": 1,
                    "sollvorgaben": {"spannung": {"min": 220, "max": 240}},
                }
            ],
            "sollbestueckung": [],
        },
    )
    assert entwurf.status_code == 201
    produktdefinition_id = entwurf.json()["produktdefinition_id"]

    zuweisung = client.put(
        f"/katalog/entwuerfe/{produktdefinition_id}/schritte/{SCHRIITT_ID}/automatisierung",
        json={"routine_id": routine_id},
    )
    assert zuweisung.status_code == 200
    assert zuweisung.json() == {
        "produktdefinition_id": produktdefinition_id,
        "schritt_id": SCHRIITT_ID,
        "kommando_id": None,
        "routine_id": routine_id,
    }

    version = client.post(f"/katalog/entwuerfe/{produktdefinition_id}/veroeffentlichen")
    assert version.status_code == 201
    version_id = version.json()["version_id"]
    assert version_id

    start = client.post(
        "/prueflaeufe",
        json={
            "produktkodierung": kodierung,
            "pruefobjekt_kennung": "GER-E2E-82B1",
        },
    )
    assert start.status_code == 201
    prueflauf_id = start.json()["prueflauf_id"]
    assert start.json()["version_id"] == version_id

    detail = client.get(f"/prueflaeufe/{prueflauf_id}")
    assert detail.status_code == 200
    schritte = detail.json()["schritte"]
    assert len(schritte) == 1
    assert schritte[0]["hat_automatisierung"] is True
    assert schritte[0]["kann_automatisierung_ausfuehren"] is True

    auto = client.post(
        f"/prueflaeufe/{prueflauf_id}/schritte/{SCHRIITT_ID}/automatisierung/ausfuehren"
    )
    assert auto.status_code == 200
    body = auto.json()
    assert body["fehlgeschlagen"] is False
    assert body["ausfuehrung_id"]
    assert body["ausgefuehrte_aktionen"] >= 1
    assert len(body["nachweise"]) >= 1
from tests.support.auth import login_as_admin
