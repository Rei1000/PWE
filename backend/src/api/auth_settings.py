"""Auth-Cookie- und Session-Konfiguration (ADR-0024)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import timedelta

SESSION_COOKIE = "pwe_session"
CSRF_COOKIE = "pwe_csrf"
CSRF_HEADER = "X-CSRF-Token"


@dataclass(frozen=True)
class AuthCookieSettings:
    secure: bool
    samesite: str
    idle: timedelta
    absolute: timedelta

    @classmethod
    def from_env(cls) -> AuthCookieSettings:
        secure = os.environ.get("PWE_COOKIE_SECURE", "false").strip().lower() in {
            "1",
            "true",
            "yes",
        }
        samesite = os.environ.get("PWE_COOKIE_SAMESITE", "lax").strip().lower() or "lax"
        if samesite not in {"lax", "strict"}:
            samesite = "lax"
        idle_min = int(os.environ.get("PWE_SESSION_IDLE_MINUTES", "60"))
        abs_hours = int(os.environ.get("PWE_SESSION_ABSOLUTE_HOURS", "12"))
        return cls(
            secure=secure,
            samesite=samesite,
            idle=timedelta(minutes=max(1, idle_min)),
            absolute=timedelta(hours=max(1, abs_hours)),
        )
