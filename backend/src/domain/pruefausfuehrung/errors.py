"""Prüfausführung — fachliche Fehler."""

from __future__ import annotations

from domain.shared.errors import DomainError


class PrueflaufNichtGefunden(DomainError):
    pass


class VersionNichtGefunden(DomainError):
    pass


class MaterialisierterProzedurSchrittNichtGefunden(DomainError):
    pass


class KommandoNichtFreigegeben(DomainError):
    pass


class ExternesKommandoAdapterFehler(DomainError):
    pass
