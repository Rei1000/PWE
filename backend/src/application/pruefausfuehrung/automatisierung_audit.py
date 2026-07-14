"""Audit-Korrelation für automatische Kommando-/Routine-Nachweise (ADR-0015)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from domain.katalog.routine import MaterialisierteRoutineHerkunft


@dataclass(frozen=True)
class AutomatisierungAuditKontext:
    ausfuehrung_id: str
    herkunft: MaterialisierteRoutineHerkunft
    aktion_position: int
    kommando_id: str
    routine_id: str | None = None


def automatisierung_payload_abschnitt(audit: AutomatisierungAuditKontext) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "ausfuehrung_id": audit.ausfuehrung_id,
        "herkunft": audit.herkunft.value,
        "aktion_position": audit.aktion_position,
        "kommando_id": audit.kommando_id,
    }
    if audit.routine_id is not None:
        payload["routine_id"] = audit.routine_id
    return payload


def nachweis_payload_mit_audit(
    fachlicher_inhalt: dict[str, Any],
    audit: AutomatisierungAuditKontext,
) -> dict[str, Any]:
    return {
        **fachlicher_inhalt,
        "automatisierung": automatisierung_payload_abschnitt(audit),
    }
