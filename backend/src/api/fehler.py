"""Stabiles API-Fehlerformat — klein, ohne Framework."""

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


def fehler_response(*, detail: str, code: str) -> dict[str, str]:
    return {"detail": detail, "code": code}
