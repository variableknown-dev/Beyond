import os
import re
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from skills.base import Skill
from tools.weather import WeatherAPIConfigurationError


class TimeDateSkill(Skill):
    name = "Time and date"
    description = "Gives the current time and date in a timezone or location."
    required_capabilities = set()

    WEATHER_TERMS = ("weather", "forecast", "rain", "snow", "temperature", "wind")
    TIME_CUES = (
        "what time", "what is the time", "what's the time", "whats the time",
        "tell me the time", "current time", "time right now", "time is it",
        "time in ", "time at ", "local time",
    )
    DATE_CUES = (
        "what date", "what is the date", "what's the date", "whats the date",
        "today's date", "todays date", "current date", "date is it",
        "what day", "which day", "today's day",
    )

    def can_handle(self, user_input):
        text = user_input.lower()
        if any(term in text for term in self.WEATHER_TERMS):
            return False
        return any(cue in text for cue in self.TIME_CUES + self.DATE_CUES)

    @staticmethod
    def _zone_for(text):
        # An explicit IANA timezone is the most precise, e.g. Asia/Tokyo.
        zone_match = re.search(r"\b[A-Z][A-Za-z_+-]+/[A-Za-z0-9_+./-]+\b", text)
        if zone_match:
            return ZoneInfo(zone_match.group(0)), zone_match.group(0)

        place_match = re.search(r"\b(?:in|at|for)\s+(.+?)\s*[?.!,;]*$", text, re.I)
        if place_match:
            from tools.weather import geocode_location

            place_name = place_match.group(1).strip(" \t\n'\"")
            place_name = re.sub(r"\b(?:right now|today|currently)\b", "", place_name, flags=re.I).strip(" ,")
            if not place_name:
                raise ValueError("Please provide a city or timezone.")
            place = geocode_location(place_name)
            if place is None:
                raise ValueError(f"I couldn't find a timezone for {place_name!r}.")
            timezone = place["timezone"]
            return ZoneInfo(timezone), f"{place['name']}, {place['country']} ({timezone})"

        timezone = os.getenv("BEYOND_DEFAULT_TIMEZONE", "Asia/Kolkata")
        return ZoneInfo(timezone), timezone

    def execute(self, user_input, model_provider=None):
        text = user_input.lower()
        asks_time = any(cue in text for cue in self.TIME_CUES)
        asks_date = any(cue in text for cue in self.DATE_CUES)
        try:
            zone, label = self._zone_for(user_input)
        except WeatherAPIConfigurationError as error:
            return str(error)
        except ValueError:
            return "I couldn't identify that timezone or location. Try a city name or an IANA timezone such as Asia/Dubai."
        except ZoneInfoNotFoundError:
            return "I couldn't identify that timezone or location. Try a city name or an IANA timezone such as Asia/Dubai."

        now = datetime.now(zone)
        parts = []
        if asks_time:
            parts.append(f"The current time in {label} is {now.strftime('%I:%M %p').lstrip('0')}.")
        if asks_date:
            parts.append(f"Today in {label} is {now.strftime('%A, %B')} {now.day}, {now.year}.")
        return " ".join(parts) or f"It is {now.strftime('%A, %B')} {now.day}, {now.year}, {now.strftime('%I:%M %p').lstrip('0')} in {label}."
