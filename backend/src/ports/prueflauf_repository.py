"""Ports — Prüfausführung."""

from __future__ import annotations

from typing import Protocol

from domain.pruefausfuehrung.prueflauf import Prueflauf


class PrueflaufRepository(Protocol):
    def save(self, prueflauf: Prueflauf) -> None: ...

    def get(self, prueflauf_id: str) -> Prueflauf | None: ...
