"""Tests — Kommando-Adapter-Wiring (Composition Root)."""

from __future__ import annotations

import pytest

from adapters.com.externes_kommando import ComExternesKommandoPort
from adapters.simulation.externes_kommando import SimuliertesExternesKommandoPort
from api.kommando_wiring import (
    KommandoAdapterConfigurationError,
    KommandoAdapterSettings,
    configure_kommando_adapter,
    create_kommando_port,
    reset_kommando_adapter_cache_for_tests,
    validate_kommando_adapter_settings,
)


@pytest.fixture(autouse=True)
def _reset_cache():
    reset_kommando_adapter_cache_for_tests()
    yield
    reset_kommando_adapter_cache_for_tests()


def test_default_simulation_adapter(monkeypatch):
    monkeypatch.delenv("EXTERNES_KOMMANDO_ADAPTER", raising=False)

    port = create_kommando_port()

    assert isinstance(port, SimuliertesExternesKommandoPort)


def test_explicit_simulation_adapter(monkeypatch):
    monkeypatch.setenv("EXTERNES_KOMMANDO_ADAPTER", "simulation")

    port = create_kommando_port(
        KommandoAdapterSettings(
            adapter="simulation",
            seriell_port=None,
            seriell_baudrate=9600,
            seriell_timeout_ms=3000,
        )
    )

    assert isinstance(port, SimuliertesExternesKommandoPort)


def test_com_adapter_with_valid_configuration(monkeypatch):
    monkeypatch.setattr(
        "api.kommando_wiring._ensure_pyserial_available",
        lambda: None,
    )

    port = create_kommando_port(
        KommandoAdapterSettings(
            adapter="com",
            seriell_port="/dev/ttyUSB0",
            seriell_baudrate=115200,
            seriell_timeout_ms=2000,
        )
    )

    assert isinstance(port, ComExternesKommandoPort)


def test_unknown_adapter_value_fails_validation():
    settings = KommandoAdapterSettings(
        adapter="can",  # type: ignore[arg-type]
        seriell_port=None,
        seriell_baudrate=9600,
        seriell_timeout_ms=3000,
    )

    with pytest.raises(KommandoAdapterConfigurationError, match="Unbekannter"):
        validate_kommando_adapter_settings(settings)


def test_com_requires_port():
    settings = KommandoAdapterSettings(
        adapter="com",
        seriell_port=None,
        seriell_baudrate=9600,
        seriell_timeout_ms=3000,
    )

    with pytest.raises(KommandoAdapterConfigurationError, match="SERIELL_PORT"):
        validate_kommando_adapter_settings(settings)


def test_com_requires_positive_baudrate():
    settings = KommandoAdapterSettings(
        adapter="com",
        seriell_port="/dev/ttyUSB0",
        seriell_baudrate=0,
        seriell_timeout_ms=3000,
    )

    with pytest.raises(KommandoAdapterConfigurationError, match="SERIELL_BAUDRATE"):
        validate_kommando_adapter_settings(settings)


def test_com_requires_positive_timeout():
    settings = KommandoAdapterSettings(
        adapter="com",
        seriell_port="/dev/ttyUSB0",
        seriell_baudrate=9600,
        seriell_timeout_ms=0,
    )

    with pytest.raises(KommandoAdapterConfigurationError, match="SERIELL_TIMEOUT_MS"):
        validate_kommando_adapter_settings(settings)


def test_com_requires_pyserial_when_missing(monkeypatch):
    import builtins

    real_import = builtins.__import__

    def _import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "serial":
            raise ImportError("No module named 'serial'")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", _import)

    settings = KommandoAdapterSettings(
        adapter="com",
        seriell_port="/dev/ttyUSB0",
        seriell_baudrate=9600,
        seriell_timeout_ms=3000,
    )

    with pytest.raises(KommandoAdapterConfigurationError, match="PySerial"):
        validate_kommando_adapter_settings(settings)


def test_configure_kommando_adapter_caches_settings(monkeypatch):
    monkeypatch.setenv("EXTERNES_KOMMANDO_ADAPTER", "simulation")
    settings = KommandoAdapterSettings.from_env()

    configure_kommando_adapter(settings)
    port = create_kommando_port()

    assert isinstance(port, SimuliertesExternesKommandoPort)


def test_in_memory_deps_use_factory(monkeypatch):
    monkeypatch.setenv("EXTERNES_KOMMANDO_ADAPTER", "simulation")
    configure_kommando_adapter(KommandoAdapterSettings.from_env())

    from api.deps import in_memory_deps

    deps = in_memory_deps()
    assert isinstance(deps.kommando_port, SimuliertesExternesKommandoPort)


def test_postgres_deps_use_factory(monkeypatch):
    monkeypatch.setenv("EXTERNES_KOMMANDO_ADAPTER", "simulation")
    configure_kommando_adapter(KommandoAdapterSettings.from_env())

    from unittest.mock import MagicMock

    from api.persistence import postgres_deps

    deps = postgres_deps(MagicMock())

    assert isinstance(deps.kommando_port, SimuliertesExternesKommandoPort)


def test_kommando_ports_are_not_shared_between_factory_calls(monkeypatch):
    monkeypatch.setenv("EXTERNES_KOMMANDO_ADAPTER", "simulation")
    configure_kommando_adapter(KommandoAdapterSettings.from_env())

    first = create_kommando_port()
    second = create_kommando_port()

    assert first is not second


def test_create_app_start_fails_on_invalid_com_config(monkeypatch):
    from fastapi.testclient import TestClient

    from api.app import create_app
    from api.kommando_wiring import KommandoAdapterConfigurationError

    monkeypatch.setenv("EXTERNES_KOMMANDO_ADAPTER", "com")
    monkeypatch.delenv("SERIELL_PORT", raising=False)

    with pytest.raises(KommandoAdapterConfigurationError, match="SERIELL_PORT"):
        with TestClient(create_app()):
            pass

