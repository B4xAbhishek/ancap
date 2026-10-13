# Open Source & GitHub Transparency

ANCAP is moving toward a GitHub-first model where public-safe components are easier to audit, integrate, review, and contribute to.

## Positioning

**ANCAP will be open-source where transparency increases trust, integration and adoption — while security-critical infrastructure, private keys, bridge signer operations, wallet hot-key logic and production secrets remain protected.**

Do **not** interpret “partial public surfaces” as hiding material product/token risk facts. Public docs must stay honest about wACP addresses, reserve/bridge risks, and free-distribution caps; only secrets and operator abuse thresholds stay private.

## Goals

- increase trust in ACP / wACP
- make the project more publicly verifiable
- simplify developer integrations
- attract open-source contributors
- prepare better for audits, grants, listings, and partnerships

## Public-safe scope

### Documentation
- roadmap
- architecture docs
- tokenomics docs
- ACP / wACP explanation
- bridge concept docs
- wallet feature docs
- security model
- API overview
- QR Pay / Smart QR Pay specs

### Frontend
- public website
- wallet UI without secrets
- landing pages
- docs UI

### SDK / integrations
- TypeScript SDK
- API client
- examples
- payment QR parser
- wallet integration examples

### Contracts / protocol surfaces
- wACP contract source
- bridge-related public contracts
- verification scripts
- testnet deployment instructions
- conversion rules
- reserve/backing explanation
- receipt / payment intent models

## Private scope

Never publish:
- private keys
- seed phrases / mnemonics
- bridge signer internals
- admin wallets
- production `.env`
- real RPC/API credentials
- deploy tokens/secrets
- hot-wallet operational logic
- internal server credentials
- abuse-sensitive thresholds that materially help attackers

## Target repository structure

Public target repos:
- `ancap-docs`
- `ancap-web`
- `ancap-wallet`
- `ancap-sdk`
- `ancap-contracts`
- `ancap-examples`
- `ancap-core`

Private target repos:
- `ancap-infra`
- `ancap-bridge-operator`
- `ancap-admin`

## Licensing direction

Recommended default:
- Apache-2.0 for protocol/core/SDK/contracts
- MIT for frontend/examples when easier adoption matters
- CC BY 4.0 or Apache-2.0 for docs depending on repo split

Current repo default: Apache-2.0.

## GitHub baseline

These community files are **already in the repo root** (Phase 1 file slice done; do not report missing `README.md`):
- `README.md`
- `LICENSE`
- `CONTRIBUTING.md`
- `SECURITY.md`
- `CODE_OF_CONDUCT.md`

Also keep enabled:
- issue templates
- PR template
- CodeQL
- Dependabot
- secret scanning
- push protection
- branch protection

## Why this matters

GitHub should become public proof that ANCAP is a real technical project, not just a token or a landing page.

People should be able to inspect:
- active roadmap progress
- code changes
- releases
- protocol and contract documentation
- integration examples
- security posture
- audit readiness

## Current publishable surfaces already in repo

Examples:
- `docs/PUBLIC_INTEGRATION_EXAMPLES.md`
- `examples/payment-integration/python_credit_topup.py`
- `examples/wallet-connection/python_wallet_login.py`

Public contract sources:
- `contracts/bridge-bsc/src/WACP.sol`
- `contracts/bridge-bsc/src/BridgeGateway.sol`

Supporting contract docs:
- `contracts/bridge-bsc/README.md`
- `docs/bridge-spec-v1.md`
- `docs/bridge-pilot-mainnet.md`
- `docs/BRIDGE_RISK_DOCUMENTATION.md`
- `docs/OFFICIAL_CONTRACT_ADDRESSES.md`
- `docs/CONTRACT_VERIFICATION_GUIDE.md`
- `docs/TESTNET_DEPLOYMENT_GUIDE.md`
- `docs/AUDIT_CHECKLIST.md`
- `docs/CHANGELOG_PUBLIC.md`

## `ancap-docs` split prep

The future public docs repo now has an in-repo seed plan and repeatable export path:

