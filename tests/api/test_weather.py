"""Weather API tests (AccuWeather proxy)."""
from __future__ import annotations

from app.main import app


def test_weather_routes_registered():
    paths = {getattr(r, "path", "") for r in app.routes}
    assert "/weather/current" in paths
    assert "/v1/weather/current" in paths
    assert "/weather/status" in paths


def test_weather_current_fallback_without_key(client, monkeypatch):
    monkeypatch.setenv("ACCUWEATHER_ENABLED", "true")
    monkeypatch.setenv("ACCUWEATHER_API_KEY", "")
    from app.config import get_settings

    get_settings.cache_clear()

    import app.services.accuweather as aw

    async def fake_fallback(lat: float, lon: float):
        return {
            "provider": "accuweather",
            "status": "fallback",
            "configured": False,
            "latitude": lat,
            "longitude": lon,
            "timezone": "UTC",
            "temperature_c": 12.5,
            "realfeel_c": 11.0,
            "weather_text": "Cloudy",
            "weather_icon": 7,
            "weather_icon_url": "https://www.awxcdn.com/adc-assets/images/weathericons/7.svg",
            "wind_kmh": 8.0,
            "relative_humidity": 70,
            "observed_at": None,
            "forecast_today": {"min_c": 8.0, "max_c": 14.0, "day_text": "Cloudy"},
            "next_hour": {"temperature_c": 12.0, "weather_text": "Cloudy"},
            "accuweather_url": "https://www.accuweather.com/",
            "attribution": "Weather data provided by AccuWeather",
            "notes": ["test"],
            "fallback_provider": "open-meteo",
        }

    monkeypatch.setattr(aw, "_open_meteo_fallback", fake_fallback)
    aw._CACHE.clear()

    res = client.get("/v1/weather/current?lat=50.45&lon=30.52", headers={"Authorization": ""})
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["provider"] == "accuweather"
    assert "accuweather.com" in body["accuweather_url"]
    assert body["temperature_c"] == 12.5
    assert body["forecast_today"]["max_c"] == 14.0


def test_wmo_icon_and_open_meteo_fallback_shape(monkeypatch):
    import app.services.accuweather as aw

    assert aw._wmo_to_aw_icon(0, is_day=True) == 1
    assert aw._wmo_to_aw_icon(3, is_day=False) == 38
    assert aw._uv_text(2.0) == "Low"
    assert aw._uv_text(7.5) == "High"

    class _FakeResp:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "timezone": "Europe/Bucharest",
                "current": {
                    "temperature_2m": 11.2,
                    "apparent_temperature": 9.0,
                    "weather_code": 3,
                    "wind_speed_10m": 12.0,
                    "wind_gusts_10m": 24.0,
                    "relative_humidity_2m": 61,
                    "cloud_cover": 90,
                    "surface_pressure": 1008.0,
                    "precipitation": 0.0,
                    "uv_index": 2.1,
                    "is_day": 1,
                },
                "daily": {
                    "time": ["2026-10-14"],
                    "temperature_2m_min": [6.0],
                    "temperature_2m_max": [13.0],
                    "weather_code": [3],
                    "precipitation_probability_max": [10],
                },
                "hourly": {
                    "time": ["2026-10-14T14:00", "2026-10-14T15:00"],
                    "temperature_2m": [11.0, 10.5],
                    "weather_code": [3, 3],
                    "precipitation_probability": [5, 8],
                },
            }

    class _FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

        async def get(self, *args, **kwargs):
            return _FakeResp()

    monkeypatch.setattr(aw.httpx, "AsyncClient", _FakeClient)

    import asyncio

    payload = asyncio.run(aw._open_meteo_fallback(44.4, 26.1))
    assert payload["temperature_c"] == 11.2
    assert payload["weather_icon"] == 7
    assert payload["forecast_today"]["max_c"] == 13.0
    assert payload["next_hour"]["temperature_c"] == 10.5
    assert "awxcdn.com" in (payload["weather_icon_url"] or "")
