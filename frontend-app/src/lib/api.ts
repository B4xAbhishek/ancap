// Prefer an explicit URL if provided.
// Fallbacks:
// - development: same-origin /api/v1 (proxied to localhost:8001/v1 by next.config.ts)
// - production without override: ancap.cloud API gateway
//
// Important: CI/local production-like builds intentionally pass a loopback
// NEXT_PUBLIC_API_URL (for example 127.0.0.1:8001). Respect it instead of
// silently falling back to ancap.cloud, otherwise auth/UI tests talk to the
// wrong backend.
const rawApiBase = process.env.NEXT_PUBLIC_API_URL;

// Dev uses Next rewrite → local API. Production defaults to the dedicated API
// host because an upstream edge strips /api on ancap.cloud before origin nginx.
const API_BASE =
  rawApiBase ||
  (process.env.NODE_ENV === "development"
    ? "/api/v1"
    : "https://api.ancap.cloud/v1");

/** Resolved client-side API base URL (e.g. "/api/v1" in dev). */
export function getApiUrl(): string {
  return API_BASE;
}

const TOKEN_COOKIE = "ancap_token";
const SAME_ORIGIN_REQUEST_HEADER = "XMLHttpRequest";

function genIdempotencyKey(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    // @ts-ignore - lib dom typing may vary
    return crypto.randomUUID();
  }
  return `${Date.now()}-${Math.random().toString(16).slice(2)}-${Math.random().toString(16).slice(2)}`;
}

// Token management — token is stored in an HttpOnly cookie set by the backend.
// Client-side read only (no JS write — HttpOnly prevents it anyway).
function getToken(): string | null {
  if (typeof document === "undefined") return null;
  const match = document.cookie.match(
    new RegExp("(?:^|; )" + TOKEN_COOKIE.replace(/([$*+?.()|[\]{}\\])/g, "\\$1") + "=([^;]*)")
  );
  return match ? decodeURIComponent(match[1]) : null;
}

// setToken/clearToken are no-ops — cookie is managed exclusively by the backend.
// Kept as no-ops so existing callers (tests / edge cases) do not break.
function setToken(_token: string): void {
  // intentional no-op
}
function clearToken(): void {
  // intentional no-op; logout calls /auth/logout which clears the cookie server-side
}

// Base fetch wrapper with auth
export class ApiError extends Error {
  status: number;
  code?: string;
  detail?: unknown;

  constructor(message: string, status: number, options?: { code?: string; detail?: unknown }) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = options?.code;
    this.detail = options?.detail;
  }
}

