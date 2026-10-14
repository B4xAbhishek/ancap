"use client";

import * as React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "./AuthProvider";
import { useLanguage } from "./LanguageProvider";
import { useWallet } from "./WalletProvider";
import { useTheme } from "./ThemeProvider";
import { MarketRateBar } from "./MarketRateBar";
import { getPreferredEvmProvider } from "@/lib/evmProvider";
import type { Language } from "@/locales/translations";

type NavItem = {
  label: string;
  href: string;
  /** When set, label text comes from translations (e.g. nav.acpWallet). */
  i18nKey?: string;
};

type NavGroup = {
  titleKey: string;
  items: NavItem[];
};

function navItemLabel(item: NavItem, t: (key: string) => string): string {
  return item.i18nKey ? t(item.i18nKey) : item.label;
}

const spotlightPublic: NavItem[] = [
  { label: "Workflows", href: "/ai/workflows", i18nKey: "positioning.workflows" },
  { label: "Solutions", href: "/projects", i18nKey: "positioning.solutions" },
  { label: "Creators", href: "/creators", i18nKey: "positioning.creators" },
  { label: "Developers", href: "/developers", i18nKey: "nav.developers" },
  { label: "Investors", href: "/investors", i18nKey: "positioning.investors" },
];
const spotlightAuth: NavItem[] = [
  { label: "Dashboard", href: "/dashboard", i18nKey: "nav.dashboard" },
  ...spotlightPublic,
];
const explorePublicGroups: NavGroup[] = [
  { titleKey: "positioning.platform", items: [
    { label: "Pricing", href: "/pricing", i18nKey: "nav.pricing" },
    { label: "Free snapshot", href: "/token-snapshot", i18nKey: "nav.freeSnapshot" },
    { label: "MCP", href: "/mcp" },
    { label: "ACP", href: "/acp" },
    { label: "Wallet", href: "/wallet/acp", i18nKey: "nav.acpWallet" },
    { label: "Bridge", href: "/bridge/acp-bsc", i18nKey: "nav.bridgeAcpBsc" },
  ] },
  { titleKey: "positioning.trust", items: [
    { label: "Proof Center", href: "/proof-center", i18nKey: "nav.proofCenter" },
    { label: "Explorer", href: "/explorer", i18nKey: "nav.explorer" },
    { label: "Whitepaper", href: "/whitepaper", i18nKey: "nav.whitepaper" },
    { label: "Legal", href: "/legal", i18nKey: "nav.legal" },
    { label: "Status", href: "/status", i18nKey: "nav.system" },
  ] },
];
const exploreAuthGroups: NavGroup[] = [
  { titleKey: "positioning.workspace", items: [
    { label: "Runs", href: "/ai/runs", i18nKey: "nav.runs" },
    { label: "Seller", href: "/dashboard/seller", i18nKey: "nav.sellerDashboard" },
    { label: "Builder", href: "/strategy-builder", i18nKey: "nav.builder" },
    { label: "Agents", href: "/agents", i18nKey: "nav.agents" },
    { label: "Organizations", href: "/organizations", i18nKey: "nav.organizations" },
    { label: "Billing", href: "/billing", i18nKey: "nav.billing" },
    { label: "Analytics", href: "/dashboard/analytics", i18nKey: "nav.analytics" },
    { label: "Notifications", href: "/notifications", i18nKey: "nav.notifications" },
  ] },
  ...explorePublicGroups,
];

function cn(...classes: Array<string | false | null | undefined>) {
  return classes.filter(Boolean).join(" ");
}

/** Single elegant row — no wrap wall, no clip. */
const navSpotlightRow =
  "flex w-full min-w-0 items-center gap-0.5 overflow-x-auto overscroll-x-contain px-1 py-0.5 [scrollbar-width:none] [-ms-overflow-style:none] [&::-webkit-scrollbar]:hidden";

const actionGhost =
  "inline-flex items-center justify-center rounded-lg border border-white/10 bg-white/[0.03] px-3 py-1.5 text-[12px] font-medium text-white/80 transition duration-200 hover:border-white/18 hover:bg-white/[0.07] hover:text-white active:scale-[0.98]";
