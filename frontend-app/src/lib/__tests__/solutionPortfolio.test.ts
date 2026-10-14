import { describe, expect, it } from "vitest";
import { existsSync } from "node:fs";
import path from "node:path";
import { portfolioByLang, solutionPortfolio, workflowArea } from "../solutionPortfolio";
import { offerForRoute, projectOffers } from "../projectOffers";
import { positioningByLang } from "@/locales/positioning";
import { t } from "@/locales/translations";

describe("public workflow presentation", () => {
  it("keeps every portfolio entry reachable at an existing page", () => {
    const links = solutionPortfolio.flatMap(area => area.routes.map(([href]) => href));
    expect(new Set(links).size).toBe(links.length);
    for (const href of links) {
      expect(existsSync(path.join(process.cwd(), "src/app", href, "page.tsx")), href).toBe(true);
    }
  });
  it("has complete copy and matching areas for every supported language", () => {
    for (const lang of ["en", "ru", "uk", "de", "zh-Hant"] as const) {
      expect(Object.keys(positioningByLang[lang]).sort()).toEqual(Object.keys(positioningByLang.en).sort());
      expect(portfolioByLang[lang].areas).toHaveLength(solutionPortfolio.length);
      expect(t(lang, "positioning.investors")).toBe(positioningByLang[lang].investors);
      for (const value of Object.values(positioningByLang[lang])) expect(value.trim()).not.toBe("");
    }
  });
  it("keeps clinical research separate from crypto launch offers", () => {
    expect(workflowArea("AETERNA")).toBe("life");
    expect(workflowArea("Premium Launch")).toBe("crypto");
    expect(workflowArea("Counsel")).toBe("business");
    expect(workflowArea("Conservation")).toBe("commerce");
    expect(workflowArea("Entertainment")).toBe("community");
    expect(workflowArea("Agent Commerce")).toBe("infrastructure");
  });
  it("maps every portfolio route to an honest buyer→receipt offer chain", () => {
    const links = solutionPortfolio.flatMap(area => area.routes.map(([href]) => href));
    expect(projectOffers.map(o => o.href).sort()).toEqual([...links].sort());
    for (const href of links) {
      const offer = offerForRoute(href);
      expect(offer, href).toBeTruthy();
      expect(offer!.buyer.trim()).not.toBe("");
      expect(offer!.task.trim()).not.toBe("");
      expect(offer!.inputs.trim()).not.toBe("");
      expect(offer!.aiResult.trim()).not.toBe("");
      expect(offer!.constraints.trim()).not.toBe("");
      expect(offer!.payment.trim()).not.toBe("");
      expect(offer!.receipt.trim()).not.toBe("");
      if (offer!.offerKind === "concept") {
        // Concept pages may still list related brief slugs for literacy, but must not claim physical delivery.
        expect(offer!.constraints.toLowerCase()).toMatch(/not |n\/a|pilot|concept|literacy|none/);
      }
    }
  });
});