- split plan: `docs/ANCAP_DOCS_SPLIT.md`
- repo bootstrap guide: `docs/ANCAP_DOCS_REPO_BOOTSTRAP.md`
- contributor-intake seed: `docs/ANCAP_DOCS_CONTRIBUTOR_INTAKE_SEED.md`
- label seed: `docs/ANCAP_DOCS_LABEL_SEED.md`
- Discussions seed: `docs/ANCAP_DOCS_DISCUSSIONS_SEED.md`
- milestone seed: `docs/ANCAP_DOCS_MILESTONE_SEED.md`
- project-board seed: `docs/ANCAP_DOCS_PROJECT_BOARD_SEED.md`
- initial-issues seed: `docs/ANCAP_DOCS_INITIAL_ISSUES_SEED.md`
- repo-settings seed: `docs/ANCAP_DOCS_REPO_SETTINGS_SEED.md`
- update-cadence seed: `docs/ANCAP_DOCS_UPDATE_CADENCE_SEED.md`
- CI seed: `docs/ANCAP_DOCS_CI_SEED.md`
- Dependabot seed: `docs/ANCAP_DOCS_DEPENDABOT_SEED.md`
- machine-readable bootstrap seeds: `.github/bootstrap/README.md`, `.github/bootstrap/ancap-docs-contributor-intake.json`, `.github/bootstrap/ancap-docs-labels.json`, `.github/bootstrap/ancap-docs-milestones.json`, `.github/bootstrap/ancap-docs-discussions.json`, `.github/bootstrap/ancap-docs-project-board.json`, `.github/bootstrap/ancap-docs-initial-issues.json`, `.github/bootstrap/ancap-docs-repo-settings.json`, `.github/bootstrap/ancap-docs-update-cadence.json`, `.github/bootstrap/ancap-docs-ci.json`, `.github/bootstrap/ancap-docs-ci-workflow.yml`, `.github/bootstrap/ancap-docs-dependabot.yml`
- export script: `scripts/export_ancap_docs.py`
- bootstrap helper: `scripts/bootstrap_ancap_docs_repo.py` for gh-driven public repo creation, repo settings, label, milestone, live repo verification, and branch-protection payload application from the checked-in seeds once launch ownership/access exists
- standalone-bundle hardening: exported Markdown now rewrites out-of-bundle links to the source monorepo on GitHub, fails export if broken relative links remain inside the bundle, uses a docs-focused root `README.md` generated from `docs/ANCAP_DOCS_REPO_README.md` instead of the monorepo operations landing page, carries the public-safe GitHub issue/PR templates needed for a contributor-ready docs repo seed, now also carries a dedicated contributor-intake seed plus matching machine-readable metadata so issue/PR lanes and security-report routing are explicit outside the raw template files, exports a baseline `.github/CODEOWNERS` file so first-push review routing is explicit, now also ships a copy-ready public `.github/workflows/docs-ci.yml`, the matching `.github/bootstrap/ancap-docs-ci-workflow.yml` template referenced by the CI seed, a docs-repo-specific exported `.github/dependabot.yml` plus the matching `.github/bootstrap/ancap-docs-dependabot.yml` template, the bootstrap checklist plus reusable contributor-intake/label/Discussions/milestone/project-board/initial-issues/repo-settings/update-cadence/CI/Dependabot seeds, copy-ready pinned-topic/update-post templates, machine-readable bootstrap metadata for the first public repo creation / push / settings / labels / Discussions / release-tracking / update-rhythm setup, plus the dedicated first-backlog bootstrap metadata carried by the initial-issues seed, and a source-monorepo helper that turns the repo-create/repo-settings/label/milestone seeds plus the later default-branch protection payload into reusable `gh` commands instead of launch-day retyping
- CI guard scope: the exported Docs CI workflow now also treats the docs-repo Dependabot template as a drift-guarded artifact, so `.github/bootstrap/ancap-docs-dependabot.yml` cannot silently diverge from the shipped public `.github/dependabot.yml` inside the docs bundle while the source monorepo keeps its broader multi-ecosystem Dependabot config
- CI guard: Backend CI now reruns the export/public-trust regression slice whenever the docs-split bundle inputs or guard tests change, and that guarded seed now includes an explicit Docs CI workflow plus default status-check context so the future `ancap-docs` branch protection does not depend on guessed check names

