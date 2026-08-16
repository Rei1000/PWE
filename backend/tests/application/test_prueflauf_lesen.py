"""Application-Tests — PrueflaufLesen (inkl. Gate 6.3b Automatisierungs-Flags)."""

import pytest

from adapters.persistence.in_memory import (
    InMemoryBibliothekRepository,
    InMemoryKatalogRepository,
    InMemoryPrueflaufRepository,
    InMemoryProtokollRepository,
)
from application.katalog.entwurf_anlegen import EntwurfAnlegen
from application.katalog.externes_kommando_anlegen import ExternesKommandoAnlegen
from application.katalog.kommando_zuweisen import KommandoProzedurSchrittZuweisen
from application.katalog.routine_anlegen import RoutineAnlegen
from application.katalog.routine_zuweisen import RoutineProzedurSchrittZuweisen
from application.katalog.veroeffentlichen import ProduktdefinitionVeroeffentlichen
from application.pruefausfuehrung.prueflauf_lesen import PrueflaufLesen
from application.pruefausfuehrung.pruefung_abschliessen import PruefungAbschliessen
from application.pruefausfuehrung.pruefung_starten import PruefungStarten
from domain.katalog.errors import MaterialisierteAutomatisierungInkonsistent
from domain.katalog.externes_kommando import MaterialisiertesExternesKommando
from domain.katalog.produktdefinition import ProzedurSchrittEntwurf
from domain.katalog.routine import (
    MaterialisierteKommandoAktion,
    MaterialisierteRoutine,
    MaterialisierteRoutineHerkunft,
)
from domain.katalog.version import MaterialisierterProzedurSchritt, ProduktdefinitionsVersion
from helpers import in_memory_abschluss_persistenz


def test_prueflauf_lesen_liefert_materialisierte_schritte():
    katalog = InMemoryKatalogRepository()
    bibliothek = InMemoryBibliothekRepository()
    prueflauf_repo = InMemoryPrueflaufRepository()

    entwurf = EntwurfAnlegen(katalog).execute(
        produktkodierung="1111111111",
        prozedur_schritte=(
            ProzedurSchrittEntwurf(
                schritt_id="s1",
                vorlage_id="v1",
                ist_pflicht=True,
                reihenfolge=1,
                sollvorgaben={"druck": {"min": 1, "max": 2}},
            ),
        ),
        sollbestueckung=("platine",),
    )
    ProduktdefinitionVeroeffentlichen(katalog, bibliothek).execute(entwurf.produktdefinition_id)

    prueflauf = PruefungStarten(katalog, prueflauf_repo).execute(
        produktkodierung="1111111111",
        pruefobjekt_kennung="OBJ-1",
        pruefer_id="p1",
    )

    detail = PrueflaufLesen(katalog, prueflauf_repo).execute(prueflauf.prueflauf_id)

    assert detail.prueflauf_id == prueflauf.prueflauf_id
    assert len(detail.schritte) == 1
    assert detail.schritte[0].schritt_id == "s1"
    assert detail.schritte[0].sollvorgaben["druck"]["min"] == 1
    assert detail.sollbestueckung == ("platine",)
    assert detail.schritte[0].hat_automatisierung is False
    assert detail.schritte[0].kann_automatisierung_ausfuehren is False
    assert detail.schritte[0].automatisierung_bezeichnung is None


