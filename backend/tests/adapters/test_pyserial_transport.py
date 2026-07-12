"""Tests — PySerialTransport (ohne Hardware)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from adapters.com.errors import (
    TransportConnectionError,
    TransportIOError,
    TransportTimeout,
)
from adapters.com.pyserial_transport import PySerialTransport


class _FakeSerialException(Exception):
    pass


def _make_serial_module(*, readline_return: bytes = b"OK\n", exc: Exception | None = None):
    serial_module = MagicMock()
    serial_module.SerialException = _FakeSerialException

    connection = MagicMock()
    connection.is_open = True
    if exc is not None:
        connection.write.side_effect = exc
        connection.readline.side_effect = exc
    else:
        connection.readline.return_value = readline_return

    serial_module.Serial.return_value = connection
    return serial_module, connection


def test_pyserial_transport_send_and_receive_success(monkeypatch):
    serial_module, connection = _make_serial_module(readline_return=b"OK spannung=230\n")
    monkeypatch.setattr(
        "adapters.com.pyserial_transport._require_pyserial",
        lambda: serial_module,
    )

    transport = PySerialTransport(port="/dev/ttyUSB0", baudrate=9600, timeout_ms=1000)
    response = transport.send_and_receive(b"READ_VOLTAGE\r\n")

    assert response == b"OK spannung=230\n"
    connection.write.assert_called_once_with(b"READ_VOLTAGE\r\n")
    connection.close.assert_called_once()


def test_pyserial_transport_timeout_on_empty_response(monkeypatch):
    serial_module, _connection = _make_serial_module(readline_return=b"")
    monkeypatch.setattr(
        "adapters.com.pyserial_transport._require_pyserial",
        lambda: serial_module,
    )

    transport = PySerialTransport(port="/dev/ttyUSB0", baudrate=9600, timeout_ms=500)

    with pytest.raises(TransportTimeout):
        transport.send_and_receive(b"READ_VOLTAGE\r\n")


def test_pyserial_transport_connection_error(monkeypatch):
    serial_module, _connection = _make_serial_module(
        exc=_FakeSerialException("could not open port /dev/ttyUSB0"),
    )
    monkeypatch.setattr(
        "adapters.com.pyserial_transport._require_pyserial",
        lambda: serial_module,
    )

    transport = PySerialTransport(port="/dev/ttyUSB0", baudrate=9600, timeout_ms=500)

    with pytest.raises(TransportConnectionError):
        transport.send_and_receive(b"READ_VOLTAGE\r\n")


def test_pyserial_transport_io_error(monkeypatch):
    serial_module, _connection = _make_serial_module(
        exc=_FakeSerialException("device reports readiness to read but returned no data"),
    )
    monkeypatch.setattr(
        "adapters.com.pyserial_transport._require_pyserial",
        lambda: serial_module,
    )

    transport = PySerialTransport(port="/dev/ttyUSB0", baudrate=9600, timeout_ms=500)

    with pytest.raises(TransportIOError):
        transport.send_and_receive(b"READ_VOLTAGE\r\n")


def test_pyserial_transport_closes_connection_on_error(monkeypatch):
    serial_module, connection = _make_serial_module(
        exc=_FakeSerialException("write failed"),
    )
    monkeypatch.setattr(
        "adapters.com.pyserial_transport._require_pyserial",
        lambda: serial_module,
    )

    transport = PySerialTransport(port="/dev/ttyUSB0", baudrate=9600, timeout_ms=500)

    with pytest.raises(TransportIOError):
        transport.send_and_receive(b"READ_VOLTAGE\r\n")

    connection.close.assert_called_once()


def test_pyserial_transport_requires_pyserial(monkeypatch):
    def _missing_pyserial():
        raise TransportConnectionError(
            "PySerial ist nicht installiert. Für EXTERNES_KOMMANDO_ADAPTER=com "
            "bitte das Backend-Extra [com] installieren."
        )

    monkeypatch.setattr(
        "adapters.com.pyserial_transport._require_pyserial",
        _missing_pyserial,
    )

    transport = PySerialTransport(port="/dev/ttyUSB0", baudrate=9600, timeout_ms=500)

    with pytest.raises(TransportConnectionError, match="PySerial"):
        transport.send_and_receive(b"READ_VOLTAGE\r\n")
