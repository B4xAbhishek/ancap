"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { useLanguage } from "@/components/LanguageProvider";
import { safeGetItem, safeSetItem } from "@/lib/safeStorage";
import { parseSavedWorkflows, plannedRunCost, recommendWorkflows, type WorkflowGoal } from "@/lib/workflowDiscovery";
import type { WorkflowTemplate } from "@/lib/workflowStore";
import { discoveryByLang } from "@/locales/discovery";

const SAVED_KEY = "ancap-workflow-shortlist-v1";
export function useWorkflowShortlist(workflows: WorkflowTemplate[]) {
  const [saved, setSaved] = useState<string[]>([]);
  const [compared, setCompared] = useState<string[]>([]);
  const [loaded, setLoaded] = useState(false);
  const [limitReached, setLimitReached] = useState(false);
  useEffect(() => {
    setSaved(parseSavedWorkflows(safeGetItem(SAVED_KEY), workflows));
    setLoaded(true);
  }, [workflows]);
  useEffect(() => { if (loaded) safeSetItem(SAVED_KEY, JSON.stringify(saved)); }, [saved, loaded]);
  const toggleSaved = (slug: string) => {
    if (!loaded || !workflows.some(item => item.slug === slug)) return;
    setSaved(ids => ids.includes(slug) ? ids.filter(id => id !== slug) : [...ids, slug].slice(-50));
  };
  const toggleCompared = (slug: string) => {
    if (!workflows.some(item => item.slug === slug)) return;
    if (!compared.includes(slug) && compared.length >= 3) { setLimitReached(true); return; }
    setLimitReached(false);
    setCompared(ids => ids.includes(slug) ? ids.filter(id => id !== slug) : [...ids, slug].slice(0, 3));
  };
  return { saved, compared, loaded, limitReached, toggleSaved, toggleCompared, clearSaved: () => setSaved([]) };
}
export type ShortlistState = ReturnType<typeof useWorkflowShortlist>;

export function WorkflowChoiceButtons({ workflow, shortlist }: { workflow: WorkflowTemplate; shortlist: ShortlistState }) {
  const { lang } = useLanguage();
  const c = discoveryByLang[lang];
  return <div className="mt-4 flex flex-wrap gap-2">
    <button type="button" disabled={!shortlist.loaded} aria-pressed={shortlist.saved.includes(workflow.slug)} onClick={() => shortlist.toggleSaved(workflow.slug)} className="rounded-lg border border-[var(--border)] px-3 py-2 text-sm text-[var(--text)] disabled:opacity-50">
      {shortlist.saved.includes(workflow.slug) ? c.saved : c.save}
    </button>
    <button type="button" aria-pressed={shortlist.compared.includes(workflow.slug)} onClick={() => shortlist.toggleCompared(workflow.slug)} className="rounded-lg border border-[var(--border)] px-3 py-2 text-sm text-[var(--text)]">
      {shortlist.compared.includes(workflow.slug) ? c.compared : c.compare}
    </button>
  </div>;
}

