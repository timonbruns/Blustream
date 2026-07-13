"""Sensor-Entitäten für Blustream Geräte."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_MODEL, DOMAIN, MODEL_DA11ABL
from .entity import BlustreamEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SensorEntity] = []
    if entry.data.get(CONF_MODEL) == MODEL_DA11ABL:
        entities.append(Da11BtSourceSensor(coordinator, entry, 1))
        entities.append(Da11BtSourceSensor(coordinator, entry, 2))

    async_add_entities(entities)


class Da11BtSourceSensor(BlustreamEntity, SensorEntity):
    """Zeigt den Namen des verbundenen Bluetooth-Geräts an einem Slot.

    Der Wert stammt aus der STATUS-Abfrage (Polling alle 5 Minuten) und
    wird zusätzlich nach Button-Aktionen (Pairing, Verbinden, Trennen)
    zeitnah aktualisiert.
    """

    _attr_icon = "mdi:cellphone-link"

    def __init__(self, coordinator, entry, slot: int) -> None:
        super().__init__(coordinator, entry)
        self._slot = slot
        self._attr_name = f"Bluetooth-Quelle {slot}"
        self._attr_unique_id = f"{self._host}_bt_source_{slot}"

    @property
    def native_value(self) -> str:
        name = self.coordinator.data.get(f"bt_source_{self._slot}")
        return name if name else "Nicht verbunden"
