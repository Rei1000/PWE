"""Port — Binärdateispeicher für Foto-Nachweise (ADR-0022)."""

from __future__ import annotations

from typing import Protocol


class DateiSpeicherFehler(Exception):
    pass


class DateiBereitsVorhanden(DateiSpeicherFehler):
    pass


class DateiSpeicherZugriffFehler(DateiSpeicherFehler):
    pass


def validiere_datei_id(datei_id: str) -> None:
    if not datei_id or datei_id in {".", ".."} or "/" in datei_id or "\\" in datei_id:
        raise DateiSpeicherZugriffFehler(datei_id)


class DateiSpeicherPort(Protocol):
    def speichern(self, datei_id: str, inhalt: bytes, mime_type: str) -> None: ...

    def lesen(self, datei_id: str) -> tuple[bytes, str]: ...

    def loeschen(self, datei_id: str) -> None: ...
