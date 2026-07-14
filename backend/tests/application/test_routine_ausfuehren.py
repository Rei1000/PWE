"""Application-Tests — RoutineAusfuehren (Gate 7.3e)."""

from __future__ import annotations

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
from application.katalog.routine_anlegen import RoutineAnlegen
from application.katalog.routine_zuweisen import RoutineProzedurSchrittZuweisen
from application.katalog.veroeffentlichen import ProduktdefinitionVeroeffentlichen
from application.pruefausfuehrung.externes_kommando_ausfuehren import ExternesKommandoAusfuehren
from application.pruefausfuehrung.nachweis_erfassen import NachweisErfassen
from application.pruefausfuehrung.pruefung_abschliessen import PruefungAbschliessen
from application.pruefausfuehrung.pruefung_starten import PruefungStarten
from application.pruefausfuehrung.routine_ausfuehren import RoutineAusfuehren
from application.pruefausfuehrung.kommando_ausfuehrung_kern import KommandoFehlerart
from domain.katalog.errors import MaterialisierteAutomatisierungInkonsistent
from domain.katalog.externes_kommando import MaterialisiertesExternesKommando
from domain.katalog.produktdefinition import ProzedurSchrittEntwurf
from domain.katalog.routine import (
    MaterialisierteKommandoAktion,
    MaterialisierteRoutine,
    MaterialisierteRoutineHerkunft,
)
from domain.katalog.version import MaterialisierterProzedurSchritt, ProduktdefinitionsVersion
from domain.pruefausfuehrung.errors import KeineAutomatisierungAmSchritt
from domain.pruefausfuehrung.kommando_ausfuehrung import ExternesKommandoAntwort
from domain.pruefausfuehrung.prueflauf import NachweisArt, Prueflauf
from domain.shared.errors import InvariantViolation
from helpers import in_memory_abschluss_persistenz
from adapters.persistence.in_memory import InMemoryProtokollRepository
from ports.prueflauf_repository import PrueflaufRepository


class CountingPrueflaufRepository(PrueflaufRepository):
    def __init__(self, inner: InMemoryPrueflaufRepository) -> None:
        self._inner = inner
        self.save_count = 0

    def save(self, prueflauf: Prueflauf) -> None:
        self.save_count += 1
        self._inner.save(prueflauf)

    def get(self, prueflauf_id: str) -> Prueflauf | None:
        return self._inner.get(prueflauf_id)


def _katalog_mit_legacy_kommando(
    katalog: InMemoryKatalogRepository,
    *,
    kommando_id: str = "cmd-legacy",
    kommandocode: str = "LEG",
) -> None:
    katalog.register_aktive_version(
        ProduktdefinitionsVersion(
            version_id="ver-legacy",
            produktdefinition_id="pd-legacy",
            produktkodierung="1111111111",
            prozedur_schritte=(
                MaterialisierterProzedurSchritt(
                    schritt_id="schritt-a",
                    vorlage_id="vorlage-a",
                    ist_pflicht=True,
                    reihenfolge=1,
                    externes_kommando=MaterialisiertesExternesKommando(
                        kommando_id=kommando_id,
                        bezeichnung="Legacy",
                        kommandocode=kommandocode,
                    ),
                ),
            ),
        )
    )


def _setup_zweistufige_routine() -> tuple[
    InMemoryKatalogRepository, InMemoryPrueflaufRepository, str, str, str
]:
    katalog = InMemoryKatalogRepository()
    bibliothek = InMemoryBibliothekRepository()
    k1 = ExternesKommandoAnlegen(bibliothek).execute(bezeichnung="A", kommandocode="CMD1")
    k2 = ExternesKommandoAnlegen(bibliothek).execute(bezeichnung="B", kommandocode="CMD2")
    routine = RoutineAnlegen(bibliothek).execute(
        bezeichnung="Zweistufig",
        kommando_ids=(k1.kommando_id, k2.kommando_id),
    )
    entwurf = EntwurfAnlegen(katalog).execute(
        produktkodierung="2222222222",
        prozedur_schritte=(
            ProzedurSchrittEntwurf(
                schritt_id="schritt-a",
                vorlage_id="vorlage-a",
                ist_pflicht=True,
                reihenfolge=1,
            ),
        ),
    )
    RoutineProzedurSchrittZuweisen(katalog, bibliothek).execute(
        entwurf.produktdefinition_id,
        "schritt-a",
        routine.routine_id,
    )
    ProduktdefinitionVeroeffentlichen(katalog, bibliothek).execute(entwurf.produktdefinition_id)
    prueflauf_repo = InMemoryPrueflaufRepository()
    return katalog, prueflauf_repo, k1.kommando_id, k2.kommando_id, routine.routine_id


