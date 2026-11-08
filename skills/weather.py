import re

from skills.base import Skill
from tools.weather import get_weather


class WeatherSkill(Skill):
    name = "Weather"
    description = "Reports current weather and short forecasts for locations worldwide."
    required_capabilities = set()

    WEATHER_CUES = (
        "weather", "forecast", "temperature", "how hot", "how cold",
        "will it rain", "is it raining", "humidity", "wind speed",
    )
    CONDITION_CODES = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Fog", 48: "Rime fog", 51: "Light drizzle", 53: "Drizzle",
        55: "Heavy drizzle", 56: "Freezing drizzle", 57: "Heavy freezing drizzle",
        61: "Light rain", 63: "Rain", 65: "Heavy rain", 66: "Freezing rain",
        67: "Heavy freezing rain", 71: "Light snow", 73: "Snow", 75: "Heavy snow",
        77: "Snow grains", 80: "Light rain showers", 81: "Rain showers",
        82: "Heavy rain showers", 85: "Snow showers", 86: "Heavy snow showers",
        95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Severe thunderstorm with hail",
    }

    def can_handle(self, user_input):
        text = user_input.lower()
        return any(cue in text for cue in self.WEATHER_CUES)

    @staticmethod
    def _location(text):
        match = re.search(r"\b(?:in|at|for|near)\s+(.+?)\s*[?.!,;]*$", text, re.I)
        if not match:
            return None
        location = match.group(1).strip(" \t\n'\"")
        location = re.sub(r"\b(?:right now|today|tomorrow|this week|this weekend)\b", "", location, flags=re.I)
        location = re.sub(r"\b(?:in|degrees?)\s+(?:celsius|fahrenheit|centigrade)\b", "", location, flags=re.I)
        location = re.sub(r"\b(?:celsius|fahrenheit|centigrade)\b", "", location, flags=re.I)
        return location.strip(" ,") or None

    def execute(self, user_input, model_provider=None):
        location = self._location(user_input)
        if not location:
            return "Which city or place should I check the weather for?"

        text = user_input.lower()
        unit = "fahrenheit" if "fahrenheit" in text or re.search(r"\b(?:°f|\bf)\b", text) else "celsius"
        include_forecast = "forecast" in text or "tomorrow" in text or "next few days" in text
        try:
            result = get_weather(location, temperature_unit=unit, include_forecast=include_forecast)
        except Exception:
            return "I couldn't retrieve weather data just now. Please try again shortly."

        if result is None:
            return f"I couldn't find a weather location matching {location!r}. Try a city and country, such as ‘Pune, India’."

        place, data = result["place"], result["data"]
        place_name = ", ".join(part for part in (place["name"], place.get("admin1"), place.get("country")) if part)
        current = data.get("current", {})
        temp_unit = data.get("current_units", {}).get("temperature_2m", "°C")
        wind_unit = data.get("current_units", {}).get("wind_speed_10m", "km/h")
        code = current.get("weather_code")
        lines = [f"Weather for {place_name} ({data.get('timezone', place.get('timezone', 'local time'))}):"]
        if current:
            lines.append(
                f"Now: {self.CONDITION_CODES.get(code, 'Conditions unavailable')}, "
                f"{current.get('temperature_2m', '—')}{temp_unit}; feels like "
                f"{current.get('apparent_temperature', '—')}{temp_unit}."
            )
            lines.append(
                f"Humidity: {current.get('relative_humidity_2m', '—')}%; "
                f"wind: {current.get('wind_speed_10m', '—')} {wind_unit}; "
                f"precipitation: {current.get('precipitation', '—')} mm."
            )
            lines.append(f"Updated at {current.get('time', 'the latest available reading')} local time.")

        daily = data.get("daily", {})
        if daily:
            lines.append("Forecast:")
            for i, day in enumerate(daily.get("time", [])):
                daily_code = daily.get("weather_code", [None] * (i + 1))[i]
                low = daily.get("temperature_2m_min", [None] * (i + 1))[i]
                high = daily.get("temperature_2m_max", [None] * (i + 1))[i]
                rain = daily.get("precipitation_probability_max", [None] * (i + 1))[i]
                rain_text = f", precipitation chance up to {rain}%" if rain is not None else ""
                lines.append(f"{day}: {self.CONDITION_CODES.get(daily_code, 'Conditions unavailable')}, {low}–{high}{temp_unit}{rain_text}.")
        lines.append("Source: [Open-Meteo](https://open-meteo.com/), licensed under CC BY 4.0.")
        return "\n".join(lines)
