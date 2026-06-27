"""Laufzeit-Vertrag für Externes Kommando — Domänensprache (§4.11).

Technische Übertragung (COM, Simulation, …) bleibt im Adapter.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ExternesKommandoAnfrage:
    """Ausführungsanfrage gegen ein konfiguriertes externes Kommando."""

    kommandocode: str
    parameter: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ExternesKommandoAntwort:
    """Fachliche Antwort — Rohdaten und optional extrahierte Ist-Werte."""

    rohdaten: str
    erfolgreich: bool = True
    extrahierte_werte: dict[str, Any] = field(default_factory=dict)
