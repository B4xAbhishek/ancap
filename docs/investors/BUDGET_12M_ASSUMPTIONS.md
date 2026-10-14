# ANCAP — 12-month operating budget (assumptions)

Date: 2026-10-14.  
Status: **planning draft for fundraising discussion**. Not a committed spend plan, not audited, and **not a valuation**.

## Purpose

Derive a funding ask from **costs and measurable milestones**, without inventing revenue, customers, partners, or company valuation. Owner still must confirm jurisdiction, headcount, and quotes.

## Currency and jurisdiction

| Item | Value | Source |
| --- | --- | --- |
| Planning currency | **EUR** | Assumption for cross-border discussion |
| Company seat | **Not chosen** (owner open) | Owner input required |
| Tax / VAT treatment | Unknown | Counsel after jurisdiction choice |

All EUR figures below are **assumptions** unless marked as a public list price. Local counsel / accountant quotes will replace them.

## Ask range (derived from budget)

| Scenario | 12-month cash need (EUR) | What it buys |
| --- | --- | --- |
| Lean core | **180,000–220,000** | Formation + 2 FT engineering + part-time ops/IR + infra + first audit slice + pilot budget |
| Standard release team | **320,000–420,000** | Formation + 4 FT (eng/QA/ops/sales) + fuller audit + LLM/infra + pilots |
| With reserve | **add 15–20%** | Working-capital buffer for delayed pilots / FX |

**Recommended discussion band until owner confirms jurisdiction:** **€250,000–€400,000**, justified by the standard-team column below. Final ask = sum of confirmed quotes + reserve, tied to milestones in `/investors`.

## One-time (year 0) costs

| Line | Lean (EUR) | Standard (EUR) | Assumption / check |
| --- | --- | --- | --- |
| Company formation + registry | 1,500–4,000 | 2,500–8,000 | EU micro-entity / Estonian e-Residency / PL/CZ ranges vary; **get counsel quote** |
| Accounting setup + year-1 bookkeeping retainer (prepaid) | 1,200–3,000 | 2,400–6,000 | Local accountant |
| Legal: terms/privacy refresh + commercial review | 3,000–8,000 | 6,000–15,000 | Counsel quote |
| Independent security review (app + wallet surface) | 8,000–15,000 | 15,000–35,000 | Scope in `docs/DEVELOPER_HANDOFF_RU.md`; **quote required** |
| Brand / investor deck production | 1,000–3,000 | 2,000–5,000 | Optional |
| **Subtotal one-time** | **≈15k–33k** | **≈28k–69k** | |

## Monthly run-rate (×12)

| Line | Lean / mo (EUR) | Standard / mo (EUR) | Assumption / check |
| --- | --- | --- | --- |
| Founding eng / product (1) | 4,500–6,500 | 5,000–7,500 | Contractor or employee; employer taxes extra if employed |
| Second eng / mobile-QA | — | 4,000–6,500 | |
| Ops / support / IR (0.5–1.0) | 1,500–2,500 | 3,000–5,000 | Fundraising Advisor role exists as opening; salary TBD by owner |
| Sales / pilot lead (0.5–1.0) | 1,000–2,000 | 3,000–5,000 | Commission later; do not invent pipeline |
| Cloud / hosting / observability | 400–900 | 800–1,800 | Current prod stack + staging; meter LLM separately |
| LLM / API inference budget | 300–1,200 | 800–3,000 | Depends on paid-run volume; **not revenue** |
| Domains, email, SaaS tools | 150–350 | 250–600 | |
| Contingency (ops) | 300–600 | 500–1,000 | |
| **Monthly subtotal** | **≈8.2k–14k** | **≈17.4k–30.4k** | |
| **×12** | **≈98k–168k** | **≈209k–365k** | |

## Pilots / sales (year bag, not monthly)

| Line | Lean (EUR) | Standard (EUR) | Notes |
| --- | --- | --- | --- |
| Pilot customer discounts / credits (ACP treasury accounting) | 2,000–5,000 | 5,000–15,000 | ACP credits ≠ cash revenue |
| Travel / conferences (optional) | 0–3,000 | 3,000–10,000 | Only if owner prioritizes |
| Content / listing experiments | 500–2,000 | 2,000–6,000 | |

## Totals (illustrative)

| | Lean | Standard |
| --- | --- | --- |
| One-time | 15–33k | 28–69k |
| Run-rate ×12 | 98–168k | 209–365k |
| Pilots bag | 2.5–10k | 10–31k |
| **Cash need before reserve** | **≈116–211k** | **≈247–465k** |
| +15% reserve | **≈133–243k** | **≈284–535k** |

## Milestone mapping (use of funds)

1. **Release & verification** — eng/QA salaries + infra + security review slice; exit: paid path smoke green on fixed SHA, mobile evidence packet started.
2. **Paid pilots** — sales/ops time + pilot credits + LLM budget; exit: measured paid runs, delivery cost, refunds (no invented targets here).
3. **Repeatable distribution** — only after pilot metrics exist; expand creator tooling and sales capacity from remaining reserve.

## Explicit non-claims

- No projected revenue, ARR, LTV, or payback period.
- No customer logos or partner commitments.
- ACP / wACP balances are **not** company equity value.
- Figures will change after jurisdiction, employment law, and vendor quotes.

## Owner checklist before sending to an investor

1. Choose company country and entity type.
2. Replace assumption bands with quotes (formation, counsel, auditor, payroll).
3. Confirm headcount and contractor vs employee mix.
4. Set the final ask = confirmed budget + reserve; attach this file + demo script + proof of paid-path smoke.
