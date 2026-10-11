"use client";

import type { ReactNode } from "react";
import Link from "next/link";
import { Navigation } from "@/components/Navigation";
import { useLanguage } from "@/components/LanguageProvider";

const pill =
  "rounded-full border border-white/15 px-5 py-2.5 text-sm font-semibold text-white/85 transition hover:border-white/30 hover:text-white";
const pillAccent =
  "rounded-full border border-emerald-400/25 px-5 py-2.5 text-sm font-semibold text-emerald-200 transition hover:border-emerald-300/50 hover:text-emerald-100";

function LegalShell({
  kickerClass,
  kicker,
  title,
  intro,
  actions,
  children,
}: {
  kickerClass: string;
  kicker: string;
  title: string;
  intro: string;
  actions: ReactNode;
  children: ReactNode;
}) {
  return (
    <div className="min-h-screen bg-[var(--bg)] text-[var(--text)]">
      <Navigation />
      <main className="mx-auto max-w-5xl px-4 py-10 sm:px-6 lg:px-8">
        <section className={`rounded-3xl border p-6 sm:p-8 ${kickerClass}`}>
          <div className="text-xs uppercase tracking-[0.18em] text-emerald-200/75">{kicker}</div>
          <h1 className="mt-3 text-3xl font-semibold tracking-[-0.04em] sm:text-5xl">{title}</h1>
          <p className="mt-4 text-sm leading-7 text-white/72 sm:text-base">{intro}</p>
          <div className="mt-5 flex flex-wrap gap-3">{actions}</div>
        </section>
        {children}
      </main>
    </div>
  );
}

function LegalNavPills({ current }: { current?: string }) {
  const { t } = useLanguage();
  const items = [
    { href: "/legal", key: "hubLink" },
    { href: "/legal/terms", key: "termsLink" },
    { href: "/legal/privacy", key: "privacyLink" },
    { href: "/legal/cookies", key: "cookiesLink" },
    { href: "/legal/risk", key: "riskLink" },
    { href: "/legal/market-data", key: "marketDataLink" },
    { href: "/legal/research-refs", key: "researchRefsLink" },
    { href: "/legal/cryo-constitution", key: "cryoLink" },
    { href: "/legal/vet-regen", key: "vetRegenLink" },
    { href: "/legal/light-chamber", key: "lightChamberLink" },
    { href: "/legal/body-contouring", key: "bodyContouringLink" },
    { href: "/legal/biofusion", key: "biofusionLink" },
    { href: "/legal/dpsc", key: "dpscLink" },
    { href: "/legal/vascular-care-plus", key: "vascularPlusLink" },
    { href: "/legal/vascular-care", key: "vascularLink" },
    { href: "/legal/transdermal", key: "transdermalLink" },
    { href: "/legal/m-receptor", key: "mReceptorLink" },
    { href: "/legal/oxygen-carrier", key: "oxygenCarrierLink" },
    { href: "/legal/synthetic-blood-mamba", key: "syntheticBloodMambaLink" },
    { href: "/legal/adhd-support", key: "adhdSupportLink" },
    { href: "/legal/aurea-vita", key: "aureaVitaLink" },
    { href: "/legal/down-syndrome-support", key: "downSyndromeSupportLink" },
    { href: "/legal/substance-coding", key: "substanceCodingLink" },
    { href: "/legal/tesla-coil-party", key: "teslaCoilPartyLink" },
    { href: "/legal/antique-fire-restore", key: "antiqueFireRestoreLink" },
    { href: "/legal/pulmopure", key: "pulmopureLink" },
    { href: "/legal/barsuk", key: "barsukLink" },
    { href: "/legal/teleport-earphones", key: "teleportEarphonesLink" },
    { href: "/legal/installation-project", key: "installationProjectLink" },
    { href: "/legal/dna-pheromone-perfume", key: "dnaPheromonePerfumeLink" },
    { href: "/legal/stardust", key: "stardustLink" },
    { href: "/legal/dark-matter", key: "darkMatterLink" },
    { href: "/legal/refunds", key: "refundsLink" },
    { href: "/legal/welcome-grant", key: "welcomeGrantLink" },
    { href: "/legal/humanitarian", key: "humanitarianLink" },
    { href: "/legal/counsel", key: "counselLink" },
    { href: "/legal/starlink-install", key: "starlinkInstallLink" },
    { href: "/legal/field-services", key: "fieldServicesLink" },
    { href: "/legal/space-ai-datacenter", key: "spaceAiDatacenterLink" },
    { href: "/legal/cyber-defense", key: "cyberLink", accent: true },
    { href: "/legal/clarity-act", key: "clarityLink", accent: true },
  ] as const;
  return (
    <>
      {items.map((item) => (
        <Link
          key={item.href}
          href={item.href}
          className={
            current === item.href
              ? "rounded-full border border-white/35 bg-white/10 px-5 py-2.5 text-sm font-semibold text-white"
              : "accent" in item && item.accent
                ? pillAccent
                : pill
          }
        >
          {t(`legal.${item.key}`)}
        </Link>
      ))}
    </>
  );
}

export function LegalHubView() {
  const { t } = useLanguage();
  const cards = [
    { href: "/legal/terms", title: "termsLink", body: "hubCardTerms" },
    { href: "/legal/privacy", title: "privacyLink", body: "hubCardPrivacy" },
    { href: "/legal/cookies", title: "cookiesLink", body: "hubCardCookies" },
    { href: "/legal/risk", title: "riskLink", body: "hubCardRisk" },
    { href: "/legal/market-data", title: "marketDataLink", body: "hubCardMarketData" },
    { href: "/legal/research-refs", title: "researchRefsLink", body: "hubCardResearchRefs" },
    { href: "/legal/cryo-constitution", title: "cryoLink", body: "hubCardCryo" },
    { href: "/legal/vet-regen", title: "vetRegenLink", body: "hubCardVetRegen" },
    { href: "/legal/light-chamber", title: "lightChamberLink", body: "hubCardLightChamber" },
    { href: "/legal/body-contouring", title: "bodyContouringLink", body: "hubCardBodyContouring" },
    { href: "/legal/biofusion", title: "biofusionLink", body: "hubCardBiofusion" },
    { href: "/legal/dpsc", title: "dpscLink", body: "hubCardDpsc" },
    { href: "/legal/vascular-care-plus", title: "vascularPlusLink", body: "hubCardVascularPlus" },
    { href: "/legal/vascular-care", title: "vascularLink", body: "hubCardVascular" },
    { href: "/legal/transdermal", title: "transdermalLink", body: "hubCardTransdermal" },
    { href: "/legal/m-receptor", title: "mReceptorLink", body: "hubCardMReceptor" },
    { href: "/legal/oxygen-carrier", title: "oxygenCarrierLink", body: "hubCardOxygenCarrier" },
    { href: "/legal/synthetic-blood-mamba", title: "syntheticBloodMambaLink", body: "hubCardSyntheticBloodMamba" },
    { href: "/legal/adhd-support", title: "adhdSupportLink", body: "hubCardAdhdSupport" },
    { href: "/legal/aurea-vita", title: "aureaVitaLink", body: "hubCardAureaVita" },
    { href: "/legal/down-syndrome-support", title: "downSyndromeSupportLink", body: "hubCardDownSyndromeSupport" },
    { href: "/legal/substance-coding", title: "substanceCodingLink", body: "hubCardSubstanceCoding" },
    { href: "/legal/tesla-coil-party", title: "teslaCoilPartyLink", body: "hubCardTeslaCoilParty" },
    { href: "/legal/antique-fire-restore", title: "antiqueFireRestoreLink", body: "hubCardAntiqueFireRestore" },
    { href: "/legal/pulmopure", title: "pulmopureLink", body: "hubCardPulmopure" },
    { href: "/legal/installation-project", title: "installationProjectLink", body: "hubCardInstallationProject" },
    { href: "/legal/dna-pheromone-perfume", title: "dnaPheromonePerfumeLink", body: "hubCardDnaPheromonePerfume" },
    { href: "/legal/stardust", title: "stardustLink", body: "hubCardStardust" },
    { href: "/legal/refunds", title: "refundsLink", body: "hubCardRefunds" },
    { href: "/legal/welcome-grant", title: "welcomeGrantLink", body: "hubCardWelcomeGrant" },
    { href: "/legal/humanitarian", title: "humanitarianLink", body: "hubCardHumanitarian" },
    { href: "/legal/counsel", title: "counselLink", body: "hubCardCounsel" },
    { href: "/legal/starlink-install", title: "starlinkInstallLink", body: "hubCardStarlinkInstall" },
    { href: "/legal/field-services", title: "fieldServicesLink", body: "hubCardFieldServices" },
    { href: "/legal/space-ai-datacenter", title: "spaceAiDatacenterLink", body: "hubCardSpaceAiDatacenter" },
    { href: "/legal/cyber-defense", title: "cyberLink", body: "hubCardCyber" },
    { href: "/legal/clarity-act", title: "clarityLink", body: "hubCardClarity" },
    { href: "/compliance", title: "complianceLink", body: "hubCardCompliance" },
  ] as const;
  return (
    <LegalShell
      kickerClass="border-emerald-300/20 bg-emerald-400/[0.06]"
      kicker={t("legal.hubKicker")}
      title={t("legal.hubTitle")}
      intro={`${t("legal.lastUpdated")} ${t("legal.hubIntro")}`}
      actions={<LegalNavPills current="/legal" />}
    >
      <section className="mt-6 grid gap-4 md:grid-cols-2">
        {cards.map((card) => (
          <Link
            key={card.href}
            href={card.href}
            className="rounded-2xl border border-white/10 bg-white/[0.03] p-5 transition hover:border-white/25 hover:bg-white/[0.05]"
          >
            <h2 className="text-xl font-semibold tracking-[-0.02em]">{t(`legal.${card.title}`)}</h2>
            <p className="mt-3 text-sm leading-7 text-white/70">{t(`legal.${card.body}`)}</p>
          </Link>
        ))}
      </section>
      <section className="mt-6 rounded-2xl border border-white/10 bg-white/[0.03] p-5">
        <h2 className="text-xl font-semibold tracking-[-0.02em]">{t("legal.hubContactTitle")}</h2>
        <p className="mt-3 text-sm leading-7 text-white/70">{t("legal.hubContactBody")}</p>
        <div className="mt-4 flex flex-wrap gap-3 text-sm">
          <a className="text-sky-200 underline decoration-sky-400/40 underline-offset-4" href="mailto:legal@ancap.cloud">
            {t("legal.contactLegal")}
          </a>
          <a className="text-sky-200 underline decoration-sky-400/40 underline-offset-4" href="mailto:privacy@ancap.cloud">
            {t("legal.contactPrivacy")}
          </a>
          <a className="text-sky-200 underline decoration-sky-400/40 underline-offset-4" href="mailto:support@ancap.cloud">
            {t("legal.contactSupport")}
          </a>
        </div>
      </section>
      <p className="mt-6 text-sm leading-7 text-white/55">{t("legal.hubDisclaimer")}</p>
    </LegalShell>
  );
}

