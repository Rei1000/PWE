"""Katalog — fachliche Fehler."""

from __future__ import annotations

from domain.shared.errors import DomainError


class ExternesKommandoNichtGefunden(DomainError):
    pass
