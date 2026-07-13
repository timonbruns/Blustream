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
from .const import DOMAIN, MODEL_DA11ABL, MODEL_MFP62

_LOGGER = logging.getLogger(__name__)

# Startwerte je Modell, bis das Gerät erstmals etwas Verwertbares meldet.
DEFAULT_STATE_MFP62 = {
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

DEFAULT_STATE_DA11 = {
    "source": 2,           # IN SOURCE: 1 Analog, 2 Bluetooth
    "out_mute": False,     # OUT MUTE
    "out_gain": "8",       # OUT GAIN 0-15 (0 = höchster Pegel)
    "ana_sens": "8",       # ANA IN SENS 0-15
    "ana_in_mute": False,  # ANA IN MUTE
    "bt_in_mute": False,   # BT IN MUTE
    "bt_pair_mode": "1",   # BT PAIR MODE 0/1/2
    "bt_priority": "0",    # BT PRIORITY 0/1
    "in_priority": "1",    # PRIORITY 1/2
    "bt_timeout": 60,      # BT TIMEOUT 1-999 s
    "auto_sw": 10,         # AUTO SW Sekunden
    "bt_source_1": None,   # Name des verbundenen BT-Geraets 1 (aus STATUS)
    "bt_source_2": None,   # Name des verbundenen BT-Geraets 2 (aus STATUS)
}

MODEL_DEFAULTS = {
    MODEL_MFP62: DEFAULT_STATE_MFP62,
    MODEL_DA11ABL: DEFAULT_STATE_DA11,
}


class BlustreamCoordinator(DataUpdateCoordinator):
    """Koordiniert Befehle und Status-Abfragen für ein Blustream-Gerät."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: BlustreamClient,
        scan_interval: int,
        model: str = MODEL_MFP62,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
        self.client = client
        self.model = model
        # Anfangszustand setzen, damit Entitäten sofort Werte haben.
        self.data = dict(MODEL_DEFAULTS.get(model, DEFAULT_STATE_MFP62))

    async def _async_update_data(self) -> dict:
        """Wird im Polling-Takt aufgerufen. Fragt STATUS ab."""
        text = await self.client.async_query("STATUS")
        # Bekannten (optimistischen) Zustand als Basis behalten.
        state = dict(self.data)
        if text:
            if self.model == MODEL_MFP62:
                self._parse_status_mfp62(text, state)
            elif self.model == MODEL_DA11ABL:
                self._parse_status_da11(text, state)
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
    # Best-Effort STATUS-Parser (MFP62)
    # ------------------------------------------------------------------
    # Das genaue Ausgabeformat ist nicht öffentlich dokumentiert. Die Parser
    # sind daher bewusst tolerant: Sie aktualisieren nur Felder mit
    # eindeutigem Muster und lassen alles andere unangetastet.
    # ------------------------------------------------------------------
    @staticmethod
    def _parse_status_mfp62(text: str, state: dict) -> None:
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

    # ------------------------------------------------------------------
    # Best-Effort STATUS-Parser (DA11ABL-V2)
    # ------------------------------------------------------------------
    @staticmethod
    def _parse_status_da11(text: str, state: dict) -> None:
        up = text.upper()

        # Eingangsquelle: "IN SOURCE 1/2"
        match = re.search(r"IN\s*SOURCE\D*([12])\b", up)
        if match:
            state["source"] = int(match.group(1))

        # Ausgang: Mute + Gain
        match = re.search(r"OUT\s*MUTE\D*(ON|OFF)\b", up)
        if match:
            state["out_mute"] = match.group(1) == "ON"
        match = re.search(r"OUT\s*GAIN\D*(\d{1,2})\b", up)
        if match:
            state["out_gain"] = str(min(15, int(match.group(1))))

        # Analog-Eingang
        match = re.search(r"ANA\s*IN\s*MUTE\D*(ON|OFF)\b", up)
        if match:
            state["ana_in_mute"] = match.group(1) == "ON"
        match = re.search(r"ANA\s*IN\s*SENS\D*(\d{1,2})\b", up)
        if match:
            state["ana_sens"] = str(min(15, int(match.group(1))))

        # Bluetooth
        match = re.search(r"BT\s*IN\s*MUTE\D*(ON|OFF)\b", up)
        if match:
            state["bt_in_mute"] = match.group(1) == "ON"
        match = re.search(r"BT\s*PAIR\s*MODE\D*([012])\b", up)
        if match:
            state["bt_pair_mode"] = match.group(1)
        match = re.search(r"BT\s*PRIORITY\D*([01])\b", up)
        if match:
            state["bt_priority"] = match.group(1)
        match = re.search(r"BT\s*TIMEOUT\D*(\d{1,3})\b", up)
        if match:
            state["bt_timeout"] = int(match.group(1))

        # Prioritäten / Auto-Switch
        match = re.search(r"(?<!BT\s)PRIORITY\D*([12])\b", up)
        if match:
            state["in_priority"] = match.group(1)
        match = re.search(r"AUTO\s*SW\D*(\d{1,3})\b", up)
        if match:
            state["auto_sw"] = int(match.group(1))

        # Verbundene Bluetooth-Geraete: Zeile nach "Bluetooth_Source_N".
        # Getrennt: "Disconnected   Disconnected"
        # Verbunden (erwartet): "<Geraetename>   Connected"
        # Achtung: Gross-/Kleinschreibung des Namens erhalten -> Original-
        # Text verwenden, nicht die Grossbuchstaben-Kopie.
        lines = [ln.strip() for ln in text.splitlines()]
        for idx, line in enumerate(lines):
            match = re.match(r"(?i)^Bluetooth_Source_([12])\b", line)
            if not match or idx + 1 >= len(lines):
                continue
            slot = match.group(1)
            info = lines[idx + 1]
            if not info or info.upper().startswith("DISCONNECT"):
                state[f"bt_source_{slot}"] = None
                continue
            # Statuswort am Zeilenende (Connected/Disconnected) abtrennen
            parts = re.split(r"\s{2,}", info)
            name = parts[0].strip()
            if name.upper() in ("CONNECTED", "DISCONNECTED", ""):
                name = None
            state[f"bt_source_{slot}"] = name
