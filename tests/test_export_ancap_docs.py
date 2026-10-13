from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "export_ancap_docs.py"
EXPECTED_EXPORTS = {
    Path("README.md"),
    Path("LICENSE"),
    Path("CONTRIBUTING.md"),
    Path("SECURITY.md"),
    Path("CODE_OF_CONDUCT.md"),
    Path(".github/CODEOWNERS"),
    Path(".github/bootstrap/README.md"),
    Path(".github/bootstrap/ancap-docs-contributor-intake.json"),
    Path(".github/bootstrap/ancap-docs-dependabot.yml"),
    Path(".github/pull_request_template.md"),
    Path(".github/ISSUE_TEMPLATE/bug_report.md"),
    Path(".github/ISSUE_TEMPLATE/feature_request.md"),
    Path(".github/ISSUE_TEMPLATE/config.yml"),
    Path(".github/bootstrap/ancap-docs-labels.json"),
    Path(".github/bootstrap/ancap-docs-milestones.json"),
    Path(".github/bootstrap/ancap-docs-discussions.json"),
    Path(".github/bootstrap/ancap-docs-project-board.json"),
    Path(".github/bootstrap/ancap-docs-initial-issues.json"),
    Path(".github/bootstrap/ancap-docs-repo-settings.json"),
    Path(".github/bootstrap/ancap-docs-update-cadence.json"),
    Path(".github/bootstrap/ancap-docs-ci.json"),
    Path(".github/bootstrap/ancap-docs-ci-workflow.yml"),
    Path(".github/workflows/docs-ci.yml"),
    Path(".github/dependabot.yml"),
    Path("MASTER_ROADMAP.md"),
    Path("docs/STATUS_MATRIX.md"),
    Path("docs/OPEN_SOURCE_GITHUB_TRANSPARENCY.md"),
    Path("docs/ANCAP_DOCS_SPLIT.md"),
    Path("docs/ANCAP_DOCS_REPO_BOOTSTRAP.md"),
    Path("docs/ANCAP_DOCS_CONTRIBUTOR_INTAKE_SEED.md"),
    Path("docs/ANCAP_DOCS_LABEL_SEED.md"),
    Path("docs/ANCAP_DOCS_DISCUSSIONS_SEED.md"),
    Path("docs/ANCAP_DOCS_MILESTONE_SEED.md"),
    Path("docs/ANCAP_DOCS_PROJECT_BOARD_SEED.md"),
    Path("docs/ANCAP_DOCS_INITIAL_ISSUES_SEED.md"),
    Path("docs/ANCAP_DOCS_REPO_SETTINGS_SEED.md"),
    Path("docs/ANCAP_DOCS_UPDATE_CADENCE_SEED.md"),
    Path("docs/ANCAP_DOCS_CI_SEED.md"),
    Path("docs/ANCAP_DOCS_DEPENDABOT_SEED.md"),
    Path("docs/VISION.md"),
    Path("docs/ARCHITECTURE_LAYERS.md"),
    Path("docs/PLAN_L0_TO_L3.md"),
    Path("docs/REPUTATION_2.md"),
    Path("docs/STAKING.md"),
    Path("docs/WHITEPAPER_PROJECT.md"),
    Path("docs/WHITEPAPER_ACP.md"),
    Path("docs/LEGAL_TERMS_TEMPLATE.md"),
    Path("docs/BRIDGE_RISK_DOCUMENTATION.md"),
    Path("docs/OFFICIAL_CONTRACT_ADDRESSES.md"),
    Path("docs/CONTRACT_VERIFICATION_GUIDE.md"),
    Path("docs/TESTNET_DEPLOYMENT_GUIDE.md"),
    Path("docs/AUDIT_CHECKLIST.md"),
    Path("docs/CHANGELOG_PUBLIC.md"),
    Path("docs/PUBLIC_INTEGRATION_EXAMPLES.md"),
}

