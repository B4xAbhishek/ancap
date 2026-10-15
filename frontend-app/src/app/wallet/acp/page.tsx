"use client";
import Link from "next/link";
import dynamic from "next/dynamic";
import {
  useEffect,
  useRef,
  useState,
  type FormEvent,
  type ReactNode,
} from "react";
import { Navigation } from "@/components/Navigation";
import { useAuth } from "@/components/AuthProvider";
import { useLanguage } from "@/components/LanguageProvider";
import { ApiError, walletAcp } from "@/lib/api";
import {
  formatAcpDisplay,
  selectHeroAcp,
  selectOnChainAtDeposit,
  selectPlatformLedger,
} from "@/lib/acpBalanceDisplay";
import {
  DEFAULT_ACP_FEE,
  maximumSend,
  transferCheck,
  isAcpAddress,
} from "@/lib/walletTransfer";
import { walletUxCopy } from "@/locales/walletUx";
import { WalletBulkTransfer } from "./WalletBulkTransfer";
import type { WalletBalance, ChainTransaction } from "./types";
import s from "./wallet.module.css";

const OtcDesk = dynamic(() =>
  import("@/components/OtcIntakeDesk").then((m) => m.OtcIntakeDesk),
);
const AssayDesk = dynamic(() =>
  import("@/components/AssayGcDesk").then((m) => m.AssayGcDesk),
);
const OwnershipDesk = dynamic(() =>
  import("@/components/OwnershipProofDesk").then((m) => m.OwnershipProofDesk),
);
type Section =
  | "overview"
  | "receive"
  | "send"
  | "history"
  | "security"
  | "services";
type TransferReview = {
  address: string;
  amount: string;
  fee: string;
  total: string;
};
type TransferResult = {
  accepted?: boolean;
  txid?: string | null;
  status?: string;
  job_id?: string;
  reason?: string;
};
const HOT_ADDRESS = "acp1qzfdkqxfgyw9ysk99qsd79yxdfe338yd85vrqnp9";

function WalletIcon({ name }: { name: string }) {
  const paths: Record<string, ReactNode> = {
    receive: (
      <>
        <path d="M12 3v12m-5-5 5 5 5-5" />
        <path d="M4 16v4h16v-4" />
      </>
    ),
    send: (
      <>
        <path d="M12 16V4m-5 5 5-5 5 5" />
        <path d="M4 17v4h16v-4" />
      </>
    ),
    history: (
      <>
        <path d="M4 5v5h5" />
        <path d="M4 10a8 8 0 1 1 1 7m7-10v5l3 2" />
      </>
    ),
    security: (
      <>
        <path d="m12 3 8 3v6c0 5-8 9-8 9s-8-4-8-9V6z" />
        <path d="m8 12 3 3 5-6" />
      </>
    ),
    overview: (
      <>
        <rect x="3" y="5" width="18" height="15" rx="3" />
        <path d="M3 9h18m-6 5h3" />
      </>
    ),
    services: (
      <>
        <circle cx="6" cy="6" r="2" />
        <circle cx="18" cy="6" r="2" />
        <circle cx="6" cy="18" r="2" />
        <circle cx="18" cy="18" r="2" />
      </>
    ),
  };
  return (
    <svg
      width="21"
      height="21"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.6"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {paths[name] || paths.overview}
    </svg>
  );
}