const actionPrimary =
  "inline-flex items-center justify-center rounded-lg bg-emerald-400 px-3.5 py-1.5 text-[12px] font-semibold text-[#041018] transition duration-200 hover:bg-emerald-300 active:scale-[0.98]";
const actionAcp =
  "inline-flex items-center justify-center rounded-lg border border-emerald-400/35 bg-emerald-400/[0.08] px-3 py-1.5 text-[12px] font-semibold tracking-wide text-emerald-100 transition duration-200 hover:border-emerald-400/50 hover:bg-emerald-400/[0.14] hover:text-white active:scale-[0.98]";
const iconBtn =
  "inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-white/10 bg-white/[0.03] text-white/55 transition duration-200 hover:border-white/18 hover:bg-white/[0.07] hover:text-white active:scale-[0.97]";

type LangCode = Language;
const LANG_OPTIONS: ReadonlyArray<{ code: LangCode; label: string }> = [
  { code: "en", label: "EN" },
  { code: "ru", label: "RU" },
  { code: "uk", label: "UK" },
  { code: "de", label: "DE" },
  { code: "zh-Hant", label: "繁中" },
];

function LangSwitcher({
  lang,
  setLang,
  size = "default",
}: {
  lang: LangCode;
  setLang: (l: LangCode) => void;
  size?: "default" | "compact";
}) {
  const onKeyDown = (e: React.KeyboardEvent<HTMLButtonElement>, idx: number) => {
    if (e.key !== "ArrowRight" && e.key !== "ArrowLeft" && e.key !== "Home" && e.key !== "End") return;
    e.preventDefault();
    let nextIdx = idx;
    if (e.key === "ArrowRight") nextIdx = (idx + 1) % LANG_OPTIONS.length;
    else if (e.key === "ArrowLeft") nextIdx = (idx - 1 + LANG_OPTIONS.length) % LANG_OPTIONS.length;
    else if (e.key === "Home") nextIdx = 0;
    else if (e.key === "End") nextIdx = LANG_OPTIONS.length - 1;
    setLang(LANG_OPTIONS[nextIdx].code);
  };

  const padCls =
    size === "compact"
      ? "rounded-md px-1.5 py-1 text-[10px] font-semibold tracking-wide transition sm:px-2 sm:py-1 sm:text-[11px]"
      : "rounded-md px-2 py-1 text-[11px] font-semibold tracking-wide transition";
  const wrapCls =
    size === "compact"
      ? "flex items-center gap-0.5 rounded-lg border border-white/10 bg-black/25 p-0.5"
      : "flex items-center gap-0.5 rounded-lg border border-white/10 bg-black/25 p-0.5";

  return (
    <div role="radiogroup" aria-label="Language" className={wrapCls}>
      {LANG_OPTIONS.map((opt, idx) => {
        const active = lang === opt.code;
        return (
          <button
            key={opt.code}
            type="button"
            role="radio"
            aria-checked={active}
            tabIndex={active ? 0 : -1}
            onClick={() => setLang(opt.code)}
            onKeyDown={(e) => onKeyDown(e, idx)}
            className={cn(
              padCls,
              active
                ? "bg-white/[0.12] text-white shadow-[inset_0_0_0_1px_rgba(255,255,255,0.08)]"
                : "text-white/40 hover:text-white/80"
            )}
          >
            {opt.label}
          </button>
        );
      })}
    </div>
  );
}

/** Desktop spotlight chip — full label visible, soft desire hover. */
function PillNavLink({
  item,
  label,
  active,
  onClick,
}: {
  item: NavItem;
  label: string;
  active: boolean;
  onClick?: () => void;
}) {
  const isSectionJump = item.href.startsWith("/#");
  return (
    <Link
      href={item.href}
      onClick={onClick}
      className={cn(
        "relative shrink-0 whitespace-nowrap rounded-lg font-medium tracking-[-0.01em] transition duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400/40 focus-visible:ring-offset-2 focus-visible:ring-offset-[#070b16]",
        active
          ? "bg-white/[0.12] px-3 py-1.5 text-[13px] text-white shadow-[inset_0_0_0_1px_rgba(255,255,255,0.12)]"
          : isSectionJump
            ? "px-2.5 py-1.5 text-[13px] text-emerald-100/75 hover:text-white"
            : "px-3 py-1.5 text-[13px] text-white/55 hover:bg-white/[0.07] hover:text-white"
      )}
    >
      <span className="relative z-10">{label}</span>
      {active && !isSectionJump ? (
        <span
          className="pointer-events-none absolute inset-x-2.5 -bottom-px h-px bg-gradient-to-r from-transparent via-emerald-300/80 to-transparent"
          aria-hidden
        />
      ) : null}
    </Link>
  );
}

