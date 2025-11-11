"""90minut.pl – Matches Integration."""

from homeassistant.exceptions import ConfigEntryNotReady
import importlib
import asyncio
import logging

_LOGGER = logging.getLogger(__name__)

DOMAIN = "matches_90minut"
PLATFORMS = ["sensor"]

REQUIRED_PACKAGES = ["PIL", "requests", "bs4"]


async def async_setup_entry(hass, entry):
    """Set up integration from a config entry with dependency check."""
    _LOGGER.info("🔄 Inicjalizacja integracji %s...", DOMAIN)

    # sprawdź, czy wymagane biblioteki są dostępne
    for pkg in REQUIRED_PACKAGES:
        for attempt in range(6):
            try:
                importlib.import_module(pkg)
                break
            except ImportError:
                _LOGGER.warning("📦 Pakiet %s niegotowy (próba %s/6)...", pkg, attempt + 1)
                await asyncio.sleep(10)
        else:
            raise ConfigEntryNotReady(f"Package {pkg} not ready")

    # poprawka: bez create_task — wymagane przez HA 2025.1+
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    _LOGGER.info("✅ Integracja %s uruchomiona pomyślnie.", DOMAIN)
    return True


async def async_unload_entry(hass, entry):
    """Unload integration when removed."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
