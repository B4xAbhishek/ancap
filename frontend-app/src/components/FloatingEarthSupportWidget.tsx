"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { weatherApi } from "@/lib/api";
import {
  FLOATING_WIDGET_EVENT,
  emitFloatingWidget,
  type FloatingWidgetEventDetail,
} from "@/lib/floatingWidgets";

const GEO_CACHE_KEY = "ancap_earth_geo_v4";
const WEATHER_CACHE_KEY = "ancap_earth_weather_accu_v4";
const OPEN_KEY = "ancap_earth_widget_open_v1";
const CACHE_TTL_MS = 12 * 60 * 1000;

type GeoInfo = {
  lat: number;
  lon: number;
  city: string;
  country: string;
  timezone: string;
};

type WeatherInfo = {
  tempC: number | null;
  realFeelC: number | null;
  realFeelPhrase: string | null;
  text: string | null;
  iconUrl: string | null;
  windKmh: number | null;
  windGustKmh: number | null;
  windDir: string | null;
  humidity: number | null;
  uvIndex: number | null;
  uvText: string | null;
  visibilityKm: number | null;
  cloudCover: number | null;
  pressureMb: number | null;
  pressureTendency: string | null;
  dewPointC: number | null;
  precip24hMm: number | null;
  forecastMin: number | null;
  forecastMax: number | null;
  forecastDay: string | null;
  forecastNight: string | null;
  precipDayPct: number | null;
  nextHourTemp: number | null;
  nextHourText: string | null;
  nextHourPrecip: number | null;
  accuweatherUrl: string;
  attribution: string;
  city?: string | null;
  country?: string | null;
  adminArea?: string | null;
  timezone?: string | null;
  isDayTime?: boolean | null;
};

type CacheEnvelope<T> = { savedAt: number; data: T };

function readCache<T>(key: string): T | null {
  try {
    const raw = sessionStorage.getItem(key);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as CacheEnvelope<T>;
    if (!parsed?.savedAt || Date.now() - parsed.savedAt > CACHE_TTL_MS) return null;
    return parsed.data;
  } catch {
    return null;
  }
}

function writeCache<T>(key: string, data: T) {
  try {
    sessionStorage.setItem(key, JSON.stringify({ savedAt: Date.now(), data } satisfies CacheEnvelope<T>));
  } catch {
    /* ignore */
  }
}

function fmtTemp(v: number | null | undefined): string {
  if (v == null || !Number.isFinite(v)) return "—";
  const n = Math.round(v);
  return `${n > 0 ? "+" : ""}${n}°`;
}

function parseLatLon(raw: unknown): { lat: number; lon: number } | null {
  if (typeof raw === "string" && raw.includes(",")) {
    const [a, b] = raw.split(",");
    const lat = Number(a);
    const lon = Number(b);
    if (Number.isFinite(lat) && Number.isFinite(lon)) return { lat, lon };
  }
  return null;
}

