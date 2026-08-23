"""Domain-Tests — Berechtigungsprofil, Einweisung, StartQualifikation (Gate 8.1b)."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

import pytest

from domain.identity.benutzer import Benutzer, PasswortHash
from domain.identity.berechtigungsprofil import Berechtigungsprofil
from domain.identity.einweisungsnachweis import (
    EinweisungNichtGueltig,
    Einweisungsnachweis,
)
from domain.identity.start_qualifikation import (
    QualifikationUnzureichend,
    StartQualifikationKontext,
    start_qualifikation_erlaubt,
)
from domain.identity.typen import BenutzerStatus, EinweisungsStatus, Systemrolle
from domain.shared.errors import InvariantViolation


def _pruefer(**kwargs) -> Benutzer:
    defaults = dict(
        login="p1",
        anzeigename="Prüfer",
        passwort_hash=PasswortHash("h"),
        rollen=frozenset({Systemrolle.PRUEFER}),
        status=BenutzerStatus.AKTIV,
    )
    defaults.update(kwargs)
    return Benutzer.anlegen(**defaults)


def test_profil_anlegen_trim_und_ids():
    p = Berechtigungsprofil.anlegen(
        bezeichnung="  Linie A  ",
        produktdefinition_ids={" pd-1 ", "", "pd-2"},
    )
    assert p.bezeichnung == "Linie A"
    assert p.produktdefinition_ids == frozenset({"pd-1", "pd-2"})


def test_profil_leere_bezeichnung_verboten():
    with pytest.raises(InvariantViolation):
        Berechtigungsprofil.anlegen(bezeichnung="  ")


def test_einweisung_gueltig_mit_gueltig_bis():
    e = Einweisungsnachweis.anlegen(
        benutzer_id="u1",
        version_id="v1",
        eingewiesen_durch="admin",
        gueltig_bis=date.today() + timedelta(days=1),
    )
    assert e.ist_gueltig()
    e.assert_gueltig()


def test_einweisung_abgelaufen_per_datum():
    e = Einweisungsnachweis.anlegen(
        benutzer_id="u1",
        version_id="v1",
        eingewiesen_durch="admin",
        gueltig_bis=date.today() - timedelta(days=1),
    )
    assert not e.ist_gueltig()
    with pytest.raises(EinweisungNichtGueltig):
        e.assert_gueltig()


def test_einweisung_widerrufen():
    e = Einweisungsnachweis.anlegen(
        benutzer_id="u1", version_id="v1", eingewiesen_durch="admin"
    )
    w = e.widerrufen()
    assert w.status == EinweisungsStatus.WIDERRUFEN
    assert not w.ist_gueltig()


def test_einweisung_uebernehmen_setzt_herkunft():
    alt = Einweisungsnachweis.anlegen(
        benutzer_id="u1",
        version_id="v-alt",
        eingewiesen_durch="qm",
        gueltig_bis=date(2099, 1, 1),
    )
    neu = alt.uebernehmen_auf_version(
        neue_version_id="v-neu",
        eingewiesen_durch="admin",
        datum=datetime(2026, 1, 1, tzinfo=UTC),
    )
    assert neu.version_id == "v-neu"
    assert neu.herkunft_einweisung_id == alt.einweisung_id
    assert neu.uebernommen_bei_publish is True
    assert neu.gueltig_bis == date(2099, 1, 1)
    assert "v-alt" in (neu.bemerkung or "")


def _ctx(**overrides) -> StartQualifikationKontext:
    benutzer = _pruefer()
    profil = Berechtigungsprofil.anlegen(
        bezeichnung="P", produktdefinition_ids={"pd-1"}
    )
    einweisung = Einweisungsnachweis.anlegen(
        benutzer_id=benutzer.benutzer_id,
        version_id="ver-1",
        eingewiesen_durch="admin",
    )
    base = dict(
        benutzer=benutzer,
        produktdefinition_id="pd-1",
        version_id="ver-1",
        version_ist_aktive_veroeffentlichte=True,
        profile_des_benutzers=(profil,),
        gueltige_einweisung=einweisung,
    )
    base.update(overrides)
    return StartQualifikationKontext(**base)


def test_start_qualifikation_ok():
    start_qualifikation_erlaubt(_ctx())


def test_start_ohne_einweisung():
    with pytest.raises(QualifikationUnzureichend):
        start_qualifikation_erlaubt(_ctx(gueltige_einweisung=None))


def test_start_ohne_passendes_profil():
    profil = Berechtigungsprofil.anlegen(
        bezeichnung="andere", produktdefinition_ids={"pd-other"}
    )
    with pytest.raises(QualifikationUnzureichend):
        start_qualifikation_erlaubt(_ctx(profile_des_benutzers=(profil,)))


def test_start_ohne_pruefer_rolle():
    admin = _pruefer(rollen=frozenset({Systemrolle.ADMINISTRATOR}))
    with pytest.raises(QualifikationUnzureichend):
        start_qualifikation_erlaubt(_ctx(benutzer=admin, gueltige_einweisung=None))


def test_start_admin_plus_pruefer_ohne_einweisung():
    both = _pruefer(
        rollen=frozenset({Systemrolle.ADMINISTRATOR, Systemrolle.PRUEFER})
    )
    with pytest.raises(QualifikationUnzureichend):
        start_qualifikation_erlaubt(
            _ctx(benutzer=both, gueltige_einweisung=None)
        )


def test_start_zwei_profile_eines_passt():
    p1 = Berechtigungsprofil.anlegen(bezeichnung="A", produktdefinition_ids={"x"})
    p2 = Berechtigungsprofil.anlegen(bezeichnung="B", produktdefinition_ids={"pd-1"})
    start_qualifikation_erlaubt(_ctx(profile_des_benutzers=(p1, p2)))


def test_start_archivierter_benutzer():
    b = _pruefer(status=BenutzerStatus.ARCHIVIERT)
    with pytest.raises(QualifikationUnzureichend):
        start_qualifikation_erlaubt(_ctx(benutzer=b))


def test_start_version_nicht_aktiv():
    with pytest.raises(QualifikationUnzureichend):
        start_qualifikation_erlaubt(_ctx(version_ist_aktive_veroeffentlichte=False))
