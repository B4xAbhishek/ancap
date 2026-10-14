"use client";
import Link from "next/link";
import { Navigation } from "@/components/Navigation";
import { useLanguage } from "@/components/LanguageProvider";
import { SolutionAreas, WorkflowFooter, presentationStyles as s } from "@/components/WorkflowPresentation";
import { positioningByLang } from "@/locales/positioning";
export default function ProjectsPage() {
  const { lang } = useLanguage();
  const c = positioningByLang[lang];
  return <div className={s.shell}><Navigation /><main className={s.main}>
    <section className={s.section} style={{ borderTop: 0, paddingTop: 60 }}>
      <p className={s.eyebrow}>ANCAP / {c.solutions}</p><h1 className={s.title}>{c.portfolio}</h1><p className={s.lead}>{c.portfolioLead}</p>
      <div className={s.actions}><Link href="/ai/workflows" className={s.primary}>{c.browse} →</Link><Link href="/investors" className={s.secondary}>{c.investors}</Link></div>
      <SolutionAreas /><p className={s.note}>{c.portfolioNote}</p>
    </section>
  </main><WorkflowFooter /></div>;
}
