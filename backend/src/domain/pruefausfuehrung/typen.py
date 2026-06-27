"""Prüfausführung — gemeinsame Typen (keine Aggregate-Abhängigkeiten)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class PrueflaufStatus(str, Enum):
    GESTARTET = "gestartet"
    IN_BEARBEITUNG = "in_bearbeitung"
    ABGESCHLOSSEN_GUELTIG = "abgeschlossen_gueltig"
    ABGESCHLOSSEN_UNGUELTIG = "abgeschlossen_ungueltig"


class NachweisArt(str, Enum):
    MESSWERT = "messwert"
    FOTO = "foto"
    KOMMENTAR = "kommentar"
    MANUELLE_EINGABE = "manuelle_eingabe"
    ROHANTWORT = "rohantwort"
    EXTRAHIERTER_WERT = "extrahierter_wert"
    ERGAENZUNG = "ergaenzung"
    KOMPONENTENERFASSUNG = "komponentenerfassung"


class BeurteilungErgebnis(str, Enum):
    BESTANDEN = "bestanden"
    NICHT_BESTANDEN = "nicht_bestanden"
    BESTANDEN_MIT_KOMMENTAR = "bestanden_mit_kommentar"


@dataclass(frozen=True)
class Nachweis:
    nachweis_id: str
    art: NachweisArt
    erfasst_am: datetime
    payload: dict[str, Any]
    bezug_nachweis_id: str | None = None
    ist_automatisch: bool = False


@dataclass
class Beurteilung:
    ergebnis: BeurteilungErgebnis
    festgelegt_am: datetime
    kommentar: str | None = None
