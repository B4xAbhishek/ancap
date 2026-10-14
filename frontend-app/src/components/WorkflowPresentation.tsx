"use client";
import Link from "next/link";
import { useLanguage } from "./LanguageProvider";
import { portfolioByLang, solutionPortfolio } from "@/lib/solutionPortfolio";
import { positioningByLang } from "@/locales/positioning";
import s from "./WorkflowPresentation.module.css";
export { default as presentationStyles } from "./WorkflowPresentation.module.css";

export function SolutionAreas({ compact = false }: { compact?: boolean }) {
  const { lang } = useLanguage();
  const c = positioningByLang[lang];
  const p = portfolioByLang[lang];
  return <div className={compact ? s.grid : s.gridTwo}>
    {solutionPortfolio.map((area, i) => {
      const copy = p.areas[i];
      return <article key={area.id} id={area.id} className={s.card}>
        <span className={`${s.tag} ${area.kind === "core" ? s.core : ""}`}>{p.kinds[area.kind]}</span>
        <h3>{copy.title}</h3><p>{copy.body}</p>
        <div className={s.deliverable}><strong>{c.output}</strong><p>{copy.deliverable}</p></div>
        {compact ? <Link className={s.projectLink} href={`/projects#${area.id}`}>{c.open} →</Link> : <>
          <strong className={s.eyebrow}>{c.projects}</strong>
          <div className={s.projects}>{area.routes.map(([href, name]) => <Link key={href} href={href} className={s.projectLink}>{name}</Link>)}</div>
        </>}
      </article>;
    })}
  </div>;
}
export function WorkflowFooter() {
  const { lang, t } = useLanguage();
  const c = positioningByLang[lang];
  return <footer className={s.footer}><span>ANCAP · {c.kicker}</span><div className={s.projects}>
    <Link href="/investors">{c.investors}</Link><Link href="/legal/terms">{t("legal.termsLink")}</Link>
    <Link href="/legal/privacy">{t("legal.privacyLink")}</Link><Link href="/legal/refunds">{t("legal.refundsLink")}</Link>
    <Link href="/legal">{t("nav.legal")}</Link><a href="mailto:support@ancap.cloud">support@ancap.cloud</a>
  </div></footer>;
}