DOCS_REPO_README_SOURCE = Path("docs/ANCAP_DOCS_REPO_README.md")


def test_export_script_contains_split_plan_and_manifest_guardrails():
    script_text = SCRIPT_PATH.read_text(encoding="utf-8")

    assert 'Path("docs/ANCAP_DOCS_SPLIT.md")' in script_text
    assert 'Path("docs/ANCAP_DOCS_REPO_BOOTSTRAP.md")' in script_text
    assert 'Path("docs/ANCAP_DOCS_CONTRIBUTOR_INTAKE_SEED.md")' in script_text
    assert 'Path("docs/ANCAP_DOCS_LABEL_SEED.md")' in script_text
    assert 'Path("docs/ANCAP_DOCS_DISCUSSIONS_SEED.md")' in script_text
    assert 'Path("docs/ANCAP_DOCS_MILESTONE_SEED.md")' in script_text
    assert 'Path("docs/ANCAP_DOCS_PROJECT_BOARD_SEED.md")' in script_text
    assert 'Path("docs/ANCAP_DOCS_INITIAL_ISSUES_SEED.md")' in script_text
    assert 'Path("docs/ANCAP_DOCS_REPO_SETTINGS_SEED.md")' in script_text
    assert 'Path("docs/ANCAP_DOCS_UPDATE_CADENCE_SEED.md")' in script_text
    assert 'Path("docs/ANCAP_DOCS_CI_SEED.md")' in script_text
    assert 'Path("docs/ANCAP_DOCS_DEPENDABOT_SEED.md")' in script_text
    assert 'Path("docs/PUBLIC_INTEGRATION_EXAMPLES.md")' in script_text
    assert 'Path("docs/ANCAP_DOCS_REPO_README.md")' in script_text
    assert 'Path(".github/CODEOWNERS")' in script_text
    assert 'Path(".github/bootstrap/README.md")' in script_text
    assert 'Path(".github/bootstrap/ancap-docs-contributor-intake.json")' in script_text
    assert 'Path(".github/bootstrap/ancap-docs-dependabot.yml")' in script_text
    assert 'Path(".github/pull_request_template.md")' in script_text
    assert 'Path(".github/ISSUE_TEMPLATE/bug_report.md")' in script_text
    assert 'Path(".github/ISSUE_TEMPLATE/feature_request.md")' in script_text
    assert 'Path(".github/ISSUE_TEMPLATE/config.yml")' in script_text
    assert 'Path(".github/bootstrap/ancap-docs-labels.json")' in script_text
    assert 'Path(".github/bootstrap/ancap-docs-milestones.json")' in script_text
    assert 'Path(".github/bootstrap/ancap-docs-discussions.json")' in script_text
    assert 'Path(".github/bootstrap/ancap-docs-project-board.json")' in script_text
    assert 'Path(".github/bootstrap/ancap-docs-initial-issues.json")' in script_text
    assert 'Path(".github/bootstrap/ancap-docs-repo-settings.json")' in script_text
    assert 'Path(".github/bootstrap/ancap-docs-update-cadence.json")' in script_text
    assert 'Path(".github/bootstrap/ancap-docs-ci.json")' in script_text
    assert 'Path(".github/bootstrap/ancap-docs-ci-workflow.yml")' in script_text
    assert 'Path(".github/workflows/docs-ci.yml")' in script_text
    assert 'EXPORT_MANIFEST.md' in script_text
    assert 'issue/PR templates' in script_text
    assert 'contributor-intake seed for the future docs repo' in script_text
    assert 'docs-repo-specific Dependabot config' in script_text
    assert 'contributor-intake / label / milestone / Discussions / project-board / initial-issues / repo-settings / update-cadence / CI' in script_text
    assert 'baseline CODEOWNERS file' in script_text
    assert 'label seed for the future docs repo' in script_text
    assert 'initial Discussions category seed with copy-ready pinned-topic text' in script_text
    assert 'initial milestone seed' in script_text
    assert 'initial project-board seed' in script_text
    assert 'initial issue seed' in script_text
    assert 'initial repo-settings seed' in script_text
    assert 'initial public update-cadence seed with copy-ready update/release-note templates' in script_text
    assert 'initial Docs CI seed with a documented default required-check context' in script_text
    assert 'initial docs-repo Dependabot seed' in script_text
    assert 'matching bootstrap workflow template referenced by that CI seed' in script_text
    assert 'matching bootstrap Dependabot template for the exported `.github/dependabot.yml`' in script_text
    assert 'machine-readable label / milestone / Discussions / project-board / initial-issues / repo-settings / update-cadence / CI seeds' in script_text
    assert 'bootstrap-seed README' in script_text
    assert 'hot-wallet / bridge-signer internals' in script_text
    assert 'rewrite_markdown_links' in script_text
    assert 'find_unresolved_bundle_links' in script_text
    assert 'https://github.com/ancapcloud/ancap' in script_text
    assert 'EXPORT_SOURCE_TO_OUTPUT' in script_text


