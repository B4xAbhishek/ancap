import * as SecureStore from "expo-secure-store";
import type {
  SmartPayExecution,
  SmartPayPaymentIntent,
  SmartPayQuote,
  SmartPayReceipt,
} from "@ancap/acp-api-client";
import type { SmartPayHistorySnapshotOrigin } from "./smart-pay-history";

const KEY_SMART_PAY_SESSION = "acp_wallet_smart_pay_session";
const DEFAULT_SMART_PAY_ASSET = "ACP";
const SMART_PAY_SELECTED_ASSET_CANONICALS = new Map<string, string>([
  ["acp", "ACP"],
  ["wacp", "wACP"],
  ["usdt", "USDT"],
]);

const STORE_OPTIONS: SecureStore.SecureStoreOptions = {
  keychainAccessible: SecureStore.WHEN_UNLOCKED_THIS_DEVICE_ONLY,
};

export type SmartPayPayloadSource = "camera" | "photo" | "paste" | "share" | "ocr";

const SMART_PAY_PAYLOAD_SOURCES: SmartPayPayloadSource[] = ["camera", "photo", "paste", "share", "ocr"];
const SMART_PAY_PARSE_METHODS = ["deterministic", "heuristic", "ai"] as const;
const SMART_PAY_INTENT_STATUSES = ["parsed", "unsupported", "needs_review", "rejected"] as const;
const SMART_PAY_NETWORKS = ["acp", "bsc", "base", "ethereum", "unknown"] as const;
const SMART_PAY_ASSET_KINDS = ["native", "erc20", "unknown"] as const;
const SMART_PAY_RECIPIENT_ADDRESS_TYPES = ["acp", "evm", "unknown"] as const;
const SMART_PAY_MEMO_TYPES = ["memo", "tag", "reference", "note"] as const;
const SMART_PAY_EXECUTION_STATUSES = ["awaiting_local_signature", "pending_reconciliation", "completed", "failed"] as const;
const SMART_PAY_QUOTE_MODES = ["direct_send", "swap_then_send"] as const;
const SMART_PAY_ROUTE_KINDS = ["bridge", "swap", "transfer"] as const;

function normalizeSmartPayPayloadSource(value: unknown): SmartPayPayloadSource {
  return typeof value === "string" && SMART_PAY_PAYLOAD_SOURCES.includes(value as SmartPayPayloadSource)
    ? (value as SmartPayPayloadSource)
    : "paste";
}

function normalizeRawPayload(value: unknown): string {
  return typeof value === "string" ? value : "";
}

function normalizeSelectedAsset(value: unknown): string {
  if (typeof value !== "string") {
    return DEFAULT_SMART_PAY_ASSET;
  }
  const trimmed = value.trim();
  if (!trimmed) {
    return DEFAULT_SMART_PAY_ASSET;
  }
  return SMART_PAY_SELECTED_ASSET_CANONICALS.get(trimmed.toLowerCase()) ?? trimmed;
}

function normalizeOptionalSessionToken(value: unknown): string | null {
  if (typeof value !== "string") {
    return null;
  }
  const trimmed = value.trim();
  return trimmed ? trimmed : null;
}

function normalizeSnapshotOrigin(value: unknown): SmartPayHistorySnapshotOrigin {
  return value === "backend"
    ? "backend"
    : value === "local+backend"
      ? "local+backend"
      : "local";
}

function normalizeRecoveryDraftTxs(value: unknown): string {
  return typeof value === "string" ? value : "";
}

function normalizeOptionalString(value: unknown): string | null {
  return typeof value === "string" ? value : null;
}

function normalizeRequiredString(value: unknown, fallback = ""): string {
  return typeof value === "string" ? value : fallback;
}

function normalizeStringArray(value: unknown): string[] {
  return Array.isArray(value)
    ? value.filter((item): item is string => typeof item === "string")
    : [];
}

function normalizeFiniteInteger(value: unknown, minimum = 0): number | null {
  let numeric: number | null = null;

  if (typeof value === "number" && Number.isFinite(value)) {
    numeric = value;
  } else if (typeof value === "string") {
    const trimmed = value.trim();
    if (/^-?\d+$/.test(trimmed)) {
      numeric = Number.parseInt(trimmed, 10);
    }
  }

  if (numeric === null || !Number.isInteger(numeric) || numeric < minimum) {
    return null;
  }

  return numeric;
}

function normalizeFiniteNumber(value: unknown, fallback = 0): number {
  return typeof value === "number" && Number.isFinite(value) ? value : fallback;
}

