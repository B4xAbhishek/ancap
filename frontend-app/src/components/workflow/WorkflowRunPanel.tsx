"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/components/AuthProvider";
import { useLanguage } from "@/components/LanguageProvider";
import { workflowStore } from "@/lib/api";
import type { WorkflowTemplate } from "@/lib/workflowStore";

type WorkflowRun = {
  id: string;
  workflow_slug: string;
  title: string;
  category: string;
  status: string;
  price: { amount: string; currency: string };
  payment_currency: string;
  unlock_full_result: boolean;
  inputs: Record<string, any>;
  preview: Record<string, any>;
  result?: Record<string, any> | null;
  receipt: {
    workflow_slug: string;
    payment_currency: string;
    quoted_price: { amount: string; currency: string };
    status: string;
    receipt_items: string[];
    proof: Record<string, any>;
  };
  created_at: string;
  owner_user_id?: string | null;
};

type ListingPackForm = {
  project_name: string;
  token_symbol: string;
  token_type: string;
  audience: string;
  chain: string;
  market: string;
  liquidity_model: string;
};

type CampaignBuilderForm = {
  project_name: string;
  audience: string;
  primary_cta: string;
  posting_style: string;
  goals_text: string;
  channels_text: string;
};

type TelegramGrowthForm = {
  project_name: string;
  audience: string;
  posting_style: string;
};

type AirdropBountyForm = {
  project_name: string;
  reward_budget: string;
  constraints_text: string;
};

type TokenRiskForm = {
  project_name: string;
  token_symbol: string;
  token_type: string;
  chain: string;
  liquidity_model: string;
  geography: string;
  competitors_text: string;
};

const DEFAULT_LISTING_PACK_FORM: ListingPackForm = {
  project_name: "",
  token_symbol: "",
  token_type: "utility token",
  audience: "crypto teams",
  chain: "Base",
  market: "global crypto market",
  liquidity_model: "DEX-led liquidity",
};

const DEFAULT_CAMPAIGN_BUILDER_FORM: CampaignBuilderForm = {
  project_name: "",
  audience: "crypto teams",
  primary_cta: "Book a call / request a workflow",
  posting_style: "direct, proof-driven, anti-hype",
  goals_text: "Increase qualified inbound\nImprove campaign clarity\nRaise conversion intent",
  channels_text: "Telegram\nX\nLanding page",
};

const DEFAULT_TELEGRAM_GROWTH_FORM: TelegramGrowthForm = {
  project_name: "",
  audience: "community members",
  posting_style: "direct, proof-driven, anti-spam",
};

const DEFAULT_AIRDROP_BOUNTY_FORM: AirdropBountyForm = {
  project_name: "",
  reward_budget: "to be defined",
  constraints_text: "Avoid spam-farm incentives\nKeep review burden manageable",
};

const DEFAULT_TOKEN_RISK_FORM: TokenRiskForm = {
  project_name: "",
  token_symbol: "",
  token_type: "utility token",
  chain: "Base",
  liquidity_model: "DEX-led liquidity",
  geography: "global",
  competitors_text: "",
};

