"""Interne Transportfehler — nur im COM-Adapter, nicht in Domain/Application."""

from __future__ import annotations


class TransportError(Exception):
    """Basisklasse für serielle Transportfehler."""


class TransportTimeout(TransportError):
    """Gerät hat innerhalb des konfigurierten Timeouts nicht geantwortet."""


class TransportConnectionError(TransportError):
    """Serieller Port konnte nicht geöffnet werden."""


class TransportIOError(TransportError):
    """Fehler beim Senden oder Empfangen über den seriellen Port."""
