"""Use Case: Prüfung abschließen und ProtokollSnapshot erzeugen."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from domain.katalog.version import ProduktdefinitionsVersion
from domain.protokoll.snapshot import ProtokollSnapshot
from domain.pruefausfuehrung.prueflauf import Prueflauf
from domain.shared.errors import DomainError
from ports.katalog_repository import KatalogRepository
from ports.prueflauf_repository import PrueflaufRepository
from ports.protokoll_repository import ProtokollRepository


class PrueflaufNichtGefunden(DomainError):
    pass


@dataclass
class PruefungAbschliessen:
    katalog: KatalogRepository
    prueflauf_repo: PrueflaufRepository
    protokoll_repo: ProtokollRepository

    def execute(self, prueflauf_id: str) -> tuple[Prueflauf, ProtokollSnapshot]:
        prueflauf = self.prueflauf_repo.get(prueflauf_id)
        if prueflauf is None:
            raise PrueflaufNichtGefunden(prueflauf_id)

        version = self._version_fuer_prueflauf(prueflauf)
        pflicht_ids = {s.schritt_id for s in version.prozedur_schritte if s.ist_pflicht}
        pflicht_map = {s.schritt_id: s.ist_pflicht for s in version.prozedur_schritte}

        prueflauf.abschliessen(pflicht_ids)
        self.prueflauf_repo.save(prueflauf)

        snapshot = ProtokollSnapshot.aus_prueflauf(str(uuid4()), prueflauf, pflicht_map)
        self.protokoll_repo.save(snapshot)
        return prueflauf, snapshot

    def _version_fuer_prueflauf(self, prueflauf: Prueflauf) -> ProduktdefinitionsVersion:
        version = self.katalog.get_aktive_version_fuer_kodierung(prueflauf.produktkodierung)
        if version is None or version.version_id != prueflauf.version_id:
            raise DomainError("Version des Prüflaufs nicht mehr im Katalog auffindbar")
        return version
