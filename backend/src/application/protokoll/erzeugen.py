"""Use Case: Protokolldokument aus gespeichertem Snapshot erzeugen."""

from __future__ import annotations

from dataclasses import dataclass

from domain.protokoll.dokument import ProtokollDokument
from domain.shared.errors import DomainError
from ports.protokoll_erzeugung_port import ProtokollErzeugungPort
from ports.protokoll_repository import ProtokollRepository


class SnapshotNichtGefunden(DomainError):
    pass


@dataclass
class ProtokollErzeugen:
    protokoll_repo: ProtokollRepository
    erzeugung_port: ProtokollErzeugungPort

    def execute(self, prueflauf_id: str) -> ProtokollDokument:
        snapshot = self.protokoll_repo.get_by_prueflauf(prueflauf_id)
        if snapshot is None:
            raise SnapshotNichtGefunden(prueflauf_id)
        return self.erzeugung_port.erzeugen(snapshot)
