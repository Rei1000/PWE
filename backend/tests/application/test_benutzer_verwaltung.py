"""Application-Tests — Benutzerverwaltung (Gate 8.1c1)."""

from __future__ import annotations

import pytest

from adapters.persistence.in_memory_identity import (
    InMemoryBenutzerRepository,
    InMemoryIdentityAuditRepository,
    InMemorySessionStore,
)
from adapters.security.argon2_hasher import Argon2PasswortHasher
from application.identity.benutzer_verwaltung import (
    BenutzerAktivieren,
    BenutzerAnlegen,
    BenutzerSperren,
    BenutzerRollenSetzen,
)
from application.identity.passwort_verwaltung import PasswortAendern, PasswortZuruecksetzen
from domain.identity.benutzer import Benutzer
from domain.identity.letzter_administrator import LetzterAdministratorVerletzt
from domain.identity.typen import BenutzerStatus, Systemrolle
from ports.session_store import SessionDaten
from datetime import UTC, datetime


def _repos():
    return (
        InMemoryBenutzerRepository(),
        Argon2PasswortHasher(),
        InMemorySessionStore(),
        InMemoryIdentityAuditRepository(),
    )


def test_anlegen_aktivieren_sperren_audit():
    benutzer, hasher, sessions, audit = _repos()
    admin = Benutzer.anlegen(
        login="admin",
        anzeigename="A",
        passwort_hash=hasher.hash("x"),
        rollen=frozenset({Systemrolle.ADMINISTRATOR}),
        status=BenutzerStatus.AKTIV,
        benutzer_id="admin-1",
    )
    benutzer.save(admin)
    neu = BenutzerAnlegen(benutzer, hasher, audit).execute(
        akteur_id="admin-1",
        login="p1",
        anzeigename="P",
        passwort_klartext="geheim",
        rollen={Systemrolle.PRUEFER},
    )
    assert neu.status == BenutzerStatus.NEU
    aktiv = BenutzerAktivieren(benutzer, sessions, audit).execute(
        akteur_id="admin-1", benutzer_id=neu.benutzer_id
    )
    assert aktiv.status == BenutzerStatus.AKTIV
    aktionen = {e.aktion for e in audit.list_all()}
    assert "benutzer_angelegt" in aktionen
    assert "benutzer_aktiviert" in aktionen


def test_letzter_admin_sperren_application():
    benutzer, hasher, sessions, audit = _repos()
    admin = Benutzer.anlegen(
        login="admin",
        anzeigename="A",
        passwort_hash=hasher.hash("x"),
        rollen=frozenset({Systemrolle.ADMINISTRATOR}),
        status=BenutzerStatus.AKTIV,
        benutzer_id="admin-1",
    )
    benutzer.save(admin)
    with pytest.raises(LetzterAdministratorVerletzt):
        BenutzerSperren(benutzer, sessions, audit).execute(
            akteur_id="admin-1", benutzer_id="admin-1"
        )


def test_passwort_reset_invalidiert_sessions():
    benutzer, hasher, sessions, audit = _repos()
    u = Benutzer.anlegen(
        login="u1",
        anzeigename="U",
        passwort_hash=hasher.hash("alt"),
        rollen=frozenset({Systemrolle.PRUEFER}),
        status=BenutzerStatus.AKTIV,
        benutzer_id="u1",
    )
    benutzer.save(u)
    now = datetime.now(UTC)
    sessions.speichern(
        SessionDaten(
            session_id="s1",
            benutzer_id="u1",
            csrf_token="c",
            erzeugt_am=now,
            zuletzt_gesehen_am=now,
        )
    )
    PasswortZuruecksetzen(benutzer, hasher, sessions, audit).execute(
        akteur_id="admin", benutzer_id="u1", neues_passwort="neu"
    )
    assert sessions.laden("s1") is None
    assert benutzer.get("u1").passwortwechsel_erforderlich is True


def test_self_passwort_aendern():
    benutzer, hasher, sessions, audit = _repos()
    u = Benutzer.anlegen(
        login="u1",
        anzeigename="U",
        passwort_hash=hasher.hash("alt"),
        rollen=frozenset({Systemrolle.PRUEFER}),
        status=BenutzerStatus.AKTIV,
        benutzer_id="u1",
        passwortwechsel_erforderlich=True,
    )
    benutzer.save(u)
    PasswortAendern(benutzer, hasher, sessions, audit).execute(
        benutzer_id="u1", altes_passwort="alt", neues_passwort="neu"
    )
    assert benutzer.get("u1").passwortwechsel_erforderlich is False


def test_rollen_setzen_behaelt_zweiten_admin():
    benutzer, hasher, sessions, audit = _repos()
    for login, bid in (("a1", "a1"), ("a2", "a2")):
        benutzer.save(
            Benutzer.anlegen(
                login=login,
                anzeigename=login,
                passwort_hash=hasher.hash("x"),
                rollen=frozenset({Systemrolle.ADMINISTRATOR}),
                status=BenutzerStatus.AKTIV,
                benutzer_id=bid,
            )
        )
    BenutzerRollenSetzen(benutzer, audit).execute(
        akteur_id="a1",
        benutzer_id="a1",
        rollen={Systemrolle.PRUEFER},
    )
    assert Systemrolle.ADMINISTRATOR not in benutzer.get("a1").rollen
