"""Application-Tests — Entwurfs-Schrittbearbeitung (Gate 8.2b2)."""

import pytest

from adapters.persistence.in_memory import InMemoryBibliothekRepository, InMemoryKatalogRepository
from application.katalog.entwurf_anlegen import EntwurfAnlegen
from application.katalog.entwurf_lesen import EntwurfLesen
from application.katalog.externes_kommando_anlegen import ExternesKommandoAnlegen
from application.katalog.kommando_zuweisen import KommandoProzedurSchrittZuweisen
from application.katalog.prozedur_schritt_anlegen import ProzedurSchrittAnlegen
from application.katalog.prozedur_schritt_aktualisieren import ProzedurSchrittAktualisieren
from application.katalog.prozedur_schritt_loeschen import ProzedurSchrittLoeschen
from application.katalog.prozedur_schritt_reihenfolge_aendern import ProzedurSchrittReihenfolgeAendern
from application.katalog.veroeffentlichen import ProduktdefinitionVeroeffentlichen
from domain.katalog.errors import (
    EntwurfNichtGefunden,
    ProzedurSchrittNichtGefunden,
    SchrittIdBereitsVorhanden,
    VorlageNichtGefunden,
)
from domain.katalog.produktdefinition import ProzedurSchrittEntwurf
from helpers import registriere_standard_vorlagen


def _setup():
    katalog = InMemoryKatalogRepository()
    bibliothek = InMemoryBibliothekRepository()
    registriere_standard_vorlagen(bibliothek, "vorlage-a", "vorlage-b")
    return katalog, bibliothek


def _leerer_entwurf(katalog):
    return EntwurfAnlegen(katalog).execute(
        produktkodierung="1234567890",
        prozedur_schritte=(),
    )


def test_entwurf_lesen_happy_path():
    katalog, _ = _setup()
    entwurf = _leerer_entwurf(katalog)
    gelesen = EntwurfLesen(katalog).execute(entwurf.produktdefinition_id)
    assert gelesen.produktkodierung == "1234567890"


def test_entwurf_lesen_nicht_gefunden():
    katalog, _ = _setup()
    with pytest.raises(EntwurfNichtGefunden):
        EntwurfLesen(katalog).execute("unbekannt")


def test_schritt_anlegen_und_lesen():
    katalog, bibliothek = _setup()
    entwurf = _leerer_entwurf(katalog)
    schritt = ProzedurSchrittAnlegen(katalog, bibliothek).execute(
        entwurf.produktdefinition_id,
        schritt_id="s1",
        vorlage_id="vorlage-a",
        ist_pflicht=True,
        sollvorgaben={"spannung": {"min": 1, "max": 2}},
    )
    assert schritt.reihenfolge == 1
    gelesen = EntwurfLesen(katalog).execute(entwurf.produktdefinition_id)
    assert len(gelesen.prozedur_schritte) == 1


def test_schritt_anlegen_vorlage_fehlt():
    katalog, bibliothek = _setup()
    entwurf = _leerer_entwurf(katalog)
    with pytest.raises(VorlageNichtGefunden):
        ProzedurSchrittAnlegen(katalog, bibliothek).execute(
            entwurf.produktdefinition_id,
            schritt_id="s1",
            vorlage_id="fehlt",
            ist_pflicht=True,
        )


def test_schritt_anlegen_doppelte_id():
    katalog, bibliothek = _setup()
    entwurf = _leerer_entwurf(katalog)
    ProzedurSchrittAnlegen(katalog, bibliothek).execute(
        entwurf.produktdefinition_id,
        schritt_id="s1",
        vorlage_id="vorlage-a",
        ist_pflicht=True,
    )
    with pytest.raises(SchrittIdBereitsVorhanden):
        ProzedurSchrittAnlegen(katalog, bibliothek).execute(
            entwurf.produktdefinition_id,
            schritt_id="s1",
            vorlage_id="vorlage-b",
            ist_pflicht=False,
        )


