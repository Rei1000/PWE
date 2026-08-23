"""Domain-Tests — Benutzer-Lifecycle und Passwort-Flag (Gate 8.1c1)."""

import pytest

from domain.identity.benutzer import (
    Benutzer,
    LoginNichtErlaubt,
    PasswortHash,
    UngueltigerStatusuebergang,
)
from domain.identity.letzter_administrator import (
    LetzterAdministratorVerletzt,
    assert_mutation_behaelt_aktiven_administrator,
)
from domain.identity.typen import BenutzerStatus, Systemrolle
from domain.shared.errors import InvariantViolation


def _hash() -> PasswortHash:
    return PasswortHash("argon2-dummy-hash")


def _admin(**kwargs) -> Benutzer:
    defaults = dict(
        login="admin",
        anzeigename="Admin",
        passwort_hash=_hash(),
        rollen=frozenset({Systemrolle.ADMINISTRATOR}),
        status=BenutzerStatus.AKTIV,
        passwortwechsel_erforderlich=False,
    )
    defaults.update(kwargs)
    return Benutzer.anlegen(**defaults)


def _pruefer(login: str = "p1", **kwargs) -> Benutzer:
    defaults = dict(
        login=login,
        anzeigename="Prüfer",
        passwort_hash=_hash(),
        rollen=frozenset({Systemrolle.PRUEFER}),
        status=BenutzerStatus.NEU,
        passwortwechsel_erforderlich=True,
    )
    defaults.update(kwargs)
    return Benutzer.anlegen(**defaults)


def test_anlegen_default_status_neu_mit_force_change():
    b = _pruefer()
    assert b.status == BenutzerStatus.NEU
    assert b.passwortwechsel_erforderlich is True
    with pytest.raises(LoginNichtErlaubt):
        b.assert_login_erlaubt()


def test_statusmaschine_erlaubte_uebergaenge():
    b = _pruefer()
    aktiv = b.aktivieren()
    assert aktiv.status == BenutzerStatus.AKTIV
    gesperrt = aktiv.sperren()
    assert gesperrt.status == BenutzerStatus.GESPERRT
    assert gesperrt.entsperren().status == BenutzerStatus.AKTIV
    assert aktiv.archivieren().status == BenutzerStatus.ARCHIVIERT
    assert gesperrt.archivieren().status == BenutzerStatus.ARCHIVIERT
    assert b.archivieren().status == BenutzerStatus.ARCHIVIERT
    archiv = aktiv.archivieren()
    assert archiv.wiederherstellen().status == BenutzerStatus.AKTIV


def test_archiviert_nach_gesperrt_verboten():
    archiv = _pruefer(status=BenutzerStatus.AKTIV).archivieren()
    with pytest.raises(UngueltigerStatusuebergang):
        archiv.sperren()


def test_rollen_setzen_mindestens_eine():
    b = _admin()
    with pytest.raises(InvariantViolation):
        b.mit_rollen(frozenset())


def test_letzter_admin_sperren_verboten():
    admin = _admin(benutzer_id="a1")
    with pytest.raises(LetzterAdministratorVerletzt):
        assert_mutation_behaelt_aktiven_administrator(
            alle_benutzer=[admin], geaenderter=admin.sperren()
        )


def test_zwei_admins_einer_darf_gesperrt_werden():
    a1 = _admin(login="a1", benutzer_id="a1")
    a2 = _admin(login="a2", benutzer_id="a2")
    assert_mutation_behaelt_aktiven_administrator(
        alle_benutzer=[a1, a2], geaenderter=a1.sperren()
    )


def test_letzte_admin_rolle_entfernen_verboten():
    admin = _admin(benutzer_id="a1")
    geaendert = admin.mit_rollen(frozenset({Systemrolle.PRUEFER}))
    with pytest.raises(LetzterAdministratorVerletzt):
        assert_mutation_behaelt_aktiven_administrator(
            alle_benutzer=[admin], geaenderter=geaendert
        )


def test_passwort_mit_force_change_flag():
    b = _pruefer(status=BenutzerStatus.AKTIV)
    neu = b.mit_passwort(_hash(), passwortwechsel_erforderlich=False)
    assert neu.passwortwechsel_erforderlich is False
