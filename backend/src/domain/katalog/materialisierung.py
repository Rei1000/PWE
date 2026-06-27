"""Sollvorgaben-Materialisierung bei Veröffentlichung (ADR-0005)."""

from __future__ import annotations

from typing import Any


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
