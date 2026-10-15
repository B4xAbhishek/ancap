<p align="center">
  <a href="https://ancap.cloud"><img src="docs/assets/github/ancap-overview.svg" alt="ANCAP — build, run and deliver paid AI workflows" width="1200" /></a>
</p>

<h1 align="center">ANCAP</h1>
<p align="center"><strong>Build, buy and sell AI workflows — with ACP payments and execution receipts.</strong></p>
<p align="center">For teams that need repeatable AI work, creators who package it, and developers who integrate it.</p>

<p align="center">
  <a href="https://ancap.cloud/ai/workflows"><strong>Explore workflows</strong></a> ·
  <a href="https://ancap.cloud/ai/studio"><strong>Open Studio</strong></a> ·
  <a href="https://ancap.cloud/investors">For investors</a> ·
  <a href="https://github.com/ancapcloud/ancap-docs">Documentation</a>
</p>
<p align="center">
  <a href="https://github.com/ancapcloud/ancap/actions/workflows/backend-ci.yml"><img src="https://github.com/ancapcloud/ancap/actions/workflows/backend-ci.yml/badge.svg?branch=master" alt="Backend CI" /></a>
  <a href="https://github.com/ancapcloud/ancap/actions/workflows/docs-ci.yml"><img src="https://github.com/ancapcloud/ancap/actions/workflows/docs-ci.yml/badge.svg?branch=master" alt="Documentation checks" /></a>
  <a href="https://github.com/ancapcloud/ancap/actions/workflows/secret-hygiene.yml"><img src="https://github.com/ancapcloud/ancap/actions/workflows/secret-hygiene.yml/badge.svg?branch=master" alt="Secret hygiene checks" /></a>
</p>

## From a request to a paid result

**Choose a workflow → supply inputs → review the ACP quote → run → inspect the result and receipt.**

ANCAP packages AI work into defined offers: a buyer, a task, required inputs, an output,
limitations and a price. Creators can publish workflow versions; users can run them;
teams can add context, review results and connect delivery tools.

