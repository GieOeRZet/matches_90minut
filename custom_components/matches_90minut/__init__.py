"""Initialization for Matches 90minut integration."""

import asyncio
import importlib
import logging
from concurrent.futures import ThreadPoolExecutor
from homeassistant.exceptions import ConfigEntryNotReady

_LOGGER = logging.getLogger(__name__)

DOMAIN = "matches_90minut"
PLATFORMS = ["sensor"]

# Pakiety wymagane przez integrację
REQUIRED_PACKAGES = ["PIL", "requests", "bs4"]


async def async_setup_entry(hass, entry):
    """Set up Matches 90minut integration from a config entry."""
    _LOGGER.info("🔄 Inicjalizacja integracji %s...", DOMAIN)

    loop = asyncio.get_running_loop()
    executor = ThreadPoolExecutor(max_workers=3)

    # Sprawdź wymagane zależności w osobnym wątku
    for pkg in REQUIRED_PACKAGES:
        success = await loop.run_in_executor(executor, _try_import, pkg)
        if not success:
            raise ConfigEntryNotReady(f"Package {pkg} not ready")

    # Załaduj platformę sensor
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    _LOGGER.info("✅ Integracja %s uruchomiona pomyślnie.", DOMAIN)
    return True


def _try_import(pkg: str) -> bool:
    """Pomocniczo: próbuj importować moduł w osobnym wątku."""
    import time
    for _ in range(3):
        try:
            importlib.import_module(pkg)
            return True
        except ImportError:
            time.sleep(2)
    return False


async def async_unload_entry(hass, entry):
    """Unload integration when entry is removed."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        _LOGGER.info("🧹 Integracja %s została poprawnie wyładowana.", DOMAIN)
    return unload_ok
