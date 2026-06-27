"""Port — Protokollerzeugung aus ProtokollSnapshot."""

from __future__ import annotations

from typing import Protocol

from domain.protokoll.dokument import ProtokollDokument
from domain.protokoll.snapshot import ProtokollSnapshot


class ProtokollErzeugungPort(Protocol):
    def erzeugen(self, snapshot: ProtokollSnapshot) -> ProtokollDokument: ...