function inferSmartPayNetworkFromExplorerUrl(value: string): string | null {
  try {
    const url = new URL(value);
    const hostname = url.hostname.toLowerCase();
    const pathname = url.pathname.toLowerCase();

    if (hostname.includes("bscscan.com")) {
      return "bsc";
    }
    if (hostname.includes("basescan.org")) {
      return "base";
    }
    if (hostname === "etherscan.io" || hostname.endsWith(".etherscan.io")) {
      return "ethereum";
    }
    if (hostname.includes("ancap.cloud") && (pathname.includes("/acp/tx") || pathname.includes("/acp/transactions"))) {
      return "acp";
    }
  } catch {
    return null;
  }

  return null;
}

function normalizeEnumValue<T extends readonly string[]>(value: unknown, allowed: T, fallback: T[number]): T[number] {
  return typeof value === "string" && allowed.includes(value as T[number])
    ? (value as T[number])
    : fallback;
}

function normalizeSmartPayTxRefs(refs: unknown): SmartPayExecution["txRefs"] {
  if (!Array.isArray(refs)) {
    return [];
  }

  return refs.flatMap((ref) => {
    if (!ref || typeof ref !== "object" || typeof (ref as { txid?: unknown }).txid !== "string") {
      return [];
    }

    const candidate = ref as {
      role?: unknown;
      network?: unknown;
      txid: string;
      explorerUrl?: unknown;
      routeStepIndex?: unknown;
    };
    const txid = candidate.txid.trim();
    if (!txid) {
      return [];
    }

    const explorerUrl = typeof candidate.explorerUrl === "string" ? candidate.explorerUrl.trim() || null : null;
    const normalizedNetwork = typeof candidate.network === "string" ? candidate.network.trim() : "";

    const normalizedRef: SmartPayExecution["txRefs"][number] = {
      role: normalizeRequiredString(candidate.role),
      network: normalizedNetwork || inferSmartPayNetworkFromExplorerUrl(explorerUrl ?? "") || "",
      txid,
      explorerUrl,
    };

    const routeStepIndex = normalizeFiniteInteger(candidate.routeStepIndex, 1);
    if (routeStepIndex !== null) {
      normalizedRef.routeStepIndex = routeStepIndex;
    }

    return [normalizedRef];
  });
}

function normalizeSmartPayExecutionProgress(progress: unknown): SmartPayExecution["progress"] | null {
  if (!progress || typeof progress !== "object") {
    return null;
  }

  const candidate = progress as {
    totalRouteSteps?: unknown;
    observedTxCount?: unknown;
    remainingRouteSteps?: unknown;
    pendingRoles?: unknown;
  };

  return {
    totalRouteSteps: normalizeFiniteInteger(candidate.totalRouteSteps) ?? 0,
    observedTxCount: normalizeFiniteInteger(candidate.observedTxCount) ?? 0,
    remainingRouteSteps: normalizeFiniteInteger(candidate.remainingRouteSteps) ?? 0,
    pendingRoles: Array.isArray(candidate.pendingRoles)
      ? candidate.pendingRoles.filter((role): role is string => typeof role === "string" && role.trim().length > 0)
      : [],
  };
}

