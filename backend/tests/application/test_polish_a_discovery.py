"""Application-Tests — V1 Operational Polish A (Discovery Reads)."""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from adapters.persistence.in_memory import (
    InMemoryBibliothekRepository,
    InMemoryKatalogRepository,
    InMemoryPrueflaufRepository,
)
from adapters.persistence.in_memory_identity import (
    InMemoryBenutzerRepository,
    InMemoryBerechtigungsprofilRepository,
    InMemoryEinweisungsnachweisRepository,
)
from application.identity.einweisung_verwaltung import EinweisungAnlegen
from application.identity.profil_verwaltung import ProfilAnlegen, ProfilBenutzerEntfernen, ProfilBenutzerZuordnen
from application.katalog.aktive_produkte_listen import AktiveProdukteListen
from application.katalog.entwurf_anlegen import EntwurfAnlegen
from application.katalog.veroeffentlichen import ProduktdefinitionVeroeffentlichen
from application.pruefausfuehrung.pruefung_starten import PruefungStarten
from application.pruefausfuehrung.startbare_pruefungen_listen import StartbarePruefungenListen
from domain.identity.benutzer import Benutzer, PasswortHash
from domain.identity.berechtigungsprofil import Berechtigungsprofil
from domain.identity.einweisungsnachweis import Einweisungsnachweis
from domain.identity.start_qualifikation import QualifikationUnzureichend
from domain.identity.typen import BenutzerStatus, EinweisungsStatus, Systemrolle
from domain.katalog.produktdefinition import ProzedurSchrittEntwurf
from domain.katalog.version import MaterialisierterProzedurSchritt, ProduktdefinitionsVersion
from helpers import registriere_standard_vorlagen


def _pruefer(benutzer_id: str = "pruefer-1") -> Benutzer:
    return Benutzer.anlegen(
        login=benutzer_id,
        anzeigename="Prüfer",
        passwort_hash=PasswortHash("h"),
        rollen=frozenset({Systemrolle.PRUEFER}),
        status=BenutzerStatus.AKTIV,
        benutzer_id=benutzer_id,
    )


def _version(
    *,
    version_id: str = "ver-1",
    pd_id: str = "pd-1",
    kodierung: str = "1234567890",
) -> ProduktdefinitionsVersion:
    return ProduktdefinitionsVersion(
        version_id=version_id,
        produktdefinition_id=pd_id,
        produktkodierung=kodierung,
        prozedur_schritte=(
            MaterialisierterProzedurSchritt(
                schritt_id="s1",
                vorlage_id="v1",
                ist_pflicht=True,
                reihenfolge=1,
            ),
        ),
    )


def _qualify(
    *,
    katalog: InMemoryKatalogRepository,
    benutzer_repo: InMemoryBenutzerRepository,
    profile_repo: InMemoryBerechtigungsprofilRepository,
    einweisung_repo: InMemoryEinweisungsnachweisRepository,
    benutzer_id: str = "pruefer-1",
    version_id: str = "ver-1",
    pd_id: str = "pd-1",
) -> None:
    profil = Berechtigungsprofil.anlegen(
        bezeichnung="P", produktdefinition_ids={pd_id}
    )
    profile_repo.save(profil)
    profile_repo.benutzer_zuordnen(profil_id=profil.profil_id, benutzer_id=benutzer_id)
    einweisung_repo.save(
        Einweisungsnachweis.anlegen(
            benutzer_id=benutzer_id,
            version_id=version_id,
            eingewiesen_durch="admin",
        )
    )


def test_aktive_produkte_entwurf_nicht_enthalten():
    katalog = InMemoryKatalogRepository()
    EntwurfAnlegen(katalog).execute(produktkodierung="1111111111", prozedur_schritte=())
    assert AktiveProdukteListen(katalog).execute() == []


def test_aktive_produkte_veroeffentlichte_version():
    katalog = InMemoryKatalogRepository()
    katalog.register_aktive_version(_version())
    produkte = AktiveProdukteListen(katalog).execute()
    assert len(produkte) == 1
    assert produkte[0].produktkodierung == "1234567890"
    assert produkte[0].produktdefinition_id == "pd-1"
    assert produkte[0].version_id == "ver-1"


