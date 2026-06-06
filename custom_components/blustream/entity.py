"""Gemeinsame Basis-Entität für die Blustream Integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MODELS
from .coordinator import BlustreamCoordinator


class BlustreamEntity(CoordinatorEntity[BlustreamCoordinator]):
    """Basisklasse: bündelt alle Entitäten unter einem Gerät."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: BlustreamCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._host = entry.data["host"]
        model = MODELS.get(entry.data.get("model"), "Blustream")
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._host)},
            name=entry.title,
            manufacturer="Blustream",
            model=model,
        )
