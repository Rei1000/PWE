"""Application-Tests — FotoNachweisErfassen (Gate 8.3a)."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from adapters.persistence.in_memory import InMemoryKatalogRepository, InMemoryPrueflaufRepository
from adapters.storage.in_memory import InMemoryDateiSpeicher
from application.pruefausfuehrung.foto_nachweis_erfassen import FotoNachweisErfassen
from domain.katalog.version import MaterialisierterProzedurSchritt, ProduktdefinitionsVersion
from domain.pruefausfuehrung.errors import (
    DateiSpeicherungFehlgeschlagen,
    DateiZuGross,
    PrueflaufNichtGefunden,
    UngueltigerDateityp,
)
from domain.pruefausfuehrung.foto_regeln import MAX_FOTO_GROESSE_BYTES
from domain.pruefausfuehrung.prueflauf import NachweisArt, Prueflauf
from domain.pruefausfuehrung.typen import Beurteilung, BeurteilungErgebnis
from domain.shared.errors import InvariantViolation
from foto_fixtures import JPEG_BYTES, PNG_BYTES, setup_prueflauf_mit_schritt
from ports.datei_speicher_port import DateiSpeicherFehler, DateiSpeicherPort
from ports.prueflauf_repository import PrueflaufRepository


class SpyDateiSpeicher:
    def __init__(self, inner: InMemoryDateiSpeicher | None = None) -> None:
        self._inner = inner or InMemoryDateiSpeicher()
        self.speichern_count = 0
        self.loeschen_count = 0

    def speichern(self, datei_id: str, inhalt: bytes, mime_type: str) -> None:
        self.speichern_count += 1
        self._inner.speichern(datei_id, inhalt, mime_type)

    def lesen(self, datei_id: str) -> tuple[bytes, str]:
        return self._inner.lesen(datei_id)

    def loeschen(self, datei_id: str) -> None:
        self.loeschen_count += 1
        self._inner.loeschen(datei_id)


class FailingDateiSpeicher:
    def speichern(self, datei_id: str, inhalt: bytes, mime_type: str) -> None:
        raise DateiSpeicherFehler("fail")

    def lesen(self, datei_id: str) -> tuple[bytes, str]:
        raise DateiSpeicherFehler("fail")

    def loeschen(self, datei_id: str) -> None:
        raise DateiSpeicherFehler("fail")


@dataclass
class FailingPrueflaufRepository(PrueflaufRepository):
    inner: InMemoryPrueflaufRepository

    def save(self, prueflauf: Prueflauf) -> None:
        raise RuntimeError("save failed")

    def get(self, prueflauf_id: str) -> Prueflauf | None:
        return self.inner.get(prueflauf_id)


def _setup_prueflauf(repo: InMemoryPrueflaufRepository) -> tuple[str, str]:
    return setup_prueflauf_mit_schritt(repo)


def test_happy_path_jpeg():
    repo = InMemoryPrueflaufRepository()
    speicher = SpyDateiSpeicher()
    prueflauf_id, schritt_id = _setup_prueflauf(repo)
    nachweis = FotoNachweisErfassen(repo, speicher).execute(
        prueflauf_id, schritt_id, JPEG_BYTES, "image/jpeg", dateiname="foto.jpg"
    )
    assert nachweis.art == NachweisArt.FOTO
    assert nachweis.payload["mime_type"] == "image/jpeg"
    assert speicher.speichern_count == 1
    reloaded = repo.get(prueflauf_id)
    assert reloaded is not None
    assert len(reloaded.durchfuehrungen["schritt-a"].nachweise) == 1


def test_happy_path_png():
    repo = InMemoryPrueflaufRepository()
    speicher = InMemoryDateiSpeicher()
    prueflauf_id, schritt_id = _setup_prueflauf(repo)
    nachweis = FotoNachweisErfassen(repo, speicher).execute(
        prueflauf_id, schritt_id, PNG_BYTES, "image/png"
    )
    assert nachweis.payload["groesse_bytes"] == len(PNG_BYTES)


def test_leere_datei_vor_storage():
    repo = InMemoryPrueflaufRepository()
    speicher = SpyDateiSpeicher()
    prueflauf_id, schritt_id = _setup_prueflauf(repo)
    with pytest.raises(UngueltigerDateityp):
        FotoNachweisErfassen(repo, speicher).execute(prueflauf_id, schritt_id, b"", "image/jpeg")
    assert speicher.speichern_count == 0


def test_ungueltiger_mime_vor_storage():
    repo = InMemoryPrueflaufRepository()
    speicher = SpyDateiSpeicher()
    prueflauf_id, schritt_id = _setup_prueflauf(repo)
    with pytest.raises(UngueltigerDateityp):
        FotoNachweisErfassen(repo, speicher).execute(
            prueflauf_id, schritt_id, JPEG_BYTES, "image/gif"
        )
    assert speicher.speichern_count == 0


def test_magic_bytes_passen_nicht():
    repo = InMemoryPrueflaufRepository()
    speicher = SpyDateiSpeicher()
    prueflauf_id, schritt_id = _setup_prueflauf(repo)
    with pytest.raises(UngueltigerDateityp):
        FotoNachweisErfassen(repo, speicher).execute(
            prueflauf_id, schritt_id, b"kein-bild", "image/jpeg"
        )
    assert speicher.speichern_count == 0


def test_zu_gross():
    repo = InMemoryPrueflaufRepository()
    speicher = SpyDateiSpeicher()
    prueflauf_id, schritt_id = _setup_prueflauf(repo)
    zu_gross = JPEG_BYTES + b"\x00" * MAX_FOTO_GROESSE_BYTES
    with pytest.raises(DateiZuGross):
        FotoNachweisErfassen(repo, speicher).execute(
            prueflauf_id, schritt_id, zu_gross, "image/jpeg"
        )
    assert speicher.speichern_count == 0


def test_prueflauf_fehlt():
    repo = InMemoryPrueflaufRepository()
    speicher = SpyDateiSpeicher()
    with pytest.raises(PrueflaufNichtGefunden):
        FotoNachweisErfassen(repo, speicher).execute("fehlt", "schritt-a", JPEG_BYTES, "image/jpeg")
    assert speicher.speichern_count == 0


def test_schritt_fehlt():
    repo = InMemoryPrueflaufRepository()
    speicher = SpyDateiSpeicher()
    prueflauf_id, _ = _setup_prueflauf(repo)
    with pytest.raises(InvariantViolation):
        FotoNachweisErfassen(repo, speicher).execute(
            prueflauf_id, "fehlt", JPEG_BYTES, "image/jpeg"
        )
    assert speicher.speichern_count == 0


def test_prueflauf_abgeschlossen():
    repo = InMemoryPrueflaufRepository()
    speicher = SpyDateiSpeicher()
    prueflauf_id, schritt_id = _setup_prueflauf(repo)
    prueflauf = repo.get(prueflauf_id)
    assert prueflauf is not None
    prueflauf.durchfuehrungen[schritt_id].beurteilung = Beurteilung(
        ergebnis=BeurteilungErgebnis.BESTANDEN,
        festgelegt_am=prueflauf.gestartet_am,
    )
    prueflauf.abschliessen(frozenset())
    repo.save(prueflauf)
    with pytest.raises(InvariantViolation):
        FotoNachweisErfassen(repo, speicher).execute(
            prueflauf_id, schritt_id, JPEG_BYTES, "image/jpeg"
        )
    assert speicher.speichern_count == 0


def test_storage_fehler():
    repo = InMemoryPrueflaufRepository()
    prueflauf_id, schritt_id = _setup_prueflauf(repo)
    with pytest.raises(DateiSpeicherungFehlgeschlagen):
        FotoNachweisErfassen(repo, FailingDateiSpeicher()).execute(
            prueflauf_id, schritt_id, JPEG_BYTES, "image/jpeg"
        )


def test_compensation_nach_repo_save_fehler():
    repo = InMemoryPrueflaufRepository()
    prueflauf_id, schritt_id = _setup_prueflauf(repo)
    speicher = SpyDateiSpeicher()
    failing_repo = FailingPrueflaufRepository(inner=repo)
    with pytest.raises(DateiSpeicherungFehlgeschlagen):
        FotoNachweisErfassen(failing_repo, speicher).execute(
            prueflauf_id, schritt_id, JPEG_BYTES, "image/jpeg"
        )
    assert speicher.speichern_count == 1
    assert speicher.loeschen_count == 1


def test_compensation_fehler_verdeckt_hauptfehler_nicht():
    repo = InMemoryPrueflaufRepository()
    prueflauf_id, schritt_id = _setup_prueflauf(repo)

    class FailingLoeschenSpeicher(SpyDateiSpeicher):
        def loeschen(self, datei_id: str) -> None:
            self.loeschen_count += 1
            raise DateiSpeicherFehler("cleanup fail")

    speicher = FailingLoeschenSpeicher()
    failing_repo = FailingPrueflaufRepository(inner=repo)
    with pytest.raises(DateiSpeicherungFehlgeschlagen):
        FotoNachweisErfassen(failing_repo, speicher).execute(
            prueflauf_id, schritt_id, JPEG_BYTES, "image/jpeg"
        )
    assert speicher.loeschen_count == 1
