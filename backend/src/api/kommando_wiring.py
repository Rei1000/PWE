"""Composition Root — Auswahl und Erzeugung des ExternesKommandoPort."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Literal

from adapters.com.externes_kommando import ComExternesKommandoPort
from adapters.com.pyserial_transport import PySerialTransport
from adapters.simulation.externes_kommando import SimuliertesExternesKommandoPort
from ports.externes_kommando_port import ExternesKommandoPort

logger = logging.getLogger(__name__)

KommandoAdapterMode = Literal["simulation", "com"]

_settings_cache: KommandoAdapterSettings | None = None


class KommandoAdapterConfigurationError(RuntimeError):
    """Ungültige oder unvollständige Konfiguration für den Kommando-Adapter."""


@dataclass(frozen=True)
class KommandoAdapterSettings:
    adapter: KommandoAdapterMode
    seriell_port: str | None
    seriell_baudrate: int
    seriell_timeout_ms: int

    @classmethod
    def from_env(cls) -> KommandoAdapterSettings:
        adapter_raw = os.environ.get("EXTERNES_KOMMANDO_ADAPTER", "simulation").strip().lower()
        if adapter_raw not in ("simulation", "com"):
            return cls(
                adapter=adapter_raw,  # type: ignore[arg-type]
                seriell_port=None,
                seriell_baudrate=0,
                seriell_timeout_ms=0,
            )

        port_raw = os.environ.get("SERIELL_PORT")
        port = port_raw.strip() if port_raw and port_raw.strip() else None

        baudrate = _parse_positive_int(os.environ.get("SERIELL_BAUDRATE"), default=9600)
        timeout_ms = _parse_positive_int(os.environ.get("SERIELL_TIMEOUT_MS"), default=3000)

        return cls(
            adapter=adapter_raw,  # type: ignore[arg-type]
            seriell_port=port,
            seriell_baudrate=baudrate,
            seriell_timeout_ms=timeout_ms,
        )


def configure_kommando_adapter(settings: KommandoAdapterSettings) -> None:
    """Validiert und cached die Adapter-Konfiguration (App-Start)."""
    validate_kommando_adapter_settings(settings)
    global _settings_cache
    _settings_cache = settings
    logger.info(
        "Kommando-Adapter konfiguriert adapter=%s port=%s baudrate=%s timeout_ms=%s",
        settings.adapter,
        settings.seriell_port or "-",
        settings.seriell_baudrate,
        settings.seriell_timeout_ms,
    )


def reset_kommando_adapter_cache_for_tests() -> None:
    global _settings_cache
    _settings_cache = None


def validate_kommando_adapter_settings(settings: KommandoAdapterSettings) -> None:
    if settings.adapter not in ("simulation", "com"):
        raise KommandoAdapterConfigurationError(
            f"Unbekannter EXTERNES_KOMMANDO_ADAPTER: {settings.adapter!r}. "
            "Erlaubt: simulation, com."
        )

    if settings.adapter == "simulation":
        return

    if not settings.seriell_port:
        raise KommandoAdapterConfigurationError(
            "EXTERNES_KOMMANDO_ADAPTER=com erfordert SERIELL_PORT."
        )
    if settings.seriell_baudrate <= 0:
        raise KommandoAdapterConfigurationError(
            "SERIELL_BAUDRATE muss eine positive Ganzzahl sein."
        )
    if settings.seriell_timeout_ms <= 0:
        raise KommandoAdapterConfigurationError(
            "SERIELL_TIMEOUT_MS muss größer als null sein."
        )
    _ensure_pyserial_available()


def create_kommando_port(
    settings: KommandoAdapterSettings | None = None,
) -> ExternesKommandoPort:
    """Erzeugt den konfigurierten ExternesKommandoPort (request-scoped)."""
    effective = settings or _get_validated_settings()
    if effective.adapter == "simulation":
        return SimuliertesExternesKommandoPort()

    assert effective.seriell_port is not None
    transport = PySerialTransport(
        port=effective.seriell_port,
        baudrate=effective.seriell_baudrate,
        timeout_ms=effective.seriell_timeout_ms,
    )
    return ComExternesKommandoPort(transport)


def _get_validated_settings() -> KommandoAdapterSettings:
    global _settings_cache
    if _settings_cache is None:
        candidate = KommandoAdapterSettings.from_env()
        validate_kommando_adapter_settings(candidate)
        _settings_cache = candidate
    return _settings_cache


def _ensure_pyserial_available() -> None:
    try:
        import serial  # noqa: F401
    except ImportError as exc:
        raise KommandoAdapterConfigurationError(
            "EXTERNES_KOMMANDO_ADAPTER=com erfordert PySerial. "
            'Installation: pip install ".[com]"'
        ) from exc


def _parse_positive_int(raw: str | None, *, default: int) -> int:
    if raw is None or not raw.strip():
        return default
    try:
        return int(raw.strip())
    except ValueError as exc:
        raise KommandoAdapterConfigurationError(
            f"Ungültiger numerischer Konfigurationswert: {raw!r}"
        ) from exc
