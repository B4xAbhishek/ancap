"use client";

import { useEffect, useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { projectPresentation } from "@/lib/solutionPortfolio";
import { Navigation } from "@/components/Navigation";
import { DnaNanobotScissors } from "@/components/DnaNanobotScissors";
import { DnaHelixSandbox } from "@/components/aeterna/DnaHelixSandbox";
import { GenomeHashVaultPanel } from "@/components/aeterna/GenomeHashVaultPanel";
import { MolecularAgingPanel } from "@/components/aeterna/MolecularAgingPanel";
import { MrnaReprogrammingPanel } from "@/components/aeterna/MrnaReprogrammingPanel";
import { VetRegenPanel } from "@/components/aeterna/VetRegenPanel";
import { VinciLightPanel } from "@/components/aeterna/VinciLightPanel";
import { MicrowaveBodyPanel } from "@/components/aeterna/MicrowaveBodyPanel";
import { BioFusionPanel } from "@/components/aeterna/BioFusionPanel";
import { DpscBiomaterialPanel } from "@/components/aeterna/DpscBiomaterialPanel";
import { VascularCarePlusPanel } from "@/components/aeterna/VascularCarePlusPanel";
import { VascularCarePanel } from "@/components/aeterna/VascularCarePanel";
import { TransdermalPistolPanel } from "@/components/aeterna/TransdermalPistolPanel";
import { MReceptorPanel } from "@/components/aeterna/MReceptorPanel";
import { OxygenCarrierPanel } from "@/components/aeterna/OxygenCarrierPanel";
import { SyntheticBloodMambaPanel } from "@/components/aeterna/SyntheticBloodMambaPanel";
import { AdhdSupportPanel } from "@/components/aeterna/AdhdSupportPanel";
import { AureaVitaPanel } from "@/components/aeterna/AureaVitaPanel";
import { DownSyndromeSupportPanel } from "@/components/aeterna/DownSyndromeSupportPanel";
import { SubstanceCodingPanel } from "@/components/aeterna/SubstanceCodingPanel";
import { PulmoPurePanel } from "@/components/aeterna/PulmoPurePanel";
import { InstallationProjectPanel } from "@/components/aeterna/InstallationProjectPanel";
import { DnaPheromonePerfumePanel } from "@/components/aeterna/DnaPheromonePerfumePanel";
import { getApiUrl } from "@/lib/api";
import { useLanguage } from "@/components/LanguageProvider";

type AgingHallmark = {
  id: string;
  title: string;
  gene_pair_hint: string;
  theme: string;
};

type AeternaStatus = {
  feature_enabled: boolean;
  division: string;
  tagline: string;
  vault_entries: number;
  intent_orders: number;
  partners_verified: number;
  workflow_slugs: string[];
  sequencing_import_hint: string;
  compliance_note: string;
  next_gate: string;
  aging_hallmarks?: AgingHallmark[];
  molecular_aging_note?: string;
  reprogramming_note?: string;
  vet_regen_note?: string;
  vinci_light_note?: string;
  microwave_body_note?: string;
  biofusion_note?: string;
  dpsc_biomaterial_note?: string;
  vascular_care_plus_note?: string;
  vascular_care_note?: string;
  transdermal_pistol_note?: string;
  m_receptor_note?: string;
  oxygen_carrier_note?: string;
  synthetic_blood_mamba_note?: string;
  adhd_support_note?: string;
  aurea_vita_note?: string;
  down_syndrome_support_note?: string;
  substance_coding_note?: string;
  pulmopure_note?: string;
  barsuk_note?: string;
  teleport_earphones_note?: string;
  installation_project_note?: string;
  dna_pheromone_perfume_note?: string;
};

const INTENT_KEYS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27] as const;
const ORGAN_PRINT_SLUG = "aeterna-stem-cell-organ-print";

