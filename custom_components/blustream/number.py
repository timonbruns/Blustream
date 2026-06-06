"""Number-Entität: Mikrofon-Lautstärke (MIC VOL xx)."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import BlustreamEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([BlustreamMicVolume(coordinator, entry)])


class BlustreamMicVolume(BlustreamEntity, NumberEntity):
    """Stellt die Mikrofon-Eingangslautstärke ein."""

    _attr_name = "Mikrofon-Lautstärke"
    _attr_icon = "mdi:microphone"
    _attr_native_min_value = 0
    _attr_native_max_value = 100
    _attr_native_step = 1

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{self._host}_mic_volume"

    @property
    def native_value(self) -> float:
        return self.coordinator.data.get("mic_vol", 0)

    async def async_set_native_value(self, value: float) -> None:
        val = int(value)
        await self.coordinator.async_send(f"MIC VOL {val}", mic_vol=val)
