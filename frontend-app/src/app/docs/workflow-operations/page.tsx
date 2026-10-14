"use client";
import Link from "next/link";
import { Navigation } from "@/components/Navigation";
import { useLanguage } from "@/components/LanguageProvider";
import { workflowOpsCopy } from "@/locales/workflowOps";

export default function Page() {
  const { lang } = useLanguage();
  const c = workflowOpsCopy[lang];
  return (
    <div className="min-h-screen bg-[var(--bg)] text-[var(--text)]">
      <Navigation />
      <main className="mx-auto max-w-3xl px-4 py-12">
        <h1 className="text-3xl font-semibold">{c.title}</h1>
        <p className="mt-5 leading-7 text-[var(--text-muted)]">{c.lead}</p>
        <ol className="mt-8 space-y-5 text-sm leading-7">
          <li>
            <strong>1. {c.projects}.</strong> {c.context} · TXT/MD/CSV ·{" "}
            {c.retention}. {c.share}: {c.viewer} / {c.editor}.
          </li>
          <li>
            <strong>2. {c.builder}.</strong> {c.steps} (1–5) → {c.save} →{" "}
            {c.test} → {c.publish}. {c.qualityNote}
          </li>
          <li>
            <strong>3. {c.run}.</strong> {c.maxCost} · {c.confirmSpend}{" "}
            {c.batch} (1–20).
          </li>
          <li>
            <strong>4. {c.schedule}.</strong> {c.scheduleNote} {c.interval} ≥
            60.
          </li>
          <li>
            <strong>5. {c.review}.</strong> {c.note} → {c.approve} / {c.reject}.{" "}
            {c.deliveryUnknown}
          </li>
          <li>
            <strong>6. {c.connections}.</strong> HTTPS webhook / Telegram /
            Google Sheets / HubSpot notes / Anthropic BYOK. {c.connectionNote}{" "}
            {c.byokNote}
          </li>
        </ol>
        <section className="mt-10 border-t border-[var(--border)] pt-6">
          <h2 className="text-xl font-semibold">API / n8n</h2>
          <p className="mt-3 text-sm leading-7">
            Bearer · Idempotency · ACP cap · Human review
          </p>
          <pre className="mt-4 overflow-x-auto rounded-xl border border-[var(--border)] p-4 text-xs">{`POST /v1/workflow-ops/automations/{id}/runs\n{ "idempotency_key": "unique-request-uuid",\n  "max_cost_acp": "YOUR_EXPLICIT_CAP",\n  "kind": "manual", "inputs": {} }\n\nGET /v1/workflow-ops/runs/{id}`}</pre>
          <div className="mt-5 flex flex-wrap gap-4">
            <a
              className="text-[var(--accent)]"
              href="/workflow-integrations/ancap-workflow-example.py"
              download
            >
              {c.downloadSdk}
            </a>
            <a
              className="text-[var(--accent)]"
              href="/workflow-integrations/ancap-workflow-n8n.json"
              download
            >
              {c.downloadN8n}
            </a>
          </div>
        </section>
        <section className="mt-10 border-t border-[var(--border)] pt-6">
          <h2 className="text-xl font-semibold">{c.privateProfile}</h2>
          <p className="mt-3 text-sm leading-7">{c.privateNote}</p>
          <a
            className="mt-3 inline-block text-[var(--accent)]"
            href="https://github.com/ancapcloud/ancap/blob/master/docs/WORKFLOW_OPERATIONS_PRIVATE_DEPLOYMENT.md"
          >
            Docker Compose / Ollama / TLS →
          </a>
        </section>
        <p className="mt-8 text-sm leading-7 text-[var(--text-muted)]">
          {c.economicsNote}
        </p>
        <Link
          href="/ai/studio"
          className="mt-6 inline-block text-[var(--accent)]"
        >
          {c.title} →
        </Link>
      </main>
    </div>
  );
}
