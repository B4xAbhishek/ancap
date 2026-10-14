"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useLanguage } from "./LanguageProvider";
import { solutionPortfolio, portfolioByLang } from "@/lib/solutionPortfolio";
import { offerForRoute, offerKindLabel } from "@/lib/projectOffers";
import { positioningByLang } from "@/locales/positioning";
import { fallbackWorkflowBundles } from "@/lib/workflowStore";

/** Existing project pages retain their routes, with an explicit buyer→receipt chain. */
export function ProjectWorkflowContext() {
  const pathname = usePathname();
  const { lang } = useLanguage();
  const index = solutionPortfolio.findIndex((area) => area.routes.some(([href]) => href === pathname));
  if (!pathname || index < 0) return null;
  const area = solutionPortfolio[index];
  const p = portfolioByLang[lang];
  const c = positioningByLang[lang];
  const offer = offerForRoute(pathname, lang);
  const primarySlug = offer?.workflowSlugs[0];
  const primaryHref = primarySlug
    ? `${fallbackWorkflowBundles.some(bundle => bundle.slug === primarySlug) ? "/ai/bundles" : "/ai/run"}/${encodeURIComponent(primarySlug)}`
    : "/ai/workflows";

  return (
    <aside
      className="relative z-10 mx-auto max-w-6xl border-b border-[var(--border)] bg-[var(--bg-card)] px-5 py-4 text-[var(--text)]"
      aria-label={c.solutions}
    >
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <Link href={`/projects#${area.id}`} className="text-sm font-semibold text-[var(--accent)]">
            {p.areas[index].title}
          </Link>
          <span className="ml-3 text-xs text-[var(--text-muted)]">{p.kinds[area.kind]}</span>
          {offer ? (
            <span className="ml-3 text-xs uppercase tracking-wide text-[var(--text-muted)]">
              {offerKindLabel(offer.offerKind, lang)}
            </span>
          ) : null}
        </div>
        <div className="flex flex-wrap gap-3">
          {primarySlug ? (
            <Link href={primaryHref} className="text-sm text-[var(--accent)]">
              {c.browse} →
            </Link>
          ) : (
            <Link href="/ai/workflows" className="text-sm text-[var(--accent)]">
              {c.browse} →
            </Link>
          )}
        </div>
      </div>
      <p className="mt-2 text-sm leading-6 text-[var(--text-muted)]">
        <strong>{c.output}: </strong>
        {p.areas[index].deliverable}
      </p>
      {offer ? (
        <dl className="mt-3 grid gap-2 text-xs leading-5 text-[var(--text-muted)] sm:grid-cols-2">
          <div>
            <dt className="font-semibold text-[var(--text)]">{c.offerBuyer}</dt>
            <dd>{offer.buyer}</dd>
          </div>
          <div>
            <dt className="font-semibold text-[var(--text)]">{c.offerTask}</dt>
            <dd>{offer.task}</dd>
          </div>
          <div>
            <dt className="font-semibold text-[var(--text)]">{c.offerInputs}</dt>
            <dd>{offer.inputs}</dd>
          </div>
          <div>
            <dt className="font-semibold text-[var(--text)]">{c.offerResult}</dt>
            <dd>{offer.aiResult}</dd>
          </div>
          <div className="sm:col-span-2">
            <dt className="font-semibold text-[var(--text)]">{c.offerLimits}</dt>
            <dd>{offer.constraints}</dd>
          </div>
          <div>
            <dt className="font-semibold text-[var(--text)]">{c.offerPay}</dt>
            <dd>{offer.payment}</dd>
          </div>
          <div>
            <dt className="font-semibold text-[var(--text)]">{c.offerReceipt}</dt>
            <dd>{offer.receipt}</dd>
          </div>
        </dl>
      ) : null}
      {area.kind !== "core" && (
        <p className="mt-2 text-xs leading-5 text-[var(--text-muted)]">{c.portfolioNote}</p>
      )}
    </aside>
  );
}
