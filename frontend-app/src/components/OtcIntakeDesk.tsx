"use client";

import { useEffect, useState, type FormEvent } from "react";
import { useLanguage } from "@/components/LanguageProvider";
import { walletAcp } from "@/lib/api";

type OtcCatalog = {
  metals: Array<{ kind: string; label: string; indicative_acp_per_gram: string; note: string }>;
  goods: Array<{ category: string; label: string; note: string }>;
  commodities?: Array<{ kind: string; label: string; unit: string; indicative_acp_per_unit: string; note: string }>;
  real_estate?: Array<{ deal_type: string; label: string; note: string }>;
  space_objects?: Array<{ object_class: string; label: string; note: string; indicative_starting_acp?: string }>;
  ip_assets?: Array<{ kind: string; label: string; note: string; ownership_asset_class: string }>;
  handoff_instructions: string;
  compliance_note: string;
};

type OtcOrder = {
  id: string;
  rail: "metal" | "goods" | "commodity" | "real_estate" | "space" | "ip";
  status: string;
  asset_label: string;
  estimated_acp_amount: string;
  payout_acp_address: string;
  intake_reference: string;
  handoff_instructions: string;
  proof_ref?: string | null;
  note?: string | null;
};

type Props = {
  defaultPayoutAddress?: string;
};

