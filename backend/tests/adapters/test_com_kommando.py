"""Tests — COM-Adapter für ExternesKommandoPort."""

from adapters.com.errors import TransportIOError, TransportTimeout
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
    assert antwort.rohdaten == "ERR UNKNOWN"
    assert antwort.extrahierte_werte == {}


def test_com_adapter_timeout_liefert_leere_rohdaten():
    transport = InMemorySeriellerTransport()
    transport.registriere_transport_fehler("READ_VOLTAGE", TransportTimeout("timeout"))
    port = ComExternesKommandoPort(transport)

    antwort = port.ausfuehren(ExternesKommandoAnfrage(kommandocode="READ_VOLTAGE"))

    assert antwort.erfolgreich is False
    assert antwort.rohdaten == ""


def test_com_adapter_transportfehler_liefert_leere_rohdaten():
    transport = InMemorySeriellerTransport()
    transport.registriere_transport_fehler("READ_VOLTAGE", TransportIOError("io"))
    port = ComExternesKommandoPort(transport)

    antwort = port.ausfuehren(ExternesKommandoAnfrage(kommandocode="READ_VOLTAGE"))

    assert antwort.erfolgreich is False
    assert antwort.rohdaten == ""


def test_com_adapter_parserfehler_behält_rohdaten():
    transport = InMemorySeriellerTransport({"READ_VOLTAGE": b"OK unparseable"})

    def _failing_extractor(_rohdaten: str) -> dict[str, float | int]:
        raise ValueError("parse failed")

    port = ComExternesKommandoPort(transport, wert_extractor=_failing_extractor)

    antwort = port.ausfuehren(ExternesKommandoAnfrage(kommandocode="READ_VOLTAGE"))

    assert antwort.erfolgreich is False
    assert antwort.rohdaten == "OK unparseable"


def test_com_adapter_fuehrt_keinen_retry_aus():
    calls: list[bytes] = []

    class _CountingTransport:
        def send_and_receive(self, payload: bytes) -> bytes:
            calls.append(payload)
            return b"OK spannung=1"

    port = ComExternesKommandoPort(_CountingTransport())

    port.ausfuehren(ExternesKommandoAnfrage(kommandocode="READ_VOLTAGE"))

    assert len(calls) == 1

