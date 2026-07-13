"""Schalter für Blustream Geräte."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_MODEL,
    CONF_OUTPUT_NAMES,
    DOMAIN,
    MFP62_OUTPUTS,
    MODEL_DA11ABL,
)
from .entity import BlustreamEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SwitchEntity] = []
    if entry.data.get(CONF_MODEL) == MODEL_DA11ABL:
        entities.append(
            BlustreamCommandSwitch(
                coordinator, entry, "ana_in_mute", "ana_in_mute",
                "Analog-Eingang stumm",
                "ANA IN MUTE ON", "ANA IN MUTE OFF", "mdi:volume-variant-off",
            )
        )
        entities.append(
            BlustreamCommandSwitch(
                coordinator, entry, "bt_in_mute", "bt_in_mute",
                "Bluetooth-Eingang stumm",
                "BT IN MUTE ON", "BT IN MUTE OFF", "mdi:bluetooth-off",
            )
        )
    else:
        output_names = entry.data.get(CONF_OUTPUT_NAMES, {})
        for i in range(1, MFP62_OUTPUTS + 1):
            name = output_names.get(f"output_{i}", f"Ausgang {i}")
            # unique-Suffix "output_{i}" beibehalten (kompatibel zu v0.3.x)
            entities.append(
                BlustreamCommandSwitch(
                    coordinator, entry, f"out{i}", f"output_{i}", name,
                    f"OUT {i:02d} ON", f"OUT {i:02d} OFF", "mdi:hdmi-port",
                )
            )
        entities.append(
            BlustreamCommandSwitch(
                coordinator, entry, "auto", "auto_switch", "Auto-Umschaltung",
                "OUT AUTO ON", "OUT AUTO OFF", "mdi:auto-mode",
            )
        )
        entities.append(
            BlustreamCommandSwitch(
                coordinator, entry, "mic_mute", "mic_mute", "Mikrofon stumm",
                "MIC MUTE ON", "MIC MUTE OFF", "mdi:microphone-off",
            )
        )

    async_add_entities(entities)


class BlustreamCommandSwitch(BlustreamEntity, SwitchEntity):
    """Generischer Schalter: ein Zustands-Key, zwei Befehle."""

    def __init__(
        self, coordinator, entry, state_key: str, unique_suffix: str,
        name: str, cmd_on: str, cmd_off: str, icon: str,
    ) -> None:
        super().__init__(coordinator, entry)
        self._state_key = state_key
        self._cmd_on = cmd_on
        self._cmd_off = cmd_off
        self._attr_name = name
        self._attr_icon = icon
        self._attr_unique_id = f"{self._host}_{unique_suffix}"

    @property
    def is_on(self) -> bool:
        return self.coordinator.data.get(self._state_key, False)

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.async_send(self._cmd_on, **{self._state_key: True})

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.async_send(self._cmd_off, **{self._state_key: False})
