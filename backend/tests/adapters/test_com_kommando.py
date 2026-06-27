"""Tests — COM-Adapter für ExternesKommandoPort."""

from adapters.com.externes_kommando import ComExternesKommandoPort
from adapters.com.in_memory_transport import InMemorySeriellerTransport
from domain.pruefausfuehrung.kommando_ausfuehrung import ExternesKommandoAnfrage


def test_com_adapter_parst_rohdaten_und_extrahiert_werte():
    transport = InMemorySeriellerTransport(
        {"READ_VOLTAGE": b"OK spannung=230"}
    )
    port = ComExternesKommandoPort(transport)

    antwort = port.ausfuehren(ExternesKommandoAnfrage(kommandocode="READ_VOLTAGE"))

    assert antwort.erfolgreich is True
    assert antwort.rohdaten == "OK spannung=230"
    assert antwort.extrahierte_werte["spannung"] == 230


def test_com_adapter_fehlerantwort():
    transport = InMemorySeriellerTransport()
    port = ComExternesKommandoPort(transport)

    antwort = port.ausfuehren(ExternesKommandoAnfrage(kommandocode="UNKNOWN"))

    assert antwort.erfolgreich is False
    assert antwort.extrahierte_werte == {}
