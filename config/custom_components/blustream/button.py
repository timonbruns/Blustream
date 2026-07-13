"""Button-Entitäten für Blustream Geräte."""
from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_INPUT_NAMES,
    CONF_MODEL,
    DOMAIN,
    MFP62_INPUTS,
    MODEL_DA11ABL,
)
from .entity import BlustreamEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[ButtonEntity] = []
    if entry.data.get(CONF_MODEL) == MODEL_DA11ABL:
        # Pairing-Fenster öffnen (entspricht der Pair-Taste der Web-UI)
        entities.append(
            BlustreamCommandButton(
                coordinator, entry, "bt_pair_start",
                "Bluetooth-Pairing starten",
                "BT RXPAIR", "mdi:bluetooth-audio",
            )
        )
        # Verbinden/Trennen der zwei möglichen Bluetooth-Geräte
        for dev in (1, 2):
            entities.append(
                BlustreamCommandButton(
                    coordinator, entry, f"bt_connect_{dev}",
                    f"Gekoppeltes Gerät {dev} verbinden",
                    f"BT RXCD {dev:02d}", "mdi:bluetooth-connect",
                )
            )
            entities.append(
                BlustreamCommandButton(
                    coordinator, entry, f"bt_disconnect_{dev}",
                    f"Gekoppeltes Gerät {dev} trennen",
                    f"BT RXDIS {dev:02d}", "mdi:bluetooth-off",
                )
            )
        entities.append(
            BlustreamCommandButton(
                coordinator, entry, "reboot", "Neustart",
                "REBOOT", "mdi:restart",
            )
        )
    else:
        input_names = entry.data.get(CONF_INPUT_NAMES, {})
        for code, default_name in MFP62_INPUTS:
            name = input_names.get(f"input_{code}", default_name)
            entities.append(
                Mfp62SourceButton(coordinator, entry, code, name)
            )

    async_add_entities(entities)


class Mfp62SourceButton(BlustreamEntity, ButtonEntity):
    """Schaltet beim Drücken direkt auf eine bestimmte Quelle (MFP62)."""

    _attr_icon = "mdi:video-input-hdmi"

    def __init__(self, coordinator, entry, code: int, name: str) -> None:
        super().__init__(coordinator, entry)
        self._code = code
        self._attr_name = name
        self._attr_unique_id = f"{self._host}_source_button_{code}"

    async def async_press(self) -> None:
        await self.coordinator.async_send(
            f"OUT 01 FR {self._code:02d}", source=self._code
        )


class BlustreamCommandButton(BlustreamEntity, ButtonEntity):
    """Generischer Befehls-Button ohne Zustandsänderung.

    Sendet per Abfrage und protokolliert die Antwort des Geräts, damit
    sich Befehlsformat-Probleme (z. B. "01" vs. "1") im Log erkennen
    lassen.
    """

    def __init__(
        self, coordinator, entry, unique_suffix: str, name: str,
        command: str, icon: str,
    ) -> None:
        super().__init__(coordinator, entry)
        self._command = command
        self._attr_name = name
        self._attr_icon = icon
        self._attr_unique_id = f"{self._host}_{unique_suffix}"

    async def async_press(self) -> None:
        response = await self.coordinator.client.async_query(self._command)
        _LOGGER.info(
            "Button '%s' sendete '%s' - Antwort: %s",
            self._attr_name,
            self._command,
            (response or "").strip() or "(keine)",
        )
