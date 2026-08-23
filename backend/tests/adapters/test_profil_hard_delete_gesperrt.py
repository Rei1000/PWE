"""Domain — Profil Hard-Delete gesperrt (Gate 8.1c1)."""

from __future__ import annotations

import pytest

from adapters.persistence.in_memory_identity import InMemoryBerechtigungsprofilRepository
from domain.identity.berechtigungsprofil import Berechtigungsprofil
from domain.shared.errors import InvariantViolation


def test_profil_hard_delete_via_repository_abgelehnt():
    repo = InMemoryBerechtigungsprofilRepository()
    profil = Berechtigungsprofil.anlegen(bezeichnung="X", produktdefinition_ids={"pd-1"})
    repo.save(profil)
    with pytest.raises(InvariantViolation, match="nicht hart gelöscht"):
        repo.delete(profil.profil_id)
    assert repo.get(profil.profil_id) is not None
