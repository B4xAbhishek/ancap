import { test, expect } from "@playwright/test";

test("public presentation explains the workflow product in five languages", async ({ page, context }) => {
  const languages = [
    ["en", "Turn expertise into paid AI workflows."],
    ["ru", "Превращайте экспертизу в платные AI-workflow."],
    ["uk", "Перетворюйте експертизу на платні AI-workflow."],
    ["de", "Expertise in bezahlte KI-Workflows verwandeln."],
    ["zh-Hant", "將專業知識轉化為付費 AI 工作流程。"],
  ];
  for (const [lang, heading] of languages) {
    await context.addCookies([{ name: "ancap-lang", value: lang, url: test.info().project.use.baseURL as string }]);
    await page.addInitScript(value => localStorage.setItem("ancap-lang-v3", value), lang);
    await page.goto("/");
    await expect(page.getByRole("heading", { level: 1 })).toHaveText(heading);
    await expect(page.getByLabel("Локальное время, погода AccuWeather и поддержка")).toHaveCount(0);
  }
});

test("investor and portfolio pages avoid the old completion claim", async ({ page, context }) => {
  await context.addCookies([{ name: "ancap-lang", value: "en", url: test.info().project.use.baseURL as string }]);
  await page.addInitScript(() => localStorage.setItem("ancap-lang-v3", "en"));
  await page.goto("/projects");
  await expect(page.locator("main article")).toHaveCount(6);
  await expect(page.getByText("Final delivery complete — all roadmap waves shipped")).toHaveCount(0);
  await expect(page.locator('main a[href="/aeterna"]')).toBeVisible();
  await page.goto("/investors");
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("A focused platform for AI workflow commerce");
  await expect(page.getByText(/metrics have not been supplied/)).toBeVisible();
  await expect(page.locator('main a[href="/proof-center"]')).toBeVisible();
});

test("catalog filters offers and has a usable empty state", async ({ page, context }) => {
  await context.addCookies([{ name: "ancap-lang", value: "en", url: test.info().project.use.baseURL as string }]);
  await page.addInitScript(() => localStorage.setItem("ancap-lang-v3", "en"));
  await page.goto("/ai/workflows");
  const search = page.getByRole("searchbox", { name: "Search workflows" });
  await search.fill("no-such-workflow-6d90");
  await expect(page.getByText("No matching workflows. Try another search.")).toBeVisible();
  await expect(page.locator("main article")).toHaveCount(0);
  await search.fill("");
  await page.getByRole("combobox", { name: "Solutions", exact: true }).selectOption("life");
  await expect(page.locator("#catalog-life")).toBeVisible();
  await expect(page.locator("#catalog-crypto")).toHaveCount(0);
});

test("mobile presentation keeps content within the viewport", async ({ page, context }) => {
  await context.addCookies([{ name: "ancap-lang", value: "ru", url: test.info().project.use.baseURL as string }]);
  await page.addInitScript(() => localStorage.setItem("ancap-lang-v3", "ru"));
  await page.setViewportSize({ width: 390, height: 844 });
  for (const route of ["/", "/projects", "/investors"]) {
    await page.goto(route);
    await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth);
    expect(overflow, route).toBe(false);
    const brand = await page.locator('header a[href="/"]').boundingBox();
    const languages = await page.getByRole("radiogroup", { name: "Language" }).boundingBox();
    expect(brand && languages && brand.x + brand.width <= languages.x, "brand and language controls should not overlap").toBe(true);
  }
});

test("research project heroes describe briefs instead of physical capabilities", async ({ page, context }) => {
  await context.addCookies([{ name: "ancap-lang", value: "en", url: test.info().project.use.baseURL as string }]);
  await page.addInitScript(() => localStorage.setItem("ancap-lang-v3", "en"));
  for (const route of ["/aeterna", "/cryo", "/saliva-rx", "/galaxy", "/lunar", "/stardust"]) {
    await page.goto(route);
    await expect(page.getByRole("heading", { level: 1 })).toContainText("Research briefs");
  }
});

test("the investor overview supports the light theme", async ({ page, context }) => {
  await context.addCookies([{ name: "ancap-lang", value: "en", url: test.info().project.use.baseURL as string }]);
  await page.addInitScript(() => {
    localStorage.setItem("ancap-lang-v3", "en");
    localStorage.setItem("ancap-theme-v1", "light");
  });
  await page.goto("/investors");
  await expect(page.locator("html")).toHaveClass(/light/);
  await expect(page.getByRole("heading", { level: 1 })).toHaveCSS("color", "rgb(15, 23, 42)");
});
