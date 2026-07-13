"""Number-Entitäten für Blustream Geräte."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_MODEL,
    DA11_AUTOSW_MAX,
    DA11_AUTOSW_MIN,
    DA11_TIMEOUT_MAX,
    DA11_TIMEOUT_MIN,
    DOMAIN,
    MODEL_DA11ABL,
)
from .entity import BlustreamEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[NumberEntity] = []
    if entry.data.get(CONF_MODEL) == MODEL_DA11ABL:
        entities.append(
            BlustreamCommandNumber(
                coordinator, entry, "bt_timeout", "bt_timeout",
                "Pairing-Timeout", "BT TIMEOUT {v}",
                DA11_TIMEOUT_MIN, DA11_TIMEOUT_MAX, "mdi:timer-outline",
                unit="s",
            )
        )
        entities.append(
            BlustreamCommandNumber(
                coordinator, entry, "auto_sw", "auto_sw",
                "Auto-Switch-Zeit", "AUTO SW {v}",
                DA11_AUTOSW_MIN, DA11_AUTOSW_MAX, "mdi:swap-horizontal",
                unit="s",
            )
        )
    else:
        entities.append(
            BlustreamCommandNumber(
                coordinator, entry, "mic_vol", "mic_volume",
                "Mikrofon-Lautstärke", "MIC VOL {v}",
                0, 100, "mdi:microphone",
            )
        )

    async_add_entities(entities)


class BlustreamCommandNumber(BlustreamEntity, NumberEntity):
    """Generische Zahlen-Entität mit Befehlsschablone."""

    _attr_native_step = 1

    def __init__(
        self, coordinator, entry, state_key: str, unique_suffix: str,
        name: str, cmd_template: str, vmin: int, vmax: int, icon: str,
        unit: str | None = None,
    ) -> None:
        super().__init__(coordinator, entry)
        self._state_key = state_key
        self._cmd_template = cmd_template
        self._attr_name = name
        self._attr_icon = icon
        self._attr_native_min_value = vmin
        self._attr_native_max_value = vmax
        if unit:
            self._attr_native_unit_of_measurement = unit
        self._attr_unique_id = f"{self._host}_{unique_suffix}"

    @property
    def native_value(self) -> float:
        return self.coordinator.data.get(self._state_key, 0)

    async def async_set_native_value(self, value: float) -> None:
        val = int(value)
        await self.coordinator.async_send(
            self._cmd_template.format(v=val), **{self._state_key: val}
        )