function ExploreMenu({
  groups,
  open,
  onOpenChange,
  pathname,
  t,
}: {
  groups: NavGroup[];
  open: boolean;
  onOpenChange: (v: boolean) => void;
  pathname: string;
  t: (key: string) => string;
}) {
  const rootRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    if (!open) return;
    const onDoc = (e: MouseEvent) => {
      if (!rootRef.current?.contains(e.target as Node)) onOpenChange(false);
    };
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onOpenChange(false);
    };
    document.addEventListener("mousedown", onDoc);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onDoc);
      document.removeEventListener("keydown", onKey);
    };
  }, [open, onOpenChange]);

  return (
    <div ref={rootRef} className="relative shrink-0">
      <button
        type="button"
        aria-expanded={open}
        aria-haspopup="menu"
        onClick={() => onOpenChange(!open)}
        className={cn(
          "inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-[13px] font-semibold tracking-[-0.01em] transition duration-200",
          open
            ? "bg-emerald-400/15 text-emerald-50 shadow-[inset_0_0_0_1px_rgba(52,211,153,0.35)]"
            : "text-emerald-100/80 hover:bg-emerald-400/10 hover:text-white"
        )}
      >
        {t("nav.explore")}
        <span className={cn("text-[10px] transition duration-200", open && "rotate-180")} aria-hidden>
          ▾
        </span>
      </button>
      {open ? (
        <div
          role="menu"
          className="absolute right-0 top-[calc(100%+8px)] z-[120] w-[min(calc(100vw-1.5rem),52rem)] max-h-[min(75vh,42rem)] animate-[navSheetIn_180ms_ease-out] overflow-x-hidden overflow-y-auto overscroll-contain rounded-2xl border border-white/14 bg-[#0c1424] p-3.5 shadow-[0_28px_80px_rgba(0,0,0,0.72)] sm:p-4 [scrollbar-width:thin] [scrollbar-color:rgba(255,255,255,0.22)_transparent]"
        >
          <div className="grid min-w-0 gap-3 sm:grid-cols-2 sm:gap-4 lg:grid-cols-3">
            {groups.map((group) => (
              <div
                key={group.titleKey}
                className="min-w-0 rounded-xl border border-white/[0.08] bg-[#101a2e] p-2.5 sm:p-3"
              >
                <div className="mb-2 break-words text-[10px] font-semibold uppercase tracking-[0.16em] text-emerald-200/70">
                  {t(group.titleKey)}
                </div>
                <div className="flex min-w-0 flex-col gap-0.5">
                  {group.items.map((item) => {
                    const active = !item.href.startsWith("/#") && pathname === item.href;
                    return (
                      <Link
                        key={item.href}
                        role="menuitem"
                        href={item.href}
                        onClick={() => onOpenChange(false)}
                        className={cn(
                          "min-w-0 break-words rounded-lg px-2 py-1.5 text-[13px] leading-snug transition duration-150",
                          active
                            ? "bg-white/[0.12] text-white"
                            : "text-white/75 hover:bg-white/[0.07] hover:text-white"
                        )}
                      >
                        {navItemLabel(item, t)}
                      </Link>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : null}
    </div>
  );
}

function MobileNavRow({
  item,
  label,
  active,
  onNavigate,
}: {
  item: NavItem;
  label: string;
  active: boolean;
  onNavigate: () => void;
}) {
  return (
    <Link
      href={item.href}
      onClick={onNavigate}
      className={cn(
        "group flex min-h-[44px] min-w-0 items-center justify-between gap-3 overflow-hidden rounded-xl border px-3.5 py-2.5 text-[14px] leading-snug transition duration-200 active:scale-[0.99]",
        active
          ? "border-emerald-400/30 bg-emerald-400/[0.08] text-white"
          : "border-white/[0.08] bg-[#0a1222] text-white/80 hover:border-white/14 hover:bg-white/[0.06] hover:text-white"
      )}
    >
      <span className="min-w-0 break-words font-medium">{label}</span>
      <span
        className={cn(
          "text-[12px] transition duration-200 group-hover:translate-x-0.5",
          active ? "text-emerald-300/80" : "text-white/20"
        )}
        aria-hidden
      >
        →
      </span>
    </Link>
  );
}

function BrandMark() {
  return (
    <Link href="/" className="group inline-flex min-w-0 items-center gap-2.5 sm:gap-3">
      <span className="relative flex h-8 w-8 shrink-0 items-center justify-center overflow-hidden rounded-lg border border-white/12 bg-gradient-to-br from-white/[0.1] to-white/[0.02] transition duration-300 group-hover:border-emerald-400/35 group-hover:from-emerald-400/15">
        <span className="absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,rgba(52,211,153,0.25),transparent_55%)] opacity-80" />
        <span className="relative font-mono text-[11px] font-bold tracking-[-0.04em] text-emerald-200/95">A</span>
      </span>
      <span className="flex min-w-0 flex-col leading-none">
        <span className="truncate text-[18px] font-semibold tracking-[-0.03em] text-white sm:text-[22px]">ANCAP</span>
        <span className="mt-0.5 hidden text-[9px] font-medium uppercase tracking-[0.22em] text-white/35 sm:block">
          ACP platform
        </span>
      </span>
    </Link>
  );
}

export function Navigation() {
  const { isAuthenticated, user, logout, loginWithWallet } = useAuth();
  const { lang, setLang, t } = useLanguage();
  const { isConnected, isConnecting, shortAddress, connect, clearError, chainId } = useWallet();
  const { theme, toggleTheme } = useTheme();
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);
  const [exploreOpen, setExploreOpen] = React.useState(false);

  const spotlight = isAuthenticated ? spotlightAuth : spotlightPublic;
  const exploreGroups = isAuthenticated ? exploreAuthGroups : explorePublicGroups;

  React.useEffect(() => {
    setMobileMenuOpen(false);
    setExploreOpen(false);
  }, [pathname]);

  React.useEffect(() => {
    if (!mobileMenuOpen && !exploreOpen) return;
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = prev;
    };
  }, [mobileMenuOpen, exploreOpen]);

  const userLabel = user?.display_name || user?.email || "";

  const handleWalletContinue = async () => {
    clearError();
    if (!isConnected) {
      await connect();
      return;
    }
    const provider = getPreferredEvmProvider();
    if (!isAuthenticated && provider) {
      const accountsRaw = await provider.request({ method: "eth_accounts" });
      const accounts = Array.isArray(accountsRaw) ? accountsRaw : [];
      const address = typeof accounts[0] === "string" ? accounts[0] : "";
      if (address) await loginWithWallet(address, chainId);
    }
  };

  return (
    <header className="sticky top-0 z-[100] border-b border-white/[0.06] bg-[#070b16]/78 backdrop-blur-2xl supports-[backdrop-filter]:bg-[#070b16]/65">
      {pathname?.startsWith("/wallet") || pathname?.startsWith("/bridge") || pathname?.startsWith("/markets") ? <MarketRateBar /> : null}
      <div
        className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-emerald-300/40 to-transparent"
        aria-hidden
      />
      <div
        className="pointer-events-none absolute inset-x-8 top-0 h-8 bg-[radial-gradient(ellipse_at_top,rgba(52,211,153,0.08),transparent_70%)]"
        aria-hidden
      />

      <div className="relative mx-auto max-w-[1440px] px-4 sm:px-6 lg:px-8 xl:px-10">
        <div className="flex min-h-[64px] items-center justify-between gap-2 py-2 sm:gap-3 lg:min-h-[60px]">
          <div className="flex min-w-0 shrink-0 items-center gap-2 sm:gap-5">
            <BrandMark />
          </div>

          <div className="hidden min-w-0 shrink-0 items-center gap-1.5 sm:gap-2 lg:flex">
            <Link href="/wallet/acp" className={actionAcp}>
              {t("nav.acpWallet")}
            </Link>
            {isConnected ? (
              <button
                type="button"
                onClick={() => {
                  const provider = getPreferredEvmProvider();
                  if (!isAuthenticated && provider) {
                    provider
                      .request({ method: "eth_accounts" })
                      .then(async (accountsRaw) => {
                        const accounts = Array.isArray(accountsRaw) ? accountsRaw : [];
                        const address = typeof accounts[0] === "string" ? accounts[0] : "";
                        if (address) await loginWithWallet(address, chainId);
                      })
                      .catch(() => undefined);
                  }
                }}
                className={cn(actionGhost, "font-mono text-[11px] text-cyan-100/90")}
              >
                {shortAddress || t("auth.walletConnected")}
              </button>
            ) : (
              <button
                type="button"
                onClick={handleWalletContinue}
                disabled={isConnecting}
                className={cn(actionGhost, "disabled:cursor-not-allowed disabled:opacity-55")}
              >
                {isConnecting ? t("auth.connectingWallet") : t("auth.connectWallet")}
              </button>
            )}
            <div className="mx-0.5 h-5 w-px shrink-0 bg-white/10" />
            <button
              type="button"
              onClick={toggleTheme}
              aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} theme`}
              className={iconBtn}
            >
              {theme === "dark" ? (
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>
              ) : (
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
              )}
            </button>
            <LangSwitcher lang={lang} setLang={setLang} />
            <div className="mx-0.5 h-5 w-px bg-white/10" />
            {isAuthenticated ? (
              <>
                <span className="max-w-[9rem] truncate text-[12px] font-medium text-white/55" title={userLabel}>
                  {userLabel}
                </span>
                <button onClick={logout} className={actionGhost}>
                  {t("nav.logout")}
                </button>
              </>
            ) : (
              <>
                <Link href="/login" className={actionGhost}>
                  {t("nav.login")}
                </Link>
                <Link href="/register" className={actionPrimary}>
                  {t("nav.register")}
                </Link>
              </>
            )}
          </div>

          <div className="flex min-w-0 flex-1 items-center justify-end gap-1.5 sm:gap-2 lg:hidden">
            <Link
              href="/wallet/acp"
              aria-label={t("nav.acpWallet")}
              title={t("nav.acpWallet")}
              className="hidden h-9 min-w-9 shrink-0 items-center justify-center rounded-lg border border-emerald-400/35 bg-emerald-400/[0.1] px-2 text-[10px] font-semibold text-emerald-50 transition hover:bg-emerald-400/[0.18] sm:inline-flex sm:h-9 sm:px-2.5 sm:text-[11px]"
            >
              <span className="sm:hidden">ACP</span>
              <span className="hidden sm:inline">{t("nav.acpWallet")}</span>
            </Link>
            <div className="hidden min-[390px]:block">
              <LangSwitcher lang={lang} setLang={setLang} size="compact" />
            </div>
            <button
              type="button"
              onClick={toggleTheme}
              aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} theme`}
              className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-white/10 bg-white/[0.03] text-white/55 transition hover:bg-white/[0.08] hover:text-white"
            >
              {theme === "dark" ? (
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>
              ) : (
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
              )}
            </button>
            <button
              onClick={() => setMobileMenuOpen((v) => !v)}
              className={cn(
                "inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border text-white/90 transition",
                mobileMenuOpen
                  ? "border-emerald-400/35 bg-emerald-400/10 text-emerald-100"
                  : "border-white/10 bg-white/[0.03] hover:bg-white/[0.08]"
              )}
              aria-expanded={mobileMenuOpen}
              aria-label={mobileMenuOpen ? "Close menu" : "Open menu"}
            >
              {mobileMenuOpen ? (
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" aria-hidden><path d="M18 6 6 18M6 6l12 12"/></svg>
              ) : (
                <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" aria-hidden><path d="M4 7h16M4 12h16M4 17h16"/></svg>
              )}
            </button>
          </div>
        </div>

        {/* One magnetic row + Explore — no wrap wall, labels stay whole */}
        <div className="hidden pb-2.5 lg:block">
          <div className="relative w-full min-w-0 rounded-xl border border-white/[0.08] bg-gradient-to-r from-black/35 via-emerald-950/10 to-black/25 p-1.5 backdrop-blur-sm">
            <div className="flex min-w-0 items-center gap-1">
              <nav className={cn(navSpotlightRow, "flex-1")} aria-label={t("nav.main")}>
                {spotlight.map((item) => (
                  <PillNavLink
                    key={item.href}
                    item={item}
                    label={navItemLabel(item, t)}
                    active={!item.href.startsWith("/#") && pathname === item.href}
                  />
                ))}
              </nav>
              <div className="mx-0.5 h-5 w-px shrink-0 bg-white/10" aria-hidden />
              <ExploreMenu
                groups={exploreGroups}
                open={exploreOpen}
                onOpenChange={setExploreOpen}
                pathname={pathname ?? ""}
                t={t}
              />
            </div>
          </div>
        </div>
      </div>

      {mobileMenuOpen && (
        <>
          <button
            type="button"
            className="fixed inset-0 z-[90] bg-black/60 backdrop-blur-[3px] lg:hidden"
            aria-label="Close menu"
            onClick={() => setMobileMenuOpen(false)}
          />
          <div className="relative z-[95] animate-[navSheetIn_220ms_ease-out] border-t border-white/[0.1] bg-[#0c1424] shadow-[0_24px_80px_rgba(0,0,0,0.72)] lg:hidden">
            <div className="mx-auto max-h-[min(85dvh,calc(100dvh-5.5rem))] max-w-[1440px] overflow-x-hidden overflow-y-auto overscroll-y-contain px-4 py-4 pb-[max(1rem,env(safe-area-inset-bottom))] sm:px-6 [scrollbar-width:thin] [scrollbar-color:rgba(255,255,255,0.22)_transparent]">
              <div className="mb-4 min-[390px]:hidden">
                <LangSwitcher lang={lang} setLang={setLang} />
              </div>
              {isAuthenticated ? (
                <div className="grid gap-5">
                  <div>
                    <div className="mb-2.5 flex items-center gap-2">
                      <span className="h-px w-4 bg-emerald-400/70" />
                      <span className="text-[10px] font-semibold uppercase tracking-[0.22em] text-white/40">
                        {t("nav.groupSpotlight")}
                      </span>
                    </div>
                    <div className="flex flex-col gap-1.5">
                      {spotlight.map((item) => (
                        <MobileNavRow
                          key={item.href}
                          item={item}
                          label={navItemLabel(item, t)}
                          active={!item.href.startsWith("/#") && pathname === item.href}
                          onNavigate={() => setMobileMenuOpen(false)}
                        />
                      ))}
                    </div>
                  </div>

                  {exploreGroups.map((group) => (
                    <div
                      key={group.titleKey}
                      className="min-w-0 overflow-hidden rounded-xl border border-white/[0.08] bg-[#101a2e] p-3"
                    >
                      <div className="mb-2.5 flex min-w-0 items-center gap-2">
                        <span className="h-px w-4 shrink-0 bg-cyan-400/60" />
                        <span className="min-w-0 break-words text-[10px] font-semibold uppercase tracking-[0.18em] text-white/50">
                          {t(group.titleKey)}
                        </span>
                      </div>
                      <div className="flex min-w-0 flex-col gap-1.5">
                        {group.items.map((item) => (
                          <MobileNavRow
                            key={item.href}
                            item={item}
                            label={navItemLabel(item, t)}
                            active={!item.href.startsWith("/#") && pathname === item.href}
                            onNavigate={() => setMobileMenuOpen(false)}
                          />
                        ))}
                      </div>
                    </div>
                  ))}

                  <div className="flex items-center justify-between gap-3 border-t border-white/10 pt-4">
                    <div className="flex min-w-0 flex-col gap-2">
                      <div className="truncate text-[13px] text-white/75" title={userLabel}>
                        {userLabel}
                      </div>
                      <Link
                        href="/wallet/acp"
                        onClick={() => setMobileMenuOpen(false)}
                        className={cn(actionAcp, "w-fit")}
                      >
                        {t("nav.acpWallet")}
                      </Link>
                    </div>
                    <button
                      onClick={() => {
                        logout();
                        setMobileMenuOpen(false);
                      }}
                      className={actionGhost}
                    >
                      {t("nav.logout")}
                    </button>
                  </div>
                </div>
              ) : (
                <div className="grid gap-4">
                  <div>
                    <div className="mb-2.5 flex items-center gap-2">
                      <span className="h-px w-4 bg-emerald-400/70" />
                      <span className="text-[10px] font-semibold uppercase tracking-[0.22em] text-white/40">
                        {t("nav.groupSpotlight")}
                      </span>
                    </div>
                    <div className="flex flex-col gap-1.5">
                      {spotlight.map((item) => (
                        <MobileNavRow
                          key={item.href}
                          item={item}
                          label={navItemLabel(item, t)}
                          active={!item.href.startsWith("/#") && pathname === item.href}
                          onNavigate={() => setMobileMenuOpen(false)}
                        />
                      ))}
                    </div>
                  </div>

                  {exploreGroups.map((group) => (
                    <div
                      key={group.titleKey}
                      className="min-w-0 overflow-hidden rounded-xl border border-white/[0.08] bg-[#101a2e] p-3"
                    >
                      <div className="mb-2.5 flex min-w-0 items-center gap-2">
                        <span className="h-px w-4 shrink-0 bg-cyan-400/60" />
                        <span className="min-w-0 break-words text-[10px] font-semibold uppercase tracking-[0.18em] text-white/50">
                          {t(group.titleKey)}
                        </span>
                      </div>
                      <div className="flex min-w-0 flex-col gap-1.5">
                        {group.items.map((item) => (
                          <MobileNavRow
                            key={item.href}
                            item={item}
                            label={navItemLabel(item, t)}
                            active={!item.href.startsWith("/#") && pathname === item.href}
                            onNavigate={() => setMobileMenuOpen(false)}
                          />
                        ))}
                      </div>
                    </div>
                  ))}

                  <Link
                    href="/wallet/acp"
                    onClick={() => setMobileMenuOpen(false)}
                    className="flex min-h-[44px] items-center rounded-xl border border-emerald-400/30 bg-emerald-400/[0.08] px-3.5 py-2.5 text-[14px] font-medium text-emerald-100 transition hover:bg-emerald-400/[0.14]"
                  >
                    {t("nav.acpWallet")}
                  </Link>
                  <button
                    type="button"
                    onClick={async () => {
                      setMobileMenuOpen(false);
                      if (!isConnected) {
                        clearError();
                        await connect();
                        return;
                      }
                      const provider = getPreferredEvmProvider();
                      if (!isAuthenticated && provider) {
                        const accountsRaw = await provider.request({ method: "eth_accounts" });
                        const accounts = Array.isArray(accountsRaw) ? accountsRaw : [];
                        const address = typeof accounts[0] === "string" ? accounts[0] : "";
                        if (address) await loginWithWallet(address, chainId);
                      }
                    }}
                    className="flex min-h-[44px] items-center rounded-xl border border-white/[0.06] bg-white/[0.02] px-3.5 py-2.5 text-[14px] text-white/70 transition hover:border-white/12 hover:bg-white/[0.05]"
                  >
                    {isConnected
                      ? shortAddress || t("auth.walletConnected")
                      : isConnecting
                        ? t("auth.connectingWallet")
                        : t("auth.connectWallet")}
                  </button>
                  <div className="flex items-center gap-2 border-t border-white/10 pt-3">
                    <Link
                      href="/login"
                      onClick={() => setMobileMenuOpen(false)}
                      className={cn(actionGhost, "flex-1 py-2.5 text-center")}
                    >
                      {t("nav.login")}
                    </Link>
                    <Link
                      href="/register"
                      onClick={() => setMobileMenuOpen(false)}
                      className={cn(actionPrimary, "flex-1 py-2.5 text-center")}
                    >
                      {t("nav.register")}
                    </Link>
                  </div>
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </header>
  );
}
