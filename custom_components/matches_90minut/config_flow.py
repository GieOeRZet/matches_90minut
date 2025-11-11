"""Config flow for Matches 90minut integration."""

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.const import CONF_NAME

from .const import DOMAIN


class NinetyMinutConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for 90minut.pl integration."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Pierwszy krok konfiguracji."""
        errors = {}

        if user_input is not None:
            return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

        schema = vol.Schema({
            vol.Required(CONF_NAME, default="Górnik Zabrze"): str,
            vol.Required("team_id", default="101"): str,
            vol.Optional("season_id", default=""): str,
            vol.Optional("last_matches", default=5): int,
            vol.Optional("next_matches", default=1): int,
        })

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    def async_get_options_flow(config_entry):
        """Zwróć handler opcji (dla rekonfiguracji)."""
        from .options_flow import NinetyMinutOptionsFlowHandler
        return NinetyMinutOptionsFlowHandler(config_entry)


class NinetyMinutOptionsFlowHandler(config_entries.OptionsFlow):
    """Obsługa rekonfiguracji (Options Flow)."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Formularz rekonfiguracji."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        data = self.config_entry.options or self.config_entry.data

        schema = vol.Schema({
            vol.Required("team_id", default=data.get("team_id", "101")): str,
            vol.Optional("season_id", default=data.get("season_id", "")): str,
            vol.Optional("last_matches", default=data.get("last_matches", 5)): int,
            vol.Optional("next_matches", default=data.get("next_matches", 1)): int,
        })

        return self.async_show_form(step_id="init", data_schema=schema)