def test_export_script_creates_expected_public_docs_bundle(tmp_path: Path):
    target_dir = tmp_path / "ancap-docs-export"

    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--target", str(target_dir), "--clean"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr or result.stdout
    assert "Exported" in result.stdout

    for rel_path in EXPECTED_EXPORTS:
        exported_path = target_dir / rel_path
        assert exported_path.exists(), f"missing export: {rel_path}"

    manifest_path = target_dir / "EXPORT_MANIFEST.md"
    assert manifest_path.exists()
    manifest_text = manifest_path.read_text(encoding="utf-8")
    assert "future public `ancap-docs` repository" in manifest_text
    assert "issue/PR templates" in manifest_text
    assert "contributor-intake seed for the future docs repo" in manifest_text
    assert "contributor-intake / label / milestone / Discussions / project-board / initial-issues / repo-settings / update-cadence / CI" in manifest_text
    assert "baseline CODEOWNERS file" in manifest_text
    assert "label seed for the future docs repo" in manifest_text
    assert "initial Discussions category seed with copy-ready pinned-topic text" in manifest_text
    assert "initial milestone seed" in manifest_text
    assert "initial project-board seed" in manifest_text
    assert "initial issue seed" in manifest_text
    assert "initial repo-settings seed" in manifest_text
    assert "initial public update-cadence seed with copy-ready update/release-note templates" in manifest_text
    assert "initial Docs CI seed with a documented default required-check context" in manifest_text
    assert "initial docs-repo Dependabot seed" in manifest_text
    assert "matching bootstrap workflow template referenced by that CI seed" in manifest_text
    assert "matching bootstrap Dependabot template for the exported `.github/dependabot.yml`" in manifest_text
    assert "machine-readable label / milestone / Discussions / project-board / initial-issues / repo-settings / update-cadence / CI seeds" in manifest_text
    assert "runtime secrets" in manifest_text
    assert "infra/" in manifest_text
    assert "rewritten to the source monorepo on GitHub" in manifest_text
    assert "blob/master" in manifest_text
    for rel_path in EXPECTED_EXPORTS:
        assert rel_path.as_posix() in manifest_text


def test_export_bundle_rewrites_out_of_bundle_links_to_source_monorepo(tmp_path: Path):
    target_dir = tmp_path / "ancap-docs-export"

    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--target", str(target_dir), "--clean"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr or result.stdout

    readme_text = (target_dir / "README.md").read_text(encoding="utf-8")
    assert "future `ancap-docs` repository" in readme_text
    assert "https://github.com/ancapcloud/ancap/blob/master/examples/README.md" in readme_text
    assert "https://github.com/ancapcloud/ancap/blob/master/examples/payment-integration/python_credit_topup.py" in readme_text
    assert "https://github.com/ancapcloud/ancap/blob/master/contracts/bridge-bsc/README.md" in readme_text
    assert "[Status matrix](docs/STATUS_MATRIX.md)" in readme_text

    architecture_text = (target_dir / "docs" / "ARCHITECTURE_LAYERS.md").read_text(encoding="utf-8")
    assert "https://github.com/ancapcloud/ancap/blob/master/ROADMAP.md" in architecture_text
    assert "https://github.com/ancapcloud/ancap/blob/master/docs/rfc/service-catalog.md" in architecture_text


