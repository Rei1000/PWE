"""Katalog — fachliche Fehler."""

from __future__ import annotations

from domain.shared.errors import DomainError


class EntwurfNichtGefunden(DomainError):
    pass


class ProzedurSchrittNichtGefunden(DomainError):
    pass


class ExternesKommandoNichtGefunden(DomainError):
    pass


class RoutineNichtGefunden(DomainError):
    pass


class KommandoInRoutineNichtGefunden(DomainError):
    pass


class AutomatisierungDoppeltZugewiesen(DomainError):
    pass


class LeereRoutine(DomainError):
    pass


class UngueltigeAktionsreihenfolge(DomainError):
    pass
