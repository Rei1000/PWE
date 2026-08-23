"""Port — aktueller Benutzer aus Auth-Kontext (Gate 8.1a)."""

from __future__ import annotations

from typing import Protocol

from domain.identity.benutzer import Benutzer


class CurrentUserProvider(Protocol):
    """Liefert den authentifizierten Benutzer der laufenden Anfrage."""

    def require(self) -> Benutzer: ...