export function TermsView() {
  const { t } = useLanguage();
  const sections = Array.from({ length: 21 }, (_, i) => i + 1);
  return (
    <LegalShell
      kickerClass="border-white/10 bg-white/[0.03]"
      kicker={t("legal.termsKicker")}
      title={t("legal.termsTitle")}
      intro={`${t("legal.lastUpdated")} ${t("legal.termsIntro")}`}
      actions={<LegalNavPills current="/legal/terms" />}
    >
      <section className="mt-6 grid gap-4">
        {sections.map((n) => (
          <article key={n} className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
            <h2 className="text-xl font-semibold tracking-[-0.02em]">{t(`legal.t${n}Title`)}</h2>
            <p className="mt-3 text-sm leading-7 text-white/70">{t(`legal.t${n}Body`)}</p>
          </article>
        ))}
      </section>
    </LegalShell>
  );
}

export function PrivacyView() {
  const { t } = useLanguage();
  return (
    <LegalShell
      kickerClass="border-sky-300/15 bg-sky-400/[0.055]"
      kicker={t("legal.privacyKicker")}
      title={t("legal.privacyTitle")}
      intro={`${t("legal.lastUpdated")} ${t("legal.privacyIntro")}`}
      actions={<LegalNavPills current="/legal/privacy" />}
    >
      <section className="mt-6 grid gap-4 md:grid-cols-2">
        {[1, 2, 3, 4, 5, 6, 7, 8, 9].map((n) => (
          <article key={n} className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
            <h2 className="text-xl font-semibold tracking-[-0.02em]">{t(`legal.p${n}Title`)}</h2>
            <p className="mt-3 text-sm leading-7 text-white/70">{t(`legal.p${n}Body`)}</p>
          </article>
        ))}
      </section>
      <section className="mt-6 rounded-2xl border border-white/10 bg-white/[0.03] p-5">
        <h2 className="text-xl font-semibold tracking-[-0.02em]">{t("legal.privacySecurityTitle")}</h2>
        <p className="mt-3 text-sm leading-7 text-white/70">
          {t("legal.privacySecurityBody")}{" "}
          <Link href="/legal/cyber-defense" className="text-sky-200 underline decoration-sky-400/40 underline-offset-4 hover:text-sky-100">
            /legal/cyber-defense
          </Link>
          .
        </p>
      </section>
      <section className="mt-6 rounded-2xl border border-white/10 bg-white/[0.03] p-5">
        <h2 className="text-xl font-semibold tracking-[-0.02em]">{t("legal.privacyContactTitle")}</h2>
        <p className="mt-3 text-sm leading-7 text-white/70">{t("legal.privacyContactBody")}</p>
      </section>
    </LegalShell>
  );
}

export function CookiesLegalView() {
  const { t } = useLanguage();
  const cats = [1, 2, 3] as const;
  return (
    <LegalShell
      kickerClass="border-white/10 bg-white/[0.03]"
      kicker={t("legal.cookiesKicker")}
      title={t("legal.cookiesTitle")}
      intro={`${t("legal.lastUpdated")} ${t("legal.cookiesIntro")}`}
      actions={<LegalNavPills current="/legal/cookies" />}
    >
      <section className="mt-6 grid gap-4">
        {cats.map((n) => (
          <article key={n} className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
            <h2 className="text-xl font-semibold tracking-[-0.02em]">{t(`legal.c${n}Title`)}</h2>
            <p className="mt-3 text-sm leading-7 text-white/70">
              <span className="font-semibold text-white/84">{t("legal.cookiesExamples")} </span>
              {t(`legal.c${n}Examples`)}
            </p>
            <p className="mt-2 text-sm leading-7 text-white/70">
              <span className="font-semibold text-white/84">{t("legal.cookiesConsent")} </span>
              {t(`legal.c${n}Consent`)}
            </p>
          </article>
        ))}
      </section>
      <section className="mt-6 rounded-2xl border border-sky-300/15 bg-sky-400/[0.055] p-5">
        <h2 className="text-xl font-semibold tracking-[-0.02em]">{t("legal.cookiesRegTitle")}</h2>
        <p className="mt-3 text-sm leading-7 text-white/70">{t("legal.cookiesRegBody")}</p>
        <div className="mt-4 grid gap-3 text-sm md:grid-cols-2">
          <a className="rounded-2xl border border-white/10 bg-black/20 p-4 text-sky-100 transition hover:border-sky-300/35" href="https://commission.europa.eu/cookies-policy_en">
            {t("legal.cookiesEc")}
          </a>
          <a className="rounded-2xl border border-white/10 bg-black/20 p-4 text-sky-100 transition hover:border-sky-300/35" href="https://www.edpb.europa.eu/our-work-tools/our-documents/guidelines/guidelines-052020-consent-under-regulation-2016679_en">
            {t("legal.cookiesEdpb")}
          </a>
        </div>
      </section>
    </LegalShell>
  );
}

export function RiskDisclosureView() {
  const { t } = useLanguage();
  return (
    <LegalShell
      kickerClass="border-amber-300/20 bg-amber-400/[0.06]"
      kicker={t("legal.riskKicker")}
      title={t("legal.riskTitle")}
      intro={`${t("legal.lastUpdated")} ${t("legal.riskIntro")}`}
      actions={<LegalNavPills current="/legal/risk" />}
    >
      <section className="mt-6 grid gap-4">
        {[1, 2, 3, 4, 5, 6, 7, 8, 9].map((n) => (
          <article key={n} className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
            <h2 className="text-xl font-semibold tracking-[-0.02em]">{t(`legal.r${n}Title`)}</h2>
            <p className="mt-3 text-sm leading-7 text-white/70">{t(`legal.r${n}Body`)}</p>
          </article>
        ))}
        <p className="text-sm leading-7 text-white/55">
          {t("legal.riskMarketDataMore")}{" "}
          <Link href="/legal/market-data" className="text-sky-200 underline decoration-sky-400/40 underline-offset-4">
            /legal/market-data
          </Link>
          {" · "}
          <Link href="/legal/research-refs" className="text-sky-200 underline decoration-sky-400/40 underline-offset-4">
            /legal/research-refs
          </Link>
          {" · "}
          <Link href="/legal/welcome-grant" className="text-sky-200 underline decoration-sky-400/40 underline-offset-4">
            /legal/welcome-grant
          </Link>
          {" · "}
          <Link href="/legal/humanitarian" className="text-sky-200 underline decoration-sky-400/40 underline-offset-4">
            /legal/humanitarian
          </Link>
        </p>
      </section>
    </LegalShell>
  );
}

export function RefundsView() {
  const { t } = useLanguage();
  return (
    <LegalShell
      kickerClass="border-white/10 bg-white/[0.03]"
      kicker={t("legal.refundsKicker")}
      title={t("legal.refundsTitle")}
      intro={`${t("legal.lastUpdated")} ${t("legal.refundsIntro")}`}
      actions={<LegalNavPills current="/legal/refunds" />}
    >
      <section className="mt-6 grid gap-4">
        {[1, 2, 3, 4, 5].map((n) => (
          <article key={n} className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
            <h2 className="text-xl font-semibold tracking-[-0.02em]">{t(`legal.f${n}Title`)}</h2>
            <p className="mt-3 text-sm leading-7 text-white/70">{t(`legal.f${n}Body`)}</p>
          </article>
        ))}
        <p className="text-sm leading-7 text-white/55">
          {t("legal.refundsWelcomeGrantMore")}{" "}
          <Link href="/legal/welcome-grant" className="text-sky-200 underline decoration-sky-400/40 underline-offset-4">
            /legal/welcome-grant
          </Link>
        </p>
      </section>
    </LegalShell>
  );
}

export function CyberDefenseView() {
  const { t } = useLanguage();
  return (
    <LegalShell
      kickerClass="border-emerald-300/20 bg-emerald-400/[0.06]"
      kicker={t("legal.cyberKicker")}
      title={t("legal.cyberTitle")}
      intro={`${t("legal.lastUpdated")} ${t("legal.cyberIntro")}`}
      actions={
        <>
          <a
            href="https://openai.com/collective-cyberdefense"
            className="rounded-full border border-emerald-400/30 px-5 py-2.5 text-sm font-semibold text-emerald-100 transition hover:border-emerald-300/60 hover:text-white"
            target="_blank"
            rel="noopener noreferrer"
          >
            {t("legal.openLetter")}
          </a>
          <LegalNavPills current="/legal/cyber-defense" />
        </>
      }
    >
      <section className="mt-6 rounded-2xl border border-white/10 bg-white/[0.03] p-5 sm:p-6">
        <h2 className="text-xl font-semibold tracking-[-0.02em]">{t("legal.cyberStatementTitle")}</h2>
        <p className="mt-3 text-sm leading-7 text-white/70">{t("legal.cyberStatement1")}</p>
        <p className="mt-3 text-sm leading-7 text-white/70">{t("legal.cyberStatement2")}</p>
      </section>
      <section className="mt-6 grid gap-4">
        {[1, 2, 3].map((n) => (
          <article key={n} className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
            <h2 className="text-xl font-semibold tracking-[-0.02em]">{t(`legal.cyberP${n}Title`)}</h2>
            <p className="mt-3 text-sm leading-7 text-white/70">{t(`legal.cyberP${n}Body`)}</p>
          </article>
        ))}
      </section>
      <section className="mt-6 rounded-2xl border border-white/10 bg-white/[0.03] p-5 sm:p-6">
        <h2 className="text-xl font-semibold tracking-[-0.02em]">{t("legal.cyberCommitTitle")}</h2>
        <div className="mt-4 grid gap-4 md:grid-cols-2">
          {[1, 2, 3, 4, 5].map((n) => (
            <article key={n} className="rounded-2xl border border-white/10 bg-black/20 p-4">
              <h3 className="text-base font-semibold">{t(`legal.cyberC${n}Title`)}</h3>
              <p className="mt-2 text-sm leading-7 text-white/70">{t(`legal.cyberC${n}Body`)}</p>
            </article>
          ))}
        </div>
      </section>
      <section className="mt-6 rounded-2xl border border-sky-300/15 bg-sky-400/[0.055] p-5">
        <h2 className="text-xl font-semibold tracking-[-0.02em]">{t("legal.cyberScopeTitle")}</h2>
        <p className="mt-3 text-sm leading-7 text-white/70">{t("legal.cyberScope1")}</p>
        <p className="mt-3 text-sm leading-7 text-white/70">
          {t("legal.cyberScope2")}{" "}
          <a
            className="text-sky-200 underline decoration-sky-400/40 underline-offset-4 hover:text-sky-100"
            href="https://openai.com/collective-cyberdefense"
            target="_blank"
            rel="noopener noreferrer"
          >
            openai.com/collective-cyberdefense
          </a>
          .
        </p>
      </section>
    </LegalShell>
  );
}

