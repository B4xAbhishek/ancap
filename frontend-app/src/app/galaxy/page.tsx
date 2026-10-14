"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { projectPresentation } from "@/lib/solutionPortfolio";
import { Navigation } from "@/components/Navigation";
import { GalaxySolarSystem } from "@/components/GalaxySolarSystem";
import { useAuth } from "@/components/AuthProvider";
import { useLanguage } from "@/components/LanguageProvider";
import { getApiUrl, spaceAuction } from "@/lib/api";

type LotKind =
  | "star"
  | "planet"
  | "satellite"
  | "dwarf_planet"
  | "asteroid"
  | "comet"
  | "nebula"
  | "galaxy"
  | "black_hole"
  | "exoplanet"
  | "radiation";

type Lot = {
  id: string;
  kind: LotKind;
  name: string;
  designation: string;
  parent?: string | null;
  blurb: string;
  starting_acp: string;
  current_acp: string;
  min_next_acp: string;
  bid_count: number;
  featured?: boolean;
};

type Catalog = {
  title: string;
  tagline: string;
  compliance_note: string;
  lots: Lot[];
  featured: Lot[];
};

function formatAcp(value: string) {
  const n = Number(value);
  if (!Number.isFinite(n)) return `${value} ACP`;
  return `${n.toLocaleString()} ACP`;
}

