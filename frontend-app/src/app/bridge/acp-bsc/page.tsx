"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Navigation } from "@/components/Navigation";
import { WacpPublicActions } from "@/components/WacpPublicActions";
import { useAuth } from "@/components/AuthProvider";
import { useLanguage } from "@/components/LanguageProvider";
import { bridgeRail, wacpPublic } from "@/lib/api";
import { buildAcpTxHref } from "@/lib/acpExplorer";

/** Canonical spec in the public ANCAP repo (same path as local `docs/`). */
const BRIDGE_SPEC_DOC_HREF =
  "https://github.com/ancapcloud/ancap/blob/master/docs/bridge-spec-v1.md";
type BridgeStatus = {
  bridge_rail_enabled: boolean;
  bridge_rail_paused: boolean;
  dry_run: boolean;
  wacp_contract: string;
  gateway_contract: string;
  reserve_acp_address: string;
  confirmations_acp: number;
  confirmations_bsc: number;
  bsc_explorer_base: string;
  acp_explorer_tx_base: string;
  counts_by_status: Record<string, number>;
  checkpoint_acp: number | null;
  checkpoint_bsc: number | null;
  checkpoint_acp_deposit?: number | null;
  last_reconciliation: Record<string, unknown> | null;
};

type ReserveSummary = {
  total_acp_smallest_locked_intent: string;
  total_wacp_wei_completed_mints: string;
  total_acp_display?: string;
  total_wacp_display?: string;
  wacp_per_acp?: number;
  ops_note?: string;
  operations_pending: number;
  operations_completed: number;
};

type ReserveProof = {
  acp_reserve_balance_smallest?: string;
  wacp_total_supply_wei?: string;
  wacp_total_supply_acp_smallest?: string;
  backing_ratio?: string | null;
  reserve_health?: string;
  notes?: string[];
};

function formatAcpFromSmallest(raw: string | undefined): string {
  if (!raw) return "—";
  const n = Number(raw);
  if (!Number.isFinite(n)) return raw;
  return (n / 1e8).toLocaleString("en-US", { maximumFractionDigits: 8 });
}

function formatWacpFromWei(raw: string | undefined): string {
  if (!raw) return "—";
  // Avoid float overflow for large wei — use BigInt when possible.
  try {
    const wei = BigInt(raw);
    const whole = wei / 10n ** 18n;
    const frac = wei % 10n ** 18n;
    const fracStr = frac.toString().padStart(18, "0").replace(/0+$/, "");
    const wholeStr = whole.toLocaleString("en-US");
    return fracStr ? `${wholeStr}.${fracStr}` : wholeStr;
  } catch {
    const n = Number(raw);
    if (!Number.isFinite(n)) return raw;
    return (n / 1e18).toLocaleString("en-US", { maximumFractionDigits: 8 });
  }
}

type OpRow = {
  id: string;
  direction: string;
  status: string;
  user_bsc_address: string | null;
  user_acp_address: string | null;
  amount_acp_smallest: string;
  amount_wacp_wei: string;
  remainder_wacp_wei: string;
  acp_tx_hash: string | null;
  bsc_tx_hash_mint: string | null;
  bsc_tx_hash_burn: string | null;
  deposit_ref_hex: string | null;
  bsc_log_index: number | null;
  version: number | null;
  created_at: string | null;
};

type RedeemQuote = {
  amount_wacp: string;
  amount_wacp_wei: string;
  acp_amount_floor: string;
  acp_smallest_floor: string;
  remainder_wacp_wei: string;
  remainder_wacp: string;
  policy: string;
};