export function ClarityActView() {
  const { t } = useLanguage();
  return (
    <LegalShell
      kickerClass="border-amber-300/20 bg-amber-400/[0.06]"
      kicker={t("legal.clarityKicker")}
      title={t("legal.clarityTitle")}
      intro={`${t("legal.lastUpdated")} ${t("legal.clarityIntro")}`}
      actions={
        <>
          <a
            href="https://www.congress.gov/bill/119th-congress/house-bill/3633"
            className="rounded-full border border-amber-400/30 px-5 py-2.5 text-sm font-semibold text-amber-100 transition hover:border-amber-300/60 hover:text-white"
            target="_blank"
            rel="noopener noreferrer"
          >
            {t("legal.clarityBillLink")}
          </a>
          <a
            href="https://x.com/BitcoinMagazine/status/2098137780610097201"
            className="rounded-full border border-white/20 px-5 py-2.5 text-sm font-semibold text-white/85 transition hover:border-white/40 hover:text-white"
            target="_blank"
            rel="noopener noreferrer"
          >
            {t("legal.clarityNewsLink")}
          </a>
          <LegalNavPills current="/legal/clarity-act" />
        </>
      }
    >
      <section className="mt-6 rounded-2xl border border-white/10 bg-white/[0.03] p-5 sm:p-6">
        <h2 className="text-xl font-semibold tracking-[-0.02em]">{t("legal.clarityStatementTitle")}</h2>
        <p className="mt-3 text-sm leading-7 text-white/70">{t("legal.clarityStatement1")}</p>
        <p className="mt-3 text-sm leading-7 text-white/70">{t("legal.clarityStatement2")}</p>
      </section>
      <section className="mt-6 grid gap-4">
        {[1, 2, 3].map((n) => (
          <article key={n} className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
            <h2 className="text-xl font-semibold tracking-[-0.02em]">{t(`legal.clarityP${n}Title`)}</h2>
            <p className="mt-3 text-sm leading-7 text-white/70">{t(`legal.clarityP${n}Body`)}</p>
          </article>
        ))}
      </section>
      <section className="mt-6 rounded-2xl border border-white/10 bg-white/[0.03] p-5 sm:p-6">
        <h2 className="text-xl font-semibold tracking-[-0.02em]">{t("legal.clarityCommitTitle")}</h2>
        <div className="mt-4 grid gap-4 md:grid-cols-2">
          {[1, 2, 3, 4, 5].map((n) => (
            <article key={n} className="rounded-2xl border border-white/10 bg-black/20 p-4">
              <h3 className="text-base font-semibold">{t(`legal.clarityC${n}Title`)}</h3>
              <p className="mt-2 text-sm leading-7 text-white/70">{t(`legal.clarityC${n}Body`)}</p>
            </article>
          ))}
        </div>
      </section>
      <section className="mt-6 rounded-2xl border border-sky-300/15 bg-sky-400/[0.055] p-5">
        <h2 className="text-xl font-semibold tracking-[-0.02em]">{t("legal.clarityScopeTitle")}</h2>
        <p className="mt-3 text-sm leading-7 text-white/70">{t("legal.clarityScope1")}</p>
        <p className="mt-3 text-sm leading-7 text-white/70">
          {t("legal.clarityScope2")}{" "}
          <a
            className="text-sky-200 underline decoration-sky-400/40 underline-offset-4 hover:text-sky-100"
            href="https://www.congress.gov/bill/119th-congress/house-bill/3633"
            target="_blank"
            rel="noopener noreferrer"
          >
            congress.gov — H.R. 3633
          </a>
          {" · "}
          <a
            className="text-sky-200 underline decoration-sky-400/40 underline-offset-4 hover:text-sky-100"
            href="https://x.com/BitcoinMagazine/status/2098137780610097201"
            target="_blank"
            rel="noopener noreferrer"
          >
            x.com/BitcoinMagazine
          </a>
          .
        </p>
      </section>
    </LegalShell>
  );
}

export function MarketDataDisclosureView() {
  const { t } = useLanguage();
  return (
    <LegalShell
      kickerClass="border-sky-300/20 bg-sky-400/[0.06]"
      kicker={t("legal.marketDataKicker")}
      title={t("legal.marketDataTitle")}
      intro={`${t("legal.lastUpdated")} ${t("legal.marketDataIntro")}`}
      actions={<LegalNavPills current="/legal/market-data" />}
    >
      <section className="mt-6 grid gap-4">
        {[1, 2, 3, 4, 5, 6, 7, 8].map((n) => (
          <article key={n} className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
            <h2 className="mt-0 text-xl font-semibold tracking-[-0.02em]">{t(`legal.md${n}Title`)}</h2>
            <p className="mt-3 text-sm leading-7 text-white/70">{t(`legal.md${n}Body`)}</p>
          </article>
        ))}
      </section>
      <section className="mt-6 rounded-2xl border border-white/10 bg-white/[0.03] p-5">
        <h2 className="text-xl font-semibold tracking-[-0.02em]">{t("legal.marketDataAttributionTitle")}</h2>
        <p className="mt-3 text-sm leading-7 text-white/70">{t("legal.marketDataAttributionBody")}</p>
        <div className="mt-3 flex flex-wrap gap-4 text-sm">
          <a
            className="text-sky-200 underline decoration-sky-400/40 underline-offset-4"
            href="https://www.coingecko.com"
            target="_blank"
            rel="noreferrer"
          >
            coingecko.com
          </a>
          <a
            className="text-sky-200 underline decoration-sky-400/40 underline-offset-4"
            href="https://www.accuweather.com/"
            target="_blank"
            rel="noreferrer"
          >
            accuweather.com
          </a>
        </div>
      </section>
    </LegalShell>
  );
}

const ZEISS_LIGHTFIELD_PRODUCT =
  "https://www.zeiss.com/microscopy/en/products/light-microscopes/confocal-microscopes/lightfield-4d.html";
const ZEISS_LIGHTFIELD_TECH_NOTE = "https://guide.microscopy.zeiss.com/content/hbrXqJoB8mu68yTAwSxe";
const ZEISS_LIGHTFIELD_FLYER =
  "https://asset-downloads.zeiss.com/catalogs/download/mic/1d2cd060-fbd3-4c97-b9b8-64673c416b7a/EN_product-flyer_LSM-Lightfield-4D.pdf";
const IXBT_QUANTUM_PARADOX =
  "https://www.ixbt.com/live/science/0-0-0-ii-pomog-dokazat-nevozmozhnyy-kvantovyy-paradoks-v-zaschite-dannyh.html";
const DAEWOONG_INC_RUSSIA =
  "https://incrussia.ru/news/v-ssha-odobrili-zayavku-na-patent-dlya-omolozheniya-kletok/";
const DAEWOONG_KOREA_HERALD = "https://www.koreaherald.com/article/10854319";
const DAEWOONG_KOREA_IT_TIMES = "https://www.koreaittimes.com/news/articleView.html?idxno=156490";
const CHALMERS_NAUKA_TV =
  "https://naukatv.ru/news/najden_sposob_uskoreniya_kvantovykh_vychislenij_v_1000_raz";
const CHALMERS_PRL = "https://doi.org/10.1103/tnb8-3m8m";
const CHALMERS_RECORD = "https://research.chalmers.se/en/publication/553484";
const CNEWS_ICT_GAZELLES =
  "https://www.cnews.ru/news/top/2026-08-13_samaya_bystrorastushchaya_it-kompaniya";
const FORBES_FRII_IT =
  "https://www.forbes.ru/svoi-biznes/548659-soft-dla-upravlenia-korovami-i-ii-repetitory-8-samyh-bystrorastusih-it-kompanij";
const SKYPRO_IT_BUSINESSES =
  "https://sky.pro/wiki/profession/15-perspektivnykh-it-biznesov-ot-iskusstvennogo-intellekta-do-fin-tech/";
const BUSINESSMENS_TECH = "https://businessmens.ru/article/biznes-v-sfere-tehnologiy";

