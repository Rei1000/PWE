"""Sollvorgaben- und Automatisierungs-Materialisierung (ADR-0005, ADR-0014)."""

from __future__ import annotations

from typing import Any

from domain.katalog.errors import MaterialisierteAutomatisierungInkonsistent
from domain.katalog.routine import MaterialisierteRoutineHerkunft
from domain.katalog.version import MaterialisierterProzedurSchritt


def materialisiere_sollvorgaben(
    basisprodukt: dict[str, Any],
    kundenprofil: dict[str, Any],
    definition: dict[str, Any],
    schritt: dict[str, Any],
) -> dict[str, Any]:
    """Auflösungskette: Basisprodukt → Kundenprofil → Definition → Schritt."""
    merged: dict[str, Any] = {}
    merged.update(basisprodukt)
    merged.update(kundenprofil)
    merged.update(definition)
    merged.update(schritt)
    return merged


def validiere_materialisierter_schritt_automatisierung(
    schritt: MaterialisierterProzedurSchritt,
) -> None:
    """Kompatibilitätsinvariante zwischen materialisierte_routine und externes_kommando."""
    mr = schritt.materialisierte_routine
    ek = schritt.externes_kommando

    if mr is None and ek is None:
        return

    if mr is None and ek is not None:
        return

    if mr is not None and ek is None:
        return

    if mr.herkunft == MaterialisierteRoutineHerkunft.BIBLIOTHEK:
        raise MaterialisierteAutomatisierungInkonsistent(
            f"ProzedurSchritt {schritt.schritt_id}: externes_kommando darf bei "
            "Bibliotheksroutine nicht gesetzt sein"
        )

    abgeleitet = mr.erstes_kommando_snapshot()
    if abgeleitet is None:
        raise MaterialisierteAutomatisierungInkonsistent(
            f"ProzedurSchritt {schritt.schritt_id}: materialisierte_routine ohne Kommando-Aktion"
        )

    if (
        ek.kommando_id != abgeleitet.kommando_id
        or ek.bezeichnung != abgeleitet.bezeichnung
        or ek.kommandocode != abgeleitet.kommandocode
    ):
        raise MaterialisierteAutomatisierungInkonsistent(
            f"ProzedurSchritt {schritt.schritt_id}: externes_kommando weicht von "
            "materialisierte_routine ab"
        )
