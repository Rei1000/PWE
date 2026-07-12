"""Vertical Slice — Protokoll abschließen und PDF erzeugen."""

from helpers import in_memory_abschluss_persistenz
from domain.katalog.version import MaterialisierterProzedurSchritt, ProduktdefinitionsVersion
from domain.pruefausfuehrung.prueflauf import NachweisArt
from adapters.pdf.protokoll_erzeugung import PdfProtokollErzeugungAdapter
from adapters.persistence.in_memory import (
    InMemoryKatalogRepository,
    InMemoryProtokollRepository,
    InMemoryPrueflaufRepository,
)
from application.protokoll.erzeugen import ProtokollErzeugen
from application.pruefausfuehrung.komponente_erfassen import KomponenteErfassen
from application.pruefausfuehrung.nachweis_erfassen import NachweisErfassen
from application.pruefausfuehrung.pruefung_abschliessen import PruefungAbschliessen
from application.pruefausfuehrung.pruefung_starten import PruefungStarten
from application.pruefausfuehrung.schritt_beurteilen import SchrittBeurteilen


def test_protokoll_pdf_slice_nach_laufabschluss():
    katalog = InMemoryKatalogRepository()
    katalog.register_aktive_version(
        ProduktdefinitionsVersion(
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
            ),
            sollbestueckung=("mainboard",),
        )
    )
    prueflauf_repo = InMemoryPrueflaufRepository()
    protokoll_repo = InMemoryProtokollRepository()

    prueflauf = PruefungStarten(katalog, prueflauf_repo).execute(
        produktkodierung="1234567890",
        pruefobjekt_kennung="GER-700",
        pruefer_id="pruefer-1",
    )
    KomponenteErfassen(prueflauf_repo).execute(prueflauf.prueflauf_id, "mainboard", "MB-7")
    NachweisErfassen(prueflauf_repo).execute(
        prueflauf.prueflauf_id, "schritt-a", NachweisArt.MESSWERT, {"spannung": 230}
    )
    SchrittBeurteilen(katalog, prueflauf_repo).execute(prueflauf.prueflauf_id, "schritt-a")
    PruefungAbschliessen(
        katalog, prueflauf_repo, in_memory_abschluss_persistenz(prueflauf_repo, protokoll_repo)
    ).execute(prueflauf.prueflauf_id)

    dokument = ProtokollErzeugen(protokoll_repo, PdfProtokollErzeugungAdapter()).execute(
        prueflauf.prueflauf_id
    )

    assert dokument.inhalt.startswith(b"%PDF")
    assert dokument.dateiname.endswith(".pdf")
