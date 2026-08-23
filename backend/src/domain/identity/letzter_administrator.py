"""Identity — Letzter-Administrator-Invariante (Gate 8.1c1)."""

from __future__ import annotations

from domain.identity.benutzer import Benutzer
from domain.shared.errors import DomainError


class LetzterAdministratorVerletzt(DomainError):
    """Mutation würde keinen aktiven Administrator mehr belassen."""


def assert_mindestens_ein_aktiver_administrator(
    benutzer_liste: list[Benutzer] | tuple[Benutzer, ...],
) -> None:
    """Wirft, wenn kein Benutzer Status Aktiv und Rolle Administrator hat."""
    if any(b.ist_aktiver_administrator() for b in benutzer_liste):
        return
    raise LetzterAdministratorVerletzt(
        "Mindestens ein aktiver Administrator muss erhalten bleiben"
    )


def assert_mutation_behaelt_aktiven_administrator(
    *,
    alle_benutzer: list[Benutzer] | tuple[Benutzer, ...],
    geaenderter: Benutzer,
) -> None:
    """Ersetzt den geänderten Benutzer in der Menge und prüft die Invariante."""
    ersetzt = [
        geaenderter if b.benutzer_id == geaenderter.benutzer_id else b for b in alle_benutzer
    ]
    if not any(b.benutzer_id == geaenderter.benutzer_id for b in alle_benutzer):
        ersetzt = list(alle_benutzer) + [geaenderter]
    assert_mindestens_ein_aktiver_administrator(ersetzt)