function getApiHeaders(options: RequestInit = {}, includeJsonContentType = true): HeadersInit {
  const token = getToken();
  return {
    ...(includeJsonContentType ? { "Content-Type": "application/json" } : {}),
    "X-Requested-With": SAME_ORIGIN_REQUEST_HEADER,
    ...options.headers,
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

/** Normalize browser network/CORS failures into a stable operator-facing message. */
export function formatNetworkError(err: unknown): Error {
  const raw = err instanceof Error ? err.message : String(err || "");
  const lower = raw.toLowerCase();
  const name = err instanceof Error ? err.name : "";
  if (
    name === "TimeoutError" ||
    name === "AbortError" ||
    lower.includes("signal timed out") ||
    lower.includes("the operation was aborted") ||
    lower.includes("aborted due to timeout")
  ) {
    return new Error(
      "Request timed out waiting for the ACP chain. Wait a moment and retry — signed spends can take up to a few minutes.",
    );
  }
  if (
    err instanceof TypeError ||
    lower.includes("failed to fetch") ||
    lower.includes("networkerror") ||
    lower.includes("load failed") ||
    lower.includes("network request failed")
  ) {
    return new Error(
      "Could not reach the ANCAP API (network cut or edge timeout). Retry — long ACP chain spends are queued server-side and polled until done.",
    );
  }
  return err instanceof Error ? err : new Error(raw || "Request failed");
}

const DEFAULT_CLIENT_TIMEOUT_MS = 45_000;
// Operator hot UTXO probes can exceed 12s; keep below server 40s hot timeout.
const BALANCE_CLIENT_TIMEOUT_MS = 45_000;
// Signed ACP transfers wait on walletd (server timeout 180s) + RPC confirmation.
const CHAIN_WRITE_CLIENT_TIMEOUT_MS = 210_000;

async function apiFetchRaw(path: string, options: RequestInit = {}, includeJsonContentType = true) {
  try {
    const signal =
      options.signal ??
      (typeof AbortSignal !== "undefined" && "timeout" in AbortSignal
        ? AbortSignal.timeout(DEFAULT_CLIENT_TIMEOUT_MS)
        : undefined);
    return await fetch(`${API_BASE}${path}`, {
      ...options,
      headers: getApiHeaders(options, includeJsonContentType),
      credentials: "include",
      ...(signal ? { signal } : {}),
    });
  } catch (err) {
    throw formatNetworkError(err);
  }
}

export async function apiFetch(path: string, options: RequestInit = {}) {
  const res = await apiFetchRaw(path, options);

  if (!res.ok) {
    let detail = "";
    let detailPayload: unknown = undefined;
    let errorCode = "";
    try {
      const maybeJson = await res.json();
      detailPayload = maybeJson?.detail;
      if (typeof maybeJson?.detail === "string") {
        detail = maybeJson.detail.trim();
      } else if (maybeJson?.detail && typeof maybeJson.detail === "object") {
        const structuredDetail = maybeJson.detail as { code?: unknown; message?: unknown };
        if (typeof structuredDetail.code === "string") {
          errorCode = structuredDetail.code.trim();
        }
        if (typeof structuredDetail.message === "string") {
          detail = structuredDetail.message.trim();
        }
      }
      if (!detail) {
        detail = String(maybeJson?.message || "").trim();
      }
    } catch {
      // If upstream/proxy returns HTML/plain text, expose short readable snippet.
      const raw = (await res.text().catch(() => "")).trim();
      if (raw) {
        detail = raw
          .replace(/\s+/g, " ")
          .replace(/<[^>]+>/g, "")
          .slice(0, 180)
          .trim();
      }
    }
    const baseMessage = `API error ${res.status}${res.statusText ? ` ${res.statusText}` : ""}`;
    throw new ApiError(detail ? `${baseMessage}: ${detail}` : baseMessage, res.status, {
      code: errorCode || undefined,
      detail: detailPayload,
    });
  }

  if (res.status === 204) {
    return null;
  }

  const contentLength = res.headers.get("content-length");
  if (contentLength === "0") {
    return null;
  }

  const contentType = (res.headers.get("content-type") || "").toLowerCase();
  const rawBody = await res.text();
  if (!rawBody.trim()) {
    return null;
  }

  if (contentType.includes("application/json") || contentType.includes("+json")) {
    return JSON.parse(rawBody);
  }

  return rawBody;
}

// Auth API
export const auth = {
  async login(email: string, password: string, turnstileToken?: string) {
    const data = await apiFetch("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password, turnstile_token: turnstileToken }),
    });
    setToken(data.access_token);
    return data;
  },

  async walletNonce(address: string, chain_id?: number, domain?: string, uri?: string, turnstileToken?: string) {
    return apiFetch("/auth/wallet/nonce", {
      method: "POST",
      body: JSON.stringify({ address, chain_id, domain, uri, turnstile_token: turnstileToken }),
    });
  },

  async walletVerify(challenge_id: string, address: string, signature: string) {
    const data = await apiFetch("/auth/wallet/verify", {
      method: "POST",
      body: JSON.stringify({ challenge_id, address, signature }),
    });
    setToken(data.access_token);
    return data;
  },

  async walletLink(challenge_id: string, address: string, signature: string) {
    return apiFetch("/auth/wallet/link", {
      method: "POST",
      body: JSON.stringify({ challenge_id, address, signature }),
    });
  },

  async forgotPassword(email: string, turnstileToken?: string) {
    return apiFetch("/auth/password/forgot", {
      method: "POST",
      body: JSON.stringify({ email, turnstile_token: turnstileToken }),
    });
  },

  async resetPassword(token: string, password: string, turnstileToken?: string) {
    return apiFetch("/auth/password/reset", {
      method: "POST",
      body: JSON.stringify({ token, password, turnstile_token: turnstileToken }),
    });
  },

  async recoverPasswordWithWallet(challenge_id: string, address: string, signature: string, newPassword: string) {
    return apiFetch("/auth/password/recover-with-wallet", {
      method: "POST",
      body: JSON.stringify({ challenge_id, address, signature, new_password: newPassword }),
    });
  },

  async changePassword(currentPassword: string, newPassword: string) {
    return apiFetch("/auth/password/change", {
      method: "POST",
      body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
    });
  },

  async register(email: string, password: string, display_name: string, referral_code?: string, turnstileToken?: string) {
    const data = await apiFetch("/auth/users", {
      method: "POST",
      body: JSON.stringify({ email, password, display_name, referral_code, turnstile_token: turnstileToken }),
    });
    if (data?.access_token) {
      setToken(data.access_token);
    }
    return data;
  },

  async logout() {
    clearToken();
    try {
      await apiFetchRaw("/auth/logout", {
        method: "POST",
        body: "{}",
      });
    } catch {
      // best-effort
    }
    // Also clear cookie client-side for immediate effect (non-HttpOnly leftovers only).
    if (typeof document !== "undefined") {
      document.cookie = `${TOKEN_COOKIE}=; Max-Age=0; path=/; SameSite=Lax`;
      document.cookie = `${TOKEN_COOKIE}=; Max-Age=0; path=/; domain=.ancap.cloud; SameSite=Lax`;
    }
  },

  isAuthenticated(): boolean {
    return !!getToken();
  },

  getToken,
};

export const users = {
  async me() {
    return apiFetch("/users/me");
  },
};

// Agents API
export const agents = {
  async list(limit = 50, cursor?: string) {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (cursor) params.append("cursor", cursor);
    return apiFetch(`/agents?${params}`);
  },

  async listMine(limit = 50, cursor?: string) {
    const params = new URLSearchParams({ limit: limit.toString(), mine: "true" });
    if (cursor) params.append("cursor", cursor);
    return apiFetch(`/agents?${params}`);
  },

  async get(id: string) {
    return apiFetch(`/agents/${id}`);
  },

  async create(data: {
    display_name: string;
    public_key: string;
    roles: string[];
    metadata?: Record<string, any>;
    attestation_id?: string;
  }) {
    return apiFetch("/agents", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async getGraphMetrics(id: string) {
    return apiFetch(`/agents/${id}/graph-metrics`);
  },
};

// Strategies API
export const strategies = {
  async list(limit = 50, cursor?: string) {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (cursor) params.append("cursor", cursor);
    return apiFetch(`/strategies?${params}`);
  },

  async get(id: string) {
    return apiFetch(`/strategies/${id}`);
  },

  async create(data: {
    name: string;
    description?: string;
    owner_agent_id: string;
    vertical_id: string;
    summary?: string;
    tags?: string[];
  }) {
    return apiFetch("/strategies", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async getVersions(id: string, limit = 50) {
    return apiFetch(`/strategies/${id}/versions?limit=${limit}`);
  },

  async createVersion(strategyId: string, data: {
    semver: string;
    workflow: Record<string, any>;
    param_schema?: Record<string, any>;
    changelog?: string;
    strategy_policy?: Record<string, any>;
  }) {
    return apiFetch(`/strategies/${strategyId}/versions`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
};

export const strategyVersions = {
  async get(id: string) {
    return apiFetch(`/strategy-versions/${id}`);
  },
};

// Runs API
export const runs = {
  async list(limit = 50, cursor?: string) {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (cursor) params.append("cursor", cursor);
    return apiFetch(`/runs?${params}`);
  },

  async get(id: string) {
    return apiFetch(`/runs/${id}`);
  },

  async create(data: {
    strategy_version_id: string;
    pool_id: string;
    contract_id?: string;
    contract_milestone_id?: string;
    params?: Record<string, any>;
    limits?: Record<string, any>;
    dry_run?: boolean;
    run_mode?: "mock" | "backtest";
    idempotency_key?: string;
  }) {
    const idk = data.idempotency_key || genIdempotencyKey();
    return apiFetch("/runs", {
      method: "POST",
      headers: {
        "Idempotency-Key": idk,
      },
      body: JSON.stringify(data),
    });
  },

  async getLogs(id: string) {
    return apiFetch(`/runs/${id}/logs`);
  },

  async getSteps(id: string) {
    return apiFetch(`/runs/${id}/steps`);
  },

  async getArtifacts(id: string) {
    return apiFetch(`/runs/${id}/artifacts`);
  },
};

// Pools API
export const pools = {
  async list(limit = 50, cursor?: string) {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (cursor) params.append("cursor", cursor);
    return apiFetch(`/pools?${params}`);
  },

  async get(id: string) {
    return apiFetch(`/pools/${id}`);
  },

  async create(data: {
    name: string;
    description?: string;
    vertical_id: string;
    policy_json?: Record<string, any>;
  }) {
    return apiFetch("/pools", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
};

// Verticals API
export const verticals = {
  async list() {
    return apiFetch("/verticals");
  },

  async get(id: string) {
    return apiFetch(`/verticals/${id}`);
  },

  async propose(data: {
    name: string;
    spec: {
      description: string;
      allowed_actions: any[];
      required_resources: any[];
      metrics: any[];
      risk_spec: Record<string, any>;
    };
  }) {
    return apiFetch("/verticals/propose", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
};

// Ledger API
export const ledger = {
  async getAccounts(limit = 50) {
    return apiFetch(`/ledger/accounts?limit=${limit}`);
  },

  async getAccount(id: string) {
    return apiFetch(`/ledger/accounts/${id}`);
  },

  async getEvents(accountId?: string, limit = 50) {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (accountId) params.append("account_id", accountId);
    return apiFetch(`/ledger/events?${params}`);
  },

  async getBalance(owner_type: string, owner_id: string) {
    const params = new URLSearchParams({ owner_type, owner_id });
    return apiFetch(`/ledger/balance?${params}`);
  },

  async deposit(data: {
    account_id: string;
    amount: string;
    currency: string;
    idempotency_key: string;
  }) {
    return apiFetch("/ledger/deposit", {
      method: "POST",
      headers: {
        "Idempotency-Key": data.idempotency_key,
      },
      body: JSON.stringify({
        account_id: data.account_id,
        amount: data.amount,
        currency: data.currency,
      }),
    });
  },
};

// ACP Wallet API
export const spaceAuction = {
  async catalog() {
    return apiFetch("/space-auction/catalog");
  },
  async lot(lotId: string) {
    return apiFetch(`/space-auction/lots/${encodeURIComponent(lotId)}`);
  },
  async bid(lotId: string, data: { amount_acp: string; note?: string }) {
    return apiFetch(`/space-auction/lots/${encodeURIComponent(lotId)}/bids`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
};

export const darkMatterAuction = {
  async catalog() {
    return apiFetch("/dark-matter-auction/catalog");
  },
  async lot(lotId: string) {
    return apiFetch(`/dark-matter-auction/lots/${encodeURIComponent(lotId)}`);
  },
  async bid(lotId: string, data: { amount_acp: string; note?: string }) {
    return apiFetch(`/dark-matter-auction/lots/${encodeURIComponent(lotId)}/bids`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
};

export const animalAuction = {
  async catalog() {
    return apiFetch("/animal-auction/catalog");
  },
  async lot(lotId: string) {
    return apiFetch(`/animal-auction/lots/${encodeURIComponent(lotId)}`);
  },
  async list(data: {
    species: string;
    name: string;
    breed: string;
    age_months?: number | null;
    blurb: string;
    starting_acp: string;
    license_acknowledged: boolean;
  }) {
    return apiFetch("/animal-auction/lots", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
  async bid(lotId: string, data: { amount_acp: string; note?: string }) {
    return apiFetch(`/animal-auction/lots/${encodeURIComponent(lotId)}/bids`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
};

export const floraAuction = {
  async catalog() {
    return apiFetch("/flora-auction/catalog");
  },
  async lot(lotId: string) {
    return apiFetch(`/flora-auction/lots/${encodeURIComponent(lotId)}`);
  },
  async list(data: {
    form: string;
    name: string;
    variety: string;
    quantity?: number | null;
    blurb: string;
    starting_acp: string;
    image_href?: string | null;
    license_acknowledged: boolean;
  }) {
    return apiFetch("/flora-auction/lots", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
  async bid(lotId: string, data: { amount_acp: string; note?: string }) {
    return apiFetch(`/flora-auction/lots/${encodeURIComponent(lotId)}/bids`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
};

export const techAuction = {
  async catalog() {
    return apiFetch("/tech-auction/catalog");
  },
  async lot(lotId: string) {
    return apiFetch(`/tech-auction/lots/${encodeURIComponent(lotId)}`);
  },
  async list(data: {
    category: string;
    title: string;
    stack: string;
    blurb: string;
    starting_acp: string;
    license_acknowledged: boolean;
  }) {
    return apiFetch("/tech-auction/lots", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
  async placeBid(lotId: string, data: { amount_acp: string; note?: string }) {
    return apiFetch(`/tech-auction/lots/${encodeURIComponent(lotId)}/bids`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
};

export const literaryAuction = {
  async catalog() {
    return apiFetch("/literary-auction/catalog");
  },
  async lot(lotId: string) {
    return apiFetch(`/literary-auction/lots/${encodeURIComponent(lotId)}`);
  },
  async list(data: {
    genre: string;
    title: string;
    author: string;
    blurb: string;
    starting_acp: string;
    rights_acknowledged: boolean;
  }) {
    return apiFetch("/literary-auction/lots", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
  async placeBid(lotId: string, data: { amount_acp: string; note?: string }) {
    return apiFetch(`/literary-auction/lots/${encodeURIComponent(lotId)}/bids`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
};

export const cryoDesk = {
  async catalog() {
    return apiFetch("/cryo/catalog");
  },
};

export const humanitarianDesk = {
  async catalog() {
    return apiFetch("/humanitarian/catalog");
  },
};

export const counselDesk = {
  async catalog() {
    return apiFetch("/counsel/catalog");
  },
};

export const starlinkInstallDesk = {
  async catalog() {
    return apiFetch("/starlink-install/catalog");
  },
  async quote(body: { service_id: string; region?: string | null; payment_currency?: string }) {
    return apiFetch("/starlink-install/quote", {
      method: "POST",
      body: JSON.stringify(body),
    });
  },
};

export const fieldServicesDesk = {
  async catalog(group?: string | null) {
    const q = group ? `?group=${encodeURIComponent(group)}` : "";
    return apiFetch(`/field-services/catalog${q}`);
  },
  async quote(body: { service_id: string; region?: string | null; payment_currency?: string }) {
    return apiFetch("/field-services/quote", {
      method: "POST",
      body: JSON.stringify(body),
    });
  },
};

export const quantumSimDesk = {
  async catalog() {
    return apiFetch("/quantum-sim/catalog");
  },
};

export const stardustDesk = {
  async catalog() {
    return apiFetch("/stardust/catalog");
  },
};

export const salivaRxDesk = {
  async catalog() {
    return apiFetch("/saliva-rx/catalog");
  },
};

export const startupInvestDesk = {
  async catalog() {
    return apiFetch("/startups/catalog");
  },
};

export const nexusSocial = {
  async catalog() {
    return apiFetch("/nexus/catalog");
  },
  async listPosts(limit = 50, parentId?: string) {
    const q = new URLSearchParams({ limit: String(limit) });
    if (parentId) q.set("parent_id", parentId);
    return apiFetch(`/nexus/posts?${q.toString()}`);
  },
  async createPost(data: { body: string; as_agent_id?: string; parent_id?: string }) {
    return apiFetch("/nexus/posts", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
};

export const serviceReviews = {
  async list(params: {
    target_type?: string;
    target_id?: string;
    reviewer_type?: string;
    limit?: number;
  }) {
    const q = new URLSearchParams();
    if (params.target_type) q.set("target_type", params.target_type);
    if (params.target_id) q.set("target_id", params.target_id);
    if (params.reviewer_type) q.set("reviewer_type", params.reviewer_type);
    if (params.limit) q.set("limit", String(params.limit));
    const suffix = q.toString() ? `?${q.toString()}` : "";
    return apiFetch(`/reviews${suffix}`);
  },
  async create(data: {
    reviewer_type: string;
    reviewer_id: string;
    target_type: string;
    target_id: string;
    rating?: number;
    text?: string;
    weight?: number;
  }) {
    return apiFetch("/reviews", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
  async createAi(data: {
    target_type: string;
    target_id: string;
    rating?: number;
    focus?: string;
  }) {
    return apiFetch("/reviews/ai", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
};

export const perimeterCleanupDesk = {
  async cipher() {
    return apiFetch("/perimeter-cleanup/cipher");
  },
  async catalog() {
    return apiFetch("/perimeter-cleanup/catalog");
  },
  async listJobs() {
    return apiFetch("/perimeter-cleanup/jobs");
  },
  async createJob(data: {
    service_id: string;
    contamination: string;
    site_label: string;
    perimeter_meters?: string;
    address_or_coords?: string;
    contact_hint?: string;
    schedule_window?: string;
    notes?: string;
    survey_json?: Record<string, unknown>;
  }) {
    return apiFetch("/perimeter-cleanup/jobs", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
  async getJob(jobId: string) {
    return apiFetch(`/perimeter-cleanup/jobs/${encodeURIComponent(jobId)}`);
  },
  async blastRadius() {
    return apiFetch("/perimeter-cleanup/blast-radius");
  },
  async jobBlastRadius(jobId: string) {
    return apiFetch(`/perimeter-cleanup/jobs/${encodeURIComponent(jobId)}/blast-radius`);
  },
};

export const insuranceDesk = {
  async catalog() {
    return apiFetch("/insurance/catalog");
  },
  async quote(data: {
    coverage_class: string;
    sum_insured_acp: string;
    term_days?: number;
    asset_ref_type?: string | null;
    asset_ref_id?: string | null;
  }) {
    return apiFetch("/insurance/quote", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
  async createPolicy(data: {
    coverage_class: string;
    sum_insured_acp: string;
    term_days?: number;
    asset_ref_type?: string | null;
    asset_ref_id?: string | null;
    note?: string | null;
  }) {
    return apiFetch("/insurance/policies", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
  async listPolicies() {
    return apiFetch("/insurance/policies");
  },
  async fileClaim(policyId: string, data: { amount_acp: string; note?: string; evidence?: Record<string, unknown> }) {
    return apiFetch(`/insurance/policies/${encodeURIComponent(policyId)}/claims`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
};

export const arenaDesk = {
  async catalog() {
    return apiFetch("/arena/catalog");
  },
  async placeBet(marketId: string, data: { side: "yes" | "no"; stake_acp: string }) {
    return apiFetch(`/arena/markets/${encodeURIComponent(marketId)}/bets`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
  async playHouse(data: { game: "coinflip" | "dice"; stake_acp: string; choice: string }) {
    return apiFetch("/arena/house/play", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
  async commitHouse(data: { game: "coinflip" | "dice"; stake_acp: string }) {
    return apiFetch("/arena/house/commit", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
  async revealHouse(data: { round_id: string; choice: string; client_seed: string }) {
    return apiFetch("/arena/house/reveal", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
};

export const exponentialGrowth = {
  async me() {
    return apiFetch("/growth/exponential");
  },
  async compound(data: { principal_acp: string; periods?: number }) {
    return apiFetch("/growth/exponential/compound", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
};

function balanceSignal(): AbortSignal | undefined {
  return typeof AbortSignal !== "undefined" && "timeout" in AbortSignal
    ? AbortSignal.timeout(BALANCE_CLIENT_TIMEOUT_MS)
    : undefined;
}

export const walletAcp = {
  async getDepositAddress() {
    // Prefer GET (cookie auth, no empty JSON body quirks). Fall back to POST for older gateways.
    try {
      return await apiFetch("/wallet/acp/deposit_address");
    } catch (err) {
      const status = err instanceof ApiError ? err.status : 0;
      if (status !== 405 && status !== 404) throw err;
      return apiFetch("/wallet/acp/deposit_address", {
        method: "POST",
        body: "{}",
      });
    }
  },

  async privacyStatus() {
    return apiFetch("/wallet/acp/privacy/status");
  },

  async privacyReceiveAddress(data?: { wallet_password?: string; label?: string }) {
    return apiFetch("/wallet/acp/privacy/receive-address", {
      method: "POST",
      body: JSON.stringify(data || {}),
    });
  },

  async personalizeWallet(data: { wallet_password: string }) {
    return apiFetch("/wallet/acp/personalize", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async getHotBalance() {
    const signal = balanceSignal();
    return apiFetch("/wallet/acp/hot/balance", signal ? { signal } : {});
  },

  async getBalance(params?: { address?: string }) {
    const qp = new URLSearchParams();
    if (params?.address) qp.append("address", params.address);
    const suffix = qp.toString();
    const signal = balanceSignal();
    return apiFetch(`/wallet/acp/balance${suffix ? `?${suffix}` : ""}`, signal ? { signal } : {});
  },

  async listTransactions(params?: { address?: string; limit?: number; privacy?: boolean }) {
    const qp = new URLSearchParams();
    if (params?.address) qp.append("address", params.address);
    if (params?.limit != null) qp.append("limit", String(params.limit));
    if (params?.privacy != null) qp.append("privacy", String(params.privacy));
    const suffix = qp.toString();
    return apiFetch(`/wallet/acp/transactions${suffix ? `?${suffix}` : ""}`);
  },

  async getTransaction(txid: string, privacy = true) {
    return apiFetch(
      `/wallet/acp/transactions/${encodeURIComponent(txid)}?privacy=${encodeURIComponent(String(privacy))}`
    );
  },

  async withdraw(data: { to_address: string; amount_acp: string; wallet_password: string; fee_acp?: string }, onQueued?: (jobId: string) => void) {
    const queued = await apiFetch("/wallet/acp/withdraw", {
      method: "POST",
      // Queue ack is fast; chain work continues server-side.
      signal:
        typeof AbortSignal !== "undefined" && "timeout" in AbortSignal
          ? AbortSignal.timeout(60_000)
          : undefined,
      body: JSON.stringify({
        to_address: data.to_address,
        amount_acp: data.amount_acp,
        fee_acp: data.fee_acp,
        wallet_password: data.wallet_password,
      }),
    });
    if (!queued || typeof queued !== "object") return queued;
    const jobId = typeof queued.job_id === "string" ? queued.job_id : "";
    if (queued.status !== "pending" || !jobId) return queued;
    onQueued?.(jobId);

    const started = Date.now();
    const maxWaitMs = CHAIN_WRITE_CLIENT_TIMEOUT_MS;
    while (Date.now() - started < maxWaitMs) {
      await new Promise((r) => setTimeout(r, 2000));
      const job = await apiFetch(`/wallet/acp/withdraw/jobs/${encodeURIComponent(jobId)}`, {
        signal:
          typeof AbortSignal !== "undefined" && "timeout" in AbortSignal
            ? AbortSignal.timeout(30_000)
            : undefined,
      });
      if (!job || typeof job !== "object") continue;
      if (job.status === "completed") {
        return {
          accepted: job.accepted ?? true,
          txid: job.txid ?? null,
          reason: job.reason ?? null,
          status: "completed",
          job_id: jobId,
        };
      }
      if (job.status === "failed") {
        throw new ApiError(String(job.error || job.reason || "Withdraw failed"), 502, {
          code: "withdraw_failed",
          detail: job,
        });
      }
    }
    throw new Error(
      "Withdraw is still processing on the ACP chain. Wait a minute, refresh history, and avoid resubmitting the same spend.",
    );
  },

  async getWithdrawJob(jobId: string) {
    return apiFetch(`/wallet/acp/withdraw/jobs/${encodeURIComponent(jobId)}`);
  },

  async swapQuote(data: { usdt_trc20_amount: string }) {
    return apiFetch("/wallet/acp/swap/quote", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async createSwapOrder(data: { usdt_trc20_amount: string; payout_acp_address: string; note?: string }) {
    return apiFetch("/wallet/acp/swap/orders", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async listSwapOrders() {
    return apiFetch("/wallet/acp/swap/orders");
  },

  async getSwapOrder(orderId: string) {
    return apiFetch(`/wallet/acp/swap/orders/${orderId}`);
  },

  async confirmSwapOrder(orderId: string, data: { tron_txid?: string }) {
    return apiFetch(`/wallet/acp/swap/orders/${orderId}/confirm`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async cancelSwapOrder(orderId: string) {
    return apiFetch(`/wallet/acp/swap/orders/${orderId}/cancel`, {
      method: "POST",
      body: JSON.stringify({}),
    });
  },

  async otcCatalog() {
    return apiFetch("/wallet/acp/otc/catalog");
  },

  async otcQuoteMetal(data: { metal: string; weight_grams: string; purity_ppt?: number }) {
    return apiFetch("/wallet/acp/otc/quote/metal", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async otcQuoteGoods(data: { category: string; estimated_value_acp: string }) {
    return apiFetch("/wallet/acp/otc/quote/goods", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async otcQuoteCommodity(data: { commodity: string; quantity: string; grade_note?: string }) {
    return apiFetch("/wallet/acp/otc/quote/commodity", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async otcQuoteRealEstate(data: {
    deal_type: string;
    estimated_value_acp: string;
    jurisdiction?: string;
    lease_months?: number;
  }) {
    return apiFetch("/wallet/acp/otc/quote/real-estate", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async otcQuoteSpace(data: {
    object_class: string;
    estimated_value_acp: string;
    norad_or_cospar_id?: string;
  }) {
    return apiFetch("/wallet/acp/otc/quote/space", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async otcQuoteIp(data: {
    kind: string;
    estimated_value_acp: string;
    registration_uri?: string;
  }) {
    return apiFetch("/wallet/acp/otc/quote/ip", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async ownershipCatalog() {
    return apiFetch("/ownership-proofs/catalog");
  },

  async issueOwnershipCertificate(data: Record<string, unknown>) {
    return apiFetch("/ownership-proofs/certificates", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async listOwnershipCertificates() {
    return apiFetch("/ownership-proofs/certificates");
  },

  async redeemOwnershipTransfer(data: { transfer_code: string; note?: string }) {
    return apiFetch("/ownership-proofs/transfers/redeem", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async createOtcOrder(data: Record<string, unknown>) {
    return apiFetch("/wallet/acp/otc/orders", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async listOtcOrders() {
    return apiFetch("/wallet/acp/otc/orders");
  },

  async confirmOtcOrder(orderId: string, data: { proof_ref?: string; note?: string }) {
    return apiFetch(`/wallet/acp/otc/orders/${orderId}/confirm`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async cancelOtcOrder(orderId: string) {
    return apiFetch(`/wallet/acp/otc/orders/${orderId}/cancel`, {
      method: "POST",
      body: JSON.stringify({}),
    });
  },

  async assayGcCatalog() {
    return apiFetch("/assay/gc/catalog");
  },

  async assayGcAnalyze(data: Record<string, unknown>) {
    return apiFetch("/assay/gc/analyze", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
};

/** wACP / BSC custodial clearing rail (see docs/bridge-spec-v1.md). */
export const bridgeRail = {
  async status() {
    return apiFetch("/bridge/status");
  },
  async reserveSummary() {
    return apiFetch("/bridge/reserve-summary");
  },
  async createIntentAcpToBsc(data: { user_bsc_address: string; amount_acp: string; user_acp_address?: string }) {
    return apiFetch("/bridge/intents/acp-to-bsc", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
  async createIntentBscToAcp(data: { user_bsc_address: string; user_acp_address: string; amount_wacp: string }) {
    return apiFetch("/bridge/intents/bsc-to-acp", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
  async quoteBscToAcp(data: { amount_wacp: string }) {
    return apiFetch("/bridge/quote/bsc-to-acp", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
  async listMyIntents(limit = 50) {
    return apiFetch(`/bridge/intents/me?limit=${encodeURIComponent(String(limit))}`);
  },
  async cancelIntent(operationId: string) {
    return apiFetch(`/bridge/intents/${encodeURIComponent(operationId)}/cancel`, {
      method: "POST",
    });
  },
};

export const stakes = {
  async list(agent_id?: string) {
    const params = new URLSearchParams();
    if (agent_id) params.append("agent_id", agent_id);
    const suffix = params.toString();
    return apiFetch(`/stakes${suffix ? `?${suffix}` : ""}`);
  },
  async create(data: { agent_id: string; amount: string; currency?: string }) {
    const params = new URLSearchParams({ agent_id: data.agent_id });
    return apiFetch(`/stakes/user/stake?${params.toString()}`, {
      method: "POST",
      body: JSON.stringify({ amount: data.amount, currency: data.currency || "ACP" }),
    });
  },
  async release(stake_id: string) {
    return apiFetch(`/stakes/user/${stake_id}/release`, {
      method: "POST",
      body: JSON.stringify({}),
    });
  },
};

// Reputation API
export const reputation = {
  async get(subjectType: string, subjectId: string, window = "90d") {
    return apiFetch(`/reputation?subject_type=${subjectType}&subject_id=${subjectId}&window=${window}`);
  },

  async getEvents(params: { subjectType: string; subjectId: string; limit?: number; cursor?: string }) {
    const limit = params.limit ?? 50;
    const qp = new URLSearchParams({
      subject_type: params.subjectType,
      subject_id: params.subjectId,
      limit: String(limit),
    });
    if (params.cursor) qp.append("cursor", params.cursor);
    return apiFetch(`/reputation/events?${qp.toString()}`);
  },
};

// Listings API
export const listings = {
  async list(limit = 50, cursor?: string, status?: string, strategy_id?: string) {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (cursor) params.append("cursor", cursor);
    if (status) params.append("status", status);
    if (strategy_id) params.append("strategy_id", strategy_id);
    return apiFetch(`/listings?${params}`);
  },

  async marketplace(params: {
    search?: string;
    category?: string;
    price_min?: string | number;
    price_max?: string | number;
    sort?: "popular" | "recent" | "price_asc" | "price_desc" | "rating";
    limit?: number;
    offset?: number;
  } = {}) {
    const qs = new URLSearchParams();
    if (params.search) qs.append("search", params.search);
    if (params.category) qs.append("category", params.category);
    if (params.price_min !== undefined) qs.append("price_min", String(params.price_min));
    if (params.price_max !== undefined) qs.append("price_max", String(params.price_max));
    if (params.sort) qs.append("sort", params.sort);
    if (params.limit !== undefined) qs.append("limit", String(params.limit));
    if (params.offset !== undefined) qs.append("offset", String(params.offset));
    const suffix = qs.toString();
    return apiFetch(`/listings/marketplace/listings${suffix ? `?${suffix}` : ""}`);
  },

  async get(id: string) {
    return apiFetch(`/listings/${id}`);
  },

  async create(data: {
    strategy_id: string;
    strategy_version_id: string;
    fee_model: Record<string, any>;
    status?: string;
    terms_url?: string;
    notes?: string;
  }) {
    return apiFetch("/listings", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
};

// Orders API
export const orders = {
  async list(limit = 50, cursor?: string, buyer_type?: string, buyer_id?: string) {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (cursor) params.append("cursor", cursor);
    if (buyer_type) params.append("buyer_type", buyer_type);
    if (buyer_id) params.append("buyer_id", buyer_id);
    return apiFetch(`/orders?${params}`);
  },

  async place(data: {
    listing_id: string;
    buyer_type: "user" | "agent" | "pool";
    buyer_id: string;
    payment_method?: string;
    note?: string;
    idempotency_key?: string;
  }) {
    const idk = data.idempotency_key || genIdempotencyKey();
    return apiFetch("/orders", {
      method: "POST",
      headers: {
        "Idempotency-Key": idk,
      },
      body: JSON.stringify(data),
    });
  },
};

// Access grants API
export const access = {
  async listGrants(limit = 50, cursor?: string, grantee_type?: string, grantee_id?: string) {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (cursor) params.append("cursor", cursor);
    if (grantee_type) params.append("grantee_type", grantee_type);
    if (grantee_id) params.append("grantee_id", grantee_id);
    return apiFetch(`/access/grants?${params}`);
  },
};

// Contracts API
export const contracts = {
  async list(limit = 50, cursor?: string, employer_agent_id?: string, worker_agent_id?: string, status?: string) {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (cursor) params.append("cursor", cursor);
    if (employer_agent_id) params.append("employer_agent_id", employer_agent_id);
    if (worker_agent_id) params.append("worker_agent_id", worker_agent_id);
    if (status) params.append("status", status);
    return apiFetch(`/contracts?${params}`);
  },

  async get(id: string) {
    return apiFetch(`/contracts/${id}`);
  },

  async getPayments(id: string) {
    return apiFetch(`/contracts/${id}/payments`);
  },

  async getRuns(id: string, limit = 50, cursor?: string) {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (cursor) params.append("cursor", cursor);
    return apiFetch(`/contracts/${id}/runs?${params}`);
  },

  async getActivity(id: string, limit = 200) {
    return apiFetch(`/contracts/${id}/activity?limit=${limit}`);
  },

  async create(data: {
    employer_agent_id: string;
    worker_agent_id: string;
    scope_type: string;
    scope_ref_id?: string | null;
    title: string;
    description?: string;
    payment_model: "fixed" | "per_run";
    fixed_amount_value?: string | null;
    currency?: string;
    max_runs?: number | null;
    risk_policy_id?: string | null;
    created_from_order_id?: string | null;
  }) {
    return apiFetch("/contracts", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async propose(id: string) {
    return apiFetch(`/contracts/${id}/propose`, { method: "POST" });
  },

  async accept(id: string) {
    return apiFetch(`/contracts/${id}/accept`, { method: "POST" });
  },

  async cancel(id: string) {
    return apiFetch(`/contracts/${id}/cancel`, { method: "POST" });
  },

  async complete(id: string) {
    return apiFetch(`/contracts/${id}/complete`, { method: "POST" });
  },

  async dispute(id: string) {
    return apiFetch(`/contracts/${id}/dispute`, { method: "POST" });
  },
};

// Contract milestones API
export const milestones = {
  async list(contractId: string, limit = 50, cursor?: string) {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (cursor) params.append("cursor", cursor);
    return apiFetch(`/milestones/contracts/${contractId}?${params}`);
  },

  async create(contractId: string, data: {
    title: string;
    description?: string;
    order_index?: number;
    amount_value: string;
    currency?: string;
    required_runs?: number | null;
  }) {
    return apiFetch(`/milestones/contracts/${contractId}`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async submit(id: string) {
    return apiFetch(`/milestones/${id}/submit`, { method: "POST" });
  },

  async accept(id: string) {
    return apiFetch(`/milestones/${id}/accept`, { method: "POST" });
  },

  async reject(id: string) {
    return apiFetch(`/milestones/${id}/reject`, { method: "POST" });
  },

  async cancel(id: string) {
    return apiFetch(`/milestones/${id}/cancel`, { method: "POST" });
  },
};

// Funds API
export const funds = {
  async list(limit = 50, cursor?: string) {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (cursor) params.append("cursor", cursor);
    return apiFetch(`/funds?${params}`);
  },

  async get(id: string) {
    return apiFetch(`/funds/${id}`);
  },

  async create(data: {
    name: string;
    pool_id: string;
  }) {
    return apiFetch("/funds", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async allocate(fundId: string, data: {
    strategy_version_id: string;
    weight: number;
  }) {
    return apiFetch(`/funds/${fundId}/allocate`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async getPerformance(id: string) {
    return apiFetch(`/funds/${id}/performance`);
  },
};

// Flows (scenario runner) API
export const flows = {
  async run(flow_id: "flow1" | "flow2" | "flow3" | "simulation", params: Record<string, any> = {}, seed?: number) {
    return apiFetch("/flows/run", {
      method: "POST",
      body: JSON.stringify({ flow_id, seed, params }),
    });
  },
};

// Growth Layer API
export const onboardingGrowth = {
  async faucetClaim(data: { currency?: string; amount?: string; agent_id?: string; user_id?: string }) {
    return apiFetch("/onboarding/faucet/claim", {
      method: "POST",
      body: JSON.stringify({ currency: "ACP", amount: "10", ...data }),
    });
  },
  async starterPackAssign(data: { starter_pack_code?: string; agent_id?: string; user_id?: string }) {
    return apiFetch("/onboarding/starter-pack/assign", {
      method: "POST",
      body: JSON.stringify({ starter_pack_code: "default", ...data }),
    });
  },
  async quickstartRun(data: { owner_agent_id: string; idempotency_key?: string }) {
    const idk = data.idempotency_key || genIdempotencyKey();
    return apiFetch("/onboarding/quickstart/run", {
      method: "POST",
      headers: { "Idempotency-Key": idk },
      body: JSON.stringify({ owner_agent_id: data.owner_agent_id }),
    });
  },
};

export const growthSocial = {
  async followStrategy(target_id: string, as_agent_id?: string) {
    return apiFetch("/social/strategies/follow", { method: "POST", body: JSON.stringify({ target_id, as_agent_id }) });
  },
  async unfollowStrategy(target_id: string, as_agent_id?: string) {
    return apiFetch("/social/strategies/unfollow", { method: "POST", body: JSON.stringify({ target_id, as_agent_id }) });
  },
  async followAgent(target_id: string, as_agent_id?: string) {
    return apiFetch("/social/agents/follow", { method: "POST", body: JSON.stringify({ target_id, as_agent_id }) });
  },
  async unfollowAgent(target_id: string, as_agent_id?: string) {
    return apiFetch("/social/agents/unfollow", { method: "POST", body: JSON.stringify({ target_id, as_agent_id }) });
  },
  async copyStrategy(source_strategy_id: string, as_agent_id?: string, new_name?: string) {
    return apiFetch("/social/strategies/copy", {
      method: "POST",
      body: JSON.stringify({ source_strategy_id, as_agent_id, new_name }),
    });
  },
};

export const growthPublic = {
  async getAgent(id: string) {
    return apiFetch(`/public/agents/${id}`);
  },
  async getStrategy(id: string) {
    return apiFetch(`/public/strategies/${id}`);
  },
  async getFeed(limit = 50) {
    return apiFetch(`/public/feed/public?limit=${limit}`);
  },
};

export const profiles = {
  async getAgent(id: string) {
    return apiFetch(`/profiles/agents/${encodeURIComponent(id)}`);
  },
  async listAgentFollowers(id: string) {
    return apiFetch(`/profiles/agents/${encodeURIComponent(id)}/followers`);
  },
  async getUser(id: string) {
    return apiFetch(`/profiles/users/${encodeURIComponent(id)}`);
  },
};

export const growthNotifications = {
  async list(limit = 50) {
    return apiFetch(`/notifications?limit=${limit}`);
  },
  async markRead(id: string) {
    return apiFetch(`/notifications/${id}/read`, { method: "POST" });
  },
};

export const growthLeaderboards = {
  async get(board_type: string, limit = 50) {
    return apiFetch(`/leaderboards/${board_type}?limit=${limit}`);
  },
};

export const growthTasks = {
  async feed(limit = 50) {
    return apiFetch(`/tasks/feed?limit=${limit}`);
  },
};

export const growthDashboard = {
  async metrics(days = 7) {
    return apiFetch(`/system/growth-metrics?days=${days}`);
  },
};

export const platformAdmin = {
  async overview() {
    return apiFetch("/platform-admin/overview");
  },
  async listUsers(params: { q?: string; limit?: number; offset?: number } = {}) {
    const search = new URLSearchParams();
    if (params.q) search.set("q", params.q);
    search.set("limit", String(params.limit ?? 50));
    search.set("offset", String(params.offset ?? 0));
    return apiFetch(`/platform-admin/users?${search.toString()}`);
  },
  async getUser(id: string) {
    return apiFetch(`/platform-admin/users/${encodeURIComponent(id)}`);
  },
  async timeseries(metric = "signups", days = 30) {
    return apiFetch(
      `/platform-admin/timeseries?metric=${encodeURIComponent(metric)}&days=${encodeURIComponent(String(days))}`,
    );
  },
  async forecast(metric = "signups", days = 30, horizon = 7) {
    return apiFetch(
      `/platform-admin/forecast?metric=${encodeURIComponent(metric)}&days=${encodeURIComponent(String(days))}&horizon=${encodeURIComponent(String(horizon))}`,
    );
  },
  acpReconcile: (limit = 500, onlyGaps = true) => {
    const search = new URLSearchParams({
      limit: String(limit),
      only_gaps: String(onlyGaps),
    });
    return apiFetch(`/platform-admin/acp-reconcile?${search.toString()}`);
  },
  acpReconcileExecute: (body: { confirm: boolean; user_ids?: string[]; max_transfers?: number }) => {
    return apiFetch("/platform-admin/acp-reconcile/execute", {
      method: "POST",
      body: JSON.stringify(body),
    });
  },
};

export const referrals = {
  async createCode(owner_agent_id?: string) {
    return apiFetch("/referrals/codes/create", {
      method: "POST",
      body: JSON.stringify({ owner_agent_id }),
    });
  },
  async listMyAttributions(limit = 50) {
    return apiFetch(`/referrals/me/attributions?limit=${limit}`);
  },
  async mySummary() {
    return apiFetch("/referrals/me/summary");
  },
  async listMyRewards(limit = 50) {
    return apiFetch(`/referrals/me/rewards?limit=${limit}`);
  },
};

export const workflowStore = {
  async listTemplates() {
    return apiFetch("/workflow-store/templates");
  },
  async listBundles() {
    return apiFetch("/workflow-store/bundles");
  },
  async getBundle(slug: string) {
    return apiFetch(`/workflow-store/bundles/${slug}`);
  },
  async checkoutBundle(slug: string, data: {
    payment_currency?: string;
    payment_method?: string;
    project_name?: string;
    unlock_full_result?: boolean;
    reserve_credits?: boolean;
    inputs_by_workflow?: Record<string, Record<string, any>>;
    note?: string;
  }) {
    return apiFetch(`/workflow-store/bundles/${slug}/checkout`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
  async listCreditPackages() {
    return apiFetch("/workflow-store/credit-packages");
  },
  async getCreditPackage(slug: string) {
    return apiFetch(`/workflow-store/credit-packages/${slug}`);
  },
  async createCreditTopUpIntent(slug: string, data: {
    payment_currency?: string;
    payment_method?: string;
    note?: string;
  } = {}) {
    return apiFetch(`/workflow-store/credit-packages/${slug}/top-up-intents`, {
      method: "POST",
      body: JSON.stringify({
        payment_method: "manual",
        ...data,
      }),
    });
  },
  async confirmCreditTopUpIntent(id: string, data: {
    payment_reference: string;
    note?: string;
  }) {
    return apiFetch(`/workflow-store/top-up-intents/${id}/confirm`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
  async listAdminTopUpIntents(status = "requires_payment", limit = 50) {
    const params = new URLSearchParams({ limit: String(limit) });
    if (status) params.set("status", status);
    return apiFetch(`/workflow-store/admin/top-up-intents?${params.toString()}`);
  },
  async approveCreditTopUpIntent(id: string, data: {
    payment_reference: string;
    note?: string;
  }) {
    return apiFetch(`/workflow-store/admin/top-up-intents/${id}/confirm`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
  async getTemplate(slug: string) {
    return apiFetch(`/workflow-store/templates/${slug}`);
  },
  async listRuns(limit = 20) {
    return apiFetch(`/workflow-store/runs?limit=${limit}`);
  },
  async getRun(id: string) {
    return apiFetch(`/workflow-store/runs/${id}`);
  },
  async createRun(data: {
    workflow_slug: string;
    payment_currency?: string;
    unlock_full_result?: boolean;
    inputs?: Record<string, any>;
  }) {
    return apiFetch("/workflow-store/runs", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
  async updateRunStatus(id: string, status: "quoted" | "paid" | "queued" | "running" | "completed" | "failed" | "cancelled") {
    return apiFetch(`/workflow-store/runs/${id}/status`, {
      method: "POST",
      body: JSON.stringify({ status }),
    });
  },
  async executeRun(id: string) {
    return apiFetch(`/workflow-store/runs/${id}/execute`, {
      method: "POST",
    });
  },
  async confirmRunPayment(id: string, data: {
    payment_reference: string;
    payment_method?: string;
    payment_amount?: { amount: string; currency: string };
    note?: string;
  }) {
    return apiFetch(`/workflow-store/runs/${id}/confirm-payment`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
  async createPaymentIntent(id: string, data: {
    payment_method?: string;
    payment_reference?: string;
    note?: string;
  } = {}) {
    return apiFetch(`/workflow-store/runs/${id}/payment-intents`, {
      method: "POST",
      body: JSON.stringify({
        payment_method: "credits",
        ...data,
      }),
    });
  },
  async retrySettlement(id: string) {
    return apiFetch(`/workflow-store/runs/${id}/retry-settlement`, {
      method: "POST",
    });
  },
  async repeatRun(id: string) {
    return apiFetch(`/workflow-store/runs/${id}/repeat`, {
      method: "POST",
    });
  },
  async getReceiptTrail(id: string) {
    return apiFetch(`/workflow-store/runs/${id}/receipt-trail`);
  },
  async getProofBundle(id: string) {
    return apiFetch(`/workflow-store/runs/${id}/proof-bundle`);
  },
  runEventsUrl(id: string) {
    const params = new URLSearchParams();
    const token = getToken();
    if (token) params.set("token", token);
    const query = params.toString();
    return `${API_BASE}/workflow-store/runs/${encodeURIComponent(id)}/events${query ? `?${query}` : ""}`;
  },
  async revenueSummary(days = 30) {
    return apiFetch(`/workflow-store/admin/revenue?days=${encodeURIComponent(String(days))}`);
  },
  revenueExportUrl(days = 30) {
    return `${API_BASE}/workflow-store/admin/revenue/export?days=${encodeURIComponent(String(days))}`;
  },
  async revenueExportCsv(days = 30) {
    const res = await apiFetchRaw(
      `/workflow-store/admin/revenue/export?days=${encodeURIComponent(String(days))}`,
      {},
      false,
    );
    if (!res.ok) {
      let message = `API request failed with ${res.status}`;
      try {
        const payload = await res.json();
        if (typeof payload?.detail === "string" && payload.detail.trim()) {
          message = payload.detail.trim();
        }
      } catch {
        // CSV export errors are JSON when possible, but keep a stable fallback.
      }
      throw new ApiError(message, res.status);
    }
    return res.blob();
  },
};

export const search = {
  async query(q: string, type?: string, limit = 20, offset = 0) {
    const params = new URLSearchParams({ q, limit: String(limit), offset: String(offset) });
    if (type) params.set("type", type);
    return apiFetch(`/search?${params.toString()}`);
  },
};

export const audit = {
  async list(params: { type?: string; days?: number; limit?: number; offset?: number } = {}) {
    const searchParams = new URLSearchParams();
    if (params.days) searchParams.set("days", String(params.days));
    if (params.type) searchParams.set("type", params.type);
    if (params.limit) searchParams.set("limit", String(params.limit));
    if (params.offset) searchParams.set("offset", String(params.offset));
    return apiFetch(`/admin/audit-log?${searchParams.toString()}`);
  },
  exportUrl(params: { type?: string; days?: number } = {}) {
    const searchParams = new URLSearchParams();
    if (params.days) searchParams.set("days", String(params.days));
    if (params.type) searchParams.set("type", params.type);
    return `${API_BASE}/admin/audit-log/export?${searchParams.toString()}`;
  },
};

export const paidApi = {
  async listProducts() {
    return apiFetch("/paid-api/products");
  },
  async listMyUsage(limit = 50) {
    return apiFetch(`/paid-api/me/usage?limit=${encodeURIComponent(String(limit))}`);
  },
  usageExportUrl(limit = 500) {
    return `${API_BASE}/paid-api/me/usage/export?limit=${encodeURIComponent(String(limit))}`;
  },
  async setSpendCap(agentId: string, data: { currency?: string; monthly_cap?: string | null }) {
    return apiFetch(`/paid-api/agents/${encodeURIComponent(agentId)}/spend-cap`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
};

export const payments = {
  async createStripeIntent(data: {
    package_slug: string;
    currency?: string;
    payment_method_id?: string;
    save_payment_method?: boolean;
    note?: string;
    idempotency_key?: string;
  }) {
    const idk = data.idempotency_key || genIdempotencyKey();
    const { idempotency_key: _ignoredIdempotencyKey, ...body } = data;
    return apiFetch("/payments/stripe/intent", {
      method: "POST",
      headers: {
        "Idempotency-Key": idk,
      },
      body: JSON.stringify(body),
    });
  },
  async getStripeIntent(intentId: string) {
    return apiFetch(`/payments/stripe/intents/${encodeURIComponent(intentId)}`);
  },
  async getStripeStatus() {
    return apiFetch("/payments/stripe/status");
  },
  async listMethods() {
    return apiFetch("/payments/methods");
  },
  async removeMethod(paymentMethodId: string) {
    const res = await apiFetchRaw(`/payments/methods/${encodeURIComponent(paymentMethodId)}`, {
      method: "DELETE",
    });
    if (!res.ok) {
      let detail = "";
      try {
        const payload = await res.json();
        if (typeof payload?.detail === "string") {
          detail = payload.detail.trim();
        }
      } catch {
        // keep stable fallback below
      }
      throw new ApiError(
        detail || `API error ${res.status}${res.statusText ? ` ${res.statusText}` : ""}`,
        res.status,
      );
    }
  },
  async createRefundRequest(data: {
    payment_intent_id: string;
    reason: string;
  }) {
    return apiFetch("/payments/refund-request", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
  async listMyRefundRequests(status?: "pending" | "approved" | "rejected", paymentIntentId?: string) {
    const params = new URLSearchParams();
    if (status) params.set("status", status);
    if (paymentIntentId) params.set("payment_intent_id", paymentIntentId);
    const suffix = params.toString();
    return apiFetch(`/payments/my-refund-requests${suffix ? `?${suffix}` : ""}`);
  },
  async listRefundRequests(status?: "pending" | "approved" | "rejected") {
    const params = new URLSearchParams();
    if (status) params.set("status", status);
    const suffix = params.toString();
    return apiFetch(`/payments/refund-requests${suffix ? `?${suffix}` : ""}`);
  },
  async approveRefundRequest(id: string, data: { admin_notes?: string }) {
    return apiFetch(`/admin/refund-requests/${encodeURIComponent(id)}/approve`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
  async rejectRefundRequest(id: string, data: { admin_notes?: string }) {
    return apiFetch(`/admin/refund-requests/${encodeURIComponent(id)}/reject`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
};

export const subscriptions = {
  async list(limit = 50, cursor?: string, status?: string) {
    const params = new URLSearchParams({ limit: String(limit) });
    if (cursor) params.append("cursor", cursor);
    if (status) params.append("status", status);
    return apiFetch(`/subscriptions?${params.toString()}`);
  },
  async create(data: { listing_id: string; billing_period?: "monthly" | "quarterly" | "annual"; auto_renew?: boolean }) {
    return apiFetch("/subscriptions", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
};

export const creators = {
  async getMyEarnings(days = 30) {
    return apiFetch(`/creators/me/earnings?days=${encodeURIComponent(String(days))}`);
  },
  async getMyConversions(days = 30) {
    return apiFetch(`/creators/me/conversions?days=${encodeURIComponent(String(days))}`);
  },
};

export const pay = {
  async createPaymentLink(data: {
    title: string;
    amount: string;
    currency?: string;
    description?: string;
    expires_in_hours?: number;
  }) {
    return apiFetch("/pay/payment-links", { method: "POST", body: JSON.stringify(data) });
  },
  async getPaymentLink(id: string) {
    return apiFetch(`/pay/payment-links/${encodeURIComponent(id)}`);
  },
  async getPublicPaymentLink(code: string) {
    return apiFetch(`/pay/${encodeURIComponent(code)}`);
  },
  async checkoutPaymentLink(code: string, data?: { payment_method?: string; payment_reference?: string }) {
    return apiFetch(`/pay/${encodeURIComponent(code)}/checkout`, {
      method: "POST",
      body: JSON.stringify(data || { payment_method: "credits" }),
    });
  },
  async createInvoice(data: {
    customer_email?: string;
    line_items: Array<{ description: string; quantity: number; unit_amount: string; currency: string }>;
    due_in_days?: number;
    notes?: string;
    create_payment_link?: boolean;
  }) {
    return apiFetch("/pay/invoices", { method: "POST", body: JSON.stringify(data) });
  },
  async getInvoice(id: string) {
    return apiFetch(`/pay/invoices/${encodeURIComponent(id)}`);
  },
  invoiceExportUrl(id: string) {
    return `${API_BASE}/pay/invoices/${encodeURIComponent(id)}/export.txt`;
  },
  async getPaymentLinkQr(code: string) {
    return apiFetch(`/pay/${encodeURIComponent(code)}/qr`);
  },
};

export const commerce = {
  async listPlans() {
    return apiFetch("/commerce/plans");
  },
  async selectPlan(tier: string) {
    return apiFetch("/commerce/plans/select", { method: "POST", body: JSON.stringify({ tier }) });
  },
  async joinRampWaitlist(data: { email: string; interest?: string; region?: string; notes?: string }) {
    return apiFetch("/commerce/ramp-waitlist", { method: "POST", body: JSON.stringify(data) });
  },
};

export const wacpPublic = {
  async status() {
    return apiFetch("/wacp/status");
  },
  async reserveProof() {
    return apiFetch("/wacp/reserve-proof");
  },
};

export const sacpPublic = {
  async status() {
    return apiFetch("/sacp/status");
  },
  async reserveProof() {
    return apiFetch("/sacp/reserve-proof");
  },
};

export const cryptoBenchmark = {
  async scorecard() {
    return apiFetch("/crypto/benchmark");
  },
};

export const marketData = {
  async prices(vs = "usd") {
    return apiFetch(`/market/prices?vs=${encodeURIComponent(vs)}`);
  },
  async status() {
    return apiFetch("/market/status");
  },
};

export const weatherApi = {
  async current(lat: number, lon: number) {
    return apiFetch(`/weather/current?lat=${encodeURIComponent(String(lat))}&lon=${encodeURIComponent(String(lon))}`);
  },
  async status() {
    return apiFetch("/weather/status");
  },
};

export const merchant = {
  async dashboard() {
    return apiFetch("/merchant/dashboard");
  },
  async listPayments() {
    return apiFetch("/merchant/payments");
  },
  async exportCsv() {
    return apiFetchRaw("/merchant/export.csv");
  },
};

export const claimCodes = {
  async create(data: {
    amount: string;
    currency?: string;
    max_redemptions?: number;
    expires_in_hours?: number;
    campaign_label?: string;
    pin?: string;
  }) {
    return apiFetch("/claim-codes/create", { method: "POST", body: JSON.stringify(data) });
  },
  async redeem(data: { code: string; pin?: string }) {
    return apiFetch("/claim-codes/redeem", { method: "POST", body: JSON.stringify(data) });
  },
  async listMine() {
    return apiFetch("/claim-codes/mine");
  },
};

export const acpExplorer = {
  async status() {
    return apiFetch("/acp/explorer/status");
  },
  async efficiency() {
    return apiFetch("/acp/explorer/efficiency");
  },
  async search(q: string) {
    return apiFetch(`/acp/explorer/search?q=${encodeURIComponent(q)}`);
  },
  async blocks(limit = 12, beforeHeight?: number | null) {
    const params = new URLSearchParams({ limit: String(limit) });
    if (beforeHeight != null) params.set("before_height", String(beforeHeight));
    return apiFetch(`/acp/explorer/blocks?${params.toString()}`);
  },
  async getBlock(id: string) {
    return apiFetch(`/acp/explorer/block/${encodeURIComponent(id)}`);
  },
  async getTx(txid: string, view: "redacted" | "full" = "full") {
    return apiFetch(
      `/acp/explorer/tx/${encodeURIComponent(txid)}?view=${encodeURIComponent(view)}`
    );
  },
  async getAddress(address: string, historyLimit = 50, historyOffset = 0) {
    const params = new URLSearchParams({
      history_limit: String(historyLimit),
      history_offset: String(historyOffset),
    });
    return apiFetch(`/acp/explorer/address/${encodeURIComponent(address)}?${params.toString()}`);
  },
  async mempool() {
    return apiFetch("/acp/explorer/mempool");
  },
  async stats() {
    return apiFetch("/acp/explorer/stats");
  },
};

export const payouts = {
  async list(status?: string) {
    const suffix = status ? `?status=${encodeURIComponent(status)}` : "";
    return apiFetch(`/payouts${suffix}`);
  },
  async request(data: {
    amount: string;
    currency?: string;
    destination: string;
    method?: "acp_wallet" | "bsc_address" | "bank_transfer";
  }) {
    return apiFetch("/payouts/request", {
      method: "POST",
      body: JSON.stringify({
        amount: { amount: data.amount, currency: data.currency || "ACP" },
        method: data.method || "acp_wallet",
        destination: data.destination,
      }),
    });
  },
};

export const paymentScanner = {
  async parse(raw_text: string, source: "paste" | "qr" | "ocr" = "paste") {
    return apiFetch("/payment-scanner/parse", {
      method: "POST",
      body: JSON.stringify({ raw_text, source }),
    });
  },
};

export const organizations = {
  async list() {
    return apiFetch("/organizations");
  },
  async get(id: string) {
    return apiFetch(`/organizations/${encodeURIComponent(id)}`);
  },
  async create(data: { name: string; description?: string }) {
    return apiFetch("/organizations", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
  async update(id: string, data: { name?: string; description?: string | null; billing_wallet_address?: string | null }) {
    return apiFetch(`/organizations/${encodeURIComponent(id)}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    });
  },
  async remove(id: string) {
    return apiFetch(`/organizations/${encodeURIComponent(id)}`, {
      method: "DELETE",
    });
  },
  async listMembers(id: string) {
    return apiFetch(`/organizations/${encodeURIComponent(id)}/members`);
  },
  async addMember(id: string, data: { email: string; role: string }) {
    return apiFetch(`/organizations/${encodeURIComponent(id)}/members`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
  async updateMemberRole(id: string, userId: string, data: { role: string }) {
    return apiFetch(`/organizations/${encodeURIComponent(id)}/members/${encodeURIComponent(userId)}/role`, {
      method: "PATCH",
      body: JSON.stringify(data),
    });
  },
  async removeMember(id: string, userId: string) {
    return apiFetch(`/organizations/${encodeURIComponent(id)}/members/${encodeURIComponent(userId)}`, {
      method: "DELETE",
    });
  },
};

export const webhooks = {
  async list() {
    return apiFetch("/webhooks");
  },
  async get(id: string) {
    return apiFetch(`/webhooks/${encodeURIComponent(id)}`);
  },
  async create(data: { url: string; event_types: string[]; description?: string }) {
    return apiFetch("/webhooks", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
  async remove(id: string) {
    return apiFetch(`/webhooks/${encodeURIComponent(id)}`, {
      method: "DELETE",
    });
  },
  async rotateSecret(id: string) {
    return apiFetch(`/webhooks/${encodeURIComponent(id)}/rotate-secret`, {
      method: "POST",
    });
  },
  async listDeliveries(id: string, limit = 50) {
    return apiFetch(`/webhooks/${encodeURIComponent(id)}/deliveries?limit=${encodeURIComponent(String(limit))}`);
  },
  async sendTest(id: string) {
    return apiFetch(`/webhooks/${encodeURIComponent(id)}/test`, {
      method: "POST",
    });
  },
};

export const system = {
  async fees() {
    return apiFetch("/system/fees");
  },
  async stakingEconomics() {
    return apiFetch("/system/staking-economics");
  },
  async health() {
    return apiFetch("/system/health");
  },
  async ledgerInvariantStatus() {
    return apiFetch("/internal/ops/ledger-invariant-status");
  },
  async deepHealth() {
    return apiFetch("/internal/ops/deep-health");
  },
  async economyHealth() {
    return apiFetch("/internal/ops/economy-health");
  },
};

export const decisionLogs = {
  async list(limit = 100, scope?: string, reason_code?: string) {
    const params = new URLSearchParams({ limit: String(limit) });
    if (scope) params.append("scope", scope);
    if (reason_code) params.append("reason_code", reason_code);
    return apiFetch(`/internal/ops/decision-logs?${params.toString()}`);
  },
};

export const governance = {
  async listProposals(status?: string, limit = 100) {
    const params = new URLSearchParams({ limit: String(limit) });
    if (status && status !== "all") params.append("status", status);
    return apiFetch(`/governance/proposals?${params.toString()}`);
  },
  async createProposal(data: {
    kind: string;
    target_type: string;
    target_id?: string;
    payload_json: Record<string, any>;
  }) {
    return apiFetch("/governance/proposals", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
  async submitProposal(id: string) {
    return apiFetch(`/governance/proposals/${id}/submit`, { method: "POST" });
  },
  async voteProposal(id: string, vote: "approve" | "reject" | "abstain", reason?: string) {
    return apiFetch(`/governance/proposals/${id}/vote`, {
      method: "POST",
      body: JSON.stringify({ vote, reason }),
    });
  },
  async decideProposal(id: string, decision: "active" | "rejected" | "appealed", reason?: string) {
    return apiFetch(`/governance/proposals/${id}/decide`, {
      method: "POST",
      body: JSON.stringify({ decision, reason }),
    });
  },
  async getProposalAudit(id: string, limit = 200) {
    return apiFetch(`/governance/proposals/${id}/audit?limit=${limit}`);
  },
  async listModerationCases(status?: string, limit = 100) {
    const params = new URLSearchParams({ limit: String(limit) });
    if (status && status !== "all") params.append("status", status);
    return apiFetch(`/moderation/cases?${params.toString()}`);
  },
  async openModerationCase(data: { subject_type: string; subject_id: string; reason_code: string }) {
    return apiFetch("/moderation/cases", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
  async resolveModerationCase(id: string, status: "resolved" | "appealed" | "rejected", resolution?: string) {
    return apiFetch(`/moderation/cases/${id}/resolve`, {
      method: "POST",
      body: JSON.stringify({ status, resolution }),
    });
  },
  async applyModerationAction(data: {
    target_type: "agent" | "strategy" | "listing" | "vertical" | "pool";
    target_id: string;
    action: "suspend" | "unsuspend" | "quarantine" | "unquarantine" | "halt" | "unhalt" | "reject";
    reason?: string;
  }) {
    return apiFetch("/moderation/actions", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
  async graphEnforcementPreview(limit = 50) {
    return apiFetch(`/system/graph-enforcement/preview?limit=${limit}`);
  },
};

export const evolution = {
  async createMutation(data: { parent_strategy_id: string; mutation_type?: string; diff_spec?: Record<string, any> }) {
    return apiFetch("/evolution/mutations", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
  async lineage(strategy_id: string, limit = 100) {
    return apiFetch(`/evolution/strategies/${strategy_id}/lineage?limit=${limit}`);
  },
};

export const competitions = {
  async createTournament(data: { name: string; scoring_metric?: string }) {
    return apiFetch("/competitions/tournaments", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
  async addEntry(tournament_id: string, data: { strategy_id: string; agent_id?: string }) {
    return apiFetch(`/competitions/tournaments/${tournament_id}/entries`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
  async leaderboard(tournament_id: string, limit = 100) {
    return apiFetch(`/competitions/tournaments/${tournament_id}/leaderboard?limit=${limit}`);
  },
};

export const bounties = {
  async createReport(data: { reporter_agent_id?: string; title: string; description: string; severity?: string }) {
    return apiFetch("/bounties/reports", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
  async listReports(limit = 100) {
    return apiFetch(`/bounties/reports?limit=${limit}`);
  },
};

export const aeterna = {
  async status() {
    return apiFetch("/aeterna/status");
  },
  async createVault(data: {
    label: string;
    source?: string;
    source_uri?: string | null;
    content_sha256: string;
    format_hint?: string;
    consent_acknowledged: boolean;
    metadata_json?: Record<string, unknown>;
  }) {
    return apiFetch("/aeterna/vault", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
  async listVault() {
    return apiFetch("/aeterna/vault");
  },
  async createIntent(data: {
    intent_kind: string;
    vault_id?: string | null;
    workflow_slug?: string | null;
    notes?: string | null;
    budget_acp: string | number;
    metadata_json?: Record<string, unknown>;
  }) {
    return apiFetch("/aeterna/intents", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
  async listIntents() {
    return apiFetch("/aeterna/intents");
  },
  async orgSummary(orgId: string) {
    return apiFetch(`/organizations/${orgId}/aeterna/summary`);
  },
  async orgCreateVault(
    orgId: string,
    data: {
      label: string;
      source?: string;
      source_uri?: string | null;
      content_sha256: string;
      format_hint?: string;
      consent_acknowledged: boolean;
      metadata_json?: Record<string, unknown>;
    },
  ) {
    return apiFetch(`/organizations/${orgId}/aeterna/vault`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
  async orgListVault(orgId: string) {
    return apiFetch(`/organizations/${orgId}/aeterna/vault`);
  },
  async orgCreateIntent(
    orgId: string,
    data: {
      intent_kind: string;
      vault_id?: string | null;
      workflow_slug?: string | null;
      notes?: string | null;
      budget_acp: string | number;
      metadata_json?: Record<string, unknown>;
    },
  ) {
    return apiFetch(`/organizations/${orgId}/aeterna/intents`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
  async orgListIntents(orgId: string) {
    return apiFetch(`/organizations/${orgId}/aeterna/intents`);
  },
  async orgCreatePartner(
    orgId: string,
    data: {
      name: string;
      jurisdiction: string;
      license_ref?: string | null;
      website?: string | null;
      supported_intents?: string[];
      metadata_json?: Record<string, unknown>;
    },
  ) {
    return apiFetch(`/organizations/${orgId}/aeterna/partners`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
  async orgListPartners(orgId: string) {
    return apiFetch(`/organizations/${orgId}/aeterna/partners`);
  },
};

export const settlements = {
  async listReceipts(limit = 100, status?: string) {
    const params = new URLSearchParams({ limit: String(limit) });
    if (status) params.append("status", status);
    return apiFetch(`/settlements/receipts?${params.toString()}`);
  },
};

export const autonomy = {
  async anomalies() {
    return apiFetch("/autonomy/ops/anomalies");
  },
  async applyRemediation(action: string) {
    return apiFetch("/autonomy/ops/remediations/apply", {
      method: "POST",
      body: JSON.stringify({ action }),
    });
  },
  async councilRecommend(subject: string, evidence: string) {
    return apiFetch("/autonomy/ai-council/recommend", {
      method: "POST",
      body: JSON.stringify({ subject, evidence }),
    });
  },
  async compileStrategy(prompt: string) {
    return apiFetch("/autonomy/strategy-compiler/compile", {
      method: "POST",
      body: JSON.stringify({ prompt }),
    });
  },
};

// Convenience aggregate export
export const api = {
  auth,
  users,
  agents,
  strategies,
  strategyVersions,
  runs,
  pools,
  verticals,
  ledger,
  walletAcp,
  bridgeRail,
  stakes,
  reputation,
  listings,
  orders,
  access,
  contracts,
  funds,
  flows,
  onboardingGrowth,
  growthSocial,
  growthPublic,
  growthNotifications,
  growthLeaderboards,
  growthTasks,
  growthDashboard,
  platformAdmin,
  referrals,
  payments,
  pay,
  merchant,
  claimCodes,
  acpExplorer,
  payouts,
  paymentScanner,
  commerce,
  wacpPublic,
  sacpPublic,
  cryptoBenchmark,
  marketData,
  weatherApi,
  subscriptions,
  organizations,
  webhooks,
  system,
  decisionLogs,
  governance,
  evolution,
  competitions,
  bounties,
  aeterna,
  settlements,
  autonomy,
};
