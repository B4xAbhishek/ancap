# ANCAP Status Matrix

> Status: active summary | Updated: 2026-10-02
> Primary source of truth: `MASTER_ROADMAP.md`
> Purpose: remove confusion between roadmap/status documents and provide one compact view of what is done, what is partial, and what is next.

---

## 1. Reading order

When documents disagree, use this order:

1. **`MASTER_ROADMAP.md`** — only execution-priority source of truth
2. **`docs/STATUS_MATRIX.md`** — compact status summary and document-role index
3. **`PRODUCTION_ROADMAP.md`** — supporting product/deploy capability snapshot
4. **`docs/mobile/ROADMAP.md`** — detailed mobile task tracker
5. **`ROADMAP-MONETIZATION.md`** — monetization strategy context
6. **`ROADMAP.md`** — historical architecture context

Rule: older/supporting documents can explain context, but they must not override `MASTER_ROADMAP.md`.

---

## 2. Top-line truth

As of 2026-10-02, the project is **not fully release-complete end-to-end**, but the **commerce + agent track** is shipped on production (build `57099a0`: Stripe live adapter configured, welcome grant, vet-regen rails). **Humanitarian aid desk** (`/humanitarian`) is in-repo as ACP briefs + Red Cross / Red Crescent national-society listings — not a signed ICRC/IFRC contract. **Work-stop blockers: none.** ACP hard cap is **210,000,000**; pre-recovery v2 inflation and stale index headlines above that cap are documented in `docs/ACP_SUPPLY_INCIDENT_2026-10-02.md`.

The core platform is largely built. Active remaining work (not blockers):

1. **ACP mobile wallet completion to real device-ready release** (local Android test env available)
2. **Open-source follow-through** (GitHub org / `ancap-docs` admin UI). Root `README.md` exists — not a missing-README blocker.
3. **Monetization depth** as optional conversion/LTV after a **live** ACP-first loop — not a freeze. Stripe 4.1 is operator verification only.

Security / CI / prod-hardening baseline closed 2026-07-01; external upstream key revoke audit remains operator-open.

Theodore / progress bots: do **not** report missing `README.md`. Do **not** report “monetization after the first ACP cycle” as a blocker.

Parallel trust/adoption track:
- **GitHub-first open-source transparency** — public-safe code/docs/protocol surfaces should become easier to audit and integrate, while private keys, bridge signer operations, hot-wallet logic, deploy secrets, and sensitive infra stay closed.

---

## 3. Document authority matrix

| Document | Role | Authority level | What it should be used for | What it should NOT be used for |
|---|---|---:|---|---|
| `MASTER_ROADMAP.md` | Master execution roadmap | Highest | Priority order, blockers, truth on what remains | Historical storytelling without current status |
| `docs/STATUS_MATRIX.md` | Unified summary | High | Quick orientation, document roles, cross-area status summary | Fine-grained task backlog |
| `PRODUCTION_ROADMAP.md` | Product/deploy snapshot | Medium | Capability snapshot, smoke/deploy context | Final project completion verdict |
| `docs/mobile/ROADMAP.md` | Mobile tracker | Medium | Detailed mobile task status | Cross-project source of truth |
| `ROADMAP-MONETIZATION.md` | Strategy note | Low-Medium | Monetization direction and priorities | Claiming monetization is still greenfield |
| `ROADMAP.md` | Historical architecture roadmap | Low | Architecture history and capability waves | Current delivery truth or release-readiness verdict |

---

## 4. Program status matrix

