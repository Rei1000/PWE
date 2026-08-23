"""Domain-Tests — Profil aktiv/inaktiv (Gate 8.1c1)."""

from domain.identity.berechtigungsprofil import Berechtigungsprofil
from domain.identity.identity_audit import IdentityAuditEintrag
from domain.identity.start_qualifikation import (
    QualifikationUnzureichend,
    StartQualifikationKontext,
    start_qualifikation_erlaubt,
)
from domain.identity.benutzer import Benutzer, PasswortHash
from domain.identity.einweisungsnachweis import Einweisungsnachweis
from domain.identity.typen import BenutzerStatus, Systemrolle
import pytest


def test_profil_deaktivieren_deckt_nicht_mehr():
    p = Berechtigungsprofil.anlegen(bezeichnung="L", produktdefinition_ids={"pd-1"})
    assert p.deckt_produktdefinition("pd-1")
    inaktiv = p.deaktivieren()
    assert inaktiv.aktiv is False
    assert not inaktiv.deckt_produktdefinition("pd-1")
    assert inaktiv.aktivieren().deckt_produktdefinition("pd-1")


def test_startregel_ignoriert_inaktives_profil():
    benutzer = Benutzer.anlegen(
        login="p",
        anzeigename="P",
        passwort_hash=PasswortHash("h"),
        rollen=frozenset({Systemrolle.PRUEFER}),
        status=BenutzerStatus.AKTIV,
    )
    profil = Berechtigungsprofil.anlegen(
        bezeichnung="L", produktdefinition_ids={"pd-1"}
    ).deaktivieren()
    einweisung = Einweisungsnachweis.anlegen(
        benutzer_id=benutzer.benutzer_id,
        version_id="v1",
        eingewiesen_durch="admin",
    )
    with pytest.raises(QualifikationUnzureichend):
        start_qualifikation_erlaubt(
            StartQualifikationKontext(
                benutzer=benutzer,
                produktdefinition_id="pd-1",
                version_id="v1",
                version_ist_aktive_veroeffentlichte=True,
                profile_des_benutzers=(profil,),
                gueltige_einweisung=einweisung,
            )
        )


def test_audit_entfernt_passwort_keys():
    e = IdentityAuditEintrag.erzeugen(
        akteur_benutzer_id="a1",
        aktion="passwort_reset",
        details={"passwort": "secret", "vorher": {"status": "aktiv"}},
    )
    assert "passwort" not in e.details
    assert e.details["vorher"]["status"] == "aktiv"
