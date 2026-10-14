"""AccuWeather Core Weather client (Earth widget).

API key from env `ACCUWEATHER_API_KEY` — never commit secrets.
Auth: Bearer (zpka_ keys) with apikey query fallback.
Docs: https://developer.accuweather.com/
Site: https://www.accuweather.com/
"""
from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from typing import Any

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)

_BASE = "https://dataservice.accuweather.com"
_CACHE: dict[str, Any] = {}
_CACHE_TTL = 12 * 60


def _api_key() -> str:
    return (get_settings().accuweather_api_key or "").strip()


def is_configured() -> bool:
    settings = get_settings()
    return bool(getattr(settings, "accuweather_enabled", True)) and bool(_api_key())


def _language() -> str:
    return (getattr(get_settings(), "accuweather_language", None) or "en-us").strip() or "en-us"


def _cache_get(key: str) -> dict | None:
    row = _CACHE.get(key)
    if not row:
        return None
    if time.time() - float(row.get("at", 0)) > _CACHE_TTL:
        return None
    return row.get("payload")


def _cache_set(key: str, payload: dict) -> None:
    _CACHE[key] = {"at": time.time(), "payload": payload}


def _metric_value(obj: Any) -> float | None:
    if not isinstance(obj, dict):
        return None
    metric = obj.get("Metric") if "Metric" in obj else obj
    if not isinstance(metric, dict):
        return None
    val = metric.get("Value")
    try:
        return float(val) if val is not None else None
    except (TypeError, ValueError):
        return None


def _icon_url(icon: Any) -> str | None:
    try:
        n = int(icon)
    except (TypeError, ValueError):
        return None
    if n < 1 or n > 44:
        return None
    # AccuWeather moved icons to awxcdn; www.accuweather.com/images/weathericons/*.png now 403s.
    return f"https://www.awxcdn.com/adc-assets/images/weathericons/{n}.svg"


def _wmo_text(code: Any) -> str:
    try:
        c = int(code)
    except (TypeError, ValueError):
        return "Weather"
    if c == 0:
        return "Clear"
    if c <= 3:
        return "Cloudy"
    if c <= 48:
        return "Fog"
    if c <= 67:
        return "Rain"
    if c <= 77:
        return "Snow"
    if c <= 82:
        return "Showers"
    if c <= 99:
        return "Thunderstorm"
    return "Weather"


def _wmo_to_aw_icon(code: Any, *, is_day: bool = True) -> int | None:
    """Map Open-Meteo WMO weather_code → AccuWeather icon id (1–44) for awxcdn SVGs."""
    try:
        c = int(code)
    except (TypeError, ValueError):
        return None
    if c == 0:
        return 1 if is_day else 33
    if c in (1, 2):
        return 2 if is_day else 34
    if c == 3:
        return 7 if is_day else 38
    if c in (45, 48):
        return 11
    if c in (51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82):
        return 12
    if c in (71, 73, 75, 77, 85, 86):
        return 22
    if c in (95, 96, 99):
        return 15
    return 7 if is_day else 38


def _uv_text(uv: Any) -> str | None:
    try:
        v = float(uv)
    except (TypeError, ValueError):
        return None
    if v < 3:
        return "Low"
    if v < 6:
        return "Moderate"
    if v < 8:
        return "High"
    if v < 11:
        return "Very High"
    return "Extreme"


async def _aw_get(client: httpx.AsyncClient, path: str, *, params: dict | None = None) -> httpx.Response:
    key = _api_key()
    p = dict(params or {})
    headers = {"Accept": "application/json"}
    # Classic AccuWeather keys expect apikey= only; Bearer on those often returns HTTP 403.
    # Modern portal keys (zpka_…) prefer Authorization: Bearer.
    if key.lower().startswith("zpka_"):
        headers["Authorization"] = f"Bearer {key}"
    p.setdefault("apikey", key)
    return await client.get(f"{_BASE}{path}", params=p, headers=headers)


