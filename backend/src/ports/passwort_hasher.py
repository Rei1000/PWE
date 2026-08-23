"""Port — Passwort hashen/verifizieren (Identity-Adapter)."""

from __future__ import annotations

from typing import Protocol

from domain.identity.benutzer import PasswortHash


class PasswortHasher(Protocol):
    def hash(self, klartext: str) -> PasswortHash: ...

    def verifizieren(self, klartext: str, passwort_hash: PasswortHash) -> bool: ...
