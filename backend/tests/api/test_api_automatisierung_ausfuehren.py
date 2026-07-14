"""API-Tests — Automatisierung ausführen (Gate 7.3f, ADR-0016)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from adapters.persistence.in_memory import InMemoryKatalogRepository, InMemoryPrueflaufRepository
from adapters.simulation.externes_kommando import SimuliertesExternesKommandoPort
from api.app import create_app
from api.deps import in_memory_deps
from domain.katalog.externes_kommando import MaterialisiertesExternesKommando
from domain.katalog.routine import (
    MaterialisierteKommandoAktion,
    MaterialisierteRoutine,
    MaterialisierteRoutineHerkunft,
)
from domain.katalog.version import MaterialisierterProzedurSchritt, ProduktdefinitionsVersion
from domain.pruefausfuehrung.kommando_ausfuehrung import ExternesKommandoAntwort
from helpers import CountingKommandoPort, CountingPrueflaufRepository

KOMMANDO_ID = "cmd-api-auto"
KOMMANDOCODE = "READ_VOLTAGE"
AUTO_PATH = "/prueflaeufe/{pid}/schritte/{sid}/automatisierung/ausfuehren"


def _auto_url(prueflauf_id: str, schritt_id: str = "schritt-a") -> str:
    return AUTO_PATH.format(pid=prueflauf_id, sid=schritt_id)


@pytest.fixture
def client():
    deps = in_memory_deps()
    assert isinstance(deps.katalog, InMemoryKatalogRepository)
    deps.katalog.register_aktive_version(
        ProduktdefinitionsVersion(
            version_id="ver-auto",
            produktdefinition_id="pd-auto",
            produktkodierung="1234567890",
            prozedur_schritte=(
                MaterialisierterProzedurSchritt(
                    schritt_id="schritt-a",
                    vorlage_id="vorlage-a",
                    ist_pflicht=True,
                    reihenfolge=1,
                    externes_kommando=MaterialisiertesExternesKommando(
                        kommando_id=KOMMANDO_ID,
                        bezeichnung="Spannung",
                        kommandocode=KOMMANDOCODE,
                    ),
                ),
            ),
        )
    )
    assert isinstance(deps.kommando_port, SimuliertesExternesKommandoPort)
    deps.kommando_port.registriere_antwort(
        KOMMANDOCODE,
        ExternesKommandoAntwort(
            rohdaten="RAW:230",
            extrahierte_werte={"spannung": 230},
        ),
    )
    app = create_app(deps)
    with TestClient(app) as http_client:
        yield http_client


def _start_prueflauf(client: TestClient) -> str:
    response = client.post(
        "/prueflaeufe",
        json={
            "produktkodierung": "1234567890",
            "pruefobjekt_kennung": "GER-AUTO",
            "pruefer_id": "pruefer-1",
        },
    )
    assert response.status_code == 201
    return response.json()["prueflauf_id"]


def test_api_automatisierung_happy_path_einzelkommando(client: TestClient):
    prueflauf_id = _start_prueflauf(client)
    response = client.post(_auto_url(prueflauf_id))

    assert response.status_code == 200
    body = response.json()
    assert body["fehlgeschlagen"] is False
    assert body["fehlerart"] is None
    assert body["abgebrochen_bei_aktion_position"] is None
    assert body["ausgefuehrte_aktionen"] == 1
    assert body["ausfuehrung_id"]
    assert len(body["nachweise"]) == 2
    assert "detail" not in body
    assert "code" not in body


def test_api_automatisierung_bibliotheksroutine_mehrere_aktionen():
    deps = in_memory_deps()
    katalog = deps.katalog
    assert isinstance(katalog, InMemoryKatalogRepository)
    katalog.register_aktive_version(
        ProduktdefinitionsVersion(
            version_id="ver-zwei",
            produktdefinition_id="pd-zwei",
            produktkodierung="2222222222",
            prozedur_schritte=(
                MaterialisierterProzedurSchritt(
                    schritt_id="schritt-a",
                    vorlage_id="vorlage-a",
                    ist_pflicht=True,
                    reihenfolge=1,
                    materialisierte_routine=MaterialisierteRoutine(
                        herkunft=MaterialisierteRoutineHerkunft.BIBLIOTHEK,
                        routine_id="r-api",
                        bezeichnung="Zwei",
                        aktionen=(
                            MaterialisierteKommandoAktion(
                                position=1,
                                kommando_id="k1",
                                bezeichnung="A",
                                kommandocode="CMD1",
                            ),
                            MaterialisierteKommandoAktion(
                                position=2,
                                kommando_id="k2",
                                bezeichnung="B",
                                kommandocode="CMD2",
                            ),
                        ),
                    ),
                ),
            ),
        )
    )
    port = deps.kommando_port
    assert isinstance(port, SimuliertesExternesKommandoPort)
    port.registriere_antwort(
        "CMD1",
        ExternesKommandoAntwort(rohdaten="RAW:1", extrahierte_werte={"a": 1}),
    )
    port.registriere_antwort(
        "CMD2",
        ExternesKommandoAntwort(rohdaten="RAW:2", extrahierte_werte={"b": 2}),
    )
    with TestClient(create_app(deps)) as client:
        start = client.post(
            "/prueflaeufe",
            json={
                "produktkodierung": "2222222222",
                "pruefobjekt_kennung": "GER-ZWEI",
                "pruefer_id": "pruefer-1",
            },
        )
        prueflauf_id = start.json()["prueflauf_id"]
        response = client.post(_auto_url(prueflauf_id))

    assert response.status_code == 200
    body = response.json()
    assert body["fehlgeschlagen"] is False
    assert body["ausgefuehrte_aktionen"] == 2
    assert len(body["nachweise"]) == 4


def test_api_teilfehler_transport_ohne_roh_http_200():
    deps = in_memory_deps()
    katalog = deps.katalog
    assert isinstance(katalog, InMemoryKatalogRepository)
    katalog.register_aktive_version(
        ProduktdefinitionsVersion(
            version_id="ver-teil",
            produktdefinition_id="pd-teil",
            produktkodierung="3333333333",
            prozedur_schritte=(
                MaterialisierterProzedurSchritt(
                    schritt_id="schritt-a",
                    vorlage_id="vorlage-a",
                    ist_pflicht=True,
                    reihenfolge=1,
                    materialisierte_routine=MaterialisierteRoutine(
                        herkunft=MaterialisierteRoutineHerkunft.BIBLIOTHEK,
                        routine_id="r-teil",
                        bezeichnung="Zwei",
                        aktionen=(
                            MaterialisierteKommandoAktion(
                                position=1,
                                kommando_id="k1",
                                bezeichnung="A",
                                kommandocode="CMD1",
                            ),
                            MaterialisierteKommandoAktion(
                                position=2,
                                kommando_id="k2",
                                bezeichnung="B",
                                kommandocode="CMD2",
                            ),
                        ),
                    ),
                ),
            ),
        )
    )
    inner_repo = InMemoryPrueflaufRepository()
    deps.prueflauf_repo = CountingPrueflaufRepository(inner_repo)
    port = CountingKommandoPort(
        antworten={
            "CMD1": ExternesKommandoAntwort(
                rohdaten="RAW:1",
                extrahierte_werte={"a": 1},
            ),
        }
    )
    deps.kommando_port = port
    with TestClient(create_app(deps)) as client:
        start = client.post(
            "/prueflaeufe",
            json={
                "produktkodierung": "3333333333",
                "pruefobjekt_kennung": "GER-TEIL",
                "pruefer_id": "pruefer-1",
            },
        )
        prueflauf_id = start.json()["prueflauf_id"]
        saves_vor_ausfuehrung = deps.prueflauf_repo.save_count
        response = client.post(_auto_url(prueflauf_id))

    assert response.status_code == 200
    body = response.json()
    assert body["fehlgeschlagen"] is True
    assert body["fehlerart"] == "keine_geraeteantwort"
    assert body["abgebrochen_bei_aktion_position"] == 2
    assert len(body["nachweise"]) == 2
    assert "detail" not in body
    assert deps.prueflauf_repo.save_count == saves_vor_ausfuehrung + 1


def test_api_teilfehler_geraete_err_http_200():
    deps = in_memory_deps()
    katalog = deps.katalog
    assert isinstance(katalog, InMemoryKatalogRepository)
    katalog.register_aktive_version(
        ProduktdefinitionsVersion(
            version_id="ver-err",
            produktdefinition_id="pd-err",
            produktkodierung="4444444444",
            prozedur_schritte=(
                MaterialisierterProzedurSchritt(
                    schritt_id="schritt-a",
                    vorlage_id="vorlage-a",
                    ist_pflicht=True,
                    reihenfolge=1,
                    externes_kommando=MaterialisiertesExternesKommando(
                        kommando_id=KOMMANDO_ID,
                        bezeichnung="Spannung",
                        kommandocode=KOMMANDOCODE,
                    ),
                ),
            ),
        )
    )
    port = deps.kommando_port
    assert isinstance(port, SimuliertesExternesKommandoPort)
    port.registriere_antwort(
        KOMMANDOCODE,
        ExternesKommandoAntwort(rohdaten="ERR FAIL", erfolgreich=False),
    )
    with TestClient(create_app(deps)) as client:
        start = client.post(
            "/prueflaeufe",
            json={
                "produktkodierung": "4444444444",
                "pruefobjekt_kennung": "GER-ERR",
                "pruefer_id": "pruefer-1",
            },
        )
        response = client.post(_auto_url(start.json()["prueflauf_id"]))

    assert response.status_code == 200
    body = response.json()
    assert body["fehlgeschlagen"] is True
    assert body["fehlerart"] == "geraetefehlschlag"
    assert len(body["nachweise"]) == 1
    assert body["nachweise"][0]["art"] == "rohantwort"


def test_api_parserfehler_http_200():
    deps = in_memory_deps()
    katalog = deps.katalog
    assert isinstance(katalog, InMemoryKatalogRepository)
    katalog.register_aktive_version(
        ProduktdefinitionsVersion(
            version_id="ver-parse",
            produktdefinition_id="pd-parse",
            produktkodierung="5555555555",
            prozedur_schritte=(
                MaterialisierterProzedurSchritt(
                    schritt_id="schritt-a",
                    vorlage_id="vorlage-a",
                    ist_pflicht=True,
                    reihenfolge=1,
                    externes_kommando=MaterialisiertesExternesKommando(
                        kommando_id=KOMMANDO_ID,
                        bezeichnung="Spannung",
                        kommandocode=KOMMANDOCODE,
                    ),
                ),
            ),
        )
    )
    port = deps.kommando_port
    assert isinstance(port, SimuliertesExternesKommandoPort)
    port.registriere_antwort(
        KOMMANDOCODE,
        ExternesKommandoAntwort(
            rohdaten="OK unparseable",
            erfolgreich=False,
        ),
    )
    with TestClient(create_app(deps)) as client:
        start = client.post(
            "/prueflaeufe",
            json={
                "produktkodierung": "5555555555",
                "pruefobjekt_kennung": "GER-PARSE",
                "pruefer_id": "pruefer-1",
            },
        )
        response = client.post(_auto_url(start.json()["prueflauf_id"]))

    assert response.status_code == 200
    body = response.json()
    assert body["fehlgeschlagen"] is True
    assert body["fehlerart"] == "geraetefehlschlag"
    assert len(body["nachweise"]) == 1


def test_api_prueflauf_fehlt_404(client: TestClient):
    response = client.post(_auto_url("fehlend"))
    assert response.status_code == 404
    body = response.json()
    assert body["code"] == "prueflauf_nicht_gefunden"
    assert "detail" in body
    assert "ausfuehrung_id" not in body


def test_api_schritt_fehlt_404(client: TestClient):
    prueflauf_id = _start_prueflauf(client)
    response = client.post(_auto_url(prueflauf_id, "fehlend"))
    assert response.status_code == 404
    assert response.json()["code"] == "materialisierter_prozedur_schritt_nicht_gefunden"


def test_api_keine_automatisierung_409():
    deps = in_memory_deps()
    katalog = deps.katalog
    assert isinstance(katalog, InMemoryKatalogRepository)
    katalog.register_aktive_version(
        ProduktdefinitionsVersion(
            version_id="ver-manuell",
            produktdefinition_id="pd-manuell",
            produktkodierung="6666666666",
            prozedur_schritte=(
                MaterialisierterProzedurSchritt(
                    schritt_id="schritt-a",
                    vorlage_id="vorlage-a",
                    ist_pflicht=True,
                    reihenfolge=1,
                ),
            ),
        )
    )
    port = CountingKommandoPort()
    deps.kommando_port = port
    with TestClient(create_app(deps)) as client:
        start = client.post(
            "/prueflaeufe",
            json={
                "produktkodierung": "6666666666",
                "pruefobjekt_kennung": "GER-M",
                "pruefer_id": "pruefer-1",
            },
        )
        response = client.post(_auto_url(start.json()["prueflauf_id"]))

    assert response.status_code == 409
    assert response.json()["code"] == "keine_automatisierung_am_schritt"
    assert port.ausfuehren_count == 0


def test_api_abgeschlossener_prueflauf_409():
    deps = in_memory_deps()
    katalog = deps.katalog
    assert isinstance(katalog, InMemoryKatalogRepository)
    katalog.register_aktive_version(
        ProduktdefinitionsVersion(
            version_id="ver-auto",
            produktdefinition_id="pd-auto",
            produktkodierung="1234567890",
            prozedur_schritte=(
                MaterialisierterProzedurSchritt(
                    schritt_id="schritt-a",
                    vorlage_id="vorlage-a",
                    ist_pflicht=True,
                    reihenfolge=1,
                    externes_kommando=MaterialisiertesExternesKommando(
                        kommando_id=KOMMANDO_ID,
                        bezeichnung="Spannung",
                        kommandocode=KOMMANDOCODE,
                    ),
                ),
            ),
        )
    )
    port = CountingKommandoPort(
        antworten={
            KOMMANDOCODE: ExternesKommandoAntwort(
                rohdaten="RAW:230",
                extrahierte_werte={"spannung": 230},
            ),
        }
    )
    deps.kommando_port = port
    with TestClient(create_app(deps)) as client:
        prueflauf_id = _start_prueflauf(client)
        client.post(
            f"/prueflaeufe/{prueflauf_id}/schritte/schritt-a/nachweise",
            json={"art": "messwert", "payload": {"spannung": 230}},
        )
        client.post(f"/prueflaeufe/{prueflauf_id}/schritte/schritt-a/beurteilung")
        client.post(f"/prueflaeufe/{prueflauf_id}/abschluss")
        response = client.post(_auto_url(prueflauf_id))

    assert response.status_code == 409
    assert response.json()["code"] == "invariant_verletzt"
    assert port.ausfuehren_count == 0


def test_api_inkonsistente_materialisierung_409():
    mr = MaterialisierteRoutine(
        herkunft=MaterialisierteRoutineHerkunft.EINZELKOMMANDO,
        routine_id=None,
        bezeichnung="A",
        aktionen=(
            MaterialisierteKommandoAktion(
                position=1,
                kommando_id="k1",
                bezeichnung="A",
                kommandocode="A",
            ),
        ),
    )
    deps = in_memory_deps()
    katalog = deps.katalog
    assert isinstance(katalog, InMemoryKatalogRepository)
    katalog.register_aktive_version(
        ProduktdefinitionsVersion(
            version_id="ver-ink",
            produktdefinition_id="pd-ink",
            produktkodierung="7777777777",
            prozedur_schritte=(
                MaterialisierterProzedurSchritt(
                    schritt_id="schritt-a",
                    vorlage_id="vorlage-a",
                    ist_pflicht=True,
                    reihenfolge=1,
                    materialisierte_routine=mr,
                    externes_kommando=MaterialisiertesExternesKommando(
                        kommando_id="k1",
                        bezeichnung="X",
                        kommandocode="DIFF",
                    ),
                ),
            ),
        )
    )
    port = CountingKommandoPort()
    deps.kommando_port = port
    with TestClient(create_app(deps)) as client:
        start = client.post(
            "/prueflaeufe",
            json={
                "produktkodierung": "7777777777",
                "pruefobjekt_kennung": "GER-INK",
                "pruefer_id": "pruefer-1",
            },
        )
        response = client.post(_auto_url(start.json()["prueflauf_id"]))

    assert response.status_code == 409
    assert response.json()["code"] == "materialisierte_automatisierung_inkonsistent"
    assert port.ausfuehren_count == 0


def test_api_ungueltiger_body_422(client: TestClient):
    prueflauf_id = _start_prueflauf(client)
    response = client.post(
        _auto_url(prueflauf_id),
        json={"kommandocode": "HACK"},
    )
    assert response.status_code == 422
    assert response.json()["code"] == "validation"


def test_api_nicht_idempotent_zwei_wellen(client: TestClient):
    prueflauf_id = _start_prueflauf(client)
    r1 = client.post(_auto_url(prueflauf_id))
    r2 = client.post(_auto_url(prueflauf_id))
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()["ausfuehrung_id"] != r2.json()["ausfuehrung_id"]
    detail = client.get(f"/prueflaeufe/{prueflauf_id}").json()
    assert len(detail["schritte"][0]["nachweise"]) == 4


def test_legacy_kommando_endpunkt_unveraendert_201(client: TestClient):
    prueflauf_id = _start_prueflauf(client)
    response = client.post(
        f"/prueflaeufe/{prueflauf_id}/schritte/schritt-a/kommandos/{KOMMANDO_ID}/ausfuehren"
    )
    assert response.status_code == 201
    assert "nachweise" in response.json()


def test_legacy_transport_ohne_roh_weiterhin_409_rollback():
    deps = in_memory_deps()
    katalog = deps.katalog
    assert isinstance(katalog, InMemoryKatalogRepository)
    katalog.register_aktive_version(
        ProduktdefinitionsVersion(
            version_id="ver-auto",
            produktdefinition_id="pd-auto",
            produktkodierung="1234567890",
            prozedur_schritte=(
                MaterialisierterProzedurSchritt(
                    schritt_id="schritt-a",
                    vorlage_id="vorlage-a",
                    ist_pflicht=True,
                    reihenfolge=1,
                    externes_kommando=MaterialisiertesExternesKommando(
                        kommando_id=KOMMANDO_ID,
                        bezeichnung="Spannung",
                        kommandocode=KOMMANDOCODE,
                    ),
                ),
            ),
        )
    )
    deps.kommando_port = SimuliertesExternesKommandoPort()
    with TestClient(create_app(deps)) as client:
        prueflauf_id = _start_prueflauf(client)
        response = client.post(
            f"/prueflaeufe/{prueflauf_id}/schritte/schritt-a/kommandos/{KOMMANDO_ID}/ausfuehren"
        )
    assert response.status_code == 409
    assert response.json()["code"] == "externes_kommando_adapter_fehler"
    assert "nachweise" not in response.json()
