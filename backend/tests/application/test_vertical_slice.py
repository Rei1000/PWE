"""Vertical Slice 1 — Katalog + Prüfausführung + Protokoll (In-Memory)."""

from domain.katalog.version import MaterialisierterProzedurSchritt, ProduktdefinitionsVersion
from domain.pruefausfuehrung.prueflauf import BeurteilungErgebnis, NachweisArt
from adapters.persistence.in_memory import (
    InMemoryKatalogRepository,
    InMemoryProtokollRepository,
    InMemoryPrueflaufRepository,
)
from application.pruefausfuehrung.pruefung_abschliessen import PruefungAbschliessen
from application.pruefausfuehrung.pruefung_starten import PruefungStarten


def _fixture_version() -> ProduktdefinitionsVersion:
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
    )


def test_vertical_slice_pruefung_mit_protokollsnapshot():
    katalog = InMemoryKatalogRepository()
    katalog.register_aktive_version(_fixture_version())
    prueflauf_repo = InMemoryPrueflaufRepository()
    protokoll_repo = InMemoryProtokollRepository()

    starten = PruefungStarten(katalog=katalog, prueflauf_repo=prueflauf_repo)
    prueflauf = starten.execute(
        produktkodierung="1234567890",
        pruefobjekt_kennung="GER-999",
        pruefer_id="pruefer-1",
    )

    prueflauf.add_nachweis("schritt-a", NachweisArt.MESSWERT, {"spannung": 230})
    prueflauf.set_beurteilung("schritt-a", BeurteilungErgebnis.BESTANDEN)
    prueflauf_repo.save(prueflauf)

    abschliessen = PruefungAbschliessen(
        katalog=katalog,
        prueflauf_repo=prueflauf_repo,
        protokoll_repo=protokoll_repo,
    )
    abgeschlossen, snapshot = abschliessen.execute(prueflauf.prueflauf_id)

    assert abgeschlossen.ist_gueltig()
    assert snapshot.version_id == "ver-1"
    assert snapshot.pruefobjekt_kennung == "GER-999"
    assert len(snapshot.schritte) == 2
    assert protokoll_repo.get_by_prueflauf(prueflauf.prueflauf_id) is not None