export default function AcpWalletPage() {
  const {
    isAuthenticated,
    isLoading: authLoading,
    user,
    changePassword,
    logout,
  } = useAuth();
  const { lang, t } = useLanguage();
  const c = walletUxCopy[lang];
  const [section, setSection] = useState<Section>("overview");
  const [sessionOwner, setSessionOwner] = useState<string | null>(null);
  const [wallet, setWallet] = useState<WalletBalance | null>(null);
  const [address, setAddress] = useState("");
  const [needsPersonalize, setNeedsPersonalize] = useState(false);
  const [depositNote, setDepositNote] = useState("");
  const [loading, setLoading] = useState(false),
    [partial, setPartial] = useState(false);
  const [updated, setUpdated] = useState<Date | null>(null);
  const [error, setError] = useState(""),
    [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false);
  const generation = useRef(0),
    actionLock = useRef(false),
    sendLock = useRef(false);
  const [personalPassword, setPersonalPassword] = useState(""),
    [backup, setBackup] = useState("");
  const [privacyPassword, setPrivacyPassword] = useState(""),
    [privacyAddress, setPrivacyAddress] = useState("");
  const [recipient, setRecipient] = useState(""),
    [amount, setAmount] = useState("");
  const [customFee, setCustomFee] = useState(false),
    [fee, setFee] = useState(DEFAULT_ACP_FEE);
  const [review, setReview] = useState<TransferReview | null>(null),
    [walletPassword, setWalletPassword] = useState("");
  const [attempted, setAttempted] = useState(false),
    [result, setResult] = useState<TransferResult | null>(null);
  const [historyAddress, setHistoryAddress] = useState(""),
    [activeAddress, setActiveAddress] = useState("");
  const [transactions, setTransactions] = useState<ChainTransaction[]>([]);
  const [historyState, setHistoryState] = useState<
    "idle" | "loading" | "error" | "ready"
  >("idle");
  const historyGeneration = useRef(0);
  const [passwords, setPasswords] = useState({
    current: "",
    next: "",
    confirm: "",
  });
  const [tool, setTool] = useState("");
  const securityRef = useRef<HTMLElement | null>(null);
  const operator =
    wallet?.view_mode === "operator_hot" ||
    wallet?.primary_kind === "operator_total" ||
    wallet?.primary_kind === "chain_supply";
  const nativeDataUnavailable =
    wallet?.probe_status === "unavailable" ||
    wallet?.probe_status === "degraded";
  const available = nativeDataUnavailable
    ? null
    : (wallet?.withdrawable_now_acp ?? wallet?.available_acp ?? null);
  const validation = transferCheck(recipient, amount, fee, available);
  const validationMessage = (code: string | null) =>
    code === "address"
      ? c.addressError
      : code === "amount"
        ? c.amountError
        : code === "fee"
          ? c.feeError
          : code === "balance"
            ? c.balanceError
            : code === "rows"
              ? c.rowsError
              : c.unknown;
  const money = (value: string | null | undefined) =>
    value == null ? "—" : formatAcpDisplay(value);
  const field = (label: string, control: ReactNode) => (
    <label className={s.field}>
      <span>{label}</span>
      {control}
    </label>
  );

  async function refreshWallet() {
    if (!isAuthenticated) return;
    const epoch = generation.current;
    setLoading(true);
    setPartial(false);
    const addressJob = walletAcp.getDepositAddress().then((data) => {
      if (epoch === generation.current) {
        setAddress(String(data.address || ""));
        setNeedsPersonalize(Boolean(data.needs_personalize));
        setDepositNote(String(data.note || ""));
      }
      return data;
    });
    try {
      const [addr, balance] = await Promise.allSettled([
        addressJob,
        walletAcp.getHotBalance(),
      ]);
      if (epoch !== generation.current) return;
      if (
        [addr, balance].some(
          (result) =>
            result.status === "rejected" &&
            result.reason instanceof ApiError &&
            result.reason.status === 401,
        )
      ) {
        logout();
        return;
      }
      let value: WalletBalance | null =
        balance.status === "fulfilled" ? balance.value : null;
      if (balance.status === "rejected") {
        try {
          value = await walletAcp.getBalance();
        } catch (e) {
          if (e instanceof ApiError && e.status === 401) {
            logout();
            return;
          }
          /* Keep the last known balance, labelled as stale. */
        }
        if (epoch !== generation.current) return;
      }
      if (value) {
        setWallet(value);
        setUpdated(new Date());
        if (
          addr.status !== "fulfilled" &&
          value.address &&
          value.address !== HOT_ADDRESS
        )
          setAddress(value.address);
      }
      setPartial(
        addr.status === "rejected" ||
          balance.status === "rejected" ||
          !value ||
          value.probe_status === "unavailable" ||
          value.probe_status === "degraded" ||
          Boolean(value.balance_status && value.balance_status !== "live"),
      );
    } finally {
      if (epoch === generation.current) setLoading(false);
    }
  }

  useEffect(() => {
    generation.current++;
    historyGeneration.current++;
    setSessionOwner(user?.id || null);
    setWallet(null);
    setAddress("");
    setUpdated(null);
    setTransactions([]);
    setHistoryState("idle");
    setHistoryAddress("");
    setActiveAddress("");
    setBackup("");
    setPrivacyAddress("");
    setWalletPassword("");
    setPersonalPassword("");
    setPrivacyPassword("");
    setPasswords({ current: "", next: "", confirm: "" });
    setResult(null);
    setReview(null);
    setAttempted(false);
    setError("");
    setNotice("");
    setBusy(false);
    if (isAuthenticated) void refreshWallet();
    const walletGeneration = generation;
    const transactionGeneration = historyGeneration;
    return () => {
      walletGeneration.current++;
      transactionGeneration.current++;
    };
    // Network data belongs to the authenticated account; language changes do not refetch funds.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated, user?.id]);

  useEffect(() => {
    const syncHash = () => {
      const key = window.location.hash.slice(1);
      if (key === "password-security") setSection("security");
      else if (
        [
          "overview",
          "receive",
          "send",
          "history",
          "security",
          "services",
        ].includes(key)
      )
        setSection(key as Section);
    };
    syncHash();
    window.addEventListener("hashchange", syncHash);
    return () => window.removeEventListener("hashchange", syncHash);
  }, []);
  useEffect(() => {
    if (
      section === "security" &&
      isAuthenticated &&
      window.location.hash === "#password-security"
    )
      securityRef.current?.focus();
  }, [section, isAuthenticated]);
  function navigate(next: Section) {
    setSection(next);
    setError("");
    setNotice("");
    setWalletPassword("");
    setPrivacyPassword("");
    setPersonalPassword("");
    setPasswords({ current: "", next: "", confirm: "" });
    window.history.replaceState(
      null,
      "",
      `#${next === "security" ? "password-security" : next}`,
    );
  }
  async function copy(value: string) {
    try {
      await navigator.clipboard.writeText(value);
      setNotice(t("walletAcpPage.copied"));
    } catch {
      setError(t("walletAcpPage.clipboardUnavailable"));
    }
  }
  async function perform<T>(job: () => Promise<T>, done: (value: T) => void) {
    if (actionLock.current) return;
    actionLock.current = true;
    const epoch = generation.current;
    setBusy(true);
    setError("");
    setNotice("");
    try {
      const value = await job();
      if (epoch === generation.current) done(value);
    } catch (e) {
      if (epoch === generation.current)
        setError(e instanceof Error ? e.message : c.unknown);
    } finally {
      actionLock.current = false;
      if (epoch === generation.current) setBusy(false);
    }
  }
  async function loadHistory(target: string) {
    if (!isAcpAddress(target)) {
      setError(c.addressError);
      return;
    }
    const sequence = ++historyGeneration.current;
    setHistoryState("loading");
    setActiveAddress(target.trim());
    setTransactions([]);
    try {
      const data = await walletAcp.listTransactions({
        address: target.trim(),
        limit: 20,
        privacy: false,
      });
      if (sequence !== historyGeneration.current) return;
      const rows = Array.isArray(data) ? data : data?.items;
      if (!Array.isArray(rows)) throw new Error("Invalid history response");
      setTransactions(rows);
      setHistoryState("ready");
    } catch (e) {
      if (
        e instanceof ApiError &&
        e.status === 401 &&
        sequence === historyGeneration.current
      ) {
        logout();
        return;
      }
      if (sequence === historyGeneration.current) setHistoryState("error");
    }
  }
  useEffect(() => {
    if (
      section === "history" &&
      isAuthenticated &&
      address &&
      historyState === "idle"
    ) {
      setHistoryAddress(address);
      void loadHistory(address);
    }
    // History loads on demand, once for the selected account/address.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [section, address, isAuthenticated]);

  async function submitTransfer(e: FormEvent) {
    e.preventDefault();
    if (!review || !walletPassword || sendLock.current || attempted) return;
    const checked = transferCheck(
      review.address,
      review.amount,
      review.fee,
      available,
    );
    if (checked.error) {
      setError(validationMessage(checked.error));
      return;
    }
    sendLock.current = true;
    const epoch = generation.current;
    setBusy(true);
    setAttempted(true);
    setError("");
    const secret = walletPassword;
    setWalletPassword("");
    try {
      const response = await walletAcp.withdraw(
        {
          to_address: review.address,
          amount_acp: review.amount,
          fee_acp: review.fee,
          wallet_password: secret,
        },
        (jobId) => {
          if (epoch === generation.current)
            setResult({ status: "pending", job_id: jobId });
        },
      );
      if (epoch !== generation.current) return;
      setResult(response || {});
      void refreshWallet();
      setHistoryState("idle");
    } catch (e) {
      if (epoch === generation.current) {
        setResult((previous) => ({ ...previous, status: "unknown" }));
        setError(e instanceof Error ? e.message : c.uncertainHint);
      }
    } finally {
      sendLock.current = false;
      if (epoch === generation.current) setBusy(false);
    }
  }

  const summary = (
    <div className={s.metrics}>
      {[
        [
          c.onChain,
          nativeDataUnavailable ? null : selectOnChainAtDeposit(wallet),
          c.network,
        ],
        [c.credits, selectPlatformLedger(wallet), c.creditsHint],
        [
          c.reserved,
          wallet?.reserved_total_acp ??
            wallet?.in_work_acp ??
            wallet?.staked_acp,
          c.reservedHint,
        ],
      ].map(([label, value, hint]) => (
        <div className={s.metric} key={label}>
          <span>{label}</span>
          <strong title={value || undefined}>
            {money(value)} <small>ACP</small>
          </strong>
          <p>{hint}</p>
        </div>
      ))}
    </div>
  );
  const intro = (
    <header className={s.header}>
      <div>
        <p className={s.eyebrow}>ANCAP / ACP</p>
        <h1>{t("walletAcpPage.title")}</h1>
        <p className={s.lead}>{c.subtitle}</p>
      </div>
      {isAuthenticated && (
        <button
          className={s.secondary}
          disabled={loading || busy}
          onClick={() => void refreshWallet()}
        >
          {loading ? t("walletAcpPage.loading") : c.refresh}
        </button>
      )}
    </header>
  );

  return (
    <div className={s.shell}>
      <Navigation />
      <main className={s.page}>
        {intro}
        {authLoading || (isAuthenticated && sessionOwner !== user?.id) ? (
          <div className={s.panel} role="status">
            {t("walletAcpPage.loading")}
          </div>
        ) : !isAuthenticated ? (
          <section className={s.welcome}>
            <WalletIcon name="overview" />
            <h2>{c.login}</h2>
            <p>{c.loginHint}</p>
            <div className={s.actions}>
              <Link
                className={s.primary}
                href={`/login?next=${encodeURIComponent("/wallet/acp" + (section === "security" ? "#password-security" : ""))}`}
              >
                {c.login}
              </Link>
              <Link className={s.secondary} href="/register">
                {c.register}
              </Link>
            </div>
            <div className={s.features}>
              {["receive", "send", "history"].map((key) => (
                <div key={key}>
                  <WalletIcon name={key} />
                  <strong>{c[key as "receive" | "send" | "history"]}</strong>
                </div>
              ))}
            </div>
          </section>
        ) : (
          <>
            <nav className={s.tabs} aria-label={c.sections}>
              {(
                [
                  "overview",
                  "receive",
                  "send",
                  "history",
                  "security",
                  "services",
                ] as Section[]
              ).map((key) => (
                <button
                  key={key}
                  aria-current={section === key ? "page" : undefined}
                  onClick={() => navigate(key)}
                  disabled={busy}
                >
                  <WalletIcon name={key} />
                  {c[key]}
                </button>
              ))}
            </nav>
            <div aria-live="polite">
              {notice && (
                <p className={s.success} role="status">
                  {notice}
                </p>
              )}
            </div>
            {error && (
              <p className={s.error} role="alert">
                {error}
              </p>
            )}
            {partial && (
              <p className={s.warning} role="status">
                {c.partial}
              </p>
            )}
            {backup && section !== "receive" && (
              <button className={s.warning} onClick={() => navigate("receive")}>
                {c.backup} →
              </button>
            )}
            {section === "overview" && (
              <div className={s.stack}>
                {operator && (
                  <aside className={s.warning}>
                    <strong>{c.operator}</strong>
                    <p>{c.operatorHint}</p>
                  </aside>
                )}
                <section className={s.hero} aria-label={c.available}>
                  <div>
                    <span className={s.eyebrow}>{c.available}</span>
                    <div className={s.balance}>
                      {loading && !wallet ? "…" : money(available)}{" "}
                      <span>ACP</span>
                    </div>
                    <p>{c.availableHint}</p>
                    <div className={s.updated}>
                      {updated
                        ? `${c.updated}: ${updated.toLocaleTimeString(lang)}`
                        : c.unknown}
                    </div>
                  </div>
                  <div className={s.quick}>
                    {(["receive", "send", "history"] as Section[]).map(
                      (key) => (
                        <button
                          key={key}
                          className={
                            key === "receive" ? s.primary : s.secondary
                          }
                          onClick={() => navigate(key)}
                        >
                          <WalletIcon name={key} />
                          {c[key]}
                        </button>
                      ),
                    )}
                  </div>
                </section>
                {summary}
                <section className={s.panel}>
                  <div className={s.sectionHeader}>
                    <div>
                      <h2>{c.address}</h2>
                      <p>{c.network}</p>
                    </div>
                    <button
                      className={s.secondary}
                      onClick={() => navigate("receive")}
                    >
                      {c.receive} →
                    </button>
                  </div>
                  <code className={s.address}>
                    {!needsPersonalize && address
                      ? address
                      : t("walletAcpPage.personalizeWallet")}
                  </code>
                  <p className={s.muted}>{c.receiveHint}</p>
                </section>
                <div className={s.linkGrid}>
                  <Link href="/wallet/credits">
                    <strong>{c.credits}</strong>
                    <span>{c.creditsHint}</span>
                  </Link>
                  <Link href="/buy-acp">
                    <strong>{c.buy} →</strong>
                    <span>{c.network} / wACP</span>
                  </Link>
                </div>
                <details className={s.panel}>
                  <summary>{c.technical}</summary>
                  <dl className={s.facts}>
                    <div>
                      <dt>{t("walletAcpPage.walletBalance")}</dt>
                      <dd>{money(selectHeroAcp(wallet))} ACP</dd>
                    </div>
                    <div>
                      <dt>
                        {wallet?.primary_kind === "chain_supply"
                          ? t("walletAcpPage.primaryKindSupply")
                          : wallet?.primary_kind === "operator_total"
                            ? t("walletAcpPage.primaryKindOperator")
                            : wallet?.primary_kind === "platform_credits"
                              ? t("walletAcpPage.primaryKindCredits")
                              : t("walletAcpPage.primaryKindOnChain")}
                      </dt>
                      <dd>{wallet?.balance_status || c.unknown}</dd>
                    </div>
                    <div>
                      <dt>
                        {t("walletAcpPage.chainHeight").replace("{n}", "")}
                      </dt>
                      <dd>{wallet?.chain_height ?? "—"}</dd>
                    </div>
                  </dl>
                  {operator && (
                    <>
                      <p className={s.muted}>
                        {t("walletAcpPage.operatorBucketsLiveNote")}
                      </p>
                      {wallet?.tokenomics_buckets?.map((bucket) => (
                        <p className={s.metricLine} key={bucket.key}>
                          <span>{bucket.label}</span>
                          <strong>{money(bucket.acp)} ACP</strong>
                        </p>
                      ))}
                    </>
                  )}
                </details>
              </div>
            )}
            {section === "receive" && (
              <section className={s.narrow}>
                <div className={s.panel}>
                  <span className={s.eyebrow}>{c.network}</span>
                  <h2>{c.receive}</h2>
                  <p className={s.muted}>{c.receiveHint}</p>
                  {needsPersonalize ? (
                    <div className={s.stack}>
                      <p>{t("walletAcpPage.personalizeLead")}</p>
                      {field(
                        t("walletAcpPage.walletPassword"),
                        <input
                          type="password"
                          value={personalPassword}
                          onChange={(e) => setPersonalPassword(e.target.value)}
                          autoComplete="current-password"
                        />,
                      )}
                      <button
                        className={s.primary}
                        disabled={busy || personalPassword.length < 8}
                        onClick={() => {
                          const secret = personalPassword;
                          setPersonalPassword("");
                          void perform(
                            () =>
                              walletAcp.personalizeWallet({
                                wallet_password: secret,
                              }),
                            (value) => {
                              setAddress(value.address || "");
                              setNeedsPersonalize(false);
                              setBackup(value.wallet_backup_mnemonic || "");
                              void refreshWallet();
                            },
                          );
                        }}
                      >
                        {t("walletAcpPage.personalizeWallet")}
                      </button>
                    </div>
                  ) : (
                    <>
                      <label className={s.field}>
                        <span>{c.address}</span>
                        <code className={s.address}>
                          {address || c.unknown}
                        </code>
                      </label>
                      <button
                        className={s.primary}
                        disabled={!address || busy}
                        onClick={() => void copy(address)}
                      >
                        {t("walletAcpPage.copy")}
                      </button>
                    </>
                  )}
                  {depositNote && <p className={s.warning}>{depositNote}</p>}
                  {backup && (
                    <section className={s.backup}>
                      <h3>{c.backup}</h3>
                      <p>{c.backupHint}</p>
                      <code>{backup}</code>
                      <div className={s.actions}>
                        <button
                          className={s.secondary}
                          onClick={() => void copy(backup)}
                        >
                          {t("walletAcpPage.copy")}
                        </button>
                        <button
                          className={s.secondary}
                          onClick={() => setBackup("")}
                        >
                          {c.backupSaved}
                        </button>
                      </div>
                    </section>
                  )}
                  <details className={s.details}>
                    <summary>{t("walletAcpPage.privacyReceive")}</summary>
                    <p className={s.muted}>
                      {t("walletAcpPage.privacyReceiveLead")}
                    </p>
                    {field(
                      t("walletAcpPage.walletPasswordOnce"),
                      <input
                        type="password"
                        value={privacyPassword}
                        onChange={(e) => setPrivacyPassword(e.target.value)}
                        autoComplete="current-password"
                      />,
                    )}
                    <button
                      className={s.secondary}
                      disabled={busy || needsPersonalize}
                      onClick={() => {
                        const secret = privacyPassword;
                        setPrivacyPassword("");
                        void perform(
                          () =>
                            walletAcp.privacyReceiveAddress({
                              wallet_password: secret || undefined,
                              label: "web-wallet",
                            }),
                          (value) => setPrivacyAddress(value.address || ""),
                        );
                      }}
                    >
                      {t("walletAcpPage.newPrivacyAddress")}
                    </button>
                    {privacyAddress && (
                      <>
                        <code className={s.address}>{privacyAddress}</code>
                        <button
                          className={s.secondary}
                          onClick={() => void copy(privacyAddress)}
                        >
                          {t("walletAcpPage.copy")}
                        </button>
                      </>
                    )}
                  </details>
                </div>
                <div className={s.actions}>
                  <Link className={s.secondary} href="/buy-acp">
                    {c.buy}
                  </Link>
                  <Link className={s.secondary} href="/bridge/acp-bsc">
                    {c.bridge}
                  </Link>
                </div>
              </section>
            )}
            {section === "send" && (
              <section className={s.narrow}>
                <div className={s.panel}>
                  <h2>{c.send}</h2>
                  <p className={s.muted}>{c.sendHint}</p>
                  <div className={s.available}>
                    {c.available}
                    <strong>{money(available)} ACP</strong>
                  </div>
                  {attempted ? (
                    <section className={s.stack} aria-live="polite">
                      <h3>
                        {result?.accepted === true && result?.txid
                          ? c.submitted
                          : busy
                            ? t("walletAcpPage.sending")
                            : c.uncertain}
                      </h3>
                      {review && (
                        <dl className={s.facts}>
                          <div>
                            <dt>{c.recipient}</dt>
                            <dd>{review.address}</dd>
                          </div>
                          <div>
                            <dt>{c.total}</dt>
                            <dd>{review.total} ACP</dd>
                          </div>
                        </dl>
                      )}
                      {result?.txid && (
                        <Link
                          className={s.transactionLink}
                          href={`/acp/tx/${encodeURIComponent(result.txid)}`}
                        >
                          {result.txid} ↗
                        </Link>
                      )}
                      {result?.accepted === true && result?.txid ? (
                        <p className={s.muted}>{c.confirmations}</p>
                      ) : (
                        <p className={s.warning}>{c.uncertainHint}</p>
                      )}
                      {result?.job_id && (
                        <div>
                          <code className={s.scope}>ID: {result.job_id}</code>
                          <button
                            className={s.secondary}
                            disabled={busy}
                            onClick={() =>
                              void perform(
                                () => walletAcp.getWithdrawJob(result.job_id!),
                                (value) => {
                                  setResult(value);
                                  if (value.accepted === true)
                                    void refreshWallet();
                                },
                              )
                            }
                          >
                            {c.checkStatus}
                          </button>
                        </div>
                      )}
                      <div className={s.actions}>
                        <button
                          className={s.primary}
                          disabled={busy}
                          onClick={() => {
                            setHistoryState("idle");
                            navigate("history");
                          }}
                        >
                          {c.history}
                        </button>
                        <button
                          className={s.secondary}
                          disabled={busy}
                          onClick={() => {
                            setAttempted(false);
                            setResult(null);
                            setReview(null);
                            setAmount("");
                            setRecipient("");
                            setError("");
                          }}
                        >
                          {c.newTransfer}
                        </button>
                      </div>
                    </section>
                  ) : review ? (
                    <form className={s.stack} onSubmit={submitTransfer}>
                      <h3>{c.review}</h3>
                      <p className={s.warning}>{c.reviewHint}</p>
                      <dl className={s.facts}>
                        <div>
                          <dt>{c.network}</dt>
                          <dd>ACP</dd>
                        </div>
                        <div>
                          <dt>{c.recipient}</dt>
                          <dd>{review.address}</dd>
                        </div>
                        <div>
                          <dt>{c.amount}</dt>
                          <dd>{review.amount} ACP</dd>
                        </div>
                        <div>
                          <dt>{c.fee}</dt>
                          <dd>{review.fee} ACP</dd>
                        </div>
                        <div className={s.total}>
                          <dt>{c.total}</dt>
                          <dd>{review.total} ACP</dd>
                        </div>
                      </dl>
                      {field(
                        t("walletAcpPage.walletPassword"),
                        <input
                          type="password"
                          value={walletPassword}
                          onChange={(e) => setWalletPassword(e.target.value)}
                          autoComplete="current-password"
                          required
                        />,
                      )}
                      <div className={s.actions}>
                        <button
                          className={s.secondary}
                          type="button"
                          onClick={() => {
                            setReview(null);
                            setWalletPassword("");
                          }}
                        >
                          {c.back}
                        </button>
                        <button
                          className={s.primary}
                          disabled={busy || !walletPassword || needsPersonalize}
                          type="submit"
                        >
                          {c.confirm}
                        </button>
                      </div>
                    </form>
                  ) : (
                    <form
                      className={s.stack}
                      onSubmit={(e) => {
                        e.preventDefault();
                        setError("");
                        if (validation.error) {
                          setError(validationMessage(validation.error));
                          return;
                        }
                        setReview({
                          address: recipient.trim(),
                          amount: amount.trim(),
                          fee: fee.trim(),
                          total: validation.total!,
                        });
                      }}
                    >
                      {field(
                        c.recipient,
                        <input
                          placeholder="acp1…"
                          value={recipient}
                          onChange={(e) => setRecipient(e.target.value)}
                          autoComplete="off"
                          spellCheck={false}
                          required
                        />,
                      )}
                      {field(
                        c.amount,
                        <div className={s.amountInput}>
                          <input
                            inputMode="decimal"
                            placeholder="0.00"
                            value={amount}
                            onChange={(e) => setAmount(e.target.value)}
                            required
                          />
                          <button
                            type="button"
                            disabled={available === null}
                            onClick={() =>
                              setAmount(maximumSend(available, fee))
                            }
                          >
                            {c.max}
                          </button>
                        </div>,
                      )}
                      <p className={s.feeLine}>
                        {c.fee}
                        <strong>{fee} ACP</strong>
                      </p>
                      <details className={s.details}>
                        <summary>{c.customFee}</summary>
                        <label className={s.checkbox}>
                          <input
                            type="checkbox"
                            checked={customFee}
                            onChange={(e) => {
                              setCustomFee(e.target.checked);
                              if (!e.target.checked) setFee(DEFAULT_ACP_FEE);
                            }}
                          />
                          {c.customFee}
                        </label>
                        {customFee &&
                          field(
                            c.fee,
                            <input
                              inputMode="decimal"
                              value={fee}
                              onChange={(e) => setFee(e.target.value)}
                            />,
                          )}
                      </details>
                      {amount && validation.error && (
                        <p className={s.warning}>
                          {validationMessage(validation.error)}
                        </p>
                      )}
                      <button
                        className={s.primary}
                        disabled={
                          busy || !!validation.error || needsPersonalize
                        }
                        type="submit"
                      >
                        {c.review} →
                      </button>
                    </form>
                  )}
                </div>
              </section>
            )}
            {section === "history" && (
              <section className={s.panel}>
                <div className={s.sectionHeader}>
                  <div>
                    <h2>{c.history}</h2>
                    <p>{c.historyHint}</p>
                  </div>
                  <Link href="/wallet/credits" className={s.secondary}>
                    {c.openCredits}
                  </Link>
                </div>
                <form
                  className={s.historyForm}
                  onSubmit={(e) => {
                    e.preventDefault();
                    void loadHistory(historyAddress);
                  }}
                >
                  {field(
                    c.address,
                    <input
                      value={historyAddress}
                      onChange={(e) => setHistoryAddress(e.target.value)}
                      placeholder="acp1…"
                      spellCheck={false}
                    />,
                  )}
                  <button
                    className={s.secondary}
                    type="submit"
                    disabled={
                      historyState === "loading" ||
                      !isAcpAddress(historyAddress)
                    }
                  >
                    {t("walletAcpPage.loadHistory")}
                  </button>
                  <button
                    type="button"
                    className={s.secondary}
                    disabled={!address || historyState === "loading"}
                    onClick={() => {
                      setHistoryAddress(address);
                      void loadHistory(address);
                    }}
                  >
                    {t("walletAcpPage.useMyWallet")}
                  </button>
                  {operator && (
                    <button
                      className={s.secondary}
                      type="button"
                      onClick={() => {
                        setHistoryAddress(HOT_ADDRESS);
                        void loadHistory(HOT_ADDRESS);
                      }}
                    >
                      {t("walletAcpPage.useCustodialHot")}
                    </button>
                  )}
                </form>
                {activeAddress && (
                  <code className={s.scope}>{activeAddress}</code>
                )}
                {historyState === "loading" || historyState === "idle" ? (
                  <p role="status" className={s.empty}>
                    {t("walletAcpPage.historyLoading")}
                  </p>
                ) : historyState === "error" ? (
                  <div className={s.error} role="alert">
                    <p>{c.historyError}</p>
                    <button
                      className={s.secondary}
                      onClick={() => void loadHistory(activeAddress || address)}
                    >
                      {t("walletAcpPage.loadHistory")}
                    </button>
                  </div>
                ) : transactions.length === 0 ? (
                  <div className={s.empty}>
                    <WalletIcon name="history" />
                    <h3>{c.emptyHistory}</h3>
                    <button
                      className={s.secondary}
                      onClick={() => navigate("receive")}
                    >
                      {c.receive} ACP
                    </button>
                  </div>
                ) : (
                  <ul className={s.transactions}>
                    {transactions.map((tx) => (
                      <li key={`${tx.txid}-${tx.block_height}`}>
                        <div className={s.transactionIcon}>
                          <WalletIcon
                            name={tx.direction === "in" ? "receive" : "send"}
                          />
                        </div>
                        <div className={s.transactionBody}>
                          <strong>
                            {tx.direction === "in"
                              ? c.incoming
                              : tx.direction === "out"
                                ? c.outgoing
                                : c.self}
                          </strong>
                          <Link href={`/acp/tx/${encodeURIComponent(tx.txid)}`}>
                            {tx.txid}
                          </Link>
                          <span>
                            {Number.isNaN(Date.parse(tx.block_time))
                              ? tx.block_time
                              : new Date(tx.block_time).toLocaleString(
                                  lang,
                                )}{" "}
                            ·{" "}
                            {t("walletAcpPage.blockConf")
                              .replace("{height}", String(tx.block_height))
                              .replace("{conf}", String(tx.confirmations))}
                          </span>
                        </div>
                        <strong
                          className={
                            tx.net_acp.startsWith("-") ? s.negative : s.positive
                          }
                        >
                          {money(tx.net_acp)} ACP
                        </strong>
                      </li>
                    ))}
                  </ul>
                )}
              </section>
            )}
            {section === "security" && (
              <section
                className={`${s.panel} ${s.narrow}`}
                id="password-security"
                ref={securityRef}
                tabIndex={-1}
              >
                <span className={s.eyebrow}>{c.security}</span>
                <h2>{t("walletAcpPage.passwordSectionTitle")}</h2>
                <p className={s.muted}>
                  {t("walletAcpPage.passwordSectionLead")}
                </p>
                {typeof window !== "undefined" &&
                  window.location.hash === "#password-security" && (
                    <p className={s.warning}>
                      {t("walletAcpPage.recoveryLine3")}
                    </p>
                  )}
                <form
                  className={s.stack}
                  onSubmit={(e) => {
                    e.preventDefault();
                    if (passwords.next !== passwords.confirm) {
                      setError(t("walletAcpPage.passwordsMismatch"));
                      return;
                    }
                    const snapshot = passwords;
                    setPasswords({ current: "", next: "", confirm: "" });
                    void perform(
                      () => changePassword(snapshot.current, snapshot.next),
                      () => setNotice(t("walletAcpPage.passwordUpdated")),
                    );
                  }}
                >
                  {field(
                    t("walletAcpPage.currentPassword"),
                    <input
                      type="password"
                      value={passwords.current}
                      onChange={(e) =>
                        setPasswords((p) => ({ ...p, current: e.target.value }))
                      }
                      autoComplete="current-password"
                      required
                      minLength={8}
                    />,
                  )}
                  {field(
                    t("walletAcpPage.newPassword"),
                    <input
                      type="password"
                      value={passwords.next}
                      onChange={(e) =>
                        setPasswords((p) => ({ ...p, next: e.target.value }))
                      }
                      autoComplete="new-password"
                      required
                      minLength={8}
                    />,
                  )}
                  {field(
                    t("walletAcpPage.confirmNewPassword"),
                    <input
                      type="password"
                      value={passwords.confirm}
                      onChange={(e) =>
                        setPasswords((p) => ({ ...p, confirm: e.target.value }))
                      }
                      autoComplete="new-password"
                      required
                      minLength={8}
                    />,
                  )}
                  <button className={s.primary} disabled={busy} type="submit">
                    {t("walletAcpPage.changePasswordSafely")}
                  </button>
                </form>
              </section>
            )}
            {section === "services" && (
              <section className={s.stack}>
                <div>
                  <h2>{c.services}</h2>
                  <p className={s.muted}>{c.servicesHint}</p>
                </div>
                <div className={s.linkGrid}>
                  <Link href="/buy-acp">
                    <strong>{c.buy} →</strong>
                    <span>ACP</span>
                  </Link>
                  <Link href="/bridge/acp-bsc">
                    <strong>{c.bridge} →</strong>
                    <span>BSC / ACP</span>
                  </Link>
                  <Link href="/wallet/credits">
                    <strong>{c.openCredits} →</strong>
                    <span>{c.creditsHint}</span>
                  </Link>
                </div>
                <div className={s.toolButtons}>
                  {[
                    ["otc", "OTC"],
                    ["assay", "GC / MS"],
                    ["ownership", c.assetDocs],
                    ["bulk", t("walletAcpPage.bulkDistribution")],
                  ].map(([key, label]) => (
                    <button
                      key={key}
                      disabled={busy}
                      className={tool === key ? s.primary : s.secondary}
                      onClick={() => setTool(tool === key ? "" : key)}
                    >
                      {label}
                    </button>
                  ))}
                </div>
                {tool === "otc" && <OtcDesk defaultPayoutAddress={address} />}{" "}
                {tool === "assay" && <AssayDesk />}{" "}
                {tool === "ownership" && <OwnershipDesk />}{" "}
                {tool === "bulk" && (
                  <WalletBulkTransfer
                    key={user?.id}
                    onBusyChange={setBusy}
                    available={available}
                    disabled={busy || needsPersonalize}
                    onComplete={() => {
                      void refreshWallet();
                      setHistoryState("idle");
                    }}
                  />
                )}
              </section>
            )}
          </>
        )}
      </main>
    </div>
  );
}
