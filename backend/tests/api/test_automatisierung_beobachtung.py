"""Monitoring-Baseline — fachliche Beobachtung der Automatisierung (Gate 7.4c)."""

from __future__ import annotations

import logging

import pytest
from fastapi.testclient import TestClient

from adapters.persistence.in_memory import InMemoryKatalogRepository
from adapters.simulation.externes_kommando import SimuliertesExternesKommandoPort
from api.app import create_app
from api.automatisierung_beobachtung import (
    EVENT_AUSGEFUEHRT,
    EVENT_NICHT_BEGONNEN,
    beobachte_ausgefuehrte_automatisierung,
    beobachte_automatisierung_nicht_begonnen,
)
from api.deps import in_memory_deps
from application.pruefausfuehrung.kommando_ausfuehrung_kern import KommandoFehlerart
from application.pruefausfuehrung.routine_ausfuehren import RoutineAusfuehrungErgebnis
from domain.katalog.routine import (
    MaterialisierteKommandoAktion,
    MaterialisierteRoutine,
    MaterialisierteRoutineHerkunft,
)
from domain.katalog.version import MaterialisierterProzedurSchritt, ProduktdefinitionsVersion
from domain.pruefausfuehrung.errors import PrueflaufNichtGefunden
from domain.pruefausfuehrung.kommando_ausfuehrung import ExternesKommandoAntwort

LOGGER_NAME = "pwe.automatisierung.beobachtung"
KOMMANDOCODE = "READ_VOLTAGE"
AUTO_PATH = "/prueflaeufe/{pid}/schritte/{sid}/automatisierung/ausfuehren"


def _katalog_mit_routine(katalog: InMemoryKatalogRepository) -> None:
    katalog.register_aktive_version(
        ProduktdefinitionsVersion(
            version_id="ver-mon",
            produktdefinition_id="pd-mon",
            produktkodierung="1234567890",
            prozedur_schritte=(
                MaterialisierterProzedurSchritt(
                    schritt_id="schritt-a",
                    vorlage_id="vorlage-a",
                    ist_pflicht=True,
                    reihenfolge=1,
                    materialisierte_routine=MaterialisierteRoutine(
                        herkunft=MaterialisierteRoutineHerkunft.EINZELKOMMANDO,
                        bezeichnung="Spannung",
                        aktionen=(
                            MaterialisierteKommandoAktion(
                                position=1,
                                kommando_id="cmd-mon",
                                bezeichnung="Spannung",
                                kommandocode=KOMMANDOCODE,
                            ),
                        ),
                    ),
                ),
            ),
        )
    )


def _start_prueflauf(client: TestClient) -> str:
    response = client.post(
        "/prueflaeufe",
        json={
            "produktkodierung": "1234567890",
            "pruefobjekt_kennung": "GER-MON",
            "pruefer_id": "pruefer-1",
        },
    )
    assert response.status_code == 201
    return response.json()["prueflauf_id"]


def test_beobachte_ausgefuehrt_loggt_fehlgeschlagen_true(caplog: pytest.LogCaptureFixture):
    ergebnis = RoutineAusfuehrungErgebnis(
        ausfuehrung_id="aid-fail",
        nachweise=[],
        fehlgeschlagen=True,
        abgebrochen_bei_aktion_position=1,
        ausgefuehrte_aktionen=0,
        fehlerart=KommandoFehlerart.KEINE_GERAETEANTWORT,
    )
    with caplog.at_level(logging.INFO, logger=LOGGER_NAME):
        beobachte_ausgefuehrte_automatisierung(
            ergebnis, prueflauf_id="pl-1", schritt_id="s-1"
        )
    assert len(caplog.records) == 1
    msg = caplog.records[0].getMessage()
    assert EVENT_AUSGEFUEHRT in msg
    assert "http_status=200" in msg
    assert "fehlgeschlagen=True" in msg
    assert "fachlicher_erfolg=False" in msg
    assert "fehlerart=keine_geraeteantwort" in msg
    assert "ausfuehrung_id=aid-fail" in msg
    assert "nachweis_anzahl=0" in msg


