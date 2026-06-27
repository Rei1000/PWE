"""Ports — Protokoll."""

from __future__ import annotations

from typing import Protocol

from domain.protokoll.snapshot import ProtokollSnapshot


class ProtokollRepository(Protocol):
    def save(self, snapshot: ProtokollSnapshot) -> None: ...

    def get_by_prueflauf(self, prueflauf_id: str) -> ProtokollSnapshot | None: ...
