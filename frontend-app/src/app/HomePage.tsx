"use client";

import Link from "next/link";
import { useEffect } from "react";
import { Navigation } from "@/components/Navigation";
import { HomeMcpSection } from "@/components/HomeMcpSection";
import { HomeMarketTicker } from "@/components/HomeMarketTicker";
import { WacpPublicActions } from "@/components/WacpPublicActions";
import { DnaNanobotScissors } from "@/components/DnaNanobotScissors";
import { HomeGalaxySection } from "@/components/HomeGalaxySection";
import { HomeAgencySection } from "@/components/HomeAgencySection";
import { useLanguage } from "@/components/LanguageProvider";
import { SiteLegalFooter } from "@/components/legal/LegalViews";

const offerDefs = [
  {
    titleKey: "homePage.offer1Title",
    labelKey: "homePage.offer1Label",
    resultKey: "homePage.offer1Result",
    price: "349 ACP",
    href: "/ai/bundles/pro-launch-pack",
  },
  {
    titleKey: "homePage.offer2Title",
    labelKey: "homePage.offer2Label",
    resultKey: "homePage.offer2Result",
    price: "149 ACP",
    href: "/ai/run/exchange-listing-submission-pack",
  },
  {
    titleKey: "homePage.offer3Title",
    labelKey: "homePage.offer3Label",
    resultKey: "homePage.offer3Result",
    price: "59 ACP",
    href: "/ai/run/token-risk-report-pro",
  },
];

const productMapDefs = [
  ["homePage.launchLabel", "homePage.launchText"],
  ["homePage.riskLabel", "homePage.riskText"],
  ["homePage.creatorLabel", "homePage.creatorText"],
  ["homePage.agentApiLabel", "homePage.agentApiText"],
  ["homePage.proofLabel", "homePage.proofText"],
];

const stepDefs = [
  ["homePage.step1Title", "homePage.step1Text"],
  ["homePage.step2Title", "homePage.step2Text"],
  ["homePage.step3Title", "homePage.step3Text"],
  ["homePage.step4Title", "homePage.step4Text"],
];

const audienceDefs = [
  ["homePage.audience1Title", "homePage.audience1Text"],
  ["homePage.audience2Title", "homePage.audience2Text"],
  ["homePage.audience3Title", "homePage.audience3Text"],
  ["homePage.audience4Title", "homePage.audience4Text"],
];

const productRoutes = [
  { titleKey: "homePage.routeWorkflowStore", href: "/ai/workflows", textKey: "homePage.route1Text" },
  { titleKey: "homePage.routePricing", href: "/pricing", textKey: "homePage.route2Text" },
  { titleKey: "homePage.routeTokenSnapshot", href: "/token-snapshot", textKey: "homePage.route3Text" },
  { titleKey: "homePage.routeDevelopers", href: "/developers", textKey: "homePage.route4Text" },
  { titleKey: "homePage.routeProofCenter", href: "/proof-center", textKey: "homePage.route5Text" },
  { titleKey: "homePage.routeAcpWallet", href: "/wallet/acp", textKey: "homePage.route6Text" },
  { titleKey: "homePage.routeSellerDashboard", href: "/dashboard/seller", textKey: "homePage.route7Text" },
  { titleKey: "homePage.routeGalaxy", href: "/galaxy", textKey: "homePage.galaxyCta" },
  { titleKey: "agencyPage.nav", href: "/agency", textKey: "agencyPage.homeLead" },
];

const socialLinks = [
  { labelKey: "hero.followOnX", href: "https://x.com/ancap24news", icon: "X" },
  { labelKey: "hero.followOnTelegram", href: "https://t.me/ancap24news", icon: "TG" },
];

