"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { Navigation } from "@/components/Navigation";
import { useAuth } from "@/components/AuthProvider";
import { useLanguage } from "@/components/LanguageProvider";
import { animalAuction, getApiUrl } from "@/lib/api";

type Species = "dog" | "cat" | "horse" | "bird" | "rabbit" | "fish" | "other_companion";

type Lot = {
  id: string;
  species: Species;
  name: string;
  breed: string;
  age_months?: number | null;
  blurb: string;
  starting_acp: string;
  current_acp: string;
  min_next_acp: string;
  bid_count: number;
  featured?: boolean;
  contract_hash: string;
  listed_by_user?: boolean;
  settlement: string;
};

type Catalog = {
  title: string;
  tagline: string;
  compliance_note: string;
  lots: Lot[];
  featured: Lot[];
};

const SPECIES_FILTERS: Array<"all" | Species> = [
  "all",
  "dog",
  "cat",
  "horse",
  "bird",
  "rabbit",
  "fish",
  "other_companion",
];

function formatAcp(value: string) {
  const n = Number(value);
  if (!Number.isFinite(n)) return `${value} ACP`;
  return `${n.toLocaleString()} ACP`;
}

function shortHash(value: string) {
  if (value.length < 18) return value;
  return `${value.slice(0, 10)}…${value.slice(-8)}`;
}

