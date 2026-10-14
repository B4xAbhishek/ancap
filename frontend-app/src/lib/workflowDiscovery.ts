import type { WorkflowTemplate } from "./workflowStore";

export type WorkflowGoal = "risk" | "launch" | "growth" | "integration";
export const goalSlugs: Record<WorkflowGoal, readonly string[]> = {
  risk: ["token-risk-report-pro", "token-risk-report", "token-launch-audit-pack"],
  launch: ["exchange-listing-submission-pack", "token-listing-pack", "token-launch-audit-pack"],
  growth: ["kol-telegram-campaign-builder", "crypto-campaign-builder", "telegram-growth-kit", "airdrop-bounty-builder"],
  integration: ["agent-api-readiness-pack", "ai-iso-governance-readiness-pack"],
};

/** Deterministic matching against the actual supplied catalog; never invent an offer. */
export function recommendWorkflows(workflows: WorkflowTemplate[], goal: WorkflowGoal): WorkflowTemplate[] {
  const priorities = goalSlugs[goal];
  return workflows.filter(item => priorities.includes(item.slug))
    .sort((a, b) => priorities.indexOf(a.slug) - priorities.indexOf(b.slug)).slice(0, 3);
}

export function parseSavedWorkflows(raw: string | null, workflows: WorkflowTemplate[]): string[] {
  try {
    const value: unknown = JSON.parse(raw ?? "[]");
    if (!Array.isArray(value)) return [];
    const available = new Set(workflows.map(item => item.slug));
    return [...new Set(value.filter((item): item is string => typeof item === "string" && available.has(item)))].slice(0, 50);
  } catch { return []; }
}

/** Exact decimal multiplication: offer currency stays unchanged, with no implied FX rate. */
export function plannedRunCost(amount: string, runs: number): string | null {
  if (!Number.isInteger(runs) || runs < 1 || runs > 10000 || !/^\d{1,18}(\.\d{1,18})?$/.test(amount)) return null;
  const [whole, fraction = ""] = amount.split(".");
  const scale = BigInt(10) ** BigInt(fraction.length);
  const total = BigInt(whole + fraction) * BigInt(runs);
  const decimal = (total % scale).toString().padStart(fraction.length, "0").replace(/0+$/, "");
  return (total / scale).toString() + (decimal ? `.${decimal}` : "");
}