def test_lesen_einzelkommando_hat_automatisierung_fehlende_komponenten_ux():
    """Variante B: fehlende Komponenten → UI-Flag false, Use Case bleibt aufrufbar."""
    katalog = InMemoryKatalogRepository()
    bibliothek = InMemoryBibliothekRepository()
    prueflauf_repo = InMemoryPrueflaufRepository()

    kommando = ExternesKommandoAnlegen(bibliothek).execute(
        bezeichnung="Spannung",
        kommandocode="READ_V",
    )
    entwurf = EntwurfAnlegen(katalog).execute(
        produktkodierung="2222222222",
        prozedur_schritte=(
            ProzedurSchrittEntwurf(
                schritt_id="s-auto",
                vorlage_id="v1",
                ist_pflicht=True,
                reihenfolge=1,
                sollvorgaben={},
            ),
        ),
        sollbestueckung=("mainboard",),
    )
    KommandoProzedurSchrittZuweisen(katalog, bibliothek).execute(
        entwurf.produktdefinition_id, "s-auto", kommando.kommando_id
    )
    ProduktdefinitionVeroeffentlichen(katalog, bibliothek).execute(entwurf.produktdefinition_id)

    prueflauf = PruefungStarten(katalog, prueflauf_repo).execute(
        produktkodierung="2222222222",
        pruefobjekt_kennung="OBJ-2",
        pruefer_id="p1",
    )

    detail = PrueflaufLesen(katalog, prueflauf_repo).execute(prueflauf.prueflauf_id)
    schritt = detail.schritte[0]

    assert schritt.hat_automatisierung is True
    assert schritt.automatisierung_bezeichnung == "Spannung"
    assert detail.fehlende_komponenten == ("mainboard",)
    # Prüferführung: nicht ausführbar, obwohl API/Use Case Komponenten nicht blockiert
    assert schritt.kann_automatisierung_ausfuehren is False

    prueflauf.erfasse_komponente("mainboard", "MB-1")
    prueflauf_repo.save(prueflauf)

    detail2 = PrueflaufLesen(katalog, prueflauf_repo).execute(prueflauf.prueflauf_id)
    assert detail2.schritte[0].kann_automatisierung_ausfuehren is True


def test_lesen_bibliotheksroutine_hat_automatisierung():
    katalog = InMemoryKatalogRepository()
    bibliothek = InMemoryBibliothekRepository()
    prueflauf_repo = InMemoryPrueflaufRepository()

    k1 = ExternesKommandoAnlegen(bibliothek).execute(bezeichnung="A", kommandocode="A1")
    k2 = ExternesKommandoAnlegen(bibliothek).execute(bezeichnung="B", kommandocode="B1")
    routine = RoutineAnlegen(bibliothek).execute(
        bezeichnung="Zwei",
        kommando_ids=(k1.kommando_id, k2.kommando_id),
    )
    entwurf = EntwurfAnlegen(katalog).execute(
        produktkodierung="3333333333",
        prozedur_schritte=(
            ProzedurSchrittEntwurf(
                schritt_id="s-r",
                vorlage_id="v1",
                ist_pflicht=True,
                reihenfolge=1,
                sollvorgaben={},
            ),
        ),
        sollbestueckung=(),
    )
    RoutineProzedurSchrittZuweisen(katalog, bibliothek).execute(
        entwurf.produktdefinition_id, "s-r", routine.routine_id
    )
    ProduktdefinitionVeroeffentlichen(katalog, bibliothek).execute(entwurf.produktdefinition_id)

    prueflauf = PruefungStarten(katalog, prueflauf_repo).execute(
        produktkodierung="3333333333",
        pruefobjekt_kennung="OBJ-3",
        pruefer_id="p1",
    )

    detail = PrueflaufLesen(katalog, prueflauf_repo).execute(prueflauf.prueflauf_id)
    schritt = detail.schritte[0]
    assert schritt.hat_automatisierung is True
    assert schritt.kann_automatisierung_ausfuehren is True
    assert schritt.automatisierung_bezeichnung == "Zwei"


def test_lesen_legacy_externes_kommando_erkannt():
    katalog = InMemoryKatalogRepository()
    prueflauf_repo = InMemoryPrueflaufRepository()
    katalog.register_aktive_version(
        ProduktdefinitionsVersion(
            version_id="ver-leg",
            produktdefinition_id="pd-leg",
            produktkodierung="4444444444",
            sollbestueckung=(),
            prozedur_schritte=(
                MaterialisierterProzedurSchritt(
                    schritt_id="s-leg",
                    vorlage_id="v1",
                    ist_pflicht=True,
                    reihenfolge=1,
                    externes_kommando=MaterialisiertesExternesKommando(
                        kommando_id="cmd-leg",
                        bezeichnung="Legacy",
                        kommandocode="LEG",
                    ),
                ),
            ),
        )
    )

    prueflauf = PruefungStarten(katalog, prueflauf_repo).execute(
        produktkodierung="4444444444",
        pruefobjekt_kennung="OBJ-4",
        pruefer_id="p1",
    )
    detail = PrueflaufLesen(katalog, prueflauf_repo).execute(prueflauf.prueflauf_id)
    assert detail.schritte[0].hat_automatisierung is True
    assert detail.schritte[0].kann_automatisierung_ausfuehren is True
    assert detail.schritte[0].automatisierung_bezeichnung == "Legacy"


