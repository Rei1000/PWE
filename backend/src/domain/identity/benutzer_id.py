"""BenutzerId Value Object (ADR-0023) — Gate 8.1a."""

from __future__ import annotations

from dataclasses import dataclass

from domain.shared.errors import InvariantViolation


@dataclass(frozen=True)
class BenutzerId:
    """Opaque Benutzer-Identität — zwischen Contexts nur als ID-String."""

    wert: str

    def __post_init__(self) -> None:
        if not self.wert.strip():
            raise InvariantViolation("BenutzerId darf nicht leer sein")

    def __str__(self) -> str:
        return self.wert
