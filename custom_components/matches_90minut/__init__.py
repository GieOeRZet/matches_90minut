"""90minut.pl – Matches Integration."""

import importlib
import logging
import asyncio
from homeassistant.exceptions import ConfigEntryNotReady

_LOGGER = logging.getLogger(__name__)
DOMAIN = "matches_90minut"
PLATFORMS = ["sensor"]

REQUIRED_PACKAGES = ["PIL", "requests", "bs4"]


async def async_setup_entry(hass, entry):
    """Set up integration from a config entry with dependency check and retry."""
    _LOGGER.info("🔄 Inicjalizacja integracji %s...", DOMAIN)

    for pkg in REQUIRED_PACKAGES:
        success = False
        for attempt in range(12):  # 12 × 10 s = 2 min
            try:
                importlib.import_module(pkg)
                success = True
                break
            except ImportError:
                _LOGGER.warning("📦 Pakiet %s nie gotowy (próba %s/12)...", pkg, attempt + 1)
                await asyncio.sleep(10)
        if not success:
            _LOGGER.error("❌ Pakiet %s nie został zainstalowany – integracja wstrzymana.", pkg)
            raise ConfigEntryNotReady(f"Package {pkg} not ready")

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    )
    _LOGGER.info("✅ Integracja %s zainicjowana pomyślnie.", DOMAIN)
    return True


async def async_unload_entry(hass, entry):
    """Unload integration when removed from Home Assistant."""
    _LOGGER.info("🧹 Wyłączanie integracji %s...", DOMAIN)
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    return unload_ok
