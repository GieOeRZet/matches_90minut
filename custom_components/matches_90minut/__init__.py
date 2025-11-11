"""90minut.pl – Matches Integration (reconfigurable, resilient loader)."""

import importlib
import logging
import asyncio
from homeassistant.exceptions import ConfigEntryNotReady

_LOGGER = logging.getLogger(__name__)

DOMAIN = "matches_90minut"
REQUIRED_PACKAGES = ["PIL", "requests", "bs4"]


async def async_setup_entry(hass, entry):
    """Set up integration from a config entry with dependency check."""
    _LOGGER.debug("Initializing integration '%s'...", DOMAIN)

    # 🔹 Sprawdź wymagane biblioteki
    for pkg in REQUIRED_PACKAGES:
        try:
            importlib.import_module(pkg)
        except ImportError:
            _LOGGER.warning("📦 Pakiet %s nie jest jeszcze dostępny – odraczam start integracji...", pkg)
            raise ConfigEntryNotReady(f"Package {pkg} not ready")

    # 🔹 Wszystko OK → załaduj sensory
    try:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
        )
        _LOGGER.info("✅ Integracja '%s' została poprawnie zainicjowana.", DOMAIN)
        return True
    except Exception as err:
        _LOGGER.exception("❌ Błąd przy inicjalizacji integracji '%s': %s", DOMAIN, err)
        raise ConfigEntryNotReady from err


async def async_unload_entry(hass, entry):
    """Unload integration when removed from Home Assistant."""
    _LOGGER.info("🧹 Wyłączanie integracji '%s'...", DOMAIN)
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unload_ok:
        _LOGGER.info("✅ Integracja '%s' została poprawnie usunięta.", DOMAIN)
    else:
        _LOGGER.warning("⚠️ Nie udało się całkowicie usunąć integracji '%s'.", DOMAIN_
