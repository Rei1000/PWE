"""Protokoll — erzeugtes Ausgabedokument (Domain-sprachlich, formatneutral)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProtokollDokument:
    """Ergebnis der Protokollerzeugung — Medientyp wird vom Adapter gesetzt."""

    inhalt: bytes
    medientyp: str
    dateiname: str
