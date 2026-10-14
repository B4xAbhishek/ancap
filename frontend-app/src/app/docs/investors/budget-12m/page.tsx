"use client";
import Link from "next/link";
import { Navigation } from "@/components/Navigation";
import { useLanguage } from "@/components/LanguageProvider";
import { investorDocsByLang } from "@/locales/investorDocs";

/** Public summary of docs/investors/BUDGET_12M_ASSUMPTIONS.md — no invented revenue. */
export default function InvestorBudgetPage() {
  const { lang } = useLanguage();
  const c = investorDocsByLang[lang];

  return (
    <main className="min-h-screen bg-[var(--bg)] text-[var(--text)]">
      <Navigation />
      <article className="mx-auto max-w-3xl px-5 py-12 leading-7">
        <p className="text-xs font-semibold uppercase tracking-[0.14em] text-[var(--accent)]">{c.budgetEyebrow}</p>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight">{c.budgetTitle}</h1>
        <p className="mt-4 text-[var(--text-muted)]">{c.budgetLead}</p>

        <h2 className="mt-10 text-xl font-semibold">{c.budgetAskHeading}</h2>
        <p className="mt-3 text-[var(--text-muted)]">
          {c.budgetAskBodyBefore}{" "}
          <strong className="text-[var(--text)]">{c.budgetAskBand}</strong>. {c.budgetAskBodyAfter}
        </p>

        <h2 className="mt-10 text-xl font-semibold">{c.budgetBucketsHeading}</h2>
        <ul className="mt-3 list-disc space-y-2 pl-5 text-[var(--text-muted)]">
          <li>{c.budgetBucket1}</li>
          <li>{c.budgetBucket2}</li>
          <li>{c.budgetBucket3}</li>
          <li>{c.budgetBucket4}</li>
        </ul>

        <h2 className="mt-10 text-xl font-semibold">{c.budgetMilestonesHeading}</h2>
        <ol className="mt-3 list-decimal space-y-2 pl-5 text-[var(--text-muted)]">
          <li>{c.budgetMs1}</li>
          <li>{c.budgetMs2}</li>
          <li>{c.budgetMs3}</li>
        </ol>

        <p className="mt-10 text-sm text-[var(--text-muted)]">{c.budgetFootnote}</p>
        <div className="mt-8 flex flex-wrap gap-3">
          <Link href="/investors" className="rounded-md border border-[var(--border)] px-4 py-2 text-sm">
            {c.budgetBack}
          </Link>
          <Link href="/docs/investors/demo-5min" className="rounded-md border border-[var(--border)] px-4 py-2 text-sm">
            {c.budgetDemoCta}
          </Link>
        </div>
      </article>
    </main>
  );
}