def test_aktive_produkte_nur_aktuelle_version_nach_publish():
    katalog = InMemoryKatalogRepository()
    bibliothek = InMemoryBibliothekRepository()
    registriere_standard_vorlagen(bibliothek, "vorlage-a")
    entwurf = EntwurfAnlegen(katalog).execute(
        produktkodierung="5555555555",
        prozedur_schritte=(
            ProzedurSchrittEntwurf(
                schritt_id="s1",
                vorlage_id="vorlage-a",
                ist_pflicht=True,
                reihenfolge=1,
            ),
        ),
    )
    v1 = ProduktdefinitionVeroeffentlichen(katalog, bibliothek).execute(
        entwurf.produktdefinition_id
    )
    v2 = ProduktdefinitionVeroeffentlichen(katalog, bibliothek).execute(
        entwurf.produktdefinition_id
    )
    produkte = AktiveProdukteListen(katalog).execute()
    assert len(produkte) == 1
    assert produkte[0].version_id == v2.version_id
    assert produkte[0].version_id != v1.version_id
    assert katalog.get_version(v1.version_id) is not None


def test_startbare_pruefungen_qualifiziert():
    katalog = InMemoryKatalogRepository()
    katalog.register_aktive_version(_version())
    benutzer_repo = InMemoryBenutzerRepository()
    profile_repo = InMemoryBerechtigungsprofilRepository()
    einweisung_repo = InMemoryEinweisungsnachweisRepository()
    benutzer_repo.save(_pruefer())
    _qualify(
        katalog=katalog,
        benutzer_repo=benutzer_repo,
        profile_repo=profile_repo,
        einweisung_repo=einweisung_repo,
    )
    result = StartbarePruefungenListen(
        katalog, benutzer_repo, profile_repo, einweisung_repo
    ).execute(benutzer_id="pruefer-1")
    assert [r.produktkodierung for r in result] == ["1234567890"]


def test_startbare_pruefungen_ohne_profil():
    katalog = InMemoryKatalogRepository()
    katalog.register_aktive_version(_version())
    benutzer_repo = InMemoryBenutzerRepository()
    profile_repo = InMemoryBerechtigungsprofilRepository()
    einweisung_repo = InMemoryEinweisungsnachweisRepository()
    benutzer_repo.save(_pruefer())
    einweisung_repo.save(
        Einweisungsnachweis.anlegen(
            benutzer_id="pruefer-1", version_id="ver-1", eingewiesen_durch="admin"
        )
    )
    assert (
        StartbarePruefungenListen(
            katalog, benutzer_repo, profile_repo, einweisung_repo
        ).execute(benutzer_id="pruefer-1")
        == []
    )


def test_startbare_pruefungen_ohne_einweisung():
    katalog = InMemoryKatalogRepository()
    katalog.register_aktive_version(_version())
    benutzer_repo = InMemoryBenutzerRepository()
    profile_repo = InMemoryBerechtigungsprofilRepository()
    einweisung_repo = InMemoryEinweisungsnachweisRepository()
    benutzer_repo.save(_pruefer())
    profil = Berechtigungsprofil.anlegen(
        bezeichnung="P", produktdefinition_ids={"pd-1"}
    )
    profile_repo.save(profil)
    profile_repo.benutzer_zuordnen(profil_id=profil.profil_id, benutzer_id="pruefer-1")
    assert (
        StartbarePruefungenListen(
            katalog, benutzer_repo, profile_repo, einweisung_repo
        ).execute(benutzer_id="pruefer-1")
        == []
    )