That prep has now been used to seed the live public repository at `https://github.com/ancapcloud/ancap-docs`: the initial docs bundle is pushed, Docs CI has already gone green on `main`, the checked-in bootstrap helper has applied repo settings / labels / milestones, and default-branch protection is live with the seeded `Docs CI / docs-bundle` required-check context. The helper's live verification path now also has an opt-in community pass (`--verify-live --verify-live-community`) that checks the seeded labels, milestones, Discussions categories, seeded discussion-topic presence, seeded discussion-topic body alignment, pinned-discussion presence, and seeded starter-issue routing against the checked-in bootstrap seeds instead of leaving those surfaces as hand-verified launch notes. In plain checklist terms, that means seeded labels, milestones, Discussions categories, seeded discussion-topic presence, pinned-discussion presence, and seeded starter-issue routing are all verified from checked-in truth, with discussion-topic body alignment called out explicitly as an additional drift check. That pass now also emits a more operator-usable follow-up payload: it records unexpected live Discussion categories (`General`, `Polls`), per-category description drift, the live URLs/category placement for each seeded bootstrap topic, per-topic body/seed alignment, the explicit project-board auth failure, and copy-ready issue-reroute commands when an existing seeded starter issue drifts away from the checked-in body summary or milestone/label routing instead of reducing all of that to a generic drift count. The JSON snapshot is now easier for cron/CI/reporting consumers to skim too, because alongside the full `checks` array it also includes a compact `driftSummary` (`driftChecks`, `unknownChecks`, and per-scope counters) plus a `manualFollowUpSummary` grouped by action kind whenever manual follow-ups exist, so automation can tell at a glance that current live drift is concentrated in Discussions/pinned topics and that the project-board path is blocked on a scope request instead of reparsing the full checklist every time. The same verification path now also supports `--format markdown`, so the current Discussions/project-board drift can be rendered as a copy-ready operator checklist instead of only text/JSON when someone needs to close those admin gaps by hand; it also supports `--output <path>` so that markdown/JSON/text handoff artifacts can be written directly as UTF-8 files instead of depending on shell redirection defaults on Windows. That Windows note is concrete, not hypothetical on this host: a direct PowerShell `>` redirect of the JSON verification output produced a UTF-16 file with a BOM that then failed UTF-8 JSON parsing, so the checked-in guidance should keep steering operators toward `--output <path>` or the wrapper script instead of shell redirection. For the current live repo follow-up, `python scripts/generate_ancap_docs_live_followup.py --repo <owner>/ancap-docs` now wraps the paired markdown + JSON handoff generation into one repeatable command, with the preferred saved artifact pair staying `tmp/ancap-docs-live-follow-up-YYYY-MM-DD.md` plus `tmp/ancap-docs-live-follow-up-YYYY-MM-DD.json` so the checklist and machine-readable snapshot stay aligned instead of getting lost in shell scrollback; by default that wrapper also refreshes the stable alias pair `tmp/ancap-docs-live-follow-up-latest.md` plus `tmp/ancap-docs-live-follow-up-latest.json`, which gives cron/reporting follow-through a fixed "latest verified handoff" path without needing to reconstruct the date suffix. Those saved markdown/JSON artifacts now also embed artifact metadata (`artifactMetadata` in JSON plus an `Artifact metadata` appendix in markdown) with the generator/bootstrap source paths, UTC generation time, generator repo HEAD provenance, dated artifact paths, and optional latest-alias paths so downstream cron/CI/reporting consumers can inspect the file itself instead of inferring context from filenames or shell scrollback. Use `--no-write-latest-alias` only when a caller intentionally wants dated artifacts without touching the stable aliases; if someone tries to reuse `latest` as a custom `--date-label` while latest-alias writes stay enabled, the wrapper now refuses that path collision up front and tells them to pick a different date label or disable alias writes explicitly. It now also rejects path-shaped `--basename` / `--date-label` values such as `nested/path` or `..`, so callers cannot silently escape `--output-dir` or blur artifact provenance through filename fragments; those guard rails keep artifact writes anchored under the intended `--output-dir`. That wrapper now also keeps successful refreshes concise by default: it prints the saved artifact paths without dumping the full markdown checklist / JSON payload back into the terminal unless `--verbose-child-output` is explicitly requested, while still echoing the child helper output automatically on failures for debugging. It also now supports `--fail-on-not-ok`, which returns exit code `2` when the generated JSON summary reports `ok=false`; that makes the same saved-artifact flow usable as a cron/CI drift alarm without extra JSON parsing glue. That generated checklist now also includes a dedicated `Discussion UI targets` section with the live Discussions landing URL plus the exact seeded category names/descriptions and the tracked cleanup issue, a `Project board seed targets` section with the checked-in board name/scope/fields/views/notes plus copy-ready `gh project create/edit/link` command skeletons, seeded field-create commands, manual board-seeding steps, the current GitHub auth login/token-source/scopes when detectable, the exact `gh auth refresh -h github.com -s read:project` command when project auth is the blocker, and `gh issue edit` commands whenever a seeded starter issue needs body-summary or milestone/label rerouting, so category, project-board, and backlog-routing cleanup no longer depend on opening the seed files separately. The Discussions automation map in that checklist is also more actionable now: whenever the live repo/discussion/category ids and checked-in seed bodies are already known, it emits copy-ready `gh api graphql --raw-field "query=..."` commands for the automatable `createDiscussion` / `updateDiscussion` portion instead of forcing maintainers to reconstruct GraphQL payloads by hand, while still flagging the pin/category-lifecycle parts that remain UI-only. In practice, that wrapper-plus-`--output` path is now the safest saved-artifact route on Windows/PowerShell because it preserves UTF-8 output without relying on redirect encoding defaults, and the new default-quiet wrapper behavior also makes routine daily artifact refreshes easier to skim. The seeded starter backlog now also reflects live repo truth instead of only seed intent: `#5` (`Align Discussions categories and pin seeded bootstrap topics`) remains `OPEN`, while `#6` (`Publish official contract-address and verification index`), `#7` (`Add public integration examples index and cross-links`), and `#8` (`Reconcile roadmap / status / changelog wording for the first monthly update`) are now `CLOSED` because those deliverables are already live and aligned with the current exported source bundle. Current honest live state: the three seeded bootstrap topics do exist live (`/discussions/2`, `/discussions/3`, `/discussions/4`), their bodies now match the checked-in seed copy, but they are still unpinned and still sit under GitHub's default `Announcements` copy instead of the ANCAP-specific category descriptions; the public repo is also still carrying GitHub's extra default `General`/`Polls` categories. The helper now documents the actual API boundary instead of hand-waving it: GitHub's public GraphQL surface does expose `createDiscussion` / `updateDiscussion` for future missing-topic, topic-body, or category-reassignment automation, but it still does not expose the full category-description/category-set/pinning admin flow needed to close the current seeded-surface drift end-to-end, so those remaining Discussions gaps still need GitHub UI work or a future owner-capable automation path driven from the checked-in seeds. It also makes the GitHub Projects blocker explicit instead of implied: under the current `ancapcloud` auth, live project-board verification is still blocked because the token lacks `read:project` scope, and the generated checklist now includes the exact auth-refresh command to request that scope. The workflow drift guard is now relaxed just enough to let GitHub Actions version-only bumps land without forcing the exported workflow template to change in the same PR, while still hard-failing any structural drift in workflow logic or action identity. The remaining live gaps are final org ownership decisions, live project-board seeding under the eventual owner once project-capable auth exists, and bringing live Discussions categories plus pinned bootstrap topics into line with the checked-in seed.
