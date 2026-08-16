"""Fachliche Beobachtbarkeit — Automatisierungsausführung (Gate 7.4c, ADR-0016).

Leitet Beobachtungen ausschließlich aus bereits vorhandenen Ergebnissen bzw.
bestehenden HTTP-Fehlerabbildungen ab. Keine Fachlogik, keine Infrastruktur-Metriken.
"""

from __future__ import annotations

import logging

from api.fehler import domain_error_code, http_status_for_domain_error
from application.pruefausfuehrung.routine_ausfuehren import RoutineAusfuehrungErgebnis
from domain.shared.errors import DomainError

logger = logging.getLogger("pwe.automatisierung.beobachtung")

EVENT_AUSGEFUEHRT = "automatisierung_ausgefuehrt"
EVENT_NICHT_BEGONNEN = "automatisierung_nicht_begonnen"


def beobachte_ausgefuehrte_automatisierung(
    ergebnis: RoutineAusfuehrungErgebnis,
    *,
    prueflauf_id: str,
    schritt_id: str,
) -> None:
    """Beobachtung nach begonnener Ausführung (HTTP 200-Pfad).

    HTTP 200 ≠ fachlicher Erfolg — `fehlgeschlagen` ist die fachliche Kennzahl.
    """
    fehlerart = ergebnis.fehlerart.value if ergebnis.fehlerart is not None else None
    logger.info(
        "%s prueflauf_id=%s schritt_id=%s ausfuehrung_id=%s http_status=200 "
        "ausfuehrung_begonnen=true fehlgeschlagen=%s fachlicher_erfolg=%s "
        "ausgefuehrte_aktionen=%s abgebrochen_bei_aktion_position=%s fehlerart=%s "
        "nachweis_anzahl=%s",
        EVENT_AUSGEFUEHRT,
        prueflauf_id,
        schritt_id,
        ergebnis.ausfuehrung_id,
        ergebnis.fehlgeschlagen,
        not ergebnis.fehlgeschlagen,
        ergebnis.ausgefuehrte_aktionen,
        ergebnis.abgebrochen_bei_aktion_position,
        fehlerart if fehlerart is not None else "-",
        len(ergebnis.nachweise),
    )


def beobachte_automatisierung_nicht_begonnen(
    exc: DomainError,
    *,
    prueflauf_id: str,
    schritt_id: str,
) -> None:
    """Beobachtung bei Fehler vor Ausführungsbeginn (HTTP 404/409/…)."""
    status = http_status_for_domain_error(exc)
    code = domain_error_code(exc)
    logger.info(
        "%s prueflauf_id=%s schritt_id=%s http_status=%s code=%s "
        "ausfuehrung_begonnen=false fehlgeschlagen=- fachlicher_erfolg=false",
        EVENT_NICHT_BEGONNEN,
        prueflauf_id,
        schritt_id,
        status,
        code,
    )
