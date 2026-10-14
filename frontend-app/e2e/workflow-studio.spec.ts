import { test, expect } from "@playwright/test";

const owner = "11111111-1111-4111-8111-111111111111";
const project = { id: "22222222-2222-4222-8222-222222222222", owner_user_id: owner, members: {}, name: "Agency", context: { text: "Brand evidence" }, retention_days: 30 };

test.beforeEach(async ({ page, context }) => {
  await context.addCookies([{ name: "ancap-lang", value: "en", url: test.info().project.use.baseURL as string }]);
  await page.addInitScript(() => {
    localStorage.setItem("ancap-lang-v3", "en");
    localStorage.setItem("ancap_cookie_consent_v1", JSON.stringify({ necessary: true, analytics: false, marketing: false }));
  });
});

test("Studio explains authentication and mobile has no horizontal overflow", async ({ page }) => {
  await page.route("**/v1/users/me", route => route.fulfill({ status: 401, json: { detail: "Sign in" } }));
  await page.route("**/v1/workflow-ops/capabilities", route => route.fulfill({ json: { workflow_slugs: ["token-listing-pack"] } }));
  await page.route("**/v1/workflow-store/templates", route => route.fulfill({ json: { items: [{ slug: "token-listing-pack", title: "Listing pack", price: { amount: "10", currency: "ACP" } }] } }));
  await page.setViewportSize({ width: 390, height: 844 });
  const errors: string[] = [];
  page.on("pageerror", error => errors.push(error.message));
  await page.goto("/ai/studio");
  await expect(page.getByRole("heading", { name: "Workflow Studio", exact: true })).toBeVisible();
  await expect(page.getByRole("link", { name: "Sign in to use the workspace" })).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await page.goto("/docs/workflow-operations");
  await expect(page.getByRole("link", { name: "Download Python example" })).toHaveAttribute("href", /ancap-workflow-example\.py$/);
  expect(errors).toEqual([]);
});

test("import preserves step inputs and extra context; publishing alone cannot spend", async ({ page }) => {
  const definition = { name: "Agency report", project_id: project.id, steps: [{ slug: "token-listing-pack", inputs: { audience: "Founders" } }], inputs: { project_name: "Agency", task_description: "Review context", custom_field: "Keep me" }, coin_ids: [], require_review: true, connection_ids: [], provider_connection_id: null, test_cases: [] };
  const automation = { id: "33333333-3333-4333-8333-333333333333", owner_user_id: owner, project_id: project.id, name: definition.name, versions: [{ version: 1, definition, hash: "fixture" }], published_version: 1, enabled: false, interval_minutes: 1440, monthly_budget_acp: "0", spent_acp: "0" };
  const writes: unknown[] = [];
  await page.route("**/v1/**", async route => {
    const path = new URL(route.request().url()).pathname;
    if (path.endsWith("/users/me")) return route.fulfill({ json: { id: owner, email: "ui-fixture@example.test", display_name: "UI fixture" } });
    if (path.endsWith("/workflow-ops/capabilities")) return route.fulfill({ json: { workflow_slugs: ["token-listing-pack"] } });
    if (path.endsWith("/workflow-store/templates")) return route.fulfill({ json: { items: [{ slug: "token-listing-pack", title: "Listing pack", price: { amount: "10", currency: "ACP" } }] } });
    if (path.endsWith("/workflow-ops")) return route.fulfill({ json: { user_id: owner, is_operator: false, projects: [project], connections: [], automations: [automation], runs: [] } });
    if (route.request().method() === "POST") { writes.push(route.request().postDataJSON()); return route.fulfill({ json: automation }); }
    return route.fulfill({ json: { items: [] } });
  });
  await page.goto("/ai/studio");
  await page.getByRole("button", { name: "Builder", exact: true }).click();
  await page.getByRole("button", { name: "Agency report", exact: true }).click();
  await expect(page.getByRole("button", { name: "Queue paid run", exact: true })).toBeDisabled();
  await page.getByLabel("Import workflow plan", { exact: true }).setInputFiles({ name: "plan.json", mimeType: "application/json", buffer: Buffer.from(JSON.stringify({ format: "ancap-workflow-plan/v1", definition })) });
  await expect(page.getByRole("button", { name: "Save", exact: true })).toBeEnabled();
  await page.getByRole("button", { name: "Save", exact: true }).click();
  await expect.poll(() => writes.length).toBe(1);
  const saved = writes[0] as typeof definition;
  expect(saved.steps[0].inputs.audience).toBe("Founders");
  expect(saved.inputs.custom_field).toBe("Keep me");
  expect(saved.require_review).toBe(true);
});
