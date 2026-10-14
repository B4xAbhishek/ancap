import type { Language } from "@/locales/translations";
import { offerCopyByLang, offerKindLabelByLang, type OfferCopyFields } from "./projectOffersCopy";

/**
 * Honest commercial chain for each public portfolio route.
 * offerKind:
 *   executable — paid workflow slug(s) exist in backend WORKFLOW_TEMPLATES
 *   brief — AI document / partner-intake brief (not a physical service)
 *   concept — planning / research page; no buyer checkout claim
 *   desk — human/partner desk handoff; catalog may list ACP intakes
 */

export type OfferKind = "executable" | "brief" | "concept" | "desk";

export type ProjectOffer = OfferCopyFields & {
  href: string;
  offerKind: OfferKind;
  /** Backend workflow-store slugs when an executable or brief SKU exists. Empty ⇒ concept page. */
  workflowSlugs: string[];
};

type OfferDef = {
  href: string;
  offerKind: OfferKind;
  workflowSlugs: string[];
};

/** Structural catalog — localized copy lives in projectOffersCopy.ts */
export const projectOfferDefs: OfferDef[] = [
  { href: "/markets", offerKind: "executable", workflowSlugs: ["market-direction-brief", "commodity-price-outlook", "crypto-quote-momentum-scan", "markets-ai-radar-pro"] },
  { href: "/business", offerKind: "brief", workflowSlugs: ["agent-api-readiness-pack", "ai-iso-governance-readiness-pack"] },
  { href: "/growth", offerKind: "executable", workflowSlugs: ["crypto-campaign-builder", "telegram-growth-kit", "kol-telegram-campaign-builder", "growth-pack", "growth-pro-pack"] },
  { href: "/agency", offerKind: "executable", workflowSlugs: ["launch-pack", "pro-launch-pack", "concierge-pack"] },
  { href: "/startups", offerKind: "executable", workflowSlugs: ["token-listing-pack", "token-launch-audit-pack", "exchange-listing-submission-pack"] },
  { href: "/counsel", offerKind: "brief", workflowSlugs: ["counsel-jurisdiction-match", "counsel-entity-setup", "counsel-contract-review", "counsel-crypto-assets"] },
  { href: "/insurance", offerKind: "concept", workflowSlugs: [] },
  { href: "/compliance", offerKind: "executable", workflowSlugs: ["ai-iso-governance-readiness-pack", "compliance-pack"] },
  { href: "/careers", offerKind: "concept", workflowSlugs: [] },
  { href: "/flora", offerKind: "desk", workflowSlugs: [] },
  { href: "/literary", offerKind: "desk", workflowSlugs: [] },
  { href: "/marketplace", offerKind: "desk", workflowSlugs: [] },
  { href: "/field-services", offerKind: "brief", workflowSlugs: ["it-pc-setup", "it-device-repair", "it-network-home", "cam-cctv-install", "solar-balcony-install"] },
  { href: "/starlink-install", offerKind: "brief", workflowSlugs: ["starlink-install-intake", "starlink-standard", "starlink-business"] },
  { href: "/antique-fire-restore", offerKind: "brief", workflowSlugs: ["antique-fire-restore"] },
  { href: "/humanitarian", offerKind: "desk", workflowSlugs: [] },
  { href: "/aeterna", offerKind: "brief", workflowSlugs: ["aeterna-dna-wellness-report", "aeterna-longevity-panel-brief", "aeterna-molecular-aging-profile"] },
  { href: "/dna-bank", offerKind: "brief", workflowSlugs: ["aeterna-dna-wellness-report"] },
  { href: "/cryo", offerKind: "desk", workflowSlugs: [] },
  { href: "/saliva-rx", offerKind: "concept", workflowSlugs: [] },
  { href: "/fauna", offerKind: "concept", workflowSlugs: ["aeterna-vet-cat-cryo-restore", "aeterna-vet-regen-pod"] },
  { href: "/tech", offerKind: "concept", workflowSlugs: ["stardust-extreme-weather-monitor", "stardust-disaster-early-warning"] },
  { href: "/perimeter", offerKind: "concept", workflowSlugs: [] },
  { href: "/galaxy", offerKind: "brief", workflowSlugs: ["space-ai-orbit-intake", "space-ai-beyond-orbit", "space-ai-superintel-architecture"] },
  { href: "/lunar", offerKind: "concept", workflowSlugs: [] },
  { href: "/stardust", offerKind: "brief", workflowSlugs: ["stardust-extreme-weather-monitor", "stardust-disaster-early-warning", "stardust-weather-control-global", "stardust-weather-control-subscription"] },
  { href: "/quantum-sim", offerKind: "concept", workflowSlugs: [] },
  { href: "/nexus", offerKind: "concept", workflowSlugs: [] },
  { href: "/dating", offerKind: "concept", workflowSlugs: [] },
  { href: "/entertainment", offerKind: "brief", workflowSlugs: ["entertainment-tesla-coil-party"] },
  { href: "/arena", offerKind: "concept", workflowSlugs: [] },
  { href: "/feed", offerKind: "concept", workflowSlugs: [] },
];

/** @deprecated Prefer offerForRoute(pathname, lang). English snapshot for tests/slug sync. */
export const projectOffers: ProjectOffer[] = projectOfferDefs.map((def) => ({
  ...def,
  ...offerCopyByLang.en[def.href],
}));

export function offerForRoute(pathname: string, lang: Language = "en"): ProjectOffer | null {
  const def = projectOfferDefs.find((item) => item.href === pathname);
  if (!def) return null;
  const copy = offerCopyByLang[lang]?.[def.href] ?? offerCopyByLang.en[def.href];
  if (!copy) return null;
  return { ...def, ...copy };
}

export function offerKindLabel(kind: OfferKind, lang: Language = "en"): string {
  return offerKindLabelByLang[lang]?.[kind] ?? offerKindLabelByLang.en[kind];
}

/** @deprecated use offerKindLabel(kind, lang) */
export const OFFER_KIND_LABEL: Record<OfferKind, string> = offerKindLabelByLang.en;
