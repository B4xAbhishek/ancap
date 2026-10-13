# ANCAP docs split plan (`ancap-docs`)

Status: active prep for the public docs repo split.

This document defines the first public-safe export bundle for the future `ancap-docs` repository so the repo can be created quickly once GitHub org/repo access is available.

## Goal

Create a clean, repeatable docs-only bundle that can seed a public `ancap-docs` repository without leaking private infrastructure, secrets, or operational internals.

## Seed bundle

The initial export should include:

- root governance/project files:
  - `README.md` (docs-repo landing page exported from `docs/ANCAP_DOCS_REPO_README.md`, not the monorepo operations README)
  - `LICENSE`
  - `CONTRIBUTING.md`
  - `SECURITY.md`
  - `CODE_OF_CONDUCT.md`
  - `.github/CODEOWNERS`
  - `.github/bootstrap/README.md`
  - `.github/pull_request_template.md`
  - `.github/ISSUE_TEMPLATE/bug_report.md`
  - `.github/ISSUE_TEMPLATE/feature_request.md`
  - `.github/ISSUE_TEMPLATE/config.yml`
  - `.github/bootstrap/README.md`
  - `.github/bootstrap/ancap-docs-contributor-intake.json`
  - `.github/bootstrap/ancap-docs-labels.json`
  - `.github/bootstrap/ancap-docs-milestones.json`
  - `.github/bootstrap/ancap-docs-discussions.json`
  - `.github/bootstrap/ancap-docs-project-board.json`
  - `.github/bootstrap/ancap-docs-initial-issues.json`
  - `.github/bootstrap/ancap-docs-repo-settings.json`
  - `.github/bootstrap/ancap-docs-update-cadence.json`
  - `.github/bootstrap/ancap-docs-ci.json`
  - `.github/bootstrap/ancap-docs-ci-workflow.yml`
  - `.github/bootstrap/ancap-docs-dependabot.yml`
  - `.github/workflows/docs-ci.yml`
  - `.github/dependabot.yml`
  - `MASTER_ROADMAP.md`
- public-facing status and open-source docs:
  - `docs/STATUS_MATRIX.md`
  - `docs/OPEN_SOURCE_GITHUB_TRANSPARENCY.md`
  - `docs/ANCAP_DOCS_REPO_BOOTSTRAP.md`
  - `docs/ANCAP_DOCS_CONTRIBUTOR_INTAKE_SEED.md`
  - `docs/ANCAP_DOCS_LABEL_SEED.md`
  - `docs/ANCAP_DOCS_DISCUSSIONS_SEED.md`
  - `docs/ANCAP_DOCS_MILESTONE_SEED.md`
  - `docs/ANCAP_DOCS_PROJECT_BOARD_SEED.md`
  - `docs/ANCAP_DOCS_INITIAL_ISSUES_SEED.md`
  - `docs/ANCAP_DOCS_REPO_SETTINGS_SEED.md`
  - `docs/ANCAP_DOCS_UPDATE_CADENCE_SEED.md`
  - `docs/ANCAP_DOCS_DEPENDABOT_SEED.md`
  - `docs/VISION.md`
  - `docs/ARCHITECTURE_LAYERS.md`
  - `docs/PLAN_L0_TO_L3.md`
  - `docs/REPUTATION_2.md`
  - `docs/STAKING.md`
  - `docs/WHITEPAPER_PROJECT.md`
  - `docs/WHITEPAPER_ACP.md`
  - `docs/LEGAL_TERMS_TEMPLATE.md`
  - `docs/BRIDGE_RISK_DOCUMENTATION.md`
  - `docs/OFFICIAL_CONTRACT_ADDRESSES.md`
  - `docs/CONTRACT_VERIFICATION_GUIDE.md`
  - `docs/TESTNET_DEPLOYMENT_GUIDE.md`
  - `docs/AUDIT_CHECKLIST.md`
  - `docs/CHANGELOG_PUBLIC.md`
  - `docs/PUBLIC_INTEGRATION_EXAMPLES.md`

## Explicitly excluded

Do **not** export:

- `.env`, deploy secrets, API keys, mnemonics, private keys
- bridge signer private logic or hot-wallet operating procedures
- server credentials and internal infrastructure notes
- abuse-sensitive thresholds or internal anti-fraud/operator runbooks
- `Sicret/`, `infra/`, and private deployment material unless reviewed and sanitized separately

## Repeatable export

Use:

```bash
python scripts/export_ancap_docs.py --target <path-to-export-dir> --clean
```