def test_routine_eine_aktion_happy_path():
    katalog = InMemoryKatalogRepository()
    _katalog_mit_legacy_kommando(katalog)
    prueflauf_repo = InMemoryPrueflaufRepository()
    prueflauf = PruefungStarten(katalog, prueflauf_repo).execute(
        produktkodierung="1111111111",
        pruefobjekt_kennung="GER-1",
        pruefer_id="pruefer-1",
    )
    port = SimuliertesExternesKommandoPort(
        {"LEG": ExternesKommandoAntwort(rohdaten="RAW:1", extrahierte_werte={"x": 1})}
    )
    counting = CountingPrueflaufRepository(prueflauf_repo)

    ergebnis = RoutineAusfuehren(katalog, counting, port).execute(
        prueflauf.prueflauf_id, "schritt-a"
    )

    assert ergebnis.fehlgeschlagen is False
    assert ergebnis.abgebrochen_bei_aktion_position is None
    assert ergebnis.ausgefuehrte_aktionen == 1
    assert len(ergebnis.nachweise) == 2
    assert counting.save_count == 1
    audit = ergebnis.nachweise[0].payload["automatisierung"]
    assert audit["ausfuehrung_id"] == ergebnis.ausfuehrung_id
    assert audit["herkunft"] == "einzelkommando"
    assert audit["aktion_position"] == 1
    assert "routine_id" not in audit


def test_routine_mehrere_aktionen_reihenfolge():
    katalog, prueflauf_repo, _, _, routine_id = _setup_zweistufige_routine()
    prueflauf = PruefungStarten(katalog, prueflauf_repo).execute(
        produktkodierung="2222222222",
        pruefobjekt_kennung="GER-2",
        pruefer_id="pruefer-1",
    )
    port = SimuliertesExternesKommandoPort(
        {
            "CMD1": ExternesKommandoAntwort(rohdaten="RAW:1", extrahierte_werte={"a": 1}),
            "CMD2": ExternesKommandoAntwort(rohdaten="RAW:2", extrahierte_werte={"b": 2}),
        }
    )
    counting = CountingPrueflaufRepository(prueflauf_repo)

    ergebnis = RoutineAusfuehren(katalog, counting, port).execute(
        prueflauf.prueflauf_id, "schritt-a"
    )

    assert ergebnis.fehlgeschlagen is False
    assert ergebnis.ausgefuehrte_aktionen == 2
    assert len(ergebnis.nachweise) == 4
    assert counting.save_count == 1
    roh = [n for n in ergebnis.nachweise if n.art == NachweisArt.ROHANTWORT]
    assert [n.payload["rohdaten"] for n in roh] == ["RAW:1", "RAW:2"]
    for n in ergebnis.nachweise:
        audit = n.payload["automatisierung"]
        assert audit["ausfuehrung_id"] == ergebnis.ausfuehrung_id
        assert audit["herkunft"] == "bibliothek"
        assert audit["routine_id"] == routine_id


def test_teilfehler_aktion1_ok_aktion2_transport_ohne_roh():
    katalog, prueflauf_repo, _, _, _ = _setup_zweistufige_routine()
    prueflauf = PruefungStarten(katalog, prueflauf_repo).execute(
        produktkodierung="2222222222",
        pruefobjekt_kennung="GER-3",
        pruefer_id="pruefer-1",
    )
    port = SimuliertesExternesKommandoPort(
        {
            "CMD1": ExternesKommandoAntwort(rohdaten="RAW:1", extrahierte_werte={"a": 1}),
        }
    )

    ergebnis = RoutineAusfuehren(katalog, prueflauf_repo, port).execute(
        prueflauf.prueflauf_id, "schritt-a"
    )

    assert ergebnis.fehlgeschlagen is True
    assert ergebnis.abgebrochen_bei_aktion_position == 2
    assert ergebnis.ausgefuehrte_aktionen == 1
    assert ergebnis.fehlerart == KommandoFehlerart.KEINE_GERAETEANTWORT
    assert len(ergebnis.nachweise) == 2

    reloaded = prueflauf_repo.get(prueflauf.prueflauf_id)
    assert len(reloaded.durchfuehrungen["schritt-a"].nachweise) == 2


