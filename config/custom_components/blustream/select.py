"""Select-Entitäten für Blustream Geräte."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_MODEL,
    DA11_BT_PRIORITY_OPTIONS,
    DA11_GAIN_OPTIONS,
    DA11_PAIR_MODE_OPTIONS,
    DA11_PRIORITY_OPTIONS,
    DA11_SENS_OPTIONS,
    DOMAIN,
    MIC_MIX_OPTIONS,
    MODEL_DA11ABL,
    RESOLUTION_OPTIONS,
)
from .entity import BlustreamEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SelectEntity] = []
    if entry.data.get(CONF_MODEL) == MODEL_DA11ABL:
        entities.append(
            BlustreamCommandSelect(
                coordinator, entry, "bt_pair_mode", "bt_pair_mode",
                "Bluetooth-Pairing", "BT PAIR MODE {v}",
                DA11_PAIR_MODE_OPTIONS, "mdi:bluetooth-settings",
            )
        )
        entities.append(
            BlustreamCommandSelect(
                coordinator, entry, "in_priority", "in_priority",
                "Eingangs-Priorität", "PRIORITY {v}",
                DA11_PRIORITY_OPTIONS, "mdi:priority-high",
            )
        )
        entities.append(
            BlustreamCommandSelect(
                coordinator, entry, "bt_priority", "bt_priority",
                "Bluetooth-Geräte-Priorität", "BT PRIORITY {v}",
                DA11_BT_PRIORITY_OPTIONS, "mdi:bluetooth-connect",
            )
        )
        entities.append(
            BlustreamCommandSelect(
                coordinator, entry, "out_gain", "out_gain",
                "Ausgangspegel", "OUT GAIN {v}",
                DA11_GAIN_OPTIONS, "mdi:volume-high",
            )
        )
        entities.append(
            BlustreamCommandSelect(
                coordinator, entry, "ana_sens", "ana_sens",
                "Analog-Empfindlichkeit", "ANA IN SENS {v}",
                DA11_SENS_OPTIONS, "mdi:knob",
            )
        )
    else:
        entities.append(
            BlustreamCommandSelect(
                coordinator, entry, "mic_mix", "mic_mix",
                "Mikrofon-Mix", "MIC MIX {v}",
                MIC_MIX_OPTIONS, "mdi:tune-vertical",
            )
        )
        entities.append(
            BlustreamCommandSelect(
                coordinator, entry, "resolution", "resolution",
                "Ausgangsauflösung", "OUT RES {v}",
                RESOLUTION_OPTIONS, "mdi:monitor-screenshot",
            )
        )

    async_add_entities(entities)


class BlustreamCommandSelect(BlustreamEntity, SelectEntity):
    """Generische Auswahl-Entität: Code-Map + Befehlsschablone."""

    def __init__(
        self, coordinator, entry, state_key: str, unique_suffix: str,
        name: str, cmd_template: str, options: dict[str, str], icon: str,
    ) -> None:
        super().__init__(coordinator, entry)
        self._state_key = state_key
        self._cmd_template = cmd_template
        self._code_to_label = dict(options)
        self._label_to_code = {v: k for k, v in options.items()}
        self._attr_options = list(options.values())
        self._attr_name = name
        self._attr_icon = icon
        self._attr_unique_id = f"{self._host}_{unique_suffix}"

    @property
    def current_option(self) -> str | None:
        return self._code_to_label.get(self.coordinator.data.get(self._state_key))

    async def async_select_option(self, option: str) -> None:
        code = self._label_to_code.get(option)
        if code is None:
            return
        await self.coordinator.async_send(
            self._cmd_template.format(v=code), **{self._state_key: code}
        )