export function WorkflowDiscoveryPanel({ workflows, shortlist, isFallback }: { workflows: WorkflowTemplate[]; shortlist: ShortlistState; isFallback: boolean }) {
  const { lang } = useLanguage();
  const c = discoveryByLang[lang];
  const [goal, setGoal] = useState<WorkflowGoal | null>(null);
  const [runs, setRuns] = useState("10");
  const recommended = goal ? recommendWorkflows(workflows, goal) : [];
  const compared = shortlist.compared.map(slug => workflows.find(item => item.slug === slug)).filter((item): item is WorkflowTemplate => Boolean(item));
  const saved = shortlist.saved.map(slug => workflows.find(item => item.slug === slug)).filter((item): item is WorkflowTemplate => Boolean(item));
  const count = Number(runs);
  const validRuns = runs.trim() !== "" && Number.isInteger(count) && count >= 1 && count <= 10000;
  const download = () => {
    if (!validRuns) return;
    const data = { version: 1, generated_at: new Date().toISOString(), catalog_source: isFallback ? "reference" : "live", planned_runs: count, workflows: compared.map(item => ({ slug: item.slug, title: item.title, price_per_run: item.price, planned_cost: { amount: plannedRunCost(item.price.amount, count), currency: item.price.currency }, outputs: item.output_items })) };
    const url = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2)], { type: "application/json" }));
    const anchor = document.createElement("a");
    anchor.href = url; anchor.download = "ancap-workflow-comparison.json"; anchor.click();
    window.setTimeout(() => URL.revokeObjectURL(url), 1000);
  };
  return <section className="mb-10 rounded-2xl border border-[var(--border)] bg-[var(--bg-card)] p-5 sm:p-7" aria-labelledby="discovery-title">
    <h2 id="discovery-title" className="text-2xl font-semibold text-[var(--text)]">{c.title}</h2>
    <p className="mt-3 text-sm leading-6 text-[var(--text-muted)]">{c.lead}</p>
    <div className="mt-5 flex flex-wrap gap-2">{(["risk", "launch", "growth", "integration"] as WorkflowGoal[]).map(item => <button type="button" key={item} aria-pressed={goal === item} onClick={() => setGoal(item)} className={`rounded-lg border px-4 py-3 text-sm ${goal === item ? "border-[var(--accent)] text-[var(--accent)]" : "border-[var(--border)] text-[var(--text)]"}`}>{c[item]}</button>)}</div>
    {goal && <div className="mt-6">
      <h3 className="font-semibold text-[var(--text)]">{c.recommended}</h3>
      {recommended.length === 0 ? <p className="mt-3 text-sm text-[var(--text-muted)]">{c.none}</p> : <div className="mt-3 grid gap-3 lg:grid-cols-3">{recommended.map(item => <article key={item.slug} className="rounded-xl border border-[var(--border)] p-4">
        <h4 className="font-semibold text-[var(--text)]">{item.title}</h4><p className="mt-2 text-sm text-[var(--text-muted)]">{item.summary}</p>
        <p className="mt-3 font-semibold text-[var(--accent)]">{item.price.amount} {item.price.currency}</p>
        <WorkflowChoiceButtons workflow={item} shortlist={shortlist} /><Link href={`/ai/run/${item.slug}`} className="mt-3 inline-block text-sm text-[var(--accent)]">{c.open} →</Link>
      </article>)}</div>}
    </div>}
    <details className="mt-6 border-t border-[var(--border)] pt-4"><summary className="cursor-pointer font-semibold text-[var(--text)]">{c.shortlist} ({saved.length})</summary>
      <p className="mt-3 text-xs text-[var(--text-muted)]">{c.device}</p>
      {saved.length === 0 ? <p className="mt-3 text-sm text-[var(--text-muted)]">{c.empty}</p> : <>
        <ul className="mt-3 space-y-3">{saved.map(item => <li key={item.slug} className="flex flex-wrap items-center justify-between gap-3"><Link href={`/ai/run/${item.slug}`} className="text-sm text-[var(--accent)]">{item.title}</Link><WorkflowChoiceButtons workflow={item} shortlist={shortlist} /></li>)}</ul>
        <button type="button" className="mt-4 rounded-lg border border-[var(--border)] px-3 py-2 text-sm" onClick={shortlist.clearSaved}>{c.clear}</button>
      </>}
    </details>
    {shortlist.limitReached && <p role="alert" className="mt-4 text-sm text-[var(--accent)]">{c.limit}</p>}
    {compared.length > 0 && <section className="mt-6 border-t border-[var(--border)] pt-5" aria-labelledby="comparison-title">
      <h3 id="comparison-title" className="text-xl font-semibold">{c.comparison}</h3>
      <label className="mt-4 flex flex-wrap items-center gap-3 text-sm">{c.runs}<input aria-describedby="run-cost-note" type="number" min="1" max="10000" step="1" value={runs} onChange={event => setRuns(event.target.value)} className="w-28 rounded-lg border border-[var(--border)] bg-[var(--bg)] px-3 py-2 text-[var(--text)]" /></label>
      {!validRuns && <p role="alert" className="mt-2 text-sm">{c.invalid}</p>}
      <p id="run-cost-note" className="mt-3 text-xs leading-6 text-[var(--text-muted)]">{c.estimate}</p>
      {isFallback && <p className="mt-2 text-xs text-[var(--text-muted)]">{c.source}</p>}
      <div className="mt-4 grid gap-3 lg:grid-cols-3">{compared.map(item => <article className="rounded-xl border border-[var(--border)] p-4" key={item.slug}>
        <h4 className="font-semibold">{item.title}</h4><dl className="mt-4 space-y-3 text-sm"><div><dt className="text-[var(--text-muted)]">{c.price}</dt><dd>{item.price.amount} {item.price.currency}</dd></div><div><dt className="text-[var(--text-muted)]">{c.total}</dt><dd data-testid={`planned-cost-${item.slug}`} className="font-semibold text-[var(--accent)]">{validRuns ? plannedRunCost(item.price.amount, count) ?? "—" : "—"} {item.price.currency}</dd></div><div><dt className="text-[var(--text-muted)]">{c.minutes}</dt><dd>{item.estimated_time_minutes}</dd></div></dl>
        <h5 className="mt-4 text-sm font-semibold">{c.outputs}</h5><ul className="mt-2 list-disc pl-4 text-sm text-[var(--text-muted)]">{item.output_items.map((output, i) => <li key={i}>{output}</li>)}</ul>
        <div className="mt-4 flex gap-3"><Link className="text-sm text-[var(--accent)]" href={`/ai/run/${item.slug}`}>{c.open}</Link><button className="text-sm text-[var(--text-muted)]" type="button" onClick={() => shortlist.toggleCompared(item.slug)}>{c.remove}</button></div>
      </article>)}</div>
      <button type="button" disabled={!validRuns} onClick={download} className="mt-4 rounded-lg bg-[var(--accent)] px-4 py-3 text-sm font-semibold text-slate-950 disabled:opacity-50">{c.export}</button>
    </section>}
  </section>;
}
