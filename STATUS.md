# ANCAP Status

> Updated: 2026-10-02
> Fast truth: this is the shortest current status entry point.

## Current truth

ANCAP is **largely built**, but it is **not fully release-complete end-to-end**.

**Work-stop blockers: none.**

**ACP supply (2026-10-02):** wallet figures such as `1,532,370,736.69` / `2,538,291,192.32` ACP were not protocol issuance. Replay of v2 heights 1–33,962 found genesis 210M + 56,537.05 synthetic validator + 622,130,939.999991 double-spend inflation = **832,187,477.05255227** unspent ACP. The UI also mixed stale UTXO-index rows across chain resets. **Regenesis v3 is live** on `ancap.cloud`: `gettxoutsetinfo` reports issued **210,000,000 ACP**, invariant ok, UTXO supply **209,999,999.999989** after 0.000011 ACP fees, height 12, genesis `78be2f72e8cf3bb41b0baa6fead9b40eb58be2f57e6a21a026d08ae8e8f6d8ce`. Recovery: `scripts/regenesis-v3-hard-cap.sh` + `docs/ACP_SUPPLY_INCIDENT_2026-10-02.md`.

**ACP “mining” clarification:** there is **no PoW mining pool**. The lean-chain miner is a fee-packed block assembler (see `docs/ACP_LEAN_CHAIN.md`). Staking bootstrap emission is ledger staking, not hash mining. Do not market “mine ACP” as energy-intensive PoW.

**Safe-launch controls (2026-09-28):** auth cookie policy is `SameSite=Lax` with prod `CORS_ORIGINS`; free ACP distribution has a 1M cap kill-switch; registration anti-sybil quarantines free grants; Theodore promo script is visible/portable with no spend keys; Terms §3 has a residency draft pending counsel; wACP mint preflight script + MetaMask education page shipped.

Active remaining work (not blockers):
1. **ACP mobile wallet** — device-ready release (Play/TestFlight, physical sign-off, iOS native). Local Android test env is available.
2. **Open-source follow-through** — GitHub org naming/ownership; `ancap-docs` Discussions pin/category UI. Phase 1 community files including root `README.md` are **present**. Do not report “absence of README.md”. Public-safe vs private boundaries stay in `docs/OPEN_SOURCE_GITHUB_TRANSPARENCY.md` (secrets stay private; do not hide material token/risk facts).
3. **Monetization depth** — optional conversion/LTV after a **live** ACP-first loop. Stripe 4.1 is operator live verification only. Do **not** report “monetization after the first ACP cycle” as a blocker.
4. **New ACP node — Oracle Cloud Always Free (eu-zurich-1)** — **live secondary full node** (2026-10-02). Public IP `152.67.79.206`, JSON-RPC `http://152.67.79.206:8545/rpc`, tip matched primary regenesis v3 (height 12 / 210M). Shape today: Always Free `VM.Standard.E2.1.Micro` (Ampere A1 retry when OCI capacity returns). Plan: [`docs/ORACLE_CLOUD_ACP_NODE_PLAN.md`](docs/ORACLE_CLOUD_ACP_NODE_PLAN.md). DNS/TLS `acp2.ancap.cloud` still open.

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
