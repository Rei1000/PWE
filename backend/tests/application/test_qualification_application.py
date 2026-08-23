"""Application-Tests — Qualifikation / Startregel / Publish-Übernahme (Gate 8.1b)."""

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
from application.identity.profil_verwaltung import (
    ProfilAnlegen,
    ProfilBenutzerZuordnen,
)
from application.katalog.entwurf_anlegen import EntwurfAnlegen
from application.katalog.veroeffentlichen import ProduktdefinitionVeroeffentlichen
from application.pruefausfuehrung.pruefung_starten import PruefungStarten
from domain.identity.benutzer import Benutzer, PasswortHash
from domain.identity.berechtigungsprofil import Berechtigungsprofil
from domain.identity.einweisungsnachweis import EinweisungBereitsGueltig
from domain.identity.start_qualifikation import QualifikationUnzureichend
from domain.identity.typen import BenutzerStatus, Systemrolle
from domain.katalog.produktdefinition import ProzedurSchrittEntwurf
from domain.katalog.version import MaterialisierterProzedurSchritt, ProduktdefinitionsVersion
from helpers import registriere_standard_vorlagen
from tests.support.qualification import make_pruefung_starten


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


def test_pruefung_starten_mit_qualifikation_ok():
    katalog = InMemoryKatalogRepository()
    katalog.register_aktive_version(_version())
    usecase = make_pruefung_starten(katalog, InMemoryPrueflaufRepository())
    prueflauf = usecase.execute(
        produktkodierung="1234567890",
        pruefobjekt_kennung="G-1",
        pruefer_id="pruefer-1",
    )
    assert prueflauf.pruefer_id == "pruefer-1"
    assert prueflauf.version_id == "ver-1"


def test_pruefung_starten_ohne_einweisung_403():
    katalog = InMemoryKatalogRepository()
    katalog.register_aktive_version(_version())
    prueflauf_repo = InMemoryPrueflaufRepository()
    benutzer_repo = InMemoryBenutzerRepository()
    profile_repo = InMemoryBerechtigungsprofilRepository()
    einweisung_repo = InMemoryEinweisungsnachweisRepository()
    benutzer_repo.save(_pruefer())
    profil = Berechtigungsprofil.anlegen(
        bezeichnung="P", produktdefinition_ids={"pd-1"}
    )
    profile_repo.save(profil)
    profile_repo.benutzer_zuordnen(profil_id=profil.profil_id, benutzer_id="pruefer-1")

    with pytest.raises(QualifikationUnzureichend):
        PruefungStarten(
            katalog, prueflauf_repo, benutzer_repo, profile_repo, einweisung_repo
        ).execute(
            produktkodierung="1234567890",
            pruefobjekt_kennung="G-1",
            pruefer_id="pruefer-1",
        )


def test_einweisung_doppelt_gueltig_conflict():
    katalog = InMemoryKatalogRepository()
    katalog.register_aktive_version(_version())
    benutzer_repo = InMemoryBenutzerRepository()
    einweisung_repo = InMemoryEinweisungsnachweisRepository()
    benutzer_repo.save(_pruefer())
    uc = EinweisungAnlegen(einweisung_repo, benutzer_repo, katalog)
    uc.execute(
        benutzer_id="pruefer-1",
        version_id="ver-1",
        eingewiesen_durch="admin",
    )
    with pytest.raises(EinweisungBereitsGueltig):
        uc.execute(
            benutzer_id="pruefer-1",
            version_id="ver-1",
            eingewiesen_durch="admin",
        )


def test_profil_zuordnung_und_start():
    katalog = InMemoryKatalogRepository()
    katalog.register_aktive_version(_version())
    prueflauf_repo = InMemoryPrueflaufRepository()
    benutzer_repo = InMemoryBenutzerRepository()
    profile_repo = InMemoryBerechtigungsprofilRepository()
    einweisung_repo = InMemoryEinweisungsnachweisRepository()
    benutzer_repo.save(_pruefer())

    profil = ProfilAnlegen(profile_repo).execute(
        bezeichnung="Linie", produktdefinition_ids=["pd-1"]
    )
    ProfilBenutzerZuordnen(profile_repo, benutzer_repo).execute(
        profil_id=profil.profil_id, benutzer_id="pruefer-1"
    )
    EinweisungAnlegen(einweisung_repo, benutzer_repo, katalog).execute(
        benutzer_id="pruefer-1",
        version_id="ver-1",
        eingewiesen_durch="admin",
    )

    prueflauf = PruefungStarten(
        katalog, prueflauf_repo, benutzer_repo, profile_repo, einweisung_repo
    ).execute(
        produktkodierung="1234567890",
        pruefobjekt_kennung="G-1",
        pruefer_id="pruefer-1",
    )
    assert prueflauf.version_id == "ver-1"


def test_publish_uebernimmt_einweisung():
    katalog = InMemoryKatalogRepository()
    bibliothek = InMemoryBibliothekRepository()
    einweisungen = InMemoryEinweisungsnachweisRepository()
    benutzer_repo = InMemoryBenutzerRepository()
    benutzer_repo.save(_pruefer())
    registriere_standard_vorlagen(bibliothek, "vorlage-a")

    entwurf = EntwurfAnlegen(katalog).execute(
        produktkodierung="KODE-1",
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
    EinweisungAnlegen(einweisungen, benutzer_repo, katalog).execute(
        benutzer_id="pruefer-1",
        version_id=v1.version_id,
        eingewiesen_durch="admin",
        gueltig_bis=date.today() + timedelta(days=30),
    )

    entwurf = katalog.get_entwurf(entwurf.produktdefinition_id)
    assert entwurf is not None
    assert entwurf.aktive_version_id == v1.version_id

    v2 = ProduktdefinitionVeroeffentlichen(katalog, bibliothek).execute(
        entwurf.produktdefinition_id,
        einweisung_uebernehmen=True,
        eingewiesen_durch="admin",
        einweisungen=einweisungen,
    )
    uebernommen = einweisungen.get_gueltige(
        benutzer_id="pruefer-1", version_id=v2.version_id
    )
    assert uebernommen is not None
    assert uebernommen.uebernommen_bei_publish is True
    assert uebernommen.herkunft_einweisung_id is not None
    assert (
        einweisungen.get_gueltige(benutzer_id="pruefer-1", version_id=v1.version_id)
        is not None
    )


def test_publish_ohne_flag_keine_uebernahme():
    katalog = InMemoryKatalogRepository()
    bibliothek = InMemoryBibliothekRepository()
    einweisungen = InMemoryEinweisungsnachweisRepository()
    benutzer_repo = InMemoryBenutzerRepository()
    benutzer_repo.save(_pruefer())
    registriere_standard_vorlagen(bibliothek, "vorlage-a")

    entwurf = EntwurfAnlegen(katalog).execute(
        produktkodierung="KODE-2",
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
    EinweisungAnlegen(einweisungen, benutzer_repo, katalog).execute(
        benutzer_id="pruefer-1",
        version_id=v1.version_id,
        eingewiesen_durch="admin",
    )
    v2 = ProduktdefinitionVeroeffentlichen(katalog, bibliothek).execute(
        entwurf.produktdefinition_id
    )
    assert (
        einweisungen.get_gueltige(benutzer_id="pruefer-1", version_id=v2.version_id)
        is None
    )
