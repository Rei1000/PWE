"""Write Exit — neue Versionen ohne Legacy-Snapshot (Gate 7.4b, ADR-0018)."""

from __future__ import annotations

import json

from adapters.persistence.in_memory import InMemoryBibliothekRepository, InMemoryKatalogRepository
from adapters.persistence.postgresql.mapping import version_from_payload, version_to_payload
from adapters.simulation.externes_kommando import SimuliertesExternesKommandoPort
from application.katalog.entwurf_anlegen import EntwurfAnlegen
from application.katalog.externes_kommando_anlegen import ExternesKommandoAnlegen
from application.katalog.kommando_zuweisen import KommandoProzedurSchrittZuweisen
from application.katalog.veroeffentlichen import ProduktdefinitionVeroeffentlichen
from application.pruefausfuehrung.pruefung_starten import PruefungStarten
from application.pruefausfuehrung.routine_ausfuehren import RoutineAusfuehren
from domain.katalog.externes_kommando import MaterialisiertesExternesKommando
from domain.katalog.materialisierung import aufgeloeste_materialisierte_routine
from domain.katalog.produktdefinition import ProzedurSchrittEntwurf
from domain.katalog.routine import MaterialisierteRoutineHerkunft
from domain.katalog.version import MaterialisierterProzedurSchritt, ProduktdefinitionsVersion
from domain.pruefausfuehrung.kommando_ausfuehrung import ExternesKommandoAntwort
from adapters.persistence.in_memory import InMemoryPrueflaufRepository


def test_veroeffentlichen_schreibt_kein_legacy_externes_kommando():
    katalog = InMemoryKatalogRepository()
    bibliothek = InMemoryBibliothekRepository()
    kommando = ExternesKommandoAnlegen(bibliothek).execute(
        bezeichnung="Spannung",
        kommandocode="READ_V",
    )
    entwurf = EntwurfAnlegen(katalog).execute(
        produktkodierung="5555555555",
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
    version = ProduktdefinitionVeroeffentlichen(katalog, bibliothek).execute(
        entwurf.produktdefinition_id
    )
    schritt = version.schritt_by_id("schritt-a")
    assert schritt is not None
    assert schritt.externes_kommando is None
    assert schritt.materialisierte_routine is not None
    assert schritt.materialisierte_routine.herkunft == MaterialisierteRoutineHerkunft.EINZELKOMMANDO
    assert schritt.materialisierte_routine.aktionen[0].kommandocode == "READ_V"

    payload = json.loads(version_to_payload(version))
    schritt_payload = payload["prozedur_schritte"][0]
    assert "materialisierte_routine" in schritt_payload
    assert "externes_kommando" not in schritt_payload


def test_neue_version_ohne_legacy_ausfuehrbar_via_routine():
    katalog = InMemoryKatalogRepository()
    bibliothek = InMemoryBibliothekRepository()
    kommando = ExternesKommandoAnlegen(bibliothek).execute(
        bezeichnung="Spannung",
        kommandocode="READ_V",
    )
    entwurf = EntwurfAnlegen(katalog).execute(
        produktkodierung="5555555556",
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
    prueflauf_repo = InMemoryPrueflaufRepository()
    prueflauf = PruefungStarten(katalog, prueflauf_repo).execute(
        produktkodierung="5555555556",
        pruefobjekt_kennung="GER-WE",
        pruefer_id="pruefer-1",
    )
    port = SimuliertesExternesKommandoPort(
        {
            "READ_V": ExternesKommandoAntwort(
                rohdaten="RAW:230",
                extrahierte_werte={"spannung": 230},
            ),
        }
    )
    ergebnis = RoutineAusfuehren(katalog, prueflauf_repo, port).execute(
        prueflauf.prueflauf_id, "schritt-a"
    )
    assert ergebnis.fehlgeschlagen is False
    assert len(ergebnis.nachweise) == 2


def test_legacy_ek_only_bleibt_nach_write_exit_lesbar_und_ausfuehrbar():
    katalog = InMemoryKatalogRepository()
    katalog.register_aktive_version(
        ProduktdefinitionsVersion(
            version_id="ver-legacy-we",
            produktdefinition_id="pd-legacy-we",
            produktkodierung="5555555557",
            prozedur_schritte=(
                MaterialisierterProzedurSchritt(
                    schritt_id="schritt-a",
                    vorlage_id="vorlage-a",
                    ist_pflicht=True,
                    reihenfolge=1,
                    externes_kommando=MaterialisiertesExternesKommando(
                        kommando_id="cmd-legacy",
                        bezeichnung="Legacy",
                        kommandocode="LEG",
                    ),
                ),
            ),
        )
    )
    version = katalog.get_version("ver-legacy-we")
    assert version is not None
    schritt = version.schritt_by_id("schritt-a")
    assert schritt is not None
    assert schritt.materialisierte_routine is None
    assert schritt.externes_kommando is not None
    aufgeloest = aufgeloeste_materialisierte_routine(schritt)
    assert aufgeloest.herkunft == MaterialisierteRoutineHerkunft.EINZELKOMMANDO

    restored = version_from_payload(version_to_payload(version))
    assert restored.schritt_by_id("schritt-a").externes_kommando is not None
    assert restored.schritt_by_id("schritt-a").materialisierte_routine is None

    prueflauf_repo = InMemoryPrueflaufRepository()
    prueflauf = PruefungStarten(katalog, prueflauf_repo).execute(
        produktkodierung="5555555557",
        pruefobjekt_kennung="GER-LEG",
        pruefer_id="pruefer-1",
    )
    port = SimuliertesExternesKommandoPort(
        {"LEG": ExternesKommandoAntwort(rohdaten="RAW:1", extrahierte_werte={"x": 1})}
    )
    ergebnis = RoutineAusfuehren(katalog, prueflauf_repo, port).execute(
        prueflauf.prueflauf_id, "schritt-a"
    )
    assert ergebnis.fehlgeschlagen is False