def test_schritt_aktualisieren_erhaelt_automatisierung():
    katalog, bibliothek = _setup()
    entwurf = _leerer_entwurf(katalog)
    ProzedurSchrittAnlegen(katalog, bibliothek).execute(
        entwurf.produktdefinition_id,
        schritt_id="s1",
        vorlage_id="vorlage-a",
        ist_pflicht=True,
    )
    kommando = ExternesKommandoAnlegen(bibliothek).execute(bezeichnung="K", kommandocode="CMD")
    KommandoProzedurSchrittZuweisen(katalog, bibliothek).execute(
        entwurf.produktdefinition_id,
        "s1",
        kommando.kommando_id,
    )
    aktualisiert = ProzedurSchrittAktualisieren(katalog, bibliothek).execute(
        entwurf.produktdefinition_id,
        "s1",
        vorlage_id="vorlage-b",
        ist_pflicht=False,
        sollvorgaben={"x": 1},
    )
    assert aktualisiert.kommando_id == kommando.kommando_id
    assert aktualisiert.vorlage_id == "vorlage-b"


def test_schritt_loeschen_und_reihenfolge():
    katalog, bibliothek = _setup()
    entwurf = _leerer_entwurf(katalog)
    for sid in ("s1", "s2"):
        ProzedurSchrittAnlegen(katalog, bibliothek).execute(
            entwurf.produktdefinition_id,
            schritt_id=sid,
            vorlage_id="vorlage-a",
            ist_pflicht=True,
        )
    ProzedurSchrittLoeschen(katalog).execute(entwurf.produktdefinition_id, "s1")
    gelesen = EntwurfLesen(katalog).execute(entwurf.produktdefinition_id)
    assert len(gelesen.prozedur_schritte) == 1
    assert gelesen.prozedur_schritte[0].reihenfolge == 1


def test_reihenfolge_aendern():
    katalog, bibliothek = _setup()
    entwurf = _leerer_entwurf(katalog)
    for sid in ("s1", "s2", "s3"):
        ProzedurSchrittAnlegen(katalog, bibliothek).execute(
            entwurf.produktdefinition_id,
            schritt_id=sid,
            vorlage_id="vorlage-a",
            ist_pflicht=True,
        )
    ProzedurSchrittReihenfolgeAendern(katalog).execute(
        entwurf.produktdefinition_id,
        ["s3", "s1", "s2"],
    )
    gelesen = EntwurfLesen(katalog).execute(entwurf.produktdefinition_id)
    assert [s.schritt_id for s in sorted(gelesen.prozedur_schritte, key=lambda x: x.reihenfolge)] == [
        "s3",
        "s1",
        "s2",
    ]


def test_publish_nach_schritt_aenderung_materialisiert_neu():
    katalog, bibliothek = _setup()
    entwurf = EntwurfAnlegen(katalog).execute(
        produktkodierung="1234567890",
        prozedur_schritte=(
            ProzedurSchrittEntwurf(
                schritt_id="s1",
                vorlage_id="vorlage-a",
                ist_pflicht=True,
                reihenfolge=1,
                sollvorgaben={"spannung": {"min": 1, "max": 2}},
            ),
        ),
    )
    v1 = ProduktdefinitionVeroeffentlichen(katalog, bibliothek).execute(entwurf.produktdefinition_id)
    ProzedurSchrittAktualisieren(katalog, bibliothek).execute(
        entwurf.produktdefinition_id,
        "s1",
        vorlage_id="vorlage-b",
        ist_pflicht=True,
        sollvorgaben={"spannung": {"min": 10, "max": 20}},
    )
    v2 = ProduktdefinitionVeroeffentlichen(katalog, bibliothek).execute(entwurf.produktdefinition_id)
    alt = katalog.get_version(v1.version_id)
    neu = katalog.get_version(v2.version_id)
    assert alt is not None and neu is not None
    assert alt.schritt_by_id("s1").sollvorgaben["spannung"]["min"] == 1
    assert neu.schritt_by_id("s1").sollvorgaben["spannung"]["min"] == 10
    assert neu.schritt_by_id("s1").materialisierte_vorlage.vorlage_id == "vorlage-b"


def test_schritt_aktualisieren_schritt_fehlt():
    katalog, bibliothek = _setup()
    entwurf = _leerer_entwurf(katalog)
    with pytest.raises(ProzedurSchrittNichtGefunden):
        ProzedurSchrittAktualisieren(katalog, bibliothek).execute(
            entwurf.produktdefinition_id,
            "s9",
            vorlage_id="vorlage-a",
            ist_pflicht=True,
            sollvorgaben={},
        )
