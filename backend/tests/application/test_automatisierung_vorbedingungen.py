"""Vorbedingungs-Tests — kein Port-Aufruf vor Domain-Validierung (Gate 7.3e P0)."""

from __future__ import annotations

import pytest

from adapters.persistence.in_memory import InMemoryKatalogRepository, InMemoryPrueflaufRepository
from application.pruefausfuehrung.externes_kommando_ausfuehren import ExternesKommandoAusfuehren
from application.pruefausfuehrung.pruefung_abschliessen import PruefungAbschliessen
from application.pruefausfuehrung.pruefung_starten import PruefungStarten
from application.pruefausfuehrung.routine_ausfuehren import RoutineAusfuehren
from domain.katalog.errors import MaterialisierteAutomatisierungInkonsistent
from domain.katalog.externes_kommando import MaterialisiertesExternesKommando
from domain.katalog.routine import (
    MaterialisierteKommandoAktion,
    MaterialisierteRoutine,
    MaterialisierteRoutineHerkunft,
)
from domain.katalog.version import MaterialisierterProzedurSchritt, ProduktdefinitionsVersion
from domain.pruefausfuehrung.errors import (
    KeineAutomatisierungAmSchritt,
    KommandoNichtFreigegeben,
    MaterialisierterProzedurSchrittNichtGefunden,
)
from domain.pruefausfuehrung.kommando_ausfuehrung import ExternesKommandoAntwort
from domain.shared.errors import InvariantViolation
from helpers import (
    CountingKommandoPort,
    CountingPrueflaufRepository,
    in_memory_abschluss_persistenz,
)
from adapters.persistence.in_memory import InMemoryProtokollRepository

KOMMANDO_ID = "cmd-vorbedingung"
KOMMANDOCODE = "READ_VOLTAGE"


def _katalog_mit_kommando(katalog: InMemoryKatalogRepository) -> None:
    katalog.register_aktive_version(
        ProduktdefinitionsVersion(
            version_id="ver-vb",
            produktdefinition_id="pd-vb",
            produktkodierung="1234567890",
            prozedur_schritte=(
                MaterialisierterProzedurSchritt(
                    schritt_id="schritt-a",
                    vorlage_id="vorlage-a",
                    ist_pflicht=True,
                    reihenfolge=1,
                    externes_kommando=MaterialisiertesExternesKommando(
                        kommando_id=KOMMANDO_ID,
                        bezeichnung="Spannung",
                        kommandocode=KOMMANDOCODE,
                    ),
                ),
            ),
        )
    )


def _offenen_prueflauf(
    katalog: InMemoryKatalogRepository,
    prueflauf_repo: InMemoryPrueflaufRepository,
):
    return PruefungStarten(katalog, prueflauf_repo).execute(
        produktkodierung="1234567890",
        pruefobjekt_kennung="GER-VB",
        pruefer_id="pruefer-1",
    )


def _abgeschlossenen_prueflauf(
    katalog: InMemoryKatalogRepository,
    prueflauf_repo: InMemoryPrueflaufRepository,
):
    prueflauf = _offenen_prueflauf(katalog, prueflauf_repo)
    protokoll_repo = InMemoryProtokollRepository()
    PruefungAbschliessen(
        katalog, prueflauf_repo, in_memory_abschluss_persistenz(prueflauf_repo, protokoll_repo)
    ).execute(prueflauf.prueflauf_id)
    return prueflauf


def test_einzelkommando_abgeschlossener_prueflauf_ruft_port_nicht_auf():
    katalog = InMemoryKatalogRepository()
    _katalog_mit_kommando(katalog)
    inner_repo = InMemoryPrueflaufRepository()
    prueflauf_repo = CountingPrueflaufRepository(inner_repo)
    prueflauf = _abgeschlossenen_prueflauf(katalog, inner_repo)
    port = CountingKommandoPort(
        antworten={
            KOMMANDOCODE: ExternesKommandoAntwort(
                rohdaten="RAW:230",
                extrahierte_werte={"spannung": 230},
            ),
        }
    )

    with pytest.raises(InvariantViolation):
        ExternesKommandoAusfuehren(katalog, prueflauf_repo, port).execute(
            prueflauf.prueflauf_id, "schritt-a", KOMMANDO_ID
        )

    assert port.ausfuehren_count == 0
    assert prueflauf_repo.save_count == 0
    reloaded = inner_repo.get(prueflauf.prueflauf_id)
    assert len(reloaded.durchfuehrungen["schritt-a"].nachweise) == 0


