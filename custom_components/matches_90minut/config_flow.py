"""Config flow for 90minut.pl integration."""
from __future__ import annotations
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import (
    DOMAIN,
    CONF_TEAM_NAME,
    CONF_TEAM_ID,
    CONF_SEASON_ID,
    CONF_LAST_MATCHES,
    CONF_NEXT_MATCHES,
    CONF_DEBUG_MODE,
)


class NinetyMinutConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for matches_90minut."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial configuration step."""
        errors = {}

        if user_input is not None:
            return self.async_create_entry(
                title=user_input[CONF_TEAM_NAME],
                data=user_input
            )

        schema = vol.Schema({
            vol.Required(CONF_TEAM_NAME): str,
            vol.Required(CONF_TEAM_ID): str,
            vol.Optional(CONF_SEASON_ID, default=""): str,
            vol.Optional(CONF_LAST_MATCHES, default=5): int,
            vol.Optional(CONF_NEXT_MATCHES, default=1): int,
            vol.Optional(CONF_DEBUG_MODE, default=False): bool,
        })

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return NinetyMinutOptionsFlow(config_entry)