export default function FaunaAuctionPage() {
  const { t } = useLanguage();
  const { isAuthenticated } = useAuth();
  const [catalog, setCatalog] = useState<Catalog | null>(null);
  const [error, setError] = useState("");
  const [filter, setFilter] = useState<"all" | Species>("all");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [amount, setAmount] = useState("");
  const [busy, setBusy] = useState(false);
  const [info, setInfo] = useState("");
  const [sellName, setSellName] = useState("");
  const [sellBreed, setSellBreed] = useState("");
  const [sellSpecies, setSellSpecies] = useState<Species>("dog");
  const [sellAge, setSellAge] = useState("12");
  const [sellPrice, setSellPrice] = useState("2500");
  const [sellBlurb, setSellBlurb] = useState("");
  const [sellLicense, setSellLicense] = useState(false);

  const load = async () => {
    try {
      const data = (await animalAuction.catalog()) as Catalog;
      setCatalog(data);
      setError("");
    } catch (err) {
      try {
        const res = await fetch(`${getApiUrl()}/animal-auction/catalog`, { credentials: "omit" });
        if (!res.ok) throw new Error(`Catalog failed (${res.status})`);
        setCatalog((await res.json()) as Catalog);
        setError("");
      } catch (inner) {
        setError(inner instanceof Error ? inner.message : t("faunaPage.loadError"));
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
    return items.filter((lot) => lot.species === filter);
  }, [catalog, filter]);

  const selected = lots.find((lot) => lot.id === selectedId) || catalog?.lots.find((lot) => lot.id === selectedId);

  const selectedMinimum = selected?.min_next_acp;
  useEffect(() => {
    if (selectedMinimum !== undefined) setAmount(selectedMinimum);
  }, [selectedId, selectedMinimum]);

  const placeBid = async (lot: Lot) => {
    setBusy(true);
    setInfo("");
    setError("");
    try {
      await animalAuction.bid(lot.id, { amount_acp: amount || lot.min_next_acp });
      setInfo(t("faunaPage.bidPlaced"));
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : t("faunaPage.bidError"));
    } finally {
      setBusy(false);
    }
  };

  const listLot = async () => {
    setBusy(true);
    setInfo("");
    setError("");
    try {
      const created = (await animalAuction.list({
        species: sellSpecies,
        name: sellName,
        breed: sellBreed,
        age_months: sellAge ? Number(sellAge) : null,
        blurb: sellBlurb,
        starting_acp: sellPrice,
        license_acknowledged: sellLicense,
      })) as Lot;
      setInfo(t("faunaPage.listed"));
      setSelectedId(created.id);
      setSellName("");
      setSellBreed("");
      setSellBlurb("");
      setSellLicense(false);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : t("faunaPage.listError"));
    } finally {
      setBusy(false);
    }
  };

  const kindLabel = (kind: Species) => {
    if (kind === "dog") return t("faunaPage.dogs");
    if (kind === "cat") return t("faunaPage.cats");
    if (kind === "horse") return t("faunaPage.horses");
    if (kind === "bird") return t("faunaPage.birds");
    if (kind === "rabbit") return t("faunaPage.rabbits");
    if (kind === "fish") return t("faunaPage.fish");
    return t("faunaPage.other");
  };

  return (
    <div className="min-h-screen bg-[#120c08] text-[#f4ece3]">
      <Navigation />
      <main>
        <section className="relative overflow-hidden border-b border-amber-500/15 bg-[radial-gradient(ellipse_at_20%_0%,rgba(245,158,11,0.18),transparent_55%)]">
          <div className="container" style={{ padding: "48px 24px 28px" }}>
            <span className="section-num">{t("faunaPage.kicker")}</span>
            <h1 className="section-title" style={{ marginBottom: 12 }}>
              {t("faunaPage.title")}
            </h1>
            <p className="section-subtitle" style={{ maxWidth: 720, marginBottom: 0 }}>
              {t("faunaPage.lead")}
            </p>
          </div>
        </section>

        <section className="container" style={{ padding: "28px 24px 72px" }}>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 10, marginBottom: 22 }}>
            {SPECIES_FILTERS.map((key) => (
              <button
                key={key}
                type="button"
                className={filter === key ? "btn btn-primary" : "btn btn-ghost"}
                onClick={() => setFilter(key)}
              >
                {key === "all" ? t("faunaPage.allLots") : kindLabel(key)}
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
                  background: "rgba(42, 28, 16, 0.88)",
                  border: selectedId === lot.id ? "1px solid rgba(251, 191, 36, 0.55)" : undefined,
                }}
              >
                <div className="card-header">
                  <span className="badge badge-info">{kindLabel(lot.species)}</span>
                  <strong style={{ color: "#fbbf24" }}>{formatAcp(lot.current_acp)}</strong>
                </div>
                <h2 style={{ fontSize: "1.2rem", fontWeight: 800, marginBottom: 6 }}>{lot.name}</h2>
                <p style={{ color: "var(--text-muted)", fontSize: "0.85rem", marginBottom: 10 }}>
                  {t("faunaPage.breed")}: {lot.breed}
                  {lot.age_months ? ` · ${lot.age_months} ${t("faunaPage.months")}` : ""}
                </p>
                <p style={{ color: "var(--text-muted)", lineHeight: 1.6, minHeight: 72 }}>{lot.blurb}</p>
                <p style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginBottom: 8, fontFamily: "monospace" }}>
                  {t("faunaPage.contract")}: {shortHash(lot.contract_hash)}
                </p>
                <p style={{ fontSize: "0.85rem", color: "var(--text-muted)", marginBottom: 14 }}>
                  {t("faunaPage.starting")}: {formatAcp(lot.starting_acp)} · {t("faunaPage.bids")}: {lot.bid_count}
                </p>
                <button type="button" className="btn btn-ghost" onClick={() => setSelectedId(lot.id)}>
                  {t("faunaPage.selectLot")}
                </button>
              </article>
            ))}
          </div>

          {selected && (
            <div className="card" style={{ marginTop: 28, borderRadius: 12, background: "rgba(42, 28, 16, 0.92)" }}>
              <h2 style={{ fontSize: "1.25rem", fontWeight: 800, marginBottom: 8 }}>
                {t("faunaPage.bidOn")} {selected.name}
              </h2>
              <p style={{ color: "var(--text-muted)", marginBottom: 8 }}>
                {t("faunaPage.minBid")}: {formatAcp(selected.min_next_acp)}
              </p>
              <p style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginBottom: 16, fontFamily: "monospace" }}>
                {t("faunaPage.contract")}: {selected.contract_hash}
              </p>
              <div className="action-cluster">
                <input
                  className="input input-bordered"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  inputMode="decimal"
                  aria-label={t("faunaPage.bidAmount")}
                  style={{ minWidth: 180 }}
                />
                {isAuthenticated ? (
                  <button
                    type="button"
                    className="btn btn-primary"
                    disabled={busy}
                    onClick={() => void placeBid(selected)}
                  >
                    {busy ? t("faunaPage.bidding") : t("faunaPage.placeBid")}
                  </button>
                ) : (
                  <Link href="/login" className="btn btn-primary">
                    {t("faunaPage.signInToBid")}
                  </Link>
                )}
              </div>
            </div>
          )}

          <div className="card" style={{ marginTop: 28, borderRadius: 12, background: "rgba(42, 28, 16, 0.92)" }} id="sell">
            <h2 style={{ fontSize: "1.25rem", fontWeight: 800, marginBottom: 8 }}>{t("faunaPage.sellTitle")}</h2>
            <p style={{ color: "var(--text-muted)", marginBottom: 16, maxWidth: 720 }}>{t("faunaPage.sellLead")}</p>
            <div className="responsive-grid responsive-grid-2" style={{ marginBottom: 14 }}>
              <label>
                <span style={{ display: "block", fontSize: "0.8rem", marginBottom: 6 }}>{t("faunaPage.sellName")}</span>
                <input className="input input-bordered" value={sellName} onChange={(e) => setSellName(e.target.value)} />
              </label>
              <label>
                <span style={{ display: "block", fontSize: "0.8rem", marginBottom: 6 }}>{t("faunaPage.sellBreed")}</span>
                <input className="input input-bordered" value={sellBreed} onChange={(e) => setSellBreed(e.target.value)} />
              </label>
              <label>
                <span style={{ display: "block", fontSize: "0.8rem", marginBottom: 6 }}>{t("faunaPage.sellSpecies")}</span>
                <select
                  className="input input-bordered"
                  value={sellSpecies}
                  onChange={(e) => setSellSpecies(e.target.value as Species)}
                >
                  {SPECIES_FILTERS.filter((key): key is Species => key !== "all").map((key) => (
                    <option key={key} value={key}>
                      {kindLabel(key)}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                <span style={{ display: "block", fontSize: "0.8rem", marginBottom: 6 }}>{t("faunaPage.sellAge")}</span>
                <input className="input input-bordered" value={sellAge} onChange={(e) => setSellAge(e.target.value)} inputMode="numeric" />
              </label>
              <label>
                <span style={{ display: "block", fontSize: "0.8rem", marginBottom: 6 }}>{t("faunaPage.sellPrice")}</span>
                <input className="input input-bordered" value={sellPrice} onChange={(e) => setSellPrice(e.target.value)} inputMode="decimal" />
              </label>
            </div>
            <label style={{ display: "block", marginBottom: 14 }}>
              <span style={{ display: "block", fontSize: "0.8rem", marginBottom: 6 }}>{t("faunaPage.sellBlurb")}</span>
              <textarea className="input input-bordered" rows={3} value={sellBlurb} onChange={(e) => setSellBlurb(e.target.value)} />
            </label>
            <label style={{ display: "flex", gap: 10, alignItems: "flex-start", marginBottom: 16, fontSize: "0.9rem" }}>
              <input type="checkbox" checked={sellLicense} onChange={(e) => setSellLicense(e.target.checked)} />
              <span>{t("faunaPage.sellLicense")}</span>
            </label>
            {isAuthenticated ? (
              <button type="button" className="btn btn-primary" disabled={busy} onClick={() => void listLot()}>
                {busy ? t("faunaPage.selling") : t("faunaPage.sellCta")}
              </button>
            ) : (
              <Link href="/login" className="btn btn-primary">
                {t("faunaPage.signInToSell")}
              </Link>
            )}
          </div>

          <p style={{ color: "var(--text-muted)", marginTop: 28, maxWidth: 820, lineHeight: 1.7 }}>
            {t("faunaPage.compliance")}
          </p>
        </section>
      </main>
    </div>
  );
}
