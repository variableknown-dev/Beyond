import re

from skills.base import Skill
from tools.weather import WeatherAPIConfigurationError, get_weather


class WeatherSkill(Skill):
    name = "Weather"
    description = "Reports current weather and short forecasts for locations worldwide."
    required_capabilities = set()
    supports_location = True

    WEATHER_CUES = (
        "weather", "forecast", "temperature", "how hot", "how cold",
        "will it rain", "is it raining", "humidity", "wind speed",
    )

    def can_handle(self, user_input):
        return any(cue in user_input.lower() for cue in self.WEATHER_CUES)

    @staticmethod
    def _location(text):
        match = re.search(r"\b(?:in|at|for|near)\s+(.+?)\s*[?.!,;]*$", text, re.I)
        if not match:
            return None
        location = match.group(1).strip(" \t\n'\"")
        if re.fullmatch(r"(?:my\s+)?(?:location|area)|here|near\s+me", location, re.I):
            return None
        location = re.sub(
            r"\b(?:right now|today|tomorrow|this week|this weekend)\b",
            "", location, flags=re.I,
        )
        location = re.sub(
            r"\b(?:in|degrees?)\s+(?:celsius|fahrenheit|centigrade)\b",
            "", location, flags=re.I,
        )
        location = re.sub(r"\b(?:celsius|fahrenheit|centigrade)\b", "", location, flags=re.I)
        return location.strip(" ,") or None

    def execute(self, user_input, model_provider=None, user_location=None):
        if re.search(
            r"\b(?:yesterday|last\s+(?:week|month|year)|historical|past\s+weather)\b",
            user_input,
            re.I,
        ):
            return (
                "I can provide current conditions and forecasts, but historical weather "
                "isn't available in this setup. I can't verify what the weather was "
                "on that past date."
            )

        location = self._location(user_input)
        if not location and user_location and user_location.get("latitude") is not None and user_location.get("longitude") is not None:
            location = f"{user_location['latitude']},{user_location['longitude']}"
        if not location:
            return "Which city or place should I check the weather for?"

        text = user_input.lower()
        unit = "fahrenheit" if "fahrenheit" in text or re.search(r"\b(?:°f|f)\b", text) else "celsius"
        include_forecast = any(cue in text for cue in ("forecast", "tomorrow", "next few days"))
        try:
            result = get_weather(location, temperature_unit=unit, include_forecast=include_forecast)
        except WeatherAPIConfigurationError:
            return "Weather is not configured yet. Add a WeatherAPI.com key as WEATHERAPI_KEY in the server environment."
        except Exception:
            return "I couldn't retrieve weather data just now. Please try again shortly."

        if result is None:
            return f"I couldn't find a weather location matching {location!r}. Try a city and country, such as ‘Pune, India’."

        place, data = result["place"], result["data"]
        unit_suffix = "°F" if unit == "fahrenheit" else "°C"
        place_name = ", ".join(part for part in (place["name"], place.get("admin1"), place.get("country")) if part)
        current = data.get("current", {})
        condition = current.get("condition", {}).get("text", "Conditions unavailable")
        temp = current.get("temp_f" if unit == "fahrenheit" else "temp_c", "—")
        feels = current.get("feelslike_f" if unit == "fahrenheit" else "feelslike_c", "—")
        lines = [f"Weather for {place_name} ({place.get('timezone', 'local time')}):"]
        lines.append(f"Now: {condition}, {temp}{unit_suffix}; feels like {feels}{unit_suffix}.")
        lines.append(
            f"Humidity: {current.get('humidity', '—')}%; wind: "
            f"{current.get('wind_kph', '—')} km/h; precipitation: "
            f"{current.get('precip_mm', '—')} mm."
        )
        lines.append(f"Updated at {current.get('last_updated', 'the latest available reading')} local time.")

        forecast_days = data.get("forecast", {}).get("forecastday", [])
        if forecast_days:
            lines.append("Forecast:")
            for forecast in forecast_days:
                day = forecast.get("day", {})
                high = day.get("maxtemp_f" if unit == "fahrenheit" else "maxtemp_c", "—")
                low = day.get("mintemp_f" if unit == "fahrenheit" else "mintemp_c", "—")
                condition = day.get("condition", {}).get("text", "Conditions unavailable")
                rain = day.get("daily_chance_of_rain")
                rain_text = f", chance of rain {rain}%" if rain is not None else ""
                lines.append(f"{forecast.get('date')}: {condition}, {low}–{high}{unit_suffix}{rain_text}.")

        lines.append("Source: [WeatherAPI.com](https://www.weatherapi.com/).")
        lines.append(
            "Weather information is for general information only; forecasts may be inaccurate "
            "for your specific place or time. Do not rely on it alone for safety-critical "
            "decisions; consult official meteorological services."
        )
        return "\n".join(lines)
