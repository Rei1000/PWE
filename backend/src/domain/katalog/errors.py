"""Katalog — fachliche Fehler."""

from __future__ import annotations

from domain.shared.errors import DomainError


class EntwurfNichtGefunden(DomainError):
    pass


class ProzedurSchrittNichtGefunden(DomainError):
    pass


class ExternesKommandoNichtGefunden(DomainError):
    pass
