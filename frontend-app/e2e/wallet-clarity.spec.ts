import { test, expect, type Page } from "@playwright/test";

const ownAddress = "acp1" + "q".repeat(38);
const recipient = "acp1" + "p".repeat(38);
const balance = {
  address: ownAddress,
  acp: "30",
  primary_acp: "70",
  primary_kind: "platform_credits",
  on_chain_at_deposit_acp: "30",
  platform_ledger_acp: "70",
  withdrawable_now_acp: "20",
  reserved_total_acp: "10",
  balance_status: "live",
  probe_status: "live",
  units: "3000000000",
  view_mode: "user",
};

async function fixtures(
  page: Page,
  options: {
    guest?: boolean;
    expired?: boolean;
    unavailable?: boolean;
    historyError?: boolean;
    personalize?: boolean;
    operator?: boolean;
    pending?: boolean;
  } = {},
) {
  let personalized = false;
  const requests: { path: string; method: string; body: unknown }[] = [];
  await page.route("**/v1/**", async (route) => {
    const request = route.request(),
      path = new URL(request.url()).pathname;
    requests.push({
      path,
      method: request.method(),
      body: request.method() === "POST" ? request.postDataJSON() : null,
    });
    if (path.endsWith("/users/me"))
      return route.fulfill({
        status: options.guest ? 401 : 200,
        json: options.guest
          ? { detail: "Login" }
          : {
              id: "wallet-fixture-user",
              email: "wallet-ui@example.test",
              display_name: "Wallet fixture",
            },
      });
    if (options.expired && path.includes("/wallet/acp/"))
      return route.fulfill({
        status: 401,
        json: { detail: "Expired fixture session" },
      });
    if (path.endsWith("/deposit_address"))
      return route.fulfill({
        json: {
          address: ownAddress,
          needs_personalize: !!options.personalize && !personalized,
        },
      });
    if (path.endsWith("/hot/balance") || path.endsWith("/balance"))
      return options.unavailable
        ? route.fulfill({ status: 503, json: { detail: "Test unavailable" } })
        : route.fulfill({
            json: options.operator
              ? {
                  ...balance,
                  primary_acp: "210000000",
                  primary_kind: "chain_supply",
                  view_mode: "operator_hot",
                  withdrawable_now_acp: "5",
                }
              : balance,
          });
    if (path.endsWith("/transactions"))
      return options.historyError
        ? route.fulfill({ status: 503, json: { detail: "Test unavailable" } })
        : route.fulfill({ json: { items: [] } });
    if (path.endsWith("/personalize")) {
      personalized = true;
      return route.fulfill({
        json: {
          address: ownAddress,
          wallet_backup_mnemonic:
            "synthetic backup fixture - no real wallet secret",
        },
      });
    }
    if (path.endsWith("/withdraw"))
      return route.fulfill({
        json: options.pending
          ? { status: "pending", job_id: "fixture-job" }
          : { accepted: true, status: "completed", txid: "a".repeat(64) },
      });
    if (path.includes("/withdraw/jobs/"))
      return route.fulfill({
        status: 504,
        json: { detail: "Synthetic polling timeout" },
      });
    return route.fulfill({ json: { items: [] } });
  });
  return requests;
}

test.beforeEach(async ({ page, context }) => {
  await context.addCookies([
    {
      name: "ancap-lang",
      value: "en",
      url: test.info().project.use.baseURL as string,
    },
  ]);
  await page.addInitScript(() => {
    localStorage.setItem("ancap-lang-v3", "en");
    localStorage.setItem(
      "ancap_cookie_consent_v1",
      JSON.stringify({ necessary: true, analytics: false, marketing: false }),
    );
  });
});

test("guest sees a useful entry instead of a blank wallet", async ({
  page,
}) => {
  const requests = await fixtures(page, { guest: true });
  await page.goto("/wallet/acp#password-security");
  await expect(
    page.getByRole("heading", { name: "ACP Wallet", exact: true }),
  ).toBeVisible();
  await expect(
    page.getByRole("link", { name: "Sign in to your wallet" }),
  ).toHaveAttribute("href", "/login?next=%2Fwallet%2Facp%23password-security");
  expect(requests.some((r) => r.path.endsWith("/hot/balance"))).toBe(false);
});

test("balances stay separate and unrelated desks load only on request", async ({
  page,
}) => {
  const requests = await fixtures(page);
  await page.goto("/wallet/acp");
  const hero = page.getByRole("region", { name: "Available to send" });
  await expect(hero).toContainText("20 ACP");
  await expect(
    page.getByText("Workflow credits", { exact: true }).first(),
  ).toBeVisible();
  await page.screenshot({
    path: test.info().outputPath("wallet-overview.png"),
    fullPage: false,
  });
  expect(
    requests.some((r) => /swap\/orders|otc|assay|ownership/.test(r.path)),
  ).toBe(false);
  await page
    .getByRole("button", { name: "Receive", exact: true })
    .first()
    .click();
  await expect(page.locator("main code").first()).toHaveText(ownAddress);
  await expect(page.getByText(/BSC wACP and USDT require/)).toBeVisible();
});