/** Public landing — sandbox + local hash work with zero account. Cloud vault sync is optional. */
export default function AeternaPage() {
  const { t, lang } = useLanguage();
  const projectCopy = projectPresentation(lang, "/aeterna");
  const [status, setStatus] = useState<AeternaStatus | null>(null);
  const [heroOk, setHeroOk] = useState(true);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await fetch(`${getApiUrl()}/aeterna/status`, { credentials: "omit" });
        if (!res.ok) return;
        if (!cancelled) setStatus((await res.json()) as AeternaStatus);
      } catch {
        /* Public page stays usable offline / when API is briefly down */
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="min-h-screen bg-[#05070c] text-[#e8eef8]">
      <Navigation />

      <section className="relative min-h-[100svh] overflow-hidden">
        {heroOk ? (
          <Image
            src="/aeterna/hero.jpg"
            alt={t("aeternaPage.heroAlt")}
            fill
            priority
            className="object-cover object-center"
            sizes="100vw"
            onError={() => setHeroOk(false)}
          />
        ) : (
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_30%_40%,#0d3a38_0%,#05070c_55%)]" />
        )}
        <div className="absolute inset-0 bg-gradient-to-r from-[#05070c]/90 via-[#05070c]/55 to-[#05070c]/25" />
        <div className="absolute inset-0 bg-gradient-to-t from-[#05070c] via-transparent to-[#05070c]/40" />

        <div className="relative mx-auto flex min-h-[100svh] max-w-6xl flex-col justify-end px-4 pb-16 pt-28 sm:px-6 lg:px-8">
          <p className="font-[family-name:var(--font-display,inherit)] text-[clamp(3.5rem,12vw,8rem)] font-black leading-[0.85] tracking-[-0.06em] text-white">
            AETERNA
          </p>
          <h1 className="mt-5 max-w-xl text-xl font-medium tracking-[-0.02em] text-white/90 sm:text-2xl">
            {projectCopy.title}
          </h1>
          <p className="mt-4 max-w-lg text-sm leading-7 text-white/65">
            {projectCopy.lead}
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <a
              href="#dna-sandbox"
              className="rounded-md bg-[#7ad0c8] px-5 py-3 text-sm font-semibold text-[#04201e] transition hover:bg-[#9ae0d9]"
            >
              {t("aeternaPage.openSandbox")}
            </a>
            <Link
              href="/ai/workflows"
              className="rounded-md border border-white/30 px-5 py-3 text-sm font-medium text-white/90 transition hover:border-white/60"
            >
              {t("aeternaPage.browseWorkflows")}
            </Link>
            <a
              href="#molecular-aging"
              className="rounded-md border border-[#7ad0c8]/40 px-5 py-3 text-sm font-medium text-[#9ae0d9] transition hover:border-[#7ad0c8]"
            >
              {t("aeternaPage.agingCta")}
            </a>
            <a
              href="#mrna-reprogramming"
              className="rounded-md border border-[#7ad0c8]/40 px-5 py-3 text-sm font-medium text-[#9ae0d9] transition hover:border-[#7ad0c8]"
            >
              {t("aeternaPage.mrnaCta")}
            </a>
            <a
              href="#organ-print"
              className="rounded-md border border-white/30 px-5 py-3 text-sm font-medium text-white/90 transition hover:border-white/60"
            >
              {t("aeternaPage.organSkuCta")}
            </a>
            <a
              href="#vet-regen"
              className="rounded-md border border-[#7ad0c8]/40 px-5 py-3 text-sm font-medium text-[#9ae0d9] transition hover:border-[#7ad0c8]"
            >
              {t("aeternaPage.organRailCta")}
            </a>
            <a
              href="#vinci-light"
              className="rounded-md border border-[#7ad0c8]/40 px-5 py-3 text-sm font-medium text-[#9ae0d9] transition hover:border-[#7ad0c8]"
            >
              {t("aeternaPage.vinciCta")}
            </a>
            <a
              href="#microwave-body"
              className="rounded-md border border-[#7ad0c8]/40 px-5 py-3 text-sm font-medium text-[#9ae0d9] transition hover:border-[#7ad0c8]"
            >
              {t("aeternaPage.mwCta")}
            </a>
            <a
              href="#biofusion"
              className="rounded-md border border-[#7ad0c8]/40 px-5 py-3 text-sm font-medium text-[#9ae0d9] transition hover:border-[#7ad0c8]"
            >
              {t("aeternaPage.bfCta")}
            </a>
            <a
              href="#dpsc-biomaterial"
              className="rounded-md border border-[#7ad0c8]/40 px-5 py-3 text-sm font-medium text-[#9ae0d9] transition hover:border-[#7ad0c8]"
            >
              {t("aeternaPage.dpscCta")}
            </a>
            <a
              href="#vascular-care-plus"
              className="rounded-md border border-[#7ad0c8]/40 px-5 py-3 text-sm font-medium text-[#9ae0d9] transition hover:border-[#7ad0c8]"
            >
              {t("aeternaPage.vplusCta")}
            </a>
            <a
              href="#vascular-care"
              className="rounded-md border border-[#7ad0c8]/40 px-5 py-3 text-sm font-medium text-[#9ae0d9] transition hover:border-[#7ad0c8]"
            >
              {t("aeternaPage.vusCta")}
            </a>
            <a
              href="#transdermal"
              className="rounded-md border border-[#7ad0c8]/40 px-5 py-3 text-sm font-medium text-[#9ae0d9] transition hover:border-[#7ad0c8]"
            >
              {t("aeternaPage.tdpCta")}
            </a>
            <a
              href="#m-receptor"
              className="rounded-md border border-[#7ad0c8]/40 px-5 py-3 text-sm font-medium text-[#9ae0d9] transition hover:border-[#7ad0c8]"
            >
              {t("aeternaPage.mrCta")}
            </a>
            <a
              href="#oxygen-carrier"
              className="rounded-md border border-[#7ad0c8]/40 px-5 py-3 text-sm font-medium text-[#9ae0d9] transition hover:border-[#7ad0c8]"
            >
              {t("aeternaPage.oxCta")}
            </a>
            <a
              href="#synthetic-blood-mamba"
              className="rounded-md border border-[#7ad0c8]/40 px-5 py-3 text-sm font-medium text-[#9ae0d9] transition hover:border-[#7ad0c8]"
            >
              {t("aeternaPage.sbmCta")}
            </a>
            <a
              href="#adhd-support"
              className="rounded-md border border-[#7ad0c8]/40 px-5 py-3 text-sm font-medium text-[#9ae0d9] transition hover:border-[#7ad0c8]"
            >
              {t("aeternaPage.adhdCta")}
            </a>
            <a
              href="#down-syndrome-support"
              className="rounded-md border border-[#8bb8e8]/40 px-5 py-3 text-sm font-medium text-[#b7d4f5] transition hover:border-[#8bb8e8]"
            >
              {t("aeternaPage.downCta")}
            </a>
            <a
              href="#substance-coding"
              className="rounded-md border border-[#c4a878]/40 px-5 py-3 text-sm font-medium text-[#e8d4b0] transition hover:border-[#c4a878]"
            >
              {t("aeternaPage.codingCta")}
            </a>
            <a
              href="#pulmopure"
              className="rounded-md border border-[#7ad0c8]/40 px-5 py-3 text-sm font-medium text-[#9ae0d9] transition hover:border-[#7ad0c8]"
            >
              {t("aeternaPage.ppCta")}
            </a>
            <a
              href="#dna-pheromone-perfume"
              className="rounded-md border border-[#d4a574]/40 px-5 py-3 text-sm font-medium text-[#e8c9a0] transition hover:border-[#d4a574]"
            >
              {t("aeternaPage.ppfCta")}
            </a>
          </div>
        </div>
      </section>

      <section className="border-b border-white/10 bg-[#05070c]" aria-label="Nanobot DNA scissors visualization">
        <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6 lg:px-8">
          <p className="mb-4 text-xs uppercase tracking-[0.16em] text-white/40">
            {t("aeternaPage.demoKicker")}
          </p>
          <div className="overflow-hidden rounded-xl border border-white/10">
            <DnaNanobotScissors />
          </div>
        </div>
      </section>

      <main className="mx-auto max-w-6xl px-4 py-16 sm:px-6 lg:px-8">
        <section id="dna-sandbox" className="scroll-mt-24">
          <h2 className="text-2xl font-semibold tracking-[-0.03em]">{t("aeternaPage.sandboxTitle")}</h2>
          <p className="mt-3 max-w-2xl text-sm leading-7 text-white/65">
            {t("aeternaPage.sandboxLead")}
          </p>
          <div className="mt-8">
            <DnaHelixSandbox />
          </div>
        </section>

        <section className="mt-16">
          <GenomeHashVaultPanel />
        </section>

        <section className="mt-16">
          <MolecularAgingPanel
            hallmarks={status?.aging_hallmarks}
            note={status?.molecular_aging_note}
          />
        </section>

        <section className="mt-16">
          <MrnaReprogrammingPanel note={status?.reprogramming_note} />
        </section>

        <section className="mt-16">
          <VetRegenPanel note={status?.vet_regen_note} />
        </section>

        <section className="mt-16">
          <VinciLightPanel note={status?.vinci_light_note} />
        </section>

        <section className="mt-16">
          <MicrowaveBodyPanel note={status?.microwave_body_note} />
        </section>

        <section className="mt-16">
          <BioFusionPanel note={status?.biofusion_note} />
        </section>

        <section className="mt-16">
          <DpscBiomaterialPanel note={status?.dpsc_biomaterial_note} />
        </section>

        <section className="mt-16">
          <VascularCarePlusPanel note={status?.vascular_care_plus_note} />
        </section>

        <section className="mt-16">
          <VascularCarePanel note={status?.vascular_care_note} />
        </section>

        <section className="mt-16">
          <TransdermalPistolPanel note={status?.transdermal_pistol_note} />
        </section>

        <section className="mt-16">
          <MReceptorPanel note={status?.m_receptor_note} />
        </section>

        <section className="mt-16">
          <OxygenCarrierPanel note={status?.oxygen_carrier_note} />
        </section>

        <section className="mt-16">
          <SyntheticBloodMambaPanel note={status?.synthetic_blood_mamba_note} />
        </section>

        <section className="mt-16">
          <AdhdSupportPanel note={status?.adhd_support_note} />
        </section>

        <section className="mt-16">
          <AureaVitaPanel note={status?.aurea_vita_note} />
        </section>

        <section className="mt-16">
          <DownSyndromeSupportPanel note={status?.down_syndrome_support_note} />
        </section>

        <section className="mt-16">
          <SubstanceCodingPanel note={status?.substance_coding_note} />
        </section>

        <section className="mt-16">
          <PulmoPurePanel note={status?.pulmopure_note} />
        </section>

        <section className="mt-16">
          <InstallationProjectPanel note={status?.installation_project_note} />
        </section>

        <section className="mt-16">
          <DnaPheromonePerfumePanel note={status?.dna_pheromone_perfume_note} />
        </section>

        <section className="mt-16 max-w-2xl">
          <h2 className="text-2xl font-semibold tracking-[-0.03em]">{t("aeternaPage.payTitle")}</h2>
          <p className="mt-3 text-sm leading-7 text-white/65">
            {t("aeternaPage.payLead")}
          </p>
        </section>

        <ul className="mt-10 grid gap-8 sm:grid-cols-2">
          {INTENT_KEYS.map((idx) => (
            <li key={idx}>
              <h3 className="text-lg font-medium tracking-[-0.02em] text-[#9ae0d9]">{t(`aeternaPage.intent${idx}Title`)}</h3>
              <p className="mt-2 text-sm leading-7 text-white/65">{t(`aeternaPage.intent${idx}Body`)}</p>
            </li>
          ))}
        </ul>

        <section
          id="organ-print"
          className="mt-14 scroll-mt-24 rounded-2xl border border-[#7ad0c8]/25 bg-[#7ad0c8]/5 p-6 sm:p-8"
        >
          <p className="text-xs uppercase tracking-[0.16em] text-[#9ae0d9]">{t("aeternaPage.organSkuKicker")}</p>
          <div className="mt-3 flex flex-wrap items-end justify-between gap-4">
            <h2 className="text-2xl font-semibold tracking-[-0.03em]">{t("aeternaPage.organSkuTitle")}</h2>
            <p className="font-mono text-2xl font-semibold text-[#9ae0d9]">{t("aeternaPage.organSkuPrice")}</p>
          </div>
          <p className="mt-4 max-w-2xl text-sm leading-7 text-white/70">{t("aeternaPage.organSkuLead")}</p>
          <Link
            href={`/ai/run/${ORGAN_PRINT_SLUG}`}
            className="mt-6 inline-flex rounded-md bg-[#7ad0c8] px-5 py-3 text-sm font-semibold text-[#04201e] transition hover:bg-[#9ae0d9]"
          >
            {t("aeternaPage.organSkuCta")}
          </Link>
        </section>

        <section className="mt-14 border-t border-white/10 pt-10">
          <h2 className="text-2xl font-semibold tracking-[-0.03em]">{t("aeternaPage.imagingTitle")}</h2>
          <p className="mt-3 max-w-2xl text-sm leading-7 text-white/65">{t("aeternaPage.imagingLead")}</p>
          <div className="mt-5 flex flex-wrap gap-3 text-sm">
            <a
              href="https://www.zeiss.com/microscopy/en/products/light-microscopes/confocal-microscopes/lightfield-4d.html"
              target="_blank"
              rel="noopener noreferrer"
              className="rounded-md border border-white/15 px-4 py-2 text-white/80 transition hover:border-white/35 hover:text-white"
            >
              ZEISS Lightfield 4D
            </a>
            <a
              href="https://guide.microscopy.zeiss.com/content/hbrXqJoB8mu68yTAwSxe"
              target="_blank"
              rel="noopener noreferrer"
              className="rounded-md border border-white/15 px-4 py-2 text-white/80 transition hover:border-white/35 hover:text-white"
            >
              {t("aeternaPage.imagingTechNote")}
            </a>
            <Link
              href="/legal/research-refs"
              className="rounded-md border border-teal-300/25 px-4 py-2 text-teal-100/90 transition hover:border-teal-200/50"
            >
              {t("aeternaPage.imagingNoteCta")}
            </Link>
          </div>
        </section>

        <section className="mt-14 border-t border-white/10 pt-10">
          <h2 className="text-2xl font-semibold tracking-[-0.03em]">{t("aeternaPage.statusTitle")}</h2>
          <p className="mt-3 max-w-2xl text-sm leading-7 text-white/65">
            {t("aeternaPage.taglineFallback")}
          </p>
          <p className="mt-2 max-w-2xl text-sm leading-7 text-white/50">
            {t("aeternaPage.complianceFallback")}
          </p>
          <dl className="mt-8 grid gap-6 sm:grid-cols-3">
            <div>
              <dt className="text-xs uppercase tracking-[0.16em] text-white/40">{t("aeternaPage.feature")}</dt>
              <dd className="mt-1 text-2xl font-semibold">
                {status ? (status.feature_enabled ? t("aeternaPage.featureOn") : t("aeternaPage.featureOff")) : t("aeternaPage.featurePublic")}
              </dd>
            </div>
            <div>
              <dt className="text-xs uppercase tracking-[0.16em] text-white/40">{t("aeternaPage.vaultEntries")}</dt>
              <dd className="mt-1 text-2xl font-semibold">{status?.vault_entries ?? "—"}</dd>
            </div>
            <div>
              <dt className="text-xs uppercase tracking-[0.16em] text-white/40">{t("aeternaPage.workflows")}</dt>
              <dd className="mt-1 text-2xl font-semibold">{status?.workflow_slugs.length ?? 11}</dd>
            </div>
          </dl>
          {status && (
            <>
              <p className="mt-6 text-sm text-white/55">{status.sequencing_import_hint}</p>
              <p className="mt-2 text-xs uppercase tracking-[0.14em] text-white/35">
                {t("aeternaPage.next")} {status.next_gate}
              </p>
              <ul className="mt-6 flex flex-wrap gap-2 font-mono text-xs text-white/50">
                {status.workflow_slugs.map((slug) => (
                  <li key={slug} className="border border-white/10 px-2 py-1">
                    {slug}
                  </li>
                ))}
              </ul>
            </>
          )}
        </section>
      </main>
    </div>
  );
}
