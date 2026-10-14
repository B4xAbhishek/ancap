"use client";
import Link from "next/link";
import { Navigation } from "@/components/Navigation";
import { useLanguage } from "@/components/LanguageProvider";
import { investorDocsByLang } from "@/locales/investorDocs";

/** Public summary of docs/investors/DEMO_SCRIPT_5MIN.md */
export default function InvestorDemoPage() {
  const { lang } = useLanguage();
  const c = investorDocsByLang[lang];

  return (
    <main className="min-h-screen bg-[var(--bg)] text-[var(--text)]">
      <Navigation />
      <article className="mx-auto max-w-3xl px-5 py-12 leading-7">
        <p className="text-xs font-semibold uppercase tracking-[0.14em] text-[var(--accent)]">{c.demoEyebrow}</p>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight">{c.demoTitle}</h1>
        <p className="mt-4 text-[var(--text-muted)]">{c.demoLead}</p>

        <ol className="mt-8 list-decimal space-y-4 pl-5 text-[var(--text-muted)]">
          <li>
            <strong className="text-[var(--text)]">{c.demoStep1Title}</strong> — {c.demoStep1Body} (
            <Link href="/">/</Link>).
          </li>
          <li>
            <strong className="text-[var(--text)]">{c.demoStep2Title}</strong> — {c.demoStep2Body} (
            <Link href="/ai/workflows">/ai/workflows</Link>).
          </li>
          <li>
            <strong className="text-[var(--text)]">{c.demoStep3Title}</strong> — {c.demoStep3Body} (
            <Link href="/sample-reports/token-risk-report-pro">{c.demoStep3Sample}</Link>).
          </li>
          <li>
            <strong className="text-[var(--text)]">{c.demoStep4Title}</strong> — {c.demoStep4Body}
          </li>
          <li>
            <strong className="text-[var(--text)]">{c.demoStep5Title}</strong> —{" "}
            <Link href="/dashboard/seller">/dashboard/seller</Link>.
          </li>
          <li>
            <strong className="text-[var(--text)]">{c.demoStep6Title}</strong> — {c.demoStep6Body} (
            <Link href="/investors">/investors</Link>) +{" "}
            <Link href="/docs/investors/budget-12m">{c.demoBudgetLink}</Link>).
          </li>
        </ol>

        <p className="mt-10 text-sm text-[var(--text-muted)]">{c.demoFootnote}</p>
        <div className="mt-8 flex flex-wrap gap-3">
          <Link href="/investors" className="rounded-md border border-[var(--border)] px-4 py-2 text-sm">
            {c.demoBack}
          </Link>
          <Link href="/docs/investors/budget-12m" className="rounded-md border border-[var(--border)] px-4 py-2 text-sm">
            {c.demoBudgetCta}
          </Link>
        </div>
      </article>
    </main>
  );
}
