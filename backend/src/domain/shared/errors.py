"""Gemeinsame Domain-Fehler."""

from __future__ import annotations


class DomainError(Exception):
    """Basisklasse für fachliche Regelverletzungen."""


class InvariantViolation(DomainError):
    """Aggregate-Invariante verletzt."""


class UnveraenderlichesObjektBereitsVorhanden(InvariantViolation):
    """Insert-only-Regel: unveränderliches Objekt existiert bereits."""