export default function BridgeAcpBscPage() {
  const router = useRouter();
  const { t } = useLanguage();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const [status, setStatus] = useState<BridgeStatus | null>(null);
  const [reserve, setReserve] = useState<ReserveSummary | null>(null);
  const [proof, setProof] = useState<ReserveProof | null>(null);
  const [intents, setIntents] = useState<OpRow[]>([]);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({ user_bsc_address: "", amount_acp: "1", user_acp_address: "" });
  const [redeemForm, setRedeemForm] = useState({ user_bsc_address: "", user_acp_address: "", amount_wacp: "1" });
  const [redeemQuote, setRedeemQuote] = useState<RedeemQuote | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const st = (await bridgeRail.status()) as BridgeStatus;
      setStatus(st);
      if (st.bridge_rail_enabled) {
        try {
          setReserve((await bridgeRail.reserveSummary()) as ReserveSummary);
        } catch {
          setReserve(null);
        }
        try {
          setProof((await wacpPublic.reserveProof()) as ReserveProof);
        } catch {
          setProof(null);
        }
        if (isAuthenticated) {
          setIntents((await bridgeRail.listMyIntents(50)) as OpRow[]);
        }
      } else {
        setReserve(null);
        setProof(null);
        setIntents([]);
      }
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : t("bridgePage.loadFailed"));
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated, t]);

  useEffect(() => {
    if (!authLoading) {
      void load();
    }
  }, [authLoading, load]);

  useEffect(() => {
    let cancelled = false;
    const raw = redeemForm.amount_wacp.trim();
    if (!raw) {
      setRedeemQuote(null);
      return;
    }
    void bridgeRail.quoteBscToAcp({ amount_wacp: raw })
      .then((q) => {
        if (!cancelled) setRedeemQuote(q as RedeemQuote);
      })
      .catch(() => {
        if (!cancelled) setRedeemQuote(null);
      });
    return () => {
      cancelled = true;
    };
  }, [redeemForm.amount_wacp]);

  async function submitIntent() {
    if (!isAuthenticated) {
      router.push("/login?next=/bridge/acp-bsc");
      return;
    }
    setBusy(true);
    setError("");
    try {
      await bridgeRail.createIntentAcpToBsc({
        user_bsc_address: form.user_bsc_address.trim(),
        amount_acp: form.amount_acp.trim(),
        user_acp_address: form.user_acp_address.trim() || undefined,
      });
      await load();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : t("bridgePage.requestFailed"));
    } finally {
      setBusy(false);
    }
  }

  async function submitRedeemIntent() {
    if (!isAuthenticated) {
      router.push("/login?next=/bridge/acp-bsc");
      return;
    }
    setBusy(true);
    setError("");
    try {
      await bridgeRail.createIntentBscToAcp({
        user_bsc_address: redeemForm.user_bsc_address.trim(),
        user_acp_address: redeemForm.user_acp_address.trim(),
        amount_wacp: redeemForm.amount_wacp.trim(),
      });
      await load();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : t("bridgePage.redeemFailed"));
    } finally {
      setBusy(false);
    }
  }

  async function cancelIntent(id: string) {
    setBusy(true);
    setError("");
    try {
      await bridgeRail.cancelIntent(id);
      await load();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : t("bridgePage.cancelFailed"));
    } finally {
      setBusy(false);
    }
  }

  if (authLoading) {
    return (
      <div className="relative min-h-screen text-zinc-100">
          <Navigation />
        <main className="relative z-10 mx-auto max-w-3xl px-4 py-16">
          <p className="text-zinc-400">{t("bridgePage.loading")}</p>
        </main>
      </div>
    );
  }

  const railDisabled = Boolean(status && !status.bridge_rail_enabled);
  const showHeaderRefresh = !railDisabled;

  return (
    <div className="relative min-h-screen text-zinc-100">
      <Navigation />
      <main className="relative z-10 mx-auto max-w-3xl px-4 py-12">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div className="min-w-0">
            <h1 className="text-2xl font-semibold tracking-tight">{t("bridgePage.title")}</h1>
            <p className="mt-2 text-sm text-zinc-400">
              {t("bridgePage.leadBefore")}{" "}
              <a
                href={BRIDGE_SPEC_DOC_HREF}
                className="text-sky-400 underline decoration-sky-400/40 underline-offset-2 hover:text-sky-300"
                target="_blank"
                rel="noreferrer"
              >
                {t("bridgePage.specLink")}
              </a>{" "}
              {t("bridgePage.leadAfter")}
            </p>
          </div>
          {showHeaderRefresh ? (
            <button
              type="button"
              className="btn btn-ghost btn-sm shrink-0 self-start"
              onClick={() => void load()}
              disabled={loading}
            >
              {loading ? t("bridgePage.refreshing") : t("bridgePage.refresh")}
            </button>
          ) : null}
        </div>

        {error ? (
          <div className="mt-4 rounded border border-red-900/60 bg-red-950/40 px-3 py-2 text-sm text-red-200">{error}</div>
        ) : null}

        <section className="mt-6 rounded-xl border border-zinc-800 bg-zinc-950/60 p-4">
          <h2 className="text-lg font-medium text-zinc-200">{t("bridgePage.metamaskTitle")}</h2>
          <p className="mt-2 text-sm text-zinc-400">{t("bridgePage.metamaskLead")}</p>
          <div className="mt-4">
            <WacpPublicActions
              contractAddress={status?.wacp_contract || undefined}
              layout="home"
            />
          </div>
        </section>

        {status && !status.bridge_rail_enabled ? (
          <div className="mt-6 flex flex-col gap-3 rounded border border-amber-900/50 bg-amber-950/30 px-4 py-3 sm:flex-row sm:items-center sm:justify-between sm:gap-4">
            <p className="text-sm text-amber-100">
              {t("bridgePage.railDisabled")}
              <code className="text-amber-200">BRIDGE_RAIL_ENABLED</code>
              {t("bridgePage.railDisabledAfter")}
            </p>
            <button
              type="button"
              className="btn btn-ghost btn-sm shrink-0 self-start sm:self-auto"
              onClick={() => void load()}
              disabled={loading}
            >
              {loading ? t("bridgePage.refreshing") : t("bridgePage.refresh")}
            </button>
          </div>
        ) : null}

        {status && status.bridge_rail_enabled ? (
          <>
            <section className="mt-8 rounded-xl border border-zinc-800 bg-zinc-950/60 p-4">
              <h2 className="text-lg font-medium text-zinc-200">{t("bridgePage.statusTitle")}</h2>
              <dl className="mt-3 grid gap-2 text-sm text-zinc-400 sm:grid-cols-2">
                <div>
                  <dt className="text-zinc-500">{t("bridgePage.paused")}</dt>
                  <dd>{status.bridge_rail_paused ? t("bridgePage.yes") : t("bridgePage.no")}</dd>
                </div>
                <div>
                  <dt className="text-zinc-500">{t("bridgePage.dryRun")}</dt>
                  <dd>{status.dry_run ? t("bridgePage.yes") : t("bridgePage.no")}</dd>
                </div>
                <div>
                  <dt className="text-zinc-500">{t("bridgePage.acpCheckpoint")}</dt>
                  <dd>{status.checkpoint_acp ?? "—"}</dd>
                </div>
                <div>
                  <dt className="text-zinc-500">{t("bridgePage.acpDepositCheckpoint")}</dt>
                  <dd>{status.checkpoint_acp_deposit ?? "—"}</dd>
                </div>
                <div>
                  <dt className="text-zinc-500">{t("bridgePage.bscCheckpoint")}</dt>
                  <dd>{status.checkpoint_bsc ?? "—"}</dd>
                </div>
                <div className="sm:col-span-2">
                  <dt className="text-zinc-500">{t("bridgePage.countsByStatus")}</dt>
                  <dd className="font-mono text-xs text-zinc-300">{JSON.stringify(status.counts_by_status)}</dd>
                </div>
                <div className="sm:col-span-2">
                  <dt className="text-zinc-500">{t("bridgePage.wacpContract")}</dt>
                  <dd className="break-all font-mono text-xs">{status.wacp_contract || "—"}</dd>
                </div>
                <div className="sm:col-span-2">
                  <dt className="text-zinc-500">{t("bridgePage.gateway")}</dt>
                  <dd className="break-all font-mono text-xs">{status.gateway_contract || "—"}</dd>
                </div>
                <div className="sm:col-span-2">
                  <dt className="text-zinc-500">{t("bridgePage.reserveAddress")}</dt>
                  <dd className="break-all font-mono text-xs">{status.reserve_acp_address || "—"}</dd>
                </div>
                {status.bsc_explorer_base ? (
                  <div className="sm:col-span-2">
                    <a className="text-sky-400 underline" href={status.bsc_explorer_base} target="_blank" rel="noreferrer">
                      {t("bridgePage.bscExplorer")}
                    </a>
                  </div>
                ) : null}
              </dl>
            </section>

            {proof ? (
              <section className="mt-6 rounded-xl border border-zinc-800 bg-zinc-950/60 p-4">
                <h2 className="text-lg font-medium text-zinc-200">{t("bridgePage.liveReserveTitle")}</h2>
                <p className="mt-1 text-xs text-zinc-500">{t("bridgePage.wrapRatio")}</p>
                <ul className="mt-3 list-inside list-disc text-sm text-zinc-400">
                  <li>
                    {t("bridgePage.liveReserveAcp")}{" "}
                    <span className="font-mono text-zinc-200">{formatAcpFromSmallest(proof.acp_reserve_balance_smallest)} ACP</span>
                  </li>
                  <li>
                    {t("bridgePage.liveReserveWacp")}{" "}
                    <span className="font-mono text-zinc-200">{formatWacpFromWei(proof.wacp_total_supply_wei)} wACP</span>
                  </li>
                  <li>
                    {t("bridgePage.liveReserveLiability")}{" "}
                    <span className="font-mono text-zinc-200">{formatAcpFromSmallest(proof.wacp_total_supply_acp_smallest)} ACP</span>
                  </li>
                  <li>
                    {t("bridgePage.liveReserveBacking")}{" "}
                    <span className="font-mono text-zinc-200">{proof.backing_ratio ?? "—"}</span>
                  </li>
                  <li>
                    {t("bridgePage.liveReserveHealth")}{" "}
                    <span className="font-mono text-zinc-200">{proof.reserve_health ?? "—"}</span>
                  </li>
                </ul>
              </section>
            ) : null}

            {reserve ? (
              <section className="mt-6 rounded-xl border border-zinc-800 bg-zinc-950/60 p-4">
                <h2 className="text-lg font-medium text-zinc-200">{t("bridgePage.reserveTitle")}</h2>
                <ul className="mt-3 list-inside list-disc text-sm text-zinc-400">
                  <li>
                    {t("bridgePage.reserveAcpTotal")}{" "}
                    <span className="font-mono text-zinc-200">
                      {reserve.total_acp_display ?? formatAcpFromSmallest(reserve.total_acp_smallest_locked_intent)} ACP
                    </span>
                  </li>
                  <li>
                    {t("bridgePage.reserveWacpTotal")}{" "}
                    <span className="font-mono text-zinc-200">
                      {reserve.total_wacp_display ?? formatWacpFromWei(reserve.total_wacp_wei_completed_mints)} wACP
                    </span>
                  </li>
                  <li>{t("bridgePage.reservePending")} {reserve.operations_pending}</li>
                  <li>{t("bridgePage.reserveCompleted")} {reserve.operations_completed}</li>
                </ul>
                <p className="mt-3 text-xs text-zinc-500">
                  {reserve.ops_note || t("bridgePage.reserveOpsNote")}
                </p>
              </section>
            ) : null}

            <section className="mt-6 rounded-xl border border-zinc-800 bg-zinc-950/60 p-4">
              <h2 className="text-lg font-medium text-zinc-200">{t("bridgePage.intentTitle")}</h2>
              {!isAuthenticated ? (
                <p className="mt-2 text-sm text-zinc-500">
                  <button type="button" className="text-sky-400 underline" onClick={() => router.push("/login?next=/bridge/acp-bsc")}>
                    {t("bridgePage.signIn")}
                  </button>{" "}
                  {t("bridgePage.signInIntent")}
                </p>
              ) : (
                <>
                  <p className="mt-1 text-xs text-zinc-500">{t("bridgePage.intentHint")}</p>
                  {status?.reserve_acp_address ? (
                    <div className="mt-3 rounded border border-amber-900/40 bg-amber-950/25 px-3 py-2 text-xs text-amber-100/90">
                      <div className="font-medium text-amber-50">{t("bridgePage.depositStepTitle")}</div>
                      <p className="mt-1 text-amber-100/80">{t("bridgePage.depositStepBody")}</p>
                      <p className="mt-2 break-all font-mono text-[11px] text-amber-50">
                        {status.reserve_acp_address}
                      </p>
                    </div>
                  ) : null}
                </>
              )}
              <div className="mt-4 flex flex-col gap-3">
                {isAuthenticated ? (
                  <>
                <label className="text-sm text-zinc-400">
                  {t("bridgePage.bscAddress")}
                  <input
                    className="mt-1 w-full rounded border border-zinc-700 bg-zinc-900 px-3 py-2 font-mono text-sm"
                    value={form.user_bsc_address}
                    onChange={(e) => setForm((f) => ({ ...f, user_bsc_address: e.target.value }))}
                    placeholder="0x…"
                    autoComplete="off"
                  />
                </label>
                <label className="text-sm text-zinc-400">
                  {t("bridgePage.amountAcp")}
                  <input
                    className="mt-1 w-full rounded border border-zinc-700 bg-zinc-900 px-3 py-2 font-mono text-sm"
                    value={form.amount_acp}
                    onChange={(e) => setForm((f) => ({ ...f, amount_acp: e.target.value }))}
                  />
                </label>
                <label className="text-sm text-zinc-400">
                  {t("bridgePage.acpPayoutOptional")}
                  <input
                    className="mt-1 w-full rounded border border-zinc-700 bg-zinc-900 px-3 py-2 font-mono text-sm"
                    value={form.user_acp_address}
                    onChange={(e) => setForm((f) => ({ ...f, user_acp_address: e.target.value }))}
                    placeholder="acp1…"
                  />
                </label>
                <button
                  type="button"
                  disabled={busy || status.bridge_rail_paused}
                  onClick={() => void submitIntent()}
                  className="rounded bg-sky-600 px-4 py-2 text-sm font-medium text-white hover:bg-sky-500 disabled:opacity-40"
                >
                  {busy ? t("bridgePage.submitting") : t("bridgePage.createIntent")}
                </button>
                  </>
                ) : null}
              </div>
            </section>

            <section className="mt-6 rounded-xl border border-zinc-800 bg-zinc-950/60 p-4">
              <h2 className="text-lg font-medium text-zinc-200">{t("bridgePage.redeemTitle")}</h2>
              {!isAuthenticated ? (
                <p className="mt-2 text-sm text-zinc-500">
                  <button type="button" className="text-sky-400 underline" onClick={() => router.push("/login?next=/bridge/acp-bsc")}>
                    {t("bridgePage.signIn")}
                  </button>{" "}
                  {t("bridgePage.signInRedeem")}
                </p>
              ) : (
              <p className="mt-1 text-xs text-zinc-500">{t("bridgePage.redeemHint")}</p>)}
              <div className="mt-4 flex flex-col gap-3">
                {isAuthenticated ? (
                  <>
                    <label className="text-sm text-zinc-400">
                      {t("bridgePage.bscAddress")}
                      <input
                        className="mt-1 w-full rounded border border-zinc-700 bg-zinc-900 px-3 py-2 font-mono text-sm"
                        value={redeemForm.user_bsc_address}
                        onChange={(e) => setRedeemForm((f) => ({ ...f, user_bsc_address: e.target.value }))}
                        placeholder="0x…"
                        autoComplete="off"
                      />
                    </label>
                    <label className="text-sm text-zinc-400">
                      {t("bridgePage.acpPayout")}
                      <input
                        className="mt-1 w-full rounded border border-zinc-700 bg-zinc-900 px-3 py-2 font-mono text-sm"
                        value={redeemForm.user_acp_address}
                        onChange={(e) => setRedeemForm((f) => ({ ...f, user_acp_address: e.target.value }))}
                        placeholder="acp1…"
                        autoComplete="off"
                      />
                    </label>
                    <label className="text-sm text-zinc-400">
                      {t("bridgePage.amountWacp")}
                      <input
                        className="mt-1 w-full rounded border border-zinc-700 bg-zinc-900 px-3 py-2 font-mono text-sm"
                        value={redeemForm.amount_wacp}
                        onChange={(e) => setRedeemForm((f) => ({ ...f, amount_wacp: e.target.value }))}
                      />
                    </label>
                    {redeemQuote ? (
                      <div className="rounded border border-zinc-800 bg-zinc-900/70 px-3 py-2 text-xs text-zinc-400">
                        <div>{t("bridgePage.quoteFloor")} <span className="font-mono text-zinc-200">{redeemQuote.acp_amount_floor}</span></div>
                        <div>{t("bridgePage.quoteSmallest")} <span className="font-mono text-zinc-200">{redeemQuote.acp_smallest_floor}</span></div>
                        <div>{t("bridgePage.quoteRemainder")} <span className="font-mono text-zinc-200">{redeemQuote.remainder_wacp}</span> wACP (<span className="font-mono text-zinc-200">{redeemQuote.remainder_wacp_wei}</span> wei)</div>
                        <div className="mt-1 text-zinc-500">{redeemQuote.policy}</div>
                      </div>
                    ) : (
                      <div className="text-xs text-zinc-500">{t("bridgePage.quotePreview")}</div>
                    )}
                    <button
                      type="button"
                      disabled={busy || status.bridge_rail_paused}
                      onClick={() => void submitRedeemIntent()}
                      className="rounded bg-zinc-100 px-4 py-2 text-sm font-medium text-zinc-900 hover:bg-white disabled:opacity-40"
                    >
                      {busy ? t("bridgePage.submitting") : t("bridgePage.createRedeem")}
                    </button>
                  </>
                ) : null}
              </div>
            </section>

            {isAuthenticated ? (
            <section className="mt-6 rounded-xl border border-zinc-800 bg-zinc-950/60 p-4">
              <h2 className="text-lg font-medium text-zinc-200">{t("bridgePage.myIntents")}</h2>
              {intents.length === 0 ? (
                <p className="mt-2 text-sm text-zinc-500">{t("bridgePage.noIntents")}</p>
              ) : (
                <ul className="mt-3 space-y-2 text-sm">
                  {intents.map((o) => {
                    const bscTxHash = o.bsc_tx_hash_mint || o.bsc_tx_hash_burn;
                    const bscTxHref = bscTxHash && status?.bsc_explorer_base
                      ? `${status.bsc_explorer_base.replace(/\/$/, "")}/tx/${bscTxHash.startsWith("0x") ? bscTxHash : `0x${bscTxHash}`}`
                      : null;
                    const acpTxHref = o.acp_tx_hash
                      ? buildAcpTxHref(o.acp_tx_hash, status?.acp_explorer_tx_base)
                      : null;
                    return (
                      <li key={o.id} className="rounded border border-zinc-800 bg-zinc-900/50 px-3 py-2 font-mono text-xs text-zinc-300">
                        <div className="text-zinc-500 break-all">{o.id}</div>
                        <div>
                          {o.status} -&gt; {o.direction}
                        </div>
                        <div>
                          acp_smallest={o.amount_acp_smallest} wacp_wei={o.amount_wacp_wei}
                        </div>
                        {o.direction === "bsc_to_acp" ? <div>remainder_wacp_wei={o.remainder_wacp_wei}</div> : null}
                        <div className="break-all">bsc={o.user_bsc_address}</div>
                        {o.user_acp_address ? <div className="break-all">acp={o.user_acp_address}</div> : null}
                        {o.acp_tx_hash ? <div className="break-all">acp_tx={o.acp_tx_hash}</div> : null}
                        {o.bsc_tx_hash_mint ? <div className="break-all">bsc_mint_tx={o.bsc_tx_hash_mint}</div> : null}
                        {o.bsc_tx_hash_burn ? <div className="break-all">bsc_burn_tx={o.bsc_tx_hash_burn}</div> : null}
                        {o.deposit_ref_hex ? <div className="break-all">deposit_ref={o.deposit_ref_hex}</div> : null}
                        {o.bsc_log_index !== null && o.bsc_log_index !== undefined ? <div>log_index={o.bsc_log_index}</div> : null}
                        {o.version !== null && o.version !== undefined ? <div>version={o.version}</div> : null}
                        {acpTxHref ? (
                          <div>
                            <a className="text-sky-400 underline" href={acpTxHref} target="_blank" rel="noreferrer">
                              {t("bridgePage.openAcpTx")}
                            </a>
                          </div>
                        ) : null}
                        {bscTxHref ? (
                          <div>
                            <a className="text-sky-400 underline" href={bscTxHref} target="_blank" rel="noreferrer">
                              {t("bridgePage.openBscTx")}
                            </a>
                          </div>
                        ) : null}
                        {o.status === "PENDING_DEPOSIT" && o.direction === "acp_to_bsc" && !o.acp_tx_hash ? (
                          <div className="mt-2">
                            <button
                              type="button"
                              disabled={busy}
                              onClick={() => void cancelIntent(o.id)}
                              className="rounded border border-amber-800/60 px-2 py-1 text-[11px] text-amber-200 hover:bg-amber-950/40 disabled:opacity-40"
                            >
                              {t("bridgePage.cancelPending")}
                            </button>
                          </div>
                        ) : null}
                      </li>
                    );
                  })}
                </ul>
              )}
            </section>
            ) : null}
          </>
        ) : null}
      </main>
    </div>
  );
}