def test_export_bundle_has_no_broken_relative_markdown_links(tmp_path: Path):
    target_dir = tmp_path / "ancap-docs-export"

    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--target", str(target_dir), "--clean"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr or result.stdout

    sys.path.insert(0, str(REPO_ROOT))
    try:
        from scripts.export_ancap_docs import find_unresolved_bundle_links

        assert find_unresolved_bundle_links(target_dir) == []
    finally:
        sys.path.pop(0)


def test_export_bundle_includes_public_safe_github_templates_and_codeowners(tmp_path: Path):
    target_dir = tmp_path / "ancap-docs-export"

    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--target", str(target_dir), "--clean"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr or result.stdout

    codeowners = (target_dir / ".github" / "CODEOWNERS").read_text(encoding="utf-8")
    pr_template = (target_dir / ".github" / "pull_request_template.md").read_text(encoding="utf-8")
    bug_template = (target_dir / ".github" / "ISSUE_TEMPLATE" / "bug_report.md").read_text(encoding="utf-8")
    feature_template = (target_dir / ".github" / "ISSUE_TEMPLATE" / "feature_request.md").read_text(encoding="utf-8")
    config_template = (target_dir / ".github" / "ISSUE_TEMPLATE" / "config.yml").read_text(encoding="utf-8")

    assert "@ancapcloud" in codeowners
    assert "/docs/ @ancapcloud" in codeowners
    assert "No secrets or sensitive infra details added" in pr_template
    assert "Do **not** include secrets" in bug_template
    assert "Which area is affected?" in feature_template
    assert "Security issue" in config_template


def test_export_bundle_includes_repo_bootstrap_guide(tmp_path: Path):
    target_dir = tmp_path / "ancap-docs-export"

    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--target", str(target_dir), "--clean"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr or result.stdout

    bootstrap_text = (target_dir / "docs" / "ANCAP_DOCS_REPO_BOOTSTRAP.md").read_text(encoding="utf-8")
    assert "GitHub Discussions" in bootstrap_text
    assert "good first issue" in bootstrap_text
    assert "help wanted" in bootstrap_text
    assert "branch protection" in bootstrap_text
    assert "secret scanning and push protection" in bootstrap_text
    assert "ANCAP_DOCS_LABEL_SEED.md" in bootstrap_text
    assert "ANCAP_DOCS_DISCUSSIONS_SEED.md" in bootstrap_text
    assert ".github/bootstrap/ancap-docs-labels.json" in bootstrap_text
    assert ".github/bootstrap/ancap-docs-milestones.json" in bootstrap_text
    assert ".github/bootstrap/ancap-docs-discussions.json" in bootstrap_text
    assert ".github/bootstrap/ancap-docs-project-board.json" in bootstrap_text


def test_export_bundle_includes_contributor_intake_seed(tmp_path: Path):
    target_dir = tmp_path / "ancap-docs-export"

    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--target", str(target_dir), "--clean"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr or result.stdout

    contributor_seed_text = (target_dir / "docs" / "ANCAP_DOCS_CONTRIBUTOR_INTAKE_SEED.md").read_text(encoding="utf-8")
    contributor_seed_json = (target_dir / ".github" / "bootstrap" / "ancap-docs-contributor-intake.json").read_text(encoding="utf-8")
    assert "issue / PR intake lanes" in contributor_seed_text
    assert ".github/ISSUE_TEMPLATE/bug_report.md" in contributor_seed_text
    assert ".github/ISSUE_TEMPLATE/feature_request.md" in contributor_seed_text
    assert ".github/pull_request_template.md" in contributor_seed_text
    assert "security-report routing" in contributor_seed_text
    assert '"bugReport"' in contributor_seed_json
    assert '"featureRequest"' in contributor_seed_json
    assert '"pullRequestTemplate"' in contributor_seed_json
    assert '"scopeOptions"' in contributor_seed_json


