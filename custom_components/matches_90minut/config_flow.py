"""Config flow for 90minut integration."""

import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, DEFAULT_LAST, DEFAULT_NEXT


class NinetyMinutConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for 90minut."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title=user_input["team_name"], data=user_input)

        schema = vol.Schema({
            vol.Required("team_name"): str,
            vol.Required("team_id"): int,
            vol.Optional("last_matches", default=DEFAULT_LAST): int,
            vol.Optional("next_matches", default=DEFAULT_NEXT): int,
        })

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
