"""Application-Tests — ExternesKommandoAusfuehren (Gate 7.3b)."""

import pytest

from adapters.persistence.in_memory import (
    InMemoryBibliothekRepository,
    InMemoryKatalogRepository,
    InMemoryPrueflaufRepository,
)
from adapters.simulation.externes_kommando import SimuliertesExternesKommandoPort
from application.katalog.entwurf_anlegen import EntwurfAnlegen
from application.katalog.externes_kommando_anlegen import ExternesKommandoAnlegen
from application.katalog.kommando_zuweisen import KommandoProzedurSchrittZuweisen
from application.katalog.veroeffentlichen import ProduktdefinitionVeroeffentlichen
from application.pruefausfuehrung.externes_kommando_ausfuehren import ExternesKommandoAusfuehren
from application.pruefausfuehrung.pruefung_abschliessen import PruefungAbschliessen
from application.pruefausfuehrung.pruefung_starten import PruefungStarten
from domain.pruefausfuehrung.errors import MaterialisierterProzedurSchrittNichtGefunden
from domain.katalog.externes_kommando import ExternesKommando, MaterialisiertesExternesKommando
from domain.katalog.produktdefinition import ProzedurSchrittEntwurf
from domain.katalog.version import MaterialisierterProzedurSchritt, ProduktdefinitionsVersion
from domain.pruefausfuehrung.errors import (
    ExternesKommandoAdapterFehler,
    KommandoNichtFreigegeben,
    PrueflaufNichtGefunden,
)
from domain.pruefausfuehrung.kommando_ausfuehrung import ExternesKommandoAntwort
from domain.pruefausfuehrung.prueflauf import NachweisArt
from domain.shared.errors import InvariantViolation
from helpers import in_memory_abschluss_persistenz
from adapters.persistence.in_memory import InMemoryProtokollRepository

KOMMANDO_ID = "cmd-read-voltage"
KOMMANDOCODE = "READ_VOLTAGE"


def _katalog_mit_kommando() -> InMemoryKatalogRepository:
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
                    externes_kommando=MaterialisiertesExternesKommando(
                        kommando_id=KOMMANDO_ID,
                        bezeichnung="Spannung messen",
                        kommandocode=KOMMANDOCODE,
                    ),
                ),
            ),
        )
    )
    return katalog


def _simulation_port() -> SimuliertesExternesKommandoPort:
    return SimuliertesExternesKommandoPort(
        {
            KOMMANDOCODE: ExternesKommandoAntwort(
                rohdaten="RAW:230",
                extrahierte_werte={"spannung": 230},
            ),
        }
    )


def test_materialisiertes_kommando_wird_ausgefuehrt():
    katalog = _katalog_mit_kommando()
    prueflauf_repo = InMemoryPrueflaufRepository()
    prueflauf = PruefungStarten(katalog, prueflauf_repo).execute(
        produktkodierung="1234567890",
        pruefobjekt_kennung="GER-1",
        pruefer_id="pruefer-1",
    )

    nachweise = ExternesKommandoAusfuehren(
        katalog, prueflauf_repo, _simulation_port()
    ).execute(prueflauf.prueflauf_id, "schritt-a", KOMMANDO_ID)

    assert len(nachweise) == 2
    assert nachweise[0].art == NachweisArt.ROHANTWORT
    assert nachweise[0].payload["kommando_id"] == KOMMANDO_ID
    assert nachweise[0].payload["kommandocode"] == KOMMANDOCODE
    assert nachweise[1].art == NachweisArt.EXTRAHIERTER_WERT
    assert nachweise[1].bezug_nachweis_id == nachweise[0].nachweis_id
    assert nachweise[1].payload["kommando_id"] == KOMMANDO_ID


def test_falsche_kommando_id_fuer_schritt():
    katalog = _katalog_mit_kommando()
    prueflauf_repo = InMemoryPrueflaufRepository()
    prueflauf = PruefungStarten(katalog, prueflauf_repo).execute(
        produktkodierung="1234567890",
        pruefobjekt_kennung="GER-1",
        pruefer_id="pruefer-1",
    )

    with pytest.raises(KommandoNichtFreigegeben):
        ExternesKommandoAusfuehren(
            katalog, prueflauf_repo, _simulation_port()
        ).execute(prueflauf.prueflauf_id, "schritt-a", "falsche-id")


