import { test, expect } from "@playwright/test";

test.describe("ANCAP Frontend - UI smoke", () => {
  test("home page renders core public surface", async ({ page }) => {
    const response = await page.goto("/", { waitUntil: "domcontentloaded" });

    expect(response?.status()).toBe(200);
    await expect(page).toHaveTitle(/ANCAP/i);
    await expect(page.locator("body")).toContainText(/ANCAP/i);

    const header = page.locator("header").first();
    await expect(header.getByRole("link", { name: /^login$/i }).first()).toBeVisible();
    await expect(header.getByRole("link", { name: /^register$/i }).first()).toBeVisible();
    await expect(header.locator('a[href="/investors"]').first()).toBeVisible();
  });

  test("public routes return success", async ({ page }) => {
    for (const path of [
      "/",
      "/projects",
      "/whitepaper",
      "/login",
      "/register",
      "/legal",
      "/legal/welcome-grant",
      "/legal/vet-regen",
      "/legal/light-chamber",
      "/legal/body-contouring",
      "/legal/biofusion",
      "/legal/dpsc",
      "/legal/vascular-care-plus",
      "/legal/vascular-care",
      "/legal/transdermal",
      "/legal/m-receptor",
      "/legal/oxygen-carrier",
      "/legal/synthetic-blood-mamba",
      "/legal/adhd-support",
      "/legal/down-syndrome-support",
      "/legal/substance-coding",
      "/legal/pulmopure",
      "/legal/barsuk",
      "/legal/teleport-earphones",
      "/legal/humanitarian",
      "/legal/tesla-coil-party",
      "/legal/antique-fire-restore",
      "/humanitarian",
      "/entertainment",
      "/aeterna",
      "/perimeter",
      "/antique-fire-restore",
    ]) {
      const response = await page.goto(path, { waitUntil: "domcontentloaded" });
      expect(response?.status(), `${path} status`).toBe(200);
      await expect(page.locator("body")).toBeVisible();
    }
  });

  test("language switcher is present and interactive", async ({ page }) => {
    const response = await page.goto("/", { waitUntil: "domcontentloaded" });
    expect(response?.status()).toBe(200);

    const ruButton = page.getByText(/^RU$/).first();
    await expect(ruButton).toBeVisible();
    await ruButton.click();
    await page.waitForTimeout(300);
    await expect(page.locator("body")).toContainText(/ANCAP/i);
  });
});