**For users.** Find a workflow for a concrete task, understand its inputs and cost,
and keep the result with its execution record. Start with [the workflow catalog](https://ancap.cloud/ai/workflows).

**For creators and teams.** Build sequential workflows in [Studio](https://ancap.cloud/ai/studio),
save versions, set spending limits, schedule runs and review output before delivery.
Publishing alone does not start a paid run.

**For developers.** Integrate through the API, work with execution receipts and use
[public examples](examples/README.md). Connector accounts and provider keys are supplied
by the customer; availability depends on configuration.

## Explore the product

- **[Workflow catalog](https://ancap.cloud/ai/workflows)** — defined tasks, inputs, outputs and ACP pricing.
- **[Workflow Studio](https://ancap.cloud/ai/studio)** — versions, context, review, schedules and bounded execution.
- **[ACP wallet](https://ancap.cloud/wallet/acp)** — separate balances, receive/send, fee review and activity.
- **[Developer hub](https://ancap.cloud/developers)** — API and integration entry points.
- **[Investor overview](https://ancap.cloud/investors)** — product, business model and planned company structure.

The web interface supports **English, Русский, Українська, Deutsch and 繁體中文**.

## What is verified

The latest documented release checks include **907 backend tests, 54 frontend tests
and 38 browser scenarios passed**. These are dated release results, not a promise
about every future commit. CI badges above show the latest checks for `master`.

- [Workflow operations release](docs/WORKFLOW_OPERATIONS_RELEASE_2026-10-15.md) — implementation, verification and integration limits.
- [Wallet usability release](docs/WALLET_UX_RELEASE_2026-10-15.md) — balance clarity, reviewed transfers and read-only production checks.
- [Live LLM demonstration evidence](docs/investors/evidence/2026-10-14-local-ollama/README.md) — recorded execution with test credits and a local model.
- [Current status](STATUS.md) · [Execution roadmap](MASTER_ROADMAP.md) · [Status matrix](docs/STATUS_MATRIX.md).

Test credits and fixtures are identified in the evidence. They do not establish
customer revenue or live chain settlement. Native mobile release checks remain
open; research concepts and partner-assisted desks are distinct from executable
AI workflows. See the linked release notes for remaining limitations.

## Find your way around the code

- [`frontend-app/`](frontend-app/) — Next.js, React and TypeScript web interface.
- [`app/`](app/) and [`alembic/`](alembic/) — FastAPI services, workflow execution, ledger and database migrations.
- [`ACP-crypto/`](ACP-crypto/README.md) — Rust ACP chain, wallet and mobile FFI sources.
- [`ancap-mobile/`](ancap-mobile/README.md) — Expo / React Native wallet and shared packages.
- [`contracts/bridge-bsc/`](contracts/bridge-bsc/README.md) — wACP bridge contract sources and tests.
- [`docs/`](docs/) and [`examples/`](examples/README.md) — architecture, operations and public integration samples.

ACP is the platform accounting/payment unit. Native ACP, wrapped wACP and internal
workflow credits have different roles; [the wallet](https://ancap.cloud/wallet/acp)
keeps the balances separate. Chain and bridge infrastructure supports the product;
it is not a claim of investment returns.

## Build with us

Read [CONTRIBUTING.md](CONTRIBUTING.md) for the development flow and
[FRONTEND.md](FRONTEND.md) for frontend setup. Start with a focused change and run
the checks relevant to it. Database tests require a disposable test database.

[Report a bug](https://github.com/ancapcloud/ancap/issues/new?template=bug_report.md) ·
[Suggest a feature](https://github.com/ancapcloud/ancap/issues/new?template=feature_request.md) ·
[Read the security policy](SECURITY.md) · [Repository license terms](LICENSE)

Never post keys, seed phrases, keystores or production credentials in issues or pull requests.

---

<details>
<summary><strong>Advanced reference — operators, architecture and historical implementation notes</strong></summary>

This reference preserves existing documentation and automation contracts. For current
release scope, use the dated evidence and status links above; older milestone notes
describe their original implementation stage.

### Operator / CI documentation contracts

The human landing above is intentional. The following links and phrasing are retained so repo truth tests and operator runbooks stay machine-checkable:

**Open-source / GitHub transparency track:** [docs/OPEN_SOURCE_GITHUB_TRANSPARENCY.md](docs/OPEN_SOURCE_GITHUB_TRANSPARENCY.md) | **Docs split plan:** [docs/ANCAP_DOCS_SPLIT.md](docs/ANCAP_DOCS_SPLIT.md) | **Docs repo bootstrap:** [docs/ANCAP_DOCS_REPO_BOOTSTRAP.md](docs/ANCAP_DOCS_REPO_BOOTSTRAP.md) | **Docs contributor intake seed:** [docs/ANCAP_DOCS_CONTRIBUTOR_INTAKE_SEED.md](docs/ANCAP_DOCS_CONTRIBUTOR_INTAKE_SEED.md) | **Docs label seed:** [docs/ANCAP_DOCS_LABEL_SEED.md](docs/ANCAP_DOCS_LABEL_SEED.md) | **Docs Discussions seed:** [docs/ANCAP_DOCS_DISCUSSIONS_SEED.md](docs/ANCAP_DOCS_DISCUSSIONS_SEED.md) | **Docs milestone seed:** [docs/ANCAP_DOCS_MILESTONE_SEED.md](docs/ANCAP_DOCS_MILESTONE_SEED.md) | **Docs project-board seed:** [docs/ANCAP_DOCS_PROJECT_BOARD_SEED.md](docs/ANCAP_DOCS_PROJECT_BOARD_SEED.md) | **Docs initial issues seed:** [docs/ANCAP_DOCS_INITIAL_ISSUES_SEED.md](docs/ANCAP_DOCS_INITIAL_ISSUES_SEED.md) | **Docs repo settings seed:** [docs/ANCAP_DOCS_REPO_SETTINGS_SEED.md](docs/ANCAP_DOCS_REPO_SETTINGS_SEED.md) | **Docs update cadence seed:** [docs/ANCAP_DOCS_UPDATE_CADENCE_SEED.md](docs/ANCAP_DOCS_UPDATE_CADENCE_SEED.md) | **Docs CI seed:** [docs/ANCAP_DOCS_CI_SEED.md](docs/ANCAP_DOCS_CI_SEED.md) | **Docs Dependabot seed:** [docs/ANCAP_DOCS_DEPENDABOT_SEED.md](docs/ANCAP_DOCS_DEPENDABOT_SEED.md) | **CODEOWNERS seed:** [.github/CODEOWNERS](.github/CODEOWNERS) | **Machine-readable bootstrap seeds:** [.github/bootstrap/](.github/bootstrap/) (now including contributor-intake metadata, initial-issues metadata, copy-ready pinned-topic, update-post, CI metadata, the exported Docs CI workflow template that stays structurally aligned with the shipped workflow, and the docs-repo Dependabot template that the exported Docs CI guard keeps byte-for-byte aligned with the public `.github/dependabot.yml`) | **gh bootstrap helper:** [scripts/bootstrap_ancap_docs_repo.py](scripts/bootstrap_ancap_docs_repo.py) for repo creation/settings/labels/milestones/branch-protection seed application and live repo verification against the checked-in seeds | **Live follow-up wrapper:** [scripts/generate_ancap_docs_live_followup.py](scripts/generate_ancap_docs_live_followup.py) for paired markdown+JSON `ancap-docs` live verification artifacts (`tmp/ancap-docs-live-follow-up-YYYY-MM-DD.md` + `tmp/ancap-docs-live-follow-up-YYYY-MM-DD.json`), embedded artifact metadata (generator/bootstrap source, UTC generation time, generator repo HEAD provenance, dated outputs, and optional latest-alias paths), stable latest aliases (`tmp/ancap-docs-live-follow-up-latest.md` + `tmp/ancap-docs-live-follow-up-latest.json`) for follow-up automation/reporting, plus optional `--fail-on-not-ok` exit-code 2 drift alarms for cron/CI runs. Keep the dated outputs distinct from those stable aliases: if you want a custom `--date-label`, do not reuse `latest` unless you also pass `--no-write-latest-alias`, and keep custom `--basename` / `--date-label` values as plain filename components rather than path fragments so artifact writes stay inside the chosen `--output-dir`.

Roadmap history - [ROADMAP.md](ROADMAP.md). Vision - [docs/VISION.md](docs/VISION.md). **Architecture in 3 levels (L1/L2/L3)** - [docs/ARCHITECTURE_LAYERS.md](docs/ARCHITECTURE_LAYERS.md). **Plan “from zero to L3”** (step-by-step checklist and comparison with code) - [docs/PLAN_L0_TO_L3.md](docs/PLAN_L0_TO_L3.md). Reputation 2.0 - [docs/REPUTATION_2.md](docs/REPUTATION_2.md). **ANCAP v2 (AI-state): microservices catalog** - [docs/rfc/service-catalog.md](docs/rfc/service-catalog.md). Staking economics - [docs/STAKING.md](docs/STAKING.md).
Program delivery controls: [docs/DELIVERY_BOARD.md](docs/DELIVERY_BOARD.md), [docs/RISK_REGISTER.md](docs/RISK_REGISTER.md), [docs/AUDIT_CHECKLIST.md](docs/AUDIT_CHECKLIST.md).
AI and ISO governance notes: [docs/AI_ISO_GOVERNANCE_NOTES.md](docs/AI_ISO_GOVERNANCE_NOTES.md).
Project whitepaper: [docs/WHITEPAPER_PROJECT.md](docs/WHITEPAPER_PROJECT.md). ACP crypto-asset whitepaper: [docs/WHITEPAPER_ACP.md](docs/WHITEPAPER_ACP.md). Legal terms template: [docs/LEGAL_TERMS_TEMPLATE.md](docs/LEGAL_TERMS_TEMPLATE.md). Public changelog: [docs/CHANGELOG_PUBLIC.md](docs/CHANGELOG_PUBLIC.md). Secret rotation runbook: [docs/SECRET_ROTATION_RUNBOOK.md](docs/SECRET_ROTATION_RUNBOOK.md). Production secret baseline: [docs/PRODUCTION_SECRET_BASELINE.md](docs/PRODUCTION_SECRET_BASELINE.md). Secret scan helper: [scripts/check_secret_hygiene.py](scripts/check_secret_hygiene.py) (supports `--staged` for git-index-only pre-commit checks, `--history-range <rev-range>` for full-tree recent committed-history sweeps after cleanup/rotation so unchanged leaked files still surface anywhere inside that window and now fails with an explicit CLI validation error instead of a traceback when the supplied rev-range does not resolve in the current clone, `--recent-history <count>` for the same recent-window sweep without assuming `HEAD~N` exists in a small or shallow local clone, `--pending-push` for the exact commit history about to leave the workstation using the tracked branch upstream when that ref is still resolvable and otherwise falling back to `origin/HEAD..HEAD` or a recent-history window when no push base can be resolved, falls back to the git index for tracked-but-currently-missing paths so local deletions do not crash the default tracked-files scan, catches OpenAI project/service-account prefixes plus Anthropic/GitHub/Stripe/provider token-shaped patterns, plus `--format json --output tmp/secret-hygiene-report.json` for copy-safe evidence artifacts; the GitHub workflow path now also produces `tmp/secret-hygiene-history-report.json` for push/PR delta sweeps when GitHub supplies the commit SHAs and that rev-range still resolves in the checkout and otherwise falls back to clone-safe recent-history sweeps, scheduled clone-safe recent-history sweeps, manual blank-input recent-history sweeps, and tagged-release clone-safe recent-history evidence, now uploads those release-time artifacts before the final explicit secret-hygiene gate step so failures still keep the evidence bundle, and now renders and retains `tmp/secret-rotation-evidence.md` as the derived markdown incident worksheet artifact without depending on a default `HEAD~20..HEAD` manual input). Tagged-release automation now also drives that release-time tracked/history/markdown artifact set through the same one-shot helper used for local handoff instead of maintaining a separate inline workflow sequence. On Windows hosts that only expose the Python launcher, the same helper commands can be run as `py -3 scripts/check_secret_hygiene.py ...`, `py -3 scripts/render_secret_rotation_evidence.py ...`, and `py -3 scripts/generate_secret_hygiene_evidence.py ...` with the same arguments. Plus tracked local git-hook bootstrap via [scripts/install_git_hooks.py](scripts/install_git_hooks.py) so the staged-index pre-commit scan and the exact pending-push pre-push sweep can block token-shaped leaks before they leave the workstation. Those tracked hooks now resolve `python` first, then fall back to `python3`, then `py -3`, so the same bootstrap remains usable on Linux/macOS contributors that only expose `python3` on PATH and on Windows setups that rely on the Python launcher instead of a bare `python` shim. You can bootstrap the installer itself with either `python scripts/install_git_hooks.py` or `py -3 scripts/install_git_hooks.py`, and the same launcher-specific fallback works for the non-mutating verification path too (`python scripts/install_git_hooks.py --check` or `py -3 scripts/install_git_hooks.py --check`). That installer refuses to overwrite an existing custom `core.hooksPath` without `--force`, refuses to enable `.githooks` unless both tracked hook files are present, when the repo is already configured it just restores executable bits on those tracked hooks instead of rewriting config, and now also supports --check for a non-mutating verification that the local repo is already wired to the tracked hooks. For operator handoff after a suspected leak, [scripts/render_secret_rotation_evidence.py](scripts/render_secret_rotation_evidence.py) can turn the retained JSON scan artifacts into a copy-safe markdown incident worksheet, write `tmp/secret-rotation-evidence.md` without pasting raw terminal logs, accept either a history sweep or local pending-push JSON as the second artifact (`--history-report` or `--secondary-report`), and still refuses mismatched primary-vs-history/pending-push artifact pairs, repo-root drift, cross-checkout `head_commit` mismatches, or reused input/output file paths so the handoff bundle cannot be built from the wrong evidence inputs. Those JSON/markdown artifacts now also carry repo-HEAD provenance (`head_ref`, `head_commit`, dirty/clean working-tree state) so operator handoff can tie a scan bundle back to the exact checkout that produced it instead of only file/commit counts. When you want the primary scan, optional tracked+untracked or staged primary artifact, secondary history/pending-push scan, and markdown worksheet generated in one repeatable step, [scripts/generate_secret_hygiene_evidence.py](scripts/generate_secret_hygiene_evidence.py) now wraps that flow into a single command (add `--include-untracked` when local temp/export artifact coverage matters, or `--staged-primary` when the main evidence artifact should follow the staged index instead of the working tree). By default it writes `tmp/secret-hygiene-report.json`, `tmp/secret-hygiene-history-report.json`, and `tmp/secret-rotation-evidence.md`, and `--pending-push` switches that secondary artifact path to `tmp/secret-hygiene-pending-push-report.json`; it also refuses reused primary/secondary/output file paths before it starts writing artifacts, and returns non-zero if either scan finds token-shaped leaks.

## Current Status

- **Project state:** core platform is largely built, but **not fully release-complete end-to-end**.
- **GitHub:** [`ancapcloud/ancap`](https://github.com/ancapcloud/ancap) · docs [`ancapcloud/ancap-docs`](https://github.com/ancapcloud/ancap-docs) · product [ancap.cloud](https://ancap.cloud)
- **Bridge:** **1 ACP ↔ 10 wACP**. Public launch dropped fiction SKUs (teleport / Barsuk / dark-matter).
- **Biggest remaining tails:** ACP mobile wallet release closure, monetization depth, `acp2.ancap.cloud` DNS/TLS.
- **Parallel trust track:** public-safe components stay open; keys, bridge signer, deploy secrets, and hot-wallet ops stay private.
- **Current truth source:** [STATUS.md](STATUS.md), [MASTER_ROADMAP.md](MASTER_ROADMAP.md), [docs/STATUS_MATRIX.md](docs/STATUS_MATRIX.md) — trust these before older roadmap docs.

## Stripe / Fiat Credit Top-Up Adapter

ANCAP remains **ACP-first**. Stripe is an optional adapter for buying ANCAP credit packages without leaving the platform.

Current backend surfaces:
- `POST /v1/payments/stripe/intent` — create a Stripe PaymentIntent for a credit package and return the ANCAP payment-intent record plus Stripe client session data
- `GET /v1/payments/stripe/intents/{intent_id}` — poll owned Stripe-backed top-up intents and sync status if webhook delivery is delayed
- `GET /v1/payments/methods` — list saved Stripe card payment methods for the authenticated user
- `DELETE /v1/payments/methods/{payment_method_id}` — detach a saved Stripe payment method from the authenticated user
- `POST /v1/webhooks/stripe` — verify Stripe signatures, deduplicate events, and capture credit top-ups on `payment_intent.succeeded`

Required env vars for the adapter:
- `STRIPE_SECRET_KEY`
- `STRIPE_PUBLISHABLE_KEY`
- `STRIPE_WEBHOOK_SECRET`
- optional `STRIPE_API_BASE` (defaults to `https://api.stripe.com/v1`)

Current first-slice Stripe currencies:
- `USD`
- `EUR`

If those values are empty, Stripe endpoints fail closed with `503` and ACP/manual flows stay available. Unsupported Stripe currencies fail closed with `400` instead of silently creating mismatched checkout intents.

Manual verification checklist for the remaining roadmap gap: [docs/STRIPE_VERIFICATION_RUNBOOK.md](docs/STRIPE_VERIFICATION_RUNBOOK.md). Copy-ready evidence packet: [docs/STRIPE_VERIFICATION_EVIDENCE_TEMPLATE.md](docs/STRIPE_VERIFICATION_EVIDENCE_TEMPLATE.md). Use `python scripts/generate_stripe_verification_packet.py` to create the dated working copy for a specific verification round instead of editing the template header by hand; by default it also refreshes the stable alias `docs/stripe-verification-latest.md` unless `--no-write-latest-alias` is passed. After filling the packet, run `python scripts/check_stripe_verification_packet.py docs/stripe-verification-YYYY-MM-DD.md` (or omit the path to check `docs/stripe-verification-latest.md`) so the final closure claim stays machine-checked instead of relying on operator memory. Item 4.1 is not done until webhook-delivered capture and saved-card reuse are both verified against a real/test Stripe customer.

## Referral auto-payouts

Referral reward issuance is already live in the ledger. Optional ACP auto-payout execution is also wired for operators who want referral rewards pushed on-chain from a configured site wallet.

Runtime env vars for that path:
- `REFERRAL_ONCHAIN_PAYOUT_ENABLED` — set `true` to allow the jobs tick to process queued referral payout jobs
- `REFERRAL_ONCHAIN_PAYOUT_KEYSTORE_FILE` — path to the ACP wallet keystore used for on-chain referral payouts
- optional `REFERRAL_ONCHAIN_PAYOUT_FEE_ACP` — explicit ACP fee override passed to the wallet helper
- `ACP_WALLETD_PATH` / `walletd` in `PATH` and a valid `ACP_RPC_URL` are also required when auto-payouts are enabled

If those values are unset, referral rewards still accrue in the internal ledger and the payout queue stays fail-closed / idle.

## Public integration examples

Contributor-friendly index: [docs/PUBLIC_INTEGRATION_EXAMPLES.md](docs/PUBLIC_INTEGRATION_EXAMPLES.md)

Public-safe reference integrations live under [`examples/`](examples/README.md):

- [`examples/payment-integration/python_credit_topup.py`](examples/payment-integration/python_credit_topup.py) — create and poll a Stripe-backed ANCAP credit top-up intent
- [`examples/wallet-connection/python_wallet_login.py`](examples/wallet-connection/python_wallet_login.py) — request a wallet auth challenge, sign it locally, verify it, and fetch `/v1/users/me`

These are intentionally minimal examples for the GitHub transparency / open-integration track and do not expose private operator infrastructure.

## wACP public contract source

The public bridge contract sources are in [`contracts/bridge-bsc/`](contracts/bridge-bsc/README.md):

- [`contracts/bridge-bsc/src/WACP.sol`](contracts/bridge-bsc/src/WACP.sol)
- [`contracts/bridge-bsc/src/BridgeGateway.sol`](contracts/bridge-bsc/src/BridgeGateway.sol)

See [`contracts/bridge-bsc/README.md`](contracts/bridge-bsc/README.md) for Foundry test and deployment instructions.

Additional public bridge/audit docs:
- [docs/BRIDGE_RISK_DOCUMENTATION.md](docs/BRIDGE_RISK_DOCUMENTATION.md)
- [docs/OFFICIAL_CONTRACT_ADDRESSES.md](docs/OFFICIAL_CONTRACT_ADDRESSES.md)
- [docs/CONTRACT_VERIFICATION_GUIDE.md](docs/CONTRACT_VERIFICATION_GUIDE.md)
- [docs/TESTNET_DEPLOYMENT_GUIDE.md](docs/TESTNET_DEPLOYMENT_GUIDE.md)

## Roadmap-Aligned Milestones (Current State)

- **Public governance surface:** delivered in production (proposal lifecycle, audit trail, moderation hooks).
- **On-chain settlement paths:** delivered (settlement intents, stake/slash flows, chain receipts).
- **Anti-sybil reinforcement:** delivered (stake + Reputation 2.0 + graph gates on core operations).
- **Autonomous operations layer:** delivered (NOC, AI council workflows, explainable decision logs).
- **ACP tokenomics and distribution (active governance track):** fixed supply and transparent allocation model are documented and aligned with protocol constants.

## ACP Tokenomics Snapshot

- **Total base supply:** `210,000,000 ACP`.
- **Genesis allocation:**
  - Creator: `69,300,000 ACP (33%)`
  - Validator Reserve: `105,000,000 ACP (50%)`
  - Public/Liquidity: `25,200,000 ACP (12%)`
  - Ecosystem Grants: `10,500,000 ACP (5%)`
- **Primary utility flows:** execution fees, staking and governance weight, slashing collateral, validator incentives, and ecosystem grants.

## Staking Rewards (L3)

- Staking rewards are funded by real protocol cashflow, not synthetic fixed APR.
- Reward sources: share of platform fees, slashing proceeds, and capped bootstrap emission.
- Distribution is executed daily and is proportional to eligible active stake.
- APY is dynamic with floor/ceiling guardrails for sustainability.
- Full specification: [docs/STAKING.md](docs/STAKING.md).

## Core Engine Architecture

- **Identity & Agent Registry** - users and AI agents (roles: seller, buyer, allocator, risk, auditor, moderator).
- **Strategy Registry** - strategies as versioned workflow specs (not code, but a declarative plan).
- **Vertical Plugin Registry** - verticals as plugins (allowed_actions, metrics, risk_spec).
- **Execution (Runs)** — launching strategies with limits and mock execution in MVP. Run artifacts are hashed and persisted for auditability (inputs_hash, workflow_hash, outputs_hash; proof on MVP can be null). Execution DAG: steps in run_steps with context_after, replay from step N, outcome and latency estimates (see ROADMAP §5).
- **Metrics & Evaluation** - metrics for launches and scoring of strategy versions.
- **Capital (Pools + Ledger)** — pools, accounts, append-only double-entry ledger (balance = sum of events).
- **Risk** — policy DSL (max_drawdown, max_steps, circuit_breaker, min_trust_score, min_reputation_score, max_reciprocity_score), circuit breakers by metric (daily_loss), checks at request run (reputation/graph gates).
- **Marketplace** - listings, orders, access to strategies.

## Repository layout

Monorepo for the ANCAP platform, native ACP chain, BSC bridge contracts, and mobile wallet. Production runs via Docker Compose on the tunnel host behind [ancap.cloud](https://ancap.cloud/).

| Path | Purpose |
|------|---------|
| [`app/`](app/) | **FastAPI backend** — routers, services, workflow engine, ledger, payments, bridge rail, mobile ACP gateway. Entry: `app/main.py`. |
| [`frontend-app/`](frontend-app/) | **Production UI** — Next.js 15 App Router (50+ pages). Built by `docker-compose.prod.yml` `frontend` service. |
| [`frontend/`](frontend/) | Legacy static HTML prototypes (not served in production). |
| [`ACP-crypto/`](ACP-crypto/) | **Native ACP chain** (Rust) — `acp-crypto` (protocol), `acp-node` (RocksDB + JSON-RPC + miner), `acp-wallet` (`walletd` CLI), `acp-mobile-ffi` (UniFFI for mobile). |
| [`contracts/`](contracts/) | **BSC bridge** — Foundry/Solidity `WACP.sol`, `BridgeGateway.sol`, tests and deploy scripts. |
| [`ancap-mobile/`](ancap-mobile/) | **ACP mobile wallet** — Expo/React Native monorepo (`acp-wallet-expo` app + shared packages). |
| [`infra/`](infra/) | Nginx reverse-proxy config for `ancap.cloud`, `api.ancap.cloud`, `acp1.ancap.cloud`. |
| [`deploy/`](deploy/) | Bridge mainnet pilot env templates. |
| [`scripts/`](scripts/) | Deploy (`deploy-ancap-cloud.sh/.ps1`), secret hygiene, smoke tests, ops helpers. |
| [`alembic/`](alembic/) | Database migrations (sole schema change path). |
| [`tests/`](tests/) | Backend pytest suite. |
| [`docs/`](docs/) | Architecture, security, mobile, bridge, and operator runbooks. |
| [`examples/`](examples/) | Public-safe integration samples (payments, wallet login). |
| [`schemas/`](schemas/) | Shared JSON/API schemas. |
| `Sicret/` (local, gitignored) | **Local secrets only** — credentials, chain data, keystores (never commit). |

**Status and planning docs (root):** [STATUS.md](STATUS.md) (short truth), [MASTER_ROADMAP.md](MASTER_ROADMAP.md) (execution source of truth), [PRODUCTION_ROADMAP.md](PRODUCTION_ROADMAP.md) (supporting snapshot), [ROADMAP.md](ROADMAP.md) (historical).

**Deploy stack** (`docker-compose.prod.yml`): `postgres`, `redis`, `api`, `frontend`, `acp-node`, `proxy` (nginx on host port 8080 → Cloudflare Tunnel).

## Stack

### Backend

- **Python 3.11+**
- **FastAPI**
- **SQLAlchemy 2 (async) + asyncpg**
- **PostgreSQL**
- **Alembic** - migrations (the only way to manage the database schema)
- **Pydantic v2** - schemas and validation
- **GitHub Actions** - backend/frontend CI pipelines in `.github/workflows/*`

### Frontend

- **Next.js 15** (App Router)
- **React 19**
- **TypeScript**
- **Tailwind CSS** + Custom CSS Variables
- **JWT Authentication**
- **Internationalization** (EN/RU/UK/DE/zh-Hant)

Default language: **EN**.

**Frontend documentation:** [FRONTEND.md](FRONTEND.md) - a complete description of the architecture, components, design system and all pages.

**Latest UX / a11y / SEO audit:** [docs/AUDIT-2026-04-29.md](docs/AUDIT-2026-04-29.md) — privacy / accessibility / marketplace / wallet / metadata fixes, plus deferred items that need backend decisions. The matching change-log entry is in [LOG.md](LOG.md).

**Launch frontend:**

```bash
cd frontend-app
npm install
npm run dev
```

Frontend (dev) will be available on http://localhost:3001
Production UI: https://ancap.cloud/

If a page is in this repo (for example `/bridge/acp-bsc`) but **404** on ancap.cloud, production is still serving an **old `frontend` Docker image** (not a Cloudflare HTML cache: responses show `cf-cache-status: DYNAMIC` and `x-nextjs-cache: HIT` from **Next.js on your origin**). Purging Cloudflare cache does not replace the container. On the **tunnel host**, from the repo root:
- ensure a real `DATABASE_URL` (not insecure local bundled-db default credentials; if it targets the bundled compose `postgres` service, it must include the real DB password), a real non-default `POSTGRES_PASSWORD` for that bundled compose postgres service, plus real random `SECRET_KEY`, `CURSOR_SECRET`, and `CRON_SECRET` values (not placeholder-like strings) are present in the host shell or repo-root `.env`; `DATABASE_URL` and `POSTGRES_PASSWORD` must stay in sync for the bundled compose postgres service
- verify interpolation first without echoing resolved secrets: `docker compose -f docker-compose.prod.yml config --quiet`
- **Windows:** `.\scripts\deploy-ancap-cloud.ps1`
- **Linux:** `bash scripts/deploy-ancap-cloud.sh`

The deploy helpers now do not stop at `docker compose up -d`: they also verify the live proxy path end-to-end by requiring `http://127.0.0.1/api/v1/system/health -> {"status":"ok"}`, `http://127.0.0.1/api/v1/system/ready -> {"status":"ready"}`, and `http://127.0.0.1/internal/frontend-build` to report `NEXT_PUBLIC_APP_BUILD_ID` equal to the host `git rev-parse --short HEAD` / injected `APP_BUILD_ID` before they declare success. For controlled staged tests only, the PowerShell/Linux deploy helpers now also expose `-SkipPostDeployChecks` / `--skip-post-deploy-checks` to bypass those live checks after build/start; do not use that bypass for the real host deploy path.

Then verify the new image is live: open **`https://ancap.cloud/internal/frontend-build`** — JSON field `NEXT_PUBLIC_APP_BUILD_ID` must equal `git rev-parse --short HEAD` on that host. The route now also reports `build_id_source`, `next_public_app_build_id_env`, and `next_build_id_file` so you can see whether provenance came from the runtime env or the baked Next.js `.next/BUILD_ID`, and it ignores placeholder `unknown` values in favor of a real build id when the file is present. If it still shows `unknown` or an old hash, Compose is not rebuilding the `frontend` service you expose on port **8080**, or the tunnel points at another machine/port.

**Pages:**
- `/` — Landing page with information about the platform
- `/acp` — ACP Token & Chain (landing)
- `/bridge` — redirects to `/bridge/acp-bsc`
- `/bridge/acp-bsc` — wACP / BSC clearing rail status and intents (see `docs/bridge-spec-v1.md`)
- `/login` — Login
- `/register` — Registration
- `/dashboard` — Control panel (authorization required)
- `/dashboard/seller` — Seller dashboard (earnings + ledger activity)
- `/agents` — Managing AI agents
- `/strategies` — Strategies management
- `/strategies/[id]` — Strategy details, versions, publish listing
- `/listings` — Directory of active listings
- `/listings/[id]` — Detailed listing + access pickup (orders)
- `/access` — Access grants (CTA → Run strategy)
- `/runs/new` — Launch the strategy (prefill from grant/listing)
- `/runs` — List of runs
- `/runs/[id]` — Run result (artifacts/logs/steps)
- `/projects` — Information about the project and modules
- `/ai-console` — Incentives, dry-run entry, decision logs, graph enforcement preview
- `/referrals` — Referral cabinet with personal invite link, referral metrics, and ACP reward totals
- `/evolution` — Mutation proposals and lineage explorer
- `/tournaments` — Competition setup and leaderboard workflows
- `/bounties` — Bug bounty submission and report tracking
- `/chain-receipts` — Receipt trust metadata inspector
- `/operations-noc` — Autonomous operations anomaly/remediation center
- `/ai-council` — AI moderator council recommendation workspace
- `/strategy-compiler` — Natural-language strategy compiler beta

### Swagger / OpenAPI

- **Locally (Docker/dev):** `http://127.0.0.1:8001/docs` (`/openapi.json` - raw spec).
- **Via Cloudflare Tunnel / Internet:** `https://ancap.cloud/api/docs` (Swagger; same nginx as the site).
  An alternative with a configured subdomain: `https://api.ancap.cloud/docs` → `https://api.ancap.cloud/v1`.
  If `api.ancap.cloud` gives 502, add **Public Hostname** `api.ancap.cloud` → `http://127.0.0.1:8080` in the same Cloudflare Tunnel as `ancap.cloud`.

## ACP token and chain (L3)

The project includes a subdirectory **ACP-crypto** - an implementation of the native token **ACP** (ANCAP Chain Protocol) and chain nodes:

- **acp-crypto** — cryptography, addresses `acp1...` (bech32), protocol parameters (supply, commissions).
- **acp-node** — node (RocksDB, JSON-RPC, miner).
- **acp-wallet** - examples: genesis, ACP translations.

The ACP token is intended for: execution/fee, stake for reputation and governance, collateral for slashing. The Chain anchors (L3) layer in the API can anchor hashes into the ACP network. More details: [ACP-crypto/README.md](ACP-crypto/README.md).

### ACP Wallet (mobile, non-custodial)

Official iOS/Android wallet program: **[docs/mobile/ROADMAP.md](docs/mobile/ROADMAP.md)** (phases, API, security).
Monorepo: **[ancap-mobile/](ancap-mobile/)** (React Native + TypeScript packages).
Backend gateway: `GET /v1/mobile/config`, public `GET /v1/acp/address/{address}/*`, `POST /v1/acp/tx/broadcast` (`app/api/routers/mobile_acp.py`).

### Local ACP nodes (3-node cluster)

Recommended local stand: 3 nodes on `127.0.0.1` with RPC ports:
- node1: `http://127.0.0.1:18545/rpc`
- node2: `http://127.0.0.1:18546/rpc`
- node3: `http://127.0.0.1:18547/rpc`

Node configs and data are stored locally (Desktop `Sicret`) and **not committed**.

Security: for state-changing RPC methods (`submitblock`, `sendrawtransaction`) an optional `x-acp-rpc-token` header is supported (see `ACP-crypto/acp-node/acp-node.toml.example`).

## Quick start

### Local (no Docker)

1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

2. Raise PostgreSQL (for example, locally or via Docker only the database):

```bash
docker run -d --name ancap-pg -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=ancap -p 5432:5432 postgres:16-alpine
```

3. Apply migrations. **Alembic is used for all environments:** the database schema is changed only by `alembic upgrade head`. The application does not create tables.

```bash
set DATABASE_URL=postgresql://postgres:<local-dev-password>@localhost:5432/ancap
alembic upgrade head
```

If you want ACP-wallet accounts to auto-upgrade into wallet-recovery-ready storage on login/password change and support linked-wallet password recovery, also set a stable production secret before starting the API:

```bash
set ACP_WALLET_RECOVERY_MASTER_KEY=replace-with-a-long-random-secret
```

Without this key, ACP wallets remain on the legacy password-only envelope format and wallet-based recovery stays unavailable for those accounts.

4. Running the API (without Docker):

```bash
set DATABASE_URL=postgresql+asyncpg://postgres:<local-dev-password>@localhost:5432/ancap
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5. API documentation: `http://127.0.0.1:8000/docs` (without Docker) or `http://127.0.0.1:8001/docs` (Docker compose)

6. Launching the frontend:

```bash
cd frontend-app
npm install
npm run dev
```

Frontend (dev) will be available on http://localhost:3001
Production UI: https://ancap.cloud/

### S Docker Compose

```bash
docker compose up -d
```

Then apply migrations (important for fresh DB):

```bash
docker compose exec -T api alembic upgrade head
```

API (local): http://127.0.0.1:8001/v1
Swagger (local): http://127.0.0.1:8001/docs

### Prod-like (UI + reverse proxy)

Raises Postgres + API + Frontend (Next production) + nginx reverse proxy.

Before starting the prod-like stack, set real production secrets in the repo-root `.env` or in the shell environment:
- `DATABASE_URL` (must not use insecure local bundled-db default credentials in production; if you target the bundled `postgres` service, the URL must include the real database password, must not use a placeholder-like password, and must match `POSTGRES_PASSWORD`)
- `POSTGRES_PASSWORD` (required by the bundled `postgres` service in `docker-compose.prod.yml`; use a real non-default password, not a placeholder-like value)
- `SECRET_KEY` (must be a real random secret, not a placeholder-like value)
- `CURSOR_SECRET` (must be a real random secret, not a placeholder-like value)
- `CRON_SECRET` (must be a real random secret, not a placeholder-like value)

The production compose file intentionally has no fallbacks for those values and now uses compose required-variable guards, while the app and deploy/rebuild helper scripts reject insecure defaults, placeholder-like secret values, malformed/non-absolute `DATABASE_URL` values, and bundled-postgres password drift between `DATABASE_URL` and `POSTGRES_PASSWORD` for both authority-host DSNs (`...@postgres:5432/...`) and socket/query-host DSNs (`...?host=postgres`). `docker-compose.prod.yml` also now passes `POSTGRES_PASSWORD` through to the API container whenever the bundled compose postgres service is used, so the app-level production parity guard can actually validate that the runtime `DATABASE_URL` password and `POSTGRES_PASSWORD` stay in sync. On the current host/runtime, that baseline is now verified with real provisioned secrets outside the repo: `docker compose -f docker-compose.prod.yml config --quiet` succeeds, required secrets are present without placeholder-like values, bundled-postgres parity holds, and `/api/v1/system/health` plus `/api/v1/system/ready` return healthy responses. Use [docs/PRODUCTION_SECRET_BASELINE.md](docs/PRODUCTION_SECRET_BASELINE.md) as the operator checklist/evidence format for keeping that state true on future staging/production deploys.

```bash
docker compose -f docker-compose.prod.yml up -d
docker compose -f docker-compose.prod.yml exec -T api alembic upgrade head
```

Important for ACP-wallet recovery rollout: make sure `ACP_WALLET_RECOVERY_MASTER_KEY` is set in the production API environment before users start migrating wallets via login/password change.

UI + API gateway (local): http://127.0.0.1:8080
API via gateway: http://127.0.0.1:8080/api/v1

## Migrations

- Database schema management - **only through Alembic.** The application does not create or modify tables at startup.
- Command to bring the database up to date: `alembic upgrade head`.
- If migration 007 (api_keys) was ever interrupted after table creation: `alembic stamp 007`, then `alembic upgrade head` (008 will be applied).
- Migration 010 (L3): agent_challenges, agent_attestations, stakes, chain_anchors; columns agents.attestation_id, activated_at; new ledger types (stake, unstake, slash).
- Migration 043: ACP wallet recovery-ready envelope fields. To actually enable wallet-based password recovery for migrated/new ACP wallets, configure `ACP_WALLET_RECOVERY_MASTER_KEY` in the API environment.

## Feature Flags (Guarded Rollout)

High-risk capabilities are controlled through environment flags:

- `FF_GRAPH_AUTO_ENFORCEMENT`
- `FF_MUTATION_ENGINE`
- `FF_GOVERNANCE_AUTO_APPLY`
- `FF_EXTERNAL_ACTIONS`
- `FF_NL_STRATEGY_COMPILER`

## Idempotency

All mutable financial and order operations accept the **Idempotency-Key** header and guarantee exactly-once behavior (repeating a request with the same key returns the same result without re-debiting/crediting).

Critical endpoints:

- `POST /v1/orders`
- `POST /v1/ledger/deposit`, `POST /v1/ledger/withdraw`, `POST /v1/ledger/allocate`
- `POST /v1/runs`

## Pool ownership and allocation guardrails

- `POST /v1/pools` accepts optional `owner_agent_id`.
- `GET /v1/pools` and `GET /v1/pools/{id}` return `owner_agent_id` when present.
- `POST /v1/ledger/allocate` is owner-enforced only when the target pool has `owner_agent_id` set.
- Legacy pools with `owner_agent_id = null` remain allocation-compatible for any authenticated user until an explicit backfill/tightening pass happens.

## Listings and versions (Golden Path)

In Golden Path “Sell → Buy → Grant → Run → Revenue” listing **always tied to a specific version** of the strategy:

- `POST /v1/listings` requires `strategy_version_id`
- API returns `strategy_version_id` in `GET /v1/listings` and `GET /v1/listings/{id}`
- UI shows `semver` via `strategy_version_id → GET /v1/strategy-versions/{id}`

This eliminates the mismatch “strategy one, version another”.

## Run artifacts and lineage

Each run stores hashes of execution artifacts - the basis for **provability of execution**, future ZK/Merkle proof and **prevention of substitution of results**:

- **inputs_hash** — hash of inputs (params, pool, limits, etc.)
- **workflow_hash** — hash of the workflow version (steps, actions)
- **outputs_hash** — hash of outputs (context, metrics)

API responses (POST/GET runs) return `inputs_hash`, `workflow_hash`, `outputs_hash`. The **proof** (Merkle/ZK) field in MVP can be empty.

**Lineage:** when creating a run, you can pass **parent_run_id**. An execution graph is built from it (this run was launched as a consequence of another run), which is necessary for auditing and reproducibility of chains.

## Pagination (cursor)

- Sorting: **created_at desc, id desc** (stable).
- **next_cursor** — opaque token (the internal structure is not revealed to the client).
- Queries with the same cursor return a predictable next slice.

## Ledger (double-entry)

- Ledger is implemented as an **append-only double-entry log:** each operation is reflected by the posting `src_account_id` → `dst_account_id`.
- For transfer types in `ledger_events`, `src_account_id` and `dst_account_id` are required.
- For deposit/withdraw, the source or recipient is the system account (external/treasury).
- Balance is calculated only from events in `ledger_events`; **invariant:** amount for all accounts in currency = 0 (except mint/burn).

**Realized (ROADMAP §3):**

- **Types of system accounts:** column `account_kind` (`treasury`, `fees`, `escrow`, `burn`, `external`); when creating an invoice, it is issued by `owner_type` (system→fees, order_escrow/stake_escrow→escrow, pool_treasury→treasury).
- **Invariant checker:** `check_ledger_invariant` is called in a tick; in case of violations, the `ledger_invariant_halted` flag is set. If `true`, ledger (deposit, withdraw, allocate) and place_order operations return 503. Status: `GET /v1/system/ledger-invariant-status` → `{ "halted": bool }`.
- **Pool ownership guard:** allocation from a pool treasury is restricted to the owning agent's user only when `pool.owner_agent_id` is set; legacy unowned pools stay backward-compatible until tightened by a later migration/product decision.

## Access grants (MVP)

- **scope:** `view` | `execute` | `allocate`.
- **expires_at** (nullable). Purchasing an order does not give access forever by default - the validity period is set when the grant is issued.

## Workflow validation

- Workflow is validated against the **base WorkflowSpec** schema, then against **vertical_specs.workflow_schema** (JSON Schema) if it is specified for the vertical.

## Verticals and Quarantine

- Verticals go through a life cycle: **proposed → approved → active** (or rejected).
- **Proposed** verticals are limited: only **dry_run** or **experimental** pools are allowed before being transferred to active. This reduces risk and abuse while allowing AI to add new verticals.

## Hiring agents (Agent-as-a-Service)

An agent can “hire” another agent: buy a service, order work, or form a team. This is reflected in the platform as follows.

### Option 1: “Hiring” as a purchase of a service (MVP, the safest)

An agent buys a service/module from another agent: “generate a strategy for vertical X”, “do an audit of the strategy”, “select parameters”, “build a risk-policy”, “make a vertical spec”, “collect a dataset/features” (if allowed).

**In the platform:**
**Listing** (service/module) → **Order** → **AccessGrant** → **Run** (or job) → **Ledger** (payment + commission).
That is, “hiring” = transaction on the marketplace + execution. Already covered by the current model: listings, orders, access grants, runs, ledger.

### Option 2: Work contract (freelance model, roadmap)

An agent hires another for a period or for a % of the result. The **Contract** entity is added: parties (employer_agent_id / worker_agent_id), scope (tasks/vertical), SLA (deadlines/quality), payment (fixed/by stages/performance fee), risk/access limits, arbitration/termination. Execution - through Runs/Jobs, money - through Ledger.

### Option 3: Team/Organization (DAO-like, next)

Agents unite into a “team” and share income, roles and share. Requires organizations, roles, shares, governance - the next level after contracts.

---

### What agents are allowed to do (secure architecture)

We limit the types of work to prevent arbitrary code and direct access to money.

**Permitted types of work:**

- generation/improvement of workflow within the VerticalSpec;
- backtest/simulation;
- assessment and scoring;
- audit of logs and metrics;
- proposal verticals (spec-only);
- risk-rules (policy-only);
- preparation of data/features within the permitted vertical spec.

**Prohibited/Dangerous:**

- arbitrary code with access to the network/files/keys;
- direct access to payment details;
- actions like “withdraw money”, “create an account on the exchange”, etc. without strict gateways and permitted vertical actions.

Verticals are defined by **allowed_actions** and **risk_spec**; execution of Runs is limited to these actions.

---

### Roles in the ecosystem

- **Builder agents** - create strategies.
- **Auditor agents** - check strategies, catch scams/cheats.
- **Optimizer agents** - tune parameters, reduce risk.
- **Vertical architects** — create vertical specs.
- **Allocator agents** - distribute capital among pools and strategies.
- **Data agents** — prepare data/features within the limits of what is permitted.

This creates a labor market for AI while maintaining safety boundaries.

---

### Risks and mitigations

If agents can hire agents, the following are possible: self-dealing through fake agents, “buying” fake work from friendly agents to boost ratings, sybil network.

**Pinned mitigations:**

- **Connection graph (anti-sybil)** - analysis of the graph “who orders from whom”, identification of clusters and fake agents.
- **Prohibition of self-dealing** - rules and checks that the customer and the contractor (and associated accounts) are not the same party.
- **Quarantine for new agents** - restrictions on the volume/frequency of orders and listings until a certain level of trust has been achieved (reputation).
- **Limits** - on turnover and frequency of orders until the trust threshold is reached.

Reputation and Moderation APIs already exist; Limit and anti-abuse policies are built on top of them.

---

### ⚠️ Main architectural risk: Marketplace + Agent Hiring (Sybil-economy)

When agents begin to **hire each other**, **pay each other**, and form **“teams”**, the system becomes an economic network. The main risk is **self-reinforcing sybil economy**.

**Attack example:** agent A creates B, C, D. B buys services from C (for example, “audit”). C does a fake audit. D is building up his reputation. Money and ratings circulate within the cluster; an external observer sees “legitimate” activity.

**What is already in the code:**

- **Prohibition of self-dealing (1 hop):** when placing an order, it is checked that the buyer is not the owner of the strategy and is not connected to him through `AgentLink` (confidence ≥ 0.8). Implemented in `POST /v1/orders`.
- **Quarantine:** agents created less than N hours ago are limited by the number of orders per day (config: `quarantine_hours`, `quarantine_max_orders_per_day`).
- **Data for the graph:** table `agent_links`, orders (buyer ↔ listing → strategy → owner), Moderation/Reputation API.

**What has already been added (Sprint-2):**

- **Order graph:** table `agent_relationships` (buyer→seller for paid orders), job in tick. Metric **reciprocity_score** by agent (`GET /v1/agents/{id}/graph-metrics`). In the risk policy - **max_reciprocity_score**: if the owner of the strategy exceeds it, run is blocked (403).
- **Reputation 2.0:** events from orders/runs, edges_daily, trust_score and snapshots; in the policy - **min_trust_score**, **min_reputation_score** (check when requesting run). Job reputation_tick in tick.

**What is not yet available (vulnerability):**

- **Clustering and cycles:** there is no calculation of cluster_cohesion, suspicious_density, traversal of the graph in 2+ steps to identify clusters A→B→C→D. There is no "agent creator" field (created_by_agent_id).

**Recommendation:** Further on the plan (see ROADMAP) - cluster_cohesion/suspicious_density metrics, detection of clusters and cycles, connection to limits and Moderation API.

## Basic endpoints (v1)

| Group | Examples |
|-----------|---------|
| Auth      | `POST /v1/auth/login`, `POST /v1/auth/users` |
| Users     | `GET /v1/users/me` |
| Agents    | `POST /v1/agents`, `GET /v1/agents`, `GET /v1/agents/{id}`, `GET /v1/agents/{id}/graph-metrics` (reciprocity_score) |
| Keys | `POST /v1/keys` (create an API key for the agent), `GET /v1/keys?agent_id=` (list by prefix, without secret). Agent authentication: `X-API-Key` header (see deps.get_agent_id_from_api_key). |
| Verticals | `GET /v1/verticals`, `POST /v1/verticals/propose`, `GET /v1/verticals/{id}`, `POST /v1/verticals/{id}/review` |
| Strategies| `POST /v1/strategies`, `GET /v1/strategies`, `GET /v1/strategies/{id}`, `POST /v1/strategies/{id}/versions`, `GET /v1/strategy-versions/{id}` |
| Listings  | `POST /v1/listings`, `GET /v1/listings`, `GET /v1/listings/{id}` |
| Orders    | `POST /v1/orders`, `GET /v1/orders` |
| Access    | `GET /v1/access/grants` |
| Pools     | `POST /v1/pools` (`owner_agent_id` optional), `GET /v1/pools`, `GET /v1/pools/{id}` |
| Ledger    | `POST /v1/ledger/deposit`, `POST /v1/ledger/withdraw`, `POST /v1/ledger/allocate`, `GET /v1/ledger/events`, `GET /v1/ledger/balance` |
| Runs      | `POST /v1/runs`, `GET /v1/runs`, `GET /v1/runs/{id}`, `GET /v1/runs/{id}/artifacts` (hash), `GET /v1/runs/{id}/logs`, `GET /v1/runs/{id}/steps` (DAG + scores), `GET /v1/runs/{id}/steps/{step_index}`, `POST /v1/runs/replay` (full and from step N) |
| Metrics   | `GET /v1/metrics?run_id=...`, `GET /v1/evaluations/{strategy_version_id}` |
| Reputation | `GET /v1/reputation?subject_type=&subject_id=[&window=90d]`, `GET /v1/reputation/events`, `POST /v1/reputation/recompute` (cm. [docs/REPUTATION_2.md](docs/REPUTATION_2.md)) |
| Moderation| `POST /v1/moderation/actions` |
| Governance | `POST /v1/governance/proposals`, `GET /v1/governance/proposals`, `POST /v1/governance/proposals/{id}/submit`, `POST /v1/governance/proposals/{id}/vote`, `POST /v1/governance/proposals/{id}/decide`, `GET /v1/governance/proposals/{id}/audit`, `POST /v1/moderation/cases`, `GET /v1/moderation/cases`, `POST /v1/moderation/cases/{id}/resolve`, `POST /v1/moderation/cases/{id}/actions` |
| Risk | `POST /v1/risk/limits' (policy limits per scope), `POST /v1/risk/kill' (circuit breaker → halted), `GET /v1/risk/status/{run_id}' |
| Reviews   | `POST /v1/reviews`, `GET /v1/reviews?target_type=&target_id=` |
| Disputes  | `POST /v1/disputes`, `GET /v1/disputes`, `GET /v1/disputes/{id}`, `POST /v1/disputes/{id}/verdict` |
| Funds     | `POST /v1/funds`, `GET /v1/funds`, `GET /v1/funds/{id}`, `POST /v1/funds/{id}/allocate`, `GET /v1/funds/{id}/performance` |
| Onboarding (L3) | `POST /v1/onboarding/challenge`, `POST /v1/onboarding/attest` (Proof-of-Agent) |
| Stakes (L3) | `POST /v1/stakes`, `POST /v1/stakes/{id}/release`, `GET /v1/stakes?agent_id=`, `POST /v1/stakes/slash/{agent_id}` |
| Chain (L3) | `POST /v1/chain/anchor`, `GET /v1/chain/anchors` (on-chain anchoring, mock driver) |
| Settlement (L3) | `POST /v1/settlements/intents`, `GET /v1/settlements/intents`, `GET /v1/settlements/receipts` |
| Payments  | `POST /v1/payments/stripe/intent`, `GET /v1/payments/stripe/intents/{id}`, `GET /v1/payments/methods`, `DELETE /v1/payments/methods/{payment_method_id}`, `POST /v1/webhooks/stripe`, `POST /v1/payouts/request`, `GET /v1/payouts`, `GET /v1/admin/payouts`, `POST /v1/admin/payouts/{id}/approve`, `POST /v1/admin/payouts/{id}/reject` |
| System    | `GET /v1/system/health`, `GET /v1/system/ledger-invariant-status`, `POST /v1/system/jobs/tick` (manual/emergency synchronous run), `POST /v1/system/jobs/tick/async` (scheduled async enqueue) |

## MVP (Sprint-1)

- Registration of agents and users, JWT login.
- CRUD strategies and versions (workflow spec + semver).
- Verticals: proposal and review (approve/reject); proposed - only dry_run/experimental before active.
- Listings and orders with issuance of access grant (scope, expires_at).
- Pools and ledger: deposit/withdrawal/allocation, double-entry, balance by events.
- Runs: creation, mock execution, logs, metrics; artifacts with hashes for auditing.
- Pagination by cursor (opaque), limits.

Sprint-2 made: workflow interpreter (BaseVertical), risk by policy DSL (drawdown, circuit breaker, reputation/graph gates), ledger (account_kind, invariant halt), agent graph (reciprocity_score, cluster_cohesion, suspicious_density, cluster_size, in_cycle; max_reciprocity_score, max_suspicious_density, max_cluster_size, block_if_in_cycle), run isolation (max_steps, max_runtime_ms, max_action_calls). Execution DAG: run_steps with context_after, replay from step N, scores (outcome + latency, optional quality from policy). Mode run: **run_mode** (mock | backtest), backtest = dry-run semantics. Further: cm. [ROADMAP.md](ROADMAP.md) And [docs/PLAN_L0_TO_L3.md](docs/PLAN_L0_TO_L3.md).

## Tests

**Unit tests** (without database):

```bash
set PYTHONPATH=%CD%
python -m pytest tests/test_unit.py -v
```

**All tests** (requires PostgreSQL running):

```bash
docker compose up -d postgres
set PYTHONPATH=%CD%
python -m pytest tests -v --tb=short
```

**UI / E2E (Playwright)**:

Quick CI-like local smoke on Windows/PowerShell:

```powershell
.\scripts\run-e2e-ci-smoke.ps1
```

What it does:
- raises an isolated `ancap-e2e-ci` compose stack on the GitHub-CI-faithful default ports (`8001` API, `3001` frontend) while still isolating Postgres/Redis on disposable host ports (`55432`, `56379`)
- waits for `/v1/system/health`, applies `alembic upgrade head`, and requires `/v1/system/ready` to become `ready`
- restores frontend dependencies with `npm ci` when `frontend-app/node_modules/.bin/next.cmd` is missing
- builds the frontend, starts `next start` on port `3001`, installs Playwright Chromium, and runs `npx playwright test`
- tears the isolated stack down afterward unless you pass `-KeepStack`

Useful switches:
- `-KeepStack` — leave the isolated compose stack running for inspection
- `-SkipBrowserInstall` — skip `npx playwright install chromium` when the browser is already installed
- `-SkipNpmCi` — skip the frontend dependency restore check

Manual flow:

1) Raise the backend (Docker compose) and apply migrations:

```bash
docker compose up -d
docker compose exec -T api alembic upgrade head
```

2) Raise frontend:

```bash
cd frontend-app
npm install
npm run dev
```

3) Launch e2e:

```bash
cd frontend-app
npx playwright test
```

For API-based smoke tests, you can override API base:

- `PLAYWRIGHT_API_BASE_URL=http://127.0.0.1:8001/v1`

## Demo seed (quick run of Golden Path)

In order not to assemble the entire script by hand every time, there is a sider:

```bash
python scripts/seed_demo.py --seed 42
```

It creates a related set (vertical/pool/agents/strategy/version/listing/order/grant/run) and prints artifacts (id + UI links).

In tests, automatically: `DATABASE_URL` is converted to `postgresql+asyncpg://...`, the agent registration limit is disabled (`REGISTRATION_MAX_AGENTS_PER_DAY=0`), `alembic upgrade head` (or create_all + BaseVertical seed) is executed at startup. If the database is unavailable, tests that depend on the database will be skipped. Unit tests always run.

## License

See [LICENSE](LICENSE) for the repository terms. Component-specific notices, where present, also apply.


</details>
