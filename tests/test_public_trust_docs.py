from pathlib import Path


README_PATH = Path("README.md")
OPEN_SOURCE_DOC_PATH = Path("docs/OPEN_SOURCE_GITHUB_TRANSPARENCY.md")
ROADMAP_PATH = Path("MASTER_ROADMAP.md")
DOCS_SPLIT_PLAN_PATH = Path("docs/ANCAP_DOCS_SPLIT.md")
DOCS_REPO_BOOTSTRAP_PATH = Path("docs/ANCAP_DOCS_REPO_BOOTSTRAP.md")
DOCS_CONTRIBUTOR_INTAKE_SEED_PATH = Path("docs/ANCAP_DOCS_CONTRIBUTOR_INTAKE_SEED.md")
DOCS_LABEL_SEED_PATH = Path("docs/ANCAP_DOCS_LABEL_SEED.md")
DOCS_DISCUSSIONS_SEED_PATH = Path("docs/ANCAP_DOCS_DISCUSSIONS_SEED.md")
DOCS_MILESTONE_SEED_PATH = Path("docs/ANCAP_DOCS_MILESTONE_SEED.md")
DOCS_PROJECT_BOARD_SEED_PATH = Path("docs/ANCAP_DOCS_PROJECT_BOARD_SEED.md")
DOCS_INITIAL_ISSUES_SEED_PATH = Path("docs/ANCAP_DOCS_INITIAL_ISSUES_SEED.md")
DOCS_REPO_SETTINGS_SEED_PATH = Path("docs/ANCAP_DOCS_REPO_SETTINGS_SEED.md")
DOCS_UPDATE_CADENCE_SEED_PATH = Path("docs/ANCAP_DOCS_UPDATE_CADENCE_SEED.md")
DOCS_CI_SEED_PATH = Path("docs/ANCAP_DOCS_CI_SEED.md")
DOCS_DEPENDABOT_SEED_PATH = Path("docs/ANCAP_DOCS_DEPENDABOT_SEED.md")
EXPORT_SCRIPT_PATH = Path("scripts/export_ancap_docs.py")
BOOTSTRAP_SCRIPT_PATH = Path("scripts/bootstrap_ancap_docs_repo.py")
DOCS_REPO_README_SOURCE_PATH = Path("docs/ANCAP_DOCS_REPO_README.md")

BRIDGE_RISK_DOC = Path("docs/BRIDGE_RISK_DOCUMENTATION.md")
OFFICIAL_CONTRACT_ADDRESSES_DOC = Path("docs/OFFICIAL_CONTRACT_ADDRESSES.md")
CONTRACT_VERIFICATION_DOC = Path("docs/CONTRACT_VERIFICATION_GUIDE.md")
TESTNET_DEPLOYMENT_DOC = Path("docs/TESTNET_DEPLOYMENT_GUIDE.md")
AUDIT_CHECKLIST_DOC = Path("docs/AUDIT_CHECKLIST.md")
PUBLIC_CHANGELOG_DOC = Path("docs/CHANGELOG_PUBLIC.md")
PUBLIC_INTEGRATION_EXAMPLES_DOC = Path("docs/PUBLIC_INTEGRATION_EXAMPLES.md")
WHITEPAPER_PAGE_PATH = Path("frontend-app/src/app/whitepaper/page.tsx")


def test_public_trust_docs_exist_and_are_linked_from_readme():
    readme_text = README_PATH.read_text(encoding="utf-8")

    for path in [
        BRIDGE_RISK_DOC,
        OFFICIAL_CONTRACT_ADDRESSES_DOC,
        CONTRACT_VERIFICATION_DOC,
        TESTNET_DEPLOYMENT_DOC,
        AUDIT_CHECKLIST_DOC,
        PUBLIC_CHANGELOG_DOC,
        PUBLIC_INTEGRATION_EXAMPLES_DOC,
    ]:
        assert path.exists(), f"missing doc: {path}"

    assert "docs/BRIDGE_RISK_DOCUMENTATION.md" in readme_text
    assert "docs/OFFICIAL_CONTRACT_ADDRESSES.md" in readme_text
    assert "docs/CONTRACT_VERIFICATION_GUIDE.md" in readme_text
    assert "docs/TESTNET_DEPLOYMENT_GUIDE.md" in readme_text
    assert "docs/AUDIT_CHECKLIST.md" in readme_text
    assert "docs/CHANGELOG_PUBLIC.md" in readme_text
    assert "docs/PUBLIC_INTEGRATION_EXAMPLES.md" in readme_text


