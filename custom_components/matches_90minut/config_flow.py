"""Config flow for 90minut.pl integration."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_NAME
from homeassistant.helpers import aiohttp_client
import logging

from .const import (
    DOMAIN,
    CONF_TEAM_NAME,
    CONF_TEAM_ID,
    CONF_SEASON_ID,
    CONF_LAST_MATCHES,
    CONF_NEXT_MATCHES,
    CONF_DEBUG_MODE,
)

_LOGGER = logging.getLogger(__name__)


class NinetyMinutConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for 90minut.pl."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            team_name = user_input[CONF_TEAM_NAME]
            team_id = user_input[CONF_TEAM_ID]

            # Prosta walidacja
            if not team_name or not team_id.isdigit():
                errors["base"] = "invalid_team"
            else:
                await self.async_set_unique_id(f"{team_id}")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=team_name, data=user_input)

        schema = vol.Schema(
            {
                vol.Required(CONF_TEAM_NAME): str,
                vol.Required(CONF_TEAM_ID): str,
                vol.Optional(CONF_SEASON_ID, default=""): str,
                vol.Optional(CONF_LAST_MATCHES, default=5): int,
                vol.Optional(CONF_NEXT_MATCHES, default=1): int,
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    def async_get_options_flow(config_entry):
        """Return the options flow handler."""
        return NinetyMinutOptionsFlowHandler(config_entry)


class NinetyMinutOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for the integration."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            _LOGGER.debug("💾 Zapisuję nowe opcje integracji: %s", user_input)
            return self.async_create_entry(title="", data=user_input)

        data = {**self.config_entry.data, **self.config_entry.options}

        schema = vol.Schema(
            {
                vol.Required(CONF_TEAM_NAME, default=data.get(CONF_TEAM_NAME, "")): str,
                vol.Required(CONF_TEAM_ID, default=data.get(CONF_TEAM_ID, "")): str,
                vol.Optional(CONF_SEASON_ID, default=data.get(CONF_SEASON_ID, "")): str,
                vol.Optional(CONF_LAST_MATCHES, default=data.get(CONF_LAST_MATCHES, 5)): int,
                vol.Optional(CONF_NEXT_MATCHES, default=data.get(CONF_NEXT_MATCHES, 1)): int,
                vol.Optional(CONF_DEBUG_MODE, default=data.get(CONF_DEBUG_MODE, False)): bool,
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
        )
