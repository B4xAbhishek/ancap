"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { Navigation } from "@/components/Navigation";
import { useAuth } from "@/components/AuthProvider";
import { workflowStore } from "@/lib/api";
import { getFallbackWorkflowBundle, getFallbackWorkflowTemplate, type WorkflowBundle, type WorkflowTemplate } from "@/lib/workflowStore";

type BundleCheckoutResponse = {
  bundle: WorkflowBundle;
  bundle_checkout_id: string;
  payment_currency: string;
  quoted_total: { amount: string; currency: string };
  original_total: { amount: string; currency: string };
  discount_amount: { amount: string; currency: string };
  reserved: boolean;
  runs: Array<{ id: string; title: string; workflow_slug: string; status: string; price: { amount: string; currency: string } }>;
  payment_intents: Array<{ id: string; status: string; amount: { amount: string; currency: string } }>;
};

export default function WorkflowBundlePage() {
  const params = useParams<{ bundle: string }>();
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuth();
  const [bundle, setBundle] = useState<WorkflowBundle | null>(null);
  const [projectName, setProjectName] = useState("");
  const [paymentCurrency, setPaymentCurrency] = useState("ACP");
  const [unlockFullResult, setUnlockFullResult] = useState(true);
  const [checkout, setCheckout] = useState<BundleCheckoutResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const slug = params?.bundle;
    if (!slug) return;
    let cancelled = false;
    (async () => {
      try {
        setLoading(true);
        setError("");
        const data = await workflowStore.getBundle(slug);
        if (!cancelled) {
          setBundle(data);
          setPaymentCurrency(data.accepted_currencies?.[0] || "ACP");
        }
      } catch {
        const fallback = getFallbackWorkflowBundle(slug);
        if (!cancelled) {
          setBundle(fallback);
          setPaymentCurrency(fallback?.accepted_currencies?.[0] || "ACP");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [params?.bundle]);

  const quotedPreview = useMemo(() => {
    if (!bundle) return "";
    const base = Number(bundle.price.amount || 0);
    // Bridge 1 ACP ↔ 10 wACP; catalog wACP rail keeps a 10% discount → ×9.
    if (paymentCurrency === "wACP") return `${(base * 9).toFixed(2)} ${paymentCurrency}`;
    return `${base.toFixed(2)} ${paymentCurrency}`;
  }, [bundle, paymentCurrency]);
  const includedWorkflows = useMemo(() => {
    if (!bundle) return [];
    return bundle.workflow_slugs
      .map((slug) => getFallbackWorkflowTemplate(slug))
      .filter((workflow): workflow is WorkflowTemplate => Boolean(workflow));
  }, [bundle]);

  async function submitCheckout() {
    if (!bundle) return;
    if (!isAuthenticated) {
      router.push("/login");
      return;
    }
    try {
      setSubmitting(true);
      setError("");
      const response = await workflowStore.checkoutBundle(bundle.slug, {
        payment_currency: paymentCurrency,
        payment_method: "credits",
        project_name: projectName.trim() || undefined,
        unlock_full_result: unlockFullResult,
        reserve_credits: true,
        note: `Bundle checkout: ${bundle.title}`,
      });
      setCheckout(response);
    } catch (e: any) {
      setError(e?.message || String(e));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen bg-[var(--bg)] text-[var(--text)]">
      <Navigation />
      <main className="mx-auto max-w-6xl px-4 py-10 sm:px-6 lg:px-8">
        <div className="mb-6">
          <Link href="/ai/workflows" className="text-sm text-emerald-300 hover:text-emerald-200">
            Back to workflow catalog
          </Link>
        </div>

        {loading ? (
          <div className="rounded-3xl border border-white/10 bg-white/[0.03] p-6 text-white/55">Loading bundle...</div>
        ) : !bundle ? (
          <div className="rounded-3xl border border-white/10 bg-white/[0.03] p-6 text-white/55">Workflow bundle not found.</div>
        ) : (
          <div className="grid gap-6 lg:grid-cols-[1fr_0.82fr]">
            <section className="rounded-3xl border border-emerald-400/20 bg-emerald-400/[0.06] p-6 sm:p-8">
              <div className="mb-3 inline-flex rounded-full border border-emerald-400/25 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.18em] text-emerald-200">
                {bundle.category}
              </div>
              <h1 className="max-w-4xl text-3xl font-semibold tracking-[-0.04em] sm:text-5xl">{bundle.title}</h1>
              <p className="mt-4 max-w-3xl text-sm leading-7 text-white/72 sm:text-base">{bundle.description}</p>

              <div className="mt-6 grid gap-3 sm:grid-cols-3">
                <div className="rounded-2xl border border-white/10 bg-black/15 p-4">
                  <div className="text-xs uppercase tracking-[0.18em] text-white/45">Bundle price</div>
                  <div className="mt-2 text-xl font-semibold text-emerald-300">{quotedPreview}</div>
                </div>
                <div className="rounded-2xl border border-white/10 bg-black/15 p-4">
                  <div className="text-xs uppercase tracking-[0.18em] text-white/45">{bundle.discount_percent > 0 ? "Discount" : "Tier"}</div>
                  <div className="mt-2 text-xl font-semibold text-white/92">{bundle.discount_percent > 0 ? `${bundle.discount_percent}%` : "Premium"}</div>
                </div>
                <div className="rounded-2xl border border-white/10 bg-black/15 p-4">
                  <div className="text-xs uppercase tracking-[0.18em] text-white/45">Workflows</div>
                  <div className="mt-2 text-xl font-semibold text-white/92">{bundle.workflow_slugs.length}</div>
                </div>
              </div>

              <div className="mt-8">
                <div className="text-xs uppercase tracking-[0.18em] text-white/45">Outputs</div>
                <ul className="mt-4 grid gap-3 text-sm text-white/78 sm:grid-cols-2">
                  {bundle.output_items.map((item) => (
                    <li key={item} className="flex items-center gap-2">
                      <span className="h-1.5 w-1.5 rounded-full bg-emerald-300" />
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="mt-8">
                <div className="text-xs uppercase tracking-[0.18em] text-white/45">Included workflow samples</div>
                <div className="mt-4 grid gap-3 sm:grid-cols-2">
                  {includedWorkflows.map((workflow) => (
                    <Link key={workflow.slug} href={`/sample-reports/${workflow.slug}`} className="rounded-2xl border border-white/10 bg-black/15 p-4 text-sm text-white/75 transition hover:border-emerald-400/25 hover:text-white">
                      <div className="font-semibold text-white/90">{workflow.title}</div>
                      <div className="mt-1 text-white/50">{workflow.price.amount} {workflow.price.currency} sample output</div>
                    </Link>
                  ))}
                </div>
              </div>
            </section>

            <aside className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
              <div className="text-sm font-semibold text-white/90">Bundle checkout</div>
              <div className="mt-4 grid gap-4">
                <div>
                  <div className="mb-2 text-xs uppercase tracking-[0.18em] text-white/45">Project name</div>
                  <input
                    value={projectName}
                    onChange={(e) => setProjectName(e.target.value)}
                    placeholder="Your token / project"
                    className="w-full rounded-2xl border border-white/10 bg-[var(--bg)] px-4 py-3 text-sm text-white outline-none"
                  />
                </div>

                <div>
                  <div className="mb-2 text-xs uppercase tracking-[0.18em] text-white/45">Payment currency</div>
                  <div className="flex flex-wrap gap-2">
                    {bundle.accepted_currencies.map((currency) => (
                      <button
                        key={currency}
                        type="button"
                        onClick={() => setPaymentCurrency(currency)}
                        className={`rounded-full px-3 py-1.5 text-xs font-semibold transition ${paymentCurrency === currency ? "bg-emerald-400 text-slate-950" : "border border-white/12 text-white/70 hover:border-white/25"}`}
                      >
                        {currency}
                      </button>
                    ))}
                  </div>
                </div>

                <label className="flex items-center gap-3 text-sm text-white/75">
                  <input type="checkbox" checked={unlockFullResult} onChange={(e) => setUnlockFullResult(e.target.checked)} />
                  <span>Unlock result shells for all workflow runs</span>
                </label>

                {error && <div className="rounded-2xl border border-red-400/25 bg-red-500/10 p-3 text-sm text-red-200">{error}</div>}

                <button
                  type="button"
                  onClick={submitCheckout}
                  disabled={submitting || isLoading}
                  className="rounded-full bg-emerald-400 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:opacity-90 disabled:opacity-60"
                >
                  {submitting ? "Creating bundle..." : isAuthenticated ? "Reserve credits and create bundle" : "Sign in to checkout"}
                </button>
                <Link href="/wallet/credits" className="text-sm font-semibold text-emerald-300 hover:text-emerald-200">
                  Check credits balance
                </Link>
              </div>

              {checkout && (
                <div className="mt-6 rounded-2xl border border-emerald-400/20 bg-emerald-500/10 p-4">
                  <div className="text-sm font-semibold text-emerald-200">Bundle created</div>
                  <div className="mt-2 text-sm text-white/80">Checkout: {checkout.bundle_checkout_id}</div>
                  <div className="text-sm text-white/80">
                    Reserved: {checkout.quoted_total.amount} {checkout.quoted_total.currency}
                  </div>
                  {Number(checkout.discount_amount.amount) > 0 && (
                    <div className="text-sm text-white/60">
                      Saved: {checkout.discount_amount.amount} {checkout.discount_amount.currency}
                    </div>
                  )}
                  <div className="mt-4 grid gap-2">
                    {checkout.runs.map((run) => (
                      <Link key={run.id} href={`/ai/runs/${run.id}`} className="rounded-2xl border border-white/10 bg-black/15 p-3 text-sm text-white/80 transition hover:border-emerald-400/25 hover:text-white">
                        <div className="font-semibold">{run.title}</div>
                        <div className="mt-1 text-white/50">
                          {run.status} · {run.price.amount} {run.price.currency}
                        </div>
                      </Link>
                    ))}
                  </div>
                </div>
              )}
            </aside>
          </div>
        )}
      </main>
    </div>
  );
}
