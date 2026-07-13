"""Config Flow für die Blustream Integration."""
from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers.selector import (
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import (
    CONF_INPUT_NAMES,
    CONF_MODEL,
    CONF_OUTPUT_NAMES,
    DEFAULT_PORT,
    DOMAIN,
    MFP62_INPUTS,
    MFP62_OUTPUTS,
    MODEL_DA11ABL,
    MODEL_MFP62,
    MODELS,
)

DEFAULT_NAMES = {
    MODEL_MFP62: "Blustream MFP62",
    MODEL_DA11ABL: "Blustream DA11ABL",
}


class BlustreamConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Geführte Einrichtung: Produkt -> Verbindung -> ggf. Benennung."""

    VERSION = 2

    def __init__(self) -> None:
        self.data: dict = {}

    async def async_step_user(self, user_input=None):
        """Schritt 1: Welches Blustream Produkt wird verwendet?"""
        if user_input is not None:
            self.data[CONF_MODEL] = user_input[CONF_MODEL]
            return await self.async_step_connection()

        options = [
            SelectOptionDict(value=value, label=label)
            for value, label in MODELS.items()
        ]
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_MODEL, default=MODEL_MFP62): SelectSelector(
                        SelectSelectorConfig(
                            options=options,
                            mode=SelectSelectorMode.DROPDOWN,
                        )
                    )
                }
            ),
        )

    async def async_step_connection(self, user_input=None):
        """Schritt 2: IP, Port und Name abfragen."""
        if user_input is not None:
            await self.async_set_unique_id(user_input["host"])
            self._abort_if_unique_id_configured()
            self.data.update(user_input)
            # Nur der MFP62 braucht Benennungs-Schritte; der DA11ABL hat
            # feste Quellen (Analog/Bluetooth) und keinen benannten Ausgang.
            if self.data[CONF_MODEL] == MODEL_MFP62:
                return await self.async_step_input_names()
            return self.async_create_entry(
                title=self.data["name"], data=self.data
            )

        default_name = DEFAULT_NAMES.get(self.data.get(CONF_MODEL), "Blustream")
        return self.async_show_form(
            step_id="connection",
            data_schema=vol.Schema(
                {
                    vol.Required("host"): str,
                    vol.Optional("port", default=DEFAULT_PORT): int,
                    vol.Required("name", default=default_name): str,
                }
            ),
        )

    async def async_step_input_names(self, user_input=None):
        """Schritt 3 (MFP62): Klarnamen für die Eingänge."""
        if user_input is not None:
            self.data[CONF_INPUT_NAMES] = user_input
            return await self.async_step_output_names()

        fields = {}
        for code, default_name in MFP62_INPUTS:
            fields[vol.Optional(f"input_{code}", default=default_name)] = str

        return self.async_show_form(
            step_id="input_names",
            data_schema=vol.Schema(fields),
            description_placeholders={"count": str(len(MFP62_INPUTS))},
        )

    async def async_step_output_names(self, user_input=None):
        """Schritt 4 (MFP62): Klarnamen für die Ausgänge."""
        if user_input is not None:
            self.data[CONF_OUTPUT_NAMES] = user_input
            return self.async_create_entry(title=self.data["name"], data=self.data)

        fields = {}
        for i in range(1, MFP62_OUTPUTS + 1):
            fields[vol.Optional(f"output_{i}", default=f"Ausgang {i}")] = str

        return self.async_show_form(
            step_id="output_names",
            data_schema=vol.Schema(fields),
            description_placeholders={"count": str(MFP62_OUTPUTS)},
        )