The script copies the approved public-safe files, exports a docs-focused root `README.md` from `docs/ANCAP_DOCS_REPO_README.md`, includes the public-safe GitHub issue/PR templates needed for a contributor-ready docs repo, ships a baseline `.github/CODEOWNERS` seed so review routing does not need to be improvised on first push, ships `.github/bootstrap/README.md` so the machine-readable seeds are self-describing instead of a loose JSON pile, ships `docs/ANCAP_DOCS_REPO_BOOTSTRAP.md` so the first public repo push has a documented creation/settings/labels/Discussions/milestones/project-board/initial-issues/repo-settings/update-cadence/CI checklist, ships `docs/ANCAP_DOCS_CONTRIBUTOR_INTAKE_SEED.md` plus `.github/bootstrap/ancap-docs-contributor-intake.json` so the issue/PR intake lanes and security-report routing are explicit and reusable too, ships `docs/ANCAP_DOCS_LABEL_SEED.md` so the initial public label taxonomy is explicit and reusable, ships `docs/ANCAP_DOCS_DISCUSSIONS_SEED.md` so the initial Discussions categories/moderation lanes plus copy-ready pinned-topic text are explicit and reusable too, ships `docs/ANCAP_DOCS_MILESTONE_SEED.md` so the initial milestone taxonomy is explicit and reusable too, ships `docs/ANCAP_DOCS_PROJECT_BOARD_SEED.md` so the initial project-board shape is explicit and reusable too, ships `docs/ANCAP_DOCS_INITIAL_ISSUES_SEED.md` plus `.github/bootstrap/ancap-docs-initial-issues.json` so the first public issue backlog is explicit and reusable too, ships `docs/ANCAP_DOCS_REPO_SETTINGS_SEED.md` so the initial public repo metadata/features/branch-protection baseline is explicit and reusable too, ships `docs/ANCAP_DOCS_UPDATE_CADENCE_SEED.md` so the initial public communication rhythm plus copy-ready update/release-note templates are explicit and reusable too, ships `docs/ANCAP_DOCS_CI_SEED.md` plus a copy-ready `.github/workflows/docs-ci.yml` so the initial public CI workflow and default required-check context are explicit and reusable too, also ships the matching `.github/bootstrap/ancap-docs-ci-workflow.yml` template referenced by the CI seed so launch-day workflow bootstrap does not depend on an unexported file, ships `docs/ANCAP_DOCS_DEPENDABOT_SEED.md` plus a docs-repo-specific exported `.github/dependabot.yml` so dependency-update automation for the public docs repo does not accidentally inherit the broader monorepo ecosystems, also carries the matching `.github/bootstrap/ancap-docs-dependabot.yml` template for launch-day alignment, exports machine-readable `.github/bootstrap/*.json` seeds for contributor-intake/labels/milestones/Discussions/project-board/initial-issues/repo-settings/update-cadence/CI setup so the future public repo can be bootstrapped without retyping metadata by hand, keeps the matching source-monorepo bootstrap helper in `scripts/bootstrap_ancap_docs_repo.py` for gh-driven repo settings/labels/milestones application from those seeds plus the later default-branch protection payload once public CI status-check names exist, rewrites links that point outside the export bundle to the source monorepo on GitHub, validates that the standalone bundle has no broken relative Markdown links, treats the docs-repo Dependabot template as another exported drift-guard artifact inside the public bundle, and writes `EXPORT_MANIFEST.md` into the target bundle.

## Current remaining follow-up

GitHub org creation is still external, but the public docs repo now exists at `https://github.com/ancapcloud/ancap-docs`. Current checks from this cron run show:

- `https://github.com/ANCAP` resolves to an existing unrelated GitHub user profile (`ancap`)
- `https://github.com/ancap-network` returns GitHub 404
- `gh api orgs/ANCAP` and `gh api orgs/ancap-network` both fail with `admin:org` scope requirement in the current auth context
- `gh repo view ancapcloud/ancap-docs` now succeeds, the repo is public, and the exported bundle has been pushed as the first seed commit
- `gh run list --repo ancapcloud/ancap-docs --limit 5` shows the exported `Docs CI` workflow already ran successfully on `main`
- repo settings/labels/milestones and default-branch protection are now applied live; the helper can also verify that live repo state still matches the checked-in seeds via `python scripts/bootstrap_ancap_docs_repo.py --repo <owner>/ancap-docs --verify-live`
- `python scripts/generate_ancap_docs_live_followup.py --repo <owner>/ancap-docs` now wraps the paired markdown + JSON handoff into one repeatable command, keeping the preferred saved artifact pair `tmp/ancap-docs-live-follow-up-YYYY-MM-DD.md` and `tmp/ancap-docs-live-follow-up-YYYY-MM-DD.json` aligned and, by default, also refreshing the stable latest aliases `tmp/ancap-docs-live-follow-up-latest.md` and `tmp/ancap-docs-live-follow-up-latest.json`
- those saved artifacts now embed artifact metadata (`artifactMetadata` in JSON plus an `Artifact metadata` appendix in markdown) including generator/bootstrap source paths, UTC generation time, and generator repo HEAD provenance
- use `--no-write-latest-alias` when only the dated artifacts should be written; the wrapper refuses `--date-label latest` while latest-alias writes stay enabled, rejects path-shaped `--basename` / `--date-label` values that would escape `--output-dir`, stays concise by default unless `--verbose-child-output` is requested, and `--fail-on-not-ok` returns exit code `2` for cron/CI drift alarms when the JSON summary is not OK
- the generated markdown handoff now includes `Discussion UI targets` plus `Project board seed targets`; live board verification is still blocked by missing `read:project` scope under the current auth, and the copy-ready remediation is `gh auth refresh -h github.com -s read:project`
- current honest live drift is still the remaining Discussions/admin follow-up: extra `General` / `Polls` categories, default category descriptions that still need the checked-in ANCAP wording, unpinned seeded bootstrap topics, and final org ownership/migration decisions

So the split is no longer just theoretical prep: the public docs repo is seeded and live, while org ownership and the remaining Discussions/project-board follow-up stay the next external/live steps.

## Done definition for this prep slice

This prep slice is complete when:

1. the export set is documented,
2. the export command is scripted and repeatable,
3. tests lock the bundle contents, link-rewrite behavior, and safety boundaries,
4. the future repo can be created from the generated bundle without manual scavenging through the monorepo,
5. contributor-facing issue/PR templates are already present in the exported seed instead of needing a second manual copy step,
6. a baseline public-safe `.github/CODEOWNERS` file is exported so review routing starts from an explicit default instead of memory,
7. exported Markdown stays navigable as a standalone docs repo seed instead of shipping broken in-bundle relative links,
8. the bundle root opens with a docs-focused landing page instead of the full monorepo/operator README,
9. the future repo bootstrap steps (initial push, baseline settings, labels, Discussions enablement) are documented inside the exported bundle instead of living only in cron notes,
10. the initial public label taxonomy is exported as a reusable seed instead of being recreated ad hoc during repo setup,
11. the initial GitHub Discussions category model is exported as a reusable seed instead of being improvised at repo launch,
12. the initial GitHub milestone model is exported as a reusable seed instead of being improvised during the first public roadmap/release-tracking pass,
13. the initial GitHub project-board shape is exported as a reusable seed instead of being improvised during the first public contributor-triage pass.
14. the initial public starter issue backlog is exported as a reusable seed instead of being improvised from chat memory during the first contributor-triage pass.
15. the initial repo metadata / feature toggles / branch-protection baseline are exported as a reusable seed instead of being improvised during launch.
16. the initial public update/release-note cadence is exported as a reusable seed instead of being improvised after repo launch.
17. the bundle also carries machine-readable bootstrap metadata for labels, milestones, Discussions, the first project board, the first public starter issues, repo settings, and update cadence so maintainers can script or batch the first public repo setup instead of retyping values from Markdown.
18. the Discussions seed already contains copy-ready pinned-topic text instead of only category names and moderation notes.
19. the update-cadence seed already contains copy-ready monthly-update / release-note / trust-change templates instead of only a structural outline.
20. the source monorepo also carries a reusable gh-driven bootstrap helper for repo settings, labels, milestones, and the later default-branch protection payload so the first public repo setup does not depend on manually retyping seed values into GitHub.
21. the bundle already includes a copy-ready public Docs CI workflow plus an explicit CI seed so required status-check names do not need to be guessed during launch.
22. the CI seed's referenced workflow template is exported too, so public-repo bootstrap does not point at a source-only file that disappears in the bundle.
23. the bundle includes a docs-repo-specific `.github/dependabot.yml` plus a matching Dependabot seed/template so launch-day dependency automation does not blindly reuse the source monorepo's broader package ecosystems.
24. the exported Docs CI workflow also guards the docs-repo Dependabot template against byte-for-byte drift from the shipped public `.github/dependabot.yml`, while leaving the source monorepo free to keep its broader multi-ecosystem Dependabot config.
25. the bundle includes a human-readable contributor-intake seed plus matching machine-readable metadata so issue/PR intake lanes and security-report routing are not left implicit inside template files alone.
26. the bundle includes a human-readable initial-issues seed plus matching machine-readable metadata so the first public backlog can be seeded from checked-in truth instead of recreated from memory at launch.