/** geojs.io is often blocked in-browser; try CORS-friendly providers next. */
async function fetchGeo(): Promise<GeoInfo> {
  const cached = readCache<GeoInfo>(GEO_CACHE_KEY);
  if (cached) return cached;

  const tzFallback = Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC";
  const attempts: Array<() => Promise<GeoInfo>> = [
    async () => {
      const res = await fetch("https://ipwho.is/", { signal: AbortSignal.timeout(8000) });
      if (!res.ok) throw new Error("ipwho failed");
      const j = (await res.json()) as Record<string, unknown>;
      if (j.success === false) throw new Error("ipwho denied");
      const lat = Number(j.latitude);
      const lon = Number(j.longitude);
      if (!Number.isFinite(lat) || !Number.isFinite(lon)) throw new Error("ipwho coords");
      return {
        lat,
        lon,
        city: String(j.city || j.region || "—"),
        country: String(j.country || j.country_code || ""),
        timezone: String(j.timezone || tzFallback),
      };
    },
    async () => {
      const res = await fetch("https://ipinfo.io/json", { signal: AbortSignal.timeout(8000) });
      if (!res.ok) throw new Error("ipinfo failed");
      const j = (await res.json()) as Record<string, unknown>;
      const coords = parseLatLon(j.loc);
      if (!coords) throw new Error("ipinfo coords");
      return {
        lat: coords.lat,
        lon: coords.lon,
        city: String(j.city || j.region || "—"),
        country: String(j.country || ""),
        timezone: String(j.timezone || tzFallback),
      };
    },
    async () => {
      const res = await fetch("https://get.geojs.io/v1/ip/geo.json", { signal: AbortSignal.timeout(8000) });
      if (!res.ok) throw new Error("geojs failed");
      const j = (await res.json()) as Record<string, unknown>;
      const lat = Number(j.latitude);
      const lon = Number(j.longitude);
      if (!Number.isFinite(lat) || !Number.isFinite(lon)) throw new Error("geojs coords");
      return {
        lat,
        lon,
        city: String(j.city || j.region || "—"),
        country: String(j.country || j.country_code || ""),
        timezone: String(j.timezone || tzFallback),
      };
    },
  ];

  let lastErr: unknown;
  for (const attempt of attempts) {
    try {
      const data = await attempt();
      writeCache(GEO_CACHE_KEY, data);
      return data;
    } catch (err) {
      lastErr = err;
    }
  }

  // Last resort: keep clock/weather usable near a stable EU desk pin (Bucharest).
  const fallback: GeoInfo = {
    lat: 44.4268,
    lon: 26.1025,
    city: "Local",
    country: "",
    timezone: tzFallback,
  };
  writeCache(GEO_CACHE_KEY, fallback);
  if (lastErr) {
    console.warn("earth-widget geo providers failed; using timezone fallback", lastErr);
  }
  return fallback;
}

async function fetchWeather(lat: number, lon: number): Promise<WeatherInfo> {
  const cached = readCache<WeatherInfo>(WEATHER_CACHE_KEY);
  if (cached) return cached;
  const p = await weatherApi.current(lat, lon);
  const ft = p?.forecast_today || null;
  const nh = p?.next_hour || null;
  const data: WeatherInfo = {
    tempC: typeof p?.temperature_c === "number" ? p.temperature_c : null,
    realFeelC: typeof p?.realfeel_c === "number" ? p.realfeel_c : null,
    realFeelPhrase: typeof p?.realfeel_phrase === "string" ? p.realfeel_phrase : null,
    text: typeof p?.weather_text === "string" ? p.weather_text : null,
    iconUrl: typeof p?.weather_icon_url === "string" ? p.weather_icon_url : null,
    windKmh: typeof p?.wind_kmh === "number" ? p.wind_kmh : null,
    windGustKmh: typeof p?.wind_gust_kmh === "number" ? p.wind_gust_kmh : null,
    windDir: typeof p?.wind_dir === "string" ? p.wind_dir : null,
    humidity: typeof p?.relative_humidity === "number" ? p.relative_humidity : null,
    uvIndex: typeof p?.uv_index === "number" ? p.uv_index : null,
    uvText: typeof p?.uv_text === "string" ? p.uv_text : null,
    visibilityKm: typeof p?.visibility_km === "number" ? p.visibility_km : null,
    cloudCover: typeof p?.cloud_cover === "number" ? p.cloud_cover : null,
    pressureMb: typeof p?.pressure_mb === "number" ? p.pressure_mb : null,
    pressureTendency: typeof p?.pressure_tendency === "string" ? p.pressure_tendency : null,
    dewPointC: typeof p?.dew_point_c === "number" ? p.dew_point_c : null,
    precip24hMm: typeof p?.precip_24h_mm === "number" ? p.precip_24h_mm : null,
    forecastMin: typeof ft?.min_c === "number" ? ft.min_c : null,
    forecastMax: typeof ft?.max_c === "number" ? ft.max_c : null,
    forecastDay: typeof ft?.day_text === "string" ? ft.day_text : null,
    forecastNight: typeof ft?.night_text === "string" ? ft.night_text : null,
    precipDayPct: typeof ft?.precip_probability_day === "number" ? ft.precip_probability_day : null,
    nextHourTemp: typeof nh?.temperature_c === "number" ? nh.temperature_c : null,
    nextHourText: typeof nh?.weather_text === "string" ? nh.weather_text : null,
    nextHourPrecip: typeof nh?.precip_probability === "number" ? nh.precip_probability : null,
    accuweatherUrl:
      typeof p?.accuweather_url === "string" && p.accuweather_url
        ? p.accuweather_url
        : "https://www.accuweather.com/",
    attribution:
      typeof p?.attribution === "string" && p.attribution
        ? p.attribution
        : "Weather data provided by AccuWeather",
    city: p?.city ?? null,
    country: p?.country ?? null,
    adminArea: p?.admin_area ?? null,
    timezone: p?.timezone ?? null,
    isDayTime: typeof p?.is_day_time === "boolean" ? p.is_day_time : null,
  };
  writeCache(WEATHER_CACHE_KEY, data);
  return data;
}

