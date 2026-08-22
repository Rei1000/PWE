"""Test-Bausteine für Foto-Nachweis (Gate 8.3a)."""

from __future__ import annotations

from adapters.persistence.in_memory import InMemoryKatalogRepository, InMemoryPrueflaufRepository
from domain.katalog.version import MaterialisierterProzedurSchritt, ProduktdefinitionsVersion
from domain.pruefausfuehrung.prueflauf import Prueflauf

JPEG_BYTES = b"\xff\xd8\xff\xe0" + b"\x00" * 32
PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"\x00" * 32


def setup_prueflauf_mit_schritt(repo: InMemoryPrueflaufRepository) -> tuple[str, str]:
    katalog = InMemoryKatalogRepository()
    version = ProduktdefinitionsVersion(
        version_id="ver-1",
        produktdefinition_id="pd-1",
        produktkodierung="1234567890",
        prozedur_schritte=(
            MaterialisierterProzedurSchritt(
                schritt_id="schritt-a",
                vorlage_id="vorlage-a",
                ist_pflicht=True,
                reihenfolge=1,
                sollvorgaben={},
            ),
        ),
    )
    katalog.register_aktive_version(version)
    prueflauf = Prueflauf.starten(
        version_id=version.version_id,
        pruefobjekt_kennung="SN-1",
        produktkodierung=version.produktkodierung,
        pruefer_id="pruefer-1",
        prozedur_schritt_ids=["schritt-a"],
    )
    repo.save(prueflauf)
    return prueflauf.prueflauf_id, "schritt-a"
