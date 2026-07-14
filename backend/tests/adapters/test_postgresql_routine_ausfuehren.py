"""PostgreSQL-Integration — RoutineAusfuehren (Gate 7.3e)."""

import pytest

from adapters.simulation.externes_kommando import SimuliertesExternesKommandoPort
from application.pruefausfuehrung.routine_ausfuehren import RoutineAusfuehren
from application.pruefausfuehrung.pruefung_starten import PruefungStarten
from domain.katalog.routine import (
    MaterialisierteKommandoAktion,
    MaterialisierteRoutine,
    MaterialisierteRoutineHerkunft,
)
from domain.katalog.version import MaterialisierterProzedurSchritt, ProduktdefinitionsVersion
from domain.pruefausfuehrung.kommando_ausfuehrung import ExternesKommandoAntwort
from domain.pruefausfuehrung.prueflauf import NachweisArt

pytestmark = pytest.mark.postgresql


def test_postgresql_routine_teilfehler_persistiert_erste_welle(pg_repos):
    katalog, _, prueflauf_repo, _ = pg_repos
    katalog.save_version(
        ProduktdefinitionsVersion(
            version_id="ver-pg-routine",
            produktdefinition_id="pd-pg-r",
            produktkodierung="8888888881",
            prozedur_schritte=(
                MaterialisierterProzedurSchritt(
                    schritt_id="schritt-a",
                    vorlage_id="vorlage-a",
                    ist_pflicht=True,
                    reihenfolge=1,
                    materialisierte_routine=MaterialisierteRoutine(
                        herkunft=MaterialisierteRoutineHerkunft.BIBLIOTHEK,
                        routine_id="r-pg",
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

    prueflauf = PruefungStarten(katalog, prueflauf_repo).execute(
        produktkodierung="8888888881",
        pruefobjekt_kennung="GER-PG-R",
        pruefer_id="pruefer-pg",
    )
    port = SimuliertesExternesKommandoPort(
        {
            "CMD1": ExternesKommandoAntwort(
                rohdaten="RAW:1",
                extrahierte_werte={"a": 1},
            ),
        }
    )

    ergebnis = RoutineAusfuehren(katalog, prueflauf_repo, port).execute(
        prueflauf.prueflauf_id,
        "schritt-a",
    )

    assert ergebnis.fehlgeschlagen is True
    reloaded = prueflauf_repo.get(prueflauf.prueflauf_id)
    assert reloaded is not None
    nachweise = reloaded.durchfuehrungen["schritt-a"].nachweise
    assert len(nachweise) == 2
    assert nachweise[0].art == NachweisArt.ROHANTWORT
    assert nachweise[0].payload["automatisierung"]["aktion_position"] == 1
    assert nachweise[0].payload["automatisierung"]["routine_id"] == "r-pg"
