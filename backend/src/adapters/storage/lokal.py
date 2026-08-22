"""Lokaler Dateisystem-Adapter für DateiSpeicherPort (ADR-0022)."""

from __future__ import annotations

import os
from pathlib import Path

from ports.datei_speicher_port import DateiBereitsVorhanden, DateiSpeicherZugriffFehler, validiere_datei_id


class LokalerDateiSpeicher:
    def __init__(self, storage_root: Path) -> None:
        self._root = storage_root.resolve()

    def _pfad_fuer(self, datei_id: str) -> Path:
        validiere_datei_id(datei_id)
        pfad = (self._root / datei_id).resolve()
        if pfad.parent != self._root:
            raise DateiSpeicherZugriffFehler(datei_id)
        return pfad

    def _mime_pfad_fuer(self, datei_id: str) -> Path:
        return self._pfad_fuer(f"{datei_id}.mime")

    def speichern(self, datei_id: str, inhalt: bytes, mime_type: str) -> None:
        pfad = self._pfad_fuer(datei_id)
        mime_pfad = self._mime_pfad_fuer(datei_id)
        if pfad.exists() or mime_pfad.exists():
            raise DateiBereitsVorhanden(datei_id)
        try:
            self._root.mkdir(parents=True, exist_ok=True)
            fd = os.open(pfad, os.O_WRONLY | os.O_CREAT | os.O_EXCL)
            with os.fdopen(fd, "wb") as handle:
                handle.write(inhalt)
            mime_pfad.write_text(mime_type, encoding="utf-8")
        except FileExistsError as exc:
            raise DateiBereitsVorhanden(datei_id) from exc
        except OSError as exc:
            pfad.unlink(missing_ok=True)
            mime_pfad.unlink(missing_ok=True)
            raise DateiSpeicherZugriffFehler(datei_id) from exc

    def lesen(self, datei_id: str) -> tuple[bytes, str]:
        pfad = self._pfad_fuer(datei_id)
        mime_pfad = self._mime_pfad_fuer(datei_id)
        if not pfad.is_file() or not mime_pfad.is_file():
            raise DateiSpeicherZugriffFehler(datei_id)
        try:
            inhalt = pfad.read_bytes()
            mime_type = mime_pfad.read_text(encoding="utf-8").strip()
        except OSError as exc:
            raise DateiSpeicherZugriffFehler(datei_id) from exc
        return inhalt, mime_type

    def loeschen(self, datei_id: str) -> None:
        pfad = self._pfad_fuer(datei_id)
        mime_pfad = self._mime_pfad_fuer(datei_id)
        try:
            pfad.unlink(missing_ok=True)
            mime_pfad.unlink(missing_ok=True)
        except OSError as exc:
            raise DateiSpeicherZugriffFehler(datei_id) from exc