def test_abgeschlossener_prueflauf_lehnt_ausfuehrung_ab():
    katalog = _katalog_mit_kommando()
    prueflauf_repo = InMemoryPrueflaufRepository()
    protokoll_repo = InMemoryProtokollRepository()
    prueflauf = PruefungStarten(katalog, prueflauf_repo).execute(
        produktkodierung="1234567890",
        pruefobjekt_kennung="GER-1",
        pruefer_id="pruefer-1",
    )
    PruefungAbschliessen(
        katalog, prueflauf_repo, in_memory_abschluss_persistenz(prueflauf_repo, protokoll_repo)
    ).execute(prueflauf.prueflauf_id)

    with pytest.raises(InvariantViolation):
        ExternesKommandoAusfuehren(
            katalog, prueflauf_repo, _simulation_port()
        ).execute(prueflauf.prueflauf_id, "schritt-a", KOMMANDO_ID)


def test_adapterfehler_wird_fachlich_gemeldet():
    katalog = _katalog_mit_kommando()
    prueflauf_repo = InMemoryPrueflaufRepository()
    prueflauf = PruefungStarten(katalog, prueflauf_repo).execute(
        produktkodierung="1234567890",
        pruefobjekt_kennung="GER-1",
        pruefer_id="pruefer-1",
    )

    with pytest.raises(ExternesKommandoAdapterFehler):
        ExternesKommandoAusfuehren(
            katalog, prueflauf_repo, SimuliertesExternesKommandoPort()
        ).execute(prueflauf.prueflauf_id, "schritt-a", KOMMANDO_ID)


def test_prueflauf_nicht_gefunden():
    katalog = _katalog_mit_kommando()
    prueflauf_repo = InMemoryPrueflaufRepository()

    with pytest.raises(PrueflaufNichtGefunden):
        ExternesKommandoAusfuehren(
            katalog, prueflauf_repo, _simulation_port()
        ).execute("fehlend", "schritt-a", KOMMANDO_ID)


def test_schritt_nicht_gefunden():
    katalog = _katalog_mit_kommando()
    prueflauf_repo = InMemoryPrueflaufRepository()
    prueflauf = PruefungStarten(katalog, prueflauf_repo).execute(
        produktkodierung="1234567890",
        pruefobjekt_kennung="GER-1",
        pruefer_id="pruefer-1",
    )

    with pytest.raises(MaterialisierterProzedurSchrittNichtGefunden):
        ExternesKommandoAusfuehren(
            katalog, prueflauf_repo, _simulation_port()
        ).execute(prueflauf.prueflauf_id, "fehlend", KOMMANDO_ID)


def test_bibliotheksaenderung_beeinflusst_ausfuehrung_nicht():
    katalog = InMemoryKatalogRepository()
    bibliothek = InMemoryBibliothekRepository()
    prueflauf_repo = InMemoryPrueflaufRepository()

    kommando = ExternesKommandoAnlegen(bibliothek).execute(
        bezeichnung="Spannung",
        kommandocode=KOMMANDOCODE,
    )
    entwurf = EntwurfAnlegen(katalog).execute(
        produktkodierung="9999999991",
        prozedur_schritte=(
            ProzedurSchrittEntwurf(
                schritt_id="schritt-a",
                vorlage_id="vorlage-a",
                ist_pflicht=True,
                reihenfolge=1,
            ),
        ),
    )
    KommandoProzedurSchrittZuweisen(katalog, bibliothek).execute(
        entwurf.produktdefinition_id,
        "schritt-a",
        kommando.kommando_id,
    )
    ProduktdefinitionVeroeffentlichen(katalog, bibliothek).execute(entwurf.produktdefinition_id)

    bibliothek.save_externes_kommando(
        ExternesKommando(
            kommando_id=kommando.kommando_id,
            bezeichnung="Geändert",
            kommandocode="CHANGED_CODE",
        )
    )

    port = SimuliertesExternesKommandoPort(
        {
            KOMMANDOCODE: ExternesKommandoAntwort(
                rohdaten="RAW:230",
                extrahierte_werte={"spannung": 230},
            ),
            "CHANGED_CODE": ExternesKommandoAntwort(
                rohdaten="SHOULD-NOT-USE",
                extrahierte_werte={"spannung": 999},
            ),
        }
    )

    prueflauf = PruefungStarten(katalog, prueflauf_repo).execute(
        produktkodierung="9999999991",
        pruefobjekt_kennung="GER-2",
        pruefer_id="pruefer-1",
    )
    nachweise = ExternesKommandoAusfuehren(katalog, prueflauf_repo, port).execute(
        prueflauf.prueflauf_id,
        "schritt-a",
        kommando.kommando_id,
    )

    assert nachweise[0].payload["kommandocode"] == KOMMANDOCODE
    assert nachweise[0].payload["rohdaten"] == "RAW:230"
