"""Wiederverwendbare Test-Bausteine."""

from __future__ import annotations

from adapters.persistence.in_memory import InMemoryProtokollRepository, InMemoryPrueflaufRepository
from adapters.persistence.in_memory_abschluss import InMemoryPrueflaufAbschlussPersistenz


def in_memory_abschluss_persistenz(
    prueflauf_repo: InMemoryPrueflaufRepository,
    protokoll_repo: InMemoryProtokollRepository,
) -> InMemoryPrueflaufAbschlussPersistenz:
    return InMemoryPrueflaufAbschlussPersistenz(
        prueflauf_repo=prueflauf_repo,
        protokoll_repo=protokoll_repo,
    )
