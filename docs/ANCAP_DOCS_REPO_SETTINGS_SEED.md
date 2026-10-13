# ANCAP docs repo settings seed

Status: active settings baseline for the live public `ancap-docs` repository.

This seed captures the baseline repository settings that should be applied during the first public launch so the repo does not depend on ad-hoc memory or one-off clicking.

## Purpose

Use this seed to configure the live public `ancap-docs` repository consistently and to keep later owner/org migration aligned with the same baseline.

It complements:
- `docs/ANCAP_DOCS_REPO_BOOTSTRAP.md` for the human checklist
- `.github/bootstrap/ancap-docs-repo-settings.json` for machine-readable setup values
- `docs/ANCAP_DOCS_UPDATE_CADENCE_SEED.md` for the public communication rhythm that should match the repo surface once it launches

## Repository metadata

Recommended baseline:
- **Visibility:** public
- **Description:** `Public-safe documentation, roadmap, trust, and integration surface for ANCAP.`
- **Homepage:** `https://ancap.cloud/`
- **Default branch:** `main`
- **Wiki:** disabled unless public docs maintenance clearly needs it later
- **Projects:** enabled if the public roadmap board is hosted in GitHub Projects
- **Discussions:** enabled
- **Issues:** enabled
- **Releases:** enabled
- **Merge commits:** disabled
- **Squash merge:** enabled
- **Rebase merge:** optional, default off unless maintainers prefer it
- **Auto-delete head branches:** enabled

## Branch protection baseline

Protect the default branch with at least:
- pull requests required before merge
- at least 1 approval required
- dismiss stale approvals on new commits
- require conversation resolution before merge
- block force pushes
- block branch deletion
- require status checks after the public CI workflow exists
- require CODEOWNERS review once maintainer/team mapping is finalized

Recommended apply path once the public repo exists:
- for the first launch, `python scripts/bootstrap_ancap_docs_repo.py --repo <owner>/ancap-docs --apply --create-repo` can create the empty public repo before the exported bundle is pushed;
- then use `python scripts/bootstrap_ancap_docs_repo.py --repo <owner>/ancap-docs --apply` to apply the repo metadata, vulnerability alerts, labels, and milestones from the checked-in seeds;
- after the first exported bundle push and once the real public CI context names are known, use `python scripts/bootstrap_ancap_docs_repo.py --repo <owner>/ancap-docs --apply --apply-branch-protection --status-check-context <context>` so the protection payload is generated from the same seed instead of hand-authoring JSON at launch time;
- keep the chosen status-check context names documented here and in `.github/bootstrap/ancap-docs-repo-settings.json` if the expected CI surface changes.

Current live status:
- `ancapcloud/ancap-docs` now exists and already has the initial public-safe docs seed pushed to `main`;
- description/homepage/merge policy/secret scanning/push protection/labels/milestones are already applied live from this seed set;
- branch protection is now applied live on `main` with the seeded `Docs CI / docs-bundle` required-check context;
- `python scripts/bootstrap_ancap_docs_repo.py --repo <owner>/ancap-docs --verify-live` can compare the live repo metadata and protection state against this seed after launch-time changes.

## Security / trust baseline

Enable when available for the owner/account plan:
- secret scanning
- push protection
- Dependabot alerts
- Code scanning / CodeQL if the repo later gains enough code to justify it
- vulnerability reporting via `SECURITY.md`

## Notes

- Keep the repo **docs-first and public-safe**. Do not enable workflows or integrations that require private deploy secrets unless they are explicitly scoped for a public repository.
- If the repo launches under a personal owner before an org exists, keep the same settings model so migration later is mostly mechanical.
- If GitHub Projects is unavailable for the target owner/account plan, keep the roadmap board documented in `docs/ANCAP_DOCS_PROJECT_BOARD_SEED.md` and defer the live board without blocking repo creation.

## Definition of done for this seed

This seed is doing its job when the initial repo settings and branch-protection baseline can be applied from a documented source instead of memory, screenshots, or launch-day improvisation.
