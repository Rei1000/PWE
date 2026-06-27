"""Use Case: Prüfung starten."""

from __future__ import annotations

from dataclasses import dataclass

from domain.pruefausfuehrung.prueflauf import Prueflauf
from domain.shared.errors import DomainError
from ports.katalog_repository import KatalogRepository
from ports.prueflauf_repository import PrueflaufRepository


class VersionNichtGefunden(DomainError):
    pass


@dataclass
class PruefungStarten:
    katalog: KatalogRepository
    prueflauf_repo: PrueflaufRepository

    def execute(
        self,
        *,
        produktkodierung: str,
        pruefobjekt_kennung: str,
        pruefer_id: str,
    ) -> Prueflauf:
        version = self.katalog.get_aktive_version_fuer_kodierung(produktkodierung)
        if version is None:
            raise VersionNichtGefunden(f"Keine aktive Version für {produktkodierung}")

        schritt_ids = [s.schritt_id for s in version.aktive_schritte()]
        prueflauf = Prueflauf.starten(
            version_id=version.version_id,
            pruefobjekt_kennung=pruefobjekt_kennung,
            produktkodierung=produktkodierung,
            pruefer_id=pruefer_id,
            prozedur_schritt_ids=schritt_ids,
        )
        self.prueflauf_repo.save(prueflauf)
        return prueflauf