async def _open_meteo_fallback(lat: float, lon: float) -> dict:
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": (
            "temperature_2m,apparent_temperature,weather_code,wind_speed_10m,wind_gusts_10m,"
            "relative_humidity_2m,cloud_cover,surface_pressure,precipitation,uv_index,is_day"
        ),
        "hourly": "temperature_2m,weather_code,precipitation_probability",
        "daily": "temperature_2m_max,temperature_2m_min,weather_code,precipitation_probability_max",
        "forecast_days": "1",
        "forecast_hours": "2",
        "wind_speed_unit": "kmh",
        "timezone": "auto",
    }
    async with httpx.AsyncClient(timeout=12.0) as client:
        res = await client.get(url, params=params)
        res.raise_for_status()
        j = res.json()
    current = j.get("current") or {}
    daily = j.get("daily") or {}
    hourly = j.get("hourly") or {}
    code = current.get("weather_code")
    is_day = bool(current.get("is_day", 1))
    icon = _wmo_to_aw_icon(code, is_day=is_day)
    uv = current.get("uv_index")

    forecast_today = None
    try:
        mins = daily.get("temperature_2m_min") or []
        maxs = daily.get("temperature_2m_max") or []
        codes = daily.get("weather_code") or []
        precip = daily.get("precipitation_probability_max") or []
        dates = daily.get("time") or []
        if mins or maxs:
            day_code = codes[0] if codes else code
            forecast_today = {
                "date": str(dates[0]) if dates else None,
                "min_c": float(mins[0]) if mins else None,
                "max_c": float(maxs[0]) if maxs else None,
                "day_text": _wmo_text(day_code),
                "night_text": None,
                "precip_probability_day": int(precip[0]) if precip and precip[0] is not None else None,
                "link": None,
            }
    except (TypeError, ValueError, IndexError):
        forecast_today = None

    next_hour = None
    try:
        h_temp = hourly.get("temperature_2m") or []
        h_code = hourly.get("weather_code") or []
        h_precip = hourly.get("precipitation_probability") or []
        h_time = hourly.get("time") or []
        # Index 0 is often "now"; prefer the next slot when present.
        idx = 1 if len(h_temp) > 1 else 0
        if h_temp:
            next_hour = {
                "time": h_time[idx] if idx < len(h_time) else None,
                "temperature_c": float(h_temp[idx]) if h_temp[idx] is not None else None,
                "weather_text": _wmo_text(h_code[idx] if idx < len(h_code) else code),
                "precip_probability": int(h_precip[idx]) if idx < len(h_precip) and h_precip[idx] is not None else None,
                "icon": _wmo_to_aw_icon(h_code[idx] if idx < len(h_code) else code, is_day=is_day),
            }
    except (TypeError, ValueError, IndexError):
        next_hour = None

    humidity = current.get("relative_humidity_2m")
    cloud = current.get("cloud_cover")
    return {
        "provider": "accuweather",
        "status": "fallback",
        "configured": False,
        "latitude": lat,
        "longitude": lon,
        "timezone": j.get("timezone"),
        "temperature_c": current.get("temperature_2m"),
        "realfeel_c": current.get("apparent_temperature"),
        "weather_text": _wmo_text(code),
        "weather_icon": icon,
        "weather_icon_url": _icon_url(icon),
        "is_day_time": is_day,
        "wind_kmh": current.get("wind_speed_10m"),
        "wind_gust_kmh": current.get("wind_gusts_10m"),
        "relative_humidity": int(humidity) if isinstance(humidity, (int, float)) else None,
        "cloud_cover": int(cloud) if isinstance(cloud, (int, float)) else None,
        "pressure_mb": current.get("surface_pressure"),
        "uv_index": float(uv) if isinstance(uv, (int, float)) else None,
        "uv_text": _uv_text(uv),
        "precip_1h_mm": current.get("precipitation"),
        "observed_at": datetime.now(timezone.utc),
        "accuweather_url": (
            f"https://www.accuweather.com/en/search-locations?query={lat:.4f},{lon:.4f}"
        ),
        "attribution": "Weather context with AccuWeather attribution; live AccuWeather API pending key.",
        "notes": [
            "ACCUWEATHER_API_KEY not configured — interim numeric feed with AccuWeather deep-link.",
        ],
        "fallback_provider": "open-meteo",
        "forecast_today": forecast_today,
        "next_hour": next_hour,
    }