def test_startbare_pruefungen_einweisung_alte_version():
    katalog = InMemoryKatalogRepository()
    katalog.register_aktive_version(_version(version_id="ver-neu"))
    benutzer_repo = InMemoryBenutzerRepository()
    profile_repo = InMemoryBerechtigungsprofilRepository()
    einweisung_repo = InMemoryEinweisungsnachweisRepository()
    benutzer_repo.save(_pruefer())
    _qualify(
        katalog=katalog,
        benutzer_repo=benutzer_repo,
        profile_repo=profile_repo,
        einweisung_repo=einweisung_repo,
        version_id="ver-alt",
    )
    assert (
        StartbarePruefungenListen(
            katalog, benutzer_repo, profile_repo, einweisung_repo
        ).execute(benutzer_id="pruefer-1")
        == []
    )


def test_startbare_pruefungen_einweisung_abgelaufen():
    katalog = InMemoryKatalogRepository()
    katalog.register_aktive_version(_version())
    benutzer_repo = InMemoryBenutzerRepository()
    profile_repo = InMemoryBerechtigungsprofilRepository()
    einweisung_repo = InMemoryEinweisungsnachweisRepository()
    benutzer_repo.save(_pruefer())
    profil = Berechtigungsprofil.anlegen(
        bezeichnung="P", produktdefinition_ids={"pd-1"}
    )
    profile_repo.save(profil)
    profile_repo.benutzer_zuordnen(profil_id=profil.profil_id, benutzer_id="pruefer-1")
    einweisung_repo.save(
        Einweisungsnachweis.anlegen(
            benutzer_id="pruefer-1",
            version_id="ver-1",
            eingewiesen_durch="admin",
            gueltig_bis=date.today() - timedelta(days=1),
        )
    )
    assert (
        StartbarePruefungenListen(
            katalog, benutzer_repo, profile_repo, einweisung_repo
        ).execute(benutzer_id="pruefer-1")
        == []
    )


def test_startbare_pruefungen_einweisung_widerrufen():
    katalog = InMemoryKatalogRepository()
    katalog.register_aktive_version(_version())
    benutzer_repo = InMemoryBenutzerRepository()
    profile_repo = InMemoryBerechtigungsprofilRepository()
    einweisung_repo = InMemoryEinweisungsnachweisRepository()
    benutzer_repo.save(_pruefer())
    _qualify(
        katalog=katalog,
        benutzer_repo=benutzer_repo,
        profile_repo=profile_repo,
        einweisung_repo=einweisung_repo,
    )
    einweisung = einweisung_repo.get_gueltige(benutzer_id="pruefer-1", version_id="ver-1")
    assert einweisung is not None
    einweisung_repo.save(einweisung.widerrufen())
    assert (
        StartbarePruefungenListen(
            katalog, benutzer_repo, profile_repo, einweisung_repo
        ).execute(benutzer_id="pruefer-1")
        == []
    )


def test_startbare_pruefungen_inaktives_profil():
    katalog = InMemoryKatalogRepository()
    katalog.register_aktive_version(_version())
    benutzer_repo = InMemoryBenutzerRepository()
    profile_repo = InMemoryBerechtigungsprofilRepository()
    einweisung_repo = InMemoryEinweisungsnachweisRepository()
    benutzer_repo.save(_pruefer())
    profil = Berechtigungsprofil.anlegen(
        bezeichnung="P", produktdefinition_ids={"pd-1"}
    )
    profile_repo.save(profil)
    profile_repo.benutzer_zuordnen(profil_id=profil.profil_id, benutzer_id="pruefer-1")
    einweisung_repo.save(
        Einweisungsnachweis.anlegen(
            benutzer_id="pruefer-1", version_id="ver-1", eingewiesen_durch="admin"
        )
    )
    profile_repo.save(profil.deaktivieren())
    assert (
        StartbarePruefungenListen(
            katalog, benutzer_repo, profile_repo, einweisung_repo
        ).execute(benutzer_id="pruefer-1")
        == []
    )


