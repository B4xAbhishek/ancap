"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { projectPresentation } from "@/lib/solutionPortfolio";
import { Navigation } from "@/components/Navigation";
import { useAuth } from "@/components/AuthProvider";
import { useLanguage } from "@/components/LanguageProvider";
import { salivaRxDesk } from "@/lib/api";
import { ServiceReviewsPanel } from "@/components/ServiceReviewsPanel";

type PipelineStep = { id: string; label: string; detail: string };

type Service = {
  id: string;
  review_target_id: string;
  label: string;
  price_from_acp: string;
  blurb: string;
};

type Partner = {
  id: string;
  review_target_id: string;
  name: string;
  jurisdiction: string;
  website: string;
  blurb: string;
  verified: boolean;
};

type Catalog = {
  title: string;
  tagline: string;
  compliance_note: string;
  pipeline: PipelineStep[];
  services: Service[];
  partners: Partner[];
  legal_href: string;
};

export default function SalivaRxPage() {
  const { t, lang } = useLanguage();
  const projectCopy = projectPresentation(lang, "/saliva-rx");
  const { user, isAuthenticated } = useAuth();
  const [catalog, setCatalog] = useState<Catalog | null>(null);
  const [error, setError] = useState("");
  const [selectedReviewId, setSelectedReviewId] = useState<string | null>(null);
  const [selectedLabel, setSelectedLabel] = useState("");
  const [selectedKind, setSelectedKind] = useState<"service" | "partner">("service");

  const load = useCallback(async () => {
    try {
      const data = (await salivaRxDesk.catalog()) as Catalog;
      setCatalog(data);
      setError("");
      if (!selectedReviewId && data.services[0]) {
        setSelectedReviewId(data.services[0].review_target_id);
        setSelectedLabel(data.services[0].label);
        setSelectedKind("service");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : t("salivaRxPage.loadError"));
    }
  }, [selectedReviewId, t]);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <main className="min-h-screen bg-[#0c1410] text-slate-100">
      <Navigation />
      <section className="mx-auto max-w-5xl px-4 py-10">
        <p className="text-sm uppercase tracking-[0.2em] text-emerald-400/80">{t("salivaRxPage.kicker")}</p>
        <h1 className="mt-2 font-serif text-4xl text-white md:text-5xl">
          {projectCopy.title}
        </h1>
        <p className="mt-3 max-w-2xl text-slate-300">{projectCopy.lead}</p>
        <p className="mt-4 text-sm leading-6 text-slate-500">{catalog?.compliance_note}</p>
        <p className="mt-3 text-sm">
          <Link href={catalog?.legal_href || "/legal/saliva-rx-notice"} className="text-emerald-300 underline">
            {t("deskCommon.legalNotice")}
          </Link>
          {" · "}
          <Link href="/aeterna" className="text-emerald-300 underline">
            {t("salivaRxPage.aeterna")}
          </Link>
          {" · "}
          <Link href="/dna-bank" className="text-emerald-300 underline">
            {t("salivaRxPage.dnaBank")}
          </Link>
        </p>

        {error ? <p className="mt-4 text-sm text-rose-400">{error}</p> : null}

        <h2 className="mt-10 text-xl text-white">{t("deskCommon.pipeline")}</h2>
        <ol className="mt-4 grid gap-4 md:grid-cols-2">
          {(catalog?.pipeline || []).map((step) => (
            <li key={step.id} className="border border-emerald-500/20 bg-emerald-950/20 p-4">
              <div className="font-medium text-emerald-100">{step.label}</div>
              <p className="mt-2 text-sm text-slate-400">{step.detail}</p>
            </li>
          ))}
        </ol>

        <h2 className="mt-10 text-xl text-white">{t("deskCommon.services")}</h2>
        <ul className="mt-4 space-y-5">
          {(catalog?.services || []).map((svc) => (
            <li key={svc.id} className="border-t border-white/10 pt-4">
              <div className="flex flex-wrap items-baseline justify-between gap-2">
                <h3 className="text-lg text-white">{svc.label}</h3>
                <span className="text-sm text-emerald-200/80">
                  {t("deskCommon.fromAcp").replace("{price}", svc.price_from_acp)}
                </span>
              </div>
              <p className="mt-2 text-slate-300">{svc.blurb}</p>
              <button
                type="button"
                className="mt-3 border border-emerald-400/40 px-3 py-1.5 text-sm text-emerald-100 hover:bg-emerald-400/10"
                onClick={() => {
                  setSelectedReviewId(svc.review_target_id);
                  setSelectedLabel(svc.label);
                  setSelectedKind("service");
                }}
              >
                {t("deskCommon.reviews")}
              </button>
            </li>
          ))}
        </ul>

        <h2 className="mt-10 text-xl text-white">{t("deskCommon.partners")}</h2>
        <ul className="mt-4 space-y-5">
          {(catalog?.partners || []).map((p) => (
            <li key={p.id} className="border-t border-white/10 pt-4">
              <div className="flex flex-wrap items-baseline justify-between gap-2">
                <h3 className="text-lg text-white">{p.name}</h3>
                <span className="text-xs uppercase tracking-wide text-slate-400">
                  {p.jurisdiction}
                  {p.verified ? ` · ${t("salivaRxPage.verified")}` : ` · ${t("salivaRxPage.intakeSlot")}`}
                </span>
              </div>
              <p className="mt-2 text-slate-300">{p.blurb}</p>
              <button
                type="button"
                className="mt-3 border border-emerald-400/40 px-3 py-1.5 text-sm text-emerald-100 hover:bg-emerald-400/10"
                onClick={() => {
                  setSelectedReviewId(p.review_target_id);
                  setSelectedLabel(p.name);
                  setSelectedKind("partner");
                }}
              >
                {t("deskCommon.reviews")}
              </button>
            </li>
          ))}
        </ul>

        {selectedReviewId ? (
          <div className="mt-12">
            <ServiceReviewsPanel
              targetType={selectedKind}
              targetId={selectedReviewId}
              label={selectedLabel}
              reviewerUserId={isAuthenticated ? user?.id : undefined}
            />
          </div>
        ) : null}
      </section>
    </main>
  );
}