def test_export_bundle_includes_label_seed(tmp_path: Path):
    target_dir = tmp_path / "ancap-docs-export"

    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--target", str(target_dir), "--clean"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr or result.stdout

    label_seed_text = (target_dir / "docs" / "ANCAP_DOCS_LABEL_SEED.md").read_text(encoding="utf-8")
    assert "good first issue" in label_seed_text
    assert "help wanted" in label_seed_text
    assert "docs" in label_seed_text
    assert "security" in label_seed_text
    assert "If GitHub Discussions is enabled" in label_seed_text


def test_export_bundle_includes_discussions_seed(tmp_path: Path):
    target_dir = tmp_path / "ancap-docs-export"

    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--target", str(target_dir), "--clean"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr or result.stdout

    discussions_seed_text = (target_dir / "docs" / "ANCAP_DOCS_DISCUSSIONS_SEED.md").read_text(encoding="utf-8")
    assert "Ideas" in discussions_seed_text
    assert "Q&A" in discussions_seed_text
    assert "Show and tell" in discussions_seed_text
    assert "Announcements" in discussions_seed_text
    assert "Suggested starter copy" in discussions_seed_text
    assert "# Welcome to ANCAP docs" in discussions_seed_text
    assert "Redirect security disclosures to `SECURITY.md`" in discussions_seed_text


def test_export_bundle_includes_milestone_seed(tmp_path: Path):
    target_dir = tmp_path / "ancap-docs-export"

    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--target", str(target_dir), "--clean"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr or result.stdout

    milestone_seed_text = (target_dir / "docs" / "ANCAP_DOCS_MILESTONE_SEED.md").read_text(encoding="utf-8")
    assert "Docs repo bootstrap" in milestone_seed_text
    assert "Trust and audit docs baseline" in milestone_seed_text
    assert "Roadmap and status sync" in milestone_seed_text
    assert "Integration docs and examples" in milestone_seed_text
    assert "Use milestone names consistently in release notes and monthly development updates" in milestone_seed_text


def test_export_bundle_includes_project_board_seed(tmp_path: Path):
    target_dir = tmp_path / "ancap-docs-export"

    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--target", str(target_dir), "--clean"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr or result.stdout

    project_board_seed_text = (target_dir / "docs" / "ANCAP_DOCS_PROJECT_BOARD_SEED.md").read_text(encoding="utf-8")
    assert "ANCAP Docs Roadmap" in project_board_seed_text
    assert "By milestone" in project_board_seed_text
    assert "good first issue" in project_board_seed_text
    assert "Milestone" in project_board_seed_text
    assert "keep the board public-facing and contributor-readable" in project_board_seed_text.lower()


def test_export_bundle_includes_update_cadence_seed(tmp_path: Path):
    target_dir = tmp_path / "ancap-docs-export"

    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--target", str(target_dir), "--clean"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr or result.stdout

    cadence_seed_text = (target_dir / "docs" / "ANCAP_DOCS_UPDATE_CADENCE_SEED.md").read_text(encoding="utf-8")
    assert "Monthly development update" in cadence_seed_text
    assert "Release notes" in cadence_seed_text
    assert "Trust-surface change notice" in cadence_seed_text
    assert "Suggested starter template" in cadence_seed_text
    assert "# Monthly development update — <month year>" in cadence_seed_text
    assert "Announcements" in cadence_seed_text