def test_routine_abgeschlossener_prueflauf_ruft_port_nicht_auf():
    katalog = InMemoryKatalogRepository()
    _katalog_mit_kommando(katalog)
    inner_repo = InMemoryPrueflaufRepository()
    prueflauf_repo = CountingPrueflaufRepository(inner_repo)
    prueflauf = _abgeschlossenen_prueflauf(katalog, inner_repo)
    port = CountingKommandoPort(
        antworten={
            KOMMANDOCODE: ExternesKommandoAntwort(
                rohdaten="RAW:230",
                extrahierte_werte={"spannung": 230},
            ),
        }
    )

    with pytest.raises(InvariantViolation):
        RoutineAusfuehren(katalog, prueflauf_repo, port).execute(
            prueflauf.prueflauf_id, "schritt-a"
        )

    assert port.ausfuehren_count == 0
    assert prueflauf_repo.save_count == 0


def test_einzelkommando_falsche_kommando_id_ruft_port_nicht_auf():
    katalog = InMemoryKatalogRepository()
    _katalog_mit_kommando(katalog)
    prueflauf_repo = InMemoryPrueflaufRepository()
    prueflauf = _offenen_prueflauf(katalog, prueflauf_repo)
    port = CountingKommandoPort()

    with pytest.raises(KommandoNichtFreigegeben):
        ExternesKommandoAusfuehren(katalog, prueflauf_repo, port).execute(
            prueflauf.prueflauf_id, "schritt-a", "falsche-id"
        )

    assert port.ausfuehren_count == 0


def test_routine_schritt_nicht_gefunden_ruft_port_nicht_auf():
    katalog = InMemoryKatalogRepository()
    _katalog_mit_kommando(katalog)
    prueflauf_repo = InMemoryPrueflaufRepository()
    prueflauf = _offenen_prueflauf(katalog, prueflauf_repo)
    port = CountingKommandoPort()

    with pytest.raises(MaterialisierterProzedurSchrittNichtGefunden):
        RoutineAusfuehren(katalog, prueflauf_repo, port).execute(
            prueflauf.prueflauf_id, "fehlend"
        )

    assert port.ausfuehren_count == 0


def test_routine_keine_automatisierung_ruft_port_nicht_auf():
    katalog = InMemoryKatalogRepository()
    katalog.register_aktive_version(
        ProduktdefinitionsVersion(
            version_id="ver-manuell",
            produktdefinition_id="pd-manuell",
            produktkodierung="9999999999",
            prozedur_schritte=(
                MaterialisierterProzedurSchritt(
                    schritt_id="schritt-a",
                    vorlage_id="vorlage-a",
                    ist_pflicht=True,
                    reihenfolge=1,
                ),
            ),
        )
    )
    prueflauf_repo = InMemoryPrueflaufRepository()
    prueflauf = PruefungStarten(katalog, prueflauf_repo).execute(
        produktkodierung="9999999999",
        pruefobjekt_kennung="GER-MAN",
        pruefer_id="pruefer-1",
    )
    port = CountingKommandoPort()

    with pytest.raises(KeineAutomatisierungAmSchritt):
        RoutineAusfuehren(katalog, prueflauf_repo, port).execute(
            prueflauf.prueflauf_id, "schritt-a"
        )

    assert port.ausfuehren_count == 0


def test_routine_inkonsistente_materialisierung_ruft_port_nicht_auf():
    mr = MaterialisierteRoutine(
        herkunft=MaterialisierteRoutineHerkunft.EINZELKOMMANDO,
        routine_id=None,
        bezeichnung="A",
        aktionen=(
            MaterialisierteKommandoAktion(
                position=1,
                kommando_id="k1",
                bezeichnung="A",
                kommandocode="A",
            ),
        ),
    )
    katalog = InMemoryKatalogRepository()
    katalog.register_aktive_version(
        ProduktdefinitionsVersion(
            version_id="ver-inkonsistent",
            produktdefinition_id="pd-inkonsistent",
            produktkodierung="8888888888",
            prozedur_schritte=(
                MaterialisierterProzedurSchritt(
                    schritt_id="schritt-a",
                    vorlage_id="vorlage-a",
                    ist_pflicht=True,
                    reihenfolge=1,
                    materialisierte_routine=mr,
                    externes_kommando=MaterialisiertesExternesKommando(
                        kommando_id="k1",
                        bezeichnung="X",
                        kommandocode="DIFF",
                    ),
                ),
            ),
        )
    )
    prueflauf_repo = InMemoryPrueflaufRepository()
    prueflauf = PruefungStarten(katalog, prueflauf_repo).execute(
        produktkodierung="8888888888",
        pruefobjekt_kennung="GER-INK",
        pruefer_id="pruefer-1",
    )
    port = CountingKommandoPort()

    with pytest.raises(MaterialisierteAutomatisierungInkonsistent):
        RoutineAusfuehren(katalog, prueflauf_repo, port).execute(
            prueflauf.prueflauf_id, "schritt-a"
        )

    assert port.ausfuehren_count == 0