export function ResearchRefsDisclosureView() {
  const { t } = useLanguage();
  return (
    <LegalShell
      kickerClass="border-teal-300/20 bg-teal-400/[0.06]"
      kicker={t("legal.researchRefsKicker")}
      title={t("legal.researchRefsTitle")}
      intro={`${t("legal.lastUpdated")} ${t("legal.researchRefsIntro")}`}
      actions={<LegalNavPills current="/legal/research-refs" />}
    >
      <section className="mt-6 grid gap-4">
        {[1, 2, 3, 4, 5, 6, 7, 8, 9].map((n) => (
          <article key={n} className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
            <h2 className="text-xl font-semibold tracking-[-0.02em]">{t(`legal.rr${n}Title`)}</h2>
            <p className="mt-3 text-sm leading-7 text-white/70">{t(`legal.rr${n}Body`)}</p>
          </article>
        ))}
      </section>
      <section className="mt-6 rounded-2xl border border-white/10 bg-white/[0.03] p-5">
        <h2 className="text-xl font-semibold tracking-[-0.02em]">{t("legal.researchRefsLinksTitle")}</h2>
        <p className="mt-3 text-sm leading-7 text-white/70">{t("legal.researchRefsLinksBody")}</p>
        <div className="mt-4 flex flex-col gap-3 text-sm">
          <a
            className="text-sky-200 underline decoration-sky-400/40 underline-offset-4"
            href={ZEISS_LIGHTFIELD_PRODUCT}
            target="_blank"
            rel="noopener noreferrer"
          >
            ZEISS LSM Lightfield 4D — product page
          </a>
          <a
            className="text-sky-200 underline decoration-sky-400/40 underline-offset-4"
            href={ZEISS_LIGHTFIELD_TECH_NOTE}
            target="_blank"
            rel="noopener noreferrer"
          >
            Technology note — Instant volume acquisition for high-speed and gentle imaging
          </a>
          <a
            className="text-sky-200 underline decoration-sky-400/40 underline-offset-4"
            href={ZEISS_LIGHTFIELD_FLYER}
            target="_blank"
            rel="noopener noreferrer"
          >
            Product flyer (PDF)
          </a>
          <a
            className="text-sky-200 underline decoration-sky-400/40 underline-offset-4"
            href={IXBT_QUANTUM_PARADOX}
            target="_blank"
            rel="noopener noreferrer"
          >
            iXBT Live — 0 + 0 &gt; 0 quantum paradox in data protection
          </a>
          <a
            className="text-sky-200 underline decoration-sky-400/40 underline-offset-4"
            href={DAEWOONG_INC_RUSSIA}
            target="_blank"
            rel="noopener noreferrer"
          >
            Inc. Russia — USPTO allowance for cell-rejuvenation mRNA lipids (8 Sep 2026)
          </a>
          <a
            className="text-sky-200 underline decoration-sky-400/40 underline-offset-4"
            href={DAEWOONG_KOREA_HERALD}
            target="_blank"
            rel="noopener noreferrer"
          >
            Korea Herald — Daewoong eTurna USPTO notice of allowance
          </a>
          <a
            className="text-sky-200 underline decoration-sky-400/40 underline-offset-4"
            href={DAEWOONG_KOREA_IT_TIMES}
            target="_blank"
            rel="noopener noreferrer"
          >
            Korea IT Times — ERA / eTurna ionizable-lipid decision
          </a>
          <Link
            href="/aeterna"
            className="text-sky-200 underline decoration-sky-400/40 underline-offset-4"
          >
            AETERNA — partial reprogramming consult
          </Link>
          <a
            className="text-sky-200 underline decoration-sky-400/40 underline-offset-4"
            href={CHALMERS_NAUKA_TV}
            target="_blank"
            rel="noopener noreferrer"
          >
            Nauka TV — ~1000× fewer Floquet periods for bosonic-code operations (10 Sep 2026)
          </a>
          <a
            className="text-sky-200 underline decoration-sky-400/40 underline-offset-4"
            href={CHALMERS_PRL}
            target="_blank"
            rel="noopener noreferrer"
          >
            PRL — Single-Period Floquet Control of Bosonic Codes (DOI 10.1103/tnb8-3m8m)
          </a>
          <a
            className="text-sky-200 underline decoration-sky-400/40 underline-offset-4"
            href={CHALMERS_RECORD}
            target="_blank"
            rel="noopener noreferrer"
          >
            Chalmers research record — Huang, Du, Guo
          </a>
          <Link
            href="/tech"
            className="text-sky-200 underline decoration-sky-400/40 underline-offset-4"
          >
            TECH stack — Floquet bosonic codes
          </Link>
          <Link
            href="/quantum-sim"
            className="text-sky-200 underline decoration-sky-400/40 underline-offset-4"
          >
            Quantum SIM — compute literacy
          </Link>
          <a
            className="text-sky-200 underline decoration-sky-400/40 underline-offset-4"
            href={CNEWS_ICT_GAZELLES}
            target="_blank"
            rel="noopener noreferrer"
          >
            CNews — Spark-Interfax ICT gazelles; GA Tactic / Golden Apple (13 Aug 2026)
          </a>
          <a
            className="text-sky-200 underline decoration-sky-400/40 underline-offset-4"
            href={FORBES_FRII_IT}
            target="_blank"
            rel="noopener noreferrer"
          >
            Forbes / FRIИ — fastest-growing small IT (farm software, AI tutors)
          </a>
          <a
            className="text-sky-200 underline decoration-sky-400/40 underline-offset-4"
            href={SKYPRO_IT_BUSINESSES}
            target="_blank"
            rel="noopener noreferrer"
          >
            Sky.pro — 15 prospective IT businesses (AI, SECaaS, FinTech idea ranges)
          </a>
          <a
            className="text-sky-200 underline decoration-sky-400/40 underline-offset-4"
            href={BUSINESSMENS_TECH}
            target="_blank"
            rel="noopener noreferrer"
          >
            businessmens.ru — 2026 technology-business niches (agrotech, production IT)
          </a>
          <Link
            href="/startups"
            className="text-sky-200 underline decoration-sky-400/40 underline-offset-4"
          >
            Startup investment desk
          </Link>
        </div>
      </section>
    </LegalShell>
  );
}

export function CryoConstitutionView() {
  const { t } = useLanguage();
  return (
    <LegalShell
      kickerClass="border-sky-300/20 bg-sky-400/[0.06]"
      kicker={t("legal.cryoKicker")}
      title={t("legal.cryoTitle")}
      intro={`${t("legal.lastUpdated")} ${t("legal.cryoIntro")}`}
      actions={<LegalNavPills current="/legal/cryo-constitution" />}
    >
      <section className="mt-6 grid gap-4">
        {[1, 2, 3, 4, 5, 6, 7, 8].map((n) => (
          <article key={n} className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
            <h2 className="text-xl font-semibold tracking-[-0.02em]">{t(`legal.cryo${n}Title`)}</h2>
            <p className="mt-3 text-sm leading-7 text-white/70">{t(`legal.cryo${n}Body`)}</p>
          </article>
        ))}
      </section>
      <section className="mt-6 rounded-2xl border border-white/10 bg-white/[0.03] p-5 text-sm leading-7 text-white/70">
        <p>
          Desk:{" "}
          <Link href="/cryo" className="text-sky-200 underline decoration-sky-400/40 underline-offset-4">
            /cryo
          </Link>
          {" · "}
          Partners:{" "}
          <a
            href="https://kriorus.ru/"
            target="_blank"
            rel="noopener noreferrer"
            className="text-sky-200 underline decoration-sky-400/40 underline-offset-4"
          >
            KrioRus
          </a>
          {", "}
          <a
            href="https://www.tomorrow.bio/"
            target="_blank"
            rel="noopener noreferrer"
            className="text-sky-200 underline decoration-sky-400/40 underline-offset-4"
          >
            Tomorrow.bio
          </a>
          {" · "}
          <Link href="/legal/vet-regen" className="text-sky-200 underline decoration-sky-400/40 underline-offset-4">
            /legal/vet-regen
          </Link>
        </p>
      </section>
    </LegalShell>
  );
}

export function HumanitarianLegalView() {
  const { t } = useLanguage();
  return (
    <LegalShell
      kickerClass="border-rose-300/20 bg-rose-400/[0.06]"
      kicker={t("legal.humanitarianKicker")}
      title={t("legal.humanitarianTitle")}
      intro={`${t("legal.lastUpdated")} ${t("legal.humanitarianIntro")}`}
      actions={<LegalNavPills current="/legal/humanitarian" />}
    >
      <section className="mt-6 grid gap-4">
        {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((n) => (
          <article key={n} className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
            <h2 className="text-xl font-semibold tracking-[-0.02em]">{t(`legal.hum${n}Title`)}</h2>
            <p className="mt-3 text-sm leading-7 text-white/70">{t(`legal.hum${n}Body`)}</p>
          </article>
        ))}
      </section>
      <section className="mt-6 rounded-2xl border border-white/10 bg-white/[0.03] p-5 text-sm leading-7 text-white/70">
        <p>
          Desk:{" "}
          <Link href="/humanitarian" className="text-sky-200 underline decoration-sky-400/40 underline-offset-4">
            /humanitarian
          </Link>
          {" · "}
          {t("legal.humanitarianAlso")}{" "}
          <Link href="/legal/welcome-grant" className="text-sky-200 underline decoration-sky-400/40 underline-offset-4">
            /legal/welcome-grant
          </Link>
          {" · "}
          <a
            href="https://www.ifrc.org/"
            target="_blank"
            rel="noopener noreferrer"
            className="text-sky-200 underline decoration-sky-400/40 underline-offset-4"
          >
            ifrc.org
          </a>
        </p>
      </section>
    </LegalShell>
  );
}

export function CounselLegalView() {
  const { t } = useLanguage();
  return (
    <LegalShell
      kickerClass="border-blue-300/20 bg-blue-400/[0.06]"
      kicker={t("legal.counselKicker")}
      title={t("legal.counselTitle")}
      intro={`${t("legal.lastUpdated")} ${t("legal.counselIntro")}`}
      actions={<LegalNavPills current="/legal/counsel" />}
    >
      <section className="mt-6 grid gap-4">
        {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((n) => (
          <article key={n} className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
            <h2 className="text-xl font-semibold tracking-[-0.02em]">{t(`legal.cn${n}Title`)}</h2>
            <p className="mt-3 text-sm leading-7 text-white/70">{t(`legal.cn${n}Body`)}</p>
          </article>
        ))}
      </section>
      <section className="mt-6 rounded-2xl border border-white/10 bg-white/[0.03] p-5 text-sm leading-7 text-white/70">
        <p>
          Product:{" "}
          <Link href="/counsel" className="text-sky-200 underline decoration-sky-400/40 underline-offset-4">
            /counsel
          </Link>
        </p>
      </section>
    </LegalShell>
  );
}

