# ANCAP — 5-minute investor demo script

Date: 2026-10-14.  
**Samples and UI walks are not paid production runs** unless you explicitly show a test-ledger receipt from the smoke path.

## Prep (before the call)

1. Local or staging frontend on a fixed commit (record SHA).
2. Backend with test ACP credits deposit enabled (ledger deposit — **no real Stripe / no chain broadcast**).
3. Open tabs: `/`, `/ai/workflows`, sample report, `/dashboard/seller` (or creators), `/investors`.
4. Have `docs/investors/BUDGET_12M_ASSUMPTIONS.md` ready; do not invent revenue.

## Minute-by-minute

| Time | Screen | Say / show |
| --- | --- | --- |
| 0:00–0:40 | `/` | ANCAP sells **defined AI workflow outputs**. Customer pays ACP → run → artifact + receipt. Creators earn on paid runs; platform takes a fee. ACP is settlement, not valuation. |
| 0:40–1:30 | `/ai/workflows` | Initial commercial focus: crypto launch / risk / growth. Filter other areas. Point at **Token Risk Report** (or Listing Pack). Note fallback banner if catalog is offline. |
| 1:30–2:30 | Sample or live test run | Prefer **illustrative** sample: `/sample-reports/token-risk-report-pro`. If showing a live test: register → credits deposit → create run → pay with credits → execute → open run receipt. Label it **test ledger**, not a customer sale. |
| 2:30–3:10 | Receipt / proof | Show run receipt fields: price snapshot, status, payment proof. Clarify: receipt records execution; it does **not** certify factual accuracy of the AI text. |
| 3:10–3:50 | `/dashboard/seller` or creators | Creator packaging: build once, sell repeatable runs. Do not claim live GMV. |
| 3:50–4:40 | `/investors` | Stage honesty: product implemented; release + commercial validation open. Metrics not supplied. Funding for formation, team, audit, pilots. Point to budget assumptions and ask band. |
| 4:40–5:00 | Ask | “We are raising to fund the 12-month plan in the budget memo — not a made-up valuation. Next proof: paid pilots with measured runs.” |

## Do not say

- Invented MRR, users, partners, or “fully released”.
- That research pages (AETERNA, weather, lunar, etc.) deliver physical medical/space/weather services.
- That ACP treasury balances are company revenue.

## Evidence to attach after the call

- Git SHA of the demo build.
- Screenshot set (optional): home, catalog, sample/result, receipt, investors.
- Result of `pytest tests/api/test_investor_paid_path_smoke.py -q` (test env).