def test_startbare_pruefungen_keine_pruefer_rolle():
    katalog = InMemoryKatalogRepository()
    katalog.register_aktive_version(_version())
    benutzer_repo = InMemoryBenutzerRepository()
    profile_repo = InMemoryBerechtigungsprofilRepository()
    einweisung_repo = InMemoryEinweisungsnachweisRepository()
    benutzer_repo.save(
        Benutzer.anlegen(
            login="qm-only",
            anzeigename="QM",
            passwort_hash=PasswortHash("h"),
            rollen=frozenset({Systemrolle.QM}),
            status=BenutzerStatus.AKTIV,
            benutzer_id="qm-1",
        )
    )
    _qualify(
        katalog=katalog,
        benutzer_repo=benutzer_repo,
        profile_repo=profile_repo,
        einweisung_repo=einweisung_repo,
        benutzer_id="qm-1",
    )
    assert (
        StartbarePruefungenListen(
            katalog, benutzer_repo, profile_repo, einweisung_repo
        ).execute(benutzer_id="qm-1")
        == []
    )


def test_startbare_pruefungen_zwei_qualifizierte_produkte():
    katalog = InMemoryKatalogRepository()
    katalog.register_aktive_version(
        _version(version_id="ver-a", pd_id="pd-a", kodierung="1111111111")
    )
    katalog.register_aktive_version(
        _version(version_id="ver-b", pd_id="pd-b", kodierung="2222222222")
    )
    benutzer_repo = InMemoryBenutzerRepository()
    profile_repo = InMemoryBerechtigungsprofilRepository()
    einweisung_repo = InMemoryEinweisungsnachweisRepository()
    benutzer_repo.save(_pruefer())
    profil = Berechtigungsprofil.anlegen(
        bezeichnung="P", produktdefinition_ids={"pd-a", "pd-b"}
    )
    profile_repo.save(profil)
    profile_repo.benutzer_zuordnen(profil_id=profil.profil_id, benutzer_id="pruefer-1")
    for vid in ("ver-a", "ver-b"):
        einweisung_repo.save(
            Einweisungsnachweis.anlegen(
                benutzer_id="pruefer-1", version_id=vid, eingewiesen_durch="admin"
            )
        )
    result = StartbarePruefungenListen(
        katalog, benutzer_repo, profile_repo, einweisung_repo
    ).execute(benutzer_id="pruefer-1")
    assert [r.produktkodierung for r in result] == ["1111111111", "2222222222"]


def test_startbare_nach_publish_ohne_uebernahme():
    katalog = InMemoryKatalogRepository()
    bibliothek = InMemoryBibliothekRepository()
    einweisung_repo = InMemoryEinweisungsnachweisRepository()
    benutzer_repo = InMemoryBenutzerRepository()
    profile_repo = InMemoryBerechtigungsprofilRepository()
    benutzer_repo.save(_pruefer())
    registriere_standard_vorlagen(bibliothek, "vorlage-a")
    entwurf = EntwurfAnlegen(katalog).execute(
        produktkodierung="3333333333",
        prozedur_schritte=(
            ProzedurSchrittEntwurf(
                schritt_id="s1",
                vorlage_id="vorlage-a",
                ist_pflicht=True,
                reihenfolge=1,
            ),
        ),
    )
    v1 = ProduktdefinitionVeroeffentlichen(katalog, bibliothek).execute(
        entwurf.produktdefinition_id
    )
    _qualify(
        katalog=katalog,
        benutzer_repo=benutzer_repo,
        profile_repo=profile_repo,
        einweisung_repo=einweisung_repo,
        version_id=v1.version_id,
        pd_id=entwurf.produktdefinition_id,
    )
    listen = StartbarePruefungenListen(
        katalog, benutzer_repo, profile_repo, einweisung_repo
    )
    assert [r.produktkodierung for r in listen.execute(benutzer_id="pruefer-1")] == [
        "3333333333"
    ]
    ProduktdefinitionVeroeffentlichen(katalog, bibliothek).execute(
        entwurf.produktdefinition_id
    )
    assert listen.execute(benutzer_id="pruefer-1") == []


