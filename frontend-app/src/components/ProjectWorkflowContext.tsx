"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useLanguage } from "./LanguageProvider";
import { solutionPortfolio, portfolioByLang } from "@/lib/solutionPortfolio";
import { positioningByLang } from "@/locales/positioning";

/** Existing project pages retain their routes, with an explicit workflow/brief context. */
export function ProjectWorkflowContext() {
  const pathname = usePathname();
  const { lang } = useLanguage();
  const index = solutionPortfolio.findIndex(area => area.routes.some(([href]) => href === pathname));
  if (index < 0) return null;
  const area = solutionPortfolio[index];
  const p = portfolioByLang[lang];
  const c = positioningByLang[lang];
  return <aside className="relative z-10 mx-auto max-w-6xl border-b border-[var(--border)] bg-[var(--bg-card)] px-5 py-4 text-[var(--text)]" aria-label={c.solutions}>
    <div className="flex flex-wrap items-center justify-between gap-3">
      <div><Link href={`/projects#${area.id}`} className="text-sm font-semibold text-[var(--accent)]">{p.areas[index].title}</Link><span className="ml-3 text-xs text-[var(--text-muted)]">{p.kinds[area.kind]}</span></div>
      <Link href="/ai/workflows" className="text-sm text-[var(--accent)]">{c.browse} →</Link>
    </div>
    <p className="mt-2 text-sm leading-6 text-[var(--text-muted)]"><strong>{c.output}: </strong>{p.areas[index].deliverable}</p>
    {area.kind !== "core" && <p className="mt-2 text-xs leading-5 text-[var(--text-muted)]">{c.portfolioNote}</p>}
  </aside>;
}