async def fetch_current(*, lat: float, lon: float) -> dict:
    cache_key = f"rich:{round(lat, 3)}:{round(lon, 3)}:{_language()}"
    cached = _cache_get(cache_key)
    if cached:
        return cached

    if not is_configured():
        payload = await _open_meteo_fallback(lat, lon)
        _cache_set(cache_key, payload)
        return payload

    lang = _language()
    try:
        async with httpx.AsyncClient(timeout=18.0) as client:
            loc_res = await _aw_get(
                client,
                "/locations/v1/cities/geoposition/search",
                params={"q": f"{lat},{lon}", "language": lang, "toplevel": "true"},
            )
            if loc_res.status_code >= 400:
                logger.warning("accuweather location HTTP %s body=%s", loc_res.status_code, loc_res.text[:200])
                payload = await _open_meteo_fallback(lat, lon)
                payload["configured"] = True
                payload["status"] = "degraded"
                payload["notes"] = [f"AccuWeather location HTTP {loc_res.status_code}", *payload.get("notes", [])]
                _cache_set(cache_key, payload)
                return payload

            loc = loc_res.json()
            location_key = str(loc.get("Key") or "")
            if not location_key:
                raise RuntimeError("missing location key")

            cur_res = await _aw_get(
                client,
                f"/currentconditions/v1/{location_key}",
                params={"language": lang, "details": "true"},
            )
            if cur_res.status_code >= 400:
                logger.warning("accuweather conditions HTTP %s", cur_res.status_code)
                payload = await _open_meteo_fallback(lat, lon)
                payload["configured"] = True
                payload["status"] = "degraded"
                payload["notes"] = [f"AccuWeather conditions HTTP {cur_res.status_code}", *payload.get("notes", [])]
                _cache_set(cache_key, payload)
                return payload

            rows = cur_res.json()
            row = rows[0] if isinstance(rows, list) and rows else {}

            forecast_today = None
            next_hour = None
            try:
                daily_res = await _aw_get(
                    client,
                    f"/forecasts/v1/daily/1day/{location_key}",
                    params={"language": lang, "metric": "true", "details": "true"},
                )
                if daily_res.status_code < 400:
                    daily = daily_res.json()
                    df = (daily.get("DailyForecasts") or [None])[0]
                    if isinstance(df, dict):
                        forecast_today = {
                            "date": str(df.get("Date") or "")[:10] or None,
                            "min_c": _metric_value((df.get("Temperature") or {}).get("Minimum")),
                            "max_c": _metric_value((df.get("Temperature") or {}).get("Maximum")),
                            "day_text": (df.get("Day") or {}).get("IconPhrase") or (df.get("Day") or {}).get("ShortPhrase"),
                            "night_text": (df.get("Night") or {}).get("IconPhrase") or (df.get("Night") or {}).get("ShortPhrase"),
                            "precip_probability_day": (df.get("Day") or {}).get("PrecipitationProbability"),
                            "link": df.get("Link") or daily.get("Link"),
                        }
            except Exception as exc:
                logger.warning("accuweather daily forecast skipped: %s", exc)

            try:
                hourly_res = await _aw_get(
                    client,
                    f"/forecasts/v1/hourly/1hour/{location_key}",
                    params={"language": lang, "metric": "true"},
                )
                if hourly_res.status_code < 400:
                    hours = hourly_res.json()
                    h0 = hours[0] if isinstance(hours, list) and hours else None
                    if isinstance(h0, dict):
                        next_hour = {
                            "time": h0.get("DateTime"),
                            "temperature_c": _metric_value(h0.get("Temperature")),
                            "weather_text": h0.get("IconPhrase") or h0.get("WeatherText"),
                            "precip_probability": h0.get("PrecipitationProbability"),
                            "icon": h0.get("WeatherIcon"),
                        }
            except Exception as exc:
                logger.warning("accuweather hourly forecast skipped: %s", exc)

            icon = row.get("WeatherIcon")
            link = str(row.get("Link") or "").strip() or "https://www.accuweather.com/"
            if link.startswith("http://"):
                link = "https://" + link[len("http://") :]

            observed_raw = row.get("LocalObservationDateTime")
            observed_at = None
            if isinstance(observed_raw, str) and observed_raw:
                try:
                    observed_at = datetime.fromisoformat(observed_raw.replace("Z", "+00:00"))
                except ValueError:
                    observed_at = datetime.now(timezone.utc)

            country = ((loc.get("Country") or {}).get("LocalizedName")) or (
                (loc.get("Country") or {}).get("ID")
            )
            admin = ((loc.get("AdministrativeArea") or {}).get("LocalizedName")) or None
            rf = row.get("RealFeelTemperature") or {}
            rf_metric = rf.get("Metric") if isinstance(rf, dict) else {}
            pressure = row.get("Pressure") or {}
            pressure_tendency = ((row.get("PressureTendency") or {}).get("LocalizedText")) if isinstance(
                row.get("PressureTendency"), dict
            ) else None

            payload = {
                "provider": "accuweather",
                "status": "ok",
                "configured": True,
                "city": loc.get("LocalizedName") or loc.get("EnglishName"),
                "country": country,
                "admin_area": admin,
                "latitude": lat,
                "longitude": lon,
                "timezone": ((loc.get("TimeZone") or {}).get("Name")),
                "temperature_c": _metric_value(row.get("Temperature")),
                "realfeel_c": _metric_value(rf) if isinstance(rf, dict) else None,
                "realfeel_phrase": (rf_metric or {}).get("Phrase") if isinstance(rf_metric, dict) else None,
                "weather_text": row.get("WeatherText"),
                "weather_icon": icon if isinstance(icon, int) else None,
                "weather_icon_url": _icon_url(icon),
                "is_day_time": row.get("IsDayTime"),
                "wind_kmh": _metric_value((row.get("Wind") or {}).get("Speed")),
                "wind_gust_kmh": _metric_value((row.get("WindGust") or {}).get("Speed")),
                "wind_dir": ((row.get("Wind") or {}).get("Direction") or {}).get("Localized")
                or ((row.get("Wind") or {}).get("Direction") or {}).get("English"),
                "relative_humidity": row.get("RelativeHumidity"),
                "indoor_humidity": row.get("IndoorRelativeHumidity"),
                "dew_point_c": _metric_value(row.get("DewPoint")),
                "uv_index": row.get("UVIndexFloat") if row.get("UVIndexFloat") is not None else row.get("UVIndex"),
                "uv_text": row.get("UVIndexText"),
                "visibility_km": _metric_value(row.get("Visibility")),
                "cloud_cover": row.get("CloudCover"),
                "pressure_mb": _metric_value(pressure),
                "pressure_tendency": pressure_tendency,
                "ceiling_m": _metric_value(row.get("Ceiling")),
                "precip_1h_mm": _metric_value((row.get("Precip1hr") or {})),
                "precip_24h_mm": _metric_value(((row.get("PrecipitationSummary") or {}).get("Past24Hours"))),
                "observed_at": observed_at or datetime.now(timezone.utc),
                "forecast_today": forecast_today,
                "next_hour": next_hour,
                "accuweather_url": link,
                "attribution": "Weather data provided by AccuWeather",
                "notes": [
                    "AccuWeather Current Conditions + 1-day / next-hour forecast for the Earth widget.",
                    "Indicative only — not an official warning service.",
                ],
                "fallback_provider": None,
            }
            _cache_set(cache_key, payload)
            return payload
    except Exception as exc:
        logger.warning("accuweather fetch failed: %s", exc)
        payload = await _open_meteo_fallback(lat, lon)
        payload["notes"] = [f"AccuWeather error: {exc}", *payload.get("notes", [])]
        payload["status"] = "degraded"
        payload["configured"] = True
        _cache_set(cache_key, payload)
        return payload
