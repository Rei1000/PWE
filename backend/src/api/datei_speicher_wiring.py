"""DateiSpeicher-Wiring und Konfiguration (Gate 8.3a, ADR-0022)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from adapters.storage.in_memory import InMemoryDateiSpeicher
from adapters.storage.lokal import LokalerDateiSpeicher
from ports.datei_speicher_port import DateiSpeicherPort


class DateiSpeicherConfigurationError(RuntimeError):
    pass


@dataclass(frozen=True)
class DateiSpeicherSettings:
    storage_pfad: Path | None

    @classmethod
    def from_env(cls) -> DateiSpeicherSettings:
        raw = os.environ.get("PWE_DATEI_STORAGE_PFAD")
        if raw is None or not raw.strip():
            return cls(storage_pfad=None)
        pfad = Path(raw.strip())
        if not pfad.is_absolute():
            raise DateiSpeicherConfigurationError(
                "PWE_DATEI_STORAGE_PFAD muss ein absoluter Pfad sein."
            )
        return cls(storage_pfad=pfad)


def create_datei_speicher(
    settings: DateiSpeicherSettings | None = None,
    *,
    in_memory: InMemoryDateiSpeicher | None = None,
) -> DateiSpeicherPort:
    if in_memory is not None:
        return in_memory
    resolved = settings or DateiSpeicherSettings.from_env()
    if resolved.storage_pfad is None:
        return InMemoryDateiSpeicher()
    return LokalerDateiSpeicher(resolved.storage_pfad)