| Area | Status | Confidence | Primary truth source | Summary |
|---|---|---:|---|---|
| Core paid AI workflow platform | **Largely built** | High | `MASTER_ROADMAP.md`, `PRODUCTION_ROADMAP.md` | Paid workflows, LLM execution, receipts/proof, realtime status, org/dev/admin surfaces are substantially present. |
| Production UI/admin surfaces | **Largely built** | High | `PRODUCTION_ROADMAP.md` | Billing, organizations, webhooks, analytics, proof center, strategy builder baseline are present. |
| Proof / receipts / realtime status | **Largely built** | High | `PRODUCTION_ROADMAP.md` | Receipts/proof and run status infrastructure exist. |
| ACP checkout / first revenue loop | **Baseline done** | Medium-High | `MASTER_ROADMAP.md`, `ROADMAP-MONETIZATION.md` | First ACP-first monetization loop exists. Not a work-stop blocker. |
| Commerce & agent track (Pay, claim codes, explorer, MCP) | **Shipped MVP** | High | `docs/ANCAP_COMMERCE_ROADMAP.md`, `MASTER_ROADMAP.md` | Payment links, invoices, merchant dashboard, claim codes, explorer/reserves/supply surfaces, payment scanner preview, plan-tier scaffolding, and ramp waitlist are in repo + prod; Stripe live E2E closure and OCR/autopay remain open. |
| Security / CI / prod-hardening | **Baseline closed / operator tail open** | High | `MASTER_ROADMAP.md`, `docs/SECURITY_CLOSURE_EVIDENCE_2026-07-01.md` | 2026-07-01 wave closed repo/server/deploy baseline and GitHub secrets; deploy/tick workflows now fail-closed; external upstream key revoke audit remains operator-open. |
| Mobile wallet | **In progress / major remaining area** | High | `MASTER_ROADMAP.md`, `docs/mobile/ROADMAP.md` | Wallet is far along but not release-ready; native build closure, device verification, and release work remain. |
| Monetization depth | **In progress (not a freeze)** | High | `MASTER_ROADMAP.md`, `ROADMAP-MONETIZATION.md` | Depth continues; Exchange ticket auth-settle + `/buy-acp` crypto-first path shipped 2026-09-11. Stripe 4.1 remains operator Run B. |
| Governance / trust / anti-sybil architecture | **Substantially delivered** | Medium | `ROADMAP.md` | Important capability waves were built, but this does not imply whole-project release completion. |
| Release hygiene / architecture cleanup | **Baseline done** | Medium | `MASTER_ROADMAP.md` | Deployment story cleanup, dependency consolidation, release workflow, and documentation-health cleanup are now baseline done; broader release closure still depends on the higher-priority top-line tails. |
| Test posture | **Good baseline, not fully closed** | Medium-High | `MASTER_ROADMAP.md`, `PRODUCTION_ROADMAP.md` | Broad test coverage exists and real GitHub CI/E2E verification is green; the main remaining validation gaps are mobile real-device/native runs plus external/manual checks like live Stripe end-to-end. |
| Humanitarian aid desk | **Shipped (honest listing)** | High | `MASTER_ROADMAP.md`, `/legal/humanitarian` | ACP briefs for food/water/nutrition/clothing/medical/livelihood with IFRC and national-society handoff listings. Not a 135-FZ charity, not an emblem licence, not a tax receipt. |

---

## 5. Remaining work by major theme

### A. Security / CI / prod-hardening

**Status:** active top priority

