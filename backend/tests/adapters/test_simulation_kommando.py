"""Tests — Simulations-Adapter für ExternesKommandoPort."""

from adapters.simulation.externes_kommando import SimuliertesExternesKommandoPort
from domain.pruefausfuehrung.kommando_ausfuehrung import (
    ExternesKommandoAnfrage,
    ExternesKommandoAntwort,
)


def test_simulation_liefert_registrierte_antwort():
    port = SimuliertesExternesKommandoPort(
        {
            "READ_VOLTAGE": ExternesKommandoAntwort(
                rohdaten="OK 230V",
                extrahierte_werte={"spannung": 230},
            ),
        }
    )

    antwort = port.ausfuehren(ExternesKommandoAnfrage(kommandocode="READ_VOLTAGE"))

    assert antwort.rohdaten == "OK 230V"
    assert antwort.extrahierte_werte["spannung"] == 230


def test_simulation_unbekanntes_kommando_fehlgeschlagene_antwort():
    port = SimuliertesExternesKommandoPort()

    antwort = port.ausfuehren(ExternesKommandoAnfrage(kommandocode="UNKNOWN"))

    assert antwort.erfolgreich is False
    assert antwort.rohdaten == ""
