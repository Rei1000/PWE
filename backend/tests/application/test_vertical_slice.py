"""Vertical Slice 1 — ausschließlich über Application-Use-Cases."""

from domain.katalog.version import MaterialisierterProzedurSchritt, ProduktdefinitionsVersion
from domain.pruefausfuehrung.prueflauf import NachweisArt, PrueflaufStatus
from helpers import in_memory_abschluss_persistenz
from adapters.persistence.in_memory import (
    InMemoryKatalogRepository,
    InMemoryProtokollRepository,
    InMemoryPrueflaufRepository,
)
from application.pruefausfuehrung.komponente_erfassen import KomponenteErfassen
from application.pruefausfuehrung.nachweis_erfassen import NachweisErfassen
from application.pruefausfuehrung.pruefung_abschliessen import PruefungAbschliessen
from application.pruefausfuehrung.pruefung_starten import PruefungStarten
from application.pruefausfuehrung.schritt_beurteilen import SchrittBeurteilen


def _fixture_version(*, mit_sollbestueckung: bool = True) -> ProduktdefinitionsVersion:
    return ProduktdefinitionsVersion(
        version_id="ver-1",
        produktdefinition_id="pd-1",
        produktkodierung="1234567890",
        prozedur_schritte=(
            MaterialisierterProzedurSchritt(
                schritt_id="schritt-a",
                vorlage_id="vorlage-a",
                ist_pflicht=True,
                reihenfolge=1,
                sollvorgaben={"spannung": {"min": 220, "max": 240}},
            ),
            MaterialisierterProzedurSchritt(
                schritt_id="schritt-b",
                vorlage_id="vorlage-b",
                ist_pflicht=False,
                reihenfolge=2,
            ),
        ),
        sollbestueckung=("mainboard",) if mit_sollbestueckung else (),
    )


def _setup():
    katalog = InMemoryKatalogRepository()
    katalog.register_aktive_version(_fixture_version())
    return katalog, InMemoryPrueflaufRepository(), InMemoryProtokollRepository()


def test_vertical_slice_gueltiger_lauf_mit_protokoll():
    katalog, prueflauf_repo, protokoll_repo = _setup()

    prueflauf = PruefungStarten(katalog, prueflauf_repo).execute(
        produktkodierung="1234567890",
        pruefobjekt_kennung="GER-999",
        pruefer_id="pruefer-1",
    )
    KomponenteErfassen(prueflauf_repo).execute(prueflauf.prueflauf_id, "mainboard", "MB-1")

    NachweisErfassen(prueflauf_repo).execute(
        prueflauf.prueflauf_id, "schritt-a", NachweisArt.MESSWERT, {"spannung": 230}
    )
    SchrittBeurteilen(katalog, prueflauf_repo).execute(prueflauf.prueflauf_id, "schritt-a")

    abgeschlossen, snapshot = PruefungAbschliessen(
        katalog, prueflauf_repo, in_memory_abschluss_persistenz(prueflauf_repo, protokoll_repo)
    ).execute(prueflauf.prueflauf_id)

    assert abgeschlossen.ist_gueltig()
    assert snapshot.version_id == "ver-1"
    assert protokoll_repo.get_by_prueflauf(prueflauf.prueflauf_id) is not None


def test_vertical_slice_ungueltiger_lauf_erhaelt_trotzdem_protokoll():
    katalog, prueflauf_repo, protokoll_repo = _setup()

    prueflauf = PruefungStarten(katalog, prueflauf_repo).execute(
        produktkodierung="1234567890",
        pruefobjekt_kennung="GER-999",
        pruefer_id="pruefer-1",
    )
    KomponenteErfassen(prueflauf_repo).execute(prueflauf.prueflauf_id, "mainboard", "MB-1")

    NachweisErfassen(prueflauf_repo).execute(
        prueflauf.prueflauf_id, "schritt-a", NachweisArt.MESSWERT, {"spannung": 999}
    )
    SchrittBeurteilen(katalog, prueflauf_repo).execute(prueflauf.prueflauf_id, "schritt-a")

    abgeschlossen, snapshot = PruefungAbschliessen(
        katalog, prueflauf_repo, in_memory_abschluss_persistenz(prueflauf_repo, protokoll_repo)
    ).execute(prueflauf.prueflauf_id)

    assert abgeschlossen.status == PrueflaufStatus.ABGESCHLOSSEN_UNGUELTIG
    assert snapshot.ist_gueltig is False
    assert protokoll_repo.get_by_prueflauf(prueflauf.prueflauf_id) is not None


def test_vertical_slice_fehlende_bestueckung_ungueltig():
    katalog, prueflauf_repo, protokoll_repo = _setup()

    prueflauf = PruefungStarten(katalog, prueflauf_repo).execute(
        produktkodierung="1234567890",
        pruefobjekt_kennung="GER-999",
        pruefer_id="pruefer-1",
    )
    NachweisErfassen(prueflauf_repo).execute(
        prueflauf.prueflauf_id, "schritt-a", NachweisArt.MESSWERT, {"spannung": 230}
    )
    SchrittBeurteilen(katalog, prueflauf_repo).execute(prueflauf.prueflauf_id, "schritt-a")

    abgeschlossen, snapshot = PruefungAbschliessen(
        katalog, prueflauf_repo, in_memory_abschluss_persistenz(prueflauf_repo, protokoll_repo)
    ).execute(prueflauf.prueflauf_id)

    assert not abgeschlossen.ist_gueltig()
    assert snapshot.fehlende_sollbestueckung == ("mainboard",)