function formatClock(now: Date, timeZone: string): string {
  try {
    return new Intl.DateTimeFormat(undefined, {
      timeZone,
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false,
    }).format(now);
  } catch {
    return now.toISOString().slice(11, 19);
  }
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-white/8 bg-white/[0.03] px-2 py-1.5">
      <div className="text-[9px] uppercase tracking-[0.12em] text-white/40">{label}</div>
      <div className="mt-0.5 text-[11px] font-medium text-white/85">{value}</div>
    </div>
  );
}

export function FloatingEarthSupportWidget() {
  const [geo, setGeo] = useState<GeoInfo | null>(null);
  const [weather, setWeather] = useState<WeatherInfo | null>(null);
  const [now, setNow] = useState(() => new Date());
  const [error, setError] = useState("");
  const [supportOpen, setSupportOpen] = useState(false);
  const [open, setOpen] = useState(false);
  const [ready, setReady] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const mq = window.matchMedia("(max-width: 767px)");
    const apply = () => setIsMobile(mq.matches);
    apply();
    mq.addEventListener("change", apply);
    try {
      const stored = localStorage.getItem(OPEN_KEY);
      if (stored === "1") setOpen(true);
      else if (stored === "0") setOpen(false);
      else setOpen(!mq.matches);
    } catch {
      setOpen(!mq.matches);
    }
    setReady(true);
    return () => mq.removeEventListener("change", apply);
  }, []);

  useEffect(() => {
    const onPeer = (ev: Event) => {
      const detail = (ev as CustomEvent<FloatingWidgetEventDetail>).detail;
      if (!detail || detail.id === "earth") return;
      if (detail.open && isMobile) setOpen(false);
    };
    window.addEventListener(FLOATING_WIDGET_EVENT, onPeer as EventListener);
    return () => window.removeEventListener(FLOATING_WIDGET_EVENT, onPeer as EventListener);
  }, [isMobile]);

  useEffect(() => {
    const id = window.setInterval(() => setNow(new Date()), 1000);
    return () => window.clearInterval(id);
  }, []);

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      let g: GeoInfo | null = null;
      try {
        g = await fetchGeo();
        if (cancelled) return;
        setGeo(g);
      } catch {
        if (!cancelled) setError("гео временно недоступен");
      }
      try {
        const lat = g?.lat ?? 44.4268;
        const lon = g?.lon ?? 26.1025;
        const w = await fetchWeather(lat, lon);
        if (cancelled) return;
        setWeather(w);
        setError("");
      } catch {
        if (!cancelled) setError((prev) => prev || "погода временно недоступна");
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const setOpenPersist = (next: boolean) => {
    setOpen(next);
    emitFloatingWidget("earth", next);
    try {
      localStorage.setItem(OPEN_KEY, next ? "1" : "0");
    } catch {
      /* ignore */
    }
  };

  const tz =
    weather?.timezone || geo?.timezone || Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC";
  const clock = useMemo(() => formatClock(now, tz), [now, tz]);

  const place = weather?.city
    ? [weather.city, weather.adminArea || weather.country].filter(Boolean).join(", ")
    : geo
      ? [geo.city, geo.country].filter(Boolean).join(", ")
      : error
        ? "—"
        : "определяем…";

  if (!ready) return null;

  if (!open) {
    return (
      <div className="pointer-events-none fixed bottom-[max(0.85rem,env(safe-area-inset-bottom))] right-3 z-[90] sm:right-4">
        <button
          type="button"
          onClick={() => setOpenPersist(true)}
          className="pointer-events-auto ancap-fab-slide-in flex items-center gap-2 rounded-full border border-sky-400/30 bg-[#071020]/94 px-3.5 py-2.5 text-[11px] font-semibold uppercase tracking-[0.14em] text-sky-100 shadow-[0_12px_40px_rgba(0,0,0,0.45)] backdrop-blur-md hover:border-sky-300/45"
          aria-label="Открыть Earth / AccuWeather"
        >
          <span className="ancap-earth ancap-earth--fab" aria-hidden="true">
            <span className="ancap-earth__map" />
            <span className="ancap-earth__shine" />
          </span>
          Earth
        </button>
      </div>
    );
  }

  return (
    <aside
      aria-label="Локальное время, погода AccuWeather и поддержка"
      className="pointer-events-none fixed bottom-[max(0.85rem,env(safe-area-inset-bottom))] right-3 z-[90] w-[min(20rem,calc(100vw-1.5rem))] sm:right-4"
    >
      <div className="pointer-events-auto ancap-panel-rise overflow-hidden rounded-2xl border border-white/12 bg-[#071020]/95 text-white shadow-[0_18px_50px_rgba(0,0,0,0.5)] backdrop-blur-xl">
        <div className="relative overflow-hidden border-b border-white/10 px-3 pb-3 pt-3">
          <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_20%_0%,rgba(56,189,248,0.16),transparent_55%)]" />
          <div className="relative flex items-start gap-3">
            <div className="ancap-earth ancap-earth--lg" aria-hidden="true">
              <div className="ancap-earth__map" />
              <div className="ancap-earth__shine" />
            </div>
            <div className="min-w-0 flex-1">
              <div className="flex items-start justify-between gap-2">
                <div>
                  <div className="text-[10px] font-semibold uppercase tracking-[0.16em] text-sky-200/90">
                    Live · AccuWeather
                  </div>
                  <div className="mt-1 font-mono text-[1.35rem] font-semibold leading-none tracking-tight text-white">
                    {clock}
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => setOpenPersist(false)}
                  className="rounded-md border border-white/10 px-2 py-1 text-[11px] text-white/55 hover:border-white/25 hover:text-white"
                >
                  {isMobile ? "Закрыть" : "Свернуть"}
                </button>
              </div>
              <div className="mt-1.5 truncate text-[11px] text-white/55" title={place}>
                {place}
              </div>
              <div className="mt-2 flex items-center gap-2">
                {weather?.iconUrl ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img
                    src={weather.iconUrl}
                    alt=""
                    width={38}
                    height={38}
                    className="h-[38px] w-[38px]"
                    onError={(e) => {
                      e.currentTarget.style.display = "none";
                    }}
                  />
                ) : null}
                <div className="min-w-0">
                  <div className="flex flex-wrap items-baseline gap-x-2">
                    <span className="text-xl font-semibold text-emerald-200">{fmtTemp(weather?.tempC)}</span>
                    <span className="text-xs text-white/55">{weather?.text || "—"}</span>
                  </div>
                  {weather?.realFeelC != null ? (
                    <div className="text-[11px] text-white/45">
                      RealFeel {fmtTemp(weather.realFeelC)}
                      {weather.realFeelPhrase ? ` · ${weather.realFeelPhrase}` : ""}
                    </div>
                  ) : null}
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-1.5 px-3 py-2.5">
          <Stat
            label="Ветер"
            value={
              weather?.windKmh != null
                ? `${Math.round(weather.windKmh)} км/ч${weather.windDir ? ` ${weather.windDir}` : ""}`
                : "—"
            }
          />
          <Stat
            label="Порывы"
            value={weather?.windGustKmh != null ? `${Math.round(weather.windGustKmh)} км/ч` : "—"}
          />
          <Stat label="Влажность" value={weather?.humidity != null ? `${weather.humidity}%` : "—"} />
          <Stat
            label="UV"
            value={
              weather?.uvIndex != null
                ? `${Number(weather.uvIndex).toFixed(1)}${weather.uvText ? ` · ${weather.uvText}` : ""}`
                : "—"
            }
          />
          <Stat
            label="Видимость"
            value={weather?.visibilityKm != null ? `${Math.round(weather.visibilityKm)} км` : "—"}
          />
          <Stat label="Облачность" value={weather?.cloudCover != null ? `${weather.cloudCover}%` : "—"} />
          <Stat
            label="Давление"
            value={
              weather?.pressureMb != null
                ? `${Math.round(weather.pressureMb)} mb${weather.pressureTendency ? ` · ${weather.pressureTendency}` : ""}`
                : "—"
            }
          />
          <Stat label="Точка росы" value={fmtTemp(weather?.dewPointC)} />
        </div>

        {(weather?.forecastDay || weather?.forecastMax != null || weather?.nextHourText) && (
          <div className="space-y-1.5 border-t border-white/10 px-3 py-2.5 text-[11px]">
            {weather?.forecastMax != null || weather?.forecastDay ? (
              <div className="rounded-xl border border-sky-400/15 bg-sky-400/[0.06] px-3 py-2">
                <div className="text-[9px] uppercase tracking-[0.14em] text-sky-200/80">Сегодня</div>
                <div className="mt-1 text-white/85">
                  {fmtTemp(weather.forecastMin)}…{fmtTemp(weather.forecastMax)}
                  {weather.forecastDay ? ` · ${weather.forecastDay}` : ""}
                </div>
                {weather.forecastNight ? (
                  <div className="mt-0.5 text-white/45">Ночь · {weather.forecastNight}</div>
                ) : null}
                {weather.precipDayPct != null ? (
                  <div className="mt-0.5 text-white/45">Осадки днём · {weather.precipDayPct}%</div>
                ) : null}
              </div>
            ) : null}
            {weather?.nextHourText || weather?.nextHourTemp != null ? (
              <div className="rounded-xl border border-white/10 bg-white/[0.03] px-3 py-2 text-white/70">
                След. час · {fmtTemp(weather.nextHourTemp)} · {weather.nextHourText || "—"}
                {weather.nextHourPrecip != null ? ` · осадки ${weather.nextHourPrecip}%` : ""}
              </div>
            ) : null}
            {weather?.precip24hMm != null && weather.precip24hMm > 0 ? (
              <div className="text-white/45">Осадки 24ч · {weather.precip24hMm.toFixed(1)} мм</div>
            ) : null}
          </div>
        )}

        <div className="flex items-center justify-between gap-2 border-t border-white/10 px-3 py-2">
          <a
            href={weather?.accuweatherUrl || "https://www.accuweather.com/"}
            target="_blank"
            rel="noreferrer"
            className="text-[10px] font-semibold uppercase tracking-[0.12em] text-sky-200/90 hover:text-sky-100"
          >
            AccuWeather ↗
          </a>
          {geo ? (
            <span className="text-[10px] text-white/35">
              {geo.lat.toFixed(2)}°, {geo.lon.toFixed(2)}°
            </span>
          ) : error ? (
            <span className="text-[10px] text-amber-200/80">{error}</span>
          ) : null}
        </div>

        <div className="border-t border-white/10 px-3 py-2.5">
          <button
            type="button"
            onClick={() => setSupportOpen((v) => !v)}
            className="flex w-full items-center justify-between gap-2 rounded-xl border border-emerald-400/25 bg-emerald-400/[0.08] px-3 py-2 text-left hover:border-emerald-300/40 hover:bg-emerald-400/[0.12]"
          >
            <span className="text-xs font-semibold text-emerald-100">Support 24/7</span>
            <span className="rounded-full bg-emerald-400/20 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-emerald-200">
              Online
            </span>
          </button>
          {supportOpen ? (
            <div className="mt-2 space-y-1.5 text-[12px]">
              <a
                href="mailto:support@ancap.cloud"
                className="block rounded-lg border border-white/10 bg-black/20 px-3 py-2 text-white/80 hover:border-white/25 hover:text-white"
              >
                support@ancap.cloud
              </a>
              <a
                href="https://t.me/ancap24news"
                target="_blank"
                rel="noreferrer"
                className="block rounded-lg border border-white/10 bg-black/20 px-3 py-2 text-white/80 hover:border-white/25 hover:text-white"
              >
                Telegram · @ancap24news
              </a>
              <Link
                href="/legal/market-data"
                className="block rounded-lg border border-white/10 bg-black/20 px-3 py-2 text-white/80 hover:border-white/25 hover:text-white"
              >
                Legal · AccuWeather / market data
              </Link>
            </div>
          ) : null}
        </div>
      </div>
    </aside>
  );
}
