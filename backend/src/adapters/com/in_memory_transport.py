"""In-Memory-Transport für COM-Adapter-Tests."""

from __future__ import annotations


class InMemorySeriellerTransport:
    """Simuliert serielle Gegenstelle ohne Hardware."""

    def __init__(self, antworten: dict[str, bytes] | None = None) -> None:
        self._antworten: dict[str, bytes] = dict(antworten or {})

    def registriere_antwort(self, kommandocode: str, antwort: bytes) -> None:
        self._antworten[kommandocode] = antwort

    def send_and_receive(self, payload: bytes) -> bytes:
        kommandocode = payload.decode("utf-8").strip()
        return self._antworten.get(kommandocode, b"ERR UNKNOWN")
