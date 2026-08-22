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


class MaterialisierteAutomatisierungInkonsistent(DomainError):
    pass


class LeereRoutine(DomainError):
    pass


class UngueltigeAktionsreihenfolge(DomainError):
    pass


class KommandoInVerwendung(DomainError):
    pass


class RoutineInVerwendung(DomainError):
    pass


class VorlageNichtGefunden(DomainError):
    pass


class VorlageInVerwendung(DomainError):
    pass


class SchrittIdBereitsVorhanden(DomainError):
    pass


class UngueltigeSchrittReihenfolge(DomainError):
    pass
