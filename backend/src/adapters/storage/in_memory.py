"""In-Memory-Implementierung von DateiSpeicherPort — Tests und Dev."""

from __future__ import annotations

from ports.datei_speicher_port import DateiBereitsVorhanden, DateiSpeicherZugriffFehler, validiere_datei_id


class InMemoryDateiSpeicher:
    def __init__(self) -> None:
        self._dateien: dict[str, tuple[bytes, str]] = {}

    def speichern(self, datei_id: str, inhalt: bytes, mime_type: str) -> None:
        validiere_datei_id(datei_id)
        if datei_id in self._dateien:
            raise DateiBereitsVorhanden(datei_id)
        self._dateien[datei_id] = (inhalt, mime_type)

    def lesen(self, datei_id: str) -> tuple[bytes, str]:
        validiere_datei_id(datei_id)
        try:
            return self._dateien[datei_id]
        except KeyError as exc:
            raise DateiSpeicherZugriffFehler(datei_id) from exc

    def loeschen(self, datei_id: str) -> None:
        validiere_datei_id(datei_id)
        self._dateien.pop(datei_id, None)