def test_einzelkommando_offener_lauf_ruft_port_genau_einmal():
    katalog = InMemoryKatalogRepository()
    _katalog_mit_kommando(katalog)
    prueflauf_repo = InMemoryPrueflaufRepository()
    prueflauf = _offenen_prueflauf(katalog, prueflauf_repo)
    port = CountingKommandoPort(
        antworten={
            KOMMANDOCODE: ExternesKommandoAntwort(
                rohdaten="RAW:230",
                extrahierte_werte={"spannung": 230},
            ),
        }
    )

    ExternesKommandoAusfuehren(katalog, prueflauf_repo, port).execute(
        prueflauf.prueflauf_id, "schritt-a", KOMMANDO_ID
    )

    assert port.ausfuehren_count == 1


def test_routine_zwei_aktionen_ruft_port_zweimal_bei_erfolg():
    katalog = InMemoryKatalogRepository()
    katalog.register_aktive_version(
        ProduktdefinitionsVersion(
            version_id="ver-zwei",
            produktdefinition_id="pd-zwei",
            produktkodierung="7777777777",
            prozedur_schritte=(
                MaterialisierterProzedurSchritt(
                    schritt_id="schritt-a",
                    vorlage_id="vorlage-a",
                    ist_pflicht=True,
                    reihenfolge=1,
                    materialisierte_routine=MaterialisierteRoutine(
                        herkunft=MaterialisierteRoutineHerkunft.BIBLIOTHEK,
                        routine_id="r-zwei",
                        bezeichnung="Zwei",
                        aktionen=(
                            MaterialisierteKommandoAktion(
                                position=1,
                                kommando_id="k1",
                                bezeichnung="A",
                                kommandocode="CMD1",
                            ),
                            MaterialisierteKommandoAktion(
                                position=2,
                                kommando_id="k2",
                                bezeichnung="B",
                                kommandocode="CMD2",
                            ),
                        ),
                    ),
                ),
            ),
        )
    )
    prueflauf_repo = InMemoryPrueflaufRepository()
    prueflauf = PruefungStarten(katalog, prueflauf_repo).execute(
        produktkodierung="7777777777",
        pruefobjekt_kennung="GER-ZWEI",
        pruefer_id="pruefer-1",
    )
    port = CountingKommandoPort(
        antworten={
            "CMD1": ExternesKommandoAntwort(rohdaten="RAW:1", extrahierte_werte={"a": 1}),
            "CMD2": ExternesKommandoAntwort(rohdaten="RAW:2", extrahierte_werte={"b": 2}),
        }
    )

    ergebnis = RoutineAusfuehren(katalog, prueflauf_repo, port).execute(
        prueflauf.prueflauf_id, "schritt-a"
    )

    assert ergebnis.fehlgeschlagen is False
    assert port.ausfuehren_count == 2


def test_routine_stop_on_first_failure_ruft_nur_erste_aktion():
    katalog = InMemoryKatalogRepository()
    katalog.register_aktive_version(
        ProduktdefinitionsVersion(
            version_id="ver-stop",
            produktdefinition_id="pd-stop",
            produktkodierung="6666666666",
            prozedur_schritte=(
                MaterialisierterProzedurSchritt(
                    schritt_id="schritt-a",
                    vorlage_id="vorlage-a",
                    ist_pflicht=True,
                    reihenfolge=1,
                    materialisierte_routine=MaterialisierteRoutine(
                        herkunft=MaterialisierteRoutineHerkunft.BIBLIOTHEK,
                        routine_id="r-stop",
                        bezeichnung="Stop",
                        aktionen=(
                            MaterialisierteKommandoAktion(
                                position=1,
                                kommando_id="k1",
                                bezeichnung="A",
                                kommandocode="CMD1",
                            ),
                            MaterialisierteKommandoAktion(
                                position=2,
                                kommando_id="k2",
                                bezeichnung="B",
                                kommandocode="CMD2",
                            ),
                        ),
                    ),
                ),
            ),
        )
    )
    prueflauf_repo = InMemoryPrueflaufRepository()
    prueflauf = PruefungStarten(katalog, prueflauf_repo).execute(
        produktkodierung="6666666666",
        pruefobjekt_kennung="GER-STOP",
        pruefer_id="pruefer-1",
    )
    port = CountingKommandoPort(
        antworten={
            "CMD1": ExternesKommandoAntwort(rohdaten="RAW:1", extrahierte_werte={"a": 1}),
        }
    )

    ergebnis = RoutineAusfuehren(katalog, prueflauf_repo, port).execute(
        prueflauf.prueflauf_id, "schritt-a"
    )

    assert ergebnis.fehlgeschlagen is True
    assert port.ausfuehren_count == 2