export function StarlinkInstallLegalView() {
  const { t } = useLanguage();
  return (
    <LegalShell
      kickerClass="border-sky-300/20 bg-sky-400/[0.06]"
      kicker={t("legal.starlinkInstallKicker")}
      title={t("legal.starlinkInstallTitle")}
      intro={`${t("legal.lastUpdated")} ${t("legal.starlinkInstallIntro")}`}
      actions={<LegalNavPills current="/legal/starlink-install" />}
    >
      <section className="mt-6 grid gap-4">
        {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((n) => (
          <article key={n} className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
            <h2 className="text-xl font-semibold tracking-[-0.02em]">{t(`legal.si${n}Title`)}</h2>
            <p className="mt-3 text-sm leading-7 text-white/70">{t(`legal.si${n}Body`)}</p>
          </article>
        ))}
      </section>
      <section className="mt-6 rounded-2xl border border-white/10 bg-white/[0.03] p-5 text-sm leading-7 text-white/70">
        <p>
          Product:{" "}
          <Link href="/field-services?group=starlink" className="text-sky-200 underline decoration-sky-400/40 underline-offset-4">
            /field-services?group=starlink
          </Link>
          {" · "}
          <Link href="/legal/field-services" className="text-sky-200 underline decoration-sky-400/40 underline-offset-4">
            /legal/field-services
          </Link>
        </p>
      </section>
    </LegalShell>
  );
}

export function FieldServicesLegalView() {
  const { t } = useLanguage();
  return (
    <LegalShell
      kickerClass="border-sky-300/20 bg-sky-400/[0.06]"
      kicker={t("legal.fieldServicesKicker")}
      title={t("legal.fieldServicesTitle")}
      intro={`${t("legal.lastUpdated")} ${t("legal.fieldServicesIntro")}`}
      actions={<LegalNavPills current="/legal/field-services" />}
    >
      <section className="mt-6 grid gap-4">
        {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((n) => (
          <article key={n} className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
            <h2 className="text-xl font-semibold tracking-[-0.02em]">{t(`legal.fs${n}Title`)}</h2>
            <p className="mt-3 text-sm leading-7 text-white/70">{t(`legal.fs${n}Body`)}</p>
          </article>
        ))}
      </section>
      <section className="mt-6 rounded-2xl border border-white/10 bg-white/[0.03] p-5 text-sm leading-7 text-white/70">
        <p>
          Product:{" "}
          <Link href="/field-services" className="text-sky-200 underline decoration-sky-400/40 underline-offset-4">
            /field-services
          </Link>
          {" · "}
          <Link href="/legal/starlink-install" className="text-sky-200 underline decoration-sky-400/40 underline-offset-4">
            /legal/starlink-install
          </Link>
          {" · "}
          <Link href="/legal/space-ai-datacenter" className="text-sky-200 underline decoration-sky-400/40 underline-offset-4">
            /legal/space-ai-datacenter
          </Link>
        </p>
      </section>
    </LegalShell>
  );
}

export function SpaceAiDatacenterLegalView() {
  const { t } = useLanguage();
  return (
    <LegalShell
      kickerClass="border-indigo-300/20 bg-indigo-400/[0.06]"
      kicker={t("legal.spaceAiDatacenterKicker")}
      title={t("legal.spaceAiDatacenterTitle")}
      intro={`${t("legal.lastUpdated")} ${t("legal.spaceAiDatacenterIntro")}`}
      actions={<LegalNavPills current="/legal/space-ai-datacenter" />}
    >
      <section className="mt-6 grid gap-4">
        {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((n) => (
          <article key={n} className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
            <h2 className="text-xl font-semibold tracking-[-0.02em]">{t(`legal.sa${n}Title`)}</h2>
            <p className="mt-3 text-sm leading-7 text-white/70">{t(`legal.sa${n}Body`)}</p>
          </article>
        ))}
      </section>
      <section className="mt-6 rounded-2xl border border-white/10 bg-white/[0.03] p-5 text-sm leading-7 text-white/70">
        <p>
          Product:{" "}
          <Link
            href="/field-services?group=space"
            className="text-sky-200 underline decoration-sky-400/40 underline-offset-4"
          >
            /field-services?group=space
          </Link>
          {" · "}
          <Link href="/legal/field-services" className="text-sky-200 underline decoration-sky-400/40 underline-offset-4">
            /legal/field-services
          </Link>
        </p>
      </section>
    </LegalShell>
  );
}

export function VetRegenLegalView() {
  const { t } = useLanguage();
  return (
    <LegalShell
      kickerClass="border-sky-300/20 bg-sky-400/[0.06]"
      kicker={t("legal.vetRegenKicker")}
      title={t("legal.vetRegenTitle")}
      intro={`${t("legal.lastUpdated")} ${t("legal.vetRegenIntro")}`}
      actions={<LegalNavPills current="/legal/vet-regen" />}
    >
      <section className="mt-6 grid gap-4">
        {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((n) => (
          <article key={n} className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
            <h2 className="text-xl font-semibold tracking-[-0.02em]">{t(`legal.vr${n}Title`)}</h2>
            <p className="mt-3 text-sm leading-7 text-white/70">{t(`legal.vr${n}Body`)}</p>
          </article>
        ))}
      </section>
      <section className="mt-6 rounded-2xl border border-white/10 bg-white/[0.03] p-5 text-sm leading-7 text-white/70">
        <p>
          Product:{" "}
          <Link href="/aeterna#vet-regen" className="text-sky-200 underline decoration-sky-400/40 underline-offset-4">
            /aeterna#vet-regen
          </Link>
          {" · "}
          <Link href="/cryo" className="text-sky-200 underline decoration-sky-400/40 underline-offset-4">
            /cryo
          </Link>
        </p>
      </section>
    </LegalShell>
  );
}

export function LightChamberLegalView() {
  const { t } = useLanguage();
  return (
    <LegalShell
      kickerClass="border-amber-300/20 bg-amber-400/[0.06]"
      kicker={t("legal.lightChamberKicker")}
      title={t("legal.lightChamberTitle")}
      intro={`${t("legal.lastUpdated")} ${t("legal.lightChamberIntro")}`}
      actions={<LegalNavPills current="/legal/light-chamber" />}
    >
      <section className="mt-6 grid gap-4">
        {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((n) => (
          <article key={n} className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
            <h2 className="text-xl font-semibold tracking-[-0.02em]">{t(`legal.lc${n}Title`)}</h2>
            <p className="mt-3 text-sm leading-7 text-white/70">{t(`legal.lc${n}Body`)}</p>
          </article>
        ))}
      </section>
      <section className="mt-6 rounded-2xl border border-white/10 bg-white/[0.03] p-5 text-sm leading-7 text-white/70">
        <p>
          Product:{" "}
          <Link href="/aeterna#vinci-light" className="text-sky-200 underline decoration-sky-400/40 underline-offset-4">
            /aeterna#vinci-light
          </Link>
        </p>
      </section>
    </LegalShell>
  );
}

export function BodyContouringLegalView() {
  const { t } = useLanguage();
  return (
    <LegalShell
      kickerClass="border-amber-300/20 bg-amber-400/[0.06]"
      kicker={t("legal.bodyContouringKicker")}
      title={t("legal.bodyContouringTitle")}
      intro={`${t("legal.lastUpdated")} ${t("legal.bodyContouringIntro")}`}
      actions={<LegalNavPills current="/legal/body-contouring" />}
    >
      <section className="mt-6 grid gap-4">
        {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((n) => (
          <article key={n} className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
            <h2 className="text-xl font-semibold tracking-[-0.02em]">{t(`legal.bc${n}Title`)}</h2>
            <p className="mt-3 text-sm leading-7 text-white/70">{t(`legal.bc${n}Body`)}</p>
          </article>
        ))}
      </section>
      <section className="mt-6 rounded-2xl border border-white/10 bg-white/[0.03] p-5 text-sm leading-7 text-white/70">
        <p>
          Product:{" "}
          <Link href="/aeterna#microwave-body" className="text-sky-200 underline decoration-sky-400/40 underline-offset-4">
            /aeterna#microwave-body
          </Link>
        </p>
      </section>
    </LegalShell>
  );
}

export function BiofusionLegalView() {
  const { t } = useLanguage();
  return (
    <LegalShell
      kickerClass="border-sky-300/20 bg-sky-400/[0.06]"
      kicker={t("legal.biofusionKicker")}
      title={t("legal.biofusionTitle")}
      intro={`${t("legal.lastUpdated")} ${t("legal.biofusionIntro")}`}
      actions={<LegalNavPills current="/legal/biofusion" />}
    >
      <section className="mt-6 grid gap-4">
        {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((n) => (
          <article key={n} className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
            <h2 className="text-xl font-semibold tracking-[-0.02em]">{t(`legal.bf${n}Title`)}</h2>
            <p className="mt-3 text-sm leading-7 text-white/70">{t(`legal.bf${n}Body`)}</p>
          </article>
        ))}
      </section>
      <section className="mt-6 rounded-2xl border border-white/10 bg-white/[0.03] p-5 text-sm leading-7 text-white/70">
        <p>
          Product:{" "}
          <Link href="/aeterna#biofusion" className="text-sky-200 underline decoration-sky-400/40 underline-offset-4">
            /aeterna#biofusion
          </Link>
        </p>
      </section>
    </LegalShell>
  );
}

export function DpscLegalView() {
  const { t } = useLanguage();
  return (
    <LegalShell
      kickerClass="border-sky-300/20 bg-sky-400/[0.06]"
      kicker={t("legal.dpscKicker")}
      title={t("legal.dpscTitle")}
      intro={`${t("legal.lastUpdated")} ${t("legal.dpscIntro")}`}
      actions={<LegalNavPills current="/legal/dpsc" />}
    >
      <section className="mt-6 grid gap-4">
        {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((n) => (
          <article key={n} className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
            <h2 className="text-xl font-semibold tracking-[-0.02em]">{t(`legal.dp${n}Title`)}</h2>
            <p className="mt-3 text-sm leading-7 text-white/70">{t(`legal.dp${n}Body`)}</p>
          </article>
        ))}
      </section>
      <section className="mt-6 rounded-2xl border border-white/10 bg-white/[0.03] p-5 text-sm leading-7 text-white/70">
        <p>
          Product:{" "}
          <Link href="/aeterna#dpsc-biomaterial" className="text-sky-200 underline decoration-sky-400/40 underline-offset-4">
            /aeterna#dpsc-biomaterial
          </Link>
          {" · "}
          <Link href="/aeterna#organ-print" className="text-sky-200 underline decoration-sky-400/40 underline-offset-4">
            /aeterna#organ-print
          </Link>
        </p>
      </section>
    </LegalShell>
  );
}