def test_beobachte_ausgefuehrt_loggt_fachlichen_erfolg(caplog: pytest.LogCaptureFixture):
    ergebnis = RoutineAusfuehrungErgebnis(
        ausfuehrung_id="aid-ok",
        nachweise=[],
        fehlgeschlagen=False,
        abgebrochen_bei_aktion_position=None,
        ausgefuehrte_aktionen=1,
        fehlerart=None,
    )
    with caplog.at_level(logging.INFO, logger=LOGGER_NAME):
        beobachte_ausgefuehrte_automatisierung(
            ergebnis, prueflauf_id="pl-1", schritt_id="s-1"
        )
    msg = caplog.records[0].getMessage()
    assert "fehlgeschlagen=False" in msg
    assert "fachlicher_erfolg=True" in msg
    assert "http_status=200" in msg


def test_beobachte_nicht_begonnen_loggt_vorbedingungsfehler(caplog: pytest.LogCaptureFixture):
    with caplog.at_level(logging.INFO, logger=LOGGER_NAME):
        beobachte_automatisierung_nicht_begonnen(
            PrueflaufNichtGefunden("fehlt"),
            prueflauf_id="fehlend",
            schritt_id="s-1",
        )
    msg = caplog.records[0].getMessage()
    assert EVENT_NICHT_BEGONNEN in msg
    assert "http_status=404" in msg
    assert "code=prueflauf_nicht_gefunden" in msg
    assert "ausfuehrung_begonnen=false" in msg
    assert "fachlicher_erfolg=false" in msg


def test_api_erfolg_erzeugt_beobachtung_mit_fachlichem_erfolg(caplog: pytest.LogCaptureFixture):
    deps = in_memory_deps()
    assert isinstance(deps.katalog, InMemoryKatalogRepository)
    _katalog_mit_routine(deps.katalog)
    assert isinstance(deps.kommando_port, SimuliertesExternesKommandoPort)
    deps.kommando_port.registriere_antwort(
        KOMMANDOCODE,
        ExternesKommandoAntwort(rohdaten="RAW:230", extrahierte_werte={"spannung": 230}),
    )
    with TestClient(create_app(deps)) as client:
        prueflauf_id = _start_prueflauf(client)
        with caplog.at_level(logging.INFO, logger=LOGGER_NAME):
            response = client.post(AUTO_PATH.format(pid=prueflauf_id, sid="schritt-a"))
    assert response.status_code == 200
    assert response.json()["fehlgeschlagen"] is False
    messages = [r.getMessage() for r in caplog.records if EVENT_AUSGEFUEHRT in r.getMessage()]
    assert len(messages) == 1
    assert "fehlgeschlagen=False" in messages[0]
    assert "fachlicher_erfolg=True" in messages[0]
    assert "http_status=200" in messages[0]
    assert f"nachweis_anzahl={len(response.json()['nachweise'])}" in messages[0]


def test_api_http_200_fehlgeschlagen_true_beobachtung(caplog: pytest.LogCaptureFixture):
    deps = in_memory_deps()
    assert isinstance(deps.katalog, InMemoryKatalogRepository)
    _katalog_mit_routine(deps.katalog)
    deps.kommando_port = SimuliertesExternesKommandoPort()
    with TestClient(create_app(deps)) as client:
        prueflauf_id = _start_prueflauf(client)
        with caplog.at_level(logging.INFO, logger=LOGGER_NAME):
            response = client.post(AUTO_PATH.format(pid=prueflauf_id, sid="schritt-a"))
    assert response.status_code == 200
    assert response.json()["fehlgeschlagen"] is True
    messages = [r.getMessage() for r in caplog.records if EVENT_AUSGEFUEHRT in r.getMessage()]
    assert len(messages) == 1
    assert "fehlgeschlagen=True" in messages[0]
    assert "fachlicher_erfolg=False" in messages[0]
    assert "http_status=200" in messages[0]


def test_api_vorbedingungsfehler_beobachtung_nicht_begonnen(caplog: pytest.LogCaptureFixture):
    deps = in_memory_deps()
    with TestClient(create_app(deps)) as client:
        with caplog.at_level(logging.INFO, logger=LOGGER_NAME):
            response = client.post(AUTO_PATH.format(pid="fehlt", sid="schritt-a"))
    assert response.status_code == 404
    messages = [r.getMessage() for r in caplog.records if EVENT_NICHT_BEGONNEN in r.getMessage()]
    assert len(messages) == 1
    assert "ausfuehrung_begonnen=false" in messages[0]
    assert "http_status=404" in messages[0]
    assert EVENT_AUSGEFUEHRT not in " ".join(r.getMessage() for r in caplog.records)
