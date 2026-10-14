"use client";
import Link from "next/link";
import { Navigation } from "@/components/Navigation";
import { useLanguage } from "@/components/LanguageProvider";
import { WorkflowFooter, presentationStyles as s } from "@/components/WorkflowPresentation";
import { positioningByLang } from "@/locales/positioning";

export function InvestorOverview() {
  const { lang } = useLanguage();
  const c = positioningByLang[lang];
  return <div className={s.shell}><Navigation /><main className={s.main}>
    <section className={s.section} style={{ borderTop: 0, paddingTop: 64 }}>
      <p className={s.eyebrow}>ANCAP / {c.investors}</p><h1 className={s.title}>{c.investmentTitle}</h1>
      <p className={s.lead}>{c.investmentLead}</p>
      <div className={s.actions}><Link href="/ai/workflows" className={s.primary}>{c.browse}</Link><Link href="/sample-reports/token-risk-report-pro" className={s.secondary}>{c.sample}</Link></div>
    </section>
    <section className={s.section}><h2 className={s.heading}>{c.model}</h2><p className={s.lead}>{c.modelBody}</p>
      <div className={s.actions}><Link href="/pricing" className={s.secondary}>{c.workflows}</Link><Link href="/dashboard/seller" className={s.secondary}>{c.creators}</Link><Link href="/projects" className={s.secondary}>{c.solutions}</Link></div>
    </section>
    <section className={s.section}><h2 className={s.heading}>{c.evidence}</h2><p className={s.lead}>{c.evidenceBody}</p>
      <div className={s.actions}><Link href="/proof-center" className={s.secondary}>{c.trust}</Link><Link href="/developers" className={s.secondary}>API / MCP</Link><a className={s.secondary} href="https://github.com/ancapcloud/ancap" target="_blank" rel="noopener noreferrer">GitHub ↗</a></div>
      <div className={s.note}><strong>{c.stage}</strong><p>{c.stageBody}</p></div>
    </section>
    <section className={s.section}><h2 className={s.heading}>{c.funding}</h2><p className={s.lead}>{c.fundingBody}</p>
      <div className={s.grid}>{[[c.milestone1, c.milestone1Body], [c.milestone2, c.milestone2Body], [c.milestone3, c.milestone3Body]].map(([title, body]) => <article className={s.card} key={title}><h3>{title}</h3><p>{body}</p></article>)}</div>
      <div className={s.actions}><a href="mailto:support@ancap.cloud?subject=ANCAP%20investment%20discussion" className={s.primary}>{c.contact} →</a></div>
    </section>
  </main><WorkflowFooter /></div>;
}