function normalizeSmartPayIntent(intent: SmartPayPaymentIntent | null | undefined): SmartPayPaymentIntent | null {
  if (!intent || typeof intent !== "object" || !intent.asset || !intent.recipient) {
    return null;
  }

  return {
    ...intent,
    id: normalizeRequiredString(intent.id),
    createdAt: normalizeRequiredString(intent.createdAt),
    source: normalizeSmartPayPayloadSource(intent.source),
    rawPayload: normalizeRequiredString(intent.rawPayload),
    payloadHash: normalizeRequiredString(intent.payloadHash),
    parseMethod: normalizeEnumValue(intent.parseMethod, SMART_PAY_PARSE_METHODS, "deterministic"),
    confidence: normalizeFiniteNumber(intent.confidence, 0),
    status: normalizeEnumValue(intent.status, SMART_PAY_INTENT_STATUSES, "needs_review"),
    network: normalizeEnumValue(intent.network, SMART_PAY_NETWORKS, "unknown"),
    asset: {
      ...intent.asset,
      kind: normalizeEnumValue(intent.asset.kind, SMART_PAY_ASSET_KINDS, "unknown"),
      symbol: normalizeOptionalString(intent.asset.symbol),
      name: normalizeOptionalString(intent.asset.name),
      tokenAddress: normalizeOptionalString(intent.asset.tokenAddress),
      decimals: normalizeFiniteInteger(intent.asset.decimals ?? null, 0),
      isSupported: Boolean(intent.asset.isSupported),
      isAllowlisted: Boolean(intent.asset.isAllowlisted),
    },
    recipient: {
      ...intent.recipient,
      address: normalizeRequiredString(intent.recipient.address),
      resolvedDisplay: normalizeOptionalString(intent.recipient.resolvedDisplay),
      addressType: normalizeEnumValue(intent.recipient.addressType, SMART_PAY_RECIPIENT_ADDRESS_TYPES, "unknown"),
      checksumValid: typeof intent.recipient.checksumValid === "boolean" ? intent.recipient.checksumValid : null,
      ensOrAlias: normalizeOptionalString(intent.recipient.ensOrAlias),
    },
    amount:
      intent.amount && typeof intent.amount === "object"
        ? {
            ...intent.amount,
            value: normalizeRequiredString(intent.amount.value),
            atomicValue: normalizeOptionalString(intent.amount.atomicValue),
            currencySymbol: normalizeOptionalString(intent.amount.currencySymbol),
            isExact: Boolean(intent.amount.isExact),
            isMax: Boolean(intent.amount.isMax),
          }
        : null,
    memo:
      intent.memo && typeof intent.memo === "object"
        ? {
            ...intent.memo,
            value: normalizeRequiredString(intent.memo.value),
            type: normalizeEnumValue(intent.memo.type, SMART_PAY_MEMO_TYPES, "memo"),
            required: Boolean(intent.memo.required),
          }
        : null,
    merchant:
      intent.merchant && typeof intent.merchant === "object"
        ? {
            ...intent.merchant,
            label: normalizeOptionalString(intent.merchant.label),
            category: normalizeOptionalString(intent.merchant.category),
            website: normalizeOptionalString(intent.merchant.website),
            invoiceId: normalizeOptionalString(intent.merchant.invoiceId),
          }
        : null,
    riskFlags: normalizeStringArray(intent.riskFlags),
    warnings: normalizeStringArray(intent.warnings),
    unsupportedReasons: normalizeStringArray(intent.unsupportedReasons),
    requiresUserConfirmation: Boolean(intent.requiresUserConfirmation),
    metadata:
      intent.metadata && typeof intent.metadata === "object"
        ? {
            ...intent.metadata,
            detectedStandard: normalizeOptionalString(intent.metadata.detectedStandard),
            invoiceType: normalizeOptionalString(intent.metadata.invoiceType),
            aiModel: normalizeOptionalString(intent.metadata.aiModel),
            aiUsed: Boolean(intent.metadata.aiUsed),
            parserVersion: normalizeRequiredString(intent.metadata.parserVersion, "unknown"),
          }
        : {
            detectedStandard: null,
            invoiceType: null,
            aiModel: null,
            aiUsed: false,
            parserVersion: "unknown",
          },
  };
}

