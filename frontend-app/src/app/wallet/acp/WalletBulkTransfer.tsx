"use client";
import { useEffect, useRef, useState, type FormEvent } from "react";
import { useLanguage } from "@/components/LanguageProvider";
import { walletAcp } from "@/lib/api";
import { DEFAULT_ACP_FEE, parseBulkTransfers } from "@/lib/walletTransfer";
import { walletUxCopy } from "@/locales/walletUx";
import s from "./wallet.module.css";

export function WalletBulkTransfer({
  available,
  disabled,
  onComplete,
  onBusyChange,
}: {
  available: string | null;
  disabled: boolean;
  onComplete: () => void;
  onBusyChange: (busy: boolean) => void;
}) {
  const { lang, t } = useLanguage(),
    c = walletUxCopy[lang];
  const [text, setText] = useState(""),
    [password, setPassword] = useState(""),
    [error, setError] = useState("");
  const [preview, setPreview] = useState<ReturnType<
    typeof parseBulkTransfers
  > | null>(null);
  const [results, setResults] = useState<
    { address: string; amount: string; txid?: string; ok: boolean }[]
  >([]);
  const [started, setStarted] = useState(false),
    [busy, setBusy] = useState(false);
  const alive = useRef(true),
    lock = useRef(false);
  useEffect(() => {
    alive.current = true;
    return () => {
      alive.current = false;
      onBusyChange(false);
    };
  }, [onBusyChange]);
  function review(e: FormEvent) {
    e.preventDefault();
    setError("");
    try {
      setPreview(parseBulkTransfers(text, available));
    } catch {
      setError(c.rowsError + " " + c.balanceError);
    }
  }
  async function send(e: FormEvent) {
    e.preventDefault();
    if (lock.current || !preview || !password || started) return;
    // Revalidate every row against the current balance before the first side effect.
    try {
      parseBulkTransfers(
        preview.rows.map((row) => `${row.address} ${row.amount}`).join("\n"),
        available,
      );
    } catch {
      setError(c.balanceError);
      return;
    }
    lock.current = true;
    setStarted(true);
    setBusy(true);
    onBusyChange(true);
    setError("");
    const secret = password;
    setPassword("");
    try {
      for (const row of preview.rows) {
        if (!alive.current) break;
        try {
          const result = await walletAcp.withdraw({
            to_address: row.address,
            amount_acp: row.amount,
            fee_acp: DEFAULT_ACP_FEE,
            wallet_password: secret,
          });
          if (!alive.current) break;
          const ok =
            result?.accepted === true &&
            typeof result?.txid === "string" &&
            !!result.txid;
          setResults((prev) => [
            ...prev,
            { ...row, ok, txid: result?.txid || undefined },
          ]);
          if (!ok) {
            setError(c.uncertainHint);
            break;
          }
        } catch {
          if (alive.current) {
            setResults((prev) => [...prev, { ...row, ok: false }]);
            setError(c.uncertainHint);
          }
          break;
        }
      }
    } finally {
      lock.current = false;
      if (alive.current) {
        setBusy(false);
        onBusyChange(false);
        onComplete();
      }
    }
  }
  return (
    <section className={s.panel}>
      <h2>{t("walletAcpPage.bulkDistribution")}</h2>
      <p className={s.muted}>{c.bulkHint}</p>
      {error && (
        <p className={s.error} role="alert">
          {error}
        </p>
      )}
      {started ? (
        <div className={s.stack}>
          <p>{busy ? t("walletAcpPage.processing") : c.uncertainHint}</p>
          {results.map((row, i) => (
            <div className={s.panel} key={row.address}>
              <strong>
                {i + 1}. {row.amount} ACP
              </strong>
              <code className={s.address}>{row.address}</code>
              <p>{row.ok ? c.submitted : c.uncertain}</p>
              {row.txid && (
                <a
                  className={s.transactionLink}
                  href={`/acp/tx/${encodeURIComponent(row.txid)}`}
                >
                  {row.txid}
                </a>
              )}
            </div>
          ))}
          <p className={s.muted}>
            {results.length} / {preview?.rows.length}
          </p>
        </div>
      ) : preview ? (
        <form className={s.stack} onSubmit={send}>
          <h3>{c.review}</h3>
          <p className={s.warning}>{c.reviewHint}</p>
          {preview.rows.map((row) => (
            <p className={s.metricLine} key={row.address}>
              <code className={s.transactionLink}>{row.address}</code>
              <strong>{row.amount} ACP</strong>
            </p>
          ))}
          <p className={s.available}>
            {c.total}
            <strong>{preview.total} ACP</strong>
          </p>
          <label className={s.field}>
            <span>{t("walletAcpPage.walletPassword")}</span>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
            />
          </label>
          <div className={s.actions}>
            <button
              className={s.secondary}
              type="button"
              onClick={() => {
                setPreview(null);
                setPassword("");
              }}
            >
              {c.back}
            </button>
            <button
              className={s.primary}
              disabled={disabled || !password}
              type="submit"
            >
              {c.confirm}
            </button>
          </div>
        </form>
      ) : (
        <form className={s.stack} onSubmit={review}>
          <label className={s.field}>
            <span>{t("walletAcpPage.bulkDistribution")}</span>
            <textarea
              rows={6}
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="acp1… 1.25"
              required
            />
          </label>
          <button
            className={s.secondary}
            disabled={disabled || !text.trim()}
            type="submit"
          >
            {c.review}
          </button>
        </form>
      )}
    </section>
  );
}
