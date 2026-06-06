"""Blustream Matrix / Presentation Switch Integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .api import BlustreamClient
from .const import DEFAULT_PORT, DEFAULT_SCAN_INTERVAL, DOMAIN, PLATFORMS
from .coordinator import BlustreamCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Richtet die Integration über die GUI ein."""
    client = BlustreamClient(
        entry.data["host"],
        entry.data.get("port", DEFAULT_PORT),
    )
    coordinator = BlustreamCoordinator(hass, client, DEFAULT_SCAN_INTERVAL)
    # Erste Abfrage (schlägt nicht fehl, falls das Gerät offline ist -
    # dann gelten die optimistischen Startwerte).
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Entfernt die Integration."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unloaded