function normalizeSmartPayQuote(quote: SmartPayQuote | null | undefined): SmartPayQuote | null {
  if (!quote || typeof quote !== "object" || !quote.sourceAsset || !quote.targetAsset) {
    return null;
  }

  return {
    ...quote,
    quoteId: normalizeRequiredString(quote.quoteId),
    paymentIntentId: normalizeRequiredString(quote.paymentIntentId),
    mode: normalizeEnumValue(quote.mode, SMART_PAY_QUOTE_MODES, "direct_send"),
    expiresAt: normalizeRequiredString(quote.expiresAt),
    sourceAsset: {
      ...quote.sourceAsset,
      network: normalizeRequiredString(quote.sourceAsset.network),
      symbol: normalizeRequiredString(quote.sourceAsset.symbol),
      tokenAddress: normalizeOptionalString(quote.sourceAsset.tokenAddress),
      decimals: normalizeFiniteInteger(quote.sourceAsset.decimals ?? null, 0),
    },
    targetAsset: {
      ...quote.targetAsset,
      network: normalizeRequiredString(quote.targetAsset.network),
      symbol: normalizeRequiredString(quote.targetAsset.symbol),
      tokenAddress: normalizeOptionalString(quote.targetAsset.tokenAddress),
      decimals: normalizeFiniteInteger(quote.targetAsset.decimals ?? null, 0),
    },
    targetAmount: normalizeRequiredString(quote.targetAmount),
    requiredSourceAmount: normalizeRequiredString(quote.requiredSourceAmount),
    serviceFeeAcp: normalizeRequiredString(quote.serviceFeeAcp),
    networkFee: Array.isArray(quote.networkFee)
      ? quote.networkFee.filter(
          (fee): fee is SmartPayQuote["networkFee"][number] =>
            Boolean(
              fee
              && typeof fee === "object"
              && typeof (fee as { network?: unknown }).network === "string"
              && typeof (fee as { assetSymbol?: unknown }).assetSymbol === "string"
              && typeof (fee as { amount?: unknown }).amount === "string"
            )
        )
      : [],
    slippageBps: normalizeFiniteInteger(quote.slippageBps, 0) ?? 0,
    route: Array.isArray(quote.route)
      ? quote.route.filter(
          (step): step is SmartPayQuote["route"][number] =>
            Boolean(
              step
              && typeof step === "object"
              && typeof (step as { network?: unknown }).network === "string"
              && typeof (step as { fromAsset?: unknown }).fromAsset === "string"
              && typeof (step as { toAsset?: unknown }).toAsset === "string"
              && typeof (step as { estimatedOut?: unknown }).estimatedOut === "string"
            )
        ).map((step) => ({
          ...step,
          kind: normalizeEnumValue(step.kind, SMART_PAY_ROUTE_KINDS, "transfer"),
          network: normalizeRequiredString(step.network),
          dexOrRail: normalizeOptionalString(step.dexOrRail),
          fromAsset: normalizeRequiredString(step.fromAsset),
          toAsset: normalizeRequiredString(step.toAsset),
          estimatedOut: normalizeRequiredString(step.estimatedOut),
        }))
      : [],
    warnings: normalizeStringArray(quote.warnings),
    riskFlags: normalizeStringArray(quote.riskFlags),
  };
}

function normalizeSmartPayExecution(execution: SmartPayExecution | null | undefined): SmartPayExecution | null {
  if (!execution || typeof execution !== "object" || !Array.isArray((execution as { txRefs?: unknown }).txRefs)) {
    return null;
  }

  return {
    ...execution,
    id: normalizeRequiredString(execution.id),
    paymentIntentId: normalizeRequiredString(execution.paymentIntentId),
    quoteId: normalizeRequiredString(execution.quoteId),
    status: normalizeEnumValue(execution.status, SMART_PAY_EXECUTION_STATUSES, "failed"),
    createdAt: normalizeRequiredString(execution.createdAt),
    updatedAt: normalizeRequiredString(execution.updatedAt),
    recoverable: Boolean(execution.recoverable),
    nextAction: typeof execution.nextAction === "string" ? execution.nextAction : null,
    progress: normalizeSmartPayExecutionProgress(execution.progress),
    txRefs: normalizeSmartPayTxRefs(execution.txRefs),
    error: typeof execution.error === "string" ? execution.error : null,
  };
}

function normalizeSmartPayReceipt(receipt: SmartPayReceipt | null | undefined): SmartPayReceipt | null {
  if (!receipt || typeof receipt !== "object") {
    return null;
  }

  return {
    ...receipt,
    id: normalizeRequiredString(receipt.id),
    paymentExecutionId: normalizeRequiredString(receipt.paymentExecutionId),
    paymentIntentId: normalizeRequiredString(receipt.paymentIntentId),
    completedAt: normalizeOptionalString(receipt.completedAt),
    sourceAssetSpent: normalizeRequiredString(receipt.sourceAssetSpent),
    sourceAmountSpent: normalizeRequiredString(receipt.sourceAmountSpent),
    targetAssetPaid: normalizeRequiredString(receipt.targetAssetPaid),
    targetAmountPaid: normalizeRequiredString(receipt.targetAmountPaid),
    serviceFeeAcp: normalizeRequiredString(receipt.serviceFeeAcp),
    networkFees: Array.isArray(receipt.networkFees)
      ? receipt.networkFees.filter(
          (fee): fee is SmartPayReceipt["networkFees"][number] =>
            Boolean(
              fee
              && typeof fee === "object"
              && typeof (fee as { network?: unknown }).network === "string"
              && typeof (fee as { assetSymbol?: unknown }).assetSymbol === "string"
              && typeof (fee as { amount?: unknown }).amount === "string"
            )
        )
      : [],
    recipientAddress: normalizeRequiredString(receipt.recipientAddress),
    merchantLabel: normalizeOptionalString(receipt.merchantLabel),
    routeSummary: normalizeStringArray(receipt.routeSummary),
    txRefs: normalizeSmartPayTxRefs(receipt.txRefs),
  };
}

