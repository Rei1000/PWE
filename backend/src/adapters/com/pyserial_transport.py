"""PySerial-Implementierung von SeriellerTransport (Gate 7.3c)."""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

from adapters.com.errors import (
    TransportConnectionError,
    TransportIOError,
    TransportTimeout,
)

logger = logging.getLogger(__name__)

SerialFactory = Callable[..., Any]


def _require_pyserial() -> Any:
    try:
        import serial  # type: ignore[import-untyped]
    except ImportError as exc:
        raise TransportConnectionError(
            "PySerial ist nicht installiert. Für EXTERNES_KOMMANDO_ADAPTER=com "
            "bitte das Backend-Extra [com] installieren."
        ) from exc
    return serial


class PySerialTransport:
    """Öffnet den seriellen Port pro Kommando, sendet Payload und liest eine Zeile."""

    def __init__(
        self,
        *,
        port: str,
        baudrate: int,
        timeout_ms: int,
        serial_factory: SerialFactory | None = None,
    ) -> None:
        self._port = port
        self._baudrate = baudrate
        self._timeout_s = timeout_ms / 1000.0
        self._serial_factory = serial_factory or _default_serial_factory

    def send_and_receive(self, payload: bytes) -> bytes:
        serial_module = _require_pyserial()
        connection = None
        logger.debug(
            "COM transport opening port=%s baudrate=%s timeout_ms=%s payload_bytes=%s",
            self._port,
            self._baudrate,
            int(self._timeout_s * 1000),
            len(payload),
        )
        try:
            connection = self._serial_factory(
                port=self._port,
                baudrate=self._baudrate,
                timeout=self._timeout_s,
            )
            connection.write(payload)
            response = connection.readline()
            if response == b"":
                logger.warning(
                    "COM transport timeout port=%s baudrate=%s",
                    self._port,
                    self._baudrate,
                )
                raise TransportTimeout(
                    f"Keine Antwort innerhalb von {int(self._timeout_s * 1000)} ms"
                )
            logger.debug(
                "COM transport received bytes=%s port=%s",
                len(response),
                self._port,
            )
            return response
        except TransportTimeout:
            raise
        except serial_module.SerialException as exc:
            message = str(exc).lower()
            if "could not open port" in message or "permission" in message or "no such file" in message:
                logger.warning(
                    "COM transport connection error port=%s error_class=%s",
                    self._port,
                    type(exc).__name__,
                )
                raise TransportConnectionError(str(exc)) from exc
            logger.warning(
                "COM transport io error port=%s error_class=%s",
                self._port,
                type(exc).__name__,
            )
            raise TransportIOError(str(exc)) from exc
        finally:
            if connection is not None:
                try:
                    if getattr(connection, "is_open", False):
                        connection.close()
                except Exception:
                    logger.warning(
                        "COM transport close failed port=%s",
                        self._port,
                        exc_info=True,
                    )


def _default_serial_factory(*, port: str, baudrate: int, timeout: float) -> Any:
    serial_module = _require_pyserial()
    return serial_module.Serial(port=port, baudrate=baudrate, timeout=timeout)
