"""Config flow for Matches 90minut integration."""
from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN, DEFAULT_TEAM_ID, DEFAULT_LAST_MATCHES, DEFAULT_NEXT_MATCHES, DEFAULT_SEASON_ID


class NinetyMinutConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Flow konfiguracji integracji."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Krok początkowy konfiguracji."""
        if user_input is not None:
            return self.async_create_entry(title=user_input["team_name"], data=user_input)

        schema = vol.Schema({
            vol.Required("team_name"): str,
            vol.Required("team_id", default=DEFAULT_TEAM_ID): str,
            vol.Optional("season_id", default=DEFAULT_SEASON_ID): str,
            vol.Optional("last_matches", default=DEFAULT_LAST_MATCHES): int,
            vol.Optional("next_matches", default=DEFAULT_NEXT_MATCHES): int,
        })
        return self.async_show_form(step_id="user", data_schema=schema)

    async def async_get_options_flow(self, config_entry):
        """Zwróć obiekt flow opcji."""
        return NinetyMinutOptionsFlow(config_entry)


class NinetyMinutOptionsFlow(config_entries.OptionsFlow):
    """Obsługa rekonfiguracji integracji."""

    def __init__(self, entry):
        self.entry_ref = entry

    async def async_step_init(self, user_input=None):
        """Pierwszy krok rekonfiguracji."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        data = self.entry_ref.options or self.entry_ref.data
        schema = vol.Schema({
            vol.Required("team_name", default=data.get("team_name")): str,
            vol.Required("team_id", default=data.get("team_id")): str,
            vol.Optional("season_id", default=data.get("season_id", "")): str,
            vol.Optional("last_matches", default=data.get("last_matches", 5)): int,
            vol.Optional("next_matches", default=data.get("next_matches", 1)): int,
        })
        return self.async_show_form(step_id="init", data_schema=schema)
