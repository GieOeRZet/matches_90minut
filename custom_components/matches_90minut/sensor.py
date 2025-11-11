"""Sensor for 90minut.pl match results."""

from datetime import datetime
import logging
import requests
from bs4 import BeautifulSoup
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import ATTR_ATTRIBUTION

_LOGGER = logging.getLogger(__name__)
ATTRIBUTION = "Dane: 90minut.pl"


async def async_setup_entry(hass, entry, async_add_entities):
    """Setup sensor from config entry."""
    team_id = entry.data.get("team_id")
    team_name = entry.data.get("team_name")
    last_matches = int(entry.data.get("last_matches", 3))
    next_matches = int(entry.data.get("next_matches", 3))

    entity = NinetyMinutSensor(team_id, team_name, last_matches, next_matches)
    async_add_entities([entity], update_before_add=True)


class NinetyMinutSensor(SensorEntity):
    """Main 90minut sensor entity."""

    def __init__(self, team_id, team_name, last_matches, next_matches):
        self._team_id = team_id
        self._team_name = team_name
        self._last_matches = last_matches
        self._next_matches = next_matches
        self._attr_name = f"90minut {team_name} matches"
        self._attr_icon = "mdi:soccer"
        self._state = None
        self._attr_extra_state_attributes = {}

    @property
    def name(self):
        return self._attr_name

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attr_extra_state_attributes

    def _parse_matches(self, soup):
        """Parse HTML page to extract matches."""
        matches = []
        for row in soup.select("table tbody tr"):
            cols = [c.get_text(strip=True) for c in row.find_all("td")]
            if len(cols) < 5:
                continue
            date, competition, home, score, away = cols[:5]
            finished = ":" in score and "-" in score
            result = None
            if finished:
                h, a = [int(x) for x in score.split("-")]
                if h > a:
                    result = "win"
                elif h < a:
                    result = "loss"
                else:
                    result = "draw"
            matches.append({
                "date": date,
                "competition": competition,
                "home": home,
                "away": away,
                "score": score,
                "finished": finished,
                "result": result
            })
        return matches

    def update(self):
        """Fetch latest data from 90minut.pl."""
        url = f"http://www.90minut.pl/skarb.php?id_klub={self._team_id}"
        _LOGGER.debug("Pobieram dane z %s", url)

        try:
            resp = requests.get(url, timeout=10)
            resp.encoding = "utf-8"
            soup = BeautifulSoup(resp.text, "html.parser")

            matches = self._parse_matches(soup)
            finished = [m for m in matches if m["finished"]][-self._last_matches :]
            upcoming = [m for m in matches if not m["finished"]][:self._next_matches]

            all_matches = finished + upcoming
            self._state = f"{finished[-1]['home']} {finished[-1]['score']} {finished[-1]['away']}" if finished else "Brak danych"

            self._attr_extra_state_attributes = {
                "matches": all_matches,
                "finished_count": len(finished),
                "upcoming_count": len(upcoming),
                ATTR_ATTRIBUTION: ATTRIBUTION,
            }
        except Exception as err:
            _LOGGER.error("Błąd pobierania danych z 90minut.pl: %s", err)
