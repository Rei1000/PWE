"""In-Memory-Repositories für Vertical Slices."""

from __future__ import annotations

from domain.katalog.produktdefinition import Produktdefinition
from domain.katalog.version import ProduktdefinitionsVersion
from domain.pruefausfuehrung.prueflauf import Prueflauf
from domain.protokoll.snapshot import ProtokollSnapshot


class InMemoryKatalogRepository:
    def __init__(self) -> None:
        self._aktive_versionen: dict[str, ProduktdefinitionsVersion] = {}
        self._versionen: dict[str, ProduktdefinitionsVersion] = {}
        self._entwuerfe: dict[str, Produktdefinition] = {}

    def register_aktive_version(self, version: ProduktdefinitionsVersion) -> None:
        self.save_version(version)

    def get_aktive_version_fuer_kodierung(
        self, produktkodierung: str
    ) -> ProduktdefinitionsVersion | None:
        return self._aktive_versionen.get(produktkodierung)

    def get_version(self, version_id: str) -> ProduktdefinitionsVersion | None:
        return self._versionen.get(version_id)

    def save_version(self, version: ProduktdefinitionsVersion) -> None:
        self._versionen[version.version_id] = version
        self._aktive_versionen[version.produktkodierung] = version

    def get_entwurf(self, produktdefinition_id: str) -> Produktdefinition | None:
        return self._entwuerfe.get(produktdefinition_id)

    def save_entwurf(self, entwurf: Produktdefinition) -> None:
        self._entwuerfe[entwurf.produktdefinition_id] = entwurf


class InMemoryPrueflaufRepository:
    def __init__(self) -> None:
        self._store: dict[str, Prueflauf] = {}

    def save(self, prueflauf: Prueflauf) -> None:
        self._store[prueflauf.prueflauf_id] = prueflauf

    def get(self, prueflauf_id: str) -> Prueflauf | None:
        return self._store.get(prueflauf_id)


class InMemoryProtokollRepository:
    def __init__(self) -> None:
        self._by_prueflauf: dict[str, ProtokollSnapshot] = {}

    def save(self, snapshot: ProtokollSnapshot) -> None:
        self._by_prueflauf[snapshot.prueflauf_id] = snapshot

    def get_by_prueflauf(self, prueflauf_id: str) -> ProtokollSnapshot | None:
        return self._by_prueflauf.get(prueflauf_id)
