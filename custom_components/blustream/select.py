"""Select-Entitäten: Mikrofon-Mix-Modus und Ausgangsauflösung."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, MIC_MIX_OPTIONS, RESOLUTION_OPTIONS
from .entity import BlustreamEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            BlustreamMicMixSelect(coordinator, entry),
            BlustreamResolutionSelect(coordinator, entry),
        ]
    )


class BlustreamMicMixSelect(BlustreamEntity, SelectEntity):
    """Mikrofon-/Hintergrund-Mischung (MIC MIX mm)."""

    _attr_name = "Mikrofon-Mix"
    _attr_icon = "mdi:tune-vertical"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{self._host}_mic_mix"
        self._code_to_label = dict(MIC_MIX_OPTIONS)
        self._label_to_code = {v: k for k, v in MIC_MIX_OPTIONS.items()}
        self._attr_options = list(MIC_MIX_OPTIONS.values())

    @property
    def current_option(self) -> str | None:
        return self._code_to_label.get(self.coordinator.data.get("mic_mix"))

    async def async_select_option(self, option: str) -> None:
        code = self._label_to_code.get(option)
        if code is None:
            return
        await self.coordinator.async_send(f"MIC MIX {code}", mic_mix=code)


class BlustreamResolutionSelect(BlustreamEntity, SelectEntity):
    """Scaler-Ausgangsauflösung (OUT RES rr)."""

    _attr_name = "Ausgangsauflösung"
    _attr_icon = "mdi:monitor-screenshot"
    _attr_entity_category = None

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{self._host}_resolution"
        self._code_to_label = dict(RESOLUTION_OPTIONS)
        self._label_to_code = {v: k for k, v in RESOLUTION_OPTIONS.items()}
        self._attr_options = list(RESOLUTION_OPTIONS.values())

    @property
    def current_option(self) -> str | None:
        return self._code_to_label.get(self.coordinator.data.get("resolution"))

    async def async_select_option(self, option: str) -> None:
        code = self._label_to_code.get(option)
        if code is None:
            return
        await self.coordinator.async_send(f"OUT RES {code}", resolution=code)
