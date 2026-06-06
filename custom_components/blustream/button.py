"""Button-Entitäten: ein Direktwahl-Button je Quelle.

Hinweis: Button-Entitäten in Home Assistant sind zustandslos. Sie senden
nur den Umschaltbefehl, zeigen im Dashboard aber nicht an, welche Quelle
gerade aktiv ist. Wer eine "aktiv"-Markierung möchte, nutzt stattdessen die
Quellenwahl des Media Players (siehe dashboard_example.yaml).
"""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_INPUT_NAMES, DOMAIN, MFP62_INPUTS
from .entity import BlustreamEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    input_names = entry.data.get(CONF_INPUT_NAMES, {})

    entities: list[ButtonEntity] = []
    for code, default_name in MFP62_INPUTS:
        name = input_names.get(f"input_{code}", default_name)
        entities.append(BlustreamSourceButton(coordinator, entry, code, name))
    async_add_entities(entities)


class BlustreamSourceButton(BlustreamEntity, ButtonEntity):
    """Schaltet beim Drücken direkt auf eine bestimmte Quelle."""

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
