"""DataUpdateCoordinator für die Blustream Integration.

Hält den gemeinsamen Zustand für alle Entitäten. Der Zustand ist primär
"optimistisch": Wenn HA einen Befehl sendet, wird der Zustand sofort
aktualisiert. Das seltene STATUS-Polling (alle 5 Minuten) zieht externe
Änderungen nach, sofern es die Antwort des Geräts interpretieren kann.
"""
from __future__ import annotations

import logging
import re
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api import BlustreamClient
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Startwerte, bis das Gerät erstmals etwas Verwertbares zurückmeldet.
DEFAULT_STATE = {
    "power": True,      # System-Power (PON/POFF)
    "source": 1,        # aktiver Eingang (FR-Code 1-6)
    "volume": 50,       # 0-100
    "mute": False,
    "out1": True,       # Ausgang 1 an/aus
    "out2": True,       # Ausgang 2 an/aus
    "auto": False,      # Auto-Umschaltung
    "mic_mute": False,
    "mic_vol": 50,
    "mic_mix": "ON",
    "resolution": "18",  # Auto
}


class BlustreamCoordinator(DataUpdateCoordinator):
    """Koordiniert Befehle und Status-Abfragen für ein Blustream-Gerät."""

    def __init__(
        self, hass: HomeAssistant, client: BlustreamClient, scan_interval: int
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
        self.client = client
        # Anfangszustand setzen, damit Entitäten sofort Werte haben.
        self.data = dict(DEFAULT_STATE)

    async def _async_update_data(self) -> dict:
        """Wird im Polling-Takt aufgerufen. Fragt STATUS ab."""
        text = await self.client.async_query("STATUS")
        # Bekannten (optimistischen) Zustand als Basis behalten.
        state = dict(self.data)
        if text:
            self._parse_status(text, state)
        return state

    async def async_send(self, command: str, **changes) -> bool:
        """Sendet einen Befehl und aktualisiert den Zustand optimistisch."""
        ok = await self.client.async_send_command(command)
        if ok and changes:
            new_state = dict(self.data)
            new_state.update(changes)
            self.async_set_updated_data(new_state)
        return ok

    # ------------------------------------------------------------------
    # Best-Effort STATUS-Parser
    # ------------------------------------------------------------------
    # Das genaue Ausgabeformat des STATUS-Befehls ist nicht öffentlich
    # dokumentiert. Dieser Parser ist daher bewusst tolerant: Er
    # aktualisiert nur Felder, bei denen er ein eindeutiges Muster findet,
    # und lässt alles andere auf dem optimistischen Wert stehen.
    #
    # ==> Zum exakten Anpassen: Debug-Logging aktivieren (siehe README),
    #     die rohe STATUS-Ausgabe aus dem Log kopieren und die folgenden
    #     regulären Ausdrücke entsprechend justieren.
    # ------------------------------------------------------------------
    @staticmethod
    def _parse_status(text: str, state: dict) -> None:
        up = text.upper()

        # Quelle: "OUT 01 FR 02" / "OUT01FR02" o. ä.
        try:
            match = re.search(r"OUT\s*0*\d+\s*FR\s*0*(\d+)", up)
            if match:
                state["source"] = int(match.group(1))
        except (ValueError, TypeError):
            pass

        # System-Power
        if re.search(r"POWER\D*OFF|\bPOFF\b|STANDBY|POWER\s*SAVE", up):
            state["power"] = False
        elif re.search(r"POWER\D*ON|\bPON\b", up):
            state["power"] = True

        # Lautstärke: "VOL 50"
        try:
            match = re.search(r"\bVOL\D*(\d{1,3})", up)
            if match:
                state["volume"] = min(100, int(match.group(1)))
        except (ValueError, TypeError):
            pass

        # Mute
        if re.search(r"\bMUTE\D*ON\b", up):
            state["mute"] = True
        elif re.search(r"\bMUTE\D*OFF\b", up):
            state["mute"] = False

        # Ausgänge an/aus: "OUT 01 ON" / "OUT 02 OFF"
        for out_id in (1, 2):
            match = re.search(rf"OUT\s*0*{out_id}\D{{0,4}}(ON|OFF)\b", up)
            if match:
                state[f"out{out_id}"] = match.group(1) == "ON"
