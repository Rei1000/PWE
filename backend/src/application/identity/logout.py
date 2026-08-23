"""Use Case — Logout (Gate 8.1a)."""

from __future__ import annotations

from dataclasses import dataclass

from ports.session_store import SessionStore


@dataclass
class Logout:
    sessions: SessionStore

    def execute(self, *, session_id: str | None) -> None:
        if session_id:
            self.sessions.loeschen(session_id)
