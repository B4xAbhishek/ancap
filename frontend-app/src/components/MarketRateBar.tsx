"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useLanguage } from "@/components/LanguageProvider";
import { marketData } from "@/lib/api";
import { formatUsdMicro } from "@/lib/formatUsd";

const GT_POOL =
  "https://www.geckoterminal.com/bsc/pools/0xf391ca2bcbab93afa23326ebf1e35db950841601";

type MarketRow = {
  id?: string;
  symbol?: string;
  price?: string | null;
};

export function MarketRateBar() {
  const { t } = useLanguage();
  const [acp, setAcp] = useState<string | null>(null);
  const [wacp, setWacp] = useState<string | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      try {
        const payload = await marketData.prices("usd");
        if (cancelled) return;
        const list: MarketRow[] = Array.isArray(payload?.prices) ? payload.prices : [];
        const acpRow = list.find((r) => r.symbol === "ACP" || r.id === "acp");
        const wacpRow = list.find((r) => r.symbol === "wACP" || r.id === "wacp");
        setAcp(acpRow?.price ?? null);
        setWacp(wacpRow?.price ?? null);
      } catch {
        if (!cancelled) {
          setAcp(null);
          setWacp(null);
        }
      } finally {
        if (!cancelled) setReady(true);
      }
    };
    void load();
    const timer = window.setInterval(() => void load(), 60_000);
    return () => {
      cancelled = true;
      window.clearInterval(timer);
    };
  }, []);

  if (!ready || (!acp && !wacp)) return null;

  return (
    <div className="market-rate-bar" role="status" aria-live="polite">
      <div className="market-rate-bar__inner">
        <span className="market-rate-bar__label">{t("marketRateBar.label")}</span>
        <span className="market-rate-bar__pair">
          <strong>wACP</strong> {formatUsdMicro(wacp)}
        </span>
        <span className="market-rate-bar__sep" aria-hidden>
          ·
        </span>
        <span className="market-rate-bar__pair">
          <strong>ACP</strong> {formatUsdMicro(acp)}
          <span className="market-rate-bar__hint">{t("marketRateBar.wrapRatio")}</span>
        </span>
        <a
          className="market-rate-bar__link"
          href={GT_POOL}
          target="_blank"
          rel="noopener noreferrer"
        >
          {t("marketRateBar.gecko")}
        </a>
        <Link href="/legal/market-data" className="market-rate-bar__link">
          {t("marketRateBar.legal")}
        </Link>
      </div>
    </div>
  );
}
