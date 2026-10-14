import { describe, expect, it } from "vitest";
import { existsSync } from "node:fs";
import path from "node:path";
import { portfolioByLang, solutionPortfolio, workflowArea } from "../solutionPortfolio";
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
});
