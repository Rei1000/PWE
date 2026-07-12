"""Application-Tests — Katalog ExternesKommando."""

import pytest

from adapters.persistence.in_memory import InMemoryBibliothekRepository, InMemoryKatalogRepository
from application.katalog.entwurf_anlegen import EntwurfAnlegen
from application.katalog.externes_kommando_anlegen import ExternesKommandoAnlegen
from application.katalog.kommando_zuweisen import KommandoProzedurSchrittZuweisen
from application.katalog.veroeffentlichen import ProduktdefinitionVeroeffentlichen
from domain.katalog.errors import ExternesKommandoNichtGefunden
from domain.katalog.externes_kommando import ExternesKommando
from domain.katalog.produktdefinition import ProzedurSchrittEntwurf


def _setup():
    return InMemoryKatalogRepository(), InMemoryBibliothekRepository()


def test_externes_kommando_anlegen():
    _, bibliothek = _setup()
    kommando = ExternesKommandoAnlegen(bibliothek).execute(
        bezeichnung="Spannung messen",
        kommandocode="MEAS:V",
    )
    gespeichert = bibliothek.get_externes_kommando(kommando.kommando_id)
    assert gespeichert == kommando


def test_produktdefinition_mit_kommando_referenz_veroeffentlichen():
    katalog, bibliothek = _setup()
    kommando = ExternesKommandoAnlegen(bibliothek).execute(
        bezeichnung="Reset",
        kommandocode="RST",
    )
    entwurf = EntwurfAnlegen(katalog).execute(
        produktkodierung="3333333333",
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
    assert schritt.externes_kommando is not None
    assert schritt.externes_kommando.kommando_id == kommando.kommando_id
    assert schritt.externes_kommando.bezeichnung == "Reset"
    assert schritt.externes_kommando.kommandocode == "RST"


def test_veroeffentlichen_mit_unbekannter_kommando_id():
    katalog, bibliothek = _setup()
    entwurf = EntwurfAnlegen(katalog).execute(
        produktkodierung="4444444444",
        prozedur_schritte=(
            ProzedurSchrittEntwurf(
                schritt_id="schritt-a",
                vorlage_id="vorlage-a",
                ist_pflicht=True,
                reihenfolge=1,
                kommando_id="fehlend",
            ),
        ),
    )
    with pytest.raises(ExternesKommandoNichtGefunden):
        ProduktdefinitionVeroeffentlichen(katalog, bibliothek).execute(entwurf.produktdefinition_id)


def test_bibliotheksaenderung_nach_veroeffentlichung():
    katalog, bibliothek = _setup()
    kommando = ExternesKommandoAnlegen(bibliothek).execute(
        bezeichnung="Alt",
        kommandocode="OLD",
    )
    entwurf = EntwurfAnlegen(katalog).execute(
        produktkodierung="5555555555",
        prozedur_schritte=(
            ProzedurSchrittEntwurf(
                schritt_id="schritt-a",
                vorlage_id="vorlage-a",
                ist_pflicht=True,
                reihenfolge=1,
                kommando_id=kommando.kommando_id,
            ),
        ),
    )
    version = ProduktdefinitionVeroeffentlichen(katalog, bibliothek).execute(
        entwurf.produktdefinition_id
    )

    bibliothek.save_externes_kommando(
        ExternesKommando(
            kommando_id=kommando.kommando_id,
            bezeichnung="Neu",
            kommandocode="NEW",
        )
    )

    gespeichert = katalog.get_version(version.version_id)
    assert gespeichert is not None
    schritt = gespeichert.schritt_by_id("schritt-a")
    assert schritt is not None
    assert schritt.externes_kommando is not None
    assert schritt.externes_kommando.bezeichnung == "Alt"
    assert schritt.externes_kommando.kommandocode == "OLD"
