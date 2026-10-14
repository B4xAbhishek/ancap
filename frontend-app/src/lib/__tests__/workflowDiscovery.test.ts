import { describe, expect, it } from "vitest";
import { fallbackWorkflowTemplates } from "../workflowStore";
import { parseSavedWorkflows, plannedRunCost, recommendWorkflows } from "../workflowDiscovery";
import { discoveryByLang } from "@/locales/discovery";

describe("workflow discovery", () => {
  it("recommends only supplied offers and keeps a predictable order", () => {
    const offers = [...fallbackWorkflowTemplates].reverse();
    const original = offers.map(item => item.slug);
    expect(recommendWorkflows(offers, "risk").map(item => item.slug)).toEqual(["token-risk-report-pro", "token-risk-report", "token-launch-audit-pack"]);
    expect(offers.map(item => item.slug)).toEqual(original);
    expect(recommendWorkflows([], "launch")).toEqual([]);
  });
  it("does not replace missing offers with unrelated medical or research products", () => {
    const research = fallbackWorkflowTemplates.filter(item => item.category === "AETERNA");
    expect(recommendWorkflows(research, "risk")).toEqual([]);
  });
  it("recovers from corrupt saved data and discards removed or duplicate offers", () => {
    expect(parseSavedWorkflows("invalid", fallbackWorkflowTemplates)).toEqual([]);
    expect(parseSavedWorkflows('{"slug":"token-risk-report"}', fallbackWorkflowTemplates)).toEqual([]);
    expect(parseSavedWorkflows('["token-risk-report","unknown",false,"token-risk-report"]', fallbackWorkflowTemplates)).toEqual(["token-risk-report"]);
  });
  it("calculates exact decimal costs without floating-point rounding", () => {
    expect(plannedRunCost("0.1", 3)).toBe("0.3");
    expect(plannedRunCost("0.00000001", 10000)).toBe("0.0001");
    expect(plannedRunCost("14.00", 10)).toBe("140");
    expect(plannedRunCost("999999999999999999.99", 10000)).toBe("9999999999999999999900");
  });
  it("rejects invalid prices and run counts instead of displaying misleading costs", () => {
    for (const count of [0, -1, 1.5, NaN, Infinity, 10001]) expect(plannedRunCost("14", count)).toBeNull();
    for (const price of ["", "-1", "1e6", "NaN", "12 ACP"]) expect(plannedRunCost(price, 10)).toBeNull();
  });
  it("provides complete controls in all five languages", () => {
    for (const lang of ["en", "ru", "uk", "de", "zh-Hant"] as const) {
      expect(Object.keys(discoveryByLang[lang]).sort()).toEqual(Object.keys(discoveryByLang.en).sort());
      for (const value of Object.values(discoveryByLang[lang])) expect(value.trim()).not.toBe("");
    }
  });
});
