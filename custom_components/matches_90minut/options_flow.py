"""Options flow for 90minut.pl integration."""
from __future__ import annotations
import voluptuous as vol
from homeassistant import config_entries
from .const import (
    CONF_TEAM_NAME,
    CONF_TEAM_ID,
    CONF_SEASON_ID,
    CONF_LAST_MATCHES,
    CONF_NEXT_MATCHES,
    CONF_DEBUG_MODE,
)


class NinetyMinutOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for matches_90minut."""

    def __init__(self, config_entry: config_entries.ConfigEntry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Handle options configuration."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        data = self.config_entry.data
        schema = vol.Schema({
            vol.Required(CONF_TEAM_NAME, default=data.get(CONF_TEAM_NAME)): str,
            vol.Required(CONF_TEAM_ID, default=data.get(CONF_TEAM_ID)): str,
            vol.Optional(CONF_SEASON_ID, default=data.get(CONF_SEASON_ID, "")): str,
            vol.Optional(CONF_LAST_MATCHES, default=data.get(CONF_LAST_MATCHES, 5)): int,
            vol.Optional(CONF_NEXT_MATCHES, default=data.get(CONF_NEXT_MATCHES, 1)): int,
            vol.Optional(CONF_DEBUG_MODE, default=data.get(CONF_DEBUG_MODE, False)): bool,
        })

        return self.async_show_form(step_id="init", data_schema=schema)
