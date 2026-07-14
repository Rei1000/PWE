"""In-Memory-Repositories für Vertical Slices."""

from __future__ import annotations

from domain.katalog.externes_kommando import ExternesKommando
from domain.katalog.routine import Routine
from domain.katalog.produktdefinition import Produktdefinition
from domain.katalog.version import ProduktdefinitionsVersion
from domain.pruefausfuehrung.prueflauf import Prueflauf
from domain.protokoll.snapshot import ProtokollSnapshot
from domain.shared.errors import UnveraenderlichesObjektBereitsVorhanden


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
        if version.version_id in self._versionen:
            raise UnveraenderlichesObjektBereitsVorhanden(
                f"ProduktdefinitionsVersion {version.version_id} existiert bereits"
            )
        self._versionen[version.version_id] = version
        self._aktive_versionen[version.produktkodierung] = version

    def get_entwurf(self, produktdefinition_id: str) -> Produktdefinition | None:
        return self._entwuerfe.get(produktdefinition_id)

    def save_entwurf(self, entwurf: Produktdefinition) -> None:
        self._entwuerfe[entwurf.produktdefinition_id] = entwurf


class InMemoryBibliothekRepository:
    def __init__(self) -> None:
        self._kommandos: dict[str, ExternesKommando] = {}
        self._routinen: dict[str, Routine] = {}

    def save_externes_kommando(self, kommando: ExternesKommando) -> None:
        self._kommandos[kommando.kommando_id] = kommando

    def get_externes_kommando(self, kommando_id: str) -> ExternesKommando | None:
        return self._kommandos.get(kommando_id)

    def save_routine(self, routine: Routine) -> None:
        self._routinen[routine.routine_id] = routine

    def get_routine(self, routine_id: str) -> Routine | None:
        return self._routinen.get(routine_id)


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
        if snapshot.prueflauf_id in self._by_prueflauf:
            raise UnveraenderlichesObjektBereitsVorhanden(
                f"ProtokollSnapshot für Prüflauf {snapshot.prueflauf_id} existiert bereits"
            )
        self._by_prueflauf[snapshot.prueflauf_id] = snapshot

    def get_by_prueflauf(self, prueflauf_id: str) -> ProtokollSnapshot | None:
        return self._by_prueflauf.get(prueflauf_id)