export default function GalaxyAuctionPage() {
  const { t, lang } = useLanguage();
  const projectCopy = projectPresentation(lang, "/galaxy");
  const { isAuthenticated } = useAuth();
  const [catalog, setCatalog] = useState<Catalog | null>(null);
  const [error, setError] = useState("");
  const [filter, setFilter] = useState<"all" | LotKind>("all");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [amount, setAmount] = useState("");
  const [busy, setBusy] = useState(false);
  const [info, setInfo] = useState("");

  const load = async () => {
    try {
      const data = (await spaceAuction.catalog()) as Catalog;
      setCatalog(data);
      setError("");
    } catch (err) {
      try {
        const res = await fetch(`${getApiUrl()}/space-auction/catalog`, { credentials: "omit" });
        if (!res.ok) throw new Error(`Catalog failed (${res.status})`);
        setCatalog((await res.json()) as Catalog);
        setError("");
      } catch (inner) {
        setError(inner instanceof Error ? inner.message : t("galaxy.loadError"));
      }
    }
  };

  useEffect(() => {
    void load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const lots = useMemo(() => {
    const items = catalog?.lots || [];
    if (filter === "all") return items;
    return items.filter((lot) => lot.kind === filter);
  }, [catalog, filter]);

  const selected = lots.find((lot) => lot.id === selectedId) || catalog?.lots.find((lot) => lot.id === selectedId);

  useEffect(() => {
    if (selected) setAmount(selected.min_next_acp);
  }, [selected?.id, selected?.min_next_acp]);

  const placeBid = async (lot: Lot) => {
    setBusy(true);
    setInfo("");
    setError("");
    try {
      await spaceAuction.bid(lot.id, { amount_acp: amount || lot.min_next_acp });
      setInfo(t("galaxy.bidPlaced"));
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : t("galaxy.bidError"));
    } finally {
      setBusy(false);
    }
  };

  const kindLabel = (kind: LotKind) => {
    const labels: Record<LotKind, string> = {
      star: t("galaxy.stars"),
      planet: t("galaxy.planets"),
      satellite: t("galaxy.satellites"),
      dwarf_planet: t("galaxy.dwarfPlanets"),
      asteroid: t("galaxy.asteroids"),
      comet: t("galaxy.comets"),
      nebula: t("galaxy.nebulae"),
      galaxy: t("galaxy.galaxies"),
      black_hole: t("galaxy.blackHoles"),
      exoplanet: t("galaxy.exoplanets"),
      radiation: t("galaxy.radiation"),
    };
    return labels[kind];
  };

  const filters: Array<"all" | LotKind> = [
    "all",
    "star",
    "planet",
    "satellite",
    "dwarf_planet",
    "asteroid",
    "comet",
    "nebula",
    "galaxy",
    "black_hole",
    "exoplanet",
    "radiation",
  ];

  return (
    <div className="min-h-screen bg-[#050814] text-[#e8eef8]">
      <Navigation />
      <main>
        <section className="relative overflow-hidden">
          <GalaxySolarSystem />
          <div className="container" style={{ padding: "28px 24px 12px" }}>
            <span className="section-num">{t("galaxy.kicker")}</span>
            <h1 className="section-title" style={{ marginBottom: 12 }}>
              {projectCopy.title}
            </h1>
            <p className="section-subtitle" style={{ maxWidth: 720, marginBottom: 0 }}>
              {projectCopy.lead}
            </p>
          </div>
        </section>

        <section className="container" style={{ padding: "28px 24px 72px" }}>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 10, marginBottom: 22 }}>
            {filters.map((key) => (
              <button
                key={key}
                type="button"
                className={filter === key ? "btn btn-primary" : "btn btn-ghost"}
                onClick={() => setFilter(key)}
              >
                {key === "all" ? t("galaxy.allLots") : kindLabel(key)}
              </button>
            ))}
          </div>

          {error && <p style={{ color: "#fbbf24", marginBottom: 16 }}>{error}</p>}
          {info && <p style={{ color: "var(--accent-strong)", marginBottom: 16 }}>{info}</p>}

          <div className="responsive-grid responsive-grid-3">
            {lots.map((lot) => (
              <article
                key={lot.id}
                className="card"
                style={{
                  borderRadius: 12,
                  background: "rgba(12, 18, 40, 0.88)",
                  border: selectedId === lot.id ? "1px solid rgba(125, 211, 252, 0.55)" : undefined,
                }}
              >
                <div className="card-header">
                  <span className="badge badge-info">{kindLabel(lot.kind)}</span>
                  <strong style={{ color: "var(--accent-strong)" }}>{formatAcp(lot.current_acp)}</strong>
                </div>
                <h2 style={{ fontSize: "1.2rem", fontWeight: 800, marginBottom: 6 }}>{lot.name}</h2>
                <p style={{ color: "var(--text-muted)", fontSize: "0.85rem", marginBottom: 10 }}>
                  {lot.designation}
                  {lot.parent ? ` · ${lot.parent}` : ""}
                </p>
                <p style={{ color: "var(--text-muted)", lineHeight: 1.6, minHeight: 72 }}>{lot.blurb}</p>
                <p style={{ fontSize: "0.85rem", color: "var(--text-muted)", marginBottom: 14 }}>
                  {t("galaxy.starting")}: {formatAcp(lot.starting_acp)} · {t("galaxy.bids")}: {lot.bid_count}
                </p>
                <button
                  type="button"
                  className="btn btn-ghost"
                  onClick={() => setSelectedId(lot.id)}
                >
                  {t("galaxy.selectLot")}
                </button>
              </article>
            ))}
          </div>

          {selected && (
            <div className="card" style={{ marginTop: 28, borderRadius: 12, background: "rgba(12, 18, 40, 0.92)" }}>
              <h2 style={{ fontSize: "1.25rem", fontWeight: 800, marginBottom: 8 }}>
                {t("galaxy.bidOn")} {selected.name}
              </h2>
              <p style={{ color: "var(--text-muted)", marginBottom: 16 }}>
                {t("galaxy.minBid")}: {formatAcp(selected.min_next_acp)}
              </p>
              <div className="action-cluster">
                <input
                  className="input input-bordered"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  inputMode="decimal"
                  aria-label={t("galaxy.bidAmount")}
                  style={{ minWidth: 180 }}
                />
                {isAuthenticated ? (
                  <button
                    type="button"
                    className="btn btn-primary"
                    disabled={busy}
                    onClick={() => void placeBid(selected)}
                  >
                    {busy ? t("galaxy.bidding") : t("galaxy.placeBid")}
                  </button>
                ) : (
                  <Link href="/login" className="btn btn-primary">
                    {t("galaxy.signInToBid")}
                  </Link>
                )}
              </div>
            </div>
          )}

          <p style={{ color: "var(--text-muted)", marginTop: 28, maxWidth: 820, lineHeight: 1.7 }}>
            {t("galaxy.compliance")}
          </p>
        </section>
      </main>
    </div>
  );
}