def test_teilfehler_aktion1_ok_aktion2_geraete_err():
    katalog, prueflauf_repo, _, _, _ = _setup_zweistufige_routine()
    prueflauf = PruefungStarten(katalog, prueflauf_repo).execute(
        produktkodierung="2222222222",
        pruefobjekt_kennung="GER-4",
        pruefer_id="pruefer-1",
    )
    port = SimuliertesExternesKommandoPort(
        {
            "CMD1": ExternesKommandoAntwort(rohdaten="RAW:1", extrahierte_werte={"a": 1}),
            "CMD2": ExternesKommandoAntwort(rohdaten="ERR FAIL", erfolgreich=False),
        }
    )

    ergebnis = RoutineAusfuehren(katalog, prueflauf_repo, port).execute(
        prueflauf.prueflauf_id, "schritt-a"
    )

    assert ergebnis.fehlgeschlagen is True
    assert ergebnis.abgebrochen_bei_aktion_position == 2
    roh = [n for n in ergebnis.nachweise if n.art == NachweisArt.ROHANTWORT]
    assert len(roh) == 2
    assert roh[1].payload["rohdaten"] == "ERR FAIL"


def test_parserfehler_mit_rohantwort_bricht_ab():
    katalog = InMemoryKatalogRepository()
    _katalog_mit_legacy_kommando(katalog, kommandocode="PARSE")
    prueflauf_repo = InMemoryPrueflaufRepository()
    prueflauf = PruefungStarten(katalog, prueflauf_repo).execute(
        produktkodierung="1111111111",
        pruefobjekt_kennung="GER-5",
        pruefer_id="pruefer-1",
    )
    port = SimuliertesExternesKommandoPort(
        {
            "PARSE": ExternesKommandoAntwort(
                rohdaten="OK unparseable",
                erfolgreich=False,
            ),
        }
    )

    ergebnis = RoutineAusfuehren(katalog, prueflauf_repo, port).execute(
        prueflauf.prueflauf_id, "schritt-a"
    )

    assert ergebnis.fehlgeschlagen is True
    assert len(ergebnis.nachweise) == 1
    assert ergebnis.nachweise[0].art == NachweisArt.ROHANTWORT
    assert ergebnis.fehlerart == KommandoFehlerart.GERAETEFEHLSCHLAG


def test_fehler_erste_aktion_transport_liefert_ergebnis():
    katalog = InMemoryKatalogRepository()
    _katalog_mit_legacy_kommando(katalog)
    prueflauf_repo = InMemoryPrueflaufRepository()
    prueflauf = PruefungStarten(katalog, prueflauf_repo).execute(
        produktkodierung="1111111111",
        pruefobjekt_kennung="GER-6",
        pruefer_id="pruefer-1",
    )

    ergebnis = RoutineAusfuehren(
        katalog, prueflauf_repo, SimuliertesExternesKommandoPort()
    ).execute(prueflauf.prueflauf_id, "schritt-a")

    assert ergebnis.fehlgeschlagen is True
    assert ergebnis.abgebrochen_bei_aktion_position == 1
    assert len(ergebnis.nachweise) == 0
    reloaded = prueflauf_repo.get(prueflauf.prueflauf_id)
    assert len(reloaded.durchfuehrungen["schritt-a"].nachweise) == 0


def test_keine_automatisierung_vor_ausfuehrungsbeginn():
    katalog = InMemoryKatalogRepository()
    katalog.register_aktive_version(
        ProduktdefinitionsVersion(
            version_id="ver-manuell",
            produktdefinition_id="pd-manuell",
            produktkodierung="3333333333",
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
        produktkodierung="3333333333",
        pruefobjekt_kennung="GER-7",
        pruefer_id="pruefer-1",
    )

    with pytest.raises(KeineAutomatisierungAmSchritt):
        RoutineAusfuehren(
            katalog, prueflauf_repo, SimuliertesExternesKommandoPort()
        ).execute(prueflauf.prueflauf_id, "schritt-a")


def test_inkonsistente_materialisierung_vor_ausfuehrungsbeginn():
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
            version_id="ver-bad",
            produktdefinition_id="pd-bad",
            produktkodierung="4444444444",
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
        produktkodierung="4444444444",
        pruefobjekt_kennung="GER-8",
        pruefer_id="pruefer-1",
    )

    with pytest.raises(MaterialisierteAutomatisierungInkonsistent):
        RoutineAusfuehren(
            katalog, prueflauf_repo, SimuliertesExternesKommandoPort()
        ).execute(prueflauf.prueflauf_id, "schritt-a")