test("max deducts fee and review does not send until explicitly confirmed", async ({
  page,
}) => {
  const requests = await fixtures(page);
  await page.goto("/wallet/acp");
  await expect(
    page.getByRole("region", { name: "Available to send" }),
  ).toContainText("20 ACP");
  await page.getByRole("button", { name: "Send", exact: true }).first().click();
  await page
    .getByLabel("Recipient ACP address", { exact: true })
    .fill(recipient);
  await page.getByRole("button", { name: "Max", exact: true }).click();
  await expect(
    page.getByRole("textbox", { name: /Amount \(ACP\)/ }),
  ).toHaveValue("19.999999");
  await page
    .getByRole("button", { name: "Review transfer", exact: false })
    .click();
  await expect(
    page.getByText("Total including fee", { exact: true }),
  ).toBeVisible();
  expect(requests.filter((r) => r.path.endsWith("/withdraw"))).toHaveLength(0);
  await page
    .getByLabel("Wallet password", { exact: true })
    .fill("synthetic-fixture-password");
  await page
    .getByRole("button", { name: "Confirm transfer", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "Submitted to the ACP network" }),
  ).toBeVisible();
  const writes = requests.filter((r) => r.path.endsWith("/withdraw"));
  expect(writes).toHaveLength(1);
  expect(writes[0].body).toEqual({
    to_address: recipient,
    amount_acp: "19.999999",
    fee_acp: "0.00000100",
    wallet_password: "synthetic-fixture-password",
  });
  await expect(page.locator('input[type="password"]')).toHaveCount(0);
});

test("network failures show unknown balance and an activity error", async ({
  page,
}) => {
  await fixtures(page, { unavailable: true, historyError: true });
  await page.goto("/wallet/acp");
  await expect(
    page.getByText("Some wallet data is unavailable. Refresh to try again."),
  ).toBeVisible();
  await expect(
    page.getByRole("region", { name: "Available to send" }),
  ).toContainText("— ACP");
  await page
    .getByRole("button", { name: "Activity", exact: true })
    .first()
    .click();
  await expect(page.locator("main").getByRole("alert")).toContainText(
    "Activity could not be loaded",
  );
  await expect(
    page.getByText("No transfers found for this address."),
  ).toHaveCount(0);
});

test("operator totals cannot look like a personal available balance", async ({
  page,
}) => {
  await fixtures(page, { operator: true });
  await page.goto("/wallet/acp");
  await expect(
    page.getByRole("region", { name: "Available to send" }),
  ).toContainText("5 ACP");
  await expect(
    page.getByRole("region", { name: "Available to send" }),
  ).not.toContainText("210,000,000");
  await expect(
    page.getByText(/These totals are not a personal spendable balance/),
  ).toBeVisible();
});

test("backup remains visible after an address is personalized", async ({
  page,
}) => {
  await fixtures(page, { personalize: true });
  await page.goto("/wallet/acp#receive");
  await expect(
    page.getByRole("button", { name: "Personalize wallet", exact: true }),
  ).toBeVisible();
  await page
    .getByLabel("Wallet password", { exact: true })
    .fill("synthetic-fixture-password");
  await page
    .getByRole("button", { name: /personal|личный|individual/i })
    .click();
  await expect(
    page.getByText("synthetic backup fixture - no real wallet secret"),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "I saved it securely; hide", exact: true })
    .click();
  await expect(
    page.getByText("synthetic backup fixture - no real wallet secret"),
  ).toHaveCount(0);
});

test("mobile wallet fits without horizontal overflow", async ({ page }) => {
  await fixtures(page);
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/wallet/acp");
  await expect(
    page.getByRole("region", { name: "Available to send" }),
  ).toContainText("20 ACP");
  for (const section of [
    "Receive",
    "Send",
    "Activity",
    "Security",
    "More services",
  ]) {
    await page
      .getByRole("button", { name: section, exact: true })
      .first()
      .click();
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    ).toBe(true);
  }
});

test("a queued transfer can be checked after a polling error without sending again", async ({
  page,
}) => {
  const requests = await fixtures(page, { pending: true });
  await page.goto("/wallet/acp#send");
  await page
    .getByLabel("Recipient ACP address", { exact: true })
    .fill(recipient);
  await page.getByRole("textbox", { name: /Amount \(ACP\)/ }).fill("1");
  await page
    .getByRole("button", { name: "Review transfer", exact: false })
    .click();
  await page
    .getByLabel("Wallet password", { exact: true })
    .fill("synthetic-fixture-password");
  await page
    .getByRole("button", { name: "Confirm transfer", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "Transfer status needs checking" }),
  ).toBeVisible();
  await expect(page.getByText("ID: fixture-job")).toBeVisible();
  await page
    .getByRole("button", { name: "Check transfer status", exact: true })
    .click();
  await expect
    .poll(
      () => requests.filter((r) => r.path.includes("/withdraw/jobs/")).length,
    )
    .toBe(2);
  expect(requests.filter((r) => r.path.endsWith("/withdraw"))).toHaveLength(1);
});

test("an expired session clears wallet details", async ({ page }) => {
  await fixtures(page, { expired: true });
  await page.goto("/wallet/acp");
  await expect(
    page.getByRole("link", { name: "Sign in to your wallet", exact: true }),
  ).toBeVisible();
  await expect(
    page.getByRole("region", { name: "Available to send" }),
  ).toHaveCount(0);
  await expect(page.getByText(ownAddress, { exact: true })).toHaveCount(0);
});
