"""Tests — PWE_DEMO_MODE und Demo-Simulationsantworten (Gate 6.3c)."""

from __future__ import annotations

import pytest

from adapters.com.externes_kommando import ComExternesKommandoPort
from adapters.simulation.externes_kommando import SimuliertesExternesKommandoPort
from api.kommando_wiring import (
    DEMO_KOMMANDOCODE,
    DEMO_MESSWERT_WERT,
    KommandoAdapterConfigurationError,
    KommandoAdapterSettings,
    configure_kommando_adapter,
    create_kommando_port,
    reset_kommando_adapter_cache_for_tests,
)
from domain.pruefausfuehrung.kommando_ausfuehrung import ExternesKommandoAnfrage


@pytest.fixture(autouse=True)
def _reset_cache():
    reset_kommando_adapter_cache_for_tests()
    yield
    reset_kommando_adapter_cache_for_tests()


def test_demo_mode_default_false_ohne_env(monkeypatch):
    monkeypatch.delenv("PWE_DEMO_MODE", raising=False)
    monkeypatch.setenv("EXTERNES_KOMMANDO_ADAPTER", "simulation")
    settings = KommandoAdapterSettings.from_env()
    assert settings.demo_mode is False

    port = create_kommando_port(settings)
    assert isinstance(port, SimuliertesExternesKommandoPort)
    antwort = port.ausfuehren(ExternesKommandoAnfrage(kommandocode=DEMO_KOMMANDOCODE))
    assert antwort.erfolgreich is False
    assert antwort.rohdaten == ""


def test_demo_mode_false_keine_demo_antwort(monkeypatch):
    monkeypatch.setenv("PWE_DEMO_MODE", "false")
    monkeypatch.setenv("EXTERNES_KOMMANDO_ADAPTER", "simulation")
    port = create_kommando_port(KommandoAdapterSettings.from_env())
    antwort = port.ausfuehren(ExternesKommandoAnfrage(kommandocode=DEMO_KOMMANDOCODE))
    assert antwort.erfolgreich is False


def test_demo_mode_true_liefert_deterministische_antwort(monkeypatch):
    monkeypatch.setenv("PWE_DEMO_MODE", "true")
    monkeypatch.setenv("EXTERNES_KOMMANDO_ADAPTER", "simulation")
    port = create_kommando_port(KommandoAdapterSettings.from_env())
    antwort = port.ausfuehren(ExternesKommandoAnfrage(kommandocode=DEMO_KOMMANDOCODE))
    assert antwort.erfolgreich is True
    assert antwort.rohdaten == f"RAW:{DEMO_MESSWERT_WERT}"
    assert antwort.extrahierte_werte == {"messwert": DEMO_MESSWERT_WERT}


def test_demo_ports_request_scoped_getrennt(monkeypatch):
    monkeypatch.setenv("PWE_DEMO_MODE", "true")
    settings = KommandoAdapterSettings.from_env()
    p1 = create_kommando_port(settings)
    p2 = create_kommando_port(settings)
    assert p1 is not p2
    p1.registriere_antwort(
        "ANDERS",
        __import__(
            "domain.pruefausfuehrung.kommando_ausfuehrung", fromlist=["ExternesKommandoAntwort"]
        ).ExternesKommandoAntwort(rohdaten="X"),
    )
    assert p2.ausfuehren(ExternesKommandoAnfrage(kommandocode="ANDERS")).rohdaten == ""


def test_com_mode_ignoriert_demo_defaults(monkeypatch):
    monkeypatch.setattr("api.kommando_wiring._ensure_pyserial_available", lambda: None)
    settings = KommandoAdapterSettings(
        adapter="com",
        seriell_port="/dev/ttyUSB0",
        seriell_baudrate=9600,
        seriell_timeout_ms=3000,
        demo_mode=True,
    )
    port = create_kommando_port(settings)
    assert isinstance(port, ComExternesKommandoPort)


def test_ungueltiger_demo_mode_wirft(monkeypatch):
    monkeypatch.setenv("PWE_DEMO_MODE", "vielleicht")
    with pytest.raises(KommandoAdapterConfigurationError, match="PWE_DEMO_MODE"):
        KommandoAdapterSettings.from_env()


def test_configure_caches_demo_mode(monkeypatch):
    monkeypatch.setenv("PWE_DEMO_MODE", "1")
    monkeypatch.setenv("EXTERNES_KOMMANDO_ADAPTER", "simulation")
    configure_kommando_adapter(KommandoAdapterSettings.from_env())
    port = create_kommando_port()
    antwort = port.ausfuehren(ExternesKommandoAnfrage(kommandocode=DEMO_KOMMANDOCODE))
    assert antwort.extrahierte_werte["messwert"] == DEMO_MESSWERT_WERT
