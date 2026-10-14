"use client";
import { useLanguage } from "@/components/LanguageProvider";
import { discoveryByLang } from "@/locales/discovery";
// Immutable archive revision; these links refer to the recorded demo, never to current customer activity.
const ARCHIVE = "https://github.com/ancapcloud/ancap/blob/588ebb765c6ec1e62d39dbc206bc8c0f9e177bcc/docs/investors/evidence/2026-10-14-local-ollama";
export function DemoEvidencePanel() {
  const { lang } = useLanguage();
  const c = discoveryByLang[lang];
  return <section className="mt-7 rounded-xl border border-[var(--border)] bg-[var(--bg-card)] p-5" aria-labelledby="demo-evidence-title">
    <span className="text-xs font-semibold text-[var(--accent)]">{c.demoLabel}</span>
    <h3 id="demo-evidence-title" className="mt-3 text-xl font-semibold">{c.demoTitle}</h3>
    <p className="mt-3 text-sm leading-7 text-[var(--text-muted)]">{c.demoLead}</p>
    <ul className="mt-4 space-y-2 text-sm"><li>{c.demoStatus}</li><li>{c.demoPayment}</li><li>{c.demoFee}</li></ul>
    <div className="mt-5 flex flex-wrap gap-3">{[["receipt.json", c.demoReceipt], ["artifact.json", c.demoArtifact], ["README.md", c.demoManifest]].map(([file, label]) => <a className="rounded-lg border border-[var(--border)] px-3 py-2 text-sm text-[var(--accent)]" href={`${ARCHIVE}/${file}`} key={file} target="_blank" rel="noopener noreferrer">{label} ↗</a>)}</div>
    <p className="mt-4 text-xs leading-6 text-[var(--text-muted)]">{c.demoNote}</p>
  </section>;
}
