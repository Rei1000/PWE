"""Domain-Tests — DateiVerweis (Gate 8.3a)."""

from __future__ import annotations

import pytest

from domain.pruefausfuehrung.datei_verweis import DateiVerweis
from domain.pruefausfuehrung.foto_regeln import MAX_FOTO_GROESSE_BYTES
from domain.shared.errors import InvariantViolation


def test_datei_verweis_gueltig():
    verweis = DateiVerweis(
        datei_id="datei-1",
        mime_type="image/jpeg",
        groesse_bytes=1024,
        dateiname="foto.jpg",
    )
    payload = verweis.to_payload()
    assert payload["datei_id"] == "datei-1"
    assert DateiVerweis.from_payload(payload).dateiname == "foto.jpg"


def test_datei_verweis_leere_id():
    with pytest.raises(InvariantViolation):
        DateiVerweis(datei_id="", mime_type="image/jpeg", groesse_bytes=1)


def test_datei_verweis_ungueltiger_mime():
    with pytest.raises(InvariantViolation):
        DateiVerweis(datei_id="x", mime_type="image/gif", groesse_bytes=1)


def test_datei_verweis_ungueltige_groesse():
    with pytest.raises(InvariantViolation):
        DateiVerweis(datei_id="x", mime_type="image/png", groesse_bytes=0)
    with pytest.raises(InvariantViolation):
        DateiVerweis(
            datei_id="x",
            mime_type="image/png",
            groesse_bytes=MAX_FOTO_GROESSE_BYTES + 1,
        )