def test_abgeschlossener_prueflauf_vor_ausfuehrungsbeginn():
    katalog = InMemoryKatalogRepository()
    _katalog_mit_legacy_kommando(katalog)
    prueflauf_repo = InMemoryPrueflaufRepository()
    protokoll_repo = InMemoryProtokollRepository()
    prueflauf = PruefungStarten(katalog, prueflauf_repo).execute(
        produktkodierung="1111111111",
        pruefobjekt_kennung="GER-9",
        pruefer_id="pruefer-1",
    )
    PruefungAbschliessen(
        katalog, prueflauf_repo, in_memory_abschluss_persistenz(prueflauf_repo, protokoll_repo)
    ).execute(prueflauf.prueflauf_id)

    with pytest.raises(InvariantViolation):
        RoutineAusfuehren(
            katalog, prueflauf_repo, SimuliertesExternesKommandoPort()
        ).execute(prueflauf.prueflauf_id, "schritt-a")


def test_erneuter_routineaufruf_neue_ausfuehrung_id():
    katalog = InMemoryKatalogRepository()
    _katalog_mit_legacy_kommando(katalog)
    prueflauf_repo = InMemoryPrueflaufRepository()
    prueflauf = PruefungStarten(katalog, prueflauf_repo).execute(
        produktkodierung="1111111111",
        pruefobjekt_kennung="GER-10",
        pruefer_id="pruefer-1",
    )
    port = SimuliertesExternesKommandoPort(
        {"LEG": ExternesKommandoAntwort(rohdaten="RAW:1", extrahierte_werte={"x": 1})}
    )
    use_case = RoutineAusfuehren(katalog, prueflauf_repo, port)

    e1 = use_case.execute(prueflauf.prueflauf_id, "schritt-a")
    e2 = use_case.execute(prueflauf.prueflauf_id, "schritt-a")

    assert e1.ausfuehrung_id != e2.ausfuehrung_id
    reloaded = prueflauf_repo.get(prueflauf.prueflauf_id)
    assert len(reloaded.durchfuehrungen["schritt-a"].nachweise) == 4


def test_einzelkommando_verwendet_dasselbe_audit_schema():
    katalog = InMemoryKatalogRepository()
    _katalog_mit_legacy_kommando(katalog, kommando_id="cmd-legacy")
    prueflauf_repo = InMemoryPrueflaufRepository()
    prueflauf = PruefungStarten(katalog, prueflauf_repo).execute(
        produktkodierung="1111111111",
        pruefobjekt_kennung="GER-11",
        pruefer_id="pruefer-1",
    )
    port = SimuliertesExternesKommandoPort(
        {"LEG": ExternesKommandoAntwort(rohdaten="RAW:1", extrahierte_werte={"x": 1})}
    )

    ergebnis = ExternesKommandoAusfuehren(katalog, prueflauf_repo, port).execute(
        prueflauf.prueflauf_id, "schritt-a", "cmd-legacy"
    )

    audit = ergebnis.nachweise[0].payload["automatisierung"]
    assert audit["herkunft"] == "einzelkommando"
    assert audit["aktion_position"] == 1
    assert "routine_id" not in audit
    assert audit["kommando_id"] == "cmd-legacy"


def test_manueller_nachweis_ohne_automatisierungsblock():
    katalog = InMemoryKatalogRepository()
    _katalog_mit_legacy_kommando(katalog)
    prueflauf_repo = InMemoryPrueflaufRepository()
    prueflauf = PruefungStarten(katalog, prueflauf_repo).execute(
        produktkodierung="1111111111",
        pruefobjekt_kennung="GER-12",
        pruefer_id="pruefer-1",
    )

    manuell = NachweisErfassen(prueflauf_repo).execute(
        prueflauf.prueflauf_id,
        "schritt-a",
        NachweisArt.KOMMENTAR,
        {"text": "manuell"},
    )

    assert "automatisierung" not in manuell.payload
