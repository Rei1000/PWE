"""Gemeinsame Foto-/Datei-Regeln für Domain und Application (ADR-0022)."""

from __future__ import annotations

MAX_FOTO_GROESSE_BYTES = 5 * 1024 * 1024  # 5 MiB

ERLAUBTE_MIME_TYPES: frozenset[str] = frozenset({"image/jpeg", "image/png"})


def erlaubter_mime_type(mime_type: str) -> bool:
    return mime_type in ERLAUBTE_MIME_TYPES


def ist_erlaubte_groesse(groesse_bytes: int) -> bool:
    return 0 < groesse_bytes <= MAX_FOTO_GROESSE_BYTES


def magic_bytes_passen(inhalt: bytes, mime_type: str) -> bool:
    if mime_type == "image/jpeg":
        return len(inhalt) >= 3 and inhalt[:3] == b"\xff\xd8\xff"
    if mime_type == "image/png":
        return len(inhalt) >= 8 and inhalt[:8] == b"\x89PNG\r\n\x1a\n"
    return False
