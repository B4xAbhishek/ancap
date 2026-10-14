"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import { projectPresentation } from "@/lib/solutionPortfolio";
import { Navigation } from "@/components/Navigation";
import { useAuth } from "@/components/AuthProvider";
import { useLanguage } from "@/components/LanguageProvider";
import { getApiUrl, apiFetch } from "@/lib/api";

type LunarStatus = {
  feature_enabled: boolean;
  tagline: string;
  parcels_listed: number;
  interests_open: number;
  science_note: string;
  compliance_note: string;
  lfm_reference: string;
  next_gate: string;
};

type LunarParcel = {
  id: string;
  parcel_code: string;
  name: string;
  region: string;
  lat_deg: number;
  lon_deg: number;
  area_km2: number;
  list_price_acp: string;
  status: string;
  lfm_themes: string[];
  summary: string;
};

export default function LunarPage() {
  const { t, lang } = useLanguage();
  const projectCopy = projectPresentation(lang, "/lunar");
  const { isAuthenticated } = useAuth();
  const [status, setStatus] = useState<LunarStatus | null>(null);
  const [parcels, setParcels] = useState<LunarParcel[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [kind, setKind] = useState<"inquire" | "reserve" | "bid">("inquire");
  const [budget, setBudget] = useState("");
  const [notes, setNotes] = useState("");
  const [consent, setConsent] = useState(false);
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const [st, pl] = await Promise.all([
          fetch(`${getApiUrl()}/lunar/status`, { credentials: "omit" }),
          fetch(`${getApiUrl()}/lunar/parcels`, { credentials: "omit" }),
        ]);
        if (!st.ok || !pl.ok) {
          if (!cancelled) setErr(t("lunarPage.loadFailed"));
          return;
        }
        const statusJson = (await st.json()) as LunarStatus;
        const parcelsJson = (await pl.json()) as LunarParcel[];
        if (cancelled) return;
        setStatus(statusJson);
        setParcels(parcelsJson);
        if (parcelsJson[0]) {
          setSelectedId(parcelsJson[0].id);
          setBudget(String(parcelsJson[0].list_price_acp));
        }
      } catch {
        if (!cancelled) setErr(t("lunarPage.loadFailed"));
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [t]);

  const selected = parcels.find((p) => p.id === selectedId) || null;

  const onSelect = (p: LunarParcel) => {
    setSelectedId(p.id);
    setBudget(String(p.list_price_acp));
    setMsg(null);
    setErr(null);
  };

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!selected || !isAuthenticated) return;
    setBusy(true);
    setMsg(null);
    setErr(null);
    try {
      await apiFetch("/lunar/interests", {
        method: "POST",
        body: JSON.stringify({
          parcel_id: selected.id,
          kind,
          budget_acp: budget,
          notes: notes || null,
          consent_acknowledged: consent,
        }),
      });
      setMsg(t("lunarPage.submitted"));
      const st = await fetch(`${getApiUrl()}/lunar/status`, { credentials: "omit" });
      if (st.ok) setStatus((await st.json()) as LunarStatus);
      const pl = await fetch(`${getApiUrl()}/lunar/parcels`, { credentials: "omit" });
      if (pl.ok) setParcels((await pl.json()) as LunarParcel[]);
    } catch {
      setErr(t("lunarPage.submitFailed"));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#07060a] text-[#f2efe8]">
      <Navigation />

      <section className="relative min-h-[100svh] overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_70%_20%,#3a3428_0%,transparent_45%),radial-gradient(ellipse_at_20%_80%,#1a2230_0%,#07060a_55%)]" />
        <div
          className="pointer-events-none absolute -right-[18%] top-[8%] h-[70vmin] w-[70vmin] rounded-full opacity-90"
          style={{
            background:
              "radial-gradient(circle at 35% 35%, #d7d0c2 0%, #9a9182 28%, #4a453c 62%, #14120f 78%, transparent 79%)",
            boxShadow: "0 0 80px rgba(215,208,194,0.12)",
            animation: "lunarDrift 28s ease-in-out infinite alternate",
          }}
        />
        <div className="pointer-events-none absolute inset-0 bg-[linear-gradient(105deg,rgba(7,6,10,0.92)_0%,rgba(7,6,10,0.55)_48%,rgba(7,6,10,0.2)_100%)]" />

        <div className="relative mx-auto flex min-h-[100svh] max-w-6xl flex-col justify-end px-4 pb-16 pt-28 sm:px-6 lg:px-8">
          <p className="font-[family-name:var(--font-display,inherit)] text-[clamp(3.5rem,12vw,8rem)] font-black leading-[0.85] tracking-[-0.06em] text-[#f7f3ea]">
            {t("lunarPage.brand")}
          </p>
          <h1 className="mt-5 max-w-xl text-xl font-medium tracking-[-0.02em] text-[#f7f3ea]/90 sm:text-2xl">
            {projectCopy.title}
          </h1>
          <p className="mt-4 max-w-lg text-sm leading-7 text-[#f7f3ea]/65">{projectCopy.lead}</p>
          <div className="mt-8 flex flex-wrap gap-3">
            <a
              href="#catalog"
              className="rounded-md bg-[#d7d0c2] px-5 py-3 text-sm font-semibold text-[#1a1712] transition hover:bg-[#ebe4d6]"
            >
              {t("lunarPage.browseCta")}
            </a>
            <Link
              href="/galaxy"
              className="rounded-md border border-[#f7f3ea]/30 px-5 py-3 text-sm font-medium text-[#f7f3ea]/90 transition hover:border-[#f7f3ea]/60"
            >
              {t("lunarPage.galaxyCta")}
            </Link>
          </div>
        </div>
      </section>

      <main className="mx-auto max-w-6xl px-4 py-16 sm:px-6 lg:px-8">
        <section className="max-w-2xl">
          <p className="text-xs uppercase tracking-[0.16em] text-[#f7f3ea]/40">{t("lunarPage.scienceKicker")}</p>
          <h2 className="mt-2 text-2xl font-semibold tracking-[-0.03em]">{t("lunarPage.scienceTitle")}</h2>
          <p className="mt-3 text-sm leading-7 text-[#f7f3ea]/65">
            {status?.science_note || t("lunarPage.scienceLead")}
          </p>
          <a
            href={status?.lfm_reference || "https://lnkd.in/p/e-SbXYMZ"}
            target="_blank"
            rel="noreferrer"
            className="mt-4 inline-block text-sm text-[#c9b896] underline decoration-[#c9b896]/40 underline-offset-4 hover:text-[#e4d7b8]"
          >
            {t("lunarPage.scienceLink")}
          </a>
        </section>

        {status ? (
          <section className="mt-12 border-t border-white/10 pt-10">
            <h2 className="text-lg font-medium">{t("lunarPage.statusTitle")}</h2>
            <p className="mt-2 text-sm text-[#f7f3ea]/60">{status.tagline}</p>
            <ul className="mt-4 space-y-1 text-sm text-[#f7f3ea]/70">
              <li>
                {t("lunarPage.parcels")}: {status.parcels_listed} · {t("lunarPage.interests")}: {status.interests_open}
              </li>
              <li>
                Feature: {status.feature_enabled ? t("lunarPage.featureOn") : t("lunarPage.featureOff")}
              </li>
              <li>
                {t("lunarPage.next")} {status.next_gate}
              </li>
            </ul>
            <p className="mt-4 max-w-2xl text-xs leading-6 text-[#f7f3ea]/45">
              {status.compliance_note || t("lunarPage.complianceFallback")}
            </p>
          </section>
        ) : null}

        <section id="catalog" className="mt-14 scroll-mt-24">
          <h2 className="text-2xl font-semibold tracking-[-0.03em]">{t("lunarPage.catalogTitle")}</h2>
          <p className="mt-3 max-w-2xl text-sm leading-7 text-[#f7f3ea]/65">{t("lunarPage.catalogLead")}</p>

          {err && !parcels.length ? <p className="mt-6 text-sm text-red-300">{err}</p> : null}
          {!parcels.length && !err ? <p className="mt-6 text-sm text-[#f7f3ea]/50">{t("lunarPage.loading")}</p> : null}

          <div className="mt-8 grid gap-3">
            {parcels.map((p) => {
              const active = p.id === selectedId;
              return (
                <button
                  key={p.id}
                  type="button"
                  onClick={() => onSelect(p)}
                  className={`w-full border px-4 py-4 text-left transition ${
                    active
                      ? "border-[#d7d0c2]/50 bg-[#d7d0c2]/10"
                      : "border-white/10 bg-transparent hover:border-white/25"
                  }`}
                >
                  <div className="flex flex-wrap items-baseline justify-between gap-2">
                    <div>
                      <div className="font-mono text-xs text-[#c9b896]">{p.parcel_code}</div>
                      <div className="mt-1 text-base font-medium text-[#f7f3ea]">{p.name}</div>
                      <div className="mt-1 text-xs text-[#f7f3ea]/50">{p.region}</div>
                    </div>
                    <div className="text-right text-sm text-[#f7f3ea]/80">
                      {t("lunarPage.price")}: {p.list_price_acp} ACP
                    </div>
                  </div>
                  <p className="mt-3 text-sm leading-6 text-[#f7f3ea]/60">{p.summary}</p>
                  <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-xs text-[#f7f3ea]/45">
                    <span>
                      {t("lunarPage.area")}: {p.area_km2} km²
                    </span>
                    <span>
                      {t("lunarPage.coords")}: {p.lat_deg}, {p.lon_deg}
                    </span>
                    <span>
                      {t("lunarPage.status")}: {p.status}
                    </span>
                    <span>
                      {t("lunarPage.themes")}: {(p.lfm_themes || []).join(", ") || "—"}
                    </span>
                  </div>
                </button>
              );
            })}
          </div>

          {selected ? (
            <form onSubmit={onSubmit} className="mt-10 max-w-xl border-t border-white/10 pt-8">
              <h3 className="text-lg font-medium">{t("lunarPage.interestTitle")}</h3>
              <p className="mt-1 font-mono text-xs text-[#c9b896]">{selected.parcel_code}</p>

              {!isAuthenticated ? (
                <p className="mt-4 text-sm text-[#f7f3ea]/60">
                  <Link href="/login?next=/lunar" className="text-[#c9b896] underline">
                    {t("lunarPage.signIn")}
                  </Link>
                </p>
              ) : (
                <>
                  <label className="mt-4 block text-sm text-[#f7f3ea]/70">
                    {t("lunarPage.kind")}
                    <select
                      className="mt-1 w-full border border-white/15 bg-[#0d0c10] px-3 py-2 text-sm"
                      value={kind}
                      onChange={(e) => setKind(e.target.value as typeof kind)}
                    >
                      <option value="inquire">inquire</option>
                      <option value="reserve">reserve</option>
                      <option value="bid">bid</option>
                    </select>
                  </label>
                  <label className="mt-3 block text-sm text-[#f7f3ea]/70">
                    {t("lunarPage.budget")}
                    <input
                      className="mt-1 w-full border border-white/15 bg-[#0d0c10] px-3 py-2 font-mono text-sm"
                      value={budget}
                      onChange={(e) => setBudget(e.target.value)}
                      required
                    />
                  </label>
                  <label className="mt-3 block text-sm text-[#f7f3ea]/70">
                    {t("lunarPage.notes")}
                    <textarea
                      className="mt-1 w-full border border-white/15 bg-[#0d0c10] px-3 py-2 text-sm"
                      rows={3}
                      value={notes}
                      onChange={(e) => setNotes(e.target.value)}
                    />
                  </label>
                  <label className="mt-4 flex items-start gap-2 text-xs leading-5 text-[#f7f3ea]/65">
                    <input
                      type="checkbox"
                      className="mt-0.5"
                      checked={consent}
                      onChange={(e) => setConsent(e.target.checked)}
                      required
                    />
                    <span>{t("lunarPage.consent")}</span>
                  </label>
                  <button
                    type="submit"
                    disabled={busy || !consent}
                    className="mt-5 rounded-md bg-[#d7d0c2] px-5 py-3 text-sm font-semibold text-[#1a1712] disabled:opacity-50"
                  >
                    {busy ? t("lunarPage.submitting") : t("lunarPage.submit")}
                  </button>
                  {msg ? <p className="mt-3 text-sm text-emerald-300">{msg}</p> : null}
                  {err ? <p className="mt-3 text-sm text-red-300">{err}</p> : null}
                </>
              )}
            </form>
          ) : null}
        </section>
      </main>

      <style>{`
        @keyframes lunarDrift {
          from { transform: translate3d(0, 0, 0) scale(1); }
          to { transform: translate3d(-3%, 2%, 0) scale(1.04); }
        }
      `}</style>
    </div>
  );
}
