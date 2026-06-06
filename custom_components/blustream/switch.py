"""Schalter: Ausgang 1/2, Auto-Umschaltung, Mikrofon-Mute."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_OUTPUT_NAMES, DOMAIN, MFP62_OUTPUTS
from .entity import BlustreamEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    output_names = entry.data.get(CONF_OUTPUT_NAMES, {})

    entities: list[SwitchEntity] = []
    for i in range(1, MFP62_OUTPUTS + 1):
        name = output_names.get(f"output_{i}", f"Ausgang {i}")
        entities.append(BlustreamOutputSwitch(coordinator, entry, i, name))

    entities.append(BlustreamAutoSwitch(coordinator, entry))
    entities.append(BlustreamMicMuteSwitch(coordinator, entry))
    async_add_entities(entities)


class BlustreamOutputSwitch(BlustreamEntity, SwitchEntity):
    """Schaltet einen einzelnen HDMI-Ausgang an/aus (OUT xx ON/OFF)."""

    _attr_icon = "mdi:hdmi-port"

    def __init__(self, coordinator, entry, output_id: int, name: str) -> None:
        super().__init__(coordinator, entry)
        self._output_id = output_id
        self._state_key = f"out{output_id}"
        self._attr_name = name
        self._attr_unique_id = f"{self._host}_output_{output_id}"

    @property
    def is_on(self) -> bool:
        return self.coordinator.data.get(self._state_key, True)

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.async_send(
            f"OUT {self._output_id:02d} ON", **{self._state_key: True}
        )

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.async_send(
            f"OUT {self._output_id:02d} OFF", **{self._state_key: False}
        )


class BlustreamAutoSwitch(BlustreamEntity, SwitchEntity):
    """Auto-Umschaltung auf eine neu erkannte Quelle (OUT AUTO ON/OFF)."""

    _attr_name = "Auto-Umschaltung"
    _attr_icon = "mdi:auto-mode"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{self._host}_auto_switch"

    @property
    def is_on(self) -> bool:
        return self.coordinator.data.get("auto", False)

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.async_send("OUT AUTO ON", auto=True)

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.async_send("OUT AUTO OFF", auto=False)


class BlustreamMicMuteSwitch(BlustreamEntity, SwitchEntity):
    """Mikrofon stummschalten (MIC MUTE ON/OFF)."""

    _attr_name = "Mikrofon stumm"
    _attr_icon = "mdi:microphone-off"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{self._host}_mic_mute"

    @property
    def is_on(self) -> bool:
        return self.coordinator.data.get("mic_mute", False)

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.async_send("MIC MUTE ON", mic_mute=True)

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.async_send("MIC MUTE OFF", mic_mute=False)
