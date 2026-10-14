"use client";
import Link from "next/link";
import { Navigation } from "@/components/Navigation";
import { useLanguage } from "@/components/LanguageProvider";
import { SolutionAreas, WorkflowFooter, presentationStyles as s } from "@/components/WorkflowPresentation";
import { positioningByLang } from "@/locales/positioning";

export function HomePage() {
  const { lang } = useLanguage();
  const c = positioningByLang[lang];
  const examples = [
    { title: c.risk, body: c.riskBody, href: "/ai/run/token-risk-report-pro" },
    { title: c.launch, body: c.launchBody, href: "/ai/run/exchange-listing-submission-pack" },
    { title: c.growth, body: c.growthBody, href: "/ai/run/crypto-campaign-builder" },
  ];
  return <div className={s.shell}><Navigation /><main className={s.main}>
    <section className={s.hero} id="product">
      <div><p className={s.eyebrow}>ANCAP / {c.kicker}</p><h1 className={s.title}>{c.title}</h1><p className={s.lead}>{c.lead}</p>
        <div className={s.actions}><Link className={s.primary} href="/ai/workflows">{c.browse} →</Link><Link className={s.secondary} href="/sample-reports/token-risk-report-pro">{c.sample}</Link></div>
      </div>
      <div className={s.flow} aria-label={c.how}><p className={s.eyebrow}>{c.how}</p>
        {[[c.step1, c.step1Body], [c.step2, c.step2Body], [c.step3, c.step3Body], [c.step4, c.step4Body]].map(([title, body]) => <div className={s.flowRow} key={title}><strong>{title}</strong><p>{body}</p></div>)}
      </div>
    </section>
    <section className={s.section}><h2 className={s.heading}>{c.examples}</h2><p className={s.lead}>{c.examplesLead}</p>
      <div className={s.grid}>{examples.map((item) => <article key={item.href} className={s.card}><h3>{item.title}</h3><p>{item.body}</p><Link className={s.secondary} href={item.href}>{c.open} →</Link></article>)}</div>
    </section>
    <section className={s.section} id="solutions"><h2 className={s.heading}>{c.portfolio}</h2><p className={s.lead}>{c.portfolioLead}</p><SolutionAreas compact /><p className={s.note}>{c.portfolioNote}</p></section>
    <section className={s.section} id="creators"><div className={s.gridTwo}>
      <div><p className={s.eyebrow}>{c.creators}</p><h2 className={s.heading}>{c.earn}</h2><p className={s.lead}>{c.earnBody}</p><div className={s.actions}><Link href="/dashboard/seller" className={s.primary}>{c.seller} →</Link></div></div>
      <div className={s.card}><h3>{c.api}</h3><p>{c.apiBody}</p><div className={s.actions}><Link className={s.secondary} href="/developers">API</Link><Link className={s.secondary} href="/mcp">MCP</Link><Link className={s.secondary} href="/proof-center">{c.trust}</Link></div></div>
    </div></section>
    <section className={s.section} id="vision"><p className={s.eyebrow}>{c.investors}</p><h2 className={s.heading}>{c.investmentTitle}</h2><p className={s.lead}>{c.investmentLead}</p><div className={s.actions}><Link className={s.secondary} href="/investors">{c.investors} →</Link></div></section>
  </main><WorkflowFooter /></div>;
}
