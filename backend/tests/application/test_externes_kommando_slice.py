"""Vertical Slice — Externes Kommando via Simulation-Adapter."""

from domain.katalog.version import MaterialisierterProzedurSchritt, ProduktdefinitionsVersion
from domain.pruefausfuehrung.kommando_ausfuehrung import ExternesKommandoAntwort
from domain.pruefausfuehrung.prueflauf import NachweisArt
from helpers import in_memory_abschluss_persistenz
from adapters.persistence.in_memory import (
    InMemoryKatalogRepository,
    InMemoryProtokollRepository,
    InMemoryPrueflaufRepository,
)
from adapters.simulation.externes_kommando import SimuliertesExternesKommandoPort
from application.pruefausfuehrung.externes_kommando_ausfuehren import ExternesKommandoAusfuehren
from application.pruefausfuehrung.pruefung_abschliessen import PruefungAbschliessen
from application.pruefausfuehrung.pruefung_starten import PruefungStarten
from application.pruefausfuehrung.schritt_beurteilen import SchrittBeurteilen


def _setup_katalog() -> InMemoryKatalogRepository:
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
        )
    )
    return katalog


def test_externes_kommando_simulation_bis_gueltiger_lauf():
    katalog = _setup_katalog()
    prueflauf_repo = InMemoryPrueflaufRepository()
    protokoll_repo = InMemoryProtokollRepository()
    kommando_port = SimuliertesExternesKommandoPort(
        {
            "READ_VOLTAGE": ExternesKommandoAntwort(
                rohdaten="RAW:230",
                extrahierte_werte={"spannung": 230},
            ),
        }
    )

    prueflauf = PruefungStarten(katalog, prueflauf_repo).execute(
        produktkodierung="1234567890",
        pruefobjekt_kennung="GER-500",
        pruefer_id="pruefer-1",
    )

    nachweise = ExternesKommandoAusfuehren(prueflauf_repo, kommando_port).execute(
        prueflauf.prueflauf_id,
        "schritt-a",
        "READ_VOLTAGE",
    )

    assert len(nachweise) == 2
    assert nachweise[0].art == NachweisArt.ROHANTWORT
    assert nachweise[0].ist_automatisch is True
    assert nachweise[1].art == NachweisArt.EXTRAHIERTER_WERT
    assert nachweise[1].bezug_nachweis_id == nachweise[0].nachweis_id

    SchrittBeurteilen(katalog, prueflauf_repo).execute(prueflauf.prueflauf_id, "schritt-a")
    abgeschlossen, snapshot = PruefungAbschliessen(
        katalog, prueflauf_repo, in_memory_abschluss_persistenz(prueflauf_repo, protokoll_repo)
    ).execute(prueflauf.prueflauf_id)

    assert abgeschlossen.ist_gueltig()
    assert snapshot.ist_gueltig is True
