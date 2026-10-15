# ANCAP Master Roadmap

## ACP wallet usability — 2026-10-15

Web wallet hierarchy, balance clarity, reviewed transfers and on-demand services are implemented. [Scope and verification](docs/WALLET_UX_RELEASE_2026-10-15.md). Existing native/consensus/bridge/SACP work is not included.

## Workflow Studio release — 2026-10-15

Implementation and limits: [workflow operations](docs/WORKFLOW_OPERATIONS_RELEASE_2026-10-15.md). Durable schedules, review, delivery, context, versions, bounded trials/batches, API examples and BYOK are implemented. Full CI passed; build `e53f949` is deployed and verified. Release evidence records test counts and remaining dependency findings. External account credentials and private infrastructure are customer supplied; wallet/bridge/consensus/SACP WIP is excluded.

> Status: active | Major revision: 2026-05-25
> Created: 2026-05-23 | Last updated: 2026-10-02

## Hardening + deploy wave (2026-07-01)

Completed in the `2026-07-01` hardening deploy:
- **Server**: root + HestiaCP admin passwords rotated (stored in server-side `Sicret/`), `apt full-upgrade` applied, ~13 GB Docker build cache pruned (disk 70% → 42%), kernel security reboot done, and all six prod compose services now carry `restart: unless-stopped` (both live containers and `docker-compose.prod.yml`).
- **Backend security**: `/v1/system/jobs/tick*` fails closed without `CRON_SECRET` outside development; `POST /acp/tx/broadcast` requires an authenticated user or a registered device token (`X-Device-Token`) plus per-caller rate limit; `walletd` deterministic fallback raises in production; ACP-node RPC fails closed for all non-public methods when `ACP_RPC_TOKEN` is unset (prod compose requires the token; nginx rate-limits `/rpc`); `POST /chain/anchor` requires user or agent API-key auth; debug platform-admin bypass removed; `/internal/ops/ledger-invariant-status` is platform-admin only.
- **ACP wallet clarity / history restore**: `/v1/wallet/acp/hot/balance` exposes non-overlapping `primary_acp` / on-chain / platform ledger / staked / withdrawable / operator live fields (design allocations never presented as live); address bindings (`083_user_acp_address_bindings`) + indexer watchlist from wallets/privacy/history; history prefers `MobileAcpTx` with chain-scan fallback; platform-admin `POST /v1/platform-admin/acp-history/rescan`.
- **Smart Pay durability**: intents/quotes/executions/receipts persist to the new `mobile_smart_pay_records` table (migration `c4d5e6f7a8b9`) with in-process cache + DB rehydration; execute requires an authenticated user.
- **Frontend**: Turnstile is optional when no site key is configured (dev unblock); SSR API base unified via `getServerApiBase()` (`ANCAP_SERVER_API_URL=http://api:8000` in prod compose); `/pricing` reads live workflow-store templates/bundles with static fallback; `/token-snapshot` now calls a real backend endpoint (`POST /token-snapshot`) doing on-chain contract + ERC-20 interface checks on BSC/Ethereum; primary/secondary navigation fully translated into RU/UK/DE.
- **Deploy**: build `5e13b3f` live on ancap.cloud (auto-deploy after hardening wave); health/ready/frontend-build checks green.
- **CI fixes (post-push)**: mobile RN typecheck fixed by hoisting `@types/react@~18.3.12` to the `ancap-mobile` workspace root; dependency-consolidation test synced to vitest `^4.1.9`; mobile roadmap sync test updated to current P4-3/P4-11 wording; ledger-halt scenario test now authenticates as a configured platform admin.

**2026-07-02 plan closure add-ons:**
- **Security evidence**: `docs/SECURITY_CLOSURE_EVIDENCE_2026-07-01.md` + synced `STATUS.md` / `docs/STATUS_MATRIX.md`
- **CI fail-closed**: `deploy-ancap-cloud.yml` and `system-jobs-tick.yml` now exit non-zero when required secrets are missing; `docs-ci.yml` triggers on `master` as well as `main`
- **Stripe repo E2E**: `docs/STRIPE_AUTOMATED_E2E_EVIDENCE.md` (`pytest tests/api/test_payments.py -q` → 33 passed); packet `docs/stripe-verification-2026-07-02.md`
- **Smart Pay**: shared OCR/receipt heuristics (`app/services/payment_text_parse.py`), web `/payment-scanner` OCR mode, mobile `ocr` parse source, execution `routePlan` for non-custodial signing steps
- **Mobile release evidence**: `docs/mobile/release-evidence-v1.0.0-rc1.md` (repo-verified slice); **local Android test env unblocked** (`docs/mobile/ANDROID_TEST_ENV.md`, AVD `Pixel_10_Pro`); store uploads remain operator follow-up
> Owner: ARDO
> Rule: execute top-to-bottom by priority. Everything must be either DONE, in progress, intentionally deferred, or replaced by a better approved plan.
> Source of truth: this is the only execution-priority roadmap. `PRODUCTION_ROADMAP.md`, `ROADMAP.md`, `ROADMAP-MONETIZATION.md`, and `docs/mobile/ROADMAP.md` are supporting or historical documents and must not override this file.
> Fast status index: `docs/STATUS_MATRIX.md`

---

## Consolidated project goals

Workflow discovery release (2026-10-14): user task matching, browser shortlist, comparison/cost planning and JSON export implemented; investor local-demo evidence exposed with test-credit labels. Deployed build `426bc5c` and live browser/API checks passed; full Linux backend 883 passed / 34 skipped and browser CI 25 passed / 1 skipped; `docs/WORKFLOW_DISCOVERY_RELEASE_2026-10-14.md` records scope and evidence.

Investor outreach preparation (2026-10-14): proposed Cyprus + German GmbH structure localized; separate formation/accounting quote requests and cross-border adviser brief prepared. RU/EN introductions and first-contact drafts: `docs/investors/INVESTOR_INTRO_RU.md`, `INVESTOR_INTRO_EN.md`, `OUTREACH_DRAFTS.md`. Documents are drafts; correspondence has not been sent. Final ask still requires quotes and entity-role confirmation.

Investor demonstration evidence (2026-10-14): local Ollama `qwen2.5:3b` run recorded `succeeded`, `fallback_used=false`, test-ledger payment 14 ACP and reported fee 1.4 ACP. Durable archive: `docs/investors/evidence/2026-10-14-local-ollama/`. This demonstrates local model execution with test credits, not production-provider acceptance or customer revenue. Localized offer and budget/demo copy is in the investor presentation source.

Investor presentation (2026-10-14, deployed in 426bc5c): homepage and public navigation focus on paid AI workflow outputs; `/projects` groups six areas; `/investors` explains model/evidence/milestones without invented traction. Portfolio routes carry an honest buyer→receipt offer chain; research heroes stay AI briefs/concepts. Demo script + 12‑month cost budget (assumptions; cash scenarios derived from line items; final ask pending quotes) and test-env paid-path smoke (credits) are in-repo. Owner still must confirm jurisdiction, quotes, and any traction metrics. Handoff: [`docs/CURSOR_INVESTOR_FINISH_RU.md`](docs/CURSOR_INVESTOR_FINISH_RU.md).

Execution / contractor handoff (2026-10-14): [`docs/DEVELOPER_HANDOFF_RU.md`](docs/DEVELOPER_HANDOFF_RU.md) defines mobile release acceptance and independent audit scope. Local backend import restored by syncing `.venv` cryptography to the pinned `50.0.1`; mobile public-docs / roadmap-sync / error-sanitization checks: **20 passed**. Physical-device and store-release items remain open.

Ship ANCAP as a production ACP-first AI workflow platform:
- real paid AI workflow execution
- proof receipts and realtime status
- creator + developer monetization
- stable production UI/admin surfaces
- reliable bridge and wallet infrastructure
- completed ACP mobile wallet MVP
- hardened CI/CD and security automation
- operational stability for real-money flows

## Current top-line truth (2026-09-12)

**Work-stop blockers: none.**

Public launch hygiene (2026-10-11):
- Bridge doctrine **1 ACP ↔ 10 wACP** enforced in exchange office, catalog wACP quotes, and Smart Pay bridge leg (not just docs).
- Fiction SKUs retired from public surface: teleport earphones, Project Barsuk, dark-matter auction, time-machine footer lore. See [`docs/SAFE_LAUNCH_CHECKLIST.md`](docs/SAFE_LAUNCH_CHECKLIST.md).

Active remaining work (not blockers):
1. ACP mobile wallet — device-ready release (Play/TestFlight, physical sign-off, iOS native). Local Android test env is available (`docs/mobile/ANDROID_TEST_ENV.md`).
2. Open-source follow-through — GitHub org naming/ownership; `ancap-docs` Discussions pin/category UI; project-board auth. Phase 1 community files (`README.md`, `LICENSE`, `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`) are **in the repo root** and on the public GitHub repo.
3. Monetization depth — optional conversion/LTV. The first ACP-first revenue loop is **live**. Stripe 4.1 is operator live verification only.
4. **Oracle Cloud Always Free ACP node** — secondary Ampere A1 (ARM64) full node / public peer. Account registered; VM + `linux/arm64` image + peer sync open. Plan: [`docs/ORACLE_CLOUD_ACP_NODE_PLAN.md`](docs/ORACLE_CLOUD_ACP_NODE_PLAN.md).

Humanitarian aid desk (`/humanitarian`, `/legal/humanitarian`, `GET /v1/humanitarian/catalog`) shipped 2026-09-12: ACP briefs for food, water, nutrition, warm clothing, medical supplies (partner channel), and livelihood matching, with IFRC / national Red Cross listings as **desk handoffs**. **Not** a 135-FZ charity, **not** a signed ICRC/IFRC partnership, **not** an emblem licence, **not** a tax-deductible donation receipt, and **distinct** from the 100 ACP welcome grant.

Theodore / progress bots: do **not** report missing `README.md`. Do **not** report “monetization after the first ACP cycle” as a blocker.

Important: some older roadmap documents still read as more complete than the repo-wide execution truth. When there is any conflict, trust this file.

## Fixed decisions

- Primary LLM: Teneta/Claude-compatible Anthropic API
- Payments: ACP-first. Stripe/fiat is a later adapter after ACP checkout is stable.
- Fallback policy: template output is allowed only as explicit degraded fallback, never as a hidden premium LLM result.
- AI governance: tracked in \docs/AI_ISO_GOVERNANCE_NOTES.md\
- Public trust layer: whitepapers, terms, privacy, cookie consent published before broader paid acquisition
- CI rule: no \|| true\ soft-fails. A failing gate must fail the build.
- Open-source positioning rule: **ANCAP will be open-source where transparency increases trust, integration and adoption - while security-critical infrastructure, private keys, bridge signer operations, wallet hot-key logic and production secrets remain protected.**

## Open Source & GitHub Transparency

Status: [~] Active execution track. Phase 1 community files are done (`README.md` exists — this is **not** a missing-README blocker). Remaining: GitHub org naming/ownership, later public-repo split, and `ancap-docs` Discussions/project-board admin follow-up. The public GitHub repo already exists.

Goal:
- increase trust in ACP / wACP;
- make the project publicly auditable and easier to verify;
- simplify developer integrations;
- attract external contributors;
- prepare the project for audits, grants, listings, and partnerships.

Critical boundary:
- publish what improves trust, integration, and adoption;
- do **not** publish private keys, seed phrases, bridge signer internals, admin wallets, production `.env`, deploy secrets, hot-wallet operation logic, real RPC/API keys, or sensitive anti-fraud internals that would make abuse easier.

Reference detail: `docs/OPEN_SOURCE_GITHUB_TRANSPARENCY.md`

### Phase 1 - GitHub Public Foundation

Community-file slice: **done**. `README.md` is present in the repo root and on `https://github.com/ancapcloud/ancap`. Do not report “absence of README.md”.

- [ ] create a public GitHub org (`ANCAP` or `ancap-network`) when ownership/naming is finalized (operator follow-up, not a README gap)
- [x] keep the main project repo public-safe and contributor-ready
- [x] `README.md`, `LICENSE`, `CONTRIBUTING.md`, `SECURITY.md`, and `CODE_OF_CONDUCT.md` in the repo root
- [x] add public docs for architecture, roadmap, API, ACP/wACP, and trust/security boundaries
- [x] add GitHub issue templates and a PR template
- [x] enable GitHub secret scanning, push protection, Dependabot, CodeQL, and branch protection

### Phase 2 - Open Source Scope

Safe-to-open scope:
1. Core documentation
   - roadmap
   - architecture docs
   - tokenomics docs
   - ACP / wACP explanation
   - bridge concept
   - wallet feature docs
   - security model
   - API overview
2. Frontend
   - public site
   - wallet UI without production secrets
   - landing pages
   - docs UI
3. SDK / integration layer
   - TypeScript SDK
   - API client
   - examples
   - payment QR parser
   - wallet integration examples
4. Smart contracts / token contracts
   - wACP BEP-20 contract
   - bridge-related public contracts
   - verification scripts
   - testnet deployment instructions
5. Protocol specs
   - ACP decimals
   - ACP ↔ wACP conversion rules
   - bridge reserve model
   - transaction receipt model
   - payment intent model
   - QR Pay spec
   - Smart QR Pay flow

Explicitly private scope:
- private keys
- seed phrases
- bridge signer private logic
- admin wallets
- production `.env`
- real RPC/API keys
- exchange/listing accounts
- deployment secrets
- server credentials
- abuse-sensitive operational thresholds that should not be public

### Phase 3 - Repository Structure

Target public structure after the current monorepo hardening phase:
- `ancap-docs` - public documentation, roadmap, whitepaper, architecture, tokenomics
- `ancap-web` - public website and landing frontend
- `ancap-wallet` - mobile/web wallet interface and Smart QR Pay UI
- `ancap-sdk` - TypeScript SDK for ACP / wACP integrations
- `ancap-contracts` - wACP contract, bridge public contracts, deployment scripts
- `ancap-examples` - merchant/payment/API/QR integration examples
- `ancap-core` - publishable protocol components safe for public review

Private target repos:
- `ancap-infra`
- `ancap-bridge-operator`
- `ancap-admin`

### Phase 4 - Licensing

Default licensing direction:
- Apache-2.0 for core / protocol / SDK / contracts
- MIT for frontend / examples when frictionless adoption matters more
- CC BY 4.0 or Apache-2.0 for docs, depending on repo split

Current repo decision:
- this mixed monorepo defaults to **Apache-2.0** until the codebase is split into dedicated public repos with component-specific licensing if needed.

### Phase 5 - GitHub Security Baseline

Before publishing any additional repo or public split:
- remove `.env`, private keys, mnemonics, tokens, and RPC keys;
- keep `.env.example` only;
- check git history for secrets;
- enable GitHub secret scanning + push protection;
- enable Dependabot + CodeQL;
- block direct pushes to the default branch;
- require review before merge;
- define revoke/rotate procedure for leaked credentials;
- publish `SECURITY.md` and responsible disclosure instructions.

### Phase 6 - Public Transparency for ACP / wACP

Public docs must explain:
- what ACP is;
- what wACP is;
- why wACP exists on BSC;
- how ACP → wACP works;
- how wACP → ACP works;
- decimals and conversion rules;
- reserve/backing model;
- fee model;
- bridge risks;
- official contract addresses;
- scam/fake contract warnings;
- how users verify contracts and transactions.

### Phase 6b - sACP (Stable ACP) foundation

ACP-backed USD-targeted commerce stablecoin (distinct from wACP wrap and partner USDC/USDT):
- [x] Spec `docs/STABLECOIN_SACP_SPEC.md`
- [x] BEP-20 source `contracts/bridge-bsc/src/SACP.sol`
- [x] Gateway `SacpGateway.sol` + `DeploySacp.s.sol` + forge tests
- [x] Public API `/v1/sacp/status` + `/v1/sacp/reserve-proof`
- [x] Mint/redeem intents + admin bind + reserve snapshots (`069_sacp_stablecoin`)
- [x] Exchange catalog asset `sacp_bsc` (`stable_peg`)
- [x] Smart Pay: sACP supported asset + ACP→sACP route
- [x] Public docs `/docs/sacp` + compliance checklist `docs/SACP_COMPLIANCE_CHECKLIST.md`
- [ ] S1 mainnet/testnet broadcast + production env addresses
- [ ] S2 live chain indexers for supply/reserve (beyond operator snapshots)
- [ ] S3 merchant checkout UX for currency=SACP
- [ ] S4 legal sign-off before public mint marketing