def test_startbare_nach_publish_mit_uebernahme():
    katalog = InMemoryKatalogRepository()
    bibliothek = InMemoryBibliothekRepository()
    einweisung_repo = InMemoryEinweisungsnachweisRepository()
    benutzer_repo = InMemoryBenutzerRepository()
    profile_repo = InMemoryBerechtigungsprofilRepository()
    benutzer_repo.save(_pruefer())
    registriere_standard_vorlagen(bibliothek, "vorlage-a")
    entwurf = EntwurfAnlegen(katalog).execute(
        produktkodierung="4444444444",
        prozedur_schritte=(
            ProzedurSchrittEntwurf(
                schritt_id="s1",
                vorlage_id="vorlage-a",
                ist_pflicht=True,
                reihenfolge=1,
            ),
        ),
    )
    v1 = ProduktdefinitionVeroeffentlichen(katalog, bibliothek).execute(
        entwurf.produktdefinition_id
    )
    EinweisungAnlegen(einweisung_repo, benutzer_repo, katalog).execute(
        benutzer_id="pruefer-1",
        version_id=v1.version_id,
        eingewiesen_durch="admin",
    )
    profil = ProfilAnlegen(profile_repo).execute(
        bezeichnung="P", produktdefinition_ids=[entwurf.produktdefinition_id]
    )
    ProfilBenutzerZuordnen(profile_repo, benutzer_repo).execute(
        profil_id=profil.profil_id, benutzer_id="pruefer-1"
    )
    ProduktdefinitionVeroeffentlichen(katalog, bibliothek).execute(
        entwurf.produktdefinition_id,
        einweisung_uebernehmen=True,
        eingewiesen_durch="admin",
        einweisungen=einweisung_repo,
    )
    result = StartbarePruefungenListen(
        katalog, benutzer_repo, profile_repo, einweisung_repo
    ).execute(benutzer_id="pruefer-1")
    assert [r.produktkodierung for r in result] == ["4444444444"]


def test_manipulierter_start_bleibt_gesperrt():
    katalog = InMemoryKatalogRepository()
    katalog.register_aktive_version(_version())
    benutzer_repo = InMemoryBenutzerRepository()
    profile_repo = InMemoryBerechtigungsprofilRepository()
    einweisung_repo = InMemoryEinweisungsnachweisRepository()
    benutzer_repo.save(_pruefer())
    listen = StartbarePruefungenListen(
        katalog, benutzer_repo, profile_repo, einweisung_repo
    )
    assert listen.execute(benutzer_id="pruefer-1") == []
    with pytest.raises(QualifikationUnzureichend):
        PruefungStarten(
            katalog,
            InMemoryPrueflaufRepository(),
            benutzer_repo,
            profile_repo,
            einweisung_repo,
        ).execute(
            produktkodierung="1234567890",
            pruefobjekt_kennung="X",
            pruefer_id="pruefer-1",
        )


def test_profil_zuordnung_read_via_repository():
    profile_repo = InMemoryBerechtigungsprofilRepository()
    benutzer_repo = InMemoryBenutzerRepository()
    benutzer_repo.save(_pruefer())
    assert profile_repo.profil_ids_fuer_benutzer("pruefer-1") == frozenset()
    p1 = ProfilAnlegen(profile_repo).execute(bezeichnung="A", produktdefinition_ids=["pd-1"])
    p2 = ProfilAnlegen(profile_repo).execute(bezeichnung="B", produktdefinition_ids=["pd-2"])
    ProfilBenutzerZuordnen(profile_repo, benutzer_repo).execute(
        profil_id=p1.profil_id, benutzer_id="pruefer-1"
    )
    ProfilBenutzerZuordnen(profile_repo, benutzer_repo).execute(
        profil_id=p2.profil_id, benutzer_id="pruefer-1"
    )
    ids = profile_repo.profil_ids_fuer_benutzer("pruefer-1")
    assert ids == frozenset({p1.profil_id, p2.profil_id})
    ProfilBenutzerEntfernen(profile_repo, benutzer_repo).execute(
        profil_id=p1.profil_id, benutzer_id="pruefer-1"
    )
    assert profile_repo.profil_ids_fuer_benutzer("pruefer-1") == frozenset({p2.profil_id})