export function HomePage() {
  const { t } = useLanguage();
  const acpUrl = process.env.NEXT_PUBLIC_ACP_URL || "/acp";

  useEffect(() => {
    document.title = t("hero.title");
  }, [t]);

  const offers = offerDefs.map((offer) => ({
    ...offer,
    title: t(offer.titleKey),
    label: t(offer.labelKey),
    result: t(offer.resultKey),
  }));
  const productSchema = {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    name: "ANCAP",
    applicationCategory: "BusinessApplication",
    operatingSystem: "Web",
    description:
      "Paid AI workflows for crypto teams and AI agents: buy execution, create paid workflows, publish them on ANCAP, earn from runs, settle in ACP, and attach proof receipts.",
    featureList: [
      "Buy paid AI workflows",
      "Create and publish paid AI workflows",
      "Earn from workflow runs",
      "ACP checkout",
      "Proof-backed receipts",
    ],
    offers: offers.map((offer) => ({
      "@type": "Offer",
      name: offer.title,
      price: offer.price.replace(" ACP", ""),
      priceCurrency: "ACP",
      url: `https://ancap.cloud${offer.href}`,
    })),
  };

  return (
    <div className="relative min-h-screen">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(productSchema) }}
      />
      <div className="min-h-screen">
        <Navigation />

        <main>
          <section style={{ padding: "72px 0 56px" }} aria-labelledby="home-title">
            <div className="container">
              <div
                className="home-hero-grid"
                style={{
                  display: "grid",
                  gap: 28,
                  alignItems: "center",
                }}
              >
                <div>
                  <div className="section-num">{t("homePage.badge")}</div>
                  <h1
                    id="home-title"
                    style={{
                      fontSize: "3.35rem",
                      fontWeight: 850,
                      letterSpacing: 0,
                      lineHeight: 1.04,
                      marginBottom: 22,
                      maxWidth: 780,
                    }}
                  >
                    {t("hero.title")}
                  </h1>
                  <p
                    style={{
                      fontSize: "1.15rem",
                      color: "var(--text)",
                      maxWidth: 760,
                      lineHeight: 1.7,
                      marginBottom: 18,
                    }}
                  >
                    {t("homePage.heroLead")}
                  </p>
                  <p
                    style={{
                      color: "var(--text-muted)",
                      maxWidth: 720,
                      lineHeight: 1.7,
                      marginBottom: 12,
                    }}
                  >
                    {t("homePage.acpLead")}
                  </p>
                  <p
                    style={{
                      color: "var(--text-muted)",
                      maxWidth: 720,
                      lineHeight: 1.7,
                      marginBottom: 28,
                      fontSize: "0.95rem",
                    }}
                  >
                    {t("homePage.welcomeGrantLead")}{" "}
                    <Link href="/legal/welcome-grant" style={{ color: "var(--accent)" }}>
                      {t("legal.welcomeGrantLink")}
                    </Link>
                    {" · "}
                    <Link href="/humanitarian" style={{ color: "var(--accent)" }}>
                      {t("legal.humanitarianLink")}
                    </Link>
                  </p>
                  <div className="home-cta-board">
                    <div className="home-cta-board__row home-cta-board__row--2">
                      <Link href="/token-snapshot" className="home-cta home-cta--primary home-cta--glow">
                        <span className="home-cta__eyebrow">{t("homePage.ctaSnapshotEyebrow")}</span>
                        <span className="home-cta__label">{t("homePage.ctaSnapshot")}</span>
                      </Link>
                      <Link href="/ai/run/token-risk-report-pro" className="home-cta home-cta--primary">
                        <span className="home-cta__eyebrow">{t("homePage.ctaProReportEyebrow")}</span>
                        <span className="home-cta__label">{t("homePage.ctaProReport")}</span>
                      </Link>
                    </div>
                    <div className="home-cta-board__row home-cta-board__row--2">
                      <Link href="/pay/create" className="home-cta home-cta--ghost">
                        <span className="home-cta__label">{t("homePage.ctaPayLink")}</span>
                      </Link>
                      <Link href="/developers" className="home-cta home-cta--ghost">
                        <span className="home-cta__label">{t("homePage.ctaApi")}</span>
                      </Link>
                    </div>
                    <div className="home-cta-board__row home-cta-board__row--3">
                      {acpUrl.startsWith("http") ? (
                        <a href={acpUrl} className="home-cta home-cta--rail" target="_blank" rel="noopener noreferrer">
                          <span className="home-cta__label">{t("hero.acpLink")}</span>
                        </a>
                      ) : (
                        <Link href={acpUrl} className="home-cta home-cta--rail">
                          <span className="home-cta__label">{t("hero.acpLink")}</span>
                        </Link>
                      )}
                      <Link href="/wallet/acp" className="home-cta home-cta--rail">
                        <span className="home-cta__label">{t("nav.acpWallet")}</span>
                      </Link>
                      <Link href="/proof-center" className="home-cta home-cta--rail">
                        <span className="home-cta__label">{t("homePage.proofCenter")}</span>
                      </Link>
                    </div>
                    <div className="home-cta-board__row home-cta-board__row--2">
                      {socialLinks.map((social) => (
                        <a
                          key={social.href}
                          href={social.href}
                          className="home-cta home-cta--social"
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          <span className="home-cta__icon" aria-hidden>
                            {social.icon}
                          </span>
                          <span className="home-cta__label">{t(social.labelKey)}</span>
                        </a>
                      ))}
                    </div>
                    <div className="home-cta-board__row home-cta-board__row--1">
                      <WacpPublicActions
                        layout="home"
                        addLabel={t("homePage.wacpAddMetaMask")}
                      />
                    </div>
                  </div>
                </div>

                <aside className="home-product-card" aria-label={t("homePage.productMapTitle")}>
                  <div className="home-product-card__badge">{t("homePage.liveMap")}</div>
                  <h2 className="home-product-card__title">{t("homePage.productMapTitle")}</h2>
                  <div className="home-product-map">
                    {productMapDefs.map(([nameKey, textKey]) => (
                      <div key={nameKey} className="home-product-map-row">
                        <strong className="home-product-map-label">{t(nameKey)}</strong>
                        <span className="home-product-map-text">{t(textKey)}</span>
                      </div>
                    ))}
                  </div>
                </aside>
              </div>
            </div>
          </section>

          <HomeMarketTicker />

          <HomeAgencySection />

          <HomeGalaxySection />

          <section
            id="aeterna"
            className="container"
            style={{ padding: "28px 24px 56px" }}
            aria-labelledby="aeterna-home-title"
          >
            <div
              style={{
                borderTop: "1px solid var(--border)",
                padding: "42px 0 0",
              }}
            >
              <div
                style={{
                  display: "flex",
                  flexWrap: "wrap",
                  gap: 28,
                  alignItems: "flex-end",
                  justifyContent: "space-between",
                  marginBottom: 22,
                }}
              >
                <div style={{ flex: "1 1 320px", maxWidth: 720 }}>
                    <span className="section-num">{t("nav.aeterna")}</span>
                    <h2
                      id="aeterna-home-title"
                      className="section-title"
                      style={{ marginBottom: 14 }}
                    >
                      {t("aeternaPage.homeTitle")}
                    </h2>
                    <p className="section-subtitle" style={{ maxWidth: 620, marginBottom: 0 }}>
                      {t("aeternaPage.homeLead")}
                    </p>
                  </div>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: 12 }}>
                    <Link href="/aeterna" className="btn btn-primary">
                      {t("aeternaPage.enter")}
                    </Link>
                    <Link href="/aeterna#dna-sandbox" className="btn btn-ghost">
                      {t("aeternaPage.sandboxCta")}
                    </Link>
                    <Link href="/aeterna#organ-print" className="btn btn-ghost">
                      {t("aeternaPage.organSkuCta")}
                    </Link>
                    <Link href="/aeterna#vet-regen" className="btn btn-ghost">
                      {t("aeternaPage.organRailCta")}
                    </Link>
                    <Link href="/aeterna#vinci-light" className="btn btn-ghost">
                      {t("aeternaPage.vinciCta")}
                    </Link>
                    <Link href="/aeterna#microwave-body" className="btn btn-ghost">
                      {t("aeternaPage.mwCta")}
                    </Link>
                    <Link href="/aeterna#biofusion" className="btn btn-ghost">
                      {t("aeternaPage.bfCta")}
                    </Link>
                    <Link href="/aeterna#dpsc-biomaterial" className="btn btn-ghost">
                      {t("aeternaPage.dpscCta")}
                    </Link>
                    <Link href="/aeterna#vascular-care-plus" className="btn btn-ghost">
                      {t("aeternaPage.vplusCta")}
                    </Link>
                    <Link href="/aeterna#vascular-care" className="btn btn-ghost">
                      {t("aeternaPage.vusCta")}
                    </Link>
                    <Link href="/aeterna#transdermal" className="btn btn-ghost">
                      {t("aeternaPage.tdpCta")}
                    </Link>
                    <Link href="/aeterna#m-receptor" className="btn btn-ghost">
                      {t("aeternaPage.mrCta")}
                    </Link>
                    <Link href="/aeterna#oxygen-carrier" className="btn btn-ghost">
                      {t("aeternaPage.oxCta")}
                    </Link>
                    <Link href="/aeterna#synthetic-blood-mamba" className="btn btn-ghost">
                      {t("aeternaPage.sbmCta")}
                    </Link>
                    <Link href="/aeterna#adhd-support" className="btn btn-ghost">
                      {t("aeternaPage.adhdCta")}
                    </Link>
                    <Link href="/aeterna#pulmopure" className="btn btn-ghost">
                      {t("aeternaPage.ppCta")}
                    </Link>
                    <Link href="/aeterna#installation-project" className="btn btn-ghost">
                      {t("aeternaPage.ipCta")}
                    </Link>
                </div>
              </div>
              <div
                style={{
                  borderRadius: 12,
                  border: "1px solid var(--border)",
                  overflow: "hidden",
                  marginBottom: 0,
                  borderBottom: "1px solid var(--border)",
                }}
              >
                <DnaNanobotScissors />
              </div>
            </div>
          </section>

          <section className="container" style={{ padding: "28px 24px 62px" }} aria-labelledby="offers-title">
            <div className="section-header">
              <div>
                <span className="section-num">{t("homePage.offersKicker")}</span>
                <h2 id="offers-title" className="section-title">
                  {t("homePage.offersTitle")}
                </h2>
              </div>
              <Link href="/ai/workflows" className="btn btn-ghost">
                {t("homePage.allCatalog")}
              </Link>
            </div>
            <div className="responsive-grid responsive-grid-3">
              {offers.map((offer) => (
                <Link
                  key={offer.href}
                  href={offer.href}
                  className="card"
                  style={{ textDecoration: "none", borderRadius: 8, minHeight: 250 }}
                >
                  <div className="card-header">
                    <span className="badge badge-info">{offer.label}</span>
                    <strong style={{ color: "var(--accent-strong)", fontSize: "1.2rem" }}>{offer.price}</strong>
                  </div>
                  <h3 style={{ color: "var(--text)", fontSize: "1.2rem", fontWeight: 800, marginBottom: 12 }}>
                    {offer.title}
                  </h3>
                  <p style={{ color: "var(--text-muted)", lineHeight: 1.65, margin: 0 }}>
                    {offer.result}
                  </p>
                </Link>
              ))}
            </div>
          </section>

          <section id="product" className="container" style={{ padding: "62px 24px", borderTop: "1px solid var(--border)" }}>
            <span className="section-num">{t("homePage.howKicker")}</span>
            <h2 className="section-title" style={{ maxWidth: 680, marginBottom: 16 }}>
              {t("homePage.howTitle")}
            </h2>
            <p className="section-subtitle" style={{ maxWidth: 760 }}>
              {t("homePage.howLead")}
            </p>
            <div className="responsive-grid responsive-grid-2">
              {stepDefs.map(([titleKey, textKey]) => (
                <div key={titleKey} className="card" style={{ borderRadius: 8 }}>
                  <h3 style={{ fontSize: "1.05rem", fontWeight: 800, marginBottom: 10 }}>{t(titleKey)}</h3>
                  <p style={{ color: "var(--text-muted)", lineHeight: 1.65, margin: 0 }}>{t(textKey)}</p>
                </div>
              ))}
            </div>
          </section>

          <section id="vision" className="container" style={{ padding: "62px 24px", borderTop: "1px solid var(--border)" }}>
            <span className="section-num">{t("homePage.audienceKicker")}</span>
            <h2 className="section-title" style={{ marginBottom: 16 }}>
              {t("homePage.audienceTitle")}
            </h2>
            <div className="responsive-grid responsive-grid-3">
              {audienceDefs.map(([titleKey, textKey]) => (
                <div key={titleKey} className="card" style={{ borderRadius: 8 }}>
                  <h3 style={{ fontSize: "1.1rem", fontWeight: 800, marginBottom: 10 }}>{t(titleKey)}</h3>
                  <p style={{ color: "var(--text-muted)", lineHeight: 1.65, margin: 0 }}>{t(textKey)}</p>
                </div>
              ))}
            </div>
          </section>

          <section className="container" style={{ padding: "62px 24px", borderTop: "1px solid var(--border)" }}>
            <div
              className="card home-acp-panel"
              style={{
                borderRadius: 8,
                display: "grid",
                gap: 22,
                alignItems: "center",
                background:
                  "linear-gradient(135deg, rgba(56, 189, 248, 0.12), rgba(25, 195, 138, 0.1) 45%, rgba(18, 26, 45, 0.92))",
              }}
            >
              <div>
                <span className="section-num">{t("homePage.creatorKicker")}</span>
                <h2 className="section-title" style={{ marginBottom: 12 }}>
                  {t("homePage.creatorTitle")}
                </h2>
                <p style={{ color: "var(--text-muted)", lineHeight: 1.7, margin: 0, maxWidth: 820 }}>
                  {t("homePage.creatorLead")}
                </p>
                <div className="responsive-grid responsive-grid-3" style={{ marginTop: 22 }}>
                  {[1, 2, 3].map((idx) => (
                    <div
                      key={idx}
                      style={{
                        borderTop: "1px solid var(--border)",
                        paddingTop: 14,
                        color: "var(--text-muted)",
                        lineHeight: 1.6,
                      }}
                    >
                      <strong style={{ color: "var(--text)" }}>{t(`homePage.creatorStep${idx}Title`)}</strong>
                      <div style={{ marginTop: 6 }}>{t(`homePage.creatorStep${idx}Text`)}</div>
                    </div>
                  ))}
                </div>
              </div>
              <div className="action-cluster" style={{ justifyContent: "flex-end" }}>
                <Link href="/dashboard/seller" className="btn btn-primary">
                  {t("homePage.creatorCta")}
                </Link>
                <Link href="/marketplace" className="btn btn-ghost">
                  {t("nav.marketplace")}
                </Link>
              </div>
            </div>
          </section>

          <section className="container" style={{ padding: "62px 24px", borderTop: "1px solid var(--border)" }}>
            <div
              className="home-split-grid"
              style={{
                display: "grid",
                gap: 24,
                alignItems: "start",
              }}
            >
              <div>
                <span className="section-num">{t("homePage.routesKicker")}</span>
                <h2 className="section-title" style={{ marginBottom: 16 }}>
                  {t("homePage.routesTitle")}
                </h2>
                <p className="section-subtitle">{t("homePage.routesLead")}</p>
                <Link href="/developers" className="btn btn-primary">
                  {t("homePage.openDevelopers")}
                </Link>
              </div>
              <div className="responsive-grid" style={{ gap: 12 }}>
                {productRoutes.map((route) => (
                  <Link
                    key={route.href}
                    href={route.href}
                    className="card home-route-link"
                    style={{
                      borderRadius: 8,
                      textDecoration: "none",
                      display: "grid",
                      gap: 14,
                      padding: 18,
                    }}
                  >
                    <strong style={{ color: "var(--text)" }}>{t(route.titleKey)}</strong>
                    <span style={{ color: "var(--text-muted)", lineHeight: 1.5 }}>{t(route.textKey)}</span>
                  </Link>
                ))}
              </div>
            </div>
          </section>

          <section className="container" style={{ padding: "62px 24px", borderTop: "1px solid var(--border)" }}>
            <div
              className="card home-acp-panel"
              style={{
                borderRadius: 8,
                display: "grid",
                gap: 22,
                alignItems: "center",
                background:
                  "linear-gradient(135deg, rgba(25, 195, 138, 0.15), rgba(56, 189, 248, 0.08) 45%, rgba(18, 26, 45, 0.9))",
              }}
            >
              <div>
                <span className="section-num">{t("homePage.acpKicker")}</span>
                <h2 className="section-title" style={{ marginBottom: 12 }}>
                  {t("homePage.acpTitle")}
                </h2>
                <p style={{ color: "var(--text-muted)", lineHeight: 1.7, margin: 0, maxWidth: 760 }}>
                  {t("homePage.acpText")}
                </p>
              </div>
              <div className="action-cluster" style={{ justifyContent: "flex-end" }}>
                <Link href="/acp" className="btn btn-ghost">
                  {t("homePage.acpPage")}
                </Link>
                <Link href="/wallet/acp" className="btn btn-primary">
                  {t("homePage.wallet")}
                </Link>
              </div>
            </div>
          </section>

          <HomeMcpSection />

          <section id="contact" style={{ textAlign: "center", padding: "74px 24px 60px" }}>
            <div className="container">
              <h2 style={{ fontSize: "2rem", fontWeight: 850, marginBottom: 16, letterSpacing: 0 }}>
                {t("homePage.finalTitle")}
              </h2>
              <p style={{ color: "var(--text-muted)", margin: "0 auto 30px", fontSize: "1.05rem", lineHeight: 1.65, maxWidth: 760 }}>
                {t("homePage.finalText")}
              </p>
              <div className="action-cluster" style={{ justifyContent: "center" }}>
                <Link href="/token-snapshot" className="btn btn-primary">
                  {t("homePage.freeSnapshot")}
                </Link>
                <Link href="/ai/workflows" className="btn btn-ghost">
                  {t("homePage.buyAiWorkflow")}
                </Link>
                <a href="/api/docs" className="btn btn-ghost" target="_blank" rel="noopener noreferrer">
                  {t("homePage.swaggerApi")}
                </a>
              </div>
            </div>
          </section>
        </main>

        <SiteLegalFooter />
      </div>
    </div>
  );
}
