"""Vertical Slice — Externes Kommando via COM-Adapter."""

from domain.katalog.version import MaterialisierterProzedurSchritt, ProduktdefinitionsVersion
from adapters.com.externes_kommando import ComExternesKommandoPort
from adapters.com.in_memory_transport import InMemorySeriellerTransport
from helpers import in_memory_abschluss_persistenz
from adapters.persistence.in_memory import (
    InMemoryKatalogRepository,
    InMemoryProtokollRepository,
    InMemoryPrueflaufRepository,
)
from application.pruefausfuehrung.externes_kommando_ausfuehren import ExternesKommandoAusfuehren
from application.pruefausfuehrung.pruefung_abschliessen import PruefungAbschliessen
from application.pruefausfuehrung.pruefung_starten import PruefungStarten
from application.pruefausfuehrung.schritt_beurteilen import SchrittBeurteilen
from domain.pruefausfuehrung.prueflauf import NachweisArt


def test_com_adapter_slice_bis_gueltiger_lauf():
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
    prueflauf_repo = InMemoryPrueflaufRepository()
    protokoll_repo = InMemoryProtokollRepository()
    transport = InMemorySeriellerTransport({"READ_VOLTAGE": b"OK spannung=230"})
    kommando_port = ComExternesKommandoPort(transport)

    prueflauf = PruefungStarten(katalog, prueflauf_repo).execute(
        produktkodierung="1234567890",
        pruefobjekt_kennung="GER-600",
        pruefer_id="pruefer-1",
    )

    nachweise = ExternesKommandoAusfuehren(prueflauf_repo, kommando_port).execute(
        prueflauf.prueflauf_id,
        "schritt-a",
        "READ_VOLTAGE",
    )

    assert nachweise[0].art == NachweisArt.ROHANTWORT
    assert nachweise[1].art == NachweisArt.EXTRAHIERTER_WERT

    SchrittBeurteilen(katalog, prueflauf_repo).execute(prueflauf.prueflauf_id, "schritt-a")
    abgeschlossen, _ = PruefungAbschliessen(
        katalog, prueflauf_repo, in_memory_abschluss_persistenz(prueflauf_repo, protokoll_repo)
    ).execute(prueflauf.prueflauf_id)

    assert abgeschlossen.ist_gueltig()