function parsePersistedTimestamp(value: unknown): { value: string; timestamp: number } | null {
  if (typeof value !== "string") {
    return null;
  }

  const trimmed = value.trim();
  if (!trimmed) {
    return null;
  }

  const timestamp = Date.parse(trimmed);
  if (Number.isNaN(timestamp)) {
    return null;
  }

  return { value: trimmed, timestamp };
}

function deriveSessionSavedAt(
  session: Partial<Pick<PersistedSmartPaySession, "savedAt" | "intent" | "execution" | "receipt">>
): string {
  const candidates = [
    parsePersistedTimestamp(session.savedAt),
    parsePersistedTimestamp(session.execution?.updatedAt),
    parsePersistedTimestamp(session.execution?.createdAt),
    parsePersistedTimestamp(session.receipt?.completedAt),
    parsePersistedTimestamp(session.intent?.createdAt),
  ];

  const best = candidates.reduce<{ value: string; timestamp: number } | null>((current, candidate) => {
    if (!candidate) {
      return current;
    }
    if (!current || candidate.timestamp > current.timestamp) {
      return candidate;
    }
    return current;
  }, null);

  return best?.value ?? new Date().toISOString();
}

export type PersistedSmartPaySession = {
  version: 1;
  rawPayload: string;
  payloadSource: SmartPayPayloadSource;
  selectedAsset: string;
  intent: SmartPayPaymentIntent | null;
  quote: SmartPayQuote | null;
  execution: SmartPayExecution | null;
  receipt: SmartPayReceipt | null;
  sessionToken: string | null;
  snapshotOrigin: SmartPayHistorySnapshotOrigin;
  recoveryDraftTxs: string;
  savedAt: string;
};

export async function loadSmartPaySession(): Promise<PersistedSmartPaySession | null> {
  const raw = await SecureStore.getItemAsync(KEY_SMART_PAY_SESSION, STORE_OPTIONS);
  if (!raw) return null;

  try {
    const parsed = JSON.parse(raw) as PersistedSmartPaySession;
    if (parsed?.version !== 1) {
      await clearSmartPaySession();
      return null;
    }
    return {
      ...parsed,
      savedAt: deriveSessionSavedAt(parsed),
      rawPayload: normalizeRawPayload(parsed.rawPayload),
      payloadSource: normalizeSmartPayPayloadSource(parsed.payloadSource),
      selectedAsset: normalizeSelectedAsset(parsed.selectedAsset),
      intent: normalizeSmartPayIntent(parsed.intent),
      quote: normalizeSmartPayQuote(parsed.quote),
      execution: normalizeSmartPayExecution(parsed.execution),
      receipt: normalizeSmartPayReceipt(parsed.receipt),
      sessionToken: normalizeOptionalSessionToken(parsed.sessionToken),
      snapshotOrigin: normalizeSnapshotOrigin(parsed.snapshotOrigin),
      recoveryDraftTxs: normalizeRecoveryDraftTxs(parsed.recoveryDraftTxs),
    };
  } catch {
    await clearSmartPaySession();
    return null;
  }
}

export async function saveSmartPaySession(
  session: Omit<PersistedSmartPaySession, "version" | "savedAt" | "snapshotOrigin" | "recoveryDraftTxs"> & {
    savedAt?: string;
    snapshotOrigin?: SmartPayHistorySnapshotOrigin;
    recoveryDraftTxs?: string;
  }
): Promise<void> {
  const payload: PersistedSmartPaySession = {
    version: 1,
    savedAt: deriveSessionSavedAt(session),
    rawPayload: normalizeRawPayload(session.rawPayload),
    payloadSource: normalizeSmartPayPayloadSource(session.payloadSource),
    selectedAsset: normalizeSelectedAsset(session.selectedAsset),
    intent: normalizeSmartPayIntent(session.intent),
    quote: normalizeSmartPayQuote(session.quote),
    execution: normalizeSmartPayExecution(session.execution),
    receipt: normalizeSmartPayReceipt(session.receipt),
    sessionToken: normalizeOptionalSessionToken(session.sessionToken),
    snapshotOrigin: normalizeSnapshotOrigin(session.snapshotOrigin),
    recoveryDraftTxs: normalizeRecoveryDraftTxs(session.recoveryDraftTxs),
  };
  await SecureStore.setItemAsync(KEY_SMART_PAY_SESSION, JSON.stringify(payload), STORE_OPTIONS);
}

export async function clearSmartPaySession(): Promise<void> {
  await SecureStore.deleteItemAsync(KEY_SMART_PAY_SESSION, STORE_OPTIONS);
}
