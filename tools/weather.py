"""Free, non-commercial weather and location lookups via Open-Meteo."""

from functools import lru_cache
import threading
import time

import httpx


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
_WEATHER_CACHE = {}
_WEATHER_CACHE_LOCK = threading.RLock()
_WEATHER_CACHE_SECONDS = 600


@lru_cache(maxsize=256)
def geocode_location(location):
    """Resolve a place to coordinates and its IANA timezone."""

    response = httpx.get(
        GEOCODING_URL,
        params={
            "name": location,
            "count": 1,
            "language": "en",
            "format": "json",
        },
        timeout=10.0,
    )
    response.raise_for_status()
    results = response.json().get("results", [])

    if not results:
        return None

    place = results[0]
    return {
        "name": place.get("name", location),
        "admin1": place.get("admin1", ""),
        "country": place.get("country", ""),
        "latitude": place["latitude"],
        "longitude": place["longitude"],
        "timezone": place.get("timezone", "UTC"),
    }


def get_weather(location, temperature_unit="celsius", include_forecast=False):
    """Return current weather, with an optional three-day forecast."""

    place = geocode_location(location)
    if place is None:
        return None

    cache_key = (
        place["latitude"],
        place["longitude"],
        temperature_unit,
        include_forecast,
    )
    now = time.monotonic()

    with _WEATHER_CACHE_LOCK:
        cached = _WEATHER_CACHE.get(cache_key)
        if cached and now - cached[0] < _WEATHER_CACHE_SECONDS:
            return {"place": place, "data": cached[1]}

    params = {
        "latitude": place["latitude"],
        "longitude": place["longitude"],
        "current": (
            "temperature_2m,relative_humidity_2m,apparent_temperature,"
            "precipitation,weather_code,wind_speed_10m"
        ),
        "temperature_unit": temperature_unit,
        "wind_speed_unit": "kmh",
        "timezone": "auto",
    }

    if include_forecast:
        params.update({
            "daily": (
                "weather_code,temperature_2m_max,temperature_2m_min,"
                "precipitation_probability_max"
            ),
            "forecast_days": 3,
        })

    response = httpx.get(FORECAST_URL, params=params, timeout=10.0)
    response.raise_for_status()
    data = response.json()

    with _WEATHER_CACHE_LOCK:
        _WEATHER_CACHE[cache_key] = (time.monotonic(), data)

    return {"place": place, "data": data}
