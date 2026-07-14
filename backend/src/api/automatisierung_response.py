"""Mapping Application → HTTP für Automatisierungsausführung (Gate 7.3f)."""

from __future__ import annotations

from api.schemas import AutomatisierungAusfuehrenResponse, AutomatisierungFehlerartEnum, NachweisResponse
from application.pruefausfuehrung.routine_ausfuehren import RoutineAusfuehrungErgebnis


def automatisierung_ausfuehren_response(
    ergebnis: RoutineAusfuehrungErgebnis,
) -> AutomatisierungAusfuehrenResponse:
    fehlerart = (
        AutomatisierungFehlerartEnum(ergebnis.fehlerart.value)
        if ergebnis.fehlerart is not None
        else None
    )
    return AutomatisierungAusfuehrenResponse(
        ausfuehrung_id=ergebnis.ausfuehrung_id,
        fehlgeschlagen=ergebnis.fehlgeschlagen,
        ausgefuehrte_aktionen=ergebnis.ausgefuehrte_aktionen,
        abgebrochen_bei_aktion_position=ergebnis.abgebrochen_bei_aktion_position,
        fehlerart=fehlerart,
        nachweise=[
            NachweisResponse(nachweis_id=n.nachweis_id, art=n.art.value)
            for n in ergebnis.nachweise
        ],
    )
