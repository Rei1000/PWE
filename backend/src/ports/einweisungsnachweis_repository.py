"""Port — Einweisungsnachweis-Persistenz (Gate 8.1b)."""

from __future__ import annotations

from typing import Protocol

from domain.identity.einweisungsnachweis import Einweisungsnachweis


class EinweisungsnachweisRepository(Protocol):
    def save(self, einweisung: Einweisungsnachweis) -> None: ...

    def get(self, einweisung_id: str) -> Einweisungsnachweis | None: ...

    def get_gueltige(
        self, *, benutzer_id: str, version_id: str
    ) -> Einweisungsnachweis | None: ...

    def list_gueltige_fuer_version(self, version_id: str) -> list[Einweisungsnachweis]: ...

    def list_fuer_benutzer_version(
        self, *, benutzer_id: str, version_id: str
    ) -> list[Einweisungsnachweis]: ...