def test_open_source_transparency_doc_points_to_public_trust_docs():
    doc_text = OPEN_SOURCE_DOC_PATH.read_text(encoding="utf-8")

    assert "docs/BRIDGE_RISK_DOCUMENTATION.md" in doc_text
    assert "docs/OFFICIAL_CONTRACT_ADDRESSES.md" in doc_text
    assert "docs/CONTRACT_VERIFICATION_GUIDE.md" in doc_text
    assert "docs/TESTNET_DEPLOYMENT_GUIDE.md" in doc_text
    assert "docs/AUDIT_CHECKLIST.md" in doc_text
    assert "docs/CHANGELOG_PUBLIC.md" in doc_text
    assert "docs/PUBLIC_INTEGRATION_EXAMPLES.md" in doc_text


def test_public_changelog_records_latest_ancap_docs_followup_contract():
    changelog_text = PUBLIC_CHANGELOG_DOC.read_text(encoding="utf-8")

    assert "scripts/generate_ancap_docs_live_followup.py" in changelog_text
    assert "tmp/ancap-docs-live-follow-up-latest.md" in changelog_text
    assert "tmp/ancap-docs-live-follow-up-latest.json" in changelog_text
    assert "--fail-on-not-ok" in changelog_text
    assert "exit code `2`" in changelog_text
    assert "artifact metadata" in changelog_text


def test_whitepaper_marks_unshipped_payment_scanner_and_claim_codes_as_planned_only():
    whitepaper_text = Path("frontend-app/src/locales/whitepaper.ts").read_text(encoding="utf-8")

    assert "planned AI Payment Scanner flows" in whitepaper_text
    assert "that scanner layer is not shipped today" in whitepaper_text
    assert "AI Payment Scanner (planned, not shipped yet)" in whitepaper_text
    assert "ANCAP Claim Codes (planned, not shipped yet)" in whitepaper_text


def test_master_roadmap_marks_documented_sprint3_items_done():
    roadmap_text = ROADMAP_PATH.read_text(encoding="utf-8")

    assert "- [x] Add bridge risk documentation" in roadmap_text
    assert "- [x] Add contract verification guide" in roadmap_text
    assert "- [x] Add public changelog" in roadmap_text
    assert "- [x] Add release tags" in roadmap_text
    assert "- [x] Add testnet deployment guide" in roadmap_text
    assert "- [x] Add audit checklist" in roadmap_text


