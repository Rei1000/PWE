"""Contract-Tests für DateiSpeicher-Adapter (Gate 8.3a)."""

from __future__ import annotations

import pytest

from adapters.storage.in_memory import InMemoryDateiSpeicher
from adapters.storage.lokal import LokalerDateiSpeicher
from ports.datei_speicher_port import DateiBereitsVorhanden, DateiSpeicherZugriffFehler


JPEG_BYTES = b"\xff\xd8\xff\xe0" + b"\x00" * 16
PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16


@pytest.fixture(params=["memory", "filesystem"])
def speicher(request, tmp_path):
    if request.param == "memory":
        return InMemoryDateiSpeicher()
    return LokalerDateiSpeicher(tmp_path / "dateien")


def test_speichern_lesen_loeschen(speicher):
    speicher.speichern("datei-1", JPEG_BYTES, "image/jpeg")
    inhalt, mime = speicher.lesen("datei-1")
    assert inhalt == JPEG_BYTES
    assert mime == "image/jpeg"
    speicher.loeschen("datei-1")
    with pytest.raises(DateiSpeicherZugriffFehler):
        speicher.lesen("datei-1")


def test_write_once_kollision(speicher):
    speicher.speichern("datei-1", JPEG_BYTES, "image/jpeg")
    with pytest.raises(DateiBereitsVorhanden):
        speicher.speichern("datei-1", PNG_BYTES, "image/png")


def test_lesen_unbekannte_id(speicher):
    with pytest.raises(DateiSpeicherZugriffFehler):
        speicher.lesen("fehlt")


def test_loeschen_idempotent(speicher):
    speicher.loeschen("fehlt")


def test_keine_pfad_traversal(speicher):
    with pytest.raises(DateiSpeicherZugriffFehler):
        speicher.speichern("../escape", JPEG_BYTES, "image/jpeg")


def test_datenintegritaet_png(speicher):
    speicher.speichern("png-1", PNG_BYTES, "image/png")
    inhalt, mime = speicher.lesen("png-1")
    assert inhalt == PNG_BYTES
    assert mime == "image/png"
