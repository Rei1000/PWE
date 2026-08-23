"""Identity — Systemrollen und Benutzerstatus (ADR-0023 / ADR-0025)."""

from __future__ import annotations

from enum import Enum


class Systemrolle(str, Enum):
    ADMINISTRATOR = "administrator"
    QM = "qm"
    ABTEILUNGSLEITER = "abteilungsleiter"
    PRUEFER = "pruefer"


class BenutzerStatus(str, Enum):
    NEU = "neu"
    AKTIV = "aktiv"
    GESPERRT = "gesperrt"
    ARCHIVIERT = "archiviert"
