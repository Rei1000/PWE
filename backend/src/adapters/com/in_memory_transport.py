"""In-Memory-Transport für COM-Adapter-Tests."""

from __future__ import annotations

from adapters.com.errors import TransportError


class InMemorySeriellerTransport:
    """Simuliert serielle Gegenstelle ohne Hardware."""

    def __init__(self, antworten: dict[str, bytes] | None = None) -> None:
        self._antworten: dict[str, bytes] = dict(antworten or {})
        self._transport_fehler: dict[str, TransportError] = {}

    def registriere_antwort(self, kommandocode: str, antwort: bytes) -> None:
        self._antworten[kommandocode] = antwort

    def registriere_transport_fehler(self, kommandocode: str, fehler: TransportError) -> None:
        self._transport_fehler[kommandocode] = fehler

    def send_and_receive(self, payload: bytes) -> bytes:
        kommandocode = payload.decode("utf-8").strip()
        if kommandocode in self._transport_fehler:
            raise self._transport_fehler[kommandocode]
        return self._antworten.get(kommandocode, b"ERR UNKNOWN")
