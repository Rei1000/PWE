"""Adapter — CurrentUser aus FastAPI request.state (nach Auth-Middleware)."""

from __future__ import annotations

from fastapi import Request

from domain.identity.benutzer import Benutzer
from domain.shared.errors import DomainError


class NichtAuthentifiziertError(DomainError):
    """Kein aktueller Benutzer im Request-Kontext."""


class RequestCurrentUserProvider:
    """Liest `request.state.aktueller_benutzer` — gesetzt durch Session-Middleware."""

    def __init__(self, request: Request) -> None:
        self._request = request

    def require(self) -> Benutzer:
        benutzer = getattr(self._request.state, "aktueller_benutzer", None)
        if benutzer is None:
            raise NichtAuthentifiziertError("Nicht angemeldet")
        return benutzer
