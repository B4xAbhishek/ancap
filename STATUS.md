# ANCAP Status

> Updated: 2026-10-14
> Fast truth: this is the shortest current status entry point.

## Current truth

**Investor presentation (local, 2026-10-14):** homepage/navigation regrouped around AI workflow commerce, six-area project portfolio, and `/investors` overview. No verified revenue/customer metrics or funding amount supplied. These presentation changes are not yet deployed and do not close mobile/security/paid-execution release checks. Next steps: `docs/CURSOR_INVESTOR_FINISH_RU.md`.

Presentation verification: production frontend build passed; portfolio/i18n/classification tests **3 passed**; Playwright investor presentation checks **6 passed** (five languages, filters, mobile width, research heroes and light theme). Screenshots: `tmp/investor-preview-2026-10-14/`.

ANCAP is **largely built**, but it is **not fully release-complete end-to-end**.

**Work-stop blockers: none.**

**Public GitHub:** source of truth is [`ancapcloud/ancap`](https://github.com/ancapcloud/ancap) (account rename from `dragoncattrx-hub`). Docs twin: [`ancapcloud/ancap-docs`](https://github.com/ancapcloud/ancap-docs). Live product: [ancap.cloud](https://ancap.cloud).

**Bridge doctrine:** **1 ACP ↔ 10 wACP** (cutover 2026-10-04). Fiction SKUs (teleport / Barsuk / dark-matter auction) retired from the public launch surface.

**ACP supply (2026-10-02):** wallet figures such as `1,532,370,736.69` / `2,538,291,192.32` ACP were not protocol issuance. **Regenesis v3 is live** on `ancap.cloud`: issued **210,000,000 ACP** hard cap. Details: `docs/ACP_SUPPLY_INCIDENT_2026-10-02.md`.

**ACP nodes (2026-10-13):** three peers on the same tip family (height **18**, tip `ab6bdd19…d018`): primary `https://acp1.ancap.cloud/rpc`, Oracle `http://152.67.79.206:8545/rpc`, local PC `:8545`. Plan: [`docs/ORACLE_CLOUD_ACP_NODE_PLAN.md`](docs/ORACLE_CLOUD_ACP_NODE_PLAN.md). DNS/TLS `acp2.ancap.cloud` still open.

**ACP “mining” clarification:** there is **no PoW mining pool**. The lean-chain miner is a fee-packed block assembler (see `docs/ACP_LEAN_CHAIN.md`).

**Safe-launch controls (2026-09-28):** auth cookie `SameSite=Lax` + prod CORS; free ACP 1M cap; anti-sybil; Terms §3 residency draft pending counsel.

Active remaining work (not blockers):
1. **ACP mobile wallet** — device-ready release (Play/TestFlight, physical sign-off, iOS native).
2. **Open-source follow-through** — `ancap-docs` Discussions pin/category UI. Root `README.md` is present — do not report it missing. Boundaries: `docs/OPEN_SOURCE_GITHUB_TRANSPARENCY.md`.
3. **Monetization depth** — optional conversion/LTV; Stripe 4.1 is operator live verification only. Do **not** report “monetization after the first ACP cycle” as a blocker.

Security / CI / prod-hardening baseline closed in the **2026-07-01** wave (`docs/SECURITY_CLOSURE_EVIDENCE_2026-07-01.md`); external upstream key revoke audit remains operator-open, not a freeze.

Theodore / progress bots: do **not** report missing `README.md`. Do **not** report monetization after the first ACP cycle as a work-stop blocker.

**2026-07-01 hardening:** see `MASTER_ROADMAP.md` § Hardening + deploy wave and `docs/SECURITY_CLOSURE_EVIDENCE_2026-07-01.md` for deploy/CI/security closure evidence.

Active trust/adoption track running alongside those priorities:
- **GitHub-first open-source transparency**, where public-safe components become easier to audit, integrate, and contribute to, while keys, bridge signer operations, deploy secrets, and sensitive infrastructure stay private.
- the public docs repo at `https://github.com/ancapcloud/ancap-docs` is now live with the exported seed bundle pushed, Docs CI green on `main`, checked-in repo settings / labels / milestones applied, and default-branch protection live.
- the repeatable live follow-up path is `python scripts/generate_ancap_docs_live_followup.py --repo ancapcloud/ancap-docs`; by default it writes the dated artifact pair plus the stable latest aliases `tmp/ancap-docs-live-follow-up-latest.md` and `tmp/ancap-docs-live-follow-up-latest.json`, treats custom `--basename` / `--date-label` values as filename components instead of path fragments so writes stay inside `--output-dir`, `--fail-on-not-ok` exits with code `2` when unresolved live drift remains, and the wrapper's default terminal summary now also surfaces per-scope drift counts plus grouped manual follow-up totals from `driftSummary` / `manualFollowUpSummary` so cron/CI logs can be triaged without reopening the saved JSON artifact.
- current honest live drift is still manual GitHub admin/auth follow-through: extra `General` / `Polls` categories still exist, the seeded `Announcements` / `Ideas` / `Q&A` / `Show and tell` category descriptions still need the checked-in ANCAP wording, the seeded bootstrap discussions still need pinning, project-board seeding/verification is still blocked until GitHub auth includes `read:project`, and the later org-ownership decision/migration is still pending.

## Read this next

1. **Execution source of truth:** [MASTER_ROADMAP.md](MASTER_ROADMAP.md)
2. **Compact status matrix:** [docs/STATUS_MATRIX.md](docs/STATUS_MATRIX.md)
3. **Supporting product snapshot:** [PRODUCTION_ROADMAP.md](PRODUCTION_ROADMAP.md)
4. **Detailed mobile tracker:** [docs/mobile/ROADMAP.md](docs/mobile/ROADMAP.md)
5. **Monetization strategy context:** [ROADMAP-MONETIZATION.md](ROADMAP-MONETIZATION.md)
6. **Historical architecture roadmap:** [ROADMAP.md](ROADMAP.md)

## Rule

If any document conflicts with `MASTER_ROADMAP.md`, trust `MASTER_ROADMAP.md`.
