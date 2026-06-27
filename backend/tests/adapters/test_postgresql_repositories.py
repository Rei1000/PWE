"""PostgreSQL-Repository-Integrationstests."""

import pytest

from domain.katalog.produktdefinition import ProzedurSchrittEntwurf
from domain.pruefausfuehrung.prueflauf import NachweisArt
from application.katalog.entwurf_anlegen import EntwurfAnlegen
from application.katalog.veroeffentlichen import ProduktdefinitionVeroeffentlichen
from application.pruefausfuehrung.komponente_erfassen import KomponenteErfassen
from application.pruefausfuehrung.nachweis_erfassen import NachweisErfassen
from application.pruefausfuehrung.pruefung_abschliessen import PruefungAbschliessen
from application.pruefausfuehrung.pruefung_starten import PruefungStarten
from application.pruefausfuehrung.schritt_beurteilen import SchrittBeurteilen

pytestmark = pytest.mark.postgresql


def test_postgresql_katalog_version_immutability(pg_repos):
    katalog, _, _ = pg_repos

    entwurf = EntwurfAnlegen(katalog).execute(
        produktkodierung="5555555555",
        prozedur_schritte=(
            ProzedurSchrittEntwurf(
                schritt_id="schritt-a",
                vorlage_id="vorlage-a",
                ist_pflicht=True,
                reihenfolge=1,
                sollvorgaben={"spannung": {"min": 220, "max": 240}},
            ),
        ),
    )
    v1 = ProduktdefinitionVeroeffentlichen(katalog).execute(entwurf.produktdefinition_id)

    entwurf.prozedur_schritte[0].sollvorgaben = {"spannung": {"min": 100, "max": 110}}
    katalog.save_entwurf(entwurf)
    v2 = ProduktdefinitionVeroeffentlichen(katalog).execute(entwurf.produktdefinition_id)

    stored_v1 = katalog.get_version(v1.version_id)
    assert stored_v1 is not None
    assert stored_v1.sollbestueckung == v1.sollbestueckung
    schritt = stored_v1.schritt_by_id("schritt-a")
    assert schritt is not None
    assert schritt.sollvorgaben["spannung"]["min"] == 220

    aktiv = katalog.get_aktive_version_fuer_kodierung("5555555555")
    assert aktiv is not None
    assert aktiv.version_id == v2.version_id


def test_postgresql_end_to_end_prueflauf(pg_repos):
    katalog, prueflauf_repo, protokoll_repo = pg_repos

    entwurf = EntwurfAnlegen(katalog).execute(
        produktkodierung="6666666666",
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
    ProduktdefinitionVeroeffentlichen(katalog).execute(entwurf.produktdefinition_id)

    prueflauf = PruefungStarten(katalog, prueflauf_repo).execute(
        produktkodierung="6666666666",
        pruefobjekt_kennung="GER-300",
        pruefer_id="pruefer-1",
    )
    assert prueflauf_repo.get(prueflauf.prueflauf_id) is not None

    KomponenteErfassen(prueflauf_repo).execute(prueflauf.prueflauf_id, "mainboard", "MB-9")
    NachweisErfassen(prueflauf_repo).execute(
        prueflauf.prueflauf_id, "schritt-a", NachweisArt.MESSWERT, {"spannung": 230}
    )
    SchrittBeurteilen(katalog, prueflauf_repo).execute(prueflauf.prueflauf_id, "schritt-a")

    abgeschlossen, snapshot = PruefungAbschliessen(
        katalog, prueflauf_repo, protokoll_repo
    ).execute(prueflauf.prueflauf_id)

    reloaded = prueflauf_repo.get(prueflauf.prueflauf_id)
    assert reloaded is not None
    assert reloaded.ist_gueltig() == abgeschlossen.ist_gueltig()
    assert protokoll_repo.get_by_prueflauf(prueflauf.prueflauf_id) == snapshot