**Already true:**
- repo-side leaked-key cleanup is done in tracked files, `scripts/check_secret_hygiene.py` now provides a repeatable secret-pattern scan (default tracked-files mode, with git-index fallback for tracked-but-currently-missing paths so local deletions do not crash the scan or hide still-tracked leaks, a dedicated `--staged` git-index mode for pre-commit catches that would otherwise hide behind later unstaged cleanup, optional `--include-untracked` coverage for local non-ignored temp/export artifacts, a `--history-range <rev-range>` mode that scans the full committed tree for each commit in a requested history window after cleanup/rotation instead of only diff-touched files, a clone-safe `--recent-history <count>` variant for local recent-window sweeps that do not assume `HEAD~N` exists, a tighter `--pending-push` mode that scans the exact local commit history about to leave the workstation using the tracked branch upstream when that ref is still resolvable and otherwise `origin/HEAD..HEAD` with a recent-history fallback only when no push base can be resolved, plus `--format json --output <path>` for copy-safe evidence handoff, including OpenAI project/service-account prefixes, Anthropic prefixes, and GitHub fine-grained/user-to-server/refresh token prefixes rather than only the older classic token shapes), the dedicated `Secret Hygiene` GitHub workflow plus tagged-release preflight now emit `tmp/secret-hygiene-report.json` as a retained CI artifact, those retained JSON artifacts now also include repo-HEAD provenance (`head_ref`, `head_commit`, dirty/clean working-tree state) so operator handoff can tie a report back to the exact scanned checkout, the workflow now also writes `tmp/secret-hygiene-history-report.json` after a full-history checkout and uses event-appropriate history scopes (push and pull_request commit deltas when GitHub provides those SHAs and that rev-range still resolves in the checkout and otherwise clone-safe `--recent-history 20` fallbacks, scheduled clone-safe `--recent-history 20` sweeps, manual blank-input runs using that same clone-safe recent-history path instead of forcing `HEAD~20..HEAD`, and tagged releases using the same clone-safe `--recent-history 20` artifact path instead of a brittle `HEAD~20..HEAD` release-only assumption), now also reruns `pytest tests/test_secret_hygiene.py tests/test_release_security_workflows.py -q` inside the workflow before evidence packaging so the artifact/report contract and the workflow/release gate contract are regression-checked in the same automation path, now also renders and retains `tmp/secret-rotation-evidence.md` (`secret-rotation-evidence`) from those JSON artifacts so operator follow-through starts from the same redacted evidence bundle, with that markdown handoff now also carrying the same repo-HEAD provenance, and tagged releases now likewise check out full history, upload the tracked/history/markdown evidence artifacts before the final explicit gate step, still fail the release job afterward when the evidence bundle or regression test fails instead of hiding the evidence bundle behind an early exit, and now drive that tagged-release tracked/history/markdown artifact path through `scripts/generate_secret_hygiene_evidence.py --recent-history 20` so release automation shares the same one-shot evidence contract as local/operator handoff instead of duplicating three separate inline scan/render commands. `scripts/render_secret_rotation_evidence.py` can now turn those retained JSON artifacts into a copy-safe markdown incident worksheet for operator-side revoke/access-cleanup handoff, accepts either a history sweep or local pending-push JSON as the second artifact (`--history-report` or `--secondary-report`), `scripts/generate_secret_hygiene_evidence.py` now wraps the primary scan + secondary history/pending-push scan + markdown worksheet render into one repeatable local handoff command, defaults that secondary artifact to `tmp/secret-hygiene-history-report.json` and switches it to `tmp/secret-hygiene-pending-push-report.json` under `--pending-push`, can optionally widen that primary artifact with `--include-untracked`, can instead switch that primary artifact onto the staged git index with `--staged-primary` when release/pre-commit evidence should follow the index rather than the working tree, now also refuses reused primary/secondary/output file paths before writing any artifact, and the renderer still refuses mismatched primary-vs-history/pending-push artifact pairs, repo-root drift, cross-checkout `head_commit` mismatches, plus reused input/output file paths so the handoff bundle cannot be assembled from the wrong evidence inputs, failed findings now use redacted finding previews so scanner output does not become a second leak surface, and Windows launcher-only workstations can now run that same scanner / renderer / one-shot bundle path as `py -3 scripts/check_secret_hygiene.py ...`, `py -3 scripts/render_secret_rotation_evidence.py ...`, and `py -3 scripts/generate_secret_hygiene_evidence.py ...` instead of depending on a bare `python` shim. The tracked-file secret scan currently passes (`python scripts/check_secret_hygiene.py`), and the repo now also carries tracked `.githooks/pre-commit` and `.githooks/pre-push` hooks plus `scripts/install_git_hooks.py` bootstrap so the staged-index scan can run automatically before local commits and the exact pending-push sweep can rerun automatically before local pushes, those tracked hooks now resolve `python` first, then `python3`, then `py -3` so the same local guard works on Windows workstations that rely on the Python launcher, and the installer itself can now be bootstrapped or rechecked with either `python scripts/install_git_hooks.py` / `python scripts/install_git_hooks.py --check` or `py -3 scripts/install_git_hooks.py` / `py -3 scripts/install_git_hooks.py --check` depending on which interpreter entrypoint the workstation actually exposes. That installer now has regression coverage for refusing to overwrite an existing custom `core.hooksPath` without `--force`, refusing to enable `.githooks` when an expected tracked hook file is missing, reusing an already-correct `.githooks` config while restoring executable bits, and a non-mutating `--check` verification path for proving the tracked hooks are already active, and the optional staged/untracked/history scans now also act as useful local tripwires for indexed, recent-commit, or temp/export artifacts that copy remediation-note content
- production secret guardrails are hardened in repo/config, `docs/PRODUCTION_SECRET_BASELINE.md` captures the operator provisioning/evidence checklist, the production-secret baseline sub-slice is now closed on the current host/runtime, and the current prod-like host runtime now passes them with real provisioned secrets outside the repo: `docker compose -f docker-compose.prod.yml config --quiet` succeeds, the required secret set is present without placeholder-like values, bundled-postgres parity holds, and `/api/v1/system/health` plus `/api/v1/system/ready` both return `200`
- backend CI soft-fail fixes are in place
- GitHub secret scanning, push protection, Dependabot security updates, and dependency review are enabled
- real GitHub runs are green for CodeQL, Backend CI, Frontend CI, and the scheduled `System Jobs Tick` workflow on `master`
- public diagnostics/ops endpoints are restricted, and the scheduled jobs path is already split onto `/v1/system/jobs/tick/async`
- auth cookie/storage/CORS hardening is live
- public Cloudflare-routed `ancap.cloud` / `api.ancap.cloud` header checks now match the canonical `DENY` + `nosniff` + `strict-origin-when-cross-origin` + explicit `Permissions-Policy` + HSTS set
- 2026-07-01 hardening wave shipped: see `docs/SECURITY_CLOSURE_EVIDENCE_2026-07-01.md`
- GitHub deploy/tick secrets configured (5 secrets); auto-deploy green on `master`
- `/.github/workflows/deploy-ancap-cloud.yml` and `system-jobs-tick.yml` now **fail closed** when required secrets are missing (no skip-success)
- `docs-ci.yml` triggers on both `main` and `master`

**Still remaining:**
- revoke/rotate the exposed provider key externally and complete any upstream access cleanup (operator checklist now lives in `docs/SECRET_ROTATION_RUNBOOK.md` and `docs/SECURITY_CLOSURE_EVIDENCE_2026-07-01.md`)

