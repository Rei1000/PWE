"""Identity — Aggregate Benutzer (Gate 8.1a/8.1c1, ADR-0023/0024)."""

from __future__ import annotations

from dataclasses import dataclass, replace
from uuid import uuid4

from domain.identity.benutzer_id import BenutzerId
from domain.identity.typen import BenutzerStatus, Systemrolle
from domain.shared.errors import DomainError, InvariantViolation


class LoginNichtErlaubt(DomainError):
    """Benutzer darf sich nicht anmelden (Status nicht aktiv)."""


class UngueltigerStatusuebergang(DomainError):
    """Statusübergang ist fachlich nicht erlaubt."""


class PasswortWechselErforderlich(DomainError):
    """Benutzer muss zuerst das Passwort ändern."""


@dataclass(frozen=True)
class PasswortHash:
    """Opaque Passwort-Hash — niemals Klartext."""

    wert: str

    def __post_init__(self) -> None:
        if not self.wert.strip():
            raise InvariantViolation("PasswortHash darf nicht leer sein")


_ERLAUBTE_UEBERGAENGE: frozenset[tuple[BenutzerStatus, BenutzerStatus]] = frozenset(
    {
        (BenutzerStatus.NEU, BenutzerStatus.AKTIV),
        (BenutzerStatus.AKTIV, BenutzerStatus.GESPERRT),
        (BenutzerStatus.GESPERRT, BenutzerStatus.AKTIV),
        (BenutzerStatus.AKTIV, BenutzerStatus.ARCHIVIERT),
        (BenutzerStatus.GESPERRT, BenutzerStatus.ARCHIVIERT),
        (BenutzerStatus.NEU, BenutzerStatus.ARCHIVIERT),
        (BenutzerStatus.ARCHIVIERT, BenutzerStatus.AKTIV),
    }
)


@dataclass(frozen=True)
class Benutzer:
    """Aggregate Root — Identity."""

    benutzer_id: str
    login: str
    anzeigename: str
    status: BenutzerStatus
    rollen: frozenset[Systemrolle]
    passwort_hash: PasswortHash
    passwortwechsel_erforderlich: bool = False

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
        passwortwechsel_erforderlich: bool = False,
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
            passwortwechsel_erforderlich=passwortwechsel_erforderlich,
        )

    def assert_login_erlaubt(self) -> None:
        if self.status != BenutzerStatus.AKTIV:
            raise LoginNichtErlaubt("Anmeldung nur für aktive Benutzer")

    def mit_status(self, neuer_status: BenutzerStatus) -> Benutzer:
        if self.status == neuer_status:
            return self
        if (self.status, neuer_status) not in _ERLAUBTE_UEBERGAENGE:
            raise UngueltigerStatusuebergang(
                f"Übergang {self.status.value} → {neuer_status.value} ist nicht erlaubt"
            )
        return replace(self, status=neuer_status)

    def aktivieren(self) -> Benutzer:
        return self.mit_status(BenutzerStatus.AKTIV)

    def sperren(self) -> Benutzer:
        return self.mit_status(BenutzerStatus.GESPERRT)

    def entsperren(self) -> Benutzer:
        if self.status != BenutzerStatus.GESPERRT:
            raise UngueltigerStatusuebergang("Nur gesperrte Benutzer können entsperrt werden")
        return self.mit_status(BenutzerStatus.AKTIV)

    def archivieren(self) -> Benutzer:
        return self.mit_status(BenutzerStatus.ARCHIVIERT)

    def wiederherstellen(self) -> Benutzer:
        if self.status != BenutzerStatus.ARCHIVIERT:
            raise UngueltigerStatusuebergang(
                "Nur archivierte Benutzer können wiederhergestellt werden"
            )
        return self.mit_status(BenutzerStatus.AKTIV)

    def mit_rollen(self, rollen: frozenset[Systemrolle] | set[Systemrolle]) -> Benutzer:
        neue = frozenset(rollen)
        if not neue:
            raise InvariantViolation("Mindestens eine Systemrolle erforderlich")
        return replace(self, rollen=neue)

    def mit_passwort(
        self,
        passwort_hash: PasswortHash,
        *,
        passwortwechsel_erforderlich: bool,
    ) -> Benutzer:
        return replace(
            self,
            passwort_hash=passwort_hash,
            passwortwechsel_erforderlich=passwortwechsel_erforderlich,
        )

    def ist_aktiver_administrator(self) -> bool:
        return (
            self.status == BenutzerStatus.AKTIV
            and Systemrolle.ADMINISTRATOR in self.rollen
        )
