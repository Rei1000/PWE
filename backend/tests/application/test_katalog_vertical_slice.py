"""Vertical Slice 2 — Katalog: Entwurf → Veröffentlichen → Prüflauf."""

from domain.pruefausfuehrung.prueflauf import NachweisArt
from domain.katalog.produktdefinition import ProzedurSchrittEntwurf
from helpers import in_memory_abschluss_persistenz
from adapters.persistence.in_memory import (
    InMemoryBibliothekRepository,
    InMemoryKatalogRepository,
    InMemoryProtokollRepository,
    InMemoryPrueflaufRepository,
)
from application.katalog.entwurf_anlegen import EntwurfAnlegen
from application.katalog.veroeffentlichen import ProduktdefinitionVeroeffentlichen
from application.pruefausfuehrung.komponente_erfassen import KomponenteErfassen
from application.pruefausfuehrung.nachweis_erfassen import NachweisErfassen
from application.pruefausfuehrung.pruefung_abschliessen import PruefungAbschliessen
from application.pruefausfuehrung.pruefung_starten import PruefungStarten
from application.pruefausfuehrung.schritt_beurteilen import SchrittBeurteilen


def _setup():
    return (
        InMemoryKatalogRepository(),
        InMemoryBibliothekRepository(),
        InMemoryPrueflaufRepository(),
        InMemoryProtokollRepository(),
    )


def test_katalog_slice_entwurf_veroeffentlichen_und_prueflauf():
    katalog, bibliothek, prueflauf_repo, protokoll_repo = _setup()

    entwurf = EntwurfAnlegen(katalog).execute(
        produktkodierung="9876543210",
        prozedur_schritte=(
            ProzedurSchrittEntwurf(
                schritt_id="schritt-a",
                vorlage_id="vorlage-a",
                ist_pflicht=True,
                reihenfolge=1,
                sollvorgaben={"spannung": {"min": 220, "max": 240}},
            ),
        ),
        sollbestueckung=("mainboard",),
        basisprodukt_sollvorgaben={"spannung": {"min": 200, "max": 250}},
    )
    version = ProduktdefinitionVeroeffentlichen(katalog, bibliothek).execute(
        entwurf.produktdefinition_id
    )

    assert katalog.get_aktive_version_fuer_kodierung("9876543210") is not None
    assert version.version_id == entwurf.aktive_version_id

    prueflauf = PruefungStarten(katalog, prueflauf_repo).execute(
        produktkodierung="9876543210",
        pruefobjekt_kennung="GER-100",
        pruefer_id="pruefer-1",
    )
    assert prueflauf.version_id == version.version_id

    KomponenteErfassen(prueflauf_repo).execute(prueflauf.prueflauf_id, "mainboard", "MB-2")
    NachweisErfassen(prueflauf_repo).execute(
        prueflauf.prueflauf_id, "schritt-a", NachweisArt.MESSWERT, {"spannung": 230}
    )
    SchrittBeurteilen(katalog, prueflauf_repo).execute(prueflauf.prueflauf_id, "schritt-a")

    abgeschlossen, snapshot = PruefungAbschliessen(
        katalog, prueflauf_repo, in_memory_abschluss_persistenz(prueflauf_repo, protokoll_repo)
    ).execute(prueflauf.prueflauf_id)

    assert abgeschlossen.ist_gueltig()
    assert snapshot.version_id == version.version_id


def test_katalog_slice_neue_version_ueberschreibt_aktive():
    katalog, bibliothek, _, _ = _setup()

    entwurf = EntwurfAnlegen(katalog).execute(
        produktkodierung="1111111111",
        prozedur_schritte=(
            ProzedurSchrittEntwurf(
                schritt_id="schritt-a",
                vorlage_id="vorlage-a",
                ist_pflicht=True,
                reihenfolge=1,
            ),
        ),
    )
    v1 = ProduktdefinitionVeroeffentlichen(katalog, bibliothek).execute(entwurf.produktdefinition_id)

    entwurf.prozedur_schritte.append(
        ProzedurSchrittEntwurf(
            schritt_id="schritt-b",
            vorlage_id="vorlage-b",
            ist_pflicht=False,
            reihenfolge=2,
        )
    )
    katalog.save_entwurf(entwurf)
    v2 = ProduktdefinitionVeroeffentlichen(katalog, bibliothek).execute(entwurf.produktdefinition_id)

    aktiv = katalog.get_aktive_version_fuer_kodierung("1111111111")
    assert aktiv is not None
    assert aktiv.version_id == v2.version_id
    assert aktiv.version_id != v1.version_id
    assert len(aktiv.prozedur_schritte) == 2
    assert katalog.get_version(v1.version_id) is not None


def test_laufende_pruefung_bleibt_auf_alter_version_nach_neuer_veroeffentlichung():
    katalog, bibliothek, prueflauf_repo, protokoll_repo = _setup()

    entwurf = EntwurfAnlegen(katalog).execute(
        produktkodierung="2222222222",
        prozedur_schritte=(
            ProzedurSchrittEntwurf(
                schritt_id="schritt-a",
                vorlage_id="vorlage-a",
                ist_pflicht=True,
                reihenfolge=1,
                sollvorgaben={"spannung": {"min": 220, "max": 240}},
            ),
        ),
        sollbestueckung=("mainboard",),
    )
    v1 = ProduktdefinitionVeroeffentlichen(katalog, bibliothek).execute(entwurf.produktdefinition_id)

    prueflauf = PruefungStarten(katalog, prueflauf_repo).execute(
        produktkodierung="2222222222",
        pruefobjekt_kennung="GER-200",
        pruefer_id="pruefer-1",
    )
    assert prueflauf.version_id == v1.version_id

    entwurf.prozedur_schritte[0].sollvorgaben = {"spannung": {"min": 100, "max": 110}}
    katalog.save_entwurf(entwurf)
    ProduktdefinitionVeroeffentlichen(katalog, bibliothek).execute(entwurf.produktdefinition_id)

    KomponenteErfassen(prueflauf_repo).execute(prueflauf.prueflauf_id, "mainboard", "MB-3")
    NachweisErfassen(prueflauf_repo).execute(
        prueflauf.prueflauf_id, "schritt-a", NachweisArt.MESSWERT, {"spannung": 230}
    )
    SchrittBeurteilen(katalog, prueflauf_repo).execute(prueflauf.prueflauf_id, "schritt-a")

    abgeschlossen, _ = PruefungAbschliessen(
        katalog, prueflauf_repo, in_memory_abschluss_persistenz(prueflauf_repo, protokoll_repo)
    ).execute(prueflauf.prueflauf_id)

    assert abgeschlossen.ist_gueltig()
    assert abgeschlossen.version_id == v1.version_id
