"""Serieller Transport — technische Abstraktion für COM-Adapter."""

from __future__ import annotations

from typing import Protocol


class SeriellerTransport(Protocol):
    def send_and_receive(self, payload: bytes) -> bytes: ...
