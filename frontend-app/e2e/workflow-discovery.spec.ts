import { test, expect } from "@playwright/test";

test.beforeEach(async ({ page, context }) => {
  await context.addCookies([{ name: "ancap-lang", value: "en", url: test.info().project.use.baseURL as string }]);
  await page.addInitScript(() => {
    localStorage.setItem("ancap-lang-v3", "en");
    localStorage.setItem("ancap_cookie_consent_v1", JSON.stringify({ necessary: true, analytics: false, marketing: false }));
  });
});

test("task matching, shortlist persistence, exact budget and downloadable comparison", async ({ page }) => {
  await page.goto("/ai/workflows");
  const discovery = page.locator('[aria-labelledby="discovery-title"]');
  await discovery.getByRole("button", { name: "Review token risks", exact: true }).click();
  const firstOffer = discovery.locator("article").first();
  await firstOffer.getByRole("button", { name: "Save", exact: true }).click();
  await expect(firstOffer.getByRole("button", { name: "Saved", exact: true })).toHaveAttribute("aria-pressed", "true");
  await firstOffer.getByRole("button", { name: "Compare", exact: true }).click();
  await expect(discovery.getByRole("heading", { name: "Compare deliverables and cost" })).toBeVisible();
  await discovery.getByRole("spinbutton", { name: "Planned runs per month" }).fill("3");
  const downloadEvent = page.waitForEvent("download");
  await discovery.getByRole("button", { name: "Download comparison" }).click();
  const download = await downloadEvent;
  expect(download.suggestedFilename()).toBe("ancap-workflow-comparison.json");
  const stream = await download.createReadStream();
  const chunks: Buffer[] = [];
  if (stream) for await (const chunk of stream) chunks.push(Buffer.from(chunk));
  const data = JSON.parse(Buffer.concat(chunks).toString());
  expect(data.planned_runs).toBe(3);
  expect(data.workflows).toHaveLength(1);
  expect(data.workflows[0].planned_cost.currency).toBe(data.workflows[0].price_per_run.currency);
  await page.reload();
  const savedSection = discovery.locator("details");
  await savedSection.locator("summary").click();
  await expect(savedSection.getByRole("button", { name: "Saved", exact: true })).toBeVisible();
  await savedSection.getByRole("button", { name: "Clear shortlist", exact: true }).click();
  await expect(savedSection.getByText("Save an offer to revisit it here.")).toBeVisible();
});

test("invalid run count disables export and mobile layouts stay usable", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/ai/workflows");
  const discovery = page.locator('[aria-labelledby="discovery-title"]');
  await discovery.getByRole("button", { name: "Prepare a listing", exact: true }).click();
  await discovery.locator("article").first().getByRole("button", { name: "Compare", exact: true }).click();
  await discovery.getByRole("spinbutton").fill("0");
  await expect(discovery.getByRole("alert")).toHaveText("Enter a whole number from 1 to 10,000.");
  await expect(discovery.getByRole("button", { name: "Download comparison" })).toBeDisabled();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
});

test("investor evidence links identify a recorded test demonstration", async ({ page }) => {
  await page.goto("/investors");
  const evidence = page.locator('[aria-labelledby="demo-evidence-title"]');
  await expect(evidence.getByText("Local demo · test credits")).toBeVisible();
  await expect(evidence.getByRole("link", { name: "Inspect receipt" })).toHaveAttribute("href", /588ebb765c6ec1e62d39dbc206bc8c0f9e177bcc.*receipt.json$/);
  await expect(evidence.getByText(/Customer revenue, production-provider acceptance/)).toBeVisible();
});
