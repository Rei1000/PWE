"""HTTP-Fehlerabbildung — stabile Codes und öffentliche Meldungen."""

from __future__ import annotations

import re

from domain.shared.errors import DomainError, InvariantViolation


def domain_error_code(exc: DomainError) -> str:
    if isinstance(exc, InvariantViolation):
        return "invariant_verletzt"
    name = type(exc).__name__
    if name == "DomainError":
        return "domain"
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def http_status_for_domain_error(exc: DomainError) -> int:
    if isinstance(exc, InvariantViolation):
        return 409
    if type(exc).__name__.endswith("NichtGefunden"):
        return 404
    return 409


def oeffentliche_fehlermeldung(exc: DomainError) -> str:
    if isinstance(exc, InvariantViolation):
        return "Die Aktion ist im aktuellen Zustand nicht zulässig."
    name = type(exc).__name__
    if name == "PrueflaufNichtGefunden":
        return "Der angeforderte Prüflauf wurde nicht gefunden."
    if name == "VersionNichtGefunden":
        return "Die referenzierte Produktdefinitionsversion wurde nicht gefunden."
    if name == "VersionNichtAufloesbar":
        return "Die Produktdefinitionsversion des Prüflaufs ist nicht verfügbar."
    if name.endswith("NichtGefunden"):
        return "Die angeforderte Ressource wurde nicht gefunden."
    return "Die Anfrage konnte aus fachlichen Gründen nicht verarbeitet werden."


def fehler_response(*, detail: str, code: str) -> dict[str, str]:
    return {"detail": detail, "code": code}
