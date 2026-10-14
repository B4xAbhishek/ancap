"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { projectPresentation } from "@/lib/solutionPortfolio";
import { Navigation } from "@/components/Navigation";
import { useAuth } from "@/components/AuthProvider";
import { useLanguage } from "@/components/LanguageProvider";
import { cryoDesk } from "@/lib/api";
import { ServiceReviewsPanel } from "@/components/ServiceReviewsPanel";

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
  verified?: boolean;
  listing_kind?: string;
  clinical_endorsement?: boolean;
  ethics_note?: string;
  regulatory_note?: string;
};

type Catalog = {
  title: string;
  tagline: string;
  compliance_note: string;
  services: Service[];
  partners: Partner[];
  legal_href: string;
};

export default function CryoPage() {
  const { t, lang } = useLanguage();
  const projectCopy = projectPresentation(lang, "/cryo");
  const { user, isAuthenticated } = useAuth();
  const [catalog, setCatalog] = useState<Catalog | null>(null);
  const [error, setError] = useState("");
  const [selectedReviewId, setSelectedReviewId] = useState<string | null>(null);
  const [selectedLabel, setSelectedLabel] = useState("");
  const [selectedKind, setSelectedKind] = useState<"service" | "partner">("service");

  const load = useCallback(async () => {
    try {
      const data = (await cryoDesk.catalog()) as Catalog;
      setCatalog(data);
      setError("");
      if (!selectedReviewId && data.services[0]) {
        setSelectedReviewId(data.services[0].review_target_id);
        setSelectedLabel(data.services[0].label);
        setSelectedKind("service");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : t("cryoPage.loadError"));
    }
  }, [selectedReviewId, t]);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <main className="min-h-screen bg-[#0a1218] text-slate-100">
      <Navigation />
      <section className="mx-auto max-w-5xl px-4 py-10">
        <p className="text-sm uppercase tracking-[0.2em] text-sky-400/80">{t("cryoPage.kicker")}</p>
        <h1 className="mt-2 font-serif text-4xl text-white md:text-5xl">
          {projectCopy.title}
        </h1>
        <p className="mt-3 max-w-2xl text-slate-300">{projectCopy.lead}</p>
        <p className="mt-4 text-sm leading-6 text-slate-500">{catalog?.compliance_note}</p>
        <p className="mt-3 text-sm">
          <Link href={catalog?.legal_href || "/legal/cryo-constitution"} className="text-sky-300 underline">
            {t("cryoPage.legalConstitutional")}
          </Link>
          {" · "}
          <Link href="/literary" className="text-sky-300 underline">
            {t("cryoPage.literaryAuction")}
          </Link>
        </p>

        {error ? <p className="mt-4 text-sm text-rose-400">{error}</p> : null}

        <h2 className="mt-10 text-xl text-white">{t("deskCommon.services")}</h2>
        <ul className="mt-4 space-y-5">
          {(catalog?.services || []).map((svc) => (
            <li key={svc.id} className="border-t border-white/10 pt-4">
              <div className="flex flex-wrap items-baseline justify-between gap-2">
                <h3 className="text-lg text-white">{svc.label}</h3>
                <span className="text-sm text-sky-200/80">
                  {t("deskCommon.fromAcp").replace("{price}", svc.price_from_acp)}
                </span>
              </div>
              <p className="mt-2 text-slate-300">{svc.blurb}</p>
              <button
                type="button"
                className="mt-3 border border-sky-400/40 px-3 py-1.5 text-sm text-sky-100 hover:bg-sky-400/10"
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

        <h2 className="mt-12 text-xl text-white">{t("deskCommon.partners")}</h2>
        <ul className="mt-4 space-y-5">
          {(catalog?.partners || []).map((p) => (
            <li key={p.id} className="border-t border-white/10 pt-4">
              <div className="flex flex-wrap items-baseline justify-between gap-2">
                <h3 className="text-lg text-white">{p.name}</h3>
                <span className="text-sm text-slate-400">{p.jurisdiction}</span>
              </div>
              <p className="mt-2 text-slate-300">{p.blurb}</p>
              {p.clinical_endorsement === false ? (
                <p className="mt-2 text-xs uppercase tracking-wide text-amber-200/70">
                  {t("cryoPage.notClinicalEndorsement")}
                </p>
              ) : null}
              {p.ethics_note ? <p className="mt-2 text-sm text-slate-400">{p.ethics_note}</p> : null}
              {p.regulatory_note ? <p className="mt-1 text-sm text-slate-500">{p.regulatory_note}</p> : null}
              <div className="mt-3 flex flex-wrap gap-3 text-sm">
                <a
                  href={p.website}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sky-300 underline"
                >
                  {t("deskCommon.website")}
                </a>
                <button
                  type="button"
                  className="border border-sky-400/40 px-3 py-1.5 text-sky-100 hover:bg-sky-400/10"
                  onClick={() => {
                    setSelectedReviewId(p.review_target_id);
                    setSelectedLabel(p.name);
                    setSelectedKind("partner");
                  }}
                >
                  {t("deskCommon.reviews")}
                </button>
              </div>
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
