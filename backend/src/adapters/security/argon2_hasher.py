"""Argon2id Passwort-Hasher (ADR-0024)."""

from __future__ import annotations

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from domain.identity.benutzer import PasswortHash


class Argon2PasswortHasher:
    def __init__(self) -> None:
        self._ph = PasswordHasher()

    def hash(self, klartext: str) -> PasswortHash:
        return PasswortHash(self._ph.hash(klartext))

    def verifizieren(self, klartext: str, passwort_hash: PasswortHash) -> bool:
        try:
            return self._ph.verify(passwort_hash.wert, klartext)
        except VerifyMismatchError:
            return False
