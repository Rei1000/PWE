"""Domain-Tests — Benutzer (Gate 8.1a)."""

import pytest

from domain.identity.benutzer import Benutzer, LoginNichtErlaubt, PasswortHash
from domain.identity.typen import BenutzerStatus, Systemrolle
from domain.shared.errors import InvariantViolation


def _hash() -> PasswortHash:
    return PasswortHash("argon2-dummy-hash")


def test_benutzer_anlegen_aktiv_mit_rollen():
    b = Benutzer.anlegen(
        login="admin",
        anzeigename="Admin",
        passwort_hash=_hash(),
        rollen=frozenset({Systemrolle.ADMINISTRATOR, Systemrolle.PRUEFER}),
        status=BenutzerStatus.AKTIV,
    )
    assert b.login == "admin"
    assert Systemrolle.ADMINISTRATOR in b.rollen
    assert Systemrolle.PRUEFER in b.rollen
    b.assert_login_erlaubt()


def test_login_nur_aktiv():
    b = Benutzer.anlegen(
        login="x",
        anzeigename="X",
        passwort_hash=_hash(),
        rollen=frozenset({Systemrolle.PRUEFER}),
        status=BenutzerStatus.GESPERRT,
    )
    with pytest.raises(LoginNichtErlaubt):
        b.assert_login_erlaubt()


@pytest.mark.parametrize(
    "status",
    [BenutzerStatus.NEU, BenutzerStatus.GESPERRT, BenutzerStatus.ARCHIVIERT],
)
def test_login_blockiert_fuer_nicht_aktiv(status: BenutzerStatus):
    b = Benutzer.anlegen(
        login="x",
        anzeigename="X",
        passwort_hash=_hash(),
        rollen=frozenset({Systemrolle.PRUEFER}),
        status=status,
    )
    with pytest.raises(LoginNichtErlaubt):
        b.assert_login_erlaubt()


def test_leerer_login_verboten():
    with pytest.raises(InvariantViolation):
        Benutzer.anlegen(
            login="  ",
            anzeigename="X",
            passwort_hash=_hash(),
            rollen=frozenset({Systemrolle.PRUEFER}),
        )


def test_passwort_hash_nicht_leer():
    with pytest.raises(InvariantViolation):
        PasswortHash("  ")


def test_benutzer_id_nicht_leer():
    from domain.identity.benutzer_id import BenutzerId

    with pytest.raises(InvariantViolation):
        BenutzerId("  ")
