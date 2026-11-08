"""Commercial-use weather lookups through WeatherAPI.com's free plan."""

from functools import lru_cache
import os
import threading
import time

import httpx


BASE_URL = "https://api.weatherapi.com/v1"
_WEATHER_CACHE = {}
_WEATHER_CACHE_LOCK = threading.RLock()
_WEATHER_CACHE_SECONDS = 600


class WeatherAPIConfigurationError(RuntimeError):
    """Raised when a WeatherAPI key has not been configured."""


def _api_key():
    key = os.getenv("WEATHERAPI_KEY", "").strip()
    if not key:
        raise WeatherAPIConfigurationError(
            "Weather needs a WeatherAPI.com key. Set WEATHERAPI_KEY in the server environment."
        )
    return key


@lru_cache(maxsize=256)
def geocode_location(location):
    """Resolve a place to its coordinates and IANA timezone."""

    response = httpx.get(
        f"{BASE_URL}/search.json",
        params={"key": _api_key(), "q": location},
        timeout=10.0,
    )
    response.raise_for_status()
    results = response.json()
    if not results:
        return None

    place = results[0]
    return {
        "name": place.get("name", location),
        "admin1": place.get("region", ""),
        "country": place.get("country", ""),
        "latitude": place.get("lat"),
        "longitude": place.get("lon"),
        "timezone": place.get("tz_id", "UTC"),
    }


def get_weather(location, temperature_unit="celsius", include_forecast=False):
    """Return current conditions and, optionally, a three-day forecast."""

    cache_key = (location.strip().lower(), temperature_unit, include_forecast)
    now = time.monotonic()
    with _WEATHER_CACHE_LOCK:
        cached = _WEATHER_CACHE.get(cache_key)
        if cached and now - cached[0] < _WEATHER_CACHE_SECONDS:
            return cached[1]

    endpoint = "forecast.json" if include_forecast else "current.json"
    params = {
        "key": _api_key(),
        "q": location,
        "aqi": "no",
    }
    if include_forecast:
        params.update({"days": 3, "alerts": "no"})

    response = httpx.get(f"{BASE_URL}/{endpoint}", params=params, timeout=10.0)
    response.raise_for_status()
    payload = response.json()
    place = payload.get("location", {})
    weather = {
        "place": {
            "name": place.get("name", location),
            "admin1": place.get("region", ""),
            "country": place.get("country", ""),
            "latitude": place.get("lat"),
            "longitude": place.get("lon"),
            "timezone": place.get("tz_id", "UTC"),
        },
        "data": payload,
        "temperature_unit": temperature_unit,
    }

    with _WEATHER_CACHE_LOCK:
        _WEATHER_CACHE[cache_key] = (time.monotonic(), weather)
    return weather
