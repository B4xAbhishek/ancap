import Link from "next/link";
import { Navigation } from "@/components/Navigation";

export const metadata = {
  title: "12-month budget assumptions",
  description: "Planning draft for ANCAP fundraising — costs and milestones, not revenue projections.",
};

/** Public summary of docs/investors/BUDGET_12M_ASSUMPTIONS.md — no invented revenue. */
export default function InvestorBudgetPage() {
  return (
    <main className="min-h-screen bg-[var(--bg)] text-[var(--text)]">
      <Navigation />
      <article className="mx-auto max-w-3xl px-5 py-12 leading-7">
        <p className="text-xs font-semibold uppercase tracking-[0.14em] text-[var(--accent)]">Investors · planning</p>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight">12-month budget (assumptions)</h1>
        <p className="mt-4 text-[var(--text-muted)]">
          Planning draft dated 2026-10-14. Figures are cost assumptions for fundraising discussion. They are not audited
          quotes, not a company valuation, and not a revenue forecast. Owner must confirm jurisdiction and replace bands
          with vendor quotes.
        </p>

        <h2 className="mt-10 text-xl font-semibold">Discussion ask band</h2>
        <p className="mt-3 text-[var(--text-muted)]">
          Until jurisdiction and quotes are fixed: <strong className="text-[var(--text)]">€250,000–€400,000</strong> cash
          for a standard release team over 12 months (formation, engineering/QA, ops/IR, infra/LLM, security review
          slice, pilot bag, reserve). Lean core planning lands nearer €180k–€220k before reserve.
        </p>

        <h2 className="mt-10 text-xl font-semibold">Cost buckets</h2>
        <ul className="mt-3 list-disc space-y-2 pl-5 text-[var(--text-muted)]">
          <li>One-time: company formation, accounting setup, legal refresh, independent security review.</li>
          <li>Monthly: engineering, ops/IR, optional sales, hosting, LLM inference, SaaS tools.</li>
          <li>Pilot bag: test credits / discounts and optional distribution experiments (ACP credits ≠ cash revenue).</li>
          <li>Reserve: 15–20% working capital.</li>
        </ul>

        <h2 className="mt-10 text-xl font-semibold">Milestone use of funds</h2>
        <ol className="mt-3 list-decimal space-y-2 pl-5 text-[var(--text-muted)]">
          <li>Release &amp; verification — paid path, mobile evidence, security findings on a fixed commit.</li>
          <li>Paid pilots — measure paid runs, delivery cost, refunds, repeat purchase.</li>
          <li>Repeatable distribution — expand only after pilot economics exist.</li>
        </ol>

        <p className="mt-10 text-sm text-[var(--text-muted)]">
          Full line-item tables: repository file <code>docs/investors/BUDGET_12M_ASSUMPTIONS.md</code>.
        </p>
        <div className="mt-8 flex flex-wrap gap-3">
          <Link href="/investors" className="rounded-md border border-[var(--border)] px-4 py-2 text-sm">
            ← Investors
          </Link>
          <Link href="/docs/investors/demo-5min" className="rounded-md border border-[var(--border)] px-4 py-2 text-sm">
            Demo script
          </Link>
        </div>
      </article>
    </main>
  );
}
