"""Sensor for 90minut.pl match data."""
import os
import logging
from datetime import datetime, timedelta
import aiohttp
from bs4 import BeautifulSoup
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)

DEFAULT_UPDATE_INTERVAL = timedelta(hours=6)
LIVE_UPDATE_INTERVAL = timedelta(minutes=10)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the sensor from a config entry."""
    sensor = NinetyMinutSensor(
        hass=hass,
        team_name=entry.data.get("team_name"),
        team_id=entry.data.get("team_id"),
        season_id=entry.data.get("season_id", ""),
        last_matches=entry.data.get("last_matches", 5),
        next_matches=entry.data.get("next_matches", 1),
    )
    async_add_entities([sensor], True)


class NinetyMinutSensor(Entity):
    """Representation of the 90minut.pl match sensor."""

    def __init__(self, hass, team_name, team_id, season_id, last_matches, next_matches):
        self.hass = hass
        self._team_name = team_name
        self._team_id = team_id
        self._season_id = season_id
        self._last_matches = last_matches
        self._next_matches = next_matches

        self._state = None
        self._attrs = {}
        self._dynamic_interval = DEFAULT_UPDATE_INTERVAL
        self._last_update_time = None

        self._herby_path = hass.config.path("www/herby")

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

        except Exception as e:
            _LOGGER.error("Błąd aktualizacji danych 90minut.pl: %s", e)

    def _parse_matches(self, soup):
        """Parse match rows from the 90minut.pl HTML."""
        matches = []
        rows = soup.find_all("tr", class_="mecz")
        for row in rows:
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
                        pass

                logo_home = self._get_logo(home)
                logo_away = self._get_logo(away)

                matches.append({
                    "date": date.strftime("%Y-%m-%d %H:%M"),
                    "competition": competition,
                    "home": home,
                    "away": away,
                    "score": score,
                    "finished": finished,
                    "result": result,
                    "league": competition.split(",")[0][:2].strip(),
                    "logo_home": logo_home,
                    "logo_away": logo_away,
                })
            except Exception:
                continue

        return matches[-(self._last_matches + self._next_matches):]

    def _parse_datetime(self, text):
        try:
            return datetime.strptime(text, "%d.%m.%Y, %H:%M")
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

    def _get_logo(self, team_name):
        """Check or download team crest."""
        slug = self._slugify(team_name)
        local_file = os.path.join(self._herby_path, f"{slug}.png")

        if os.path.exists(local_file):
            return f"/local/herby/{slug}.png"

        os.makedirs(self._herby_path, exist_ok=True)
        logo_url = f"http://www.90minut.pl/logo/{slug}.png"

        try:
            import aiohttp
            async def download_logo():
                async with aiohttp.ClientSession() as session:
                    async with session.get(logo_url) as resp:
                        if resp.status == 200:
                            with open(local_file, "wb") as f:
                                f.write(await resp.read())

            import asyncio
            asyncio.create_task(download_logo())
        except Exception:
            pass

        return f"/local/herby/{slug}.png"

    def _update_interval_based_on_live_match(self, matches):
        """Adjust update interval depending on whether a match is live."""
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
