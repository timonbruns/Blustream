"""Media Player für Blustream: Quelle, Lautstärke, Mute, Power."""
from __future__ import annotations

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_INPUT_NAMES, DOMAIN, MFP62_INPUTS
from .entity import BlustreamEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([BlustreamMediaPlayer(coordinator, entry)])


class BlustreamMediaPlayer(BlustreamEntity, MediaPlayerEntity):
    """Repräsentiert den (gemeinsamen) Ausgang des MFP62."""

    # Name = Gerätename (kein Zusatz), da dies die Haupt-Entität ist.
    _attr_name = None

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{self._host}_media_player"

        input_names = entry.data.get(CONF_INPUT_NAMES, {})
        self._id_to_name: dict[int, str] = {}
        self._name_to_id: dict[str, int] = {}
        for code, default_name in MFP62_INPUTS:
            name = input_names.get(f"input_{code}", default_name)
            self._id_to_name[code] = name
            self._name_to_id[name] = code

        self._attr_source_list = list(self._id_to_name.values())
        self._attr_supported_features = (
            MediaPlayerEntityFeature.SELECT_SOURCE
            | MediaPlayerEntityFeature.TURN_ON
            | MediaPlayerEntityFeature.TURN_OFF
            | MediaPlayerEntityFeature.VOLUME_SET
            | MediaPlayerEntityFeature.VOLUME_MUTE
            | MediaPlayerEntityFeature.VOLUME_STEP
        )

    @property
    def state(self) -> MediaPlayerState:
        if self.coordinator.data.get("power", True):
            return MediaPlayerState.ON
        return MediaPlayerState.OFF

    @property
    def source(self) -> str | None:
        return self._id_to_name.get(self.coordinator.data.get("source"))

    @property
    def volume_level(self) -> float:
        return self.coordinator.data.get("volume", 0) / 100

    @property
    def is_volume_muted(self) -> bool:
        return self.coordinator.data.get("mute", False)

    async def async_select_source(self, source: str) -> None:
        code = self._name_to_id.get(source)
        if code is None:
            return
        # Beide Ausgänge des MFP62 spiegeln dieselbe Quelle; Senden an
        # Ausgang 01 setzt die gemeinsame Quelle.
        await self.coordinator.async_send(f"OUT 01 FR {code:02d}", source=code)

    async def async_turn_on(self) -> None:
        await self.coordinator.async_send("PON", power=True)

    async def async_turn_off(self) -> None:
        await self.coordinator.async_send("POFF", power=False)

    async def async_set_volume_level(self, volume: float) -> None:
        value = round(volume * 100)
        await self.coordinator.async_send(f"VOL {value}", volume=value)

    async def async_mute_volume(self, mute: bool) -> None:
        await self.coordinator.async_send(
            f"MUTE {'ON' if mute else 'OFF'}", mute=mute
        )

    async def async_volume_up(self) -> None:
        new = min(100, self.coordinator.data.get("volume", 0) + 5)
        await self.coordinator.async_send("VOL +", volume=new)

    async def async_volume_down(self) -> None:
        new = max(0, self.coordinator.data.get("volume", 0) - 5)
        await self.coordinator.async_send("VOL -", volume=new)