**Truth source:** `MASTER_ROADMAP.md`

### B. Mobile wallet

**Status:** active major remaining area

**Already true:**
- Rust FFI core exists
- TypeScript SDK packages exist
- mobile backend endpoints exist
- Expo app shell and most wallet UX are implemented
- PIN/biometrics and SecureVault are wired in app code
- i18n is done
- release evidence rc1 packet filled for repo-verified slice: `docs/mobile/release-evidence-v1.0.0-rc1.md`
- public legal page routes already exist for `/legal/terms`, `/legal/privacy`, and `/legal/cookies`
- Smart Pay first-scope backend groundwork exists for capabilities, deterministic parse, quote, and execute/status/recover
- Smart Pay placeholder execution lifecycle now maps recovered txs onto quoted route steps, emits explorer links, reports route-progress metadata, and can close placeholder sessions once all quoted txs are known
- Smart Pay typed client wiring and Expo beta flow already exist for parse → quote → execute → refresh/recover, now including quote-expiry freshness hints plus expired-quote review/execute guards in the Expo beta surface
- Smart Pay Expo beta now also keeps recent device-local session/receipt snapshots for resume/history/recovery baseline UX, preserves locally available per-execution `sessionToken` access for resume/recover flows, can merge authenticated backend payment-history listing with local history, can fetch backend receipt snapshots for the active payment, now makes the authenticated-vs-device-token resume boundary explicit in UI/docs, surfaces route-progress/recovery-state hints directly inside the session history list, now also labels whether each restored snapshot still supports refresh, refresh-only finalized inspection, or snapshot-only restore, maps quoted route steps to linked-vs-pending proof coverage in the receipt view while keeping unmatched additional tx refs visible separately, avoids reusing one observed tx ref across multiple quoted steps with the same role/network pair, now surfaces pending-proof summaries for quoted route steps that still lack linked tx refs in both restored history cards and receipt snapshots, now keeps quoted-route proof coverage explicit even for receipt snapshots that still have 0 linked tx refs, now labels snapshot freshness from the freshest saved execution/receipt evidence in both restored history cards and receipt snapshots so stale local/backend restores are easier to distinguish from recent proof updates, now normalizes pasted recovery input from raw tx hashes or explorer links before recover requests, now rejects unparseable structured recovery-locator noise instead of forwarding fake tx ids while surfacing duplicate/invalid recovery tokens directly in the Expo UI, now blocks recover submission when the pasted field contains only invalid locator noise while still allowing an empty status-only recovery pass, now previews each parsed recovery ref in the Expo UI with preserved network/explorer-link context before submit, now deduplicates recovered/history proof tx refs case-insensitively across backend receipts and local execution snapshots while preserving the richer explorer-linked copy, now forwards structured recovery refs (including network/explorer metadata from pasted explorer links) through the backend recover API so restored proof coverage keeps richer explorer-linked route context instead of degrading to bare tx hashes, now allows the authenticated execution owner to refresh status/receipt and submit recovery without the original device-local session token while still blocking non-owners, now keeps explicit conflicting `routeStepIndex` refs in the additional-proof bucket instead of silently remapping them onto a different quoted step or inflating observed progress counts, and now preserves richer local proof refs plus receipt context/session continuity when authenticated backend history later overlaps the same execution instead of flattening to the later final-state snapshot only, while the active receipt snapshot now also renders from that merged history context so route summaries, fees, merchant labels, and completion metadata stay aligned with the richer overlap state instead of falling back to a thinner in-memory receipt copy, both restored history cards plus the active receipt snapshot now summarize proof-linkage quality as explicit route-step matches vs inferred role/network matches vs pending steps, the compact history overview now aggregates linked-vs-additional proof provenance (receipt-backed vs execution-only) across the visible timeline, and the history cards plus active execution/receipt views now also label whether route progress comes from live execution telemetry, proof-derived quote/receipt linkage fallback, raw tx refs, or status-only snapshots
- Android native `.so` emission via `ancap-mobile/scripts/build-android-native.ps1` is now verified on the current Windows host, with `libacp_mobile_ffi.so` emitted for `arm64-v8a`, `armeabi-v7a`, and `x86_64` under `modules/expo-acp-core/android/src/main/jniLibs`

**Still remaining:**
- Android Expo dev-build/runtime verification using the emitted `.so` artifacts
- iOS native packaging on macOS/Xcode
- native create/send/sign verification in dev builds
- real device verification for PIN / biometrics / SecureVault
- remaining MASVS/device-release verification (repo baseline is closed; real-device/native validation still remains)
- release-closure scaffolding now exists in `docs/mobile/DEVICE_MATRIX.md`, `docs/mobile/RELEASE_CHECKLIST.md`, and `docs/mobile/RELEASE_RUNBOOK.md`, and the remaining external evidence now has copy-ready templates in `docs/mobile/DEVICE_VERIFICATION_EVIDENCE_TEMPLATE.md` and `docs/mobile/RELEASE_EVIDENCE_PACKET_TEMPLATE.md`
- public legal page routes already exist for `/legal/terms`, `/legal/privacy`, and `/legal/cookies`
- actual device runs, TestFlight/Play Internal uploads, final listing assets/operator/legal completion, and the final v1.0.0 cut (the final runbook is now scaffolded, but the external execution work still remains)

