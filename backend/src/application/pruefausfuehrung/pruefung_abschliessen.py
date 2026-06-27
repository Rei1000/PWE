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
        pflicht_map = {s.schritt_id: s.ist_pflicht for s in version.prozedur_schritte}

        prueflauf.abschliessen(version.pflicht_schritt_ids(), version.sollbestueckung)
        self.prueflauf_repo.save(prueflauf)

        view = prueflauf.to_abschluss_view(pflicht_map)
        snapshot = ProtokollSnapshot.aus_abschluss(str(uuid4()), view)
        self.protokoll_repo.save(snapshot)
        return prueflauf, snapshot

    def _version_fuer_prueflauf(self, prueflauf: Prueflauf) -> ProduktdefinitionsVersion:
        version = self.katalog.get_version(prueflauf.version_id)
        if version is None:
            raise DomainError("Version des Prüflaufs nicht mehr im Katalog auffindbar")
        return version
