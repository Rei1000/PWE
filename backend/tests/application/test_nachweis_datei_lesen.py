"""Application-Tests — NachweisDateiLesen (Gate 8.3a)."""

from __future__ import annotations

import pytest

from adapters.persistence.in_memory import InMemoryPrueflaufRepository
from adapters.storage.in_memory import InMemoryDateiSpeicher
from application.pruefausfuehrung.foto_nachweis_erfassen import FotoNachweisErfassen
from application.pruefausfuehrung.nachweis_datei_lesen import NachweisDateiLesen
from domain.pruefausfuehrung.errors import (
    DateiNichtGefunden,
    NachweisKeinFoto,
    NachweisNichtGefunden,
    PrueflaufNichtGefunden,
)
from domain.pruefausfuehrung.prueflauf import NachweisArt
from domain.pruefausfuehrung.typen import Nachweis
from foto_fixtures import JPEG_BYTES, setup_prueflauf_mit_schritt


def test_foto_lesen_happy_path():
    repo = InMemoryPrueflaufRepository()
    speicher = InMemoryDateiSpeicher()
    prueflauf_id, schritt_id = setup_prueflauf_mit_schritt(repo)
    nachweis = FotoNachweisErfassen(repo, speicher).execute(
        prueflauf_id, schritt_id, JPEG_BYTES, "image/jpeg", dateiname="bild.jpg"
    )
    ergebnis = NachweisDateiLesen(repo, speicher).execute(prueflauf_id, nachweis.nachweis_id)
    assert ergebnis.inhalt == JPEG_BYTES
    assert ergebnis.mime_type == "image/jpeg"
    assert ergebnis.dateiname == "bild.jpg"


def test_prueflauf_fehlt():
    repo = InMemoryPrueflaufRepository()
    speicher = InMemoryDateiSpeicher()
    with pytest.raises(PrueflaufNichtGefunden):
        NachweisDateiLesen(repo, speicher).execute("fehlt", "nachweis-1")


def test_nachweis_fehlt():
    repo = InMemoryPrueflaufRepository()
    speicher = InMemoryDateiSpeicher()
    prueflauf_id, _ = setup_prueflauf_mit_schritt(repo)
    with pytest.raises(NachweisNichtGefunden):
        NachweisDateiLesen(repo, speicher).execute(prueflauf_id, "fehlt")


def test_nachweis_kein_foto():
    repo = InMemoryPrueflaufRepository()
    speicher = InMemoryDateiSpeicher()
    prueflauf_id, schritt_id = setup_prueflauf_mit_schritt(repo)
    prueflauf = repo.get(prueflauf_id)
    assert prueflauf is not None
    nachweis = Nachweis(
        nachweis_id="n-kommentar",
        art=NachweisArt.KOMMENTAR,
        erfasst_am=prueflauf.gestartet_am,
        payload={"text": "ok"},
    )
    prueflauf.durchfuehrungen[schritt_id].add_nachweis(nachweis)
    repo.save(prueflauf)
    with pytest.raises(NachweisKeinFoto):
        NachweisDateiLesen(repo, speicher).execute(prueflauf_id, nachweis.nachweis_id)


def test_datei_fehlt_im_storage():
    repo = InMemoryPrueflaufRepository()
    speicher = InMemoryDateiSpeicher()
    prueflauf_id, schritt_id = setup_prueflauf_mit_schritt(repo)
    prueflauf = repo.get(prueflauf_id)
    assert prueflauf is not None
    nachweis = Nachweis(
        nachweis_id="n-foto",
        art=NachweisArt.FOTO,
        erfasst_am=prueflauf.gestartet_am,
        payload={
            "datei_id": "fehlende-datei",
            "mime_type": "image/jpeg",
            "groesse_bytes": 10,
        },
    )
    prueflauf.durchfuehrungen[schritt_id].add_nachweis(nachweis)
    repo.save(prueflauf)
    with pytest.raises(DateiNichtGefunden):
        NachweisDateiLesen(repo, speicher).execute(prueflauf_id, nachweis.nachweis_id)
