import Link from "next/link";
import { Navigation } from "@/components/Navigation";

export const metadata = {
  title: "5-minute investor demo",
  description: "Demo path for ANCAP workflow commerce — samples labeled separately from paid runs.",
};

/** Public summary of docs/investors/DEMO_SCRIPT_5MIN.md */
export default function InvestorDemoPage() {
  return (
    <main className="min-h-screen bg-[var(--bg)] text-[var(--text)]">
      <Navigation />
      <article className="mx-auto max-w-3xl px-5 py-12 leading-7">
        <p className="text-xs font-semibold uppercase tracking-[0.14em] text-[var(--accent)]">Investors · demo</p>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight">5-minute demo script</h1>
        <p className="mt-4 text-[var(--text-muted)]">
          Walk the product without inventing traction. Label every sample or test-ledger run clearly. No real card
          charges and no chain broadcast in the demo environment.
        </p>

        <ol className="mt-8 list-decimal space-y-4 pl-5 text-[var(--text-muted)]">
          <li>
            <strong className="text-[var(--text)]">Home</strong> — paid AI workflow outputs, ACP settlement, creator fee
            model (<Link href="/">/</Link>).
          </li>
          <li>
            <strong className="text-[var(--text)]">Catalog</strong> — crypto launch / risk / growth focus (
            <Link href="/ai/workflows">/ai/workflows</Link>).
          </li>
          <li>
            <strong className="text-[var(--text)]">Sample result</strong> — illustrative report (
            <Link href="/sample-reports/token-risk-report-pro">sample report</Link>), or a labeled test-ledger execution.
          </li>
          <li>
            <strong className="text-[var(--text)]">Receipt</strong> — price snapshot and payment proof; not a guarantee of
            factual accuracy.
          </li>
          <li>
            <strong className="text-[var(--text)]">Creator workspace</strong> —{" "}
            <Link href="/dashboard/seller">/dashboard/seller</Link>.
          </li>
          <li>
            <strong className="text-[var(--text)]">Investors</strong> — stage, evidence, funding milestones (
            <Link href="/investors">/investors</Link>) +{" "}
            <Link href="/docs/investors/budget-12m">budget assumptions</Link>).
          </li>
        </ol>

        <p className="mt-10 text-sm text-[var(--text-muted)]">
          Full script: repository file <code>docs/investors/DEMO_SCRIPT_5MIN.md</code>. Test-env paid path:{" "}
          <code>pytest tests/api/test_investor_paid_path_smoke.py -q</code>.
        </p>
        <div className="mt-8 flex flex-wrap gap-3">
          <Link href="/investors" className="rounded-md border border-[var(--border)] px-4 py-2 text-sm">
            ← Investors
          </Link>
          <Link href="/docs/investors/budget-12m" className="rounded-md border border-[var(--border)] px-4 py-2 text-sm">
            Budget assumptions
          </Link>
        </div>
      </article>
    </main>
  );
}
