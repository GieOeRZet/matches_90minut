"""Options flow for Matches 90minut integration."""

import voluptuous as vol
from homeassistant import config_entries

from .const import DOMAIN


class NinetyMinutOptionsFlowHandler(config_entries.OptionsFlow):
    """Obsługa rekonfiguracji (Options Flow)."""

    def __init__(self, entry):
        # Zmieniamy nazwę, żeby nie nadpisywać wewnętrznego config_entry
        self.entry_ref = entry

    async def async_step_init(self, user_input=None):
        """Formularz rekonfiguracji."""
        if user_input is not None:
            # Tworzymy wpis opcji na podstawie danych z formularza
            return self.async_create_entry(title="", data=user_input)

        data = self.entry_ref.options or self.entry_ref.data

        schema = vol.Schema({
            vol.Required("team_id", default=data.get("team_id", "101")): str,
            vol.Optional("season_id", default=data.get("season_id", "")): str,
            vol.Optional("last_matches", default=data.get("last_matches", 5)): int,
            vol.Optional("next_matches", default=data.get("next_matches", 1)): int,
        })

        return self.async_show_form(step_id="init", data_schema=schema)
