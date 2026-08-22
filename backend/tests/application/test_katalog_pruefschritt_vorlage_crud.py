"""Application-Tests — PrüfschrittVorlage CRUD und Publish (Gate 8.2b1)."""

import pytest

from adapters.persistence.in_memory import InMemoryBibliothekRepository, InMemoryKatalogRepository
from application.katalog.entwurf_anlegen import EntwurfAnlegen
from application.katalog.pruefschritt_vorlage_anlegen import PruefschrittVorlageAnlegen
from application.katalog.pruefschritt_vorlage_aktualisieren import PruefschrittVorlageAktualisieren
from application.katalog.pruefschritt_vorlage_lesen import PruefschrittVorlageLesen
from application.katalog.pruefschritt_vorlage_loeschen import PruefschrittVorlageLoeschen
from application.katalog.pruefschritt_vorlagen_listen import PruefschrittVorlagenListen
from application.katalog.veroeffentlichen import ProduktdefinitionVeroeffentlichen
from domain.katalog.errors import VorlageInVerwendung, VorlageNichtGefunden
from domain.katalog.produktdefinition import ProzedurSchrittEntwurf


def _setup():
    return InMemoryKatalogRepository(), InMemoryBibliothekRepository()


def test_pruefschritt_vorlage_crud():
    _, bibliothek = _setup()
    vorlage = PruefschrittVorlageAnlegen(bibliothek).execute(
        bezeichnung="Messung",
        beschreibung="Manuell",
    )
    assert PruefschrittVorlageLesen(bibliothek).execute(vorlage.vorlage_id).bezeichnung == "Messung"
    assert len(PruefschrittVorlagenListen(bibliothek).execute()) == 1
    aktualisiert = PruefschrittVorlageAktualisieren(bibliothek).execute(
        vorlage.vorlage_id,
        bezeichnung="Geändert",
        beschreibung=None,
    )
    assert aktualisiert.bezeichnung == "Geändert"
    PruefschrittVorlageLoeschen(InMemoryKatalogRepository(), bibliothek).execute(vorlage.vorlage_id)
    with pytest.raises(VorlageNichtGefunden):
        PruefschrittVorlageLesen(bibliothek).execute(vorlage.vorlage_id)


def test_publish_mit_gueltiger_vorlage():
    katalog, bibliothek = _setup()
    vorlage = PruefschrittVorlageAnlegen(bibliothek).execute(bezeichnung="V")
    entwurf = EntwurfAnlegen(katalog).execute(
        produktkodierung="1111111111",
        prozedur_schritte=(
            ProzedurSchrittEntwurf(
                schritt_id="s1",
                vorlage_id=vorlage.vorlage_id,
                ist_pflicht=True,
                reihenfolge=1,
            ),
        ),
    )
    version = ProduktdefinitionVeroeffentlichen(katalog, bibliothek).execute(
        entwurf.produktdefinition_id
    )
    schritt = version.schritt_by_id("s1")
    assert schritt is not None
    assert schritt.materialisierte_vorlage is not None
    assert schritt.materialisierte_vorlage.bezeichnung == "V"


def test_publish_mit_unbekannter_vorlage():
    katalog, bibliothek = _setup()
    entwurf = EntwurfAnlegen(katalog).execute(
        produktkodierung="2222222222",
        prozedur_schritte=(
            ProzedurSchrittEntwurf(
                schritt_id="s1",
                vorlage_id="fehlend",
                ist_pflicht=True,
                reihenfolge=1,
            ),
        ),
    )
    with pytest.raises(VorlageNichtGefunden):
        ProduktdefinitionVeroeffentlichen(katalog, bibliothek).execute(entwurf.produktdefinition_id)


def test_vorlage_loeschen_in_entwurf_verwendet():
    katalog, bibliothek = _setup()
    vorlage = PruefschrittVorlageAnlegen(bibliothek).execute(bezeichnung="V")
    EntwurfAnlegen(katalog).execute(
        produktkodierung="3333333333",
        prozedur_schritte=(
            ProzedurSchrittEntwurf(
                schritt_id="s1",
                vorlage_id=vorlage.vorlage_id,
                ist_pflicht=True,
                reihenfolge=1,
            ),
        ),
    )
    with pytest.raises(VorlageInVerwendung):
        PruefschrittVorlageLoeschen(katalog, bibliothek).execute(vorlage.vorlage_id)


def test_vorlage_loeschen_nicht_durch_veroeffentlichte_version_blockiert():
    katalog, bibliothek = _setup()
    v1 = PruefschrittVorlageAnlegen(bibliothek).execute(bezeichnung="V1")
    v2 = PruefschrittVorlageAnlegen(bibliothek).execute(bezeichnung="V2")
    entwurf = EntwurfAnlegen(katalog).execute(
        produktkodierung="4444444444",
        prozedur_schritte=(
            ProzedurSchrittEntwurf(
                schritt_id="s1",
                vorlage_id=v1.vorlage_id,
                ist_pflicht=True,
                reihenfolge=1,
            ),
        ),
    )
    ProduktdefinitionVeroeffentlichen(katalog, bibliothek).execute(entwurf.produktdefinition_id)
    PruefschrittVorlageLoeschen(katalog, bibliothek).execute(v2.vorlage_id)
    assert bibliothek.get_pruefschritt_vorlage(v2.vorlage_id) is None


def test_vorlage_loeschen_blockiert_wenn_offener_entwurf_referenziert():
    katalog, bibliothek = _setup()
    vorlage = PruefschrittVorlageAnlegen(bibliothek).execute(bezeichnung="V")
    entwurf = EntwurfAnlegen(katalog).execute(
        produktkodierung="5555555555",
        prozedur_schritte=(
            ProzedurSchrittEntwurf(
                schritt_id="s1",
                vorlage_id=vorlage.vorlage_id,
                ist_pflicht=True,
                reihenfolge=1,
            ),
        ),
    )
    ProduktdefinitionVeroeffentlichen(katalog, bibliothek).execute(entwurf.produktdefinition_id)
    with pytest.raises(VorlageInVerwendung):
        PruefschrittVorlageLoeschen(katalog, bibliothek).execute(vorlage.vorlage_id)
