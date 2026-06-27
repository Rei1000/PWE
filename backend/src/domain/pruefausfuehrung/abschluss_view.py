"""Abschluss-View — Published Language für Protokoll-Context (ADR-0008)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from domain.pruefausfuehrung.typen import BeurteilungErgebnis


@dataclass(frozen=True)
class SchrittAbschlussView:
    prozedur_schritt_id: str
    ist_pflicht: bool
    beurteilung: BeurteilungErgebnis | None
    nachweis_ids: tuple[str, ...]


@dataclass(frozen=True)
class PrueflaufAbschlussView:
    prueflauf_id: str
    version_id: str
    pruefobjekt_kennung: str
    produktkodierung: str
    pruefer_id: str
    gestartet_am: datetime
    abgeschlossen_am: datetime
    ist_gueltig: bool
    schritte: tuple[SchrittAbschlussView, ...]
    fehlende_sollbestueckung: tuple[str, ...] = ()
