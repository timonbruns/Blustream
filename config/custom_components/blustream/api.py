"""Asynchrone Kommunikation mit der Blustream Hardware.

Ersetzt das alte, blockierende telnetlib (welches in Python 3.13 entfernt
wurde) durch eine reine asyncio-Verbindung. Dadurch entstehen keine
Thread-Sicherheits-Probleme mehr und die Integration bleibt zukunftssicher.
"""
from __future__ import annotations

import asyncio
import logging

_LOGGER = logging.getLogger(__name__)

# Alle Befehle werden mit Carriage Return abgeschlossen (laut MFP62-Handbuch).
TERMINATOR = "\r"
CONNECT_TIMEOUT = 5.0


class BlustreamClient:
    """Schlanker TCP/Telnet-Client für Blustream-Geräte."""

    def __init__(self, host: str, port: int) -> None:
        self._host = host
        self._port = port
        # Verhindert, dass mehrere Befehle gleichzeitig dieselbe
        # (kurzlebige) Verbindung öffnen.
        self._lock = asyncio.Lock()

    async def async_send_command(self, command: str) -> bool:
        """Sendet einen Befehl ohne auf eine Antwort zu warten."""
        async with self._lock:
            writer = None
            try:
                _reader, writer = await asyncio.wait_for(
                    asyncio.open_connection(self._host, self._port),
                    timeout=CONNECT_TIMEOUT,
                )
                writer.write(f"{command}{TERMINATOR}".encode("ascii"))
                await writer.drain()
                _LOGGER.debug("Befehl gesendet an %s: %s", self._host, command)
                return True
            except (OSError, asyncio.TimeoutError) as err:
                _LOGGER.error(
                    "Verbindungsfehler zu %s:%s - %s", self._host, self._port, err
                )
                return False
            finally:
                await self._close(writer)

    async def async_query(self, command: str, read_window: float = 1.5) -> str | None:
        """Sendet einen Befehl und liest die Antwort des Geräts.

        Es wird gelesen, bis innerhalb von ``read_window`` Sekunden keine
        weiteren Daten mehr eintreffen.
        """
        async with self._lock:
            writer = None
            try:
                reader, writer = await asyncio.wait_for(
                    asyncio.open_connection(self._host, self._port),
                    timeout=CONNECT_TIMEOUT,
                )
                writer.write(f"{command}{TERMINATOR}".encode("ascii"))
                await writer.drain()

                buffer = bytearray()
                try:
                    while True:
                        chunk = await asyncio.wait_for(
                            reader.read(1024), timeout=read_window
                        )
                        if not chunk:
                            break
                        buffer.extend(chunk)
                except asyncio.TimeoutError:
                    # Kein weiteres Datenpaket -> Antwort gilt als vollständig.
                    pass

                text = buffer.decode("ascii", errors="ignore")
                _LOGGER.debug("Antwort auf '%s' von %s:\n%s", command, self._host, text)
                return text
            except (OSError, asyncio.TimeoutError) as err:
                _LOGGER.error(
                    "Abfragefehler zu %s:%s - %s", self._host, self._port, err
                )
                return None
            finally:
                await self._close(writer)

    @staticmethod
    async def _close(writer) -> None:
        """Schließt die Verbindung sauber."""
        if writer is None:
            return
        try:
            writer.close()
            await writer.wait_closed()
        except (OSError, asyncio.TimeoutError):
            pass