function linesToArray(value: string) {
  return value
    .split(/\r?\n/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function supportsStructuredWorkflow(workflowSlug: string) {
  return [
    "token-listing-pack",
    "crypto-campaign-builder",
    "telegram-growth-kit",
    "airdrop-bounty-builder",
    "token-risk-report",
  ].includes(workflowSlug);
}

function buildInputsFromStructuredForm(
  workflowSlug: string,
  listingPackForm: ListingPackForm,
  campaignBuilderForm: CampaignBuilderForm,
  telegramGrowthForm: TelegramGrowthForm,
  airdropBountyForm: AirdropBountyForm,
  tokenRiskForm: TokenRiskForm,
) {
  if (workflowSlug === "token-listing-pack") {
    return {
      project_name: listingPackForm.project_name.trim(),
      token_symbol: listingPackForm.token_symbol.trim(),
      token_type: listingPackForm.token_type.trim(),
      audience: listingPackForm.audience.trim(),
      chain: listingPackForm.chain.trim(),
      market: listingPackForm.market.trim(),
      liquidity_model: listingPackForm.liquidity_model.trim(),
    };
  }

  if (workflowSlug === "crypto-campaign-builder") {
    return {
      project_name: campaignBuilderForm.project_name.trim(),
      audience: campaignBuilderForm.audience.trim(),
      primary_cta: campaignBuilderForm.primary_cta.trim(),
      posting_style: campaignBuilderForm.posting_style.trim(),
      goals: linesToArray(campaignBuilderForm.goals_text),
      channels: linesToArray(campaignBuilderForm.channels_text),
    };
  }

  if (workflowSlug === "telegram-growth-kit") {
    return {
      project_name: telegramGrowthForm.project_name.trim(),
      audience: telegramGrowthForm.audience.trim(),
      posting_style: telegramGrowthForm.posting_style.trim(),
    };
  }

  if (workflowSlug === "airdrop-bounty-builder") {
    return {
      project_name: airdropBountyForm.project_name.trim(),
      reward_budget: airdropBountyForm.reward_budget.trim(),
      constraints: linesToArray(airdropBountyForm.constraints_text),
    };
  }

  if (workflowSlug === "token-risk-report") {
    return {
      project_name: tokenRiskForm.project_name.trim(),
      token_symbol: tokenRiskForm.token_symbol.trim(),
      token_type: tokenRiskForm.token_type.trim(),
      chain: tokenRiskForm.chain.trim(),
      liquidity_model: tokenRiskForm.liquidity_model.trim(),
      geography: tokenRiskForm.geography.trim(),
      competitors: linesToArray(tokenRiskForm.competitors_text),
    };
  }

  return {};
}

function hydrateStructuredFormFromInputs(
  workflowSlug: string,
  inputs: Record<string, any>,
): {
  listingPackForm?: ListingPackForm;
  campaignBuilderForm?: CampaignBuilderForm;
  telegramGrowthForm?: TelegramGrowthForm;
  airdropBountyForm?: AirdropBountyForm;
  tokenRiskForm?: TokenRiskForm;
} {
  if (workflowSlug === "token-listing-pack") {
    return {
      listingPackForm: {
        project_name: String(inputs.project_name || ""),
        token_symbol: String(inputs.token_symbol || ""),
        token_type: String(inputs.token_type || DEFAULT_LISTING_PACK_FORM.token_type),
        audience: String(inputs.audience || DEFAULT_LISTING_PACK_FORM.audience),
        chain: String(inputs.chain || DEFAULT_LISTING_PACK_FORM.chain),
        market: String(inputs.market || DEFAULT_LISTING_PACK_FORM.market),
        liquidity_model: String(inputs.liquidity_model || DEFAULT_LISTING_PACK_FORM.liquidity_model),
      },
    };
  }

  if (workflowSlug === "crypto-campaign-builder") {
    return {
      campaignBuilderForm: {
        project_name: String(inputs.project_name || ""),
        audience: String(inputs.audience || DEFAULT_CAMPAIGN_BUILDER_FORM.audience),
        primary_cta: String(inputs.primary_cta || DEFAULT_CAMPAIGN_BUILDER_FORM.primary_cta),
        posting_style: String(inputs.posting_style || DEFAULT_CAMPAIGN_BUILDER_FORM.posting_style),
        goals_text: Array.isArray(inputs.goals) ? inputs.goals.join("\n") : DEFAULT_CAMPAIGN_BUILDER_FORM.goals_text,
        channels_text: Array.isArray(inputs.channels) ? inputs.channels.join("\n") : DEFAULT_CAMPAIGN_BUILDER_FORM.channels_text,
      },
    };
  }

  if (workflowSlug === "telegram-growth-kit") {
    return {
      telegramGrowthForm: {
        project_name: String(inputs.project_name || ""),
        audience: String(inputs.audience || DEFAULT_TELEGRAM_GROWTH_FORM.audience),
        posting_style: String(inputs.posting_style || DEFAULT_TELEGRAM_GROWTH_FORM.posting_style),
      },
    };
  }

  if (workflowSlug === "airdrop-bounty-builder") {
    return {
      airdropBountyForm: {
        project_name: String(inputs.project_name || ""),
        reward_budget: String(inputs.reward_budget || DEFAULT_AIRDROP_BOUNTY_FORM.reward_budget),
        constraints_text: Array.isArray(inputs.constraints) ? inputs.constraints.join("\n") : DEFAULT_AIRDROP_BOUNTY_FORM.constraints_text,
      },
    };
  }

  if (workflowSlug === "token-risk-report") {
    return {
      tokenRiskForm: {
        project_name: String(inputs.project_name || ""),
        token_symbol: String(inputs.token_symbol || ""),
        token_type: String(inputs.token_type || DEFAULT_TOKEN_RISK_FORM.token_type),
        chain: String(inputs.chain || DEFAULT_TOKEN_RISK_FORM.chain),
        liquidity_model: String(inputs.liquidity_model || DEFAULT_TOKEN_RISK_FORM.liquidity_model),
        geography: String(inputs.geography || DEFAULT_TOKEN_RISK_FORM.geography),
        competitors_text: Array.isArray(inputs.competitors) ? inputs.competitors.join("\n") : DEFAULT_TOKEN_RISK_FORM.competitors_text,
      },
    };
  }

  return {};
}

export function WorkflowRunPanel({ workflow }: { workflow: WorkflowTemplate }) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { isAuthenticated, isLoading } = useAuth();
  const { t } = useLanguage();
  const [paymentCurrency, setPaymentCurrency] = useState(workflow.accepted_currencies[0] || "ACP");
  const [unlockFullResult, setUnlockFullResult] = useState(true);
  const [useStructuredForm, setUseStructuredForm] = useState(supportsStructuredWorkflow(workflow.slug));
  const [inputsText, setInputsText] = useState(JSON.stringify({}, null, 2));
  const [listingPackForm, setListingPackForm] = useState<ListingPackForm>(DEFAULT_LISTING_PACK_FORM);
  const [campaignBuilderForm, setCampaignBuilderForm] = useState<CampaignBuilderForm>(DEFAULT_CAMPAIGN_BUILDER_FORM);
  const [telegramGrowthForm, setTelegramGrowthForm] = useState<TelegramGrowthForm>(DEFAULT_TELEGRAM_GROWTH_FORM);
  const [airdropBountyForm, setAirdropBountyForm] = useState<AirdropBountyForm>(DEFAULT_AIRDROP_BOUNTY_FORM);
  const [tokenRiskForm, setTokenRiskForm] = useState<TokenRiskForm>(DEFAULT_TOKEN_RISK_FORM);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [createdRun, setCreatedRun] = useState<WorkflowRun | null>(null);
  const [history, setHistory] = useState<WorkflowRun[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [adultAttested, setAdultAttested] = useState(false);

  const requiresAdultAttestation = workflow.slug === "entertainment-tesla-coil-party";
  const supportsStructuredForm = supportsStructuredWorkflow(workflow.slug);
  const prefillAppliedKey = useMemo(
    () => `${workflow.slug}:${searchParams?.get("fromRun") || ""}:${searchParams?.get("prefill") || ""}`,
    [workflow.slug, searchParams],
  );

  const pricePreview = useMemo(() => {
    const base = Number(workflow.price.amount || 0);
    if (paymentCurrency === "wACP") return `${(base * 9).toFixed(2)} ${paymentCurrency}`;
    return `${base.toFixed(2)} ${paymentCurrency}`;
  }, [workflow.price.amount, paymentCurrency]);

  useEffect(() => {
    const prefillMode = searchParams?.get("prefill");
    const prefillInputsRaw = searchParams?.get("inputs");
    const prefillCurrency = searchParams?.get("paymentCurrency");
    const prefillUnlock = searchParams?.get("unlockFullResult");

    if (prefillMode !== "1" || !prefillInputsRaw) return;

    try {
      const parsed = JSON.parse(prefillInputsRaw);
      const nextInputs = parsed && typeof parsed === "object" ? parsed : {};
      setInputsText(JSON.stringify(nextInputs, null, 2));

      if (prefillCurrency && workflow.accepted_currencies.includes(prefillCurrency)) {
        setPaymentCurrency(prefillCurrency);
      }
      if (prefillUnlock === "0") {
        setUnlockFullResult(false);
      } else if (prefillUnlock === "1") {
        setUnlockFullResult(true);
      }

      if (supportsStructuredForm) {
        setUseStructuredForm(true);
        const hydrated = hydrateStructuredFormFromInputs(workflow.slug, nextInputs);
        if (hydrated.listingPackForm) setListingPackForm(hydrated.listingPackForm);
        if (hydrated.campaignBuilderForm) setCampaignBuilderForm(hydrated.campaignBuilderForm);
        if (hydrated.telegramGrowthForm) setTelegramGrowthForm(hydrated.telegramGrowthForm);
        if (hydrated.airdropBountyForm) setAirdropBountyForm(hydrated.airdropBountyForm);
        if (hydrated.tokenRiskForm) setTokenRiskForm(hydrated.tokenRiskForm);
      }
    } catch {
      // ignore malformed prefill payloads
    }
  }, [prefillAppliedKey, searchParams, workflow.slug, workflow.accepted_currencies, supportsStructuredForm]);

  useEffect(() => {
    if (!supportsStructuredForm || !useStructuredForm) return;
    const nextInputs = buildInputsFromStructuredForm(
      workflow.slug,
      listingPackForm,
      campaignBuilderForm,
      telegramGrowthForm,
      airdropBountyForm,
      tokenRiskForm,
    );
    setInputsText(JSON.stringify(nextInputs, null, 2));
  }, [
    workflow.slug,
    supportsStructuredForm,
    useStructuredForm,
    listingPackForm,
    campaignBuilderForm,
    telegramGrowthForm,
    airdropBountyForm,
    tokenRiskForm,
  ]);

  useEffect(() => {
    if (!isAuthenticated) return;
    let cancelled = false;
    (async () => {
      try {
        setHistoryLoading(true);
        const data = await workflowStore.listRuns(10);
        if (!cancelled) {
          setHistory((data.items || []).filter((item: WorkflowRun) => item.workflow_slug === workflow.slug));
        }
      } catch {
        if (!cancelled) setHistory([]);
      } finally {
        if (!cancelled) setHistoryLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [isAuthenticated, workflow.slug]);

  async function submit() {
    if (!isAuthenticated) {
      router.push("/login");
      return;
    }
    if (requiresAdultAttestation && !adultAttested) {
      setError(t("workflowRunPanel.adultAttestationError"));
      return;
    }

    setSubmitting(true);
    setError("");
    try {
      const parsed = JSON.parse(inputsText || "{}");
      const inputs =
        requiresAdultAttestation
          ? { ...parsed, adult_age_attested: true, age_gate: "18_or_21_by_jurisdiction" }
          : parsed;
      const created = await workflowStore.createRun({
        workflow_slug: workflow.slug,
        payment_currency: paymentCurrency,
        unlock_full_result: unlockFullResult,
        inputs,
      });
      setCreatedRun(created);
      setHistory((prev) => [created, ...prev].slice(0, 10));
      router.push(`/ai/runs/${created.id}`);
    } catch (e: any) {
      setError(e?.message || String(e));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="mt-6 space-y-4">
      <div className="rounded-2xl border border-white/10 bg-black/15 p-4">
        <div className="text-sm font-semibold text-white/90">{t("workflowRunPanel.createRun")}</div>
        <div className="mt-3 grid gap-3 md:grid-cols-4">
          {[
            [t("workflowRunPanel.stepQuote"), pricePreview],
            [t("workflowRunPanel.stepPayment"), t("workflowRunPanel.acpIntent")],
            [t("workflowRunPanel.stepRun"), workflow.slug],
            [t("workflowRunPanel.stepReceipt"), t("workflowRunPanel.proofReady")],
          ].map(([label, value]) => (
            <div key={label} className="rounded-2xl border border-white/10 bg-white/[0.03] p-3">
              <div className="text-[11px] uppercase tracking-[0.18em] text-white/40">{label}</div>
              <div className="mt-1 break-all text-sm font-semibold text-white/82">{value}</div>
            </div>
          ))}
        </div>
        {searchParams?.get("prefill") === "1" && (
          <div className="mt-3 rounded-2xl border border-emerald-400/20 bg-emerald-400/8 p-3 text-sm text-emerald-100/90">
            {t("workflowRunPanel.prefilledNotice")}
          </div>
        )}
        <div className="mt-4 grid gap-4">
          <div>
            <div className="mb-2 text-xs uppercase tracking-[0.18em] text-white/45">{t("workflowRunPanel.paymentCurrency")}</div>
            <div className="flex flex-wrap gap-2">
              {workflow.accepted_currencies.map((currency) => (
                <button
                  key={currency}
                  type="button"
                  onClick={() => setPaymentCurrency(currency)}
                  className={`rounded-full px-3 py-1.5 text-xs font-semibold transition ${paymentCurrency === currency ? "bg-emerald-400 text-slate-950" : "border border-white/12 text-white/70 hover:border-white/25"}`}
                >
                  {currency}
                </button>
              ))}
            </div>
            <div className="mt-2 text-sm text-emerald-300">{t("workflowRunPanel.quotedPrice")} {pricePreview}</div>
          </div>

          <label className="flex items-center gap-3 text-sm text-white/75">
            <input type="checkbox" checked={unlockFullResult} onChange={(e) => setUnlockFullResult(e.target.checked)} />
            <span>{t("workflowRunPanel.unlockFullResult")}</span>
          </label>

          {supportsStructuredForm && (
            <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <div className="text-sm font-semibold text-white/90">{t("workflowRunPanel.inputMode")}</div>
                  <div className="mt-1 text-sm text-white/55">{t("workflowRunPanel.inputModeLead")}</div>
                </div>
                <button
                  type="button"
                  onClick={() => setUseStructuredForm((value) => !value)}
                  className="rounded-full border border-white/15 px-4 py-2 text-sm font-semibold text-white/85 transition hover:border-white/30 hover:text-white"
                >
                  {useStructuredForm ? t("workflowRunPanel.switchToJson") : t("workflowRunPanel.switchToForm")}
                </button>
              </div>
            </div>
          )}

          {useStructuredForm && workflow.slug === "token-listing-pack" && (
            <div className="grid gap-4 md:grid-cols-2">
              <InputField label={t("workflowRunPanel.projectName")} value={listingPackForm.project_name} onChange={(value) => setListingPackForm((prev) => ({ ...prev, project_name: value }))} />
              <InputField label={t("workflowRunPanel.tokenSymbol")} value={listingPackForm.token_symbol} onChange={(value) => setListingPackForm((prev) => ({ ...prev, token_symbol: value }))} />
              <InputField label={t("workflowRunPanel.tokenType")} value={listingPackForm.token_type} onChange={(value) => setListingPackForm((prev) => ({ ...prev, token_type: value }))} />
              <InputField label={t("workflowRunPanel.audience")} value={listingPackForm.audience} onChange={(value) => setListingPackForm((prev) => ({ ...prev, audience: value }))} />
              <InputField label={t("workflowRunPanel.chainNetwork")} value={listingPackForm.chain} onChange={(value) => setListingPackForm((prev) => ({ ...prev, chain: value }))} />
              <InputField label={t("workflowRunPanel.market")} value={listingPackForm.market} onChange={(value) => setListingPackForm((prev) => ({ ...prev, market: value }))} />
              <div className="md:col-span-2">
                <InputField label={t("workflowRunPanel.liquidityModel")} value={listingPackForm.liquidity_model} onChange={(value) => setListingPackForm((prev) => ({ ...prev, liquidity_model: value }))} />
              </div>
            </div>
          )}

          {useStructuredForm && workflow.slug === "crypto-campaign-builder" && (
            <div className="grid gap-4 md:grid-cols-2">
              <InputField label={t("workflowRunPanel.projectName")} value={campaignBuilderForm.project_name} onChange={(value) => setCampaignBuilderForm((prev) => ({ ...prev, project_name: value }))} />
              <InputField label={t("workflowRunPanel.audience")} value={campaignBuilderForm.audience} onChange={(value) => setCampaignBuilderForm((prev) => ({ ...prev, audience: value }))} />
              <div className="md:col-span-2">
                <InputField label={t("workflowRunPanel.primaryCta")} value={campaignBuilderForm.primary_cta} onChange={(value) => setCampaignBuilderForm((prev) => ({ ...prev, primary_cta: value }))} />
              </div>
              <div className="md:col-span-2">
                <InputField label={t("workflowRunPanel.postingStyle")} value={campaignBuilderForm.posting_style} onChange={(value) => setCampaignBuilderForm((prev) => ({ ...prev, posting_style: value }))} />
              </div>
              <TextareaField label={t("workflowRunPanel.goalsOnePerLine")} value={campaignBuilderForm.goals_text} rows={5} onChange={(value) => setCampaignBuilderForm((prev) => ({ ...prev, goals_text: value }))} />
              <TextareaField label={t("workflowRunPanel.channelsOnePerLine")} value={campaignBuilderForm.channels_text} rows={5} onChange={(value) => setCampaignBuilderForm((prev) => ({ ...prev, channels_text: value }))} />
            </div>
          )}

          {useStructuredForm && workflow.slug === "telegram-growth-kit" && (
            <div className="grid gap-4 md:grid-cols-2">
              <InputField label={t("workflowRunPanel.projectName")} value={telegramGrowthForm.project_name} onChange={(value) => setTelegramGrowthForm((prev) => ({ ...prev, project_name: value }))} />
              <InputField label={t("workflowRunPanel.audience")} value={telegramGrowthForm.audience} onChange={(value) => setTelegramGrowthForm((prev) => ({ ...prev, audience: value }))} />
              <div className="md:col-span-2">
                <InputField label={t("workflowRunPanel.postingStyle")} value={telegramGrowthForm.posting_style} onChange={(value) => setTelegramGrowthForm((prev) => ({ ...prev, posting_style: value }))} />
              </div>
            </div>
          )}

          {useStructuredForm && workflow.slug === "airdrop-bounty-builder" && (
            <div className="grid gap-4 md:grid-cols-2">
              <InputField label={t("workflowRunPanel.projectName")} value={airdropBountyForm.project_name} onChange={(value) => setAirdropBountyForm((prev) => ({ ...prev, project_name: value }))} />
              <InputField label={t("workflowRunPanel.rewardBudget")} value={airdropBountyForm.reward_budget} onChange={(value) => setAirdropBountyForm((prev) => ({ ...prev, reward_budget: value }))} />
              <div className="md:col-span-2">
                <TextareaField label={t("workflowRunPanel.constraintsOnePerLine")} value={airdropBountyForm.constraints_text} rows={5} onChange={(value) => setAirdropBountyForm((prev) => ({ ...prev, constraints_text: value }))} />
              </div>
            </div>
          )}

          {useStructuredForm && workflow.slug === "token-risk-report" && (
            <div className="grid gap-4 md:grid-cols-2">
              <InputField label={t("workflowRunPanel.projectName")} value={tokenRiskForm.project_name} onChange={(value) => setTokenRiskForm((prev) => ({ ...prev, project_name: value }))} />
              <InputField label={t("workflowRunPanel.tokenSymbol")} value={tokenRiskForm.token_symbol} onChange={(value) => setTokenRiskForm((prev) => ({ ...prev, token_symbol: value }))} />
              <InputField label={t("workflowRunPanel.tokenType")} value={tokenRiskForm.token_type} onChange={(value) => setTokenRiskForm((prev) => ({ ...prev, token_type: value }))} />
              <InputField label={t("workflowRunPanel.chainNetwork")} value={tokenRiskForm.chain} onChange={(value) => setTokenRiskForm((prev) => ({ ...prev, chain: value }))} />
              <InputField label={t("workflowRunPanel.liquidityModel")} value={tokenRiskForm.liquidity_model} onChange={(value) => setTokenRiskForm((prev) => ({ ...prev, liquidity_model: value }))} />
              <InputField label={t("workflowRunPanel.geography")} value={tokenRiskForm.geography} onChange={(value) => setTokenRiskForm((prev) => ({ ...prev, geography: value }))} />
              <div className="md:col-span-2">
                <TextareaField label={t("workflowRunPanel.competitorsOnePerLine")} value={tokenRiskForm.competitors_text} rows={5} onChange={(value) => setTokenRiskForm((prev) => ({ ...prev, competitors_text: value }))} />
              </div>
            </div>
          )}

          <div>
            <div className="mb-2 text-xs uppercase tracking-[0.18em] text-white/45">{t("workflowRunPanel.inputsJson")}</div>
            <textarea
              value={inputsText}
              onChange={(e) => {
                setUseStructuredForm(false);
                setInputsText(e.target.value);
              }}
              rows={8}
              className="w-full rounded-2xl border border-white/10 bg-[var(--bg)] p-3 text-sm text-white outline-none"
              style={{ fontFamily: "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace" }}
            />
            <div className="mt-2 text-xs text-white/45">{t("workflowRunPanel.inputsJsonHint")}</div>
          </div>

          {requiresAdultAttestation ? (
            <label className="flex items-start gap-3 rounded-2xl border border-amber-400/25 bg-amber-400/8 p-4 text-sm text-amber-50/90">
              <input
                type="checkbox"
                checked={adultAttested}
                onChange={(e) => setAdultAttested(e.target.checked)}
                className="mt-1"
              />
              <span>{t("workflowRunPanel.adultAttestation")}</span>
            </label>
          ) : null}

          {error && <div className="rounded-2xl border border-red-400/25 bg-red-500/10 p-3 text-sm text-red-200">{error}</div>}

          <div className="flex flex-wrap gap-3">
            <button
              type="button"
              onClick={submit}
              disabled={submitting || isLoading || (requiresAdultAttestation && !adultAttested)}
              className="rounded-full bg-emerald-400 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:opacity-90 disabled:opacity-60"
            >
              {submitting ? t("workflowRunPanel.creatingRun") : isAuthenticated ? t("workflowRunPanel.runWorkflow") : t("workflowRunPanel.signInToRun")}
            </button>
            <Link href="/dashboard" className="rounded-full border border-white/15 px-5 py-3 text-sm font-semibold text-white/85 transition hover:border-white/30 hover:text-white">
              {t("workflowRunPanel.openDashboard")}
            </Link>
          </div>
        </div>
      </div>

      {createdRun && (
        <div className="rounded-2xl border border-emerald-400/20 bg-emerald-500/10 p-4">
          <div className="text-sm font-semibold text-emerald-200">{t("workflowRunPanel.runCreated")}</div>
          <div className="mt-2 text-sm text-white/80">{t("workflowRunPanel.status")} {createdRun.status}</div>
          <div className="text-sm text-white/80">{t("workflowRunPanel.quotedPriceLabel")} {createdRun.price.amount} {createdRun.price.currency}</div>
          <div className="text-sm text-white/80">{t("workflowRunPanel.runId")} {createdRun.id}</div>
          {Array.isArray(createdRun.receipt.receipt_items) && createdRun.receipt.receipt_items.length > 0 && (
            <ul className="mt-3 space-y-2 text-sm text-white/75">
              {createdRun.receipt.receipt_items.map((item) => (
                <li key={item} className="flex items-center gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-300" />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          )}
          <div className="mt-4 flex flex-wrap gap-3">
            <Link href={`/proof-center?run=${createdRun.id}`} className="rounded-full border border-emerald-400/25 px-4 py-2 text-sm font-semibold text-emerald-200 transition hover:border-emerald-300/50 hover:text-emerald-100">
              {t("workflowRunPanel.openProofUrl")}
            </Link>
            <Link href={`/ai/runs/${createdRun.id}`} className="rounded-full border border-white/15 px-4 py-2 text-sm font-semibold text-white/85 transition hover:border-white/30 hover:text-white">
              {t("workflowRunPanel.openRunDetail")}
            </Link>
          </div>
        </div>
      )}

      <div className="rounded-2xl border border-white/10 bg-black/15 p-4">
        <div className="text-sm font-semibold text-white/90">{t("workflowRunPanel.recentRuns")}</div>
        {!isAuthenticated ? (
          <div className="mt-3 text-sm text-white/55">{t("workflowRunPanel.signInForHistory")}</div>
        ) : historyLoading ? (
          <div className="mt-3 text-sm text-white/55">{t("workflowRunPanel.loadingHistory")}</div>
        ) : history.length === 0 ? (
          <div className="mt-3 text-sm text-white/55">{t("workflowRunPanel.noRuns")}</div>
        ) : (
          <div className="mt-3 space-y-3">
            {history.map((run) => (
              <div key={run.id} className="rounded-2xl border border-white/10 bg-white/[0.03] p-3 text-sm">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div className="font-medium text-white/88">{run.title}</div>
                  <div className="text-emerald-300">{run.price.amount} {run.price.currency}</div>
                </div>
                <div className="mt-2 text-white/60">{t("workflowRunPanel.status")} {run.status}</div>
                <div className="text-white/45">{new Date(run.created_at).toLocaleString()}</div>
                <div className="mt-3">
                  <Link href={`/ai/runs/${run.id}`} className="rounded-full border border-white/15 px-3 py-1.5 text-xs font-semibold text-white/85 transition hover:border-white/30 hover:text-white">
                    {t("workflowRunPanel.openRun")}
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function InputField({ label, value, onChange }: { label: string; value: string; onChange: (value: string) => void }) {
  return (
    <div>
      <div className="mb-2 text-xs uppercase tracking-[0.18em] text-white/45">{label}</div>
      <input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full rounded-2xl border border-white/10 bg-[var(--bg)] px-4 py-3 text-sm text-white outline-none"
      />
    </div>
  );
}

function TextareaField({ label, value, rows, onChange }: { label: string; value: string; rows: number; onChange: (value: string) => void }) {
  return (
    <div>
      <div className="mb-2 text-xs uppercase tracking-[0.18em] text-white/45">{label}</div>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        rows={rows}
        className="w-full rounded-2xl border border-white/10 bg-[var(--bg)] p-3 text-sm text-white outline-none"
      />
    </div>
  );
}