def test_lesen_abgeschlossen_nicht_ausfuehrbar():
    katalog = InMemoryKatalogRepository()
    bibliothek = InMemoryBibliothekRepository()
    prueflauf_repo = InMemoryPrueflaufRepository()
    protokoll_repo = InMemoryProtokollRepository()

    kommando = ExternesKommandoAnlegen(bibliothek).execute(
        bezeichnung="Spannung",
        kommandocode="READ_V",
    )
    entwurf = EntwurfAnlegen(katalog).execute(
        produktkodierung="5555555555",
        prozedur_schritte=(
            ProzedurSchrittEntwurf(
                schritt_id="s1",
                vorlage_id="v1",
                ist_pflicht=True,
                reihenfolge=1,
                sollvorgaben={},
            ),
        ),
        sollbestueckung=(),
    )
    KommandoProzedurSchrittZuweisen(katalog, bibliothek).execute(
        entwurf.produktdefinition_id, "s1", kommando.kommando_id
    )
    ProduktdefinitionVeroeffentlichen(katalog, bibliothek).execute(entwurf.produktdefinition_id)

    prueflauf = PruefungStarten(katalog, prueflauf_repo).execute(
        produktkodierung="5555555555",
        pruefobjekt_kennung="OBJ-5",
        pruefer_id="p1",
    )
    PruefungAbschliessen(
        katalog,
        prueflauf_repo,
        in_memory_abschluss_persistenz(prueflauf_repo, protokoll_repo),
    ).execute(prueflauf.prueflauf_id)

    detail = PrueflaufLesen(katalog, prueflauf_repo).execute(prueflauf.prueflauf_id)
    assert detail.ist_abgeschlossen is True
    assert detail.schritte[0].hat_automatisierung is True
    assert detail.schritte[0].kann_automatisierung_ausfuehren is False


def test_lesen_inkonsistente_automatisierung_nicht_verschluckt():
    katalog = InMemoryKatalogRepository()
    prueflauf_repo = InMemoryPrueflaufRepository()
    katalog.register_aktive_version(
        ProduktdefinitionsVersion(
            version_id="ver-bad",
            produktdefinition_id="pd-bad",
            produktkodierung="6666666666",
            sollbestueckung=(),
            prozedur_schritte=(
                MaterialisierterProzedurSchritt(
                    schritt_id="s-bad",
                    vorlage_id="v1",
                    ist_pflicht=True,
                    reihenfolge=1,
                    materialisierte_routine=MaterialisierteRoutine(
                        herkunft=MaterialisierteRoutineHerkunft.EINZELKOMMANDO,
                        routine_id=None,
                        bezeichnung="Gut",
                        aktionen=(
                            MaterialisierteKommandoAktion(
                                position=1,
                                kommando_id="k1",
                                bezeichnung="Gut",
                                kommandocode="OK",
                            ),
                        ),
                    ),
                    externes_kommando=MaterialisiertesExternesKommando(
                        kommando_id="k-anders",
                        bezeichnung="Anders",
                        kommandocode="ANDERS",
                    ),
                ),
            ),
        )
    )

    prueflauf = PruefungStarten(katalog, prueflauf_repo).execute(
        produktkodierung="6666666666",
        pruefobjekt_kennung="OBJ-6",
        pruefer_id="p1",
    )

    with pytest.raises(MaterialisierteAutomatisierungInkonsistent):
        PrueflaufLesen(katalog, prueflauf_repo).execute(prueflauf.prueflauf_id)