def test_export_bundle_includes_initial_issues_seed(tmp_path: Path):
    target_dir = tmp_path / "ancap-docs-export"

    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--target", str(target_dir), "--clean"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr or result.stdout

    initial_issues_seed_text = (target_dir / "docs" / "ANCAP_DOCS_INITIAL_ISSUES_SEED.md").read_text(encoding="utf-8")
    initial_issues_seed_json = (target_dir / ".github" / "bootstrap" / "ancap-docs-initial-issues.json").read_text(encoding="utf-8")
    assert "Align Discussions categories and pin seeded bootstrap topics" in initial_issues_seed_text
    assert "Publish official contract-address and verification index" in initial_issues_seed_text
    assert "Add public integration examples index and cross-links" in initial_issues_seed_text
    assert "Reconcile roadmap / status / changelog wording for the first monthly update" in initial_issues_seed_text
    assert "Docs repo bootstrap" in initial_issues_seed_text
    assert ".github/bootstrap/ancap-docs-initial-issues.json" in initial_issues_seed_text
    assert '"title": "Align Discussions categories and pin seeded bootstrap topics"' in initial_issues_seed_json
    assert '"milestone": "Trust and audit docs baseline"' in initial_issues_seed_json
    assert '"good first issue"' in initial_issues_seed_json
    assert '"Priority": "P2"' in initial_issues_seed_json


def test_export_bundle_includes_machine_readable_bootstrap_seeds(tmp_path: Path):
    target_dir = tmp_path / "ancap-docs-export"

    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--target", str(target_dir), "--clean"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr or result.stdout

    bootstrap_readme = (target_dir / ".github" / "bootstrap" / "README.md").read_text(encoding="utf-8")
    contributor_seed = (target_dir / ".github" / "bootstrap" / "ancap-docs-contributor-intake.json").read_text(encoding="utf-8")
    labels_seed = (target_dir / ".github" / "bootstrap" / "ancap-docs-labels.json").read_text(encoding="utf-8")
    milestones_seed = (target_dir / ".github" / "bootstrap" / "ancap-docs-milestones.json").read_text(encoding="utf-8")
    discussions_seed = (target_dir / ".github" / "bootstrap" / "ancap-docs-discussions.json").read_text(encoding="utf-8")
    project_board_seed = (target_dir / ".github" / "bootstrap" / "ancap-docs-project-board.json").read_text(encoding="utf-8")
    initial_issues_seed = (target_dir / ".github" / "bootstrap" / "ancap-docs-initial-issues.json").read_text(encoding="utf-8")
    update_cadence_seed = (target_dir / ".github" / "bootstrap" / "ancap-docs-update-cadence.json").read_text(encoding="utf-8")
    ci_seed = (target_dir / ".github" / "bootstrap" / "ancap-docs-ci.json").read_text(encoding="utf-8")
    dependabot_template = (target_dir / ".github" / "bootstrap" / "ancap-docs-dependabot.yml").read_text(encoding="utf-8")

    assert "machine-readable bootstrap metadata" in bootstrap_readme
    assert 'docs/ANCAP_DOCS_CONTRIBUTOR_INTAKE_SEED.md' in bootstrap_readme
    assert 'ancap-docs-contributor-intake.json' in bootstrap_readme
    assert '"bugReport"' in contributor_seed
    assert '"pullRequestTemplate"' in contributor_seed
    assert '"good first issue"' in labels_seed
    assert '"Docs repo bootstrap"' in milestones_seed
    assert '"Announcements"' in discussions_seed
    assert '"starterBody"' in discussions_seed
    assert '"ANCAP Docs Roadmap"' in project_board_seed
    assert '"Milestone"' in project_board_seed
    assert '"Publish official contract-address and verification index"' in initial_issues_seed
    assert '"labels": ["docs", "help wanted"]' in initial_issues_seed
    assert '"Monthly development update"' in update_cadence_seed
    assert '"starterTemplate"' in update_cadence_seed
    assert 'ancap-docs-ci.json' in bootstrap_readme
    assert 'docs/ANCAP_DOCS_CI_SEED.md' in bootstrap_readme
    assert 'docs/ANCAP_DOCS_INITIAL_ISSUES_SEED.md' in bootstrap_readme
    assert 'docs/ANCAP_DOCS_DEPENDABOT_SEED.md' in bootstrap_readme
    assert 'ancap-docs-initial-issues.json' in bootstrap_readme
    assert 'ancap-docs-dependabot.yml' in bootstrap_readme
    assert '"Docs CI / docs-bundle"' in ci_seed
    assert '"targetWorkflowPath": ".github/workflows/docs-ci.yml"' in ci_seed
    assert 'package-ecosystem: "github-actions"' in dependabot_template
    assert 'labels:' in dependabot_template


