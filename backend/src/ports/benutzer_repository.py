"""Port — Benutzer-Persistenz (Identity)."""

from __future__ import annotations

from typing import Protocol

from domain.identity.benutzer import Benutzer


class BenutzerRepository(Protocol):
    def save(self, benutzer: Benutzer) -> None: ...

    def get(self, benutzer_id: str) -> Benutzer | None: ...

    def get_by_login(self, login: str) -> Benutzer | None: ...

    def list_all(self, *, for_update: bool = False) -> list[Benutzer]: ...
