# Public changelog

Curated public-facing changelog for major ANCAP repository milestones.

For exhaustive implementation detail, see [LOG.md](../LOG.md).

## 2026-09-30 — new Oracle Always Free ACP node + wallet send hardening

- announced a **new ACP node** host on Oracle Cloud Always Free Ampere A1 in `eu-zurich-1` (secondary peer beside primary `acp1.ancap.cloud`); public plan: [`docs/ORACLE_CLOUD_ACP_NODE_PLAN.md`](ORACLE_CLOUD_ACP_NODE_PLAN.md)
- added operator bootstrap helper [`scripts/deploy-oracle-acp-node.ps1`](../scripts/deploy-oracle-acp-node.ps1) for native ARM64 `acp-node` Docker build on the VM
- wallet ACP withdraw path now prefers indexed UTXOs and an async job queue so personal sends no longer hang on full tip scans

## 2026-09-12 — startup investment desk (IT gazelle literacy)

- added public `/startups` desk with ACP-paid screens of AI/ML, retail/e-commerce B2B ops, SECaaS, and agrotech/production software
- cited CNews/Spark-Interfax ICT gazelles, Forbes/FRIИ small-IT growth, Sky.pro idea ranges, and businessmens.ru 2026 niches as literacy — not a securities offering
- legal `/legal/research-refs` §9 + `docs/STARTUP_INVEST_DESK.md`

## 2026-09-12 — false work-stop blockers cleared in status docs

- Phase 1 GitHub community files (`README.md`, `LICENSE`, `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`) are recorded as present; progress bots must not report missing README
- First ACP-first revenue loop remains live; monetization depth is optional follow-through, not a work-stop blocker
- Compact status surfaces (`STATUS.md`, `docs/STATUS_MATRIX.md`, `MASTER_ROADMAP.md`) now say **work-stop blockers: none**

## 2026-06-01 — ancap-docs live follow-up truth surfaced

- refreshed the checked-in status surfaces so they now explicitly reflect the live `ancapcloud/ancap-docs` repo state instead of stopping at launch-day notes
- captured that the public docs repo is already live with the exported bundle pushed, Docs CI green on `main`, checked-in settings / labels / milestones applied, and default-branch protection enforced with the seeded `Docs CI / docs-bundle` check
- recorded the first paired live follow-up artifact result from `scripts/generate_ancap_docs_live_followup.py`, including that the current run reported `8` concrete drifts and `0` unknowns rather than generic "still needs follow-up" wording
- documented that the same wrapper now refreshes stable latest-alias handoff files (`tmp/ancap-docs-live-follow-up-latest.md` and `tmp/ancap-docs-live-follow-up-latest.json`) with embedded artifact metadata, now including generator repo HEAD provenance, so cron/reporting follow-through can read the latest verified public-repo state without reconstructing a date suffix
- documented that `python scripts/generate_ancap_docs_live_followup.py --repo <owner>/ancap-docs --fail-on-not-ok` now doubles as a drift alarm by returning exit code `2` while still writing the paired markdown + JSON follow-up artifacts
- tightened the wrapper's terminal summary too: successful runs now print per-scope drift counts plus grouped manual follow-up totals from `driftSummary` / `manualFollowUpSummary`, so cron/CI logs can tell at a glance whether remaining work is discussion pinning/category cleanup or project-board auth/seeding without reopening the saved JSON artifact
- hardened that wrapper against path-collision footguns too: if a caller tries `--date-label latest` while latest aliases are still enabled, it now fails fast and tells them to pick a different date label or pass `--no-write-latest-alias` instead of silently collapsing the dated artifact pair onto the stable alias paths
- tightened the wrapper's filename guard rails as well: `--basename` and `--date-label` now have to stay plain filename components instead of path fragments like `nested/path` or `..`, which keeps artifact writes anchored under the intended `--output-dir`
- narrowed those remaining drifts to manual GitHub Discussions cleanup plus project-board auth/seeding: extra default `General` / `Polls` categories, default category descriptions that still need the checked-in ANCAP wording, unpinned seeded bootstrap topics, and the still-missing `read:project` scope for live board verification

## 2026-05-30 — contract trust index + public examples index

- added `docs/OFFICIAL_CONTRACT_ADDRESSES.md` as the public-safe canonical index for ACP / `wACP` / `BridgeGateway` identities
- linked the official address index from trust, verification, pilot, deployment, and contract-doc surfaces so reviewers have one canonical public lookup path
- kept fake-contract / scam-warning guidance next to the official address list for the future `ancap-docs` trust surface
- added `docs/PUBLIC_INTEGRATION_EXAMPLES.md` as a contributor-friendly index for publishable payment, wallet, and bridge-facing example surfaces
- linked that new examples index from repo/docs landing surfaces so the seeded public integration backlog no longer depends on browsing the monorepo tree manually

## 2026-05-27 — release + transparency + deployment-story cleanup

- added a tag-driven GitHub release workflow with draft release generation and release-gate checks
- published public integration examples for Stripe-backed credit top-up and wallet-auth flow
- linked public `wACP` / `BridgeGateway` contract sources more clearly from repo-facing docs
- removed the abandoned Cloudflare Workers repo path so Docker/nginx remains the single declared production deployment path

## 2026-05-27 — Stripe / payouts / deploy hardening

- shipped Stripe-backed ANCAP credit top-up adapter surfaces
- shipped payout request workflow
- fixed a real production-like Alembic migration defect exposed during live deploy
- tightened CI so frontend e2e reruns on backend/migration changes
- cleaned repo/dev docs/config around bundled Postgres default-secret scanning false positives

## 2026-05-24 — mobile SDK native helper exports

- expanded `ancap-mobile` SDK native helper exports
- synchronized mobile roadmap status with actual shipped capability

## 2026-04-30 — ACP wallet balance correctness

- corrected creator-vesting labeling and genesis vout layout assumptions
- improved ACP balance presentation and integer-safe amount handling

## 2026-04-29 — frontend audit and local ACP chain bring-up

- landed a frontend UX/a11y/privacy/SEO audit pass
- brought up local ACP chain/genesis flow for real wallet balance visibility
- repaired backend test suite and fixed several production bugs surfaced by tests

## Notes

This changelog is intentionally selective and public-facing.
It should summarize meaningful external milestones, while [LOG.md](../LOG.md) remains the detailed internal change log for reproducibility.