export function OtcIntakeDesk({ defaultPayoutAddress = "" }: Props) {
  const { t } = useLanguage();
  const [tab, setTab] = useState<"metal" | "goods" | "commodity" | "real_estate" | "space" | "ip">("metal");
  const [catalog, setCatalog] = useState<OtcCatalog | null>(null);
  const [orders, setOrders] = useState<OtcOrder[]>([]);
  const [selectedId, setSelectedId] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [info, setInfo] = useState("");
  const [quote, setQuote] = useState<{ estimated_acp_amount: string; rate_note: string } | null>(null);

  const [metalForm, setMetalForm] = useState({
    metal: "gold",
    weight_grams: "10",
    purity_ppt: "999",
    payout_acp_address: defaultPayoutAddress,
    note: "",
  });
  const [goodsForm, setGoodsForm] = useState({
    goods_category: "electronics",
    goods_title: "",
    goods_description: "",
    estimated_value_acp: "1000",
    payout_acp_address: defaultPayoutAddress,
    note: "",
  });
  const [commodityForm, setCommodityForm] = useState({
    commodity: "oil",
    quantity: "100",
    grade_note: "",
    payout_acp_address: defaultPayoutAddress,
    note: "",
  });
  const [reForm, setReForm] = useState({
    re_deal_type: "sale",
    re_address_or_parcel: "",
    re_jurisdiction: "",
    re_lease_months: "12",
    estimated_value_acp: "100000",
    document_hash: "",
    payout_acp_address: defaultPayoutAddress,
    note: "",
  });
  const [spaceForm, setSpaceForm] = useState({
    space_object_class: "satellite",
    space_object_id: "",
    space_jurisdiction: "",
    estimated_value_acp: "250000",
    document_hash: "",
    payout_acp_address: defaultPayoutAddress,
    note: "",
  });
  const [ipForm, setIpForm] = useState({
    ip_kind: "patent",
    ip_title: "",
    ip_registration_uri: "",
    ip_jurisdiction: "",
    estimated_value_acp: "25000",
    document_hash: "",
    payout_acp_address: defaultPayoutAddress,
    note: "",
  });
  const [proofRef, setProofRef] = useState("");

  useEffect(() => {
    if (defaultPayoutAddress) {
      setMetalForm((p) => ({ ...p, payout_acp_address: p.payout_acp_address || defaultPayoutAddress }));
      setGoodsForm((p) => ({ ...p, payout_acp_address: p.payout_acp_address || defaultPayoutAddress }));
      setCommodityForm((p) => ({ ...p, payout_acp_address: p.payout_acp_address || defaultPayoutAddress }));
    }
  }, [defaultPayoutAddress]);

  const loadFailedMessage = t("otcIntake.loadFailed");
  useEffect(() => {
    void (async () => {
      try {
        const [cat, list] = await Promise.all([
          walletAcp.otcCatalog() as Promise<OtcCatalog>,
          walletAcp.listOtcOrders() as Promise<OtcOrder[]>,
        ]);
        setCatalog(cat);
        setOrders(Array.isArray(list) ? list : []);
        if (list?.[0]?.id) setSelectedId(list[0].id);
      } catch (err) {
        setError(err instanceof Error ? err.message : loadFailedMessage);
      }
    })();
  }, [loadFailedMessage]);

  const selected = orders.find((o) => o.id === selectedId) || orders[0] || null;

  async function refreshOrders() {
    const list = (await walletAcp.listOtcOrders()) as OtcOrder[];
    setOrders(Array.isArray(list) ? list : []);
  }

  async function previewQuote() {
    setBusy(true);
    setError("");
    try {
      let q: { estimated_acp_amount: string; rate_note: string };
      if (tab === "metal") {
        q = (await walletAcp.otcQuoteMetal({
          metal: metalForm.metal,
          weight_grams: metalForm.weight_grams,
          purity_ppt: Number(metalForm.purity_ppt) || 999,
        })) as { estimated_acp_amount: string; rate_note: string };
      } else if (tab === "commodity") {
        q = (await walletAcp.otcQuoteCommodity({
          commodity: commodityForm.commodity,
          quantity: commodityForm.quantity,
          grade_note: commodityForm.grade_note || undefined,
        })) as { estimated_acp_amount: string; rate_note: string };
      } else if (tab === "real_estate") {
        q = (await walletAcp.otcQuoteRealEstate({
          deal_type: reForm.re_deal_type,
          estimated_value_acp: reForm.estimated_value_acp,
          jurisdiction: reForm.re_jurisdiction || undefined,
          lease_months: reForm.re_deal_type === "rental" ? Number(reForm.re_lease_months) || 12 : undefined,
        })) as { estimated_acp_amount: string; rate_note: string };
      } else if (tab === "space") {
        q = (await walletAcp.otcQuoteSpace({
          object_class: spaceForm.space_object_class,
          estimated_value_acp: spaceForm.estimated_value_acp,
          norad_or_cospar_id: spaceForm.space_object_id || undefined,
        })) as { estimated_acp_amount: string; rate_note: string };
      } else if (tab === "ip") {
        q = (await walletAcp.otcQuoteIp({
          kind: ipForm.ip_kind,
          estimated_value_acp: ipForm.estimated_value_acp,
          registration_uri: ipForm.ip_registration_uri || undefined,
        })) as { estimated_acp_amount: string; rate_note: string };
      } else {
        q = (await walletAcp.otcQuoteGoods({
          category: goodsForm.goods_category,
          estimated_value_acp: goodsForm.estimated_value_acp,
        })) as { estimated_acp_amount: string; rate_note: string };
      }
      setQuote(q);
    } catch (err) {
      setError(err instanceof Error ? err.message : t("otcIntake.quoteFailed"));
    } finally {
      setBusy(false);
    }
  }

  async function createOrder(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError("");
    setInfo("");
    try {
      let created: OtcOrder;
      if (tab === "metal") {
        created = (await walletAcp.createOtcOrder({
          rail: "metal",
          metal: metalForm.metal,
          weight_grams: metalForm.weight_grams,
          purity_ppt: Number(metalForm.purity_ppt) || 999,
          payout_acp_address: metalForm.payout_acp_address.trim(),
          note: metalForm.note || undefined,
        })) as OtcOrder;
      } else if (tab === "commodity") {
        created = (await walletAcp.createOtcOrder({
          rail: "commodity",
          commodity: commodityForm.commodity,
          quantity: commodityForm.quantity,
          grade_note: commodityForm.grade_note || undefined,
          payout_acp_address: commodityForm.payout_acp_address.trim(),
          note: commodityForm.note || undefined,
        })) as OtcOrder;
      } else if (tab === "real_estate") {
        created = (await walletAcp.createOtcOrder({
          rail: "real_estate",
          re_deal_type: reForm.re_deal_type,
          re_address_or_parcel: reForm.re_address_or_parcel.trim(),
          re_jurisdiction: reForm.re_jurisdiction.trim() || undefined,
          re_lease_months: reForm.re_deal_type === "rental" ? Number(reForm.re_lease_months) || 12 : undefined,
          estimated_value_acp: reForm.estimated_value_acp,
          document_hash: reForm.document_hash.trim() || undefined,
          payout_acp_address: reForm.payout_acp_address.trim(),
          note: reForm.note || undefined,
        })) as OtcOrder;
      } else if (tab === "space") {
        created = (await walletAcp.createOtcOrder({
          rail: "space",
          space_object_class: spaceForm.space_object_class,
          space_object_id: spaceForm.space_object_id.trim() || undefined,
          space_jurisdiction: spaceForm.space_jurisdiction.trim() || undefined,
          estimated_value_acp: spaceForm.estimated_value_acp,
          document_hash: spaceForm.document_hash.trim() || undefined,
          payout_acp_address: spaceForm.payout_acp_address.trim(),
          note: spaceForm.note || undefined,
        })) as OtcOrder;
      } else if (tab === "ip") {
        created = (await walletAcp.createOtcOrder({
          rail: "ip",
          ip_kind: ipForm.ip_kind,
          ip_title: ipForm.ip_title.trim(),
          ip_registration_uri: ipForm.ip_registration_uri.trim() || undefined,
          ip_jurisdiction: ipForm.ip_jurisdiction.trim() || undefined,
          estimated_value_acp: ipForm.estimated_value_acp,
          document_hash: ipForm.document_hash.trim(),
          payout_acp_address: ipForm.payout_acp_address.trim(),
          note: ipForm.note || undefined,
        })) as OtcOrder;
      } else {
        created = (await walletAcp.createOtcOrder({
          rail: "goods",
          goods_category: goodsForm.goods_category,
          goods_title: goodsForm.goods_title.trim(),
          goods_description: goodsForm.goods_description.trim() || undefined,
          estimated_value_acp: goodsForm.estimated_value_acp,
          payout_acp_address: goodsForm.payout_acp_address.trim(),
          note: goodsForm.note || undefined,
        })) as OtcOrder;
      }
      setInfo(t("otcIntake.orderCreated").replace("{ref}", created.intake_reference));
      setSelectedId(created.id);
      await refreshOrders();
    } catch (err) {
      setError(err instanceof Error ? err.message : t("otcIntake.createFailed"));
    } finally {
      setBusy(false);
    }
  }

  async function confirmSelected() {
    if (!selected) return;
    setBusy(true);
    setError("");
    try {
      await walletAcp.confirmOtcOrder(selected.id, {
        proof_ref: proofRef.trim() || undefined,
      });
      setInfo(t("otcIntake.markedForReview"));
      setProofRef("");
      await refreshOrders();
    } catch (err) {
      setError(err instanceof Error ? err.message : t("otcIntake.confirmFailed"));
    } finally {
      setBusy(false);
    }
  }

  async function cancelSelected() {
    if (!selected) return;
    setBusy(true);
    setError("");
    try {
      await walletAcp.cancelOtcOrder(selected.id);
      setInfo(t("otcIntake.orderCancelled"));
      await refreshOrders();
    } catch (err) {
      setError(err instanceof Error ? err.message : t("otcIntake.cancelFailed"));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="responsive-grid responsive-grid-2" id="otc-intake">
      <div className="card">
        <div className="card-header">
          <h3 style={{ fontWeight: 800, margin: 0 }}>{t("otcIntake.title")}</h3>
          <span className="badge badge-info">{t("otcIntake.badge")}</span>
        </div>
        <p style={{ marginTop: 10, color: "var(--text-muted)", fontSize: "0.9rem", lineHeight: 1.6 }}>
          {t("otcIntake.lead")}
        </p>

        <div style={{ display: "flex", gap: 8, marginTop: 12, flexWrap: "wrap" }}>
          <button
            type="button"
            className="btn btn-ghost"
            onClick={() => {
              setTab("metal");
              setQuote(null);
            }}
            style={{
              borderColor: tab === "metal" ? "rgba(16,185,129,0.5)" : undefined,
              color: tab === "metal" ? "#34d399" : undefined,
            }}
          >
            {t("otcIntake.tabMetals")}
          </button>
          <button
            type="button"
            className="btn btn-ghost"
            onClick={() => {
              setTab("goods");
              setQuote(null);
            }}
            style={{
              borderColor: tab === "goods" ? "rgba(16,185,129,0.5)" : undefined,
              color: tab === "goods" ? "#34d399" : undefined,
            }}
          >
            {t("otcIntake.tabGoods")}
          </button>
          <button
            type="button"
            className="btn btn-ghost"
            onClick={() => {
              setTab("commodity");
              setQuote(null);
            }}
            style={{
              borderColor: tab === "commodity" ? "rgba(16,185,129,0.5)" : undefined,
              color: tab === "commodity" ? "#34d399" : undefined,
            }}
          >
            {t("otcIntake.tabCommodity")}
          </button>
          <button
            type="button"
            className="btn btn-ghost"
            onClick={() => {
              setTab("real_estate");
              setQuote(null);
            }}
            style={{
              borderColor: tab === "real_estate" ? "rgba(16,185,129,0.5)" : undefined,
              color: tab === "real_estate" ? "#34d399" : undefined,
            }}
          >
            {t("otcIntake.tabRealEstate")}
          </button>
          <button
            type="button"
            className="btn btn-ghost"
            onClick={() => {
              setTab("space");
              setQuote(null);
            }}
            style={{
              borderColor: tab === "space" ? "rgba(16,185,129,0.5)" : undefined,
              color: tab === "space" ? "#34d399" : undefined,
            }}
          >
            {t("otcIntake.tabSpace")}
          </button>
          <button
            type="button"
            className="btn btn-ghost"
            onClick={() => {
              setTab("ip");
              setQuote(null);
            }}
            style={{
              borderColor: tab === "ip" ? "rgba(16,185,129,0.5)" : undefined,
              color: tab === "ip" ? "#34d399" : undefined,
            }}
          >
            {t("otcIntake.tabIp")}
          </button>
        </div>

        {error && (
          <div style={{ marginTop: 12, padding: 10, borderRadius: 8, background: "rgba(239,68,68,0.1)", color: "#ef4444", fontSize: "0.9rem" }}>
            {error}
          </div>
        )}
        {info && (
          <div style={{ marginTop: 12, padding: 10, borderRadius: 8, background: "rgba(16,185,129,0.1)", color: "#10b981", fontSize: "0.9rem" }}>
            {info}
          </div>
        )}

        <form onSubmit={createOrder} style={{ marginTop: 14, display: "grid", gap: 10 }}>
          {tab === "metal" ? (
            <>
              <label style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>{t("otcIntake.metal")}</label>
              <select
                className="input input-bordered w-full"
                value={metalForm.metal}
                onChange={(e) => setMetalForm((p) => ({ ...p, metal: e.target.value }))}
              >
                {(catalog?.metals || [
                  { kind: "gold", label: "Gold (Au)" },
                  { kind: "silver", label: "Silver (Ag)" },
                  { kind: "platinum", label: "Platinum (Pt)" },
                  { kind: "palladium", label: "Palladium (Pd)" },
                ]).map((m) => (
                  <option key={m.kind} value={m.kind}>
                    {m.label}
                    {"indicative_acp_per_gram" in m && m.indicative_acp_per_gram
                      ? t("otcIntake.perGram").replace("{rate}", m.indicative_acp_per_gram)
                      : ""}
                  </option>
                ))}
              </select>
              <label style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>{t("otcIntake.weightGrams")}</label>
              <input
                className="input input-bordered w-full"
                inputMode="decimal"
                value={metalForm.weight_grams}
                onChange={(e) => setMetalForm((p) => ({ ...p, weight_grams: e.target.value }))}
                required
              />
              <label style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>{t("otcIntake.purityPpt")}</label>
              <input
                className="input input-bordered w-full"
                inputMode="numeric"
                value={metalForm.purity_ppt}
                onChange={(e) => setMetalForm((p) => ({ ...p, purity_ppt: e.target.value }))}
                required
              />
              <label style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>{t("otcIntake.payoutAddress")}</label>
              <input
                className="input input-bordered w-full"
                value={metalForm.payout_acp_address}
                onChange={(e) => setMetalForm((p) => ({ ...p, payout_acp_address: e.target.value.trim() }))}
                required
              />
              <label style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>{t("otcIntake.noteOptional")}</label>
              <input
                className="input input-bordered w-full"
                value={metalForm.note}
                onChange={(e) => setMetalForm((p) => ({ ...p, note: e.target.value }))}
              />
            </>
          ) : tab === "commodity" ? (
            <>
              <label style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>{t("otcIntake.commodity")}</label>
              <select
                className="input input-bordered w-full"
                value={commodityForm.commodity}
                onChange={(e) => setCommodityForm((p) => ({ ...p, commodity: e.target.value }))}
              >
                {(catalog?.commodities || [
                  { kind: "oil", label: "Crude oil", unit: "bbl", indicative_acp_per_unit: "80" },
                  { kind: "natural_gas", label: "Natural gas", unit: "m3", indicative_acp_per_unit: "0.45" },
                  { kind: "timber", label: "Timber / forest", unit: "m3", indicative_acp_per_unit: "95" },
                  { kind: "sand", label: "Sand", unit: "t", indicative_acp_per_unit: "18" },
                  { kind: "stone", label: "Stone / rock", unit: "t", indicative_acp_per_unit: "28" },
                  { kind: "uranium", label: "Uranium", unit: "kg", indicative_acp_per_unit: "220" },
                ]).map((c) => (
                  <option key={c.kind} value={c.kind}>
                    {c.label}{t("otcIntake.perUnit").replace("{rate}", c.indicative_acp_per_unit).replace("{unit}", c.unit)}
                  </option>
                ))}
              </select>
              <label style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>
                {t("otcIntake.quantity")} (
                {(catalog?.commodities || []).find((c) => c.kind === commodityForm.commodity)?.unit || t("otcIntake.unitFallback")}
                )
              </label>
              <input
                className="input input-bordered w-full"
                inputMode="decimal"
                value={commodityForm.quantity}
                onChange={(e) => setCommodityForm((p) => ({ ...p, quantity: e.target.value }))}
                required
              />
              <label style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>{t("otcIntake.gradeSpec")}</label>
              <input
                className="input input-bordered w-full"
                value={commodityForm.grade_note}
                onChange={(e) => setCommodityForm((p) => ({ ...p, grade_note: e.target.value }))}
                placeholder={t("otcIntake.gradePlaceholder")}
              />
              <label style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>{t("otcIntake.payoutAddress")}</label>
              <input
                className="input input-bordered w-full"
                value={commodityForm.payout_acp_address}
                onChange={(e) => setCommodityForm((p) => ({ ...p, payout_acp_address: e.target.value.trim() }))}
                required
              />
              <label style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>{t("otcIntake.noteOptional")}</label>
              <input
                className="input input-bordered w-full"
                value={commodityForm.note}
                onChange={(e) => setCommodityForm((p) => ({ ...p, note: e.target.value }))}
              />
            </>
          ) : tab === "real_estate" ? (
            <>
              <label style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>{t("otcIntake.dealType")}</label>
              <select
                className="input input-bordered w-full"
                value={reForm.re_deal_type}
                onChange={(e) => setReForm((p) => ({ ...p, re_deal_type: e.target.value }))}
              >
                {(catalog?.real_estate || [{ deal_type: "sale", label: "Sale" }, { deal_type: "rental", label: "Rental" }]).map((r) => (
                  <option key={r.deal_type} value={r.deal_type}>{r.label}</option>
                ))}
              </select>
              <label style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>{t("otcIntake.addressParcel")}</label>
              <input className="input input-bordered w-full" value={reForm.re_address_or_parcel} onChange={(e) => setReForm((p) => ({ ...p, re_address_or_parcel: e.target.value }))} required />
              <label style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>{t("otcIntake.jurisdiction")}</label>
              <input className="input input-bordered w-full" value={reForm.re_jurisdiction} onChange={(e) => setReForm((p) => ({ ...p, re_jurisdiction: e.target.value }))} />
              {reForm.re_deal_type === "rental" ? (
                <>
                  <label style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>{t("otcIntake.leaseMonths")}</label>
                  <input className="input input-bordered w-full" value={reForm.re_lease_months} onChange={(e) => setReForm((p) => ({ ...p, re_lease_months: e.target.value }))} />
                </>
              ) : null}
              <label style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>{t("otcIntake.estimatedAcp")}</label>
              <input className="input input-bordered w-full" value={reForm.estimated_value_acp} onChange={(e) => setReForm((p) => ({ ...p, estimated_value_acp: e.target.value }))} />
              <label style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>{t("otcIntake.documentHashOptional")}</label>
              <input className="input input-bordered w-full" value={reForm.document_hash} onChange={(e) => setReForm((p) => ({ ...p, document_hash: e.target.value }))} />
              <label style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>{t("otcIntake.payoutAddress")}</label>
              <input className="input input-bordered w-full" value={reForm.payout_acp_address} onChange={(e) => setReForm((p) => ({ ...p, payout_acp_address: e.target.value.trim() }))} required />
              <label style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>{t("otcIntake.note")}</label>
              <input className="input input-bordered w-full" value={reForm.note} onChange={(e) => setReForm((p) => ({ ...p, note: e.target.value }))} />
            </>
          ) : tab === "space" ? (
            <>
              <label style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>{t("otcIntake.objectClass")}</label>
              <select
                className="input input-bordered w-full"
                value={spaceForm.space_object_class}
                onChange={(e) => {
                  const next = e.target.value;
                  const hint = (catalog?.space_objects || []).find((s) => s.object_class === next)?.indicative_starting_acp;
                  setSpaceForm((p) => ({
                    ...p,
                    space_object_class: next,
                    estimated_value_acp: hint || p.estimated_value_acp,
                  }));
                }}
              >
                {(catalog?.space_objects || [{ object_class: "satellite", label: "Satellite", indicative_starting_acp: "250000" }]).map((s) => (
                  <option key={s.object_class} value={s.object_class}>
                    {s.label}
                    {s.indicative_starting_acp ? ` — ${s.indicative_starting_acp} ACP` : ""}
                  </option>
                ))}
              </select>
              <label style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>{t("otcIntake.noradCospar")}</label>
              <input className="input input-bordered w-full" value={spaceForm.space_object_id} onChange={(e) => setSpaceForm((p) => ({ ...p, space_object_id: e.target.value }))} />
              <label style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>{t("otcIntake.jurisdiction")}</label>
              <input className="input input-bordered w-full" value={spaceForm.space_jurisdiction} onChange={(e) => setSpaceForm((p) => ({ ...p, space_jurisdiction: e.target.value }))} />
              <label style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>
                {t("otcIntake.estimatedAcp")}
                {catalog?.space_objects?.find((s) => s.object_class === spaceForm.space_object_class)?.indicative_starting_acp
                  ? t("otcIntake.auctionStartHint").replace("{amount}", catalog.space_objects.find((s) => s.object_class === spaceForm.space_object_class)?.indicative_starting_acp || "")
                  : ""}
              </label>
              <input className="input input-bordered w-full" value={spaceForm.estimated_value_acp} onChange={(e) => setSpaceForm((p) => ({ ...p, estimated_value_acp: e.target.value }))} />
              <label style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>{t("otcIntake.documentHashOptional")}</label>
              <input className="input input-bordered w-full" value={spaceForm.document_hash} onChange={(e) => setSpaceForm((p) => ({ ...p, document_hash: e.target.value }))} />
              <label style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>{t("otcIntake.payoutAddress")}</label>
              <input className="input input-bordered w-full" value={spaceForm.payout_acp_address} onChange={(e) => setSpaceForm((p) => ({ ...p, payout_acp_address: e.target.value.trim() }))} required />
              <label style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>{t("otcIntake.note")}</label>
              <input className="input input-bordered w-full" value={spaceForm.note} onChange={(e) => setSpaceForm((p) => ({ ...p, note: e.target.value }))} />
            </>
          ) : tab === "ip" ? (
            <>
              <label style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>{t("otcIntake.ipKind")}</label>
              <select
                className="input input-bordered w-full"
                value={ipForm.ip_kind}
                onChange={(e) => setIpForm((p) => ({ ...p, ip_kind: e.target.value }))}
              >
                {(catalog?.ip_assets || [
                  { kind: "patent", label: "Patent / invention", note: "", ownership_asset_class: "patent_invention" },
                  { kind: "recipe", label: "Recipe / formula", note: "", ownership_asset_class: "recipe_formula" },
                ]).map((i) => (
                  <option key={i.kind} value={i.kind}>{i.label}</option>
                ))}
              </select>
              <label style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>{t("otcIntake.ipTitle")}</label>
              <input className="input input-bordered w-full" value={ipForm.ip_title} onChange={(e) => setIpForm((p) => ({ ...p, ip_title: e.target.value }))} placeholder={t("otcIntake.ipTitlePlaceholder")} required />
              <label style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>{t("otcIntake.registrationUri")}</label>
              <input className="input input-bordered w-full" value={ipForm.ip_registration_uri} onChange={(e) => setIpForm((p) => ({ ...p, ip_registration_uri: e.target.value }))} />
              <label style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>{t("otcIntake.jurisdiction")}</label>
              <input className="input input-bordered w-full" value={ipForm.ip_jurisdiction} onChange={(e) => setIpForm((p) => ({ ...p, ip_jurisdiction: e.target.value }))} />
              <label style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>{t("otcIntake.estimatedAcp")}</label>
              <input className="input input-bordered w-full" value={ipForm.estimated_value_acp} onChange={(e) => setIpForm((p) => ({ ...p, estimated_value_acp: e.target.value }))} required />
              <label style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>{t("otcIntake.documentHashRequired")}</label>
              <input className="input input-bordered w-full" value={ipForm.document_hash} onChange={(e) => setIpForm((p) => ({ ...p, document_hash: e.target.value }))} required />
              <label style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>{t("otcIntake.payoutAddress")}</label>
              <input className="input input-bordered w-full" value={ipForm.payout_acp_address} onChange={(e) => setIpForm((p) => ({ ...p, payout_acp_address: e.target.value.trim() }))} required />
              <label style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>{t("otcIntake.note")}</label>
              <input className="input input-bordered w-full" value={ipForm.note} onChange={(e) => setIpForm((p) => ({ ...p, note: e.target.value }))} />
            </>
          ) : (
            <>
              <label style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>{t("otcIntake.category")}</label>
              <select
                className="input input-bordered w-full"
                value={goodsForm.goods_category}
                onChange={(e) => setGoodsForm((p) => ({ ...p, goods_category: e.target.value }))}
              >
                {(catalog?.goods || [
                  { category: "electronics", label: "Electronics" },
                  { category: "jewelry", label: "Jewelry / watches" },
                  { category: "collectibles", label: "Collectibles" },
                  { category: "industrial", label: "Industrial materials" },
                  { category: "other", label: "Other goods" },
                ]).map((g) => (
                  <option key={g.category} value={g.category}>
                    {g.label}
                  </option>
                ))}
              </select>
              <label style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>{t("otcIntake.goodsTitle")}</label>
              <input
                className="input input-bordered w-full"
                value={goodsForm.goods_title}
                onChange={(e) => setGoodsForm((p) => ({ ...p, goods_title: e.target.value }))}
                placeholder={t("otcIntake.goodsTitlePlaceholder")}
                required
              />
              <label style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>{t("otcIntake.description")}</label>
              <textarea
                className="input input-bordered w-full"
                rows={3}
                value={goodsForm.goods_description}
                onChange={(e) => setGoodsForm((p) => ({ ...p, goods_description: e.target.value }))}
                placeholder={t("otcIntake.goodsDescPlaceholder")}
              />
              <label style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>{t("otcIntake.estimatedAcpValue")}</label>
              <input
                className="input input-bordered w-full"
                inputMode="decimal"
                value={goodsForm.estimated_value_acp}
                onChange={(e) => setGoodsForm((p) => ({ ...p, estimated_value_acp: e.target.value }))}
                required
              />
              <label style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>{t("otcIntake.payoutAddress")}</label>
              <input
                className="input input-bordered w-full"
                value={goodsForm.payout_acp_address}
                onChange={(e) => setGoodsForm((p) => ({ ...p, payout_acp_address: e.target.value.trim() }))}
                required
              />
              <label style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>{t("otcIntake.noteOptional")}</label>
              <input
                className="input input-bordered w-full"
                value={goodsForm.note}
                onChange={(e) => setGoodsForm((p) => ({ ...p, note: e.target.value }))}
              />
            </>
          )}

          <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
            <button type="button" className="btn btn-ghost" onClick={() => void previewQuote()} disabled={busy}>
              {t("otcIntake.previewQuote")}
            </button>
            <button type="submit" className="btn btn-primary" disabled={busy}>
              {busy ? t("otcIntake.creating") : t("otcIntake.createIntakeOrder")}
            </button>
          </div>
        </form>

        {quote && (
          <div
            style={{
              marginTop: 12,
              color: "var(--text-muted)",
              lineHeight: 1.7,
              border: "1px solid var(--border)",
              borderRadius: 8,
              padding: 10,
              background: "var(--bg)",
            }}
          >
            <div>{quote.rate_note}</div>
            <div>
              {t("otcIntake.estimatedPayout")} <strong style={{ color: "var(--text)" }}>{quote.estimated_acp_amount} ACP</strong>
            </div>
          </div>
        )}

        {catalog && (
          <div style={{ marginTop: 14, padding: 10, border: "1px solid var(--border)", borderRadius: 8, color: "var(--text-muted)", fontSize: "0.85rem", lineHeight: 1.6 }}>
            <div>{catalog.handoff_instructions}</div>
            <div style={{ marginTop: 8 }}>{catalog.compliance_note}</div>
          </div>
        )}
      </div>

      <div className="card">
        <div className="card-header">
          <h3 style={{ fontWeight: 800, margin: 0 }}>{t("otcIntake.ordersTitle")}</h3>
          <span className="badge badge-active">{t("otcIntake.history")}</span>
        </div>

        {orders.length === 0 ? (
          <div style={{ marginTop: 12, color: "var(--text-muted)" }}>{t("otcIntake.noOrders")}</div>
        ) : (
          <div style={{ marginTop: 12, display: "grid", gap: 10 }}>
            {orders.map((o) => (
              <button
                key={o.id}
                type="button"
                className="btn btn-ghost"
                style={{ justifyContent: "space-between" }}
                onClick={() => setSelectedId(o.id)}
              >
                <span>
                  [{o.rail}] {o.asset_label} → {o.estimated_acp_amount} ACP
                </span>
                <span>{o.status}</span>
              </button>
            ))}
          </div>
        )}

        {selected && (
          <div
            style={{
              marginTop: 14,
              padding: 12,
              borderRadius: 10,
              border: "1px solid var(--border)",
              background: "var(--bg)",
              display: "grid",
              gap: 8,
            }}
          >
            <div>
              <strong>{t("otcIntake.orderLabel")}</strong> {selected.id}
            </div>
            <div>
              <strong>{t("otcIntake.statusLabel")}</strong> {selected.status}
            </div>
            <div>
              <strong>{t("otcIntake.assetLabel")}</strong> {selected.asset_label}
            </div>
            <div>
              <strong>{t("otcIntake.referenceLabel")}</strong> {selected.intake_reference}
            </div>
            <div>
              <strong>{t("otcIntake.payoutLabel")}</strong> {selected.estimated_acp_amount} ACP → {selected.payout_acp_address}
            </div>
            <div style={{ color: "var(--text-muted)", fontSize: "0.85rem", lineHeight: 1.5 }}>{selected.handoff_instructions}</div>
            <input
              className="input input-bordered w-full"
              placeholder={t("otcIntake.proofPlaceholder")}
              value={proofRef}
              onChange={(e) => setProofRef(e.target.value)}
            />
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
              <button
                type="button"
                className="btn btn-primary"
                disabled={busy || !(selected.status === "awaiting_handoff" || selected.status === "pending_review")}
                onClick={() => void confirmSelected()}
              >
                {t("otcIntake.handedOff")}
              </button>
              <button
                type="button"
                className="btn btn-ghost"
                disabled={busy || !(selected.status === "awaiting_handoff" || selected.status === "pending_review")}
                onClick={() => void cancelSelected()}
              >
                {t("otcIntake.cancel")}
              </button>
              <button
                type="button"
                className="btn btn-ghost"
                onClick={() => void navigator.clipboard.writeText(selected.intake_reference)}
              >
                {t("otcIntake.copyReference")}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
