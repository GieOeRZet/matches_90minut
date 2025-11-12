"""Sensor for 90minut.pl match data."""

from datetime import datetime, timedelta
import logging
import aiohttp
from bs4 import BeautifulSoup
from homeassistant.helpers.entity import Entity
from homeassistant.const import CONF_DEBUG_MODE

_LOGGER = logging.getLogger(__name__)

DEFAULT_UPDATE_INTERVAL = timedelta(hours=6)
LIVE_UPDATE_INTERVAL = timedelta(minutes=10)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the sensor from a config entry."""
    team_name = entry.data.get("team_name")
    team_id = entry.data.get("team_id")
    season_id = entry.data.get("season_id", "")
    last_matches = entry.data.get("last_matches", 5)
    next_matches = entry.data.get("next_matches", 1)
    debug_mode = entry.data.get("debug_mode", False)

    sensor = NinetyMinutSensor(team_name, team_id, season_id, last_matches, next_matches, debug_mode)
    async_add_entities([sensor], True)
    await sensor.async_update()  # natychmiastowe pobranie danych


class NinetyMinutSensor(Entity):
    """Representation of the 90minut.pl match sensor."""

    def __init__(self, team_name, team_id, season_id, last_matches, next_matches, debug_mode):
        self._team_name = team_name
        self._team_id = team_id
        self._season_id = season_id
        self._last_matches = last_matches
        self._next_matches = next_matches
        self._debug_mode = debug_mode
        self._state = None
        self._attrs = {}
        self._dynamic_interval = DEFAULT_UPDATE_INTERVAL
        self._last_update_time = None

    @property
    def name(self):
        return f"90minut {self._team_name} matches"

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attrs

    @property
    def icon(self):
        return "mdi:soccer"

    async def async_update(self):
        """Fetch and parse data from 90minut.pl."""
        now = datetime.now()

        if self._last_update_time and now - self._last_update_time < self._dynamic_interval:
            return

        try:
            url = f"http://www.90minut.pl/skarb.php?id_klub={self._team_id}"
            if self._season_id:
                url += f"&id_sezon={self._season_id}"

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    html = await response.text()

            soup = BeautifulSoup(html, "html.parser")
            matches = self._parse_matches(soup)

            if matches:
                last_match = matches[-1]
                self._state = f"{last_match['home']} {last_match['score']} {last_match['away']}"
                self._attrs = {
                    "matches": matches,
                    "finished_count": len([m for m in matches if m["finished"]]),
                    "upcoming_count": len([m for m in matches if not m["finished"]]),
                    "icon": "mdi:soccer",
                    "friendly_name": f"90minut {self._team_name} matches",
                }

            self._update_interval_based_on_live_match(matches)
            self._last_update_time = now

            if self._debug_mode:
                _LOGGER.warning(f"[DEBUG] Odświeżono dane dla {self._team_name} — interwał: {self._dynamic_interval}")

        except Exception as e:
            _LOGGER.error("❌ Błąd aktualizacji danych 90minut.pl: %s", e)

    # --- reszta metod bez zmian ---
    def _parse_matches(self, soup):
        matches = []
        table_rows = soup.find_all("tr", class_="mecz")

        for row in table_rows:
            try:
                date_text = row.find("td", class_="data").get_text(strip=True)
                home = row.find("td", class_="gospodarz").get_text(strip=True)
                away = row.find("td", class_="gosc").get_text(strip=True)
                score = row.find("td", class_="wynik").get_text(strip=True)
                competition = row.find("td", class_="rozgrywki").get_text(strip=True)

                date = self._parse_datetime(date_text)
                finished = ":" in score and score != "-"
                result = None
                if finished:
                    try:
                        g, h = map(int, score.split("-"))
                        result = "win" if g > h else "loss" if g < h else "draw"
                    except Exception:
                        result = None

                matches.append({
                    "date": date.strftime("%Y-%m-%d %H:%M"),
                    "competition": competition,
                    "home": home,
                    "away": away,
                    "score": score,
                    "finished": finished,
                    "result": result,
                    "league": competition.split(",")[0][:2].strip(),
                    "logo_home": f"/local/herby/{self._slugify(home)}.png",
                    "logo_away": f"/local/herby/{self._slugify(away)}.png",
                })
            except Exception:
                continue

        return matches[-(self._last_matches + self._next_matches):]

    def _parse_datetime(self, date_text):
        try:
            return datetime.strptime(date_text, "%d.%m.%Y, %H:%M")
        except Exception:
            return datetime.now()

    def _slugify(self, text):
        return (
            text.lower()
            .replace(" ", "_")
            .replace("ł", "l").replace("ó", "o").replace("ś", "s")
            .replace("ć", "c").replace("ż", "z").replace("ź", "z")
            .replace("ń", "n").replace("ą", "a").replace("ę", "e")
        )

    def _update_interval_based_on_live_match(self, matches):
        if not matches:
            self._dynamic_interval = DEFAULT_UPDATE_INTERVAL
            return

        now = datetime.now()
        for match in matches:
            match_time = datetime.strptime(match["date"], "%Y-%m-%d %H:%M")
            if match_time <= now <= match_time + timedelta(hours=2):
                self._dynamic_interval = LIVE_UPDATE_INTERVAL
                return
        self._dynamic_interval = DEFAULT_UPDATE_INTERVAL