def test_export_bundle_includes_copy_ready_docs_ci_workflow(tmp_path: Path):
    target_dir = tmp_path / "ancap-docs-export"

    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--target", str(target_dir), "--clean"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr or result.stdout

    workflow_text = (target_dir / ".github" / "workflows" / "docs-ci.yml").read_text(encoding="utf-8")
    ci_seed_text = (target_dir / "docs" / "ANCAP_DOCS_CI_SEED.md").read_text(encoding="utf-8")

    assert 'name: "Docs CI"' in workflow_text
    assert 'docs-bundle:' in workflow_text
    assert 'ancap-docs-ci.json' in workflow_text
    assert 'ancap-docs-dependabot.yml' in workflow_text
    assert 'Docs repo Dependabot drift detected' in workflow_text
    assert 'GitHub Actions version-only bumps may differ' in workflow_text
    assert 'docs/ANCAP_DOCS_CI_SEED.md' in ci_seed_text
    assert 'Docs CI / docs-bundle' in ci_seed_text
    assert '.github/workflows/docs-ci.yml' in ci_seed_text
    assert '.github/bootstrap/ancap-docs-dependabot.yml' in ci_seed_text


def test_export_bundle_includes_docs_repo_dependabot_seed_and_export(tmp_path: Path):
    target_dir = tmp_path / "ancap-docs-export"

    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--target", str(target_dir), "--clean"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr or result.stdout

    dependabot_seed_text = (target_dir / "docs" / "ANCAP_DOCS_DEPENDABOT_SEED.md").read_text(encoding="utf-8")
    exported_dependabot_text = (target_dir / ".github" / "dependabot.yml").read_text(encoding="utf-8")
    bootstrap_dependabot_text = (target_dir / ".github" / "bootstrap" / "ancap-docs-dependabot.yml").read_text(encoding="utf-8")

    assert "future public `ancap-docs` repository" in dependabot_seed_text
    assert "docs-repo-specific `.github/dependabot.yml`" in dependabot_seed_text
    assert "package-ecosystem: \"github-actions\"" in dependabot_seed_text
    assert ".github/bootstrap/ancap-docs-dependabot.yml" in dependabot_seed_text
    assert 'package-ecosystem: "github-actions"' in exported_dependabot_text
    assert 'directory: "/"' in exported_dependabot_text
    assert 'open-pull-requests-limit: 5' in exported_dependabot_text
    assert '- "docs"' in exported_dependabot_text
    assert exported_dependabot_text == bootstrap_dependabot_text


def test_export_bundle_root_readme_comes_from_docs_repo_template(tmp_path: Path):
    target_dir = tmp_path / "ancap-docs-export"

    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--target", str(target_dir), "--clean"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr or result.stdout

    exported_readme = (target_dir / "README.md").read_text(encoding="utf-8")
    source_template = DOCS_REPO_README_SOURCE.read_text(encoding="utf-8")

    assert "This is the public-safe documentation landing page for the future `ancap-docs` repository." in source_template
    assert "This landing page is generated into the export bundle by `scripts/export_ancap_docs.py`" in source_template
    assert "This is the public-safe documentation landing page for the future `ancap-docs` repository." in exported_readme
    assert "The source monorepo still lives at:" in exported_readme
    assert "AI-Native Capital Allocation Platform" not in exported_readme