**Truth source:** `MASTER_ROADMAP.md`, `docs/mobile/ROADMAP.md`

### C. Monetization depth

**Status:** depth in progress — **not a work-stop blocker** (ACP-first loop live)

**Already true:**
- first ACP-first workflow monetization loop exists in baseline form
- creator/developer monetization surfaces exist in baseline form
- creator earnings dashboard, API monetization depth, referrals, marketplace discovery, refunds — baseline done in `MASTER_ROADMAP.md` 4.2–4.8
- Exchange ticket auth-settle + `/buy-acp` crypto-first path (2026-09-11)
- repo automated Stripe webhook→ledger E2E verified: `docs/STRIPE_AUTOMATED_E2E_EVIDENCE.md` (`pytest tests/api/test_payments.py -q` → 33 passed on 2026-07-02)
- dated verification packet: `docs/stripe-verification-2026-07-02.md`

**Still remaining (operator / optional depth):**
- Stripe live dashboard / saved-card operator verification (Run B). Live secrets are in GitHub and `GET /v1/payments/stripe/status` reports `configured: true` as of 12 Sep 2026.
- further conversion polish / LTV levers (Priority 7 deferred)

**Truth source:** `MASTER_ROADMAP.md`, `ROADMAP-MONETIZATION.md`

---

## 6. Current highest-priority queue

This is the practical reading of the current queue from `MASTER_ROADMAP.md`:

1. **Priority 0:** external upstream key revoke audit (operator checklist in `docs/SECURITY_CLOSURE_EVIDENCE_2026-07-01.md`)
2. **Priority 1:** CI/CD honesty — **baseline closed** (fail-closed deploy/tick; docs-ci on `master`)
3. **Priority 2:** domain model gaps and skipped tests
4. **Priority 3:** auth/cookie/CORS/security-header hardening follow-through (now baseline closed in repo/runtime/public headers)
5. **Priority 4:** monetization depth (optional; ACP-first loop live — not a work-stop blocker)
6. **Priority 5:** mobile wallet completion
7. **Priority 6:** architecture/release hygiene

Note: security/CI/prod-hardening baseline is closed. Mobile is the main remaining product tail. Monetization after the first ACP cycle is **not** a work-stop blocker.

---

## 7. Fast truth by component

