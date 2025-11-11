"""Options flow for 90minut integration."""

import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, DEFAULT_LAST, DEFAULT_NEXT


class NinetyMinutOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow (rekonfiguracja integracji)."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Zarządzanie opcjami integracji."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = self.config_entry.options or self.config_entry.data

        schema = vol.Schema({
            vol.Required("team_name", default=current.get("team_name")): str,
            vol.Required("team_id", default=current.get("team_id")): int,
            vol.Optional("season_id", default=current.get("season_id", "")): str,
            vol.Optional("last_matches", default=current.get("last_matches", DEFAULT_LAST)): int,
            vol.Optional("next_matches", default=current.get("next_matches", DEFAULT_NEXT)): int,
        })

        return self.async_show_form(step_id="init", data_schema=schema)
