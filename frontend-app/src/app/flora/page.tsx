"use client";

import Image from "next/image";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { Navigation } from "@/components/Navigation";
import { useAuth } from "@/components/AuthProvider";
import { useLanguage } from "@/components/LanguageProvider";
import { floraAuction, getApiUrl } from "@/lib/api";

type FlowerForm =
  | "cut"
  | "bouquet"
  | "potted"
  | "seed"
  | "bulb"
  | "dried"
  | "arrangement"
  | "hybrid_literacy"
  | "other";

type Lot = {
  id: string;
  form: FlowerForm;
  name: string;
  variety: string;
  quantity?: number | null;
  blurb: string;
  starting_acp: string;
  current_acp: string;
  min_next_acp: string;
  bid_count: number;
  image_href?: string | null;
  featured?: boolean;
  contract_hash: string;
  listed_by_user?: boolean;
  settlement: string;
};

type Catalog = {
  title: string;
  tagline: string;
  compliance_note: string;
  hero_image_href?: string;
  lots: Lot[];
  featured: Lot[];
};

const FORM_FILTERS: Array<"all" | FlowerForm> = [
  "all",
  "cut",
  "bouquet",
  "potted",
  "seed",
  "bulb",
  "dried",
  "arrangement",
  "hybrid_literacy",
  "other",
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

function qtyLabel(qty: number | null | undefined, unlimited: string) {
  if (qty === null || qty === undefined) return unlimited;
  return String(qty);
}

export default function FloraAuctionPage() {
  const { t } = useLanguage();
  const { isAuthenticated } = useAuth();
  const [catalog, setCatalog] = useState<Catalog | null>(null);
  const [error, setError] = useState("");
  const [filter, setFilter] = useState<"all" | FlowerForm>("all");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [amount, setAmount] = useState("");
  const [busy, setBusy] = useState(false);
  const [info, setInfo] = useState("");
  const [sellName, setSellName] = useState("");
  const [sellVariety, setSellVariety] = useState("");
  const [sellForm, setSellForm] = useState<FlowerForm>("bouquet");
  const [sellQty, setSellQty] = useState("");
  const [sellPrice, setSellPrice] = useState("500");
  const [sellBlurb, setSellBlurb] = useState("");
  const [sellLicense, setSellLicense] = useState(false);

  const load = async () => {
    try {
      const data = (await floraAuction.catalog()) as Catalog;
      setCatalog(data);
      setError("");
    } catch (err) {
      try {
        const res = await fetch(`${getApiUrl()}/flora-auction/catalog`, { credentials: "omit" });
        if (!res.ok) throw new Error(`Catalog failed (${res.status})`);
        setCatalog((await res.json()) as Catalog);
        setError("");
      } catch (inner) {
        setError(inner instanceof Error ? inner.message : t("floraPage.loadError"));
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
    return items.filter((lot) => lot.form === filter);
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
      await floraAuction.bid(lot.id, { amount_acp: amount || lot.min_next_acp });
      setInfo(t("floraPage.bidPlaced"));
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : t("floraPage.bidError"));
    } finally {
      setBusy(false);
    }
  };

  const listLot = async () => {
    setBusy(true);
    setInfo("");
    setError("");
    try {
      const qtyRaw = sellQty.trim();
      const quantity = qtyRaw === "" ? null : Number(qtyRaw);
      const created = (await floraAuction.list({
        form: sellForm,
        name: sellName,
        variety: sellVariety,
        quantity,
        blurb: sellBlurb,
        starting_acp: sellPrice,
        license_acknowledged: sellLicense,
      })) as Lot;
      setInfo(t("floraPage.listed"));
      setSelectedId(created.id);
      setSellName("");
      setSellVariety("");
      setSellBlurb("");
      setSellQty("");
      setSellLicense(false);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : t("floraPage.listError"));
    } finally {
      setBusy(false);
    }
  };

  const formLabel = (kind: FlowerForm) => {
    if (kind === "cut") return t("floraPage.cut");
    if (kind === "bouquet") return t("floraPage.bouquet");
    if (kind === "potted") return t("floraPage.potted");
    if (kind === "seed") return t("floraPage.seed");
    if (kind === "bulb") return t("floraPage.bulb");
    if (kind === "dried") return t("floraPage.dried");
    if (kind === "arrangement") return t("floraPage.arrangement");
    if (kind === "hybrid_literacy") return t("floraPage.hybrid");
    return t("floraPage.other");
  };

  const heroSrc = catalog?.hero_image_href || "/flora/black-beauty.jpg";

  return (
    <div className="min-h-screen bg-[#0a1210] text-[#e8f5ef]">
      <Navigation />
      <main>
        <section className="relative overflow-hidden border-b border-emerald-500/20">
          <div className="absolute inset-0">
            <Image
              src={heroSrc}
              alt={t("floraPage.heroAlt")}
              fill
              priority
              className="object-cover object-center opacity-55"
              sizes="100vw"
            />
            <div
              className="absolute inset-0"
              style={{
                background:
                  "linear-gradient(105deg, rgba(6,16,12,0.92) 0%, rgba(6,16,12,0.72) 42%, rgba(6,16,12,0.35) 100%)",
              }}
            />
          </div>
          <div className="container relative" style={{ padding: "56px 24px 36px" }}>
            <span className="section-num">{t("floraPage.kicker")}</span>
            <h1 className="section-title" style={{ marginBottom: 12, maxWidth: 720 }}>
              {t("floraPage.title")}
            </h1>
            <p className="section-subtitle" style={{ maxWidth: 640, marginBottom: 14 }}>
              {t("floraPage.lead")}
            </p>
            <p style={{ color: "rgba(167, 243, 208, 0.85)", fontSize: "0.95rem", maxWidth: 520 }}>
              {t("floraPage.heroCaption")}
            </p>
          </div>
        </section>

        <section className="container" style={{ padding: "28px 24px 72px" }}>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 10, marginBottom: 22 }}>
            {FORM_FILTERS.map((key) => (
              <button
                key={key}
                type="button"
                className={filter === key ? "btn btn-primary" : "btn btn-ghost"}
                onClick={() => setFilter(key)}
              >
                {key === "all" ? t("floraPage.allLots") : formLabel(key)}
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
                  background: "rgba(16, 36, 28, 0.9)",
                  border: selectedId === lot.id ? "1px solid rgba(52, 211, 153, 0.55)" : undefined,
                  overflow: "hidden",
                }}
              >
                {lot.image_href ? (
                  <div style={{ position: "relative", width: "100%", height: 160, marginBottom: 12 }}>
                    <Image
                      src={lot.image_href}
                      alt={lot.name}
                      fill
                      className="object-cover"
                      sizes="(max-width: 768px) 100vw, 33vw"
                    />
                  </div>
                ) : null}
                <div className="card-header">
                  <span className="badge badge-info">{formLabel(lot.form)}</span>
                  <strong style={{ color: "#6ee7b7" }}>{formatAcp(lot.current_acp)}</strong>
                </div>
                <h2 style={{ fontSize: "1.2rem", fontWeight: 800, marginBottom: 6 }}>{lot.name}</h2>
                <p style={{ color: "var(--text-muted)", fontSize: "0.85rem", marginBottom: 10 }}>
                  {t("floraPage.variety")}: {lot.variety}
                  {" · "}
                  {t("floraPage.qty")}: {qtyLabel(lot.quantity, t("floraPage.qtyUnlimited"))}
                </p>
                <p style={{ color: "var(--text-muted)", lineHeight: 1.6, minHeight: 72 }}>{lot.blurb}</p>
                <p style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginBottom: 8, fontFamily: "monospace" }}>
                  {t("floraPage.contract")}: {shortHash(lot.contract_hash)}
                </p>
                <p style={{ fontSize: "0.85rem", color: "var(--text-muted)", marginBottom: 14 }}>
                  {t("floraPage.starting")}: {formatAcp(lot.starting_acp)} · {t("floraPage.bids")}: {lot.bid_count}
                </p>
                <button type="button" className="btn btn-ghost" onClick={() => setSelectedId(lot.id)}>
                  {t("floraPage.selectLot")}
                </button>
              </article>
            ))}
          </div>

          {selected && (
            <div className="card" style={{ marginTop: 28, borderRadius: 12, background: "rgba(16, 36, 28, 0.94)" }}>
              <h2 style={{ fontSize: "1.25rem", fontWeight: 800, marginBottom: 8 }}>
                {t("floraPage.bidOn")} {selected.name}
              </h2>
              <p style={{ color: "var(--text-muted)", marginBottom: 8 }}>
                {t("floraPage.minBid")}: {formatAcp(selected.min_next_acp)}
              </p>
              <p style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginBottom: 16, fontFamily: "monospace" }}>
                {t("floraPage.contract")}: {selected.contract_hash}
              </p>
              <div className="action-cluster">
                <input
                  className="input input-bordered"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  inputMode="decimal"
                  aria-label={t("floraPage.bidAmount")}
                  style={{ minWidth: 180 }}
                />
                {isAuthenticated ? (
                  <button
                    type="button"
                    className="btn btn-primary"
                    disabled={busy}
                    onClick={() => void placeBid(selected)}
                  >
                    {busy ? t("floraPage.bidding") : t("floraPage.placeBid")}
                  </button>
                ) : (
                  <Link href="/login" className="btn btn-primary">
                    {t("floraPage.signInToBid")}
                  </Link>
                )}
              </div>
            </div>
          )}

          <div className="card" style={{ marginTop: 28, borderRadius: 12, background: "rgba(16, 36, 28, 0.94)" }} id="sell">
            <h2 style={{ fontSize: "1.25rem", fontWeight: 800, marginBottom: 8 }}>{t("floraPage.sellTitle")}</h2>
            <p style={{ color: "var(--text-muted)", marginBottom: 16, maxWidth: 720 }}>{t("floraPage.sellLead")}</p>
            <div className="responsive-grid responsive-grid-2" style={{ marginBottom: 14 }}>
              <label>
                <span style={{ display: "block", fontSize: "0.8rem", marginBottom: 6 }}>{t("floraPage.sellName")}</span>
                <input className="input input-bordered" value={sellName} onChange={(e) => setSellName(e.target.value)} />
              </label>
              <label>
                <span style={{ display: "block", fontSize: "0.8rem", marginBottom: 6 }}>{t("floraPage.sellVariety")}</span>
                <input className="input input-bordered" value={sellVariety} onChange={(e) => setSellVariety(e.target.value)} />
              </label>
              <label>
                <span style={{ display: "block", fontSize: "0.8rem", marginBottom: 6 }}>{t("floraPage.sellForm")}</span>
                <select
                  className="input input-bordered"
                  value={sellForm}
                  onChange={(e) => setSellForm(e.target.value as FlowerForm)}
                >
                  {FORM_FILTERS.filter((key): key is FlowerForm => key !== "all").map((key) => (
                    <option key={key} value={key}>
                      {formLabel(key)}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                <span style={{ display: "block", fontSize: "0.8rem", marginBottom: 6 }}>{t("floraPage.sellQty")}</span>
                <input className="input input-bordered" value={sellQty} onChange={(e) => setSellQty(e.target.value)} inputMode="numeric" placeholder="âˆž" />
              </label>
              <label>
                <span style={{ display: "block", fontSize: "0.8rem", marginBottom: 6 }}>{t("floraPage.sellPrice")}</span>
                <input className="input input-bordered" value={sellPrice} onChange={(e) => setSellPrice(e.target.value)} inputMode="decimal" />
              </label>
            </div>
            <label style={{ display: "block", marginBottom: 14 }}>
              <span style={{ display: "block", fontSize: "0.8rem", marginBottom: 6 }}>{t("floraPage.sellBlurb")}</span>
              <textarea className="input input-bordered" rows={3} value={sellBlurb} onChange={(e) => setSellBlurb(e.target.value)} />
            </label>
            <label style={{ display: "flex", gap: 10, alignItems: "flex-start", marginBottom: 16, fontSize: "0.9rem" }}>
              <input type="checkbox" checked={sellLicense} onChange={(e) => setSellLicense(e.target.checked)} />
              <span>{t("floraPage.sellLicense")}</span>
            </label>
            {isAuthenticated ? (
              <button type="button" className="btn btn-primary" disabled={busy} onClick={() => void listLot()}>
                {busy ? t("floraPage.selling") : t("floraPage.sellCta")}
              </button>
            ) : (
              <Link href="/login" className="btn btn-primary">
                {t("floraPage.signInToSell")}
              </Link>
            )}
          </div>

          <p style={{ color: "var(--text-muted)", marginTop: 28, maxWidth: 820, lineHeight: 1.7 }}>
            {t("floraPage.compliance")}
          </p>
        </section>
      </main>
    </div>
  );
}
