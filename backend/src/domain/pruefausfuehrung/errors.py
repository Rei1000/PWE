"""Prüfausführung — fachliche Fehler."""

from __future__ import annotations

from domain.shared.errors import DomainError


class PrueflaufNichtGefunden(DomainError):
    pass


class VersionNichtGefunden(DomainError):
    pass


class MaterialisierterProzedurSchrittNichtGefunden(DomainError):
    pass


class KeineAutomatisierungAmSchritt(DomainError):
    pass


class FotoNurPerMultipart(DomainError):
    pass


class UngueltigerDateityp(DomainError):
    pass


class DateiZuGross(DomainError):
    pass


class DateiNichtGefunden(DomainError):
    pass


class DateiSpeicherungFehlgeschlagen(DomainError):
    pass


class NachweisNichtGefunden(DomainError):
    pass


class NachweisKeinFoto(DomainError):
    pass


class PrueflaufNichtEigentuemer(DomainError):
    """Aktueller Benutzer ist nicht der Prüfer des Prüflaufs."""
