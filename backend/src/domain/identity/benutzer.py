"""Identity — Aggregate Benutzer (Gate 8.1a, ADR-0023)."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from domain.identity.benutzer_id import BenutzerId
from domain.identity.typen import BenutzerStatus, Systemrolle
from domain.shared.errors import DomainError, InvariantViolation


class LoginNichtErlaubt(DomainError):
    """Benutzer darf sich nicht anmelden (Status nicht aktiv)."""


@dataclass(frozen=True)
class PasswortHash:
    """Opaque Passwort-Hash — niemals Klartext."""

    wert: str

    def __post_init__(self) -> None:
        if not self.wert.strip():
            raise InvariantViolation("PasswortHash darf nicht leer sein")


@dataclass(frozen=True)
class Benutzer:
    """Aggregate Root — Identity."""

    benutzer_id: str
    login: str
    anzeigename: str
    status: BenutzerStatus
    rollen: frozenset[Systemrolle]
    passwort_hash: PasswortHash

    @classmethod
    def anlegen(
        cls,
        *,
        login: str,
        anzeigename: str,
        passwort_hash: PasswortHash,
        rollen: frozenset[Systemrolle],
        status: BenutzerStatus = BenutzerStatus.NEU,
        benutzer_id: str | None = None,
    ) -> Benutzer:
        login_n = login.strip()
        name_n = anzeigename.strip()
        if not login_n:
            raise InvariantViolation("Login darf nicht leer sein")
        if not name_n:
            raise InvariantViolation("Anzeigename darf nicht leer sein")
        if not rollen:
            raise InvariantViolation("Mindestens eine Systemrolle erforderlich")
        id_wert = BenutzerId(benutzer_id or str(uuid4())).wert
        return cls(
            benutzer_id=id_wert,
            login=login_n,
            anzeigename=name_n,
            status=status,
            rollen=frozenset(rollen),
            passwort_hash=passwort_hash,
        )

    def assert_login_erlaubt(self) -> None:
        if self.status != BenutzerStatus.AKTIV:
            raise LoginNichtErlaubt("Anmeldung nur für aktive Benutzer")