### Phase 7 - Community Contribution Model

Community baseline:
- GitHub Issues for bug reports and feature requests;
- GitHub Discussions for ideas and technical questions;
- label system (`good first issue`, `help wanted`, `security`, `wallet`, `bridge`, `docs`, `sdk`, `contracts`, `frontend`);
- contributor guide;
- public roadmap board;
- monthly development update;
- changelog;
- release notes.

### Phase 8 - GitHub as Trust Layer

GitHub should function as public proof that ANCAP is a live technical project.

Publish and maintain:
- roadmap progress
- commits
- releases
- smart contract source code
- SDK updates
- security updates
- audit preparation
- integration examples
- public issues
- public milestones

### Immediate execution queue - Open Source Preparation

Sprint 1 - Open Source Preparation
- [~] Create GitHub organization (operator follow-up pending final ownership/name decision plus GitHub org-admin access; `ANCAP` is already taken by an unrelated user profile and current auth cannot inspect/create org state without `admin:org` scope)
- [~] Create public `ancap-docs` (public repo now exists at `https://github.com/ancapcloud/ancap-docs`; the exported docs bundle has been pushed as the first seed commit, `Docs CI` already passed on `main`, repo settings/labels/milestones were applied live from the checked-in seeds, and default-branch protection is now live with required PRs, 1 approval, stale-review dismissal, CODEOWNERS review, conversation resolution, and required status check `Docs CI / docs-bundle`. The in-repo prep still matters: export uses a docs-focused root README, includes public-safe GitHub issue/PR templates plus a baseline CODEOWNERS review-routing seed, carries a dedicated contributor-intake seed plus matching machine-readable metadata so issue/PR lanes and security-report routing stay explicit outside the raw template files, ships an exported repo-bootstrap checklist plus reusable contributor-intake/label/Discussions/milestone/project-board/repo-settings/update-cadence/CI/Dependabot seeds for the first public repo creation/push/settings/labels/Discussions/release-tracking/update-rhythm setup, now also carries a dedicated initial-issues seed plus matching machine-readable metadata so the first public starter backlog can be recreated from checked-in truth instead of chat memory instead of living only in chat memory, which means the prep now effectively covers reusable contributor-intake/label/Discussions/milestone/project-board/initial-issues/repo-settings/update-cadence/CI/Dependabot seeds across the full launch surface, and carries copy-ready pinned-topic text plus monthly-update/release-note/trust-change starter templates, ships a bootstrap-seed README plus machine-readable `.github/bootstrap/*.json` seeds for contributor-intake/labels/milestones/Discussions/project-board/initial-issues/repo-settings/update-cadence/CI metadata so launch setup can be scripted instead of retyped, exports a copy-ready `.github/workflows/docs-ci.yml` plus `docs/ANCAP_DOCS_CI_SEED.md` with the default `Docs CI / docs-bundle` required-check context, exports the matching `.github/bootstrap/ancap-docs-ci-workflow.yml` template referenced by that CI seed so workflow bootstrap does not point at a source-only file, exports a docs-repo-specific `.github/dependabot.yml` plus `docs/ANCAP_DOCS_DEPENDABOT_SEED.md` and `.github/bootstrap/ancap-docs-dependabot.yml` so the public docs repo does not inherit monorepo-only dependency ecosystems by accident, adds `scripts/bootstrap_ancap_docs_repo.py` so public repo creation, repo settings/labels/milestones, live repo verification, and the branch-protection payload can be applied or audited from those checked-in seeds with `gh` instead of launch-day retyping, now also offers `--verify-live --verify-live-community` so seeded labels, milestones, Discussions categories, seeded discussion-topic presence, seeded discussion-topic body alignment, pinned-discussion presence, and seeded starter-issue routing can be checked live against those seeds instead of only via launch notes, and that community verification now emits the operator-facing follow-up detail that was still missing before: unexpected live category names (`General`, `Polls`), per-category description drift, the live URLs/category placement for each seeded bootstrap topic, per-topic body/seed alignment, the explicit project-board auth failure under the current token, and copy-ready reroute commands when an existing seeded starter issue drifts away from its checked-in body summary or milestone/label routing. That same live-verification path now also supports `--format markdown`, turning the current Discussions/project-board drift into a copy-ready operator checklist instead of only text/JSON diagnostics when someone needs to finish the remaining admin follow-up by hand, and now also supports `--output <path>` so that markdown/JSON/text handoff artifacts can be written directly as UTF-8 files instead of depending on shell redirection defaults on Windows. `scripts/generate_ancap_docs_live_followup.py` now wraps the paired current-run handoff generation into one repeatable command (`python scripts/generate_ancap_docs_live_followup.py --repo <owner>/ancap-docs`), writing the default artifact pair `tmp/ancap-docs-live-follow-up-YYYY-MM-DD.md` plus `tmp/ancap-docs-live-follow-up-YYYY-MM-DD.json` so the operator checklist and machine-readable snapshot stay together instead of living only in shell scrollback. By default that wrapper now also refreshes the stable alias pair `tmp/ancap-docs-live-follow-up-latest.md` plus `tmp/ancap-docs-live-follow-up-latest.json`, which gives cron/CI/reporting follow-through a fixed latest verified handoff path without reconstructing the date suffix; `--no-write-latest-alias` is available when a caller intentionally wants dated artifacts without touching the stable aliases, and the wrapper now also refuses `--date-label latest` while latest-alias writes stay enabled so the dated outputs cannot silently collapse onto those stable alias paths. It now also treats `--basename` and `--date-label` as filename components only instead of path fragments, rejecting values like `nested/path` or `..` up front so callers cannot silently escape the chosen `--output-dir`. Those saved markdown/JSON artifacts now also embed artifact metadata (`artifactMetadata` in JSON plus an `Artifact metadata` appendix in markdown) with the generator/bootstrap source paths, UTC generation time, generator repo HEAD provenance, dated artifact paths, and optional latest-alias paths so downstream cron/CI/reporting consumers can inspect the file itself instead of inferring context from filenames or shell scrollback. That wrapper now also keeps successful refreshes concise by default and only echoes the underlying helper stdout/stderr when a generation step fails unless `--verbose-child-output` is set, so routine artifact refreshes do not spam the terminal while still leaving the full checklist/payload in the saved files, and `--fail-on-not-ok` now turns the same saved-artifact path into an exit-code-2 cron/CI drift alarm whenever the generated JSON summary reports `ok=false`. That generated checklist now also includes a dedicated `Discussion UI targets` section with the live Discussions landing URL plus the exact seeded category names/descriptions and the tracked cleanup issue `#5`, plus a `Project board seed targets` section with the checked-in board name/scope/fields/views/notes, copy-ready `gh project create/edit/link` command skeletons, seeded field-create commands, manual board-seeding steps, the current GitHub auth login/token-source/scopes when detectable, the exact `gh auth refresh -h github.com -s read:project` command when project auth is the blocker, and `gh issue edit` commands for starter-issue body-summary or milestone/label rerouting when drift is detected, so the remaining category/project-board/backlog-routing cleanup can be executed from one handoff artifact instead of cross-opening the seed docs. When the live repo/discussion/category ids and checked-in seed bodies are already known, that same Discussions automation map now also emits copy-ready `gh api graphql --raw-field "query=..."` commands for the automatable `createDiscussion` / `updateDiscussion` portion, leaving only the pin/category-lifecycle remainder as explicit UI-only follow-up instead of forcing maintainers to rebuild GraphQL payloads by hand. The helper dry-run output now also prints copy-ready `gh issue create` commands for the seeded starter backlog from `docs/ANCAP_DOCS_INITIAL_ISSUES_SEED.md` / `.github/bootstrap/ancap-docs-initial-issues.json`, so maintainers can open the first public docs queue from checked-in truth instead of manually retyping titles/labels/milestones. Those seeded issues have now also been exercised against the live public repo: `#5` (`Align Discussions categories and pin seeded bootstrap topics`) remains `OPEN` because the Discussions/category/pinning cleanup is still genuinely unfinished, while `#6`, `#7`, and `#8` are now `CLOSED` because their trust-doc / integration-index / wording-sync deliverables are already live and match the current exported source of truth. Current honest live state is better specified now: the three seeded bootstrap topics already exist live at `/discussions/2`, `/discussions/3`, and `/discussions/4`, their bodies match the checked-in seed copy, but they are still unpinned and still sit under GitHub's default `Announcements` wording while the repo also still carries the extra default `General`/`Polls` categories. The helper now documents the real API boundary: GitHub's public GraphQL surface does expose `createDiscussion` / `updateDiscussion` for future missing-topic, topic-body, or category-reassignment automation, but it still does not expose the full category-description/category-set/pinning admin flow needed to close the current seeded-surface drift end-to-end, so that cleanup still needs GitHub UI work or a future owner-capable automation path driven from the checked-in seeds. It rewrites out-of-bundle links to source-monorepo GitHub URLs, validates the standalone docs bundle for broken relative links, drift-guards the exported docs-repo Dependabot file against its bootstrap template inside the public bundle while leaving the source monorepo's broader Dependabot config untouched, and now tolerates GitHub Actions version-only bumps between `.github/workflows/docs-ci.yml` and `.github/bootstrap/ancap-docs-ci-workflow.yml` while still hard-failing structural workflow drift; backend CI now runs the docs export/public-trust regression slice when those inputs change. Remaining gaps on this item: final org ownership decision/migration, aligning live Discussions categories and pinned bootstrap topics with the checked-in seed, and live project-board seeding under the eventual owner once project-capable auth exists.)
- [x] Add README.md
- [x] Add LICENSE
- [x] Add SECURITY.md
- [x] Add CONTRIBUTING.md
- [x] Add CODE_OF_CONDUCT.md
- [x] Add public roadmap
- [x] Add architecture overview
- [x] Add ACP / wACP docs
- [x] Add `.env.example`
- [x] Enable GitHub secret scanning
- [x] Enable branch protection

Sprint 2 - Public Developer Base
- [x] Publish API overview
- [x] Publish Smart QR Pay specification
- [x] Publish ACP / wACP conversion rules
- [x] Publish wACP contract source
- [x] Publish SDK skeleton
- [x] Add example payment integration
- [x] Add example wallet connection flow
- [x] Add GitHub issue templates

Sprint 3 - Community + Audit Readiness
- [x] Add public security policy
- [x] Add responsible disclosure process
- [x] Add bridge risk documentation
- [x] Add contract verification guide
- [x] Add public changelog
- [x] Add release tags
- [x] Add testnet deployment guide
- [x] Add audit checklist

## Source documents this roadmap supersedes

- \PRODUCTION_ROADMAP.md\ -- merged into this document
- \ROADMAP-MONETIZATION.md\ -- merged into this document
- \docs/mobile/ROADMAP.md\ -- merged into Priority 5 section
- \docs/bridge-next-steps.md\ -- merged into Priority 4 section
- \docs/DELIVERY_BOARD.md\ -- archived
- legacy plaintext-key config snippet -- **DELETE. Do not use as reference. Contains leaked secret.**

---

## Priority 0 -- EMERGENCY (fix before next deploy)

### 0.1 Leaked API key remediation [CRITICAL]

Status: [~] Repo-side cleanup is tighter, `docs/SECRET_ROTATION_RUNBOOK.md` now captures the operator follow-through checklist, but external secret rotation and access cleanup still require manual credentialed follow-through.

File: a previously tracked provider/config snippet contained a plaintext API key (redacted here; treat as compromised).

Verification (2026-05-25 / 2026-05-28):
- the tracked plaintext-key snippet is absent from the repo
- repo-side token-shaped examples were removed from tracked docs
- repo scan found no other live leaked-token patterns; the only remaining sk-aw-... matches are this roadmap's own remediation notes / grep example
- `scripts/check_secret_hygiene.py` now gives the repo a repeatable secret-pattern scan so this verification is executable instead of living only as a one-off grep note; default mode scans tracked files and now falls back to git-index content for tracked-but-currently-missing paths so local deletions do not crash the scan or hide still-tracked leaks, the dedicated `--staged` mode scans git-index content so pre-commit leaks cannot hide behind later unstaged cleanup, the optional `--include-untracked` mode also catches token-shaped leaks in local non-ignored temp/export artifacts before they get committed, the `--history-range <rev-range>` mode sweeps the full committed tree state for each commit in the requested recent-history window after cleanup/rotation so a secret cannot hide in unchanged files that diff-only history scans would skip, the clone-safe `--recent-history <count>` mode gives local hooks/operators the same recent-window sweep without assuming `HEAD~N` exists in every clone, the tighter `--pending-push` mode scans the exact local commit history about to leave the workstation using the tracked branch upstream when that ref is still resolvable and otherwise `origin/HEAD..HEAD` with a recent-history fallback only when no push base can be resolved, and it also now supports `--format json --output <path>` for copy-safe evidence handoff without depending on shell redirection. Those JSON artifacts now also carry repo-HEAD provenance (`head_ref`, `head_commit`, dirty/clean working-tree state) so a retained scan can be tied back to the exact checkout that produced it. It catches OpenAI project/service-account prefixes (`sk-proj-`, `sk-svcacct-`), Anthropic prefixes (`sk-ant-`), and GitHub fine-grained/user-to-server/refresh token prefixes (`github_pat_`, `ghu_`, `ghr_`) instead of only the older classic token shapes, `scripts/render_secret_rotation_evidence.py` can now turn the retained tracked/history JSON artifacts into a copy-safe markdown incident worksheet for operator revoke/access-cleanup handoff while preserving that same repo-HEAD provenance in the rendered markdown, now also refuses cross-checkout `head_commit` mismatches in addition to repo-root drift / scope mismatches / reused artifact paths so the handoff packet cannot silently mix evidence from different scans, failed findings now use redacted finding previews so a detection does not copy the live token value into CI logs or shared artifacts, and Windows launcher-only workstations can now run that same scanner / renderer / one-shot bundle path as `py -3 scripts/check_secret_hygiene.py ...`, `py -3 scripts/render_secret_rotation_evidence.py ...`, and `py -3 scripts/generate_secret_hygiene_evidence.py ...` instead of depending on a bare `python` shim. The repo now also carries tracked `.githooks/pre-commit` and `.githooks/pre-push` hooks plus `scripts/install_git_hooks.py` bootstrap so the staged-index scan can run automatically before local commits and the exact pending-push sweep can rerun automatically before local pushes without retyping commands. Those tracked hooks now resolve `python` first, then `python3`, then `py -3`, so the same guard still works on Windows workstations that rely on the Python launcher instead of a bare `python` shim. The installer itself now documents the same launcher reality too: local bootstrap/verification can be run as either `python scripts/install_git_hooks.py` / `python scripts/install_git_hooks.py --check` or `py -3 scripts/install_git_hooks.py` / `py -3 scripts/install_git_hooks.py --check`, depending on which interpreter entrypoint the workstation actually exposes. That installer now has explicit regression coverage for the guard rails that matter here too: refusing to overwrite an existing custom `core.hooksPath` without `--force`, refusing to enable `.githooks` when an expected tracked hook file is missing, reusing an already-correct `.githooks` config while restoring executable bits on the tracked hooks, and a non-mutating `--check` mode for proving the tracked hook wiring is already active.
- `.github/workflows/secret-hygiene.yml` now runs that tracked-files scan on pushes / pull requests, now also runs a history sweep via `python scripts/check_secret_hygiene.py --history-range ... --format json --output tmp/secret-hygiene-history-report.json` with full-history checkout using event-appropriate scope (push/pull_request commit deltas when GitHub provides those SHAs and that rev-range still resolves in the checkout and otherwise a clone-safe `--recent-history 20` fallback, scheduled sweeps on the clone-safe `--recent-history 20` path, and manual sweeps using the same clone-safe recent-history path whenever `history_range` is left blank instead of forcing `HEAD~20..HEAD` into the dispatch form), now also reruns `pytest tests/test_secret_hygiene.py tests/test_release_security_workflows.py -q` in a dedicated workflow job before evidence packaging so the workflow keeps both its scanner/report contract and release/workflow gate contract honest, now also renders and retains `tmp/secret-rotation-evidence.md` (`secret-rotation-evidence`) from those tracked/history JSON artifacts so operator handoff starts from the same redacted evidence bundle, `.github/workflows/release.yml` now also checks out full history and gates tagged releases with the same tracked/history/markdown evidence bundle plus `pytest tests/test_secret_hygiene.py tests/test_release_security_workflows.py -q`, with that release-time bundle now generated through `python scripts/generate_secret_hygiene_evidence.py --recent-history 20` so the release workflow shares the same one-shot local/operator artifact contract instead of maintaining a separate inline scan/render sequence, while still uploading the tracked/history/markdown evidence artifacts before the final explicit secret-hygiene gate step so release-time failures leave behind the redacted handoff bundle instead of exiting too early to retain it. `scripts/generate_secret_hygiene_evidence.py` now wraps the primary scan + secondary history/pending-push scan + markdown handoff render into one repeatable local command, can optionally include untracked temp/export artifact coverage in that primary artifact via `--include-untracked`, can instead switch that primary artifact onto the staged git index via `--staged-primary` when release/pre-commit evidence should follow the index rather than the working tree, now also refuses reused primary/secondary/output file paths before writing any artifact, the handoff renderer now refuses mismatched primary-vs-history/pending-push artifact pairs, repo-root drift, cross-checkout `head_commit` mismatches, plus reused input/output file paths, and the workflow/report path now retains both `tmp/secret-hygiene-report.json` and the history-sweep `tmp/secret-hygiene-history-report.json` plus the derived markdown handoff artifact instead of depending on pasted shell logs
- `docs/SECRET_ROTATION_RUNBOOK.md` now captures the operator-side containment / revoke / replace / evidence checklist so the remaining manual work is explicit instead of living only in status notes

Action (in order):
1. Revoke the compromised provider key at the upstream dashboard/API
2. Generate a new key and store only in CI secrets / env management
3. Remove or replace any tracked docs/snippets that demonstrate direct key embedding
4. Run repo-side secret scans:
   - `python scripts/check_secret_hygiene.py`
   - `python scripts/check_secret_hygiene.py --staged`
   - optional local automation: `python scripts/install_git_hooks.py` (or `py -3 scripts/install_git_hooks.py` on Windows hosts that only expose the launcher) to wire the tracked `.githooks/pre-commit` and `.githooks/pre-push` hooks so git runs the staged scan automatically before commit and the exact pending-push sweep automatically before push; those tracked hooks resolve `python` first, then `python3`, then `py -3`, so the same bootstrap still works on Windows hosts that expose the Python launcher instead of a bare `python` shim; the installer refuses to overwrite an existing custom `core.hooksPath` unless you pass `--force`, refuses to enable `.githooks` when either tracked hook file is missing, and if `core.hooksPath` already points at `.githooks` it only restores executable bits on those tracked hooks instead of rewriting config
   - optional non-mutating verification: `python scripts/install_git_hooks.py --check` (or `py -3 scripts/install_git_hooks.py --check` on that same Windows launcher-only setup) when you want to prove the local repo is still wired to the tracked hook path before a release/push without rewriting config
   - `python scripts/check_secret_hygiene.py --include-untracked`
   - `python scripts/check_secret_hygiene.py --history-range HEAD~20..HEAD`
   - optional clone-safe local recent-window variant: `python scripts/check_secret_hygiene.py --recent-history 20`
   - optional exact local pre-push variant: `python scripts/check_secret_hygiene.py --pending-push`
   - on Windows hosts that only expose the launcher, those same direct scan commands can be run as `py -3 scripts/check_secret_hygiene.py ...`
   - `python scripts/check_secret_hygiene.py --format json --output tmp/secret-hygiene-report.json`
   - optional CI/backfill history artifact path: `python scripts/check_secret_hygiene.py --history-range HEAD~20..HEAD --format json --output tmp/secret-hygiene-history-report.json`
   - optional markdown handoff artifact: `python scripts/render_secret_rotation_evidence.py --tracked-report tmp/secret-hygiene-report.json --history-report tmp/secret-hygiene-history-report.json --output tmp/secret-rotation-evidence.md`
   - if the second artifact is a local `--pending-push` JSON report instead of a history sweep, the same renderer also accepts `--secondary-report tmp/secret-hygiene-pending-push-report.json`
   - on Windows hosts that only expose the launcher, the same renderer command can be run as `py -3 scripts/render_secret_rotation_evidence.py ...`
   - optional one-shot local bundle: `python scripts/generate_secret_hygiene_evidence.py` (or add `--pending-push` / `--history-range ...`) to generate the primary JSON artifact, the secondary history/pending-push artifact, and the derived markdown worksheet in one repeatable command; it now also refuses reused primary/secondary/output file paths before writing any artifact
   - on Windows hosts that only expose the launcher, that same one-shot bundle can be run as `py -3 scripts/generate_secret_hygiene_evidence.py ...`
   - add `--include-untracked` to that one-shot bundle when local non-ignored temp/export artifact coverage matters too, so the primary JSON artifact matches the stricter local leak sweep instead of tracked-files-only scope
   - add `--staged-primary` to that same one-shot bundle when the primary evidence artifact should reflect the staged git index rather than the working tree after a local cleanup-before-restage scenario
   - that renderer now refuses mismatched primary-vs-history/pending-push artifact pairs, repo-root drift, or reused input/output file paths so operator handoff cannot silently package the wrong evidence set
   - CI/release automation now retains that same derived markdown worksheet as artifact `secret-rotation-evidence`, so operator follow-through can start from the redacted handoff bundle instead of manually re-rendering it from downloaded JSON
   - prefer the JSON artifact (or the derived markdown worksheet) for evidence handoff; failed findings use redacted finding previews on purpose so scan logs do not become a second leak surface
   - if you still want a raw grep fallback for ad-hoc inspection:
     \\\bash
     grep -rn "sk-aw-\|sk-prod-\|sk-proj-\|sk-svcacct-\|sk-ant-\|sk_live_\|pk_live_\|whsec_\|ghp_\|ghs_\|gho_\|github_pat_\|ghu_\|ghr_\|rk_live_" . \
       --include="*.py" --include="*.json*" --include="*.yml" \
       --include="*.yaml" --include="*.ts" --include="*.tsx" 2>/dev/null
     \\
5. Enable GitHub secret scanning: Settings > Code security and analysis > Secret scanning > On + Push protection > On

Reference: GitHub Docs -- any exposed secret = assume compromised, revoke immediately.
### 0.2 Insecure dev defaults in production configs [CRITICAL]

Status: [x] Done for the current host/runtime. Repo-side hardening is in place and test-covered, `docs/PRODUCTION_SECRET_BASELINE.md` captures the operator provisioning/evidence checklist, and the current prod-like host runtime now has real required secrets provisioned outside the repo with healthy verification.

Files: \docker-compose.prod.yml\, \pp/config.py\

Verification (2026-05-25):
- `docker-compose.prod.yml` now requires `DATABASE_URL`, `POSTGRES_PASSWORD`, `SECRET_KEY`, `CURSOR_SECRET`, `CRON_SECRET`, and `ACP_RPC_TOKEN` (acp-node) without production fallbacks; compose `${VAR:?message}` guards make `docker compose config/up` fail immediately when any required secret is unset, and the API service now explicitly receives `POSTGRES_PASSWORD` too so the app-level production parity guard can validate bundled-postgres `DATABASE_URL` / `POSTGRES_PASSWORD` consistency at runtime instead of only in deploy-script preflight
- `app/config.py` fails fast in `environment=production` when `SECRET_KEY`, `CURSOR_SECRET`, or `CRON_SECRET` are missing/placeholder-like, rejects blank or non-absolute `DATABASE_URL` values and the insecure bundled-db default credentials, rejects placeholder/default DB passwords hidden inside `DATABASE_URL`, URL-decodes bundled-postgres passwords before comparison, and when the bundled compose `postgres` service is targeted - whether via authority host `@postgres:...` or socket/query host `?host=postgres` - it now also requires a real non-default non-placeholder `POSTGRES_PASSWORD` plus exact `DATABASE_URL` / `POSTGRES_PASSWORD` parity
- `scripts/deploy-ancap-cloud.ps1`, `scripts/deploy-ancap-cloud.sh`, and `scripts/rebuild-prod.ps1` now load repo-root `.env`, assert those required production secrets are present (including `POSTGRES_PASSWORD` for the bundled compose postgres service), reject placeholder-like `SECRET_KEY` / `CURSOR_SECRET` / `CRON_SECRET` values before compose startup, reject the insecure default `DATABASE_URL`, reject placeholder/default DB passwords embedded in `DATABASE_URL`, reject `DATABASE_URL` / `POSTGRES_PASSWORD` drift for the bundled compose postgres service (including socket/query-host DSNs such as `?host=postgres`), avoid shadowing compose interpolation with the bridge-only env file, and the bash helper now parses repo-root `.env` directly so CRLF-authored env files do not break preflight on Linux/WSL
- PowerShell deploy/rebuild and bash deploy preflight now also correctly accept URL-encoded bundled-postgres passwords inside `DATABASE_URL` (for example `p%40ss%3Aword`) while still comparing them against the raw `POSTGRES_PASSWORD` value, avoiding false mismatch failures when real secrets contain reserved URL characters, including the socket/query-host `?host=postgres` DSN form and percent-encoded socket-host query variants such as `?host=%70ostgres`
- `tests/test_prod_deploy_scripts.py` now goes beyond string-presence assertions and actually exercises the deploy/rebuild helpers against staged minimal repos, confirming that PowerShell deploy/rebuild and bash deploy can bootstrap required production secrets from a repo-root `.env` without relying on pre-exported shell state, including the CRLF-authored `.env` case for the bash helper and URL-encoded `DATABASE_URL` password handling across authority-host and socket/query-host bundled-postgres DSN variants; it now also directly exercises real `docker compose -f docker-compose.prod.yml config --quiet` success/failure behavior so the compose required-var guard itself is covered, including fail-fast proof that a missing required secret does not dump the other provided secret values to stdout/stderr
- `scripts/deploy-ancap-cloud.ps1` no longer relies on unsupported `??` null-coalescing syntax in Windows PowerShell error/log formatting, so deploy-script preflight failures now surface the intended guard messages instead of a parser error before any real validation runs
- the deploy helpers now also run `docker compose -f docker-compose.prod.yml config --quiet` before any build/start step, so compose interpolation or missing-required-var failures stop the deploy/rebuild path before image work begins without dumping resolved secrets to stdout; the staged-script tests assert that config validation is actually invoked for PowerShell deploy/rebuild and bash deploy, and the deploy helpers expose opt-in `-SkipPostDeployChecks` / `--skip-post-deploy-checks` switches for controlled staged-test contexts while keeping live `/api/v1/system/health`, `/api/v1/system/ready`, and `/internal/frontend-build` verification enabled by default on the real deploy path
- deploy-facing docs now consistently call out those required secrets before production compose startup, including `README.md`, `PRODUCTION_ROADMAP.md`, `.github/RELEASE_PROCESS.md`, and `docs/PRODUCTION_SECRET_BASELINE.md`; they explicitly note that `DATABASE_URL` must include the same real DB password as `POSTGRES_PASSWORD` when targeting the bundled compose postgres service, and the new baseline doc captures the remaining operator-side provisioning / evidence checklist so the manual env/CI follow-through is explicit instead of living only in status notes; the prod-like compose/docs truth now also records that `POSTGRES_PASSWORD` is passed through to the API container so the same parity rule is enforced by app startup in real runtime, not just by helper-script preflight
- current host follow-through is now explicitly verified against real provisioned runtime state, not only repo-side docs/tests: `docker compose -f docker-compose.prod.yml config --quiet` succeeds under the current host secret set, the rendered compose model includes `POSTGRES_PASSWORD` in the API service environment, the required `DATABASE_URL`, `POSTGRES_PASSWORD`, `SECRET_KEY`, `CURSOR_SECRET`, and `CRON_SECRET` values are present from repo-root `.env` with no placeholder-like values, bundled-postgres password parity holds, and `http://127.0.0.1:8080/api/v1/system/health` plus `/api/v1/system/ready` both return healthy responses on the current host
- `pytest tests/test_config_admin_ids.py tests/test_system.py tests/test_prod_deploy_scripts.py -q` passes with coverage for the production secret guard, explicit bundled-postgres `POSTGRES_PASSWORD` requirements, URL-encoded bundled-postgres password acceptance in both app config and deploy-script preflight (including `?host=postgres` and percent-encoded `?host=%70ostgres` socket/query-host DSNs), deploy-script preflight rejection of placeholder-like app secrets and insecure/default/invalid DB settings, repo-root `.env` bootstrap behavior, `DATABASE_URL` / `POSTGRES_PASSWORD` mismatch rejection, direct compose required-var success/failure coverage for `docker compose -f docker-compose.prod.yml config --quiet`, explicit compose proof that `POSTGRES_PASSWORD` is rendered into the API service environment for bundled-postgres prod runs, compose-config preflight invocation in deploy helpers, and cron-secret-gated jobs endpoints

Fix:
- \secret_key\ must not have a fallback default in production-configured files -- must be a required env var with no insecure fallback
- \cursor_secret\ dev fallback must not exist in any file that could be docker-compose-prodd
- production \DATABASE_URL\ must not silently keep insecure bundled-db local defaults
- Add startup guard: if \ENV == "production"\ and a required secret is missing -- fail fast

---

## Priority 1 -- CI/CD honesty and security automation

### 1.1 Fix backend CI soft-fails [HIGH]

Status: [x] Done. `backend-ci.yml` now fails on Bandit findings and on Docker build errors (no `|| true`, no invalid `--target deps`).

File: \.github/workflows/backend-ci.yml\

\\\diff
# Bandit -- must fail the build on findings
- run: bandit -r app/ -f txt 2>&1 | tee bandit-report.txt || true
+ run: bandit -r app/ -f txt 2>&1 | tee bandit-report.txt

# Docker build check -- the line below has two bugs:
#   (1) --target deps stage does NOT exist in root Dockerfile
#   (2) || true makes it always pass even on real build errors
- run: |
-     docker build --target deps -t ancap:build-check . 2>&1 | tail -20 || true
-     docker build -t ancap:build-check . 2>&1 | tail -10 || true
+ run: docker build -t ancap:build-check .
\\\

Exit criteria: CI build fails on Bandit HIGH/medium findings. CI build fails on Docker build error.

### 1.2 Enable Dependabot [HIGH]

Status: [x] Done. Dependabot config is in repo, GitHub vulnerability alerts / security update automation are enabled, secret scanning + push protection are enabled, and dependency PRs now have an explicit review gate.

Files: `.github/dependabot.yml`, `.github/workflows/dependency-review.yml`, `tests/test_dependency_review_workflow.py`

Verification (2026-05-26):
- `.github/dependabot.yml` covers pip, frontend npm, mobile npm, and GitHub Actions with weekly schedules
- `GET /repos/ancapcloud/ancap/vulnerability-alerts` returns `204 No Content`, confirming GitHub vulnerability alerts are enabled
- `gh api repos/ancapcloud/ancap --jq ".security_and_analysis"` reports:
  - `dependabot_security_updates: enabled`
  - `secret_scanning: enabled`
  - `secret_scanning_push_protection: enabled`
- new workflow `.github/workflows/dependency-review.yml` runs `actions/dependency-review-action@v4` on PRs that change Python or npm dependency manifests / lockfiles and fails on `moderate`+ findings
- `pytest tests/test_dependency_review_workflow.py tests/test_system_jobs_tick_workflow.py -q` passes

Exit criteria: satisfied - dependency update automation is enabled, secret scanning / push protection are on, and dependency PRs get a real review gate instead of relying on docs-only intent.

### 1.3 Add CodeQL scanning [HIGH]

Status: [x] Done. The repo uses an explicit advanced CodeQL workflow, recent real GitHub runs succeeded, and alerts are being published into GitHub code scanning.

File: `/.github/workflows/codeql.yml`

Verification (2026-05-26):
- `.github/workflows/codeql.yml` scans Python, JavaScript/TypeScript, and GitHub Actions on push / pull_request plus the weekly Monday 06:00 UTC schedule
- recent successful real CodeQL runs on `master`:
  - `26463212516` - `fix(frontend): remove duplicate page backgrounds after layout rollout`
  - `26460632345` - `fix(ci): harden e2e smoke and system jobs guards`
  - `26460162797` - `fix(ci): stabilize frontend e2e smoke and golden path`
- `GET /repos/ancapcloud/ancap/code-scanning/alerts` returns live CodeQL results (currently 89 open alerts; sample rule: `js/unused-local-variable` created `2026-05-26T16:09:58Z`), proving the workflow is publishing findings into GitHub code scanning
- `GET /repos/ancapcloud/ancap/code-scanning/default-setup` currently reports `state: not-configured`, which is expected because this repo uses the explicit workflow above instead of GitHub's default setup wizard

Exit criteria: satisfied - CodeQL is running on the intended languages in real GitHub Actions and feeding the code-scanning surface.

### 1.4 Playwright E2E in CI [HIGH]

Status: [x] Done. The full local CI-like smoke path is green and the same GitHub Actions `Frontend CI` / `e2e-tests` path completed successfully on a real push.

Verification (2026-05-26):
- `.github/workflows/frontend-ci.yml` contains an `e2e-tests` job that:
  - boots `postgres`, `redis`, and `api`
  - waits for `/v1/system/health`
  - runs `alembic upgrade head`
  - builds/starts the frontend on port `3001`
  - installs Playwright Chromium and runs `npx playwright test`
  - uploads Playwright artifacts and tears down services afterward
- `frontend-app/playwright.config.ts` is aligned with the CI pattern and accepts `PLAYWRIGHT_BASE_URL` overrides
- the repo contains real E2E specs under `frontend-app/e2e/` covering golden-path, growth, contracts, hydration, and public-surface flows
- local CI-like backend validation succeeds in isolated compose projects, including the current honest `3001/8001` path:
  - `docker compose -p ancap-e2e-ci up -d postgres redis api`
  - `docker compose -p ancap-e2e-ci exec -T api alembic upgrade head`
  - `http://127.0.0.1:8001/v1/system/ready` returned `{"status":"ready","checks":{"database":true,"redis":true}}`
  - `scripts/run-e2e-ci-smoke.ps1 -ProjectName ancap-ci-cycle -KeepStack -SkipBrowserInstall -SkipNpmCi` passes on the GitHub-faithful `3001/8001` path with `13 passed, 1 skipped`
  - `scripts/run-e2e-ci-smoke.ps1 -ProjectName ancap-ci-verify-20260526b -ApiPort 18002 -PostgresPort 15433 -RedisPort 16380 -FrontendPort 3312 -SkipBrowserInstall -SkipNpmCi` also passes on a fully isolated alternate-port path with `13 passed, 1 skipped`
- `scripts/run-e2e-ci-smoke.ps1` now does a stricter real-stack check on isolated ports, cleans up stale repo-owned frontend listeners before retrying `next start`, and fails fast with an explicit reusable message when Docker port bindings are already occupied by another smoke stack instead of surfacing the raw daemon bind error later during `docker compose up`
- live local CI-like verification on 2026-05-26 exposed and fixed real stack/runtime issues before GitHub CI could hide them:
  - `docker-compose.yml` did not pass `CORS_ORIGINS` into the dev API container, so isolated smoke stacks on alternate frontend ports (for example `3311`) silently fell back to the app default allowlist and cross-origin browser calls failed with UI-level `Failed to fetch`
  - this broke authenticated Playwright flows on `/contracts/{id}`, `/strategies/{id}`, and `/runs/{id}` even though direct API calls and static-page smoke tests still passed
  - `docker-compose.yml` now forwards `CORS_ORIGINS` into the API service with the current dev-safe default allowlist, so CI/local smoke runs can override it for alternate frontend ports without patching app config
  - `tests/test_cors_dev_stack.py` now locks that compose-level env pass-through in place
  - the remaining last red spec in the full smoke run turned out to be a false Playwright assumption in `frontend-app/e2e/ancap.ui.spec.ts`, not an app/runtime defect: the responsive unauthenticated header intentionally renders duplicate `/login` and `/register` links across desktop/mobile layouts, so the old raw `locator('a[href="/login"]')` assertion hit strict-mode ambiguity with one hidden duplicate
  - `frontend-app/e2e/ancap.ui.spec.ts` now scopes those assertions to the visible header and uses role-based link expectations, which matches the real responsive UI contract
- first real GitHub Actions success is now recorded:
  - workflow: `Frontend CI`
  - run: `26460162796`
  - conclusion: `success`
  - push SHA: `59a59b0d38397b34f0f26992a183a90d59efc340`
  - URL: `https://github.com/ancapcloud/ancap/actions/runs/26460162796`
  - the `e2e-tests` job completed successfully in `4m44s`

Fix: Keep the `e2e-tests` job in `frontend-ci.yml`, keep `scripts/run-e2e-ci-smoke.ps1` as the repeatable repro path, and preserve the compose-level `CORS_ORIGINS` pass-through that made the CI-faithful browser path honest again.

Files needed: `playwright.config.ts` and the E2E specs already exist; local repro helper now lives in `scripts/run-e2e-ci-smoke.ps1`.

Exit criteria: satisfied - the same E2E path now runs successfully in GitHub Actions on a real push.

### 1.5 RESTRICT ops/diagnostics endpoints [HIGH]

Status: [x] Done. Repo-side tier split and platform-admin protection are implemented, test-covered, and now live-verified on the prod-like path.

Files: `app/api/routers/system.py`, nginx/proxy config

Problem:
- `GET /system/health/full` does external LLM probe on every request
- `GET /system/economy-health` pings ACP RPC, returns operational details
- `GET /system/diagnostics` exposes `acp_rpc_url`, driver info
- All of the above are unauthenticated

Fix: Split into three tiers:
- **Tier 1 -- liveness**: `GET /system/health` (DB + Redis only, no external I/O, < 50ms)
- **Tier 2 -- readiness**: `GET /system/ready` (local checks, no external HTTP)
- **Tier 3 -- deep diagnostics** (internal only, platform-admin auth required):
  - `GET /internal/ops/deep-health`
  - `GET /internal/ops/diagnostics`
  - LLM probe: run async in background, cache result 60s
  - ACP RPC probe: run async in background, cache result 30s

Verification (2026-05-26):
- `app/api/routers/system.py` exposes:
  - `GET /v1/system/health` as lightweight liveness
  - `GET /v1/system/ready` as DB+Redis readiness
  - `GET /v1/system/health/full` as public local-only expanded health
  - `GET /v1/internal/ops/diagnostics`, `/deep-health`, and `/economy-health` behind `require_platform_admin`
- `tests/api/test_system_economy_health.py` passes for internal ops auth/shape coverage and now also locks the intended probe-refresh boundary: public `GET /v1/system/health/full` must not schedule external LLM/ACP probe refreshes, while internal `GET /v1/internal/ops/deep-health` does schedule the cached async refresh path; it also now proves internal deep-health reports the LLM check as degraded until a configured provider probe actually succeeds, instead of treating mere configuration as operational success
- `tests/test_nginx_security_headers.py` passes, confirming proxied nginx locations hide upstream security headers and re-add the canonical in-proxy header set
- `tests/test_system.py` now also covers the public `/v1/system/ready` and `/v1/system/health/full` response shapes, including proof that the public `health/full` payload does not expose `acp_rpc_url`
- live prod-like verification on `http://127.0.0.1:8080` now confirms the public surfaces meet the latency target without external I/O:
  - `/api/v1/system/health` -> `200` in `0.0150s`
  - `/api/v1/system/ready` -> `200` in `0.0111s`
  - `/api/v1/system/health/full` -> `200` in `0.0226s`
- unauthenticated access to `GET /api/v1/internal/ops/diagnostics` on the same prod-like path is denied with `401`, confirming deep diagnostics are no longer public

Exit criteria: satisfied - public endpoints return < 200ms without external I/O, and deep diagnostics remain internal/admin-protected.

### 1.6 Separate jobs_tick from HTTP [HIGH]

Status: [x] Done. The async enqueue path is implemented, test-covered, scheduled in GitHub Actions, and now live-verified on the prod-like runtime; the synchronous route remains manual emergency-only.

File: \pp/api/routers/system.py\

Problem: \POST /system/jobs/tick\ runs 20+ sequential jobs (edges_daily, agent relationships, auto limits, circuit breaker, reputation, referrals, notifications, leaderboards, activity feed, governance checks, graph enforcement, staking rewards, ledger invariant check, bridge reconciliation, mobile indexer) -- all in one HTTP request. This is a mini-orchestrator in a request handler.

Fix: Hybrid approach:
- \POST /system/jobs/tick/async\ -- enqueues job, returns \202 Accepted\ immediately (background task via FastAPI BackgroundTasks or Redis queue)
- \POST /system/jobs/tick\ -- kept for manual emergency ops triggers only
- Add GitHub Actions scheduled workflow (runs every 5 min) that calls \/system/jobs/tick/async\
- Jobs run with retry and dead-letter queue

Verification (2026-05-26):
- `.github/workflows/system-jobs-tick.yml` exists and schedules every 5 minutes
- the workflow still POSTs `X-Cron-Secret` to `ANCAP_SYSTEM_JOBS_TICK_URL`, but now also fails fast unless that secret URL ends with `/v1/system/jobs/tick/async`, so repo/GitHub secret drift cannot silently route scheduler traffic back to the sync/manual endpoint
- latest real scheduled GitHub run succeeded:
  - workflow: `System Jobs Tick`
  - run: `26460430404`
  - conclusion: `success`
- `tests/test_system.py` already covers `POST /v1/system/jobs/tick/async` returning `202 Accepted` plus cron-secret/retry/dead-letter behavior
- `tests/test_system_jobs_tick_workflow.py` now locks the async-endpoint guard into the workflow file
- live prod-like enqueue verification now also succeeds:
  - `POST /api/v1/system/jobs/tick/async` with the real `X-Cron-Secret` returned `202` in `0.4565s`
  - the created `system_job_runs` row `6196cb8c-3546-4316-bb5b-2751c02db0f3` completed as `succeeded` with `attempts=1` and `trigger_source=api`

Exit criteria: satisfied - the scheduled path now uses the async enqueue route, returns in < 1s, and heavy work completes in background job records instead of the scheduler request path.

---

## Priority 2 -- Domain model and skipped tests

### 2.1 Pool ownership model [HIGH]

Status: [x] Done. `Pool.owner_agent_id` is present in the data model and migration history, pool create/read APIs expose it, owner-aware allocation enforcement is live in `POST /v1/ledger/allocate`, and the repo docs now describe the backward-compatible legacy-null-owner rule explicitly.

Files: `app/db/models.py` (Pool class), `alembic/versions/911774c4bec4_add_owner_agent_id_to_pools.py`, `app/api/routers/pools.py`, `app/api/routers/ledger.py`, `tests/test_ledger.py`, `tests/test_pools.py`, `README.md`

Verification (2026-05-26):
- `Pool.owner_agent_id` exists in `app/db/models.py`
- migration `911774c4bec4_add_owner_agent_id_to_pools.py` adds the column in-repo
- pool create/get/list responses include `owner_agent_id`
- creating a pool optionally validates and persists `owner_agent_id`
- `POST /v1/ledger/allocate` now:
  - requires caller ownership when `pool.owner_agent_id` is set
  - allows authenticated backward-compatible allocation when it is unset
- `README.md` documents:
  - optional `owner_agent_id` on `POST /v1/pools`
  - `owner_agent_id` in pool read surfaces
  - owner-enforced allocation only for owned pools, with explicit legacy-null-owner compatibility
- `pytest tests/test_pools.py tests/test_ledger.py -q` passes (`9 passed`)

Exit criteria: satisfied - pool ownership is implemented, verified, and documented; any future product decision to forbid legacy null-owner pools is a separate tightening pass, not unfinished core ownership work.

### 2.2 Fix economy_health async/sync bug [MEDIUM]

Status: [x] Done. `ops_economy_health` is already async in `app/api/routers/system.py`, and ACP RPC probing now uses cached `httpx.AsyncClient` background refresh helpers instead of synchronous `httpx.post()` in-request.

File: `app/api/routers/system.py`

Verification (2026-05-25):
- `@_internal_router.get("/economy-health")` is implemented as `async def ops_economy_health(...)`
- ACP RPC probing is handled through `_refresh_acp_rpc_probe_cache()` with `httpx.AsyncClient`
- `tests/api/test_system_economy_health.py` passes against the current internal ops surface

### 2.3 Unskip ledger invariant test [MEDIUM]

Status: [x] Done. `tests/api/test_growth_layer.py::test_jobs_tick_sets_ledger_halt_blocks_faucet` now injects a malformed one-sided `transfer` event directly, runs `/v1/system/jobs/tick`, and verifies the faucet is blocked once the ledger invariant halt flag is raised.

File: \	ests/api/test_growth_layer.py\

### 2.4 Resolve test_unit.py bcrypt skip [LOW]

Status: [x] Done. `tests/test_unit.py` no longer contains the old bcrypt-backend skip, unit auth hashing tests pass directly against `bcrypt`, and dependency metadata now matches the actual runtime implementation instead of still declaring the stale `passlib[bcrypt]` extra.

Files: `tests/test_unit.py`, `app/services/auth.py`, `requirements.txt`, `pyproject.toml`

Verification (2026-05-25):
- `tests/test_unit.py` contains no `pytest.skip("bcrypt backend not available")` guard anymore
- `app/services/auth.py` hashes/verifies passwords directly with `bcrypt`
- `requirements.txt` now pins `bcrypt==5.0.0`
- `pyproject.toml` now declares `bcrypt>=5.0` instead of the stale `passlib[bcrypt]` extra
- `pytest tests/test_unit.py -q` passes

---

## Priority 3 -- Security hardening

### 3.1 Auth token: localStorage to HttpOnly cookies [MEDIUM]

Status: [x] Done. Browser auth now prefers HttpOnly `ancap_token` cookies instead of JS-readable auth storage, shared authenticated requests consistently send `X-Requested-With`, and the live prod-like stack confirms the cookie/CSRF path behaves as intended.

Files: `frontend-app/src/components/AuthProvider.tsx`, `frontend-app/src/lib/api.ts`, `app/api/deps.py`, `app/api/routers/auth.py`, `frontend-app/e2e/*.spec.ts`

Verification (2026-05-26):
- `AuthProvider` no longer depends on `auth.getToken()` to decide signed-in bootstrap; it restores cached user display data only and then resolves real auth from `/users/me`
- frontend shared API client now always sends `X-Requested-With: XMLHttpRequest`
- `frontend-app/src/lib/api.ts` centralizes raw authenticated fetch helpers (`apiFetchRaw` / shared headers), and the admin overview, funds create, vertical propose, profile loads, agent follow/unfollow, logout, and workflow revenue CSV export flows use that shared path instead of bespoke client-side fetch calls
- repo scan of `frontend-app/src` shows no remaining auth-token writes to localStorage; `ancap_user` is kept only as non-secret UI bootstrap data while Playwright auth seeders stage `ancap_token` as a cookie
- cookie-authenticated unsafe requests fail closed in `app/api/deps.py` unless `X-Requested-With` is present, while explicit Bearer-token clients remain allowed
- auth cookie set/clear paths use `SameSite=lax` (required for ancap.cloud ↔ api.ancap.cloud subdomain cookie sharing)
- local prod-like runtime truth on `http://127.0.0.1:8080` is healthy (`/api/v1/system/health` 200, `/api/v1/system/ready` ready, `/internal/frontend-build` matches build id `32b5d58`)
- `pytest tests/test_auth.py tests/test_system.py tests/api/test_system_economy_health.py -q` passes
- `npm run build` in `frontend-app` passes

Exit criteria: satisfied - no Bearer tokens are stored in localStorage for auth and CSRF protection is active on cookie-authenticated unsafe routes.

### 3.2 SameSite cookie + CORS hardening [MEDIUM]

Status: [x] Done. Auth cookies are `SameSite=lax`, CORS is explicit, and live prod-like preflight checks confirm the intended same-site browser path while rejecting disallowed origins.

Files: `app/main.py`, `app/api/routers/auth.py`, `infra/nginx/default.conf`, `docker-compose.prod.yml`

Verification (2026-05-26; docs aligned 2026-09-28):
- auth cookie set/clear paths use `SameSite=lax`
- `app.main` CORS middleware keeps explicit `allow_origins` and explicit allowed methods/headers (`Authorization`, `Content-Type`, `Idempotency-Key`, `X-API-Key`, `X-Bridge-Operator-Secret`, `X-Cron-Secret`, `X-Requested-With`, `X-Request-Id`)
- `app.main` already injects `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy`, and `Permissions-Policy`
- `infra/nginx/default.conf` already matches `DENY` + HSTS across public locations
- live prod-like preflight to `OPTIONS /api/v1/auth/logout` with `Origin: https://ancap.cloud` and `Access-Control-Request-Headers: content-type,x-requested-with` now returns `200 OK` with `access-control-allow-origin: https://ancap.cloud`, `access-control-allow-credentials: true`, and `x-requested-with` present in the explicit allowlist
- the same preflight from a disallowed origin returns `400 Disallowed CORS origin`, confirming the app stayed explicit instead of drifting back to wildcard behavior
- `tests/test_auth.py` now locks those allowed-origin and rejected-origin preflight expectations in addition to the existing cookie-authenticated logout guard

Exit criteria: satisfied - browser preflight/runtime verification is in place and any future route-specific header expansion must be added deliberately to the explicit CORS allowlist.

### 3.3 Production security header alignment [LOW]

Status: [x] Done. Inner prod proxy, outer origin nginx, and public Cloudflare-routed responses are now aligned on the canonical security-header set.

Files: `infra/nginx/default.conf`, production nginx config

Verification (2026-05-28):
- added `proxy_hide_header` for `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy`, and `Strict-Transport-Security` in every proxied location of `infra/nginx/default.conf` before nginx re-adds the canonical header set
- this fixes the real local prod-like defect where `/api` responses previously carried duplicate security headers from both FastAPI and nginx
- `docker compose exec -T proxy nginx -t` ✅
- `docker compose exec -T proxy nginx -s reload` ✅
- live local checks now show a single canonical header set on both `http://127.0.0.1:8080/` and `http://127.0.0.1:8080/api/v1/system/health`:
  - `X-Frame-Options: DENY`
  - `X-Content-Type-Options: nosniff`
  - `Referrer-Policy: strict-origin-when-cross-origin`
  - `Permissions-Policy: geolocation=(), microphone=(), camera=()`
  - `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- production follow-through on the server was completed:
  - `/opt/ancap-migration/current/infra/nginx/default.conf` on `ancap-server` already contains `proxy_hide_header` rules for proxied locations
  - `docker compose -f docker-compose.prod.yml exec -T proxy nginx -t` on `ancap-server` succeeds
  - `docker compose -f docker-compose.prod.yml exec -T proxy nginx -s reload` on `ancap-server` succeeds
  - direct origin checks now show the inner container proxy is clean: `http://127.0.0.1:8080/api/v1/system/health` returns a single canonical set
  - direct HTTPS-to-origin checks with `Host: ancap.cloud` / `Host: api.ancap.cloud` initially exposed duplicate headers at the outer nginx layer, so the outer vhost files under `/etc/nginx/conf.d/domains/*.conf` and `*.ssl.conf` were patched to hide upstream security headers before `proxy_pass`, then `sudo systemctl reload nginx` was applied
  - after that outer-nginx patch, direct origin HTTPS checks return the canonical single set (`DENY`, `nosniff`, `strict-origin-when-cross-origin`, `camera=(), microphone=(), geolocation()`, HSTS) with no duplicates
- public Cloudflare-routed responses are now aligned with origin truth too:
  - `https://ancap.cloud/api/v1/system/health` now returns `X-Frame-Options: DENY` and `Referrer-Policy: strict-origin-when-cross-origin`
  - `https://api.ancap.cloud/v1/system/health` now returns the same canonical set while preserving the origin debug header `X-Debug-Vhost: api-https`
  - both public endpoints now return the expected `Permissions-Policy: camera=(), microphone=(), geolocation()` and `Strict-Transport-Security: max-age=31536000; includeSubDomains` headers too
- `tests/test_nginx_security_headers.py` still guards the in-repo nginx config so proxied locations must hide upstream security headers before re-adding the canonical set

Exit criteria: satisfied - local, origin, and public Cloudflare-routed responses now match the intended single-source-of-truth security header set.

---

## Priority 4 -- Monetization depth

**Not a work-stop blocker.** First ACP-first revenue loop is live (paid workflows, marketplace, subscriptions, paid API, claim codes, merchant pay). Remaining work is depth + conversion friction — not “monetization missing.”

ACP acquisition path (2026-10-04): `/buy-acp` leads with bridge + credits + **MoonPay Commerce (Helio) checkout** + spend CTAs; Stripe optional. Mobile Exchange auth-settle for USDT→ACP. V3 Pancake bootstrap `0xe626…f5e1` published as shallow; checkout oracle stays on V2 until `WACP_ORACLE_USE_V3` + quote smoke (`docs/GOLDEN_PATH_ACP_SPEND.md`, `docs/HELIO_MOONPAY_COMMERCE.md`).

### 4.0b MoonPay Commerce / Helio checkout [HIGH]

Status: [~] Adapter shipped: env `HELIO_*`, `GET /v1/commerce/helio/status`, signed `POST /v1/commerce/helio/webhook`, `/buy-acp` `@heliofi/checkout-react` widget, deploy sync via GitHub secrets. Pay Link created for USDC (dynamic). Remaining: live checkout smoke + operator ACP ledger credit from webhook (auto-credit not wired).

### 4.0c WebID KYC slot + physical card / Apple Pay waitlist [MEDIUM]

Status: [x] P0 — docs (`docs/WEBID_KYC_AND_CARD_ISSUING_PATH.md`), `/cards` waitlist (`interest=physical_card_apple_pay`), fail-closed `GET /v1/commerce/webid/status` (`issues_cards=false`). WebID is KYC/KYB only; plastic + Apple Pay need a separate licensed BaaS/EMI after counsel. P1 sandbox API and P2 issuer track remain open.

### 4.1 Stripe / fiat payment gateway [HIGH]

Status: [~] Core backend, schema, migration, deploy-env plumbing, and wallet credits UI are now implemented and passing repo checks. **Repo automated webhook→ledger E2E is closed** (`docs/STRIPE_AUTOMATED_E2E_EVIDENCE.md`, `pytest tests/api/test_payments.py -q`). Remaining operator follow-up before marking 4.1 fully done (not a work-stop blocker; ACP-first loop is live): live Stripe Dashboard checkout + saved-card operator verification (`docs/stripe-verification-2026-07-02.md` Run B).

ACP checkout is stable. New users must acquire ACP on exchange -- huge friction.

Production Stripe secrets are in GitHub (`STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`, `STRIPE_WEBHOOK_SECRET`) as of 12 September 2026 (live mode). Deploy syncs them into the host `.env`. Public truth: `GET /v1/payments/stripe/status` → `configured`. Webhook: `https://ancap.cloud/api/v1/webhooks/stripe` (`payment_intent.succeeded|payment_failed|canceled`). Item 4.1 stays `[~]` until a live Dashboard checkout + saved-card Run B is recorded.

Implemented surfaces:
- `POST /v1/payments/stripe/intent` -- create Stripe-backed top-up PaymentIntent and return client session data
- `GET /v1/payments/stripe/intents/{intent_id}` -- poll owned Stripe top-up intent status / credited state, including Stripe-provider sync fallback when webhook delivery is delayed
- `POST /v1/webhooks/stripe` -- Stripe webhook handler with signature verification + idempotent event deduplication
- `GET /v1/payments/methods` -- list saved payment methods
- `DELETE /v1/payments/methods/{id}` -- remove payment method
- frontend wallet credits page now supports saved cards, new-card Stripe.js entry, submit flow, webhook-status polling, and an explicit settlement-evidence panel that separates `Settlement signal` (`webhook` vs `poll fallback`) from `Verification status` so operators can see whether a captured top-up is already backed by real webhook delivery or still needs live webhook closure evidence; that same panel now also surfaces `Payment method evidence` (`saved card` vs `new card`, plus requested saved-method id / save-for-reuse flag when present) so manual verification can prove which checkout path was exercised without relying only on operator memory
- Stripe intent persistence now also records payment-method selection evidence (`payment_method_selection`, `save_payment_method_requested`, `requested_payment_method_id`) so saved-card vs fresh-card verification can be audited from the fetched ANCAP intent/provider payload instead of depending only on UI memory during manual runbook execution

Model changes now in repo:
- `User.stripe_customer_id` (nullable)
- `PaymentIntent.stripe_payment_intent_id` (nullable)
- new `StripeEvent` model/table for webhook deduplication
- migration `56f5c6a2d1ab_add_stripe_payment_support.py`

Deployment/config follow-through now in repo:
- `.env.example` documents Stripe env vars
- `docker-compose.prod.yml` passes Stripe runtime env through to API
- prod/rebuild scripts and settings validation now guard bundled-postgres URL/user/db consistency so deploys fail fast instead of drifting
- README documents Stripe adapter surfaces and fail-closed behavior when Stripe is unconfigured

Verification (2026-05-27):
- `pytest tests/api/test_payments.py -q` ✅ (now includes unsupported-currency fail-closed coverage for the first-slice Stripe allowlist)
- `pytest tests/test_prod_deploy_scripts.py -q` ✅ (`61 passed`)
- `pytest tests/test_config_admin_ids.py -q` ✅ (`10 passed`)
- `npm run test` in `frontend-app` ✅
- `npm run build` in `frontend-app` ✅
- `docker compose -f docker-compose.prod.yml exec -T api alembic upgrade head` ✅
- local prod stack healthy: `docker compose -f docker-compose.prod.yml ps` shows api/postgres/redis/frontend/proxy up; `http://127.0.0.1:8080/api/v1/system/health` returns `{"status":"ok"}`
- Stripe service layer now rejects unsupported checkout currencies with an explicit `400` (`USD`, `EUR` only for the current adapter slice) so the wallet UI and backend cannot silently drift into fake fiat coverage the repo has not actually implemented or verified
- wallet Stripe settlement helpers/tests now also keep manual verification honest by surfacing real webhook event timestamps and a separate verification-state line (`webhook delivery confirmed` vs `live webhook verification still open`) instead of making poll-captured credits look equivalent to true webhook closure
- `tests/api/test_payments.py` now also locks saved-card vs fresh-card intent metadata plus fetched webhook/poll provenance (`stripe_last_event_id`, `stripe_last_event_type`, `stripe_last_event_at`, `stripe_last_polled_at`) so repo-side evidence survives refactors even though final roadmap closure still needs live Stripe/manual proof, and frontend settlement helpers/tests now preserve that same saved-card/new-card evidence in the wallet UI instead of leaving it implicit during manual runbook execution

Existing `payment_intents` contract is preserved: Stripe is an adapter, not a replacement.

Remaining follow-through:
- run a real Stripe checkout with valid configured keys and confirm webhook delivery credits the wallet end-to-end
- verify saved-card reuse on a live/test Stripe customer, not only mocked repo tests
- follow `docs/STRIPE_VERIFICATION_RUNBOOK.md` and fill `docs/STRIPE_VERIFICATION_EVIDENCE_TEMPLATE.md` so the remaining manual closure evidence is captured consistently and webhook-delivered capture is not confused with poll-only fallback; `scripts/generate_stripe_verification_packet.py` now turns that template into a dated run packet (`docs/stripe-verification-YYYY-MM-DD.md`) with prefilled round metadata plus generator/repo provenance, and refreshes the stable alias `docs/stripe-verification-latest.md` by default so the newest verification packet has a fixed handoff path without replacing the dated evidence-of-record
- only then mark this item done

### 4.2 Creator earnings withdrawal [HIGH]

Status: [x] Done. Creator payout requests, admin review, ledger hold/refund handling, migration history, and repo tests are implemented. Remaining future work is payout automation/completion depth, not the baseline withdrawal flow itself.

Implemented surfaces:
- `POST /v1/payouts/request` -- creator requests ACP withdrawal
- `GET /v1/payouts` -- creator lists own payout requests and filters by status
- `GET /v1/admin/payouts` -- platform admin lists all payout requests
- `POST /v1/admin/payouts/{id}/approve` -- platform admin approves a pending request and records the approval event
- `POST /v1/admin/payouts/{id}/reject` -- platform admin rejects a pending request and refunds the held balance

Model in repo:
- `PayoutRequest` with status `pending|approved|rejected|completed|failed`
- methods: `acp_wallet|bsc_address|bank_transfer`
- amount/destination/admin notes + request/approval/rejection ledger event links
- migration `57b0c4a8d9ef_add_payout_requests.py`

Verification (2026-05-27):
- `app/db/models.py` contains `PayoutRequest` plus `PayoutRequestStatusEnum`
- `app/api/routers/payouts.py` implements creator request/list and admin approve/reject/list routes behind auth / platform-admin enforcement
- create-request flow fails closed on non-ACP currency, non-positive amount, insufficient balance, and duplicate in-progress payout requests
- create-request flow places the requested amount on ledger hold immediately; rejection restores the held ACP; approval leaves the hold in place while recording admin approval metadata for downstream/manual settlement
- `tests/api/test_payouts.py -q` ✅ (`8 passed`) covering hold behavior, insufficient balance, duplicate prevention, admin auth, approve/reject, filters, and terminal-state reprocessing guards

Exit criteria: satisfied -- creator can request payout, and admin can approve/reject it. Full automatic on-chain payout completion can be layered later without reopening this baseline item.

### 4.3 Creator earnings dashboard [MEDIUM]

Status: [x] Done. Creator earnings/conversion endpoints, seller dashboard UI, timeline chart, and CSV export are implemented and passing validation. Remaining future work is deeper funnel instrumentation for views/add-to-cart/checkout-started, not the baseline creator earnings surface.

Implemented surfaces:
- `GET /v1/creators/me/earnings` -- total/window revenue, pending payout, paid out, workflow breakdown, per-day earnings timeline
- `GET /v1/creators/me/conversions` -- listing/period conversion counts with explicit funnel coverage metadata
- `/dashboard/seller/earnings` -- seller-facing revenue cards, workflow breakdown, conversion coverage panel, daily line chart, CSV export
- seller dashboard quick-link now points creators directly to the new earnings page

Verification (2026-05-27):
- `app/api/routers/creators.py` aggregates creator-owned listing revenue from paid ACP orders and payout backlog/completions
- `app/schemas/creators.py` defines the public response contracts for earnings timelines and conversion summaries
- `tests/api/test_creators.py -q` ✅ (`3 passed`) covering earnings aggregation, conversion coverage defaults, and auth enforcement
- `pytest tests/api/test_creators.py tests/api/test_payouts.py -q` ✅ (`11 passed`) confirming the earnings dashboard slice stays consistent with payout-hold/refund behavior
- `npm run build` in `frontend-app` ✅, including the new `/dashboard/seller/earnings` route in the production build output

Exit criteria: satisfied -- creators can inspect revenue by workflow/day, see pending vs paid payout state, export CSV, and understand current funnel coverage limits.

### 4.4 Subscriptions for workflows [MEDIUM]

Status: [x] Done. Workflow subscription pricing, buyer subscribe flow, renewal scheduler, retry/pause notifications, and marketplace/listing UI support are implemented and validated. Remaining future work belongs to broader monetization depth, not this baseline subscription item.

Implemented surfaces:
- `POST /v1/subscriptions` -- start a subscription for an active listing with monthly/quarterly/annual ACP billing
- `GET /v1/subscriptions` -- list the caller's subscriptions with status filtering and cursor pagination
- scheduler integration via `POST /v1/system/jobs/tick` / `subscriptions_tick(...)` for due renewals
- creator listing publish flow now supports subscription price tiers on strategy/listing surfaces
- marketplace + listing detail UI now supports choosing billing period and starting subscriptions

Model in repo:
- `Subscription` (id, user_id, listing_id, plan_id, status: active|paused|cancelled|past_due, billing_period: monthly|quarterly|annual, price_acp, next_billing_at, auto_renew, retry_count, last_order_id)
- migration `9f1c7a4b2d10_add_subscriptions.py`

Scheduler behavior (implemented):
- On `next_billing_at`: check ledger -> debit buyer -> credit seller -> create renewal order -> extend access grant -> mark renewed
- If insufficient balance: retry up to 3 times with 3-day intervals, then pause + notify
- If listing becomes unavailable: pause + notify

Verification (2026-05-28):
- `app/api/routers/subscriptions.py` implements create/list subscription routes with ACP-only pricing validation and insufficient-balance / duplicate guards
- `app/jobs/subscriptions_tick.py` renews due subscriptions, records renewal orders/transfers, emits low-balance + paused + renewed notifications, and pauses inactive-listing subscriptions
- `frontend-app/src/app/strategies/[id]/page.tsx`, `frontend-app/src/app/listings/[id]/page.tsx`, `frontend-app/src/app/listings/page.tsx`, and `frontend-app/src/app/marketplace/page.tsx` expose subscription pricing and purchase flows in the UI
- `pytest tests/api/test_subscriptions.py -q` ✅ (`4 passed`)
- `docker compose exec -T api alembic upgrade head` ✅
- clean `npm run build` in `frontend-app` ✅ after clearing stale `.next` cache artifacts from a previous build attempt

Exit criteria: satisfied -- creators can offer subscription plans, users can subscribe, and billing auto-renews with retry/pause handling.

### 4.5 API monetization depth [MEDIUM]

Status: [x] Done. Usage export, per-agent spend caps, per-endpoint / per-org-key spend caps, cost-plus margin snapshots, and admin revenue reporting now exist in repo and are test-covered.

Implemented / verified (2026-05-28):
- `GET /v1/paid-api/me/usage/export` -- monthly usage export CSV for callers
- `POST /v1/paid-api/agents/{agent_id}/spend-cap` -- per-agent monthly spend caps stored on agent metadata
- `PATCH /v1/organizations/{org_id}/api-keys/{key_id}` -- per-endpoint / per-currency monthly spend caps stored on org or org-attached agent API keys
- paid API usage events now persist `provider_cost`, `estimated_margin`, `api_key_id`, and org attribution metadata for captured charges
- `GET /v1/paid-api/revenue-summary` -- platform-admin-only gross / provider-cost / margin summary grouped by endpoint, period, and organization
- org attribution now survives agent-owned API keys after agent -> organization transfer by falling back to `Agent.metadata_.org_id` when the key itself is not org-owned
- verification:
  - `pytest tests/api/test_paid_api.py tests/api/test_organizations.py -q` ✅
  - `pytest tests/api/test_paid_api.py tests/api/test_organizations.py tests/test_release_workflow.py tests/test_open_source_examples.py tests/test_public_trust_docs.py -q` ✅

### 4.6 Referral commission auto-payout [MEDIUM]

Status: [x] Done. Referral reward issuance, optional on-chain payout job enqueueing, jobs-tick execution, and runtime/deploy env wiring are implemented and now covered by repo tests.

Implemented behavior:
- first paid ACP workflow capture issues both `referral_signup_bonus` and `referral_commission_share` reward events idempotently
- reward issuance credits the beneficiary ledger immediately while preserving ledger invariants
- when `REFERRAL_ONCHAIN_PAYOUT_ENABLED=true` and the ACP wallet runtime is configured, ACP beneficiary wallets also receive queued `referral_onchain_payout_jobs`
- `POST /v1/system/jobs/tick` processes pending referral payout jobs through the ACP wallet helper and records `sent` / retryable `pending` / terminal `failed` outcomes
- admin economy-health diagnostics expose `pending_referral_payout_jobs` and `failed_referral_payout_jobs`
- production compose/env/docs now pass through `REFERRAL_ONCHAIN_PAYOUT_ENABLED`, `REFERRAL_ONCHAIN_PAYOUT_KEYSTORE_FILE`, and `REFERRAL_ONCHAIN_PAYOUT_FEE_ACP`

Verification:
- `pytest tests/api/test_ai_console_wave1.py -q` ✅
- `pytest tests/api/test_ai_console_wave1.py tests/test_prod_deploy_scripts.py tests/api/test_workflow_store.py tests/api/test_system_economy_health.py -q` ✅

Remaining future work: richer payout operations/monitoring may still be layered later, but the baseline referral commission auto-payout path itself is no longer missing.

### 4.7 Marketplace search + filters [MEDIUM]

Status: [x] Done. Marketplace discovery now exposes server-side search/filter/sort, returns listing popularity/rating metadata, and records listing-open view activity for discovery ranking.

Implemented / verified (2026-05-28):
- `GET /v1/listings/marketplace/listings` now supports `search`, `category`, `price_min`, `price_max`, `sort` (`popular|recent|price_asc|price_desc|rating`), `limit`, and `offset`
- PostgreSQL FTS is connected to marketplace discovery via `to_tsvector(...)` / `plainto_tsquery(...)` over strategy + vertical fields, with `ILIKE` fallback matching on names/descriptions/notes/ids
- marketplace responses now include computed `price`, `listing_purchases`, `listing_views`, `rating`, `rating_count`, `is_featured`, `is_trending`, and `available_categories`
- `GET /v1/listings/{id}` now records a lightweight public `listing_opened` activity event so discovery view counts are backed by real runtime events instead of docs-only intent
- frontend marketplace page now consumes the server-side marketplace API directly and exposes live search, category filter, min/max price, popular/newest/price/rating sort, plus featured/trending merchandising badges
- verification:
  - `pytest tests/test_listings_orders.py -q` ✅
  - `pytest tests/test_listings_orders.py tests/api/test_ai_console_wave1.py -q` ✅
  - `npm run build` in `frontend-app` ✅
  - `docker compose -f docker-compose.prod.yml config --quiet` ✅

Remaining future work: richer dedicated view-tracking instrumentation and deeper recommendation logic can still be layered later, but the roadmap baseline marketplace search/filter/discovery slice itself is no longer missing.

### 4.8 Chargebacks and dispute UI [MEDIUM]

Status: [x] Done baseline. Refund requests now have a persistent backend model, user initiation path, user-visible status, and admin approve/reject review surface wired into the workflow payment ledger trail.

Implemented / verified (2026-05-28):
- `RefundRequest` persistence model + migration with pending/approved/rejected states, user/admin indexes, notes, timestamps, and refund-ledger linkage
- `POST /v1/payments/refund-request` lets users open a refund request against a captured workflow payment intent
- `GET /v1/payments/my-refund-requests` exposes user-visible refund status/history, optionally filtered by payment intent
- `GET /v1/payments/refund-requests` remains platform-admin-only for review queue listing
- `POST /v1/admin/refund-requests/{id}/approve` credits the user ledger back, marks the payment intent refunded, updates proof trail metadata, and emits refund webhook events best-effort
- `POST /v1/admin/refund-requests/{id}/reject` closes the request with admin notes without crediting balance
- workflow run detail UI now exposes refund/dispute submission for completed captured runs and shows current request status inline
- admin overview now shows pending refund requests with approve/reject actions next to existing top-up approvals
- verification:
  - `pytest tests/api/test_refund_requests.py -q` ✅
  - `npm run test -- --run src/lib/__tests__/api.test.ts` in `frontend-app` ✅
  - `npm run build` in `frontend-app` ✅
  - `docker compose -f docker-compose.prod.yml config --quiet` ✅

Remaining future work: deeper dispute evidence capture, external fiat-provider chargeback sync, and richer customer-facing refund history UX can still be layered later, but the roadmap baseline refund / dispute / chargeback slice itself is no longer missing.

---

## Priority 5 -- Mobile wallet completion

### 5.1 Unblocked items (no native FFI dependency)

| ID | Task | Status |
|----|------|--------|
| P4-8 | PIN + biometrics | [~] wired, real device verification pending |
| P4-9 | SecureVault | [~] SecureStore wired, biometric migration done, verification pending |
| P4-15 | i18n EN/RU/UK/DE | [x] react-i18next wired in the Expo app with persisted language selection and translated core wallet flows/screens |
| P5-XO | Exchange office foundation (ACP hub, all↔all quotes, tickets, Exchange tab) | [x] see `docs/mobile/EXCHANGE_OFFICE_FOUNDATION.md` — catalog/quote/tickets + **auth-settle/sync/admin-complete**; USDT→ACP opens linked swap desk order; Expo open-ticket+settle wired |
| P5-XO2 | OTC commodities + Markets AI workflows | [x] oil/gas/uranium/timber/sand/stone/ores desk rail; Markets category workflows + Markets Intel Pack on `/ai/workflows` |
| P5-XO3 | Banknote/coin authenticity + numismatic ACP value (iPhone) | [x] see `docs/mobile/NUMISMATIC_AUTHENTICITY.md` — `/mobile/numismatic/*` + Expo Auth tab; educational prototype only |
| P5-XO4 | Real estate / antiques / space OTC + ACP ownership certificates | [x] see `docs/mobile/TITLE_OWNERSHIP_RAILS.md` — RE sale/rental, antiques, space objects; `/ownership-proofs/*` crypto register contracts |
| P5-XO5 | Patent inventions + recipes OTC/IP rail + ownership classes | [x] `ip` rail (`patent`/`recipe`), exchange chips `ip_*`, ownership `patent_invention`/`recipe_formula`; see `docs/mobile/TITLE_OWNERSHIP_RAILS.md` |
| P5-XO6 | ACP Insurance desk (universal parametric cover) | [x] `/insurance/*` + UI `/insurance` — `docs/ECONOMY_INSURANCE_ARENA.md` (record-only settlement; claim expiry + rate limits) |
| P5-XO7 | ACP Arena prediction + house games | [x] `/arena/*` + UI `/arena` — commit-reveal house games (`/house/commit` → `/house/reveal`) |
| P5-XO8 | Exponential network growth levers | [x] `/growth/exponential` + compound quote — `(1+r)^depth × passport boost` |
| P5-XO9 | ANCAP AI Agency (AI-sector ads) | [x] Home `#agency` promo block + `/agency` vertical (campaign packs, Telegram/X/email rails, ACP settle) |
| P5-XO10 | Digital DNA/RNA bank | [x] `/dna-bank` + API `/v1/dna-rna-bank/*`, migration `073`, AES-256-GCM + HKDF-SHA384 (v1); no full genomes |
| P5-XO13 | Perimeter desk (cleanup + security watch) | [x] `/perimeter` + `/v1/perimeter-cleanup/*`, migration `074`, Abrams Suite-B AES-256-GCM + HKDF-SHA384; small-site operator SKU; **security-watch** site intake 8,500 ACP (cameras/sensors/SOC partner brief, not a detection-rate claim); blast-radius failed-decrypt proof vs DNA/passport keys; not an Aave/Maker/RWA yield wrap; insurance `perimeter_cleanup` |
| P5-XO11 | Legal entertainment worldwide desk | [x] `/entertainment` — licensed venues/festivals/lotteries/resorts by region + Arena on-platform; no grey books |
| P5-XO12 | ZEISS Lightfield 4D research citation | [x] `/legal/research-refs` + AETERNA imaging refs; tech note link; no affiliation / no PDF host |
| P5-XO14 | Daewoong eTurna mRNA LNP USPTO citation | [x] `/legal/research-refs` §7 + `/aeterna` consult `aeterna-mrna-reprogramming-brief`; notice of allowance literacy as of 11 Sep 2026; no affiliation / no lipid recipes |
| P5-XO15 | Chalmers Floquet bosonic-code stack | [x] `/tech` `stack-floquet-bosonic` + lot `tech-floquet-bosonic`; `/quantum-sim` compute_stack; `/legal/research-refs` §8; docs/CHALMERS_FLOQUET_BOSONIC_CODES.md |
| P5-XO16 | Startup investment desk | [x] `/startups` + `GET /v1/startups/catalog`; AI/retail-B2B/SECaaS/agrotech literacy as of 12 Sep 2026; `/legal/research-refs` §9; `docs/STARTUP_INVEST_DESK.md` — not a securities offering |
| P5-XO17 | Welcome 100 ACP grant | [x] 100 ACP promotional access credit on register (`welcome_grant_acp`); news widget + `/legal/welcome-grant`; not a donation / not USD cash — `docs/WELCOME_GRANT.md` |
| P5-XO9 | AuctionEscrow + TECH auction | [x] Foundry `contracts/auction-escrow` + `/tech-auction/*` + UI `/tech` — `docs/TECH_AUCTION_ESCROW.md` |
| P5-1 | MASVS L1 checklist | [~] repo-baseline closed in `docs/mobile/SECURITY_MODEL.md` (hashed PIN verifier, device-only secure storage, biometric-gated vault migration, error redaction, screenshot/clipboard/auto-lock controls); remaining closure is real-device/native release verification |
| P5-5 | No secrets in Sentry/logs | [x] mobile wallet error surfaces now route thrown messages through a shared secret-redacting helper; mnemonic/keystore/rawTx/bearer-token shaped values are scrubbed before UI/log propagation |
| P5.5 | Biohax NFC + org identity + digital passport | [~] backend + `066_digital_passport` + `072_passport_education_docs` (ChaCha20-Poly1305 edu vault), soulbound BSC contract (`contracts/digital-passport/`), API `/v1/passports/*` + education-docs, web `/passport`, mobile Passport tab + NFC backend sync; admin web UI + DESFire still open — see `docs/DIGITAL_PASSPORT.md`, `docs/mobile/BIOHAX_NFC.md` |
| P6-3 | Device matrix (iOS + Android) | [~] Android local test env **ready** (`Pixel_10_Pro` via `ancap-mobile/scripts/start-android-test-env.ps1`, `docs/mobile/ANDROID_TEST_ENV.md`); physical + iOS matrix rows still open |
| P6-4 | TestFlight + Play Internal | [~] local device/test-env blocker **cleared**; Play/TestFlight uploads remain operator credentials/listing follow-up (`docs/mobile/RELEASE_CHECKLIST.md`) |
| P6-5 | Store listing + legal pages | [~] legal routes exist and release pack is outlined in `docs/mobile/RELEASE_CHECKLIST.md`; final operator/assets review still pending |
| P6-6 | Production v1.0.0 | [~] Android emulator runtime path unblocked; production cut still needs store evidence + physical/MASVS sign-off (`docs/mobile/RELEASE_RUNBOOK.md`) |

### 5.2 Native-build-dependent items

| ID | Task | Status / blocker |
|----|------|------------------|
| P1-6 | Android FFI `.so` build | [x] `ancap-mobile/scripts/build-android-native.ps1` now succeeds on the current Windows host with Android SDK/NDK installed, emitting `arm64-v8a`, `armeabi-v7a`, and `x86_64` `libacp_mobile_ffi.so` artifacts into `ancap-mobile/modules/expo-acp-core/android/src/main/jniLibs` |
| P4-3 | Create wallet via FFI | [~] Android native artifacts + host assemble OK; **local emulator online** (`Pixel_10_Pro`) — run Expo against it; iOS still depends on P1-7 |
| P4-11 | Send + preview + sign | [~] Android native artifacts + host assemble OK; **local emulator online** for runtime verification; iOS still depends on P1-7 |
| P1-7 | iOS Swift UniFFI link | [~] Run `ancap-mobile/scripts/build-ios-native.ps1` on macOS/Xcode and verify packaged artifacts |

### 5.3 Smart QR Pay / AI Payment Scanner / Claim Codes track (v1.1 / v2, after wallet release closure)

Status: [~] First-scope Smart Pay groundwork is implemented beyond docs-only intent: backend `capabilities` + deterministic `parse` + `quote` + execute/status/recover endpoints exist in repo code with API tests, typed mobile client methods exist with client tests, the Expo beta flow already supports paste, QR import, camera scan, review, execute, refresh/recover, and session restore, and placeholder execution lifecycle semantics are now hardened enough to map recovered txs onto quoted route steps with explorer links and placeholder completion. **ANCAP Claim Codes** and web **Payment Scanner** parse/preview (`/claim`, `/payment-scanner`, `/pay`, merchant dashboard) shipped in the commerce release (`93b6625`); photo/OCR invoice decode and real non-custodial route execution remain **not shipped** and must not be marketed as live autopay.

Product formula inside this track:
- `Photo / QR -> AI Decode -> Payment Intent -> Smart Swap -> Pay`
- `Lock crypto -> Generate claim code -> Share code -> Redeem -> Receive crypto`

Execution order inside this track:
1. [x] docs/spec split: plan + schema + API + security
2. [x] backend `GET /v1/mobile/smart-pay/capabilities`
3. [x] backend `POST /v1/mobile/smart-pay/parse` (deterministic ACP + raw EVM + EIP-681 first scope)
4. [x] backend `POST /v1/mobile/smart-pay/quote` for first supported routes
5. [x] backend execution-session groundwork:
   - `POST /v1/mobile/smart-pay/execute`
   - `GET /v1/mobile/smart-pay/payments/{executionId}`
   - `POST /v1/mobile/smart-pay/payments/{executionId}/recover`
6. [x] mobile SDK/client wiring for Smart Pay endpoints (`@ancap/acp-api-client` typed methods plus client tests cover capabilities/parse/quote/execute/status/recover)
7. [~] Expo app scan/import/pay UX (beta screen now supports paste, gallery QR import, camera QR scan, explicit confirmation before execute, quote-expiry freshness hints plus expired-quote execute guards, refresh/recover, and persisted draft/session restore in-device; polished UX/history and real route execution still pending)
8. [~] real route engine / bridge-swap execution integration
   - placeholder execution lifecycle is now hardened in repo code: recover maps known txs onto bridge/swap/payment route steps, emits explorer links, and marks placeholder sessions completed once all quoted route txs are known
   - execute responses now include actionable `routePlan` signing steps for client-side non-custodial orchestration
   - on-chain bridge/swap/transfer broadcast orchestration still remains
9. [ ] AI fallback classifier for ambiguous payloads (only after deterministic/heuristic path is solid)
10. [~] receipt/history/recovery UX hardening
   - Expo beta now persists recent device-local Smart Pay session snapshots, keeps per-execution `sessionToken` resume access when locally available, supports tap-to-resume, merges authenticated backend payment-history listing with local history, fetches backend receipt snapshots, and now makes the authenticated-vs-device-token resume boundary explicit in both docs and UI while rendering a richer receipt summary from receipt/intent/quote/execution data; the history list now also surfaces route-progress and recovery-state hints so resumed sessions expose more than status text alone, now also labels whether each restored snapshot still supports refresh, refresh-only finalized inspection, or snapshot-only restore, now also labels snapshot freshness from the freshest saved execution/receipt evidence in both restored history cards and receipt snapshots so stale local/backend restores are easier to distinguish from recent proof updates, local-history clearing now preserves signed-in backend history instead of wiping the whole visible timeline, and the receipt view now maps quoted route steps to linked-vs-pending proof coverage while keeping unmatched additional tx refs visible instead of collapsing everything into one flat list; the history surface now also adds a compact overview card summarizing total/in-flight/needs-attention/completed sessions plus live-resume, refresh/recover, stale-snapshot, and proof-follow-up counts, while also summarizing per-history-entry action state and surfacing explicit next-step labels/hints so users can tell whether to sign, refresh, recover, or treat the snapshot as read-only context; the active receipt snapshot now renders from merged history context so route summaries, fees, merchant labels, and completion metadata stay aligned with richer overlap state instead of falling back to a thinner in-memory receipt copy
   - route-proof matching no longer reuses the same tx ref across multiple quoted steps with identical role/network pairs; each observed tx is now consumed at most once while extra unmatched refs stay in the additional-proof bucket, and stored-receipt fallback proof matching now also enforces summary-network alignment so a BSC tx ref cannot silently satisfy an ACP receipt step just because the role text looks compatible
   - restored history cards and receipt snapshots now both surface pending-proof summaries for quoted route steps that still lack linked tx refs, receipt snapshots now also keep quoted-route proof coverage explicit even when 0 route tx refs are linked yet, recover input now normalizes pasted raw tx hashes or explorer links before the request is sent, now rejects unparseable structured recovery-locator noise instead of forwarding fake tx ids while surfacing duplicate/invalid recovery tokens directly in the Expo UI, now blocks recover submission when the pasted field contains only invalid locator noise while still allowing an empty status-only recovery pass, now previews each parsed recovery ref in the Expo UI with preserved network/explorer-link context before submit, recovered/history proof tx refs are now deduplicated case-insensitively across backend receipts and local execution snapshots while preserving the richer explorer-linked copy, structured recovery refs now flow through the backend recover API so pasted explorer links can preserve network/explorer metadata in reconciled proof receipts instead of collapsing back to bare hashes, authenticated execution owners can now refresh status/receipt and submit recovery without the original device-local sessionToken while non-owners still stay blocked, explicit conflicting `routeStepIndex` refs now remain in the additional-proof bucket instead of silently remapping onto a different quoted step or inflating observed progress counts, and overlapping authenticated-backend/local-history snapshots now preserve richer locally observed proof refs plus receipt context/device session continuity instead of flattening to whichever final-state snapshot sorted last, while the active receipt snapshot now also renders from that merged history context so route summaries, fees, merchant labels, and completion metadata stay aligned with the richer overlap state instead of falling back to a thinner in-memory receipt copy, and both restored history cards plus the active receipt snapshot now summarize how many route-proof links are explicit route-step matches vs inferred role/network matches vs still pending so users can judge proof quality at a glance; the compact history overview now also aggregates linked-vs-additional proof provenance (receipt-backed vs execution-only) across the visible timeline so users can quickly see whether proof refs are already persisted into receipt snapshots or still only preserved in execution history, and now also aggregates the route-progress source mix (live telemetry vs proof-link fallback vs raw tx refs vs status-only snapshots) so users can quickly spot whether a session list is driven by fresh execution counters or mostly by recovery-only evidence; final route-execution-linked proof polish still remains. History cards plus the active execution/receipt views now also label whether route progress comes from live execution telemetry, proof-derived quote/receipt linkage fallback, raw tx refs, or status-only snapshots so stale execution counters are easier to spot during recovery and receipt review
11. [~] AI Payment Scanner MVP:
   - [x] website paste + preview + manual confirm (`/payment-scanner`, `POST /v1/payment-scanner/parse`)
   - [~] camera/photo upload in wallet and website
   - [x] OCR heuristics for receipts/invoices/payment screens (`app/services/payment_text_parse.py`, web `/payment-scanner` OCR mode, mobile `ocr` parse source)
   - [x] QR / URI recognition for ACP and common crypto payment patterns (deterministic parse path)
   - detect amount, recipient, network, asset, memo/tag/comment, payment deadline, and payment currency
   - build `paymentIntent` preview with manual correction before execute
   - service fee charged in ACP
12. [ ] Smart Payment Flow expansion:
   - automatic asset matching
   - smart swap before payment
   - multi-chain routing beyond narrow first-scope routes
   - suspicious-address / risk scoring
   - duplicate invoice/payment detection
   - saved recipients, templates, and merchant payment mode
13. [x] ANCAP Claim Codes / Crypto Voucher layer (commerce MVP shipped):
   - [x] lock internal balance or escrowed asset
   - [x] generate redeemable public claim code
   - [x] redeem from website (`/claim`)
   - [x] one-time and multi-use codes
   - [x] expiration and proof receipt
   - [~] cancel/refund before redemption; creation / redeem fees charged in ACP
14. [~] Secure escrow and code-verification layer:
   - `claim_code` as public user code
   - `secret_hash` only in storage (never store redeem codes in plain text)
   - `locked_balance`, `status`, expiry, and redemption metadata
   - brute-force protection, rate limits, anti-fraud monitoring, optional PIN/password
15. [ ] Merchant / growth layer:
   - businesses create payment QR codes
   - users create gift or payout claim codes
   - campaigns distribute ACP/wACP through claim codes
   - referral claim codes, airdrop claim links, and QR vouchers for Telegram / X / web

Truth constraints:
- deterministic parser first, AI second
- user confirmation mandatory before any payment
- AI/OCR may prepare a payment, but it must never auto-send without explicit user confirmation
- ACP fee reserve required
- first release scope stays narrow: ACP + BSC/EVM supported paths only
- claim-code storage must be hash-based and abuse-resistant, not plain-text voucher storage

---

## Priority 6 -- Architecture and release hygiene

### 6.1 Deployment story cleanup [MEDIUM]

Status: [x] Done. The abandoned Cloudflare Workers repo path was removed; Docker/containerized deploy is now the single repo-declared production path.

Problem: Two conflicting deployment paths:
1. Docker/Containerized: `frontend-app/Dockerfile` + `docker-compose.prod.yml` (confirmed working)
2. Cloudflare Workers: `wrangler.jsonc` + static framework (appeared abandoned)

PR #1 had added Cloudflare Workers config but actual production uses the containerized approach.

Implemented:
- removed stale `wrangler.jsonc` from the repo
- kept Docker/nginx deployment as the canonical production path
- aligned repo state with the already-working production topology instead of keeping a broken parallel build path

Verification (2026-05-27):
- repo no longer contains `wrangler.jsonc`
- production deploy path remains `docker-compose.prod.yml` + deploy scripts
- GitHub/Cloudflare no longer have a repo-declared abandoned Workers config to treat as a build source

### 6.2 Dependency management consolidation [MEDIUM]

Status: [x] Done. Runtime dependency inputs are now centralized in `requirements.in`, `requirements.txt` is the generated runtime lock, packaging metadata imports runtime deps from that same source, and CI/release workflows install a single `.[dev]` package definition instead of drifting between separate lists.

Problem: `requirements.txt` (exact pins) and `pyproject.toml` (range pins) coexist.

Implemented:
- added `requirements.in` as the runtime dependency input file for backend image / Python CI installs
- `requirements.txt` is now explicitly the generated runtime lock target for `python -m piptools compile --generate-hashes --output-file requirements.txt requirements.in` and is regenerated in-repo with hashes from that source
- `pyproject.toml` now uses setuptools dynamic metadata to import runtime dependencies from `requirements.in`
- `pyproject.toml` now defines a `dev` extra for Python test/security tooling (`pytest`, `pytest-asyncio`, `bandit`)
- backend CI and release workflows now install `pip install .[dev]` instead of maintaining a second manual test-tool list
- dependency-review workflow now also triggers on `requirements.in`
- contributor/release docs now describe the regenerate-lock flow explicitly
- `tests/test_dependency_management_consolidation.py` locks the new source-of-truth wiring into repo coverage

Verification (2026-05-28):
- `requirements.in` exists and contains the backend runtime dependency set
- `requirements.txt` documents the `piptools compile` regeneration path and no longer pretends to be a hand-maintained mixed runtime+dev list
- `pyproject.toml` imports runtime deps from `requirements.in` and exposes the `dev` extra
- `.github/workflows/backend-ci.yml` and `.github/workflows/release.yml` install `.[dev]`
- `pytest tests/test_dependency_management_consolidation.py tests/test_dependency_review_workflow.py tests/test_release_workflow.py tests/test_prod_deploy_scripts.py -q` ✅

### 6.3 Formal releases and tags [MEDIUM]

Status: [x] Done. A real tag-triggered GitHub release workflow is now in repo and test-covered.

Problem: No GitHub Releases / tags. \LOG.md\ is the changelog.

Implemented:
- `.github/workflows/release.yml` now runs on `push.tags: ["v*"]`
- backend release gate runs Alembic, `pytest -q`, Bandit, and `docker build -t ancap:release-check .`
- frontend release gate runs `npm test -- --run`, `npm run lint`, and `npm run build`
- final `draft-release` job waits on both gates and uses `softprops/action-gh-release@v1` with `draft: true` and `generate_release_notes: true`
- `tests/test_release_workflow.py` locks the release trigger, gate jobs, and draft-release behavior into CI coverage

Verification (2026-05-27):
- `pytest tests/test_release_workflow.py -q` ✅
- release workflow file present in repo at `.github/workflows/release.yml`

Policy: every merge to master touching \app/\ or \frontend-app/\ -> bump patch. Feature branches -> minor. Breaking changes -> major. Tag format: \vYYYY.MM.DD\ or \vMAJOR.MINOR.PATCH\.

### 6.4 Documentation health [LOW]

Status: [x] Done. The old frontend audit is now explicitly marked superseded, roadmap/audit support docs now carry `Last verified` headers, and `docs/STATUS_MATRIX.md` remains the compact status authority beneath `MASTER_ROADMAP.md`.

Tasks:
- Mark \docs/AUDIT-2026-04-29.md\ as superseded
- Add \> Last verified: YYYY-MM-DD\ header to all roadmap and audit docs
- Create \docs/STATUS_MATRIX.md\ -- single source of truth mapping every component to status

Verification (2026-05-28):
- `docs/AUDIT-2026-04-29.md` now declares itself superseded and records `Last verified: 2026-05-28`
- `PRODUCTION_ROADMAP.md`, `ROADMAP.md`, `ROADMAP-MONETIZATION.md`, and `docs/mobile/ROADMAP.md` now carry `Last verified: 2026-05-28`
- `docs/STATUS_MATRIX.md` remains aligned with the current roadmap truth, including the now-baseline-done dependency-consolidation slice

---

## Priority 7 -- Retention and LTV (later expansion)

Goes after monetization core is stable:
- Volume discounts: 5+ runs = 10% off, 20+ = 20% off
- Credits expiry policy: unused credits expire after 12 months (notify at 30/7/1 days)
- Win-back campaigns: discount codes for users inactive > 30 days
- Upsell banners: inline CTAs on receipt pages, billing page, developer dashboard
- React Flow strategy canvas (after builder API stable)

---

## Consolidated test status

| Suite | Status | Notes |
|-------|--------|-------|
| \pytest -q\ | 258 passed, 3 skipped | Full backend suite |
| \
pm test --workspaces\ (mobile SDK) | 56 passed across 5 packages | Including wallet-service tests |
| \
px tsc --noEmit\ (Expo wallet) | TypeScript clean | |
| \playwright install --with-deps\ | Browser binary ready | **E2E not run in CI yet** |
| \andit -r app/\ | Runs but soft-fails | Fix: remove \\|\| true\ |
| \docker build\ | \--target deps\ nonexistent stage | Fix: remove invalid target |

**Skipped tests to unskip:**
- \	est_allocate\ -- after Pool ownership migration (055)
- \	est_jobs_tick_sets_ledger_halt_blocks_faucet\ -- rework to use malformed transfer
- \pytest.skip("bcrypt backend not available")\ -- fix system dependency

---

## Execution order

Current active phase: Priority 0 (emergency) + Priority 1 (CI/security automation)

**Execution sequence:**

Week 1 (Priority 0 -- EMERGENCY)
  0.1  Revoke leaked key + delete/clean legacy plaintext-key snippet
  0.2  Fix insecure dev defaults in docker-compose.prod.yml + config

Week 2 (Priority 1a -- CI fixes)
  1.1  Fix backend CI: remove || true from Bandit + Docker check
  1.2  Enable Dependabot (add .github/dependabot.yml + enable in settings)
  1.3  Add CodeQL workflow

Week 3 (Priority 1b -- E2E + ops separation)
  1.4  Playwright E2E in CI (add docker-compose job)
  1.5  Restrict ops/diagnostics endpoints (auth + tier split)
  1.6  Separate jobs_tick from HTTP request path

Week 4 (Priority 2 -- Domain model)
  2.1  Pool ownership migration (055) + unskip test_allocate
  2.2  Fix economy_health sync/async bug
  2.3  Unskip ledger invariant test
  2.4  Fix bcrypt skip

Week 5 (Priority 3 -- Security)
  3.1  localStorage -> HttpOnly cookies (auth migration)
  3.2  SameSite + CORS hardening
  3.3  Production header alignment

Week 6 (Priority 4a -- Monetization: payments)
  4.1  Stripe integration (intent + webhook + credit ledger)
  4.2  Creator earnings withdrawal
  4.8  Chargeback + dispute UI

Week 7 (Priority 4b -- Monetization: growth)
  4.3  Creator earnings dashboard
  4.4  Subscriptions for workflows
  4.6  Referral commission auto-payout

Week 8 (Priority 4c -- Monetization: platform)
  4.5  API monetization depth (cost-plus, exports, spend caps)
  4.7  Marketplace search + filters

Week 9 (Priority 5 -- Mobile)
  5.1  PIN + biometrics (real device verification)
  5.1  SecureVault (real device verification)
  5.1  MASVS/device-release verification (real hardware)

Week 10 (Priority 6 -- Architecture hygiene)
  6.1  Deployment story cleanup (remove Cloudflare artifacts or migrate)
  6.2  Dependency management consolidation
  6.3  Formal release workflow
  6.4  Documentation health

Ongoing (Priority 7 -- Later)
  7   Retention / LTV mechanics
  Playwright smoke in CI (Phase 7 from old roadmap)
  React Flow strategy canvas

---

## Post-audit roadmap (2026-06-10)

Security and ops hardening completed in this audit:
- Rotated HestiaCP admin, root console, and `admin@ancap.cloud` mailbox passwords (stored in private `Sicret/`)
- Removed plaintext credentials from tracked docs; secret-hygiene scan passes
- `apt upgrade` applied on production host; Docker reclaimed ~7.8 GB
- HestiaCP `:8083` restricted to admin IP + localhost (UFW)
- Exim hostname aligned to `mail.ancap.cloud`; SPF/DKIM/DMARC verified in DNS
- Repository cleanup: tmp/log artifacts removed, `.gitignore` tightened, README project tree added

### Next priorities (Q3 2026)

| ID | Track | Deliverable | Why |
|----|-------|-------------|-----|
| R1 | **ACP transparency** | Public block explorer (`/explorer` or `explorer.ancap.cloud`) — height, txs, addresses | Trust + auditability for native chain |
| R1b | **Crypto Benchmark Library** | QOBLIB-style scorecard for ACP/wACP/sACP vs published baselines (`GET /v1/crypto/benchmark`, `/reserves`) | See `docs/CRYPTO_BENCHMARK_LIBRARY.md` |
| R2 | **Ops monitoring** | Uptime + ACP block-height + container health alerts (Telegram/email) | Catch chain/API regressions early |
| R3 | **Backups** | Automated nightly Postgres + ACP chain data export off-server | Disaster recovery |
| R4 | **Mail deliverability** | Provider PTR → `mail.ancap.cloud`; optional SES/SendGrid relay fallback | Fix external delivery reputation |
| R5 | **Mobile release** | EAS production build, store listings, MASVS sign-off | Close device-ready wallet tail |
| R6 | **Monetization depth** | Workflow subscriptions, partner API tiers, creator payout UX | Optional depth after live ACP-first loop (not a work-stop blocker) |
| R7 | **CI/CD deploy** | GitHub Actions → SSH deploy to tunnel host (replace manual scripts) | Faster, repeatable releases |
| R8 | **ACP Lean chain** | Fee-packed mining, 5s cadence, hybrid PQC signatures, experimental X-Wing draft-10 envelopes, throttled heartbeat | `docs/ACP_LEAN_CHAIN.md` + `docs/ACP_PQC_ENCRYPTION.md` — security/speed/energy |
| R9 | **Securities intake** | Accept securities, promissory notes (векселя), and shares (акции) into org treasury / collateral rails | Expand capital layer beyond ACP cash; see `docs/SECURITIES_INTAKE_ROADMAP.md` |
| R10 | **Apple Watch HR fleet** | 3 watches/employee (distinct bands), continuous heart-rate sync, charge/rotation schedule | Workplace safety + shift presence; see `docs/mobile/APPLE_WATCH_EMPLOYEE_FLEET.md` |
| R11 | **SpaceX encrypted sats** | Launch satellites with encrypted ANCAP edge servers via SpaceX rideshare/manifest | Sovereign sealed orbital compute; see docs/SPACEX_SATELLITE_ENCRYPTED_SERVERS_ROADMAP.md |
| R12 | **AETERNA longevity** | DNA vault + ACP-paid genomic/longevity workflows + licensed partner rails (Sequencing.com import) | Eternal-life division; see `docs/AETERNA_LONGEVITY_MARKETPLACE_ROADMAP.md` |
| R13 | **Lunar land trading** | Science-tagged lunar parcel registry + ACP interest desk (NASA–IBM LFM themes) | Speculative registry claims only; see `docs/LUNAR_LAND_TRADING_ROADMAP.md` |

**ACP chain note:** Lean v1.4 packs fee-prioritized mempool txs (up to 512 / 2 MB) on a 5s miner interval. The assembler never mints; validator rewards are signed spends from the 105M genesis reserve. Hard cap is exactly 210,000,000 ACP. Recovery from the 2026-10-02 double-spend inflation: `docs/ACP_SUPPLY_INCIDENT_2026-10-02.md`. See `docs/ACP_LEAN_CHAIN.md`.

---

## SpaceX Encrypted Satellite Servers Track (2027+) - NEW

Execution detail: **docs/SPACEX_SATELLITE_ENCRYPTED_SERVERS_ROADMAP.md**.

Launch **encrypted ANCAP edge servers** as satellite payloads using **SpaceX** (rideshare / Transporter-class or dedicated as required): sealed storage, authenticated uplink, ground HSM key ceremony, then ACP orbital-edge productization.

| Phase | Status | Deliverables |
|-------|--------|--------------|
| X0 Feasibility | [~] | Orbit/mass/power, export/legal memo, cubesat vs ESPA decision; in-repo `/orbital-edge` registry stub |
| X1 Payload crypto arch | [~] | Encrypted server block diagram, threat model, sealed boot; attestation tables + API (FF_ORBITAL_EDGE) |
| X2 Ground & keys | [ ] | Ground segment, dual-control HSM ceremony, ops runbooks |
| X3 SpaceX program | [ ] | ICD/manifest path, env test plan, insurance/license with counsel |
| X4 First flight | [ ] | FlatSat -> launch -> LEOP encrypted round-trip demo |
| X5 ACP orbital edge | [ ] | Feature-flagged product: attestation/sealed offload; fleet cadence |

**Depends on:** ACP ledger stability + org authorization model + compliance review before public claims.
**Does not block:** Phase 6 mobile, R9 securities, R10 Watch fleet.


## Apple Watch Employee Fleet Track (2026-Q4+) — NEW

Execution detail: **`docs/mobile/APPLE_WATCH_EMPLOYEE_FLEET.md`** · Mobile checklist: Phase **5.6** in `docs/mobile/ROADMAP.md`.

| Phase | Status | Deliverables |
|-------|--------|--------------|
| W0 Spec & consent | `[x]` | Domain, org policy, legal/consent templates |
| W1 Backend fleet API | `[~]` | 3-watch inventory, rotation state machine, HR ingest (alerts deferred) |
| W2 iPhone HealthKit sync | `[ ]` | Permissions, background sync, rotation coach in mobile app |
| W3 watchOS companion | `[ ]` | Native sampling, swap haptics, band-slot complication |
| W4 Safety dashboard | `[ ]` | Org web live/near-live HR + compliance |
| W5 Fleet hardening | `[ ]` | Lost/maintenance workflows, battery-tuned intervals |

**Policy default:** one active watch; swap on interval (4–6h) or low SOC; A/B/C bands always color-coded.  
**Depends on:** org roles + employee consent. **Does not block:** mobile MASVS / securities S0–S2.

---

## Securities Intake Track (2026-Q4+) — NEW

Execution detail: **`docs/SECURITIES_INTAKE_ROADMAP.md`**.

Accept **securities (tsennye bumagi)**, **promissory notes (vekselya)**, and **equity shares (aktsii)** as intake instruments for verified orgs: register → review → custody stub → haircut valuation → ACP collateral hold (escrow-only first).

| Phase | Status | Deliverables |
|-------|--------|--------------|
| S0 Spec & domain | `[x]` | Glossary, schemas, custody model memo, status machine |
| S1 Data + API MVP | `[~]` | Instruments / intake / custody tables; org-gated CRUD + admin review (valuations/events deferred) |
| S2 Treasury UX | `[ ]` | Org Treasury → Securities desk; note + equity forms; dual-control review |
| S3 Valuation & pledge | `[ ]` | Haircuts, pledge → ACP collateral credit (escrow hold), risk alerts |
| S4 Custodian adapters | `[ ]` | Partner custody interface; optional registrar/CSD; mobile read-only + step-up |
| S5 Ecosystem | `[ ]` | Settlement intents vs pledges; invite-only discounting; audit attestations |

**Depends on:** verified org identity, stable ACP ledger/checkout, compliance matrix update.  
**Does not block:** mobile MASVS device closure or commerce days 61–90 polish.

---

## AETERNA Longevity Marketplace Track (2026-Q4+) — NEW

Execution detail: **`docs/AETERNA_LONGEVITY_MARKETPLACE_ROADMAP.md`**.

Division **AETERNA**: DNA vault (incl. Sequencing.com-style import), ACP-paid analysis/consult workflows (pigmentation, telomere, disease-risk, longevity), **15-axis molecular aging profile** (blood-RNA / PCR-style hallmarks — configuration of aging, not one bio-age number; sex-aware), **partial mRNA-reprogramming consult** (eTurna/USPTO notice-of-allowance literacy as of 11 Sep 2026; 1,000,000 ACP), stem-cell organ bioprint at **250,000 ACP** per organ (wisdom-tooth DPSC fallback; licensed bioreactor partner), **veterinary organ rails** as of 12 Sep 2026 (feline tissue cryoconservator-restorer 75,000 ACP; canine VET REGEN POD 180,000 ACP — conceptual partner architecture, licensed veterinarian only, no resurrection / survival-rate claims; `/legal/vet-regen`), **Vinci light chamber** as of 12 Sep 2026 (photobiomodulation / LED session protocol 48,000 ACP — Leonardo sunlight-health literacy, licensed phototherapy partner only, no safe-tanning or CE/FDA device claim; `/legal/light-chamber`), **microwave body contouring** as of 12 Sep 2026 (contact-cooled 2.45 / 5.8 GHz ISM applicator 52,000 ACP — licensed aesthetic/dermatology partner only, not liposuction, no CE/FDA or guaranteed fat-loss claim; `/legal/body-contouring`), **BioFusion micromanipulation chamber** as of 12 Sep 2026 (88,000 ACP IVF/ICSI / plant / BSL-lab partner brief — not a fertility clinic, not a guaranteed embryo, not a gene-editing kit; `/legal/biofusion`), **wisdom-tooth DPSC biomaterial** as of 12 Sep 2026 (65,000 ACP licensed bioreactor construct — not a full organ; `/legal/dpsc`), **Vascular Care+** as of 12 Sep 2026 (54,000 ACP anhydrous N2+O2 + light-wave — licensed phlebology/aesthetic partner only, not a thrombosis treatment; `/legal/vascular-care-plus`), **Vascular Care** as of 12 Sep 2026 (58,000 ACP ultrasound/RF/thermal; `/legal/vascular-care`), **needle-free transdermal pistol** as of 12 Sep 2026 (46,000 ACP aerosol + carrier gas — licensed clinic partner only, not a prescription dispenser; `/legal/transdermal`), **M-receptor delivery subscription** as of 12 Sep 2026 (12,000 ACP / month — patch / iontophoresis / inhaler / vagus-adjacent neuromodulation; licensed clinic retainer only, not compounding, not a treatment claim; `/legal/m-receptor`), **artificial oxygen carrier** as of 12 Sep 2026 (92,000 ACP hemoglobin-vesicle / PFC-emulsion architecture literacy — licensed bioreactor / transfusion-medicine partner only, not a blood product, not compounding, not a CE/FDA oxygen therapeutic; `/, synthetic blood / Black Mamba architecture (98,000 ACP multi-layer HBOC/PFC + modified peptide literacy; licensed bioreactor partner only; /legal/synthetic-blood-mamba)legal/oxygen-carrier`). **No DIY CRISPR / gene synthesis / LNP recipes; no institute affiliation claims.**

| Phase | Status | Deliverables |
|-------|--------|--------------|
| A0 Spec & brand | `[x]` | Schemas, `/aeterna` landing + hero, Workflow Store category |
| A1 Vault + intent API | `[~]` | `aeterna_dna_vault` / orders / partners; `FF_AETERNA`; migration `059` |
| A2 Checkout UX | `[ ]` | Category filter, org desk, longevity bundle UX |
| A3 Sandbox viz | `[~]` | Helix + hash vault + homepage promo + organ-print SKU + mRNA-reprogramming consult citation + veterinary organ rails (cat cryo / VET REGEN POD) + Vinci light chamber + microwave body contouring + BioFusion micromanipulation + DPSC biomaterial + Vascular Care+/Care + transdermal pistol + M-receptor subscription + oxygen-carrier brief + synthetic-blood / Black Mamba architecture; variant browser still open |
| A4 Partner network | `[ ]` | Verified clinics, ACP escrow until consult delivered |
| A5 Economy | `[ ]` | Vertical `AETERNA` + creator-listed genomic workflows |

**Depends on:** consent/compliance matrix, Workflow Store checkout, org roles.  
**Does not block:** Phase 6 mobile MVP or R9–R11.

---

## Lunar Land Trading Track (2026-Q4+) — NEW

Execution detail: **`docs/LUNAR_LAND_TRADING_ROADMAP.md`**.

ACP-settled **lunar parcel registry + interest desk**. Science tags follow open lunar observation themes (ice / volcanism / crater) highlighted by the [NASA–IBM Lunar Foundation Model](https://lnkd.in/p/e-SbXYMZ). **Speculative ANCAP registry claims only** — not Outer Space Treaty sovereign title. Distinct from Galaxy `sat-luna` and R11 orbital compute.

| Phase | Status | Notes |
|-------|--------|-------|
| L0 Spec & brand | `[x]` | `/lunar`, schemas, roadmap hooks |
| L1 Catalog + interest API | `[x]` | `lunar_parcels` / interests; `FF_LUNAR_LAND`; migration `070` |
| L2 Checkout UX | `[ ]` | ACP escrow + ownership-proof handoff |
| L3 LFM enrichment adapter | `[ ]` | Off-host metadata tiles; no model weights on API; gated by `docs/EMBODIED_AI_SECURITY_CONTROLS.md` |
| L4 Secondary market | `[ ]` | Transfer settled claims |

**Embodied AI security baseline (2026-09-10):** `docs/EMBODIED_AI_SECURITY_CONTROLS.md` · `FF_EMBODIED_ADAPTER=false` · `GET /v1/embodied-ai/security` approved-model register (UnifoLM pending digest). Does not enable robot adapters.

**Does not block:** Phase 6 mobile MVP or R9–R12.

---

## Commerce & Agent Track (2026-Q3)

Execution detail: **`docs/ANCAP_COMMERCE_ROADMAP.md`** (90-day commerce + AI agent plan).

| Phase | Status | Deliverables |
|-------|--------|--------------|
| Days 1–14 | **Shipped in repo** | Landing 4 CTAs, `/pricing`, ANCAP Pay MVP (`/pay`, `/merchant`, `/invoices`), `/buy-acp`, `/status`, `/explorer` beta, analytics events |
| Days 15–30 | **Shipped in repo** | Merchant dashboard + CSV, claim codes MVP, Workflow Store 2.0 bundles, creator payout UI |
| Days 31–60 | **Shipped in repo** | MCP server (`mcp-server/`), paid API challenge/settle/consume, `/mcp` docs |
| Days 61–90 | **Partial** | Payment scanner API + parse UX; embedded wallet / Business treasury UI stubs; full reserves dashboard → ongoing |
| Ongoing | **Shipped in repo** | `/compliance`, `/cards` waitlist, `docs/COMPLIANCE_ONRAMP_MATRIX.md`, `docs/WEBID_KYC_AND_CARD_ISSUING_PATH.md`, MiCA-safe messaging |

---

## Working tree rule

Before ending every session:
1. \git status --short\ -> must return nothing
2. \pytest -q\ -> must pass or show only known/skipped
3. Roadmap updated for any status changes
4. CLAUDE.md updated for any new patterns learned