def test_docs_split_plan_and_export_script_are_linked_and_reflected_in_roadmap():
    readme_text = README_PATH.read_text(encoding="utf-8")
    open_source_doc_text = OPEN_SOURCE_DOC_PATH.read_text(encoding="utf-8")
    roadmap_text = ROADMAP_PATH.read_text(encoding="utf-8")
    status_matrix_text = Path("docs/STATUS_MATRIX.md").read_text(encoding="utf-8")
    docs_split_text = DOCS_SPLIT_PLAN_PATH.read_text(encoding="utf-8")
    docs_repo_readme_text = DOCS_REPO_README_SOURCE_PATH.read_text(encoding="utf-8")

    docs_bootstrap_text = DOCS_REPO_BOOTSTRAP_PATH.read_text(encoding="utf-8")
    docs_contributor_seed_text = DOCS_CONTRIBUTOR_INTAKE_SEED_PATH.read_text(encoding="utf-8")
    docs_label_seed_text = DOCS_LABEL_SEED_PATH.read_text(encoding="utf-8")
    docs_discussions_seed_text = DOCS_DISCUSSIONS_SEED_PATH.read_text(encoding="utf-8")
    docs_milestone_seed_text = DOCS_MILESTONE_SEED_PATH.read_text(encoding="utf-8")
    docs_project_board_seed_text = DOCS_PROJECT_BOARD_SEED_PATH.read_text(encoding="utf-8")
    docs_initial_issues_seed_text = DOCS_INITIAL_ISSUES_SEED_PATH.read_text(encoding="utf-8")
    docs_repo_settings_seed_text = DOCS_REPO_SETTINGS_SEED_PATH.read_text(encoding="utf-8")
    docs_update_cadence_seed_text = DOCS_UPDATE_CADENCE_SEED_PATH.read_text(encoding="utf-8")
    docs_ci_seed_text = DOCS_CI_SEED_PATH.read_text(encoding="utf-8")
    docs_dependabot_seed_text = DOCS_DEPENDABOT_SEED_PATH.read_text(encoding="utf-8")
    bootstrap_script_text = BOOTSTRAP_SCRIPT_PATH.read_text(encoding="utf-8")

    assert DOCS_SPLIT_PLAN_PATH.exists()
    assert DOCS_REPO_BOOTSTRAP_PATH.exists()
    assert DOCS_CONTRIBUTOR_INTAKE_SEED_PATH.exists()
    assert DOCS_LABEL_SEED_PATH.exists()
    assert DOCS_DISCUSSIONS_SEED_PATH.exists()
    assert DOCS_MILESTONE_SEED_PATH.exists()
    assert DOCS_PROJECT_BOARD_SEED_PATH.exists()
    assert DOCS_INITIAL_ISSUES_SEED_PATH.exists()
    assert DOCS_REPO_SETTINGS_SEED_PATH.exists()
    assert DOCS_UPDATE_CADENCE_SEED_PATH.exists()
    assert DOCS_CI_SEED_PATH.exists()
    assert DOCS_DEPENDABOT_SEED_PATH.exists()
    assert EXPORT_SCRIPT_PATH.exists()
    assert BOOTSTRAP_SCRIPT_PATH.exists()
    assert DOCS_REPO_README_SOURCE_PATH.exists()
    assert "docs/ANCAP_DOCS_SPLIT.md" in readme_text
    assert "docs/ANCAP_DOCS_REPO_BOOTSTRAP.md" in readme_text
    assert "docs/ANCAP_DOCS_CONTRIBUTOR_INTAKE_SEED.md" in readme_text
    assert "docs/ANCAP_DOCS_LABEL_SEED.md" in readme_text
    assert "docs/ANCAP_DOCS_DISCUSSIONS_SEED.md" in readme_text
    assert "docs/ANCAP_DOCS_MILESTONE_SEED.md" in readme_text
    assert "docs/ANCAP_DOCS_PROJECT_BOARD_SEED.md" in readme_text
    assert "docs/ANCAP_DOCS_INITIAL_ISSUES_SEED.md" in readme_text
    assert "docs/ANCAP_DOCS_REPO_SETTINGS_SEED.md" in readme_text
    assert "docs/ANCAP_DOCS_UPDATE_CADENCE_SEED.md" in readme_text
    assert "docs/ANCAP_DOCS_CI_SEED.md" in readme_text
    assert "docs/ANCAP_DOCS_DEPENDABOT_SEED.md" in readme_text
    assert ".github/CODEOWNERS" in readme_text
    assert ".github/bootstrap/" in readme_text
    assert "docs/ANCAP_DOCS_SPLIT.md" in open_source_doc_text
    assert "docs/ANCAP_DOCS_REPO_BOOTSTRAP.md" in open_source_doc_text
    assert "docs/ANCAP_DOCS_CONTRIBUTOR_INTAKE_SEED.md" in open_source_doc_text
    assert "docs/ANCAP_DOCS_LABEL_SEED.md" in open_source_doc_text
    assert "docs/ANCAP_DOCS_DISCUSSIONS_SEED.md" in open_source_doc_text
    assert "docs/ANCAP_DOCS_MILESTONE_SEED.md" in open_source_doc_text
    assert "docs/ANCAP_DOCS_PROJECT_BOARD_SEED.md" in open_source_doc_text
    assert "docs/ANCAP_DOCS_INITIAL_ISSUES_SEED.md" in open_source_doc_text
    assert "docs/ANCAP_DOCS_REPO_SETTINGS_SEED.md" in open_source_doc_text
    assert "docs/ANCAP_DOCS_UPDATE_CADENCE_SEED.md" in open_source_doc_text
    assert "docs/ANCAP_DOCS_CI_SEED.md" in open_source_doc_text
    assert "docs/ANCAP_DOCS_DEPENDABOT_SEED.md" in open_source_doc_text
    assert ".github/bootstrap/README.md" in open_source_doc_text
    assert ".github/bootstrap/ancap-docs-contributor-intake.json" in open_source_doc_text
    assert ".github/bootstrap/ancap-docs-labels.json" in open_source_doc_text
    assert ".github/bootstrap/ancap-docs-milestones.json" in open_source_doc_text
    assert ".github/bootstrap/ancap-docs-discussions.json" in open_source_doc_text
    assert ".github/bootstrap/ancap-docs-project-board.json" in open_source_doc_text
    assert ".github/bootstrap/ancap-docs-initial-issues.json" in open_source_doc_text
    assert ".github/bootstrap/ancap-docs-repo-settings.json" in open_source_doc_text
    assert ".github/bootstrap/ancap-docs-update-cadence.json" in open_source_doc_text
    assert ".github/bootstrap/ancap-docs-ci.json" in open_source_doc_text
    assert ".github/bootstrap/ancap-docs-ci-workflow.yml" in open_source_doc_text
    assert ".github/bootstrap/ancap-docs-dependabot.yml" in open_source_doc_text
    assert ".github/workflows/docs-ci.yml" in open_source_doc_text
    assert "scripts/export_ancap_docs.py" in open_source_doc_text
    assert "public repo creation" in open_source_doc_text
    assert ".github/CODEOWNERS" in docs_split_text
    assert ".github/pull_request_template.md" in docs_split_text
    assert ".github/ISSUE_TEMPLATE/bug_report.md" in docs_split_text
    assert "docs/ANCAP_DOCS_REPO_BOOTSTRAP.md" in docs_split_text
    assert "docs/ANCAP_DOCS_CONTRIBUTOR_INTAKE_SEED.md" in docs_split_text
    assert "docs/ANCAP_DOCS_LABEL_SEED.md" in docs_split_text
    assert "docs/ANCAP_DOCS_DISCUSSIONS_SEED.md" in docs_split_text
    assert "docs/ANCAP_DOCS_MILESTONE_SEED.md" in docs_split_text
    assert "docs/ANCAP_DOCS_PROJECT_BOARD_SEED.md" in docs_split_text
    assert "docs/ANCAP_DOCS_INITIAL_ISSUES_SEED.md" in docs_split_text
    assert "docs/ANCAP_DOCS_REPO_SETTINGS_SEED.md" in docs_split_text
    assert "docs/ANCAP_DOCS_UPDATE_CADENCE_SEED.md" in docs_split_text
    assert "docs/ANCAP_DOCS_CI_SEED.md" in docs_split_text
    assert "docs/ANCAP_DOCS_DEPENDABOT_SEED.md" in docs_split_text
    assert "docs/PUBLIC_INTEGRATION_EXAMPLES.md" in docs_split_text
    assert ".github/bootstrap/README.md" in docs_split_text
    assert ".github/bootstrap/ancap-docs-contributor-intake.json" in docs_split_text
    assert ".github/bootstrap/ancap-docs-labels.json" in docs_split_text
    assert ".github/bootstrap/ancap-docs-milestones.json" in docs_split_text
    assert ".github/bootstrap/ancap-docs-discussions.json" in docs_split_text
    assert ".github/bootstrap/ancap-docs-project-board.json" in docs_split_text
    assert ".github/bootstrap/ancap-docs-initial-issues.json" in docs_split_text
    assert ".github/bootstrap/ancap-docs-repo-settings.json" in docs_split_text
    assert ".github/bootstrap/ancap-docs-update-cadence.json" in docs_split_text
    assert ".github/bootstrap/ancap-docs-ci.json" in docs_split_text
    assert ".github/bootstrap/ancap-docs-ci-workflow.yml" in docs_split_text
    assert ".github/bootstrap/ancap-docs-dependabot.yml" in docs_split_text
    assert ".github/workflows/docs-ci.yml" in docs_split_text
    assert ".github/dependabot.yml" in docs_split_text
    assert "docs/ANCAP_DOCS_REPO_README.md" in docs_split_text
    assert "https://github.com/ancapcloud/ancap-docs" in docs_split_text
    assert "scripts/generate_ancap_docs_live_followup.py" in docs_split_text
    assert "tmp/ancap-docs-live-follow-up-YYYY-MM-DD.md" in docs_split_text
    assert "tmp/ancap-docs-live-follow-up-YYYY-MM-DD.json" in docs_split_text
    assert "tmp/ancap-docs-live-follow-up-latest.md" in docs_split_text
    assert "tmp/ancap-docs-live-follow-up-latest.json" in docs_split_text
    assert "artifactMetadata" in docs_split_text
    assert "Artifact metadata" in docs_split_text
    assert "generator repo HEAD provenance" in docs_split_text
    assert "--no-write-latest-alias" in docs_split_text
    assert "--verbose-child-output" in docs_split_text
    assert "--fail-on-not-ok" in docs_split_text
    assert "Discussion UI targets" in docs_split_text
    assert "Project board seed targets" in docs_split_text
    assert "gh auth refresh -h github.com -s read:project" in docs_split_text
    assert "General` / `Polls" in docs_split_text
    assert "docs-focused root `README.md`" in open_source_doc_text
    assert "issue/PR templates" in open_source_doc_text
    assert "contributor-intake seed" in open_source_doc_text
    assert "baseline `.github/CODEOWNERS` file" in open_source_doc_text
    assert "bootstrap checklist" in open_source_doc_text
    assert "label seed" in open_source_doc_text
    assert "Discussions seed" in open_source_doc_text
    assert "milestone seed" in open_source_doc_text
    assert "project-board seed" in open_source_doc_text
    assert "initial-issues seed" in open_source_doc_text
    assert "repo-settings seed" in open_source_doc_text
    assert "update-cadence seed" in open_source_doc_text
    assert "CI seed" in open_source_doc_text
    assert "Dependabot seed" in open_source_doc_text
    assert "copy-ready pinned-topic/update-post templates" in open_source_doc_text
    assert "matching `.github/bootstrap/ancap-docs-ci-workflow.yml` template" in open_source_doc_text
    assert "version-only bumps land without forcing the exported workflow template to change in the same PR" in open_source_doc_text
    assert "--verify-live --verify-live-community" in open_source_doc_text
    assert "scripts/generate_ancap_docs_live_followup.py" in open_source_doc_text
    assert "tmp/ancap-docs-live-follow-up-YYYY-MM-DD.md" in open_source_doc_text
    assert "tmp/ancap-docs-live-follow-up-YYYY-MM-DD.json" in open_source_doc_text
    assert "tmp/ancap-docs-live-follow-up-latest.md" in open_source_doc_text
    assert "tmp/ancap-docs-live-follow-up-latest.json" in open_source_doc_text
    assert "driftSummary" in open_source_doc_text
    assert "manualFollowUpSummary" in open_source_doc_text
    assert "if someone tries to reuse `latest` as a custom `--date-label`" in open_source_doc_text
    assert "path-shaped `--basename` / `--date-label` values" in open_source_doc_text
    assert "keep artifact writes anchored under the intended `--output-dir`" in open_source_doc_text
    assert "checklist and machine-readable snapshot stay aligned" in open_source_doc_text
    assert "artifactMetadata" in open_source_doc_text
    assert "generator repo HEAD provenance" in open_source_doc_text
    assert "Artifact metadata" in open_source_doc_text
    assert "keeps successful refreshes concise by default" in open_source_doc_text
    assert "--verbose-child-output" in open_source_doc_text
    assert "--no-write-latest-alias" in open_source_doc_text
    assert "--fail-on-not-ok" in open_source_doc_text
    assert "cron/CI drift alarm" in open_source_doc_text
    assert "PowerShell `>` redirect" in open_source_doc_text
    assert "UTF-16 file with a BOM" in open_source_doc_text
    assert "seeded labels, milestones, Discussions categories, seeded discussion-topic presence, seeded discussion-topic body alignment, pinned-discussion presence, and seeded starter-issue routing" in open_source_doc_text
    assert "later default-branch protection payload" in open_source_doc_text
    assert "docs-focused root README" in roadmap_text
    assert "issue/PR templates" in roadmap_text
    assert "contributor-intake seed" in roadmap_text
    assert "baseline CODEOWNERS review-routing seed" in roadmap_text
    assert "repo-bootstrap checklist" in roadmap_text
    assert "reusable contributor-intake/label/Discussions/milestone/project-board/initial-issues/repo-settings/update-cadence/CI/Dependabot seeds" in roadmap_text
    assert "copy-ready pinned-topic text plus monthly-update/release-note/trust-change starter templates" in roadmap_text
    assert "public repo creation, repo settings/labels/milestones, live repo verification, and the branch-protection payload" in roadmap_text
    assert "docs-repo-specific `.github/dependabot.yml`" in roadmap_text
    assert "bootstrap-seed README" in roadmap_text
    assert ".github/bootstrap/*.json" in roadmap_text
    assert ".github/workflows/docs-ci.yml" in roadmap_text
    assert ".github/bootstrap/ancap-docs-ci-workflow.yml" in roadmap_text
    assert "scripts/generate_ancap_docs_live_followup.py" in readme_text
    assert "ancap-docs-live-follow-up-YYYY-MM-DD.md" in readme_text
    assert "ancap-docs-live-follow-up-YYYY-MM-DD.json" in readme_text
    assert "ancap-docs-live-follow-up-latest.md" in readme_text
    assert "ancap-docs-live-follow-up-latest.json" in readme_text
    assert "--no-write-latest-alias" in readme_text
    assert "do not reuse `latest` unless you also pass `--no-write-latest-alias`" in readme_text
    assert "--fail-on-not-ok" in readme_text
    assert "scripts/generate_ancap_docs_live_followup.py" in roadmap_text
    assert "tmp/ancap-docs-live-follow-up-YYYY-MM-DD.md" in roadmap_text
    assert "tmp/ancap-docs-live-follow-up-YYYY-MM-DD.json" in roadmap_text
    assert "tmp/ancap-docs-live-follow-up-latest.md" in roadmap_text
    assert "tmp/ancap-docs-live-follow-up-latest.json" in roadmap_text
    assert "artifactMetadata" in roadmap_text
    assert "generator repo HEAD provenance" in roadmap_text
    assert "Artifact metadata" in roadmap_text
    assert "--no-write-latest-alias" in roadmap_text
    assert "refuses `--date-label latest` while latest-alias writes stay enabled" in roadmap_text
    assert "treats `--basename` and `--date-label` as filename components only" in roadmap_text
    assert "--fail-on-not-ok" in roadmap_text
    assert "exit-code-2 cron/CI drift alarm" in roadmap_text
    assert "current GitHub auth login/token-source/scopes when detectable" in roadmap_text
    assert "gh auth refresh -h github.com -s read:project" in roadmap_text
    assert "only echoes the underlying helper stdout/stderr when a generation step fails unless `--verbose-child-output` is set" in roadmap_text
    assert "GitHub Discussions" in docs_bootstrap_text
    assert 'copy-ready `gh api graphql --raw-field "query=..."` commands for the automatable `createDiscussion` / `updateDiscussion` portion' in docs_bootstrap_text
    assert "docs/ANCAP_DOCS_CONTRIBUTOR_INTAKE_SEED.md" in docs_bootstrap_text
    assert ".github/bootstrap/ancap-docs-contributor-intake.json" in docs_bootstrap_text
    assert ".github/CODEOWNERS" in docs_bootstrap_text
    assert "good first issue" in docs_bootstrap_text
    assert "first public roadmap board" in docs_bootstrap_text
    assert "docs-repo-specific `.github/dependabot.yml`" in docs_bootstrap_text
    assert ".github/bootstrap/ancap-docs-labels.json" in docs_bootstrap_text
    assert ".github/bootstrap/ancap-docs-milestones.json" in docs_bootstrap_text
    assert ".github/bootstrap/ancap-docs-discussions.json" in docs_bootstrap_text
    assert ".github/bootstrap/ancap-docs-project-board.json" in docs_bootstrap_text
    assert ".github/bootstrap/ancap-docs-initial-issues.json" in docs_bootstrap_text
    assert ".github/bootstrap/ancap-docs-repo-settings.json" in docs_bootstrap_text
    assert ".github/bootstrap/ancap-docs-update-cadence.json" in docs_bootstrap_text
    assert ".github/bootstrap/ancap-docs-ci.json" in docs_bootstrap_text
    assert ".github/ISSUE_TEMPLATE/bug_report.md" in docs_contributor_seed_text
    assert ".github/pull_request_template.md" in docs_contributor_seed_text
    assert "security-report routing" in docs_contributor_seed_text
    assert "help wanted" in docs_label_seed_text
    assert "Announcements" in docs_discussions_seed_text
    assert "# Welcome to ANCAP docs" in docs_discussions_seed_text
    assert "Roadmap and status sync" in docs_milestone_seed_text
    assert "ANCAP Docs Roadmap" in docs_project_board_seed_text
    assert "Align Discussions categories and pin seeded bootstrap topics" in docs_initial_issues_seed_text
    assert "good first issue" in docs_initial_issues_seed_text
    assert "Default branch" in docs_repo_settings_seed_text
    assert "branch-protection baseline" in docs_repo_settings_seed_text
    assert "--apply --create-repo" in docs_repo_settings_seed_text
    assert "--apply-branch-protection --status-check-context <context>" in docs_repo_settings_seed_text
    assert "Monthly development update" in docs_update_cadence_seed_text
    assert "# Release notes — <tag or milestone>" in docs_update_cadence_seed_text
    assert "docs-repo-specific `.github/dependabot.yml`" in docs_dependabot_seed_text
    assert ".github/bootstrap/ancap-docs-dependabot.yml" in docs_dependabot_seed_text
    assert "Docs CI / docs-bundle" in docs_ci_seed_text
    assert ".github/workflows/docs-ci.yml" in docs_ci_seed_text
    assert "--verify-live" in docs_repo_settings_seed_text
    assert "--verify-live" in docs_bootstrap_text
    assert "--verify-live-community" in docs_bootstrap_text
    assert "tmp/ancap-docs-live-follow-up-YYYY-MM-DD.md" in docs_bootstrap_text
    assert "tmp/ancap-docs-live-follow-up-YYYY-MM-DD.json" in docs_bootstrap_text
    assert "tmp/ancap-docs-live-follow-up-latest.md" in docs_bootstrap_text
    assert "tmp/ancap-docs-live-follow-up-latest.json" in docs_bootstrap_text
    assert "do not reuse `latest` as a custom `--date-label`" in docs_bootstrap_text
    assert "path-shaped input on purpose" in docs_bootstrap_text
    assert "plain filename components instead of path fragments" in docs_bootstrap_text
    assert "current GitHub auth login/token-source/scopes when detectable" in docs_bootstrap_text
    assert "gh auth refresh -h github.com -s read:project" in docs_bootstrap_text
    assert "scripts/generate_ancap_docs_live_followup.py" in docs_bootstrap_text
    assert "driftSummary" in docs_bootstrap_text
    assert "manualFollowUpSummary" in docs_bootstrap_text
    assert "wrapper now stays concise by default" in docs_bootstrap_text
    assert "--verbose-child-output" in docs_bootstrap_text
    assert "--no-write-latest-alias" in docs_bootstrap_text
    assert "--fail-on-not-ok" in docs_bootstrap_text
    assert "exit code `2`" in docs_bootstrap_text
    assert "PowerShell `>` redirect" in docs_bootstrap_text
    assert "UTF-16 JSON file" in docs_bootstrap_text
    assert "prefer saving both artifact flavors instead of relying on shell scrollback" in docs_bootstrap_text
    assert "markdown checklist and machine-readable payload stay paired" in docs_bootstrap_text
    assert "seeded labels, milestones, Discussions categories, seeded discussion-topic presence, seeded discussion-topic body alignment, and pinned-discussion presence" in docs_bootstrap_text
    assert "Project board seed targets" in bootstrap_script_text
    assert "Current GitHub auth account" in bootstrap_script_text
    assert "Current GitHub auth scopes" in bootstrap_script_text
    assert "Missing project auth scopes" in bootstrap_script_text
    assert 'copy-ready `gh api graphql --raw-field "query=..."` commands for the automatable `createDiscussion` / `updateDiscussion` portion' in open_source_doc_text
    assert "current GitHub auth login/token-source/scopes when detectable" in open_source_doc_text
    assert "gh auth refresh -h github.com -s read:project" in open_source_doc_text
    assert "scripts/generate_ancap_docs_live_followup.py" in status_matrix_text
    assert "tmp/ancap-docs-live-follow-up-YYYY-MM-DD.md" in status_matrix_text
    assert "tmp/ancap-docs-live-follow-up-YYYY-MM-DD.json" in status_matrix_text
    assert "tmp/ancap-docs-live-follow-up-latest.md" in status_matrix_text
    assert "tmp/ancap-docs-live-follow-up-latest.json" in status_matrix_text
    assert "refuses `--date-label latest` while alias writes stay enabled" in status_matrix_text
    assert "treats `--basename` and `--date-label` as filename components only" in status_matrix_text
    assert "artifactMetadata" in status_matrix_text
    assert "generator repo HEAD provenance" in status_matrix_text
    assert "Artifact metadata" in status_matrix_text
    assert "--fail-on-not-ok" in status_matrix_text
    assert "exit code `2`" in status_matrix_text
    assert "current GitHub auth login/token-source/scopes when detectable" in status_matrix_text
    assert "gh auth refresh -h github.com -s read:project" in status_matrix_text
    assert "keeps successful refreshes concise by default" in status_matrix_text
    assert "--verbose-child-output" in status_matrix_text
    assert "PowerShell `>` redirect" in status_matrix_text
    assert "UTF-16 JSON file with a BOM" in status_matrix_text
    assert "defaultStatusCheckContexts" in bootstrap_script_text
    assert "docsCI" in bootstrap_script_text
    assert "../.github/bootstrap/" in docs_repo_readme_text
    assert "../.github/bootstrap/README.md" in docs_repo_readme_text
    assert "PUBLIC_INTEGRATION_EXAMPLES.md" in docs_repo_readme_text
    assert "public-safe documentation landing page" in docs_repo_readme_text
    assert "- [~] Create public `ancap-docs`" in roadmap_text
