"""Sensor for 90minut.pl match data."""

from datetime import datetime, timedelta
import logging
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

_LOGGER = logging.getLogger(__name__)

MIN_TIME_BETWEEN_UPDATES = timedelta(hours=6)  # domyślnie co 6h
LIVE_UPDATE_INTERVAL = timedelta(minutes=10)   # w trakcie meczu co 10min


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the sensor from a config entry."""
    team_name = entry.data.get("team_name")
    team_id = entry.data.get("team_id")
    season_id = entry.data.get("season_id", "")
    last_matches = entry.data.get("last_matches", 5)
    next_matches = entry.data.get("next_matches", 1)

    sensor = NinetyMinutSensor(team_name, team_id, season_id, last_matches, next_matches)
    async_add_entities([sensor], True)


class NinetyMinutSensor(Entity):
    """Representation of the 90minut.pl match sensor."""

    def __init__(self, team_name, team_id, season_id, last_matches, next_matches):
        self._team_name = team_name
        self._team_id = team_id
        self._season_id = season_id
        self._last_matches = last_matches
        self._next_matches = next_matches

        self._state = None
        self._attrs = {}
        self._next_update = None
        self._last_update_time = None
        self._dynamic_interval = MIN_TIME_BETWEEN_UPDATES

    @property
    def name(self):
        return f"90minut {self._team_name} matches"

    @property
    def stat