export function VascularCarePlusLegalView() {
  const { t } = useLanguage();
  return (
    <LegalShell
      kickerClass="border-sky-300/20 bg-sky-400/[0.06]"
      kicker={t("legal.vascularPlusKicker")}
      title={t("legal.vascularPlusTitle")}
      intro={`${t("legal.lastUpdated")} ${t("legal.vascularPlusIntro")}`}
      actions={<LegalNavPills current="/legal/vascular-care-plus" />}
    >
      <section className="mt-6 grid gap-4">
        {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((n) => (
          <article key={n} className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
            <h2 className="text-xl font-semibold tracking-[-0.02em]">{t(`legal.vp${n}Title`)}</h2>
            <p className="mt-3 text-sm leading-7 text-white/70">{t(`legal.vp${n}Body`)}</p>
          </article>
        ))}
      </section>
      <section className="mt-6 rounded-2xl border border-white/10 bg-white/[0.03] p-5 text-sm leading-7 text-white/70">
        <p>
          Product:{" "}
          <Link href="/aeterna#vascular-care-plus" className="text-sky-200 underline decoration-sky-400/40 underline-offset-4">
            /aeterna#vascular-care-plus
          </Link>
        </p>
      </section>
    </LegalShell>
  );
}

export function VascularCareLegalView() {
  const { t } = useLanguage();
  return (
    <LegalShell
      kickerClass="border-sky-300/20 bg-sky-400/[0.06]"
      kicker={t("legal.vascularKicker")}
      title={t("legal.vascularTitle")}
      intro={`${t("legal.lastUpdated")} ${t("legal.vascularIntro")}`}
      actions={<LegalNavPills current="/legal/vascular-care" />}
    >
      <section className="mt-6 grid gap-4">
        {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((n) => (
          <article key={n} className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
            <h2 className="text-xl font-semibold tracking-[-0.02em]">{t(`legal.vu${n}Title`)}</h2>
            <p className="mt-3 text-sm leading-7 text-white/70">{t(`legal.vu${n}Body`)}</p>
          </article>
        ))}
      </section>
      <section className="mt-6 rounded-2xl border border-white/10 bg-white/[0.03] p-5 text-sm leading-7 text-white/70">
        <p>
          Product:{" "}
          <Link href="/aeterna#vascular-care" className="text-sky-200 underline decoration-sky-400/40 underline-offset-4">
            /aeterna#vascular-care
          </Link>
        </p>
      </section>
    </LegalShell>
  );
}

export function TransdermalLegalView() {
  const { t } = useLanguage();
  return (
    <LegalShell
      kickerClass="border-sky-300/20 bg-sky-400/[0.06]"
      kicker={t("legal.transdermalKicker")}
      title={t("legal.transdermalTitle")}
      intro={`${t("legal.lastUpdated")} ${t("legal.transdermalIntro")}`}
      actions={<LegalNavPills current="/legal/transdermal" />}
    >
      <section className="mt-6 grid gap-4">
        {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((n) => (
          <article key={n} className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
            <h2 className="text-xl font-semibold tracking-[-0.02em]">{t(`legal.td${n}Title`)}</h2>
            <p className="mt-3 text-sm leading-7 text-white/70">{t(`legal.td${n}Body`)}</p>
          </article>
        ))}
      </section>
      <section className="mt-6 rounded-2xl border border-white/10 bg-white/[0.03] p-5 text-sm leading-7 text-white/70">
        <p>
          Product:{" "}
          <Link href="/aeterna#transdermal" className="text-sky-200 underline decoration-sky-400/40 underline-offset-4">
            /aeterna#transdermal
          </Link>
        </p>
      </section>
    </LegalShell>
  );
}

export function MReceptorLegalView() {
  const { t } = useLanguage();
  return (
    <LegalShell
      kickerClass="border-sky-300/20 bg-sky-400/[0.06]"
      kicker={t("legal.mReceptorKicker")}
      title={t("legal.mReceptorTitle")}
      intro={`${t("legal.lastUpdated")} ${t("legal.mReceptorIntro")}`}
      actions={<LegalNavPills current="/legal/m-receptor" />}
    >
      <section className="mt-6 grid gap-4">
        {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((n) => (
          <article key={n} className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
            <h2 className="text-xl font-semibold tracking-[-0.02em]">{t(`legal.mr${n}Title`)}</h2>
            <p className="mt-3 text-sm leading-7 text-white/70">{t(`legal.mr${n}Body`)}</p>
          </article>
        ))}
      </section>
      <section className="mt-6 rounded-2xl border border-white/10 bg-white/[0.03] p-5 text-sm leading-7 text-white/70">
        <p>
          Product:{" "}
          <Link href="/aeterna#m-receptor" className="text-sky-200 underline decoration-sky-400/40 underline-offset-4">
            /aeterna#m-receptor
          </Link>
        </p>
      </section>
    </LegalShell>
  );
}

export function OxygenCarrierLegalView() {
  const { t } = useLanguage();
  return (
    <LegalShell
      kickerClass="border-sky-300/20 bg-sky-400/[0.06]"
      kicker={t("legal.oxygenCarrierKicker")}
      title={t("legal.oxygenCarrierTitle")}
      intro={`${t("legal.lastUpdated")} ${t("legal.oxygenCarrierIntro")}`}
      actions={<LegalNavPills current="/legal/oxygen-carrier" />}
    >
      <section className="mt-6 grid gap-4">
        {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((n) => (
          <article key={n} className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
            <h2 className="text-xl font-semibold tracking-[-0.02em]">{t(`legal.ox${n}Title`)}</h2>
            <p className="mt-3 text-sm leading-7 text-white/70">{t(`legal.ox${n}Body`)}</p>
          </article>
        ))}
      </section>
      <section className="mt-6 rounded-2xl border border-white/10 bg-white/[0.03] p-5 text-sm leading-7 text-white/70">
        <p>
          Product:{" "}
          <Link href="/aeterna#oxygen-carrier" className="text-sky-200 underline decoration-sky-400/40 underline-offset-4">
            /aeterna#oxygen-carrier
          </Link>
        </p>
      </section>
    </LegalShell>
  );
}

export function SyntheticBloodMambaLegalView() {
  const { t } = useLanguage();
  return (
    <LegalShell
      kickerClass="border-violet-300/20 bg-violet-400/[0.06]"
      kicker={t("legal.syntheticBloodMambaKicker")}
      title={t("legal.syntheticBloodMambaTitle")}
      intro={`${t("legal.lastUpdated")} ${t("legal.syntheticBloodMambaIntro")}`}
      actions={<LegalNavPills current="/legal/synthetic-blood-mamba" />}
    >
      <section className="mt-6 grid gap-4">
        {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((n) => (
          <article key={n} className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
            <h2 className="text-xl font-semibold tracking-[-0.02em]">{t(`legal.sbm${n}Title`)}</h2>
            <p className="mt-3 text-sm leading-7 text-white/70">{t(`legal.sbm${n}Body`)}</p>
          </article>
        ))}
      </section>
      <section className="mt-6 rounded-2xl border border-white/10 bg-white/[0.03] p-5 text-sm leading-7 text-white/70">
        <p>
          Product:{" "}
          <Link
            href="/aeterna#synthetic-blood-mamba"
            className="text-sky-200 underline decoration-sky-400/40 underline-offset-4"
          >
            /aeterna#synthetic-blood-mamba
          </Link>
        </p>
      </section>
    </LegalShell>
  );
}

export function AdhdSupportLegalView() {
  const { t } = useLanguage();
  return (
    <LegalShell
      kickerClass="border-amber-300/20 bg-amber-400/[0.06]"
      kicker={t("legal.adhdSupportKicker")}
      title={t("legal.adhdSupportTitle")}
      intro={`${t("legal.lastUpdated")} ${t("legal.adhdSupportIntro")}`}
      actions={<LegalNavPills current="/legal/adhd-support" />}
    >
      <section className="mt-6 grid gap-4">
        {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((n) => (
          <article key={n} className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
            <h2 className="text-xl font-semibold tracking-[-0.02em]">{t(`legal.adhd${n}Title`)}</h2>
            <p className="mt-3 text-sm leading-7 text-white/70">{t(`legal.adhd${n}Body`)}</p>
          </article>
        ))}
      </section>
      <section className="mt-6 rounded-2xl border border-white/10 bg-white/[0.03] p-5 text-sm leading-7 text-white/70">
        <p>
          Product:{" "}
          <Link href="/aeterna#adhd-support" className="text-sky-200 underline decoration-sky-400/40 underline-offset-4">
            /aeterna#adhd-support
          </Link>
        </p>
      </section>
    </LegalShell>
  );
}

export function AureaVitaLegalView() {
  const { t } = useLanguage();
  return (
    <LegalShell
      kickerClass="border-amber-300/25 bg-amber-400/[0.07]"
      kicker={t("legal.aureaVitaKicker")}
      title={t("legal.aureaVitaTitle")}
      intro={`${t("legal.lastUpdated")} ${t("legal.aureaVitaIntro")}`}
      actions={<LegalNavPills current="/legal/aurea-vita" />}
    >
      <section className="mt-6 grid gap-4">
        {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((n) => (
          <article key={n} className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
            <h2 className="text-xl font-semibold tracking-[-0.02em]">{t(`legal.av${n}Title`)}</h2>
            <p className="mt-3 text-sm leading-7 text-white/70">{t(`legal.av${n}Body`)}</p>
          </article>
        ))}
      </section>
      <section className="mt-6 rounded-2xl border border-white/10 bg-white/[0.03] p-5 text-sm leading-7 text-white/70">
        <p>
          Product:{" "}
          <Link href="/aeterna#aurea-vita" className="text-amber-200 underline decoration-amber-400/40 underline-offset-4">
            /aeterna#aurea-vita
          </Link>
        </p>
      </section>
    </LegalShell>
  );
}