| Component | Status | Notes |
|---|---|---|
| Paid workflow execution | Done baseline | Core capability exists |
| ACP-first payments | Done baseline / needs depth | Works as base loop; needs lower-friction expansion |
| Proof center / receipts | Done baseline | Present and important trust layer |
| Organizations / teams | Done baseline | Delivered stabilization slice |
| Webhooks | Done baseline | Delivered stabilization slice |
| Strategy Builder | Done baseline | Lightweight builder exists; React Flow is later |
| Search / analytics | Done baseline | Exists, but marketplace depth remains |
| Mobile native signing flow | Partial | Native closure and verification remain |
| Mobile release readiness | Not done | Device/stores/security/release still open |
| CI hardening | Baseline done | Secret scanning/push protection, dependency review, CodeQL, Backend/Frontend CI, and scheduled async `System Jobs Tick` verification are confirmed on GitHub; the remaining adjacent security tail is external key rotation/access cleanup, not CI gate honesty. |
| Secret remediation | Partial | Cleanup is done in tracked repo files, `scripts/check_secret_hygiene.py` now provides a repeatable secret-pattern scan with default tracked-files coverage plus git-index fallback for tracked-but-currently-missing paths, dedicated `--staged` git-index coverage for pre-commit catches, optional `--include-untracked` checking for local non-ignored temp/export artifacts, `--history-range <rev-range>` coverage that scans the full committed tree for each commit in the requested recent-history window after cleanup/rotation instead of only diff-touched files, clone-safe `--recent-history <count>` coverage for local recent-window sweeps that do not assume `HEAD~N` exists, tighter `--pending-push` coverage for the exact local commit history about to leave the workstation using the tracked branch upstream when that ref is still resolvable and otherwise `origin/HEAD..HEAD` with a recent-history fallback only when no push base can be resolved, plus `--format json --output <path>` for copy-safe evidence handoff, including OpenAI project/service-account prefixes, Anthropic prefixes, and GitHub fine-grained/user-to-server/refresh token prefixes; the dedicated `Secret Hygiene` workflow plus tagged-release preflight enforce the tracked-files gate and now retain `tmp/secret-hygiene-report.json` as an evidence artifact, the same workflow now also writes `tmp/secret-hygiene-history-report.json` for push/PR commit-delta sweeps when GitHub supplies those SHAs and that rev-range still resolves in the checkout and otherwise clone-safe `--recent-history 20` fallbacks, scheduled clone-safe `--recent-history 20` sweeps, manual blank-input runs using that same clone-safe recent-history path instead of forcing `HEAD~20..HEAD`, and tagged-release clone-safe recent-history sweeps after full-history checkout, now also reruns `pytest tests/test_secret_hygiene.py tests/test_release_security_workflows.py -q` inside the workflow before evidence packaging so the scanner/report contract and workflow/release gate contract are checked in the same automation path, now also renders and retains `tmp/secret-rotation-evidence.md` (`secret-rotation-evidence`) from those JSON artifacts for operator handoff, tagged releases now also retain that recent-history artifact instead of checking only the working tree, `scripts/render_secret_rotation_evidence.py` can convert those JSON artifacts into a copy-safe markdown incident worksheet for operator handoff without relying on pasted shell logs, `scripts/generate_secret_hygiene_evidence.py` can now generate the tracked artifact + secondary history/pending-push artifact + markdown worksheet in one repeatable local step, can optionally widen that primary artifact with `--include-untracked` when local temp/export leak coverage matters too, and now refuses reused primary/secondary/output file paths before writing any artifact; both tools accept either a history sweep or local pending-push JSON as the second artifact (`--history-report` or `--secondary-report`), while still refusing mismatched tracked-vs-history/pending-push artifact pairs plus reused input/output file paths, failed findings now emit redacted finding previews so logs/artifacts do not become a second leak surface, and launcher-only Windows hosts can now run the same scanner / renderer / one-shot bundle commands as `py -3 scripts/check_secret_hygiene.py ...`, `py -3 scripts/render_secret_rotation_evidence.py ...`, and `py -3 scripts/generate_secret_hygiene_evidence.py ...` instead of depending on a bare `python` shim. Public security headers are now aligned end-to-end, the tracked-file secret scan currently passes (`python scripts/check_secret_hygiene.py`), and the repo now also carries tracked `.githooks/pre-commit` and `.githooks/pre-push` hooks plus `scripts/install_git_hooks.py` bootstrap so the staged-index scan can run automatically before local commits and the exact pending-push sweep can rerun automatically before local pushes, and that installer bootstrap/verification now stays honest for launcher-only Windows hosts too because the documented entrypoints cover both `python scripts/install_git_hooks.py` / `python scripts/install_git_hooks.py --check` and `py -3 scripts/install_git_hooks.py` / `py -3 scripts/install_git_hooks.py --check`. That installer now has regression coverage for refusing to overwrite an existing custom `core.hooksPath` without `--force`, refusing to enable `.githooks` when an expected tracked hook file is missing, and reusing an already-correct `.githooks` config while restoring executable bits, and the optional staged/untracked/history scans double as local tripwires for indexed, recent-commit, or temp/export artifacts that would otherwise copy roadmap remediation-note patterns; `docs/SECRET_ROTATION_RUNBOOK.md` captures the operator rotation checklist, but upstream revoke/rotation and access cleanup still remain external/manual. |
| Monetization expansion | Partial | First loop exists; depth features remain; Stripe repo-side saved-card/webhook evidence is now stronger in both persisted payloads and the wallet UI, the remaining manual run can now be captured in a dated copy of `docs/STRIPE_VERIFICATION_EVIDENCE_TEMPLATE.md` (or bootstrapped directly via `python scripts/generate_stripe_verification_packet.py`, which also refreshes `docs/stripe-verification-latest.md` by default unless `--no-write-latest-alias` is used), but final closure still needs a real/test webhook-confirmed top-up plus saved-card reuse run per `docs/STRIPE_VERIFICATION_RUNBOOK.md`. |
| Release workflow / tagging / dep hygiene | Baseline done | Tag-driven release workflow is in repo, `v1.0.0` is present, and Python dependency management now has a single runtime input (`requirements.in`) plus generated lock / shared `.[dev]` CI install path; broader release closure still depends on the remaining top-line roadmap tails. |
| Public `ancap-docs` split | In progress / live repo seeded | The public docs repo now exists at `ancapcloud/ancap-docs`, the exported bundle has been pushed as the first public-safe seed commit, `Docs CI` already passed on `main`, repo settings / labels / milestones are applied live from the checked-in seeds, and default-branch protection is now live with required PRs, 1 approval, stale-review dismissal, CODEOWNERS review, conversation resolution, and required status check `Docs CI / docs-bundle`. The source monorepo still holds the repeatable export/bootstrap path via `docs/ANCAP_DOCS_SPLIT.md`, `docs/ANCAP_DOCS_REPO_BOOTSTRAP.md`, `docs/ANCAP_DOCS_CONTRIBUTOR_INTAKE_SEED.md`, `docs/ANCAP_DOCS_LABEL_SEED.md`, `docs/ANCAP_DOCS_DISCUSSIONS_SEED.md`, `docs/ANCAP_DOCS_MILESTONE_SEED.md`, `docs/ANCAP_DOCS_PROJECT_BOARD_SEED.md`, `docs/ANCAP_DOCS_INITIAL_ISSUES_SEED.md`, `docs/ANCAP_DOCS_REPO_SETTINGS_SEED.md`, `docs/ANCAP_DOCS_UPDATE_CADENCE_SEED.md`, `docs/ANCAP_DOCS_CI_SEED.md`, `docs/ANCAP_DOCS_DEPENDABOT_SEED.md`, `.github/CODEOWNERS`, `.github/bootstrap/README.md`, `.github/bootstrap/ancap-docs-contributor-intake.json`, `.github/bootstrap/ancap-docs-labels.json`, `.github/bootstrap/ancap-docs-milestones.json`, `.github/bootstrap/ancap-docs-discussions.json`, `.github/bootstrap/ancap-docs-project-board.json`, `.github/bootstrap/ancap-docs-initial-issues.json`, `.github/bootstrap/ancap-docs-repo-settings.json`, `.github/bootstrap/ancap-docs-update-cadence.json`, `.github/bootstrap/ancap-docs-ci.json`, `.github/bootstrap/ancap-docs-ci-workflow.yml`, `.github/bootstrap/ancap-docs-dependabot.yml`, `.github/workflows/docs-ci.yml`, `scripts/export_ancap_docs.py`, and `scripts/bootstrap_ancap_docs_repo.py`; that export still ships a docs-focused root README, public-safe GitHub issue/PR templates plus a baseline CODEOWNERS review-routing seed, a dedicated contributor-intake seed with matching machine-readable metadata, reusable repo bootstrap/settings/labels/Discussions/milestones/project-board/repo-settings/update-cadence/CI/Dependabot seeds plus a dedicated initial-issues seed, copy-ready pinned-topic/update-post templates, a bootstrap-seed README, machine-readable bootstrap metadata for bulk/scripting-friendly setup, a copy-ready Docs CI workflow with the default `Docs CI / docs-bundle` required-check context, a docs-repo-specific Dependabot config/template, and a gh-driven helper for public repo creation, repo settings/labels/milestones, live repo verification, and the default-branch protection payload so launch setup does not depend on retyping seed values by hand. The live follow-up wrapper has now been exercised against the seeded repo truth too: `python scripts/generate_ancap_docs_live_followup.py --repo ancapcloud/ancap-docs --date-label 2026-06-01 --fail-on-not-ok` produced the paired artifacts `tmp/ancap-docs-live-follow-up-2026-06-01.md` + `tmp/ancap-docs-live-follow-up-2026-06-01.json` and reported `ok=false` with `driftCount=8` / `unknownCount=0`, which confirms the remaining live gaps are real rather than undocumented guesswork. That same wrapper now doubles as a cron/CI drift-alarm surface because `--fail-on-not-ok` returns exit code `2` when the generated JSON summary reports `ok=false`, so callers can gate on unresolved live drift without adding separate JSON parsing glue. By default it also refreshes the stable alias pair `tmp/ancap-docs-live-follow-up-latest.md` + `tmp/ancap-docs-live-follow-up-latest.json`, which gives follow-up automation/reporting a fixed latest verified handoff path without reconstructing a date suffix; `--no-write-latest-alias` is available when a caller intentionally wants only the dated artifacts, and the wrapper now also refuses `--date-label latest` while alias writes stay enabled so the dated outputs cannot silently collapse onto those stable alias paths. It now also treats `--basename` and `--date-label` as filename components only instead of path fragments, rejecting values like `nested/path` or `..` up front so callers cannot silently escape the chosen `--output-dir`. Those saved markdown/JSON artifacts now also embed artifact metadata (`artifactMetadata` in JSON plus an `Artifact metadata` appendix in markdown) with the generator/bootstrap source paths, UTC generation time, generator repo HEAD provenance, dated artifact paths, and optional latest-alias paths so downstream cron/CI/reporting consumers can inspect the file itself instead of inferring context from filenames or shell scrollback. Those eight drifts are fully narrowed now: GitHub's extra default `General` / `Polls` categories still exist, the seeded `Announcements` / `Ideas` / `Q&A` / `Show and tell` category descriptions still carry GitHub defaults instead of the checked-in ANCAP wording, and the three seeded bootstrap discussions (`/discussions/2`, `/discussions/3`, `/discussions/4`) are still unpinned even though their bodies already match the checked-in seed copy. That live verification path still has the opt-in community pass (`--verify-live --verify-live-community`) for seeded labels, milestones, Discussions categories, seeded discussion-topic presence, seeded discussion-topic body alignment, pinned-discussion presence, and seeded starter-issue routing, and it now returns explicit follow-up detail instead of only a drift count: unexpected live category names (`General`, `Polls`), per-category description drift, the live URLs/category placement for each seeded bootstrap topic, the explicit project-board auth failure, and copy-ready reroute commands whenever an existing seeded starter issue drifts away from its checked-in body summary or milestone/label routing. It also has a markdown checklist mode (`--verify-live --verify-live-community --format markdown`) plus `--output <path>` so those markdown/JSON/text handoffs can be written directly as UTF-8 artifacts instead of relying on shell redirection defaults on Windows; that warning is backed by a real host-side probe, because a direct PowerShell `>` redirect produced a UTF-16 JSON file with a BOM that then failed UTF-8 parsing. `scripts/generate_ancap_docs_live_followup.py` wraps the paired current-run handoff generation into one repeatable command, with the preferred default artifact pair staying `tmp/ancap-docs-live-follow-up-YYYY-MM-DD.md` plus `tmp/ancap-docs-live-follow-up-YYYY-MM-DD.json` so the operator checklist and machine-readable snapshot stay aligned instead of living only in shell scrollback, and that wrapper keeps successful refreshes concise by default by printing the saved artifact paths without dumping the full checklist/payload back into the terminal unless `--verbose-child-output` is explicitly requested. That worksheet includes a dedicated `Discussion UI targets` section with the live Discussions landing URL, the exact seeded category names/descriptions, and the tracked cleanup issue `#5`, plus a `Project board seed targets` section with the checked-in board name/scope/fields/views/notes, copy-ready `gh project create/edit/link` command skeletons, seeded field-create commands, manual board-seeding steps, the current GitHub auth login/token-source/scopes when detectable, the exact `gh auth refresh -h github.com -s read:project` command when project auth is blocked, and `gh issue edit` commands for starter-issue body-summary or milestone/label rerouting when drift is detected. When the live repo/discussion/category ids and checked-in seed bodies are already known, that same Discussions automation map also carries copy-ready `gh api graphql --raw-field "query=..."` commands for the automatable `createDiscussion` / `updateDiscussion` portion, leaving only the pin/category-lifecycle remainder as explicit UI-only follow-up instead of forcing someone to rebuild GraphQL payloads from scratch. The helper dry-run output also emits copy-ready `gh issue create` commands for the seeded starter backlog, including milestone/label routing plus suggested board-field mapping from the checked-in initial-issues seed, so the first public queue can be opened from repo truth instead of retyped from memory. The seeded issue backlog has now also been exercised against live repo state: only `#5` remains `OPEN`, while `#6`, `#7`, and `#8` are already `CLOSED` because their checked-in deliverables are live in the public docs repo. The helper now documents the real API boundary: GitHub's public GraphQL surface does expose `createDiscussion` / `updateDiscussion` for future missing-topic, topic-body, or category-reassignment automation, but it still does not expose the full category-description/category-set/pinning admin flow needed to close the current seeded-surface drift end-to-end, so the remaining Discussions cleanup still needs GitHub UI work or a future owner-capable automation path driven from the checked-in seeds. The remaining honest live gaps are final org ownership/migration decisions, bringing live Discussions categories and pinned bootstrap topics into line with the checked-in seed, and live project-board seeding under the eventual owner once project-capable auth exists; Backend CI still reruns the export/public-trust regression slice when those bundle inputs change, and the exported Docs CI guard now enforces structural alignment for the workflow template plus byte-for-byte alignment for the docs-repo Dependabot template so version-only GitHub Actions bumps no longer break the public repo unnecessarily. |

---

## 8. Anti-confusion rules

Use these rules when updating docs:

1. If a file claims the whole project is “release-ready”, verify it against `MASTER_ROADMAP.md` first.
2. If a capability exists but still lacks hardening, device validation, or release closure, prefer **baseline done** or **partial** over absolute **done**.
3. Mobile feature code being written does **not** equal mobile release readiness.
4. Monetization being live at baseline does **not** mean monetization depth is finished.
5. Architecture waves being delivered does **not** mean overall product execution is complete.

---

## 9. Suggested maintenance rule

When any roadmap/status file is edited:

- update `MASTER_ROADMAP.md` first if execution truth changed
- update this file if document roles or cross-area status changed
- keep supporting docs scoped to their purpose
- avoid reintroducing whole-project “all done” language unless the top three remaining tails are actually closed

---

## 10. One-sentence summary

**ANCAP is a largely built ACP-first workflow platform whose main remaining work is security/CI/prod hardening, mobile wallet release closure, and monetization depth — and `MASTER_ROADMAP.md` remains the final authority on execution truth.**
