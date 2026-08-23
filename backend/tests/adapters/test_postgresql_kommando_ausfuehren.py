"""PostgreSQL-Integration — Legacy ek-only Version über RoutineAusfuehren (Gate 7.4a)."""

import pytest

from adapters.simulation.externes_kommando import SimuliertesExternesKommandoPort
from tests.support.qualification import make_pruefung_starten
from application.pruefausfuehrung.routine_ausfuehren import RoutineAusfuehren
from domain.katalog.externes_kommando import MaterialisiertesExternesKommando
from domain.katalog.version import MaterialisierterProzedurSchritt, ProduktdefinitionsVersion
from domain.pruefausfuehrung.kommando_ausfuehrung import ExternesKommandoAntwort
from domain.pruefausfuehrung.prueflauf import NachweisArt

pytestmark = pytest.mark.postgresql

KOMMANDO_ID = "cmd-pg-voltage"
KOMMANDOCODE = "READ_VOLTAGE"


def test_postgresql_legacy_ek_only_routine_ausfuehren_persistiert_nachweise(pg_repos):
    """Alte Version: externes_kommando gesetzt, materialisierte_routine=None."""
    katalog, _, prueflauf_repo, _ = pg_repos
    katalog.save_version(
        ProduktdefinitionsVersion(
            version_id="ver-pg-kommando",
            produktdefinition_id="pd-pg",
            produktkodierung="7777777771",
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

    prueflauf = make_pruefung_starten(katalog, prueflauf_repo).execute(
        produktkodierung="7777777771",
        pruefobjekt_kennung="GER-PG-K",
        pruefer_id="pruefer-pg",
    )
    port = SimuliertesExternesKommandoPort(
        {
            KOMMANDOCODE: ExternesKommandoAntwort(
                rohdaten="RAW:230",
                extrahierte_werte={"spannung": 230},
            ),
        }
    )

    ergebnis = RoutineAusfuehren(katalog, prueflauf_repo, port).execute(
        prueflauf.prueflauf_id,
        "schritt-a",
    )

    reloaded = prueflauf_repo.get(prueflauf.prueflauf_id)
    assert reloaded is not None
    assert ergebnis.fehlgeschlagen is False
    assert len(ergebnis.nachweise) == 2
    assert reloaded.durchfuehrungen["schritt-a"].nachweise[0].art == NachweisArt.ROHANTWORT


def test_postgresql_legacy_ek_only_geraete_err_persistiert_rohantwort(pg_repos):
    katalog, _, prueflauf_repo, _ = pg_repos
    katalog.save_version(
        ProduktdefinitionsVersion(
            version_id="ver-pg-kommando-err",
            produktdefinition_id="pd-pg-err",
            produktkodierung="7777777772",
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

    prueflauf = make_pruefung_starten(katalog, prueflauf_repo).execute(
        produktkodierung="7777777772",
        pruefobjekt_kennung="GER-PG-K-ERR",
        pruefer_id="pruefer-pg",
    )
    port = SimuliertesExternesKommandoPort(
        {
            KOMMANDOCODE: ExternesKommandoAntwort(
                rohdaten="ERR OUT_OF_RANGE",
                erfolgreich=False,
            ),
        }
    )

    ergebnis = RoutineAusfuehren(katalog, prueflauf_repo, port).execute(
        prueflauf.prueflauf_id,
        "schritt-a",
    )

    assert ergebnis.fehlgeschlagen is True
    assert len(ergebnis.nachweise) == 1

    reloaded = prueflauf_repo.get(prueflauf.prueflauf_id)
    assert reloaded is not None
    nachweise = reloaded.durchfuehrungen["schritt-a"].nachweise
    assert len(nachweise) == 1
    assert nachweise[0].payload["rohdaten"] == "ERR OUT_OF_RANGE"
    assert nachweise[0].payload["erfolgreich"] is False