export function DownSyndromeSupportLegalView() {
  const { t } = useLanguage();
  return (
    <LegalShell
      kickerClass="border-sky-300/20 bg-sky-400/[0.06]"
      kicker={t("legal.downSyndromeSupportKicker")}
      title={t("legal.downSyndromeSupportTitle")}
      intro={`${t("legal.lastUpdated")} ${t("legal.downSyndromeSupportIntro")}`}
      actions={<LegalNavPills current="/legal/down-syndrome-support" />}
    >
      <section className="mt-6 grid gap-4">
        {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((n) => (
          <article key={n} className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
            <h2 className="text-xl font-semibold tracking-[-0.02em]">{t(`legal.ds${n}Title`)}</h2>
            <p className="mt-3 text-sm leading-7 text-white/70">{t(`legal.ds${n}Body`)}</p>
          </article>
        ))}
      </section>
      <section className="mt-6 rounded-2xl border border-white/10 bg-white/[0.03] p-5 text-sm leading-7 text-white/70">
        <p>
          Product:{" "}
          <Link
            href="/aeterna#down-syndrome-support"
            className="text-sky-200 underline decoration-sky-400/40 underline-offset-4"
          >
            /aeterna#down-syndrome-support
          </Link>
        </p>
      </section>
    </LegalShell>
  );
}

export function SubstanceCodingLegalView() {
  const { t } = useLanguage();
  return (
    <LegalShell
      kickerClass="border-amber-300/20 bg-amber-400/[0.06]"
      kicker={t("legal.substanceCodingKicker")}
      title={t("legal.substanceCodingTitle")}
      intro={`${t("legal.lastUpdated")} ${t("legal.substanceCodingIntro")}`}
      actions={<LegalNavPills current="/legal/substance-coding" />}
    >
      <section className="mt-6 grid gap-4">
        {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((n) => (
          <article key={n} className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
            <h2 className="text-xl font-semibold tracking-[-0.02em]">{t(`legal.sc${n}Title`)}</h2>
            <p className="mt-3 text-sm leading-7 text-white/70">{t(`legal.sc${n}Body`)}</p>
          </article>
        ))}
      </section>
      <section className="mt-6 rounded-2xl border border-white/10 bg-white/[0.03] p-5 text-sm leading-7 text-white/70">
        <p>
          Product:{" "}
          <Link
            href="/aeterna#substance-coding"
            className="text-amber-200 underline decoration-amber-400/40 underline-offset-4"
          >
            /aeterna#substance-coding
          </Link>
        </p>
      </section>
    </LegalShell>
  );
}

export function TeslaCoilPartyLegalView() {
  const { t } = useLanguage();
  return (
    <LegalShell
      kickerClass="border-violet-300/20 bg-violet-400/[0.06]"
      kicker={t("legal.teslaCoilPartyKicker")}
      title={t("legal.teslaCoilPartyTitle")}
      intro={`${t("legal.lastUpdated")} ${t("legal.teslaCoilPartyIntro")}`}
      actions={<LegalNavPills current="/legal/tesla-coil-party" />}
    >
      <section className="mt-6 grid gap-4">
        {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((n) => (
          <article key={n} className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
            <h2 className="text-xl font-semibold tracking-[-0.02em]">{t(`legal.tcp${n}Title`)}</h2>
            <p className="mt-3 text-sm leading-7 text-white/70">{t(`legal.tcp${n}Body`)}</p>
          </article>
        ))}
      </section>
      <section className="mt-6 rounded-2xl border border-white/10 bg-white/[0.03] p-5 text-sm leading-7 text-white/70">
        <p>
          Product:{" "}
          <Link
            href="/entertainment#tesla-coil-party"
            className="text-violet-200 underline decoration-violet-400/40 underline-offset-4"
          >
            /entertainment#tesla-coil-party
          </Link>
        </p>
      </section>
    </LegalShell>
  );
}

export function AntiqueFireRestoreLegalView() {
  const { t } = useLanguage();
  return (
    <LegalShell
      kickerClass="border-amber-300/20 bg-amber-400/[0.06]"
      kicker={t("legal.antiqueFireRestoreKicker")}
      title={t("legal.antiqueFireRestoreTitle")}
      intro={`${t("legal.lastUpdated")} ${t("legal.antiqueFireRestoreIntro")}`}
      actions={<LegalNavPills current="/legal/antique-fire-restore" />}
    >
      <section className="mt-6 grid gap-4">
        {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((n) => (
          <article key={n} className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
            <h2 className="text-xl font-semibold tracking-[-0.02em]">{t(`legal.afr${n}Title`)}</h2>
            <p className="mt-3 text-sm leading-7 text-white/70">{t(`legal.afr${n}Body`)}</p>
          </article>
        ))}
      </section>
      <section className="mt-6 rounded-2xl border border-white/10 bg-white/[0.03] p-5 text-sm leading-7 text-white/70">
        <p>
          Product:{" "}
          <Link
            href="/antique-fire-restore"
            className="text-amber-200 underline decoration-amber-400/40 underline-offset-4"
          >
            /antique-fire-restore
          </Link>
        </p>
      </section>
    </LegalShell>
  );
}

export function PulmoPureLegalView() {
  const { t } = useLanguage();
  return (
    <LegalShell
      kickerClass="border-violet-300/20 bg-violet-400/[0.06]"
      kicker={t("legal.pulmopureKicker")}
      title={t("legal.pulmopureTitle")}
      intro={`${t("legal.lastUpdated")} ${t("legal.pulmopureIntro")}`}
      actions={<LegalNavPills current="/legal/pulmopure" />}
    >
      <section className="mt-6 grid gap-4">
        {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((n) => (
          <article key={n} className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
            <h2 className="text-xl font-semibold tracking-[-0.02em]">{t(`legal.pp${n}Title`)}</h2>
            <p className="mt-3 text-sm leading-7 text-white/70">{t(`legal.pp${n}Body`)}</p>
          </article>
        ))}
      </section>
      <section className="mt-6 rounded-2xl border border-white/10 bg-white/[0.03] p-5 text-sm leading-7 text-white/70">
        <p>
          Product:{" "}
          <Link href="/aeterna#pulmopure" className="text-sky-200 underline decoration-sky-400/40 underline-offset-4">
            /aeterna#pulmopure
          </Link>
        </p>
      </section>
    </LegalShell>
  );
}

export function BarsukLegalView() {
  const { t } = useLanguage();
  return (
    <LegalShell
      kickerClass="border-slate-300/20 bg-slate-400/[0.06]"
      kicker={t("legal.barsukKicker")}
      title={t("legal.barsukTitle")}
      intro={`${t("legal.lastUpdated")} ${t("legal.barsukIntro")}`}
      actions={<LegalNavPills current="/legal/barsuk" />}
    >
      <section className="mt-6 grid gap-4">
        {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((n) => (
          <article key={n} className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
            <h2 className="text-xl font-semibold tracking-[-0.02em]">{t(`legal.bk${n}Title`)}</h2>
            <p className="mt-3 text-sm leading-7 text-white/70">{t(`legal.bk${n}Body`)}</p>
          </article>
        ))}
      </section>
      <section className="mt-6 rounded-2xl border border-white/10 bg-white/[0.03] p-5 text-sm leading-7 text-white/70">
        <p>
          Product:{" "}
          <Link href="/aeterna#barsuk" className="text-sky-200 underline decoration-sky-400/40 underline-offset-4">
            /aeterna#barsuk
          </Link>
        </p>
      </section>
    </LegalShell>
  );
}

export function TeleportEarphonesLegalView() {
  const { t } = useLanguage();
  return (
    <LegalShell
      kickerClass="border-cyan-300/20 bg-cyan-400/[0.06]"
      kicker={t("legal.teleportEarphonesKicker")}
      title={t("legal.teleportEarphonesTitle")}
      intro={`${t("legal.lastUpdated")} ${t("legal.teleportEarphonesIntro")}`}
      actions={<LegalNavPills current="/legal/teleport-earphones" />}
    >
      <section className="mt-6 grid gap-4">
        {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((n) => (
          <article key={n} className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
            <h2 className="text-xl font-semibold tracking-[-0.02em]">{t(`legal.tp${n}Title`)}</h2>
            <p className="mt-3 text-sm leading-7 text-white/70">{t(`legal.tp${n}Body`)}</p>
          </article>
        ))}
      </section>
      <section className="mt-6 rounded-2xl border border-white/10 bg-white/[0.03] p-5 text-sm leading-7 text-white/70">
        <p>
          Product:{" "}
          <Link
            href="/aeterna#teleport-earphones"
            className="text-sky-200 underline decoration-sky-400/40 underline-offset-4"
          >
            /aeterna#teleport-earphones
          </Link>
        </p>
      </section>
    </LegalShell>
  );
}

export function InstallationProjectLegalView() {
  const { t } = useLanguage();
  return (
    <LegalShell
      kickerClass="border-sky-300/20 bg-sky-400/[0.06]"
      kicker={t("legal.installationProjectKicker")}
      title={t("legal.installationProjectTitle")}
      intro={`${t("legal.lastUpdated")} ${t("legal.installationProjectIntro")}`}
      actions={<LegalNavPills current="/legal/installation-project" />}
    >
      <section className="mt-6 grid gap-4">
        {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((n) => (
          <article key={n} className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
            <h2 className="text-xl font-semibold tracking-[-0.02em]">{t(`legal.ip${n}Title`)}</h2>
            <p className="mt-3 text-sm leading-7 text-white/70">{t(`legal.ip${n}Body`)}</p>
          </article>
        ))}
      </section>
      <section className="mt-6 rounded-2xl border border-white/10 bg-white/[0.03] p-5 text-sm leading-7 text-white/70">
        <p>
          Product:{" "}
          <Link
            href="/aeterna#installation-project"
            className="text-sky-200 underline decoration-sky-400/40 underline-offset-4"
          >
            /aeterna#installation-project
          </Link>
        </p>
        <p className="mt-2">
          Insurance:{" "}
          <Link href="/insurance" className="text-sky-200 underline decoration-sky-400/40 underline-offset-4">
            /insurance
          </Link>{" "}
          (coverage class neonatal_install)
        </p>
      </section>
    </LegalShell>
  );
}

export function DnaPheromonePerfumeLegalView() {
  const { t } = useLanguage();
  return (
    <LegalShell
      kickerClass="border-amber-300/20 bg-amber-400/[0.06]"
      kicker={t("legal.dnaPheromonePerfumeKicker")}
      title={t("legal.dnaPheromonePerfumeTitle")}
      intro={`${t("legal.lastUpdated")} ${t("legal.dnaPheromonePerfumeIntro")}`}
      actions={<LegalNavPills current="/legal/dna-pheromone-perfume" />}
    >
      <section className="mt-6 grid gap-4">
        {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((n) => (
          <article key={n} className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
            <h2 className="text-xl font-semibold tracking-[-0.02em]">{t(`legal.ppf${n}Title`)}</h2>
            <p className="mt-3 text-sm leading-7 text-white/70">{t(`legal.ppf${n}Body`)}</p>
          </article>
        ))}
      </section>
      <section className="mt-6 rounded-2xl border border-white/10 bg-white/[0.03] p-5 text-sm leading-7 text-white/70">
        <p>
          Product:{" "}
          <Link
            href="/aeterna#dna-pheromone-perfume"
            className="text-amber-200 underline decoration-amber-400/40 underline-offset-4"
          >
            /aeterna#dna-pheromone-perfume
          </Link>
        </p>
        <p className="mt-2">
          Workflow:{" "}
          <Link
            href="/ai/run/aeterna-dna-pheromone-perfume"
            className="text-amber-200 underline decoration-amber-400/40 underline-offset-4"
          >
            aeterna-dna-pheromone-perfume
          </Link>{" "}
          (8,900 ACP / 1 bottle)
        </p>
      </section>
    </LegalShell>
  );
}

export function StardustLegalView() {
  const { t } = useLanguage();
  return (
    <LegalShell
      kickerClass="border-cyan-300/20 bg-cyan-400/[0.06]"
      kicker={t("legal.stardustKicker")}
      title={t("legal.stardustTitle")}
      intro={`${t("legal.lastUpdated")} ${t("legal.stardustIntro")}`}
      actions={<LegalNavPills current="/legal/stardust" />}
    >
      <section className="mt-6 grid gap-4">
        {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((n) => (
          <article key={n} className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
            <h2 className="text-xl font-semibold tracking-[-0.02em]">{t(`legal.sd${n}Title`)}</h2>
            <p className="mt-3 text-sm leading-7 text-white/70">{t(`legal.sd${n}Body`)}</p>
          </article>
        ))}
      </section>
      <section className="mt-6 rounded-2xl border border-white/10 bg-white/[0.03] p-5 text-sm leading-7 text-white/70">
        <p>
          Product:{" "}
          <Link href="/stardust" className="text-sky-200 underline decoration-sky-400/40 underline-offset-4">
            /stardust
          </Link>
        </p>
        <p className="mt-2">
          Insurance:{" "}
          <Link href="/insurance" className="text-sky-200 underline decoration-sky-400/40 underline-offset-4">
            /insurance
          </Link>{" "}
          (coverage class weather_control)
        </p>
      </section>
    </LegalShell>
  );
}

export function DarkMatterLegalView() {
  const { t } = useLanguage();
  return (
    <LegalShell
      kickerClass="border-indigo-300/20 bg-indigo-400/[0.06]"
      kicker={t("legal.darkMatterKicker")}
      title={t("legal.darkMatterTitle")}
      intro={`${t("legal.lastUpdated")} ${t("legal.darkMatterIntro")}`}
      actions={<LegalNavPills current="/legal/dark-matter" />}
    >
      <section className="mt-6 grid gap-4">
        {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((n) => (
          <article key={n} className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
            <h2 className="text-xl font-semibold tracking-[-0.02em]">{t(`legal.dm${n}Title`)}</h2>
            <p className="mt-3 text-sm leading-7 text-white/70">{t(`legal.dm${n}Body`)}</p>
          </article>
        ))}
      </section>
      <section className="mt-6 rounded-2xl border border-white/10 bg-white/[0.03] p-5 text-sm leading-7 text-white/70">
        <p>
          Product:{" "}
          <Link href="/dark-matter" className="text-indigo-200 underline decoration-indigo-400/40 underline-offset-4">
            /dark-matter
          </Link>
        </p>
        <p className="mt-2">
          Related:{" "}
          <Link href="/galaxy" className="text-indigo-200 underline decoration-indigo-400/40 underline-offset-4">
            /galaxy
          </Link>
          {" · "}
          <Link href="/insurance" className="text-indigo-200 underline decoration-indigo-400/40 underline-offset-4">
            /insurance
          </Link>{" "}
          (coverage class dark_matter_title)
        </p>
      </section>
    </LegalShell>
  );
}

export function WelcomeGrantView() {
  const { t } = useLanguage();
  return (
    <LegalShell
      kickerClass="border-emerald-300/20 bg-emerald-400/[0.06]"
      kicker={t("legal.welcomeGrantKicker")}
      title={t("legal.welcomeGrantTitle")}
      intro={`${t("legal.lastUpdated")} ${t("legal.welcomeGrantIntro")}`}
      actions={<LegalNavPills current="/legal/welcome-grant" />}
    >
      <section className="mt-6 grid gap-4">
        {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map((n) => (
          <article key={n} className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
            <h2 className="text-xl font-semibold tracking-[-0.02em]">{t(`legal.wg${n}Title`)}</h2>
            <p className="mt-3 text-sm leading-7 text-white/70">{t(`legal.wg${n}Body`)}</p>
          </article>
        ))}
        <p className="text-sm leading-7 text-white/55">
          {t("legal.welcomeGrantAlso")}{" "}
          <Link href="/register" className="text-sky-200 underline decoration-sky-400/40 underline-offset-4">
            /register
          </Link>
          {" · "}
          <Link href="/legal/refunds" className="text-sky-200 underline decoration-sky-400/40 underline-offset-4">
            /legal/refunds
          </Link>
          {" · "}
          <Link href="/legal/risk" className="text-sky-200 underline decoration-sky-400/40 underline-offset-4">
            /legal/risk
          </Link>
          {" · "}
          <Link href="/legal/humanitarian" className="text-sky-200 underline decoration-sky-400/40 underline-offset-4">
            /legal/humanitarian
          </Link>
        </p>
      </section>
    </LegalShell>
  );
}

export function SiteLegalFooter() {
  const { t } = useLanguage();
  const links = [
    { href: "/legal", label: "footerLegal" },
    { href: "/legal/terms", label: "footerTerms" },
    { href: "/legal/privacy", label: "footerPrivacy" },
    { href: "/legal/cookies", label: "footerCookies" },
    { href: "/legal/risk", label: "footerRisk" },
    { href: "/legal/market-data", label: "footerMarketData" },
    { href: "/legal/research-refs", label: "footerResearchRefs" },
    { href: "/legal/cryo-constitution", label: "footerCryo" },
    { href: "/legal/vet-regen", label: "footerVetRegen" },
    { href: "/legal/light-chamber", label: "footerLightChamber" },
    { href: "/legal/body-contouring", label: "footerBodyContouring" },
    { href: "/legal/biofusion", label: "footerBiofusion" },
    { href: "/legal/dpsc", label: "footerDpsc" },
    { href: "/legal/vascular-care-plus", label: "footerVascularPlus" },
    { href: "/legal/vascular-care", label: "footerVascular" },
    { href: "/legal/transdermal", label: "footerTransdermal" },
    { href: "/legal/m-receptor", label: "footerMReceptor" },
    { href: "/legal/oxygen-carrier", label: "footerOxygenCarrier" },
    { href: "/legal/synthetic-blood-mamba", label: "footerSyntheticBloodMamba" },
    { href: "/legal/adhd-support", label: "footerAdhdSupport" },
    { href: "/legal/aurea-vita", label: "footerAureaVita" },
    { href: "/legal/down-syndrome-support", label: "footerDownSyndromeSupport" },
    { href: "/legal/substance-coding", label: "footerSubstanceCoding" },
    { href: "/legal/tesla-coil-party", label: "footerTeslaCoilParty" },
    { href: "/legal/antique-fire-restore", label: "footerAntiqueFireRestore" },
    { href: "/legal/pulmopure", label: "footerPulmopure" },
    { href: "/legal/installation-project", label: "footerInstallationProject" },
    { href: "/legal/stardust", label: "footerStardust" },
    { href: "/legal/refunds", label: "footerRefunds" },
    { href: "/legal/welcome-grant", label: "footerWelcomeGrant" },
    { href: "/legal/humanitarian", label: "footerHumanitarian" },
    { href: "/legal/clarity-act", label: "footerClarity" },
  ] as const;
  return (
    <footer
      style={{
        padding: "32px 24px",
        borderTop: "1px solid var(--border)",
        color: "var(--text-muted)",
        fontSize: "0.9rem",
      }}
    >
      <div className="container" style={{ textAlign: "center" }}>
        <div style={{ display: "flex", flexWrap: "wrap", gap: "12px 18px", justifyContent: "center", marginBottom: 12 }}>
          {links.map((link) => (
            <Link key={link.href} href={link.href} style={{ color: "var(--text-muted)", textDecoration: "none" }}>
              {t(`legal.${link.label}`)}
            </Link>
          ))}
        </div>
        <div>
          <Link href="/" style={{ color: "var(--text-muted)", textDecoration: "none", fontWeight: 800 }}>
            ANCAP
          </Link>
          <span> — {t("homePage.footer")}</span>
        </div>
        <div style={{ marginTop: 8, fontSize: "0.8rem" }}>
          <a href="mailto:legal@ancap.cloud" style={{ color: "var(--text-muted)" }}>
            legal@ancap.cloud
          </a>
          {" · "}
          <a href="mailto:privacy@ancap.cloud" style={{ color: "var(--text-muted)" }}>
            privacy@ancap.cloud
          </a>
          {" · "}
          <a href="mailto:support@ancap.cloud" style={{ color: "var(--text-muted)" }}>
            support@ancap.cloud
          </a>
        </div>
      </div>
    </footer>
  );
}
