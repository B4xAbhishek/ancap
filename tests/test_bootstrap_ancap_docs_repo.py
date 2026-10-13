from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "bootstrap_ancap_docs_repo.py"
README_PATH = REPO_ROOT / "README.md"
ROADMAP_PATH = REPO_ROOT / "MASTER_ROADMAP.md"
STATUS_MATRIX_PATH = REPO_ROOT / "docs" / "STATUS_MATRIX.md"
OPEN_SOURCE_DOC_PATH = REPO_ROOT / "docs" / "OPEN_SOURCE_GITHUB_TRANSPARENCY.md"
DOCS_SPLIT_PLAN_PATH = REPO_ROOT / "docs" / "ANCAP_DOCS_SPLIT.md"
DOCS_BOOTSTRAP_PATH = REPO_ROOT / "docs" / "ANCAP_DOCS_REPO_BOOTSTRAP.md"
LIVE_ANCAP_DOCS_VERIFY = os.environ.get("RUN_ANCAP_DOCS_LIVE_VERIFY") == "1"


def load_bootstrap_script_module():
    spec = importlib.util.spec_from_file_location("bootstrap_ancap_docs_repo", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_bootstrap_script_mentions_seed_files_and_gh_commands():
    script_text = SCRIPT_PATH.read_text(encoding="utf-8")

    assert '.github" / "bootstrap"' in script_text
    assert 'ancap-docs-labels.json' in script_text
    assert 'ancap-docs-milestones.json' in script_text
    assert 'ancap-docs-discussions.json' in script_text
    assert 'ancap-docs-project-board.json' in script_text
    assert 'ancap-docs-initial-issues.json' in script_text
    assert 'ancap-docs-repo-settings.json' in script_text
    assert 'ancap-docs-update-cadence.json' in script_text
    assert 'ancap-docs-ci.json' in script_text
    assert 'ancap-docs-ci-workflow.yml' in Path('.github/bootstrap/README.md').read_text(encoding='utf-8')
    assert 'gh",\n        "repo",\n        "create"' in script_text
    assert 'gh",\n        "repo",\n        "edit"' in script_text
    assert 'gh",\n        "issue",\n        "edit"' in script_text
    assert 'parse_issue_number_from_url' in script_text
    assert '--create-repo' in script_text
    assert '--create-repo requires --apply' in script_text
    assert '--create-repo cannot be combined with --apply-branch-protection' in script_text
    assert '"label"' in script_text
    assert '"create"' in script_text
    assert 'repos/{repo}/vulnerability-alerts' in script_text
    assert 'repos/{repo}/milestones' in script_text
    assert '--apply-branch-protection' in script_text
    assert '--status-check-context' in script_text
    assert '--verify-live' in script_text
    assert '--verify-live-community' in script_text
    assert '--output' in script_text
    assert 'Optional file path to also write the rendered output as UTF-8' in script_text
    assert '--verify-live-community requires --verify-live' in script_text
    assert '--verify-live cannot be combined with --apply' in script_text
    assert '--verify-live cannot be combined with --create-repo' in script_text
    assert 'status checks are intentionally deferred until the public docs repo has stable CI context names' in script_text
    assert 'Docs CI workflow' in script_text
    assert 'Docs CI status-check contexts' in script_text
    assert 'Discussions categories' in script_text
    assert 'Project board views' in script_text
    assert 'Update cadence' in script_text


def test_bootstrap_script_dry_run_renders_expected_plan():
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), '--repo', 'ancapcloud/ancap-docs'],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr or result.stdout
    output = result.stdout
    assert 'ANCAP docs bootstrap plan for ancapcloud/ancap-docs' in output
    assert 'gh repo create ancapcloud/ancap-docs --public' in output
    assert 'Create the repo empty so the exported docs bundle can become the first push without merge noise.' in output
    assert 'For the first public launch, the helper can run this create step with --apply --create-repo; do not combine that first-run creation step with branch-protection apply before the initial bundle push exists.' in output
    assert 'Enable GitHub Discussions immediately after creation so the seeded categories and pinned topics have a live home.' in output
    assert 'Enable GitHub Projects after creation before applying the project-board seed when the owner/account plan supports it.' in output
    assert 'gh repo edit ancapcloud/ancap-docs' in output
    assert 'gh api --method PUT repos/ancapcloud/ancap-docs/vulnerability-alerts' in output
    assert 'gh label create "good first issue" --repo ancapcloud/ancap-docs --color 7057ff' in output
    assert 'gh api --method POST repos/ancapcloud/ancap-docs/milestones -f "title=Docs repo bootstrap"' in output
    assert 'default branch: main' in output
    assert 'required approvals: 1' in output
    assert 'Discussions categories: Ideas, Q&A, Show and tell, Announcements' in output
    assert 'Project board: ANCAP Docs Roadmap' in output
    assert 'Docs CI workflow: Docs CI -> .github/workflows/docs-ci.yml' in output
    assert 'Docs CI jobs: docs-bundle' in output
    assert 'Docs CI status-check contexts: Docs CI / docs-bundle' in output
    assert 'Update cadence: Monthly development update, Release notes, Trust-surface change notice' in output
    assert 'status checks are intentionally deferred until the public docs repo has stable CI context names' in output
    assert 'Keep repo settings / labels / milestones / CI seed data aligned with the matching Markdown docs' in output


def test_bootstrap_script_json_output_renders_expected_snapshot():
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            '--repo',
            'ancapcloud/ancap-docs',
            '--apply-branch-protection',
            '--status-check-context',
            'Docs CI / docs-bundle',
            '--status-check-context',
            'Docs CI / docs-bundle',
            '--status-check-context',
            'link-check',
            '--format',
            'json',
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr or result.stdout
    payload = json.loads(result.stdout)
    assert payload['repo'] == 'ancapcloud/ancap-docs'
    assert payload['commands']['repoCreate'].startswith('gh repo create ancapcloud/ancap-docs --public')
    assert payload['repoCreateNotes'][0].startswith('Create the repo empty so the exported docs bundle can become the first push')
    assert 'For the first public launch, the helper can run this create step with --apply --create-repo; do not combine that first-run creation step with branch-protection apply before the initial bundle push exists.' in payload['repoCreateNotes']
    assert 'Enable GitHub Discussions immediately after creation so the seeded categories and pinned topics have a live home.' in payload['repoCreateNotes']
    assert 'Enable GitHub Projects after creation before applying the project-board seed when the owner/account plan supports it.' in payload['repoCreateNotes']
    assert payload['commands']['repoSettings'].startswith('gh repo edit ancapcloud/ancap-docs')
    assert payload['commands']['dependabotAlerts'] == 'gh api --method PUT repos/ancapcloud/ancap-docs/vulnerability-alerts'
    assert payload['commands']['branchProtection'].startswith(
        'gh api --method PUT -H "Accept: application/vnd.github+json" '
        'repos/ancapcloud/ancap-docs/branches/main/protection --input -'
    )
    assert payload['branchProtection']['statusCheckContexts'] == ['Docs CI / docs-bundle', 'link-check']
    assert payload['branchProtection']['payload']['required_status_checks']['contexts'] == ['Docs CI / docs-bundle', 'link-check']
    assert payload['branchProtection']['payload']['required_conversation_resolution'] is True
    assert payload['branchProtection']['payload']['allow_force_pushes'] is False
    assert payload['branchProtection']['payload']['allow_deletions'] is False
    assert payload['branchProtection']['payload']['block_creations'] is False
    assert payload['branchProtection']['payload']['required_linear_history'] is False
    assert payload['branchProtection']['payload']['lock_branch'] is False
    assert payload['branchProtection']['payload']['allow_fork_syncing'] is False
    assert payload['manualFollowUps']['projectBoard']['name'] == 'ANCAP Docs Roadmap'
    assert payload['manualFollowUps']['projectBoard']['views'] == ['Board', 'By milestone', 'Good first issues', 'Trust / audit docs']
    assert payload['manualFollowUps']['pinnedDiscussionTopics'] == [
        'Welcome / how to use this repo',
        'Where to ask what',
        'Public scope boundaries',
    ]
    assert payload['manualFollowUps']['discussionsAdminNotes'] == [
        'The gh/API helper currently verifies Discussions drift and could later automate missing-topic/body/category-reassignment follow-up via createDiscussion/updateDiscussion, but it does not apply those mutations today.',
        'The remaining live gaps still need GitHub UI or a future owner-capable path because the public gh/API surface does not expose full category-description/category-set/pinned-topic admin controls; use docs/ANCAP_DOCS_DISCUSSIONS_SEED.md and .github/bootstrap/ancap-docs-discussions.json as the copy-ready source of truth.',
    ]
    assert payload['manualFollowUps']['docsCI'] == {
        'workflowName': 'Docs CI',
        'targetWorkflowPath': '.github/workflows/docs-ci.yml',
        'jobs': ['docs-bundle'],
        'statusCheckContexts': ['Docs CI / docs-bundle'],
    }
    assert payload['manualFollowUps']['updateCadence'] == [
        'Monthly development update',
        'Release notes',
        'Trust-surface change notice',
    ]
    assert payload['manualFollowUps']['initialIssuesNote'] == (
        'Keep the seeded starter backlog explicit via the checked-in gh issue create commands; use them to open the first public queue on a fresh repo, or to recreate/reconcile issues later if live state drifts.'
    )
    assert payload['manualFollowUps']['initialIssues'] == [
        {
            'title': 'Align Discussions categories and pin seeded bootstrap topics',
            'milestone': 'Docs repo bootstrap',
            'labels': ['docs'],
            'boardFields': {'Status': 'Inbox', 'Area': 'docs', 'Priority': 'P1'},
            'command': 'gh issue create --repo ancapcloud/ancap-docs --title "Align Discussions categories and pin seeded bootstrap topics" --body "Remove or repurpose extra default Discussion categories if they still exist, update category descriptions to match the checked-in ANCAP seed, and pin the seeded bootstrap topics so the Discussions landing surface matches the documented baseline." --milestone "Docs repo bootstrap" --label docs',
            'expectedState': 'OPEN',
            'statusNote': 'This cleanup issue should stay open until the remaining live Discussions category-description drift, extra default categories, and unpinned seeded bootstrap topics are actually fixed in the public repo UI.',
        },
        {
            'title': 'Publish official contract-address and verification index',
            'milestone': 'Trust and audit docs baseline',
            'labels': ['docs', 'contracts', 'security', 'bridge'],
            'boardFields': {'Status': 'Inbox', 'Area': 'contracts', 'Priority': 'P1'},
            'command': 'gh issue create --repo ancapcloud/ancap-docs --title "Publish official contract-address and verification index" --body "Create one public-safe page that lists official ACP / wACP / bridge contract addresses and explorer links, cross-links contract-verification guidance and bridge-risk docs, and places explicit fake-contract warnings next to the official address list." --milestone "Trust and audit docs baseline" --label docs --label contracts --label security --label bridge',
            'expectedState': 'CLOSED',
            'statusNote': 'This seeded issue can stay closed because the public-safe contract-address and verification index is already live in the exported docs bundle and the matching live repo issue was completed.',
        },
        {
            'title': 'Add public integration examples index and cross-links',
            'milestone': 'Integration docs and examples',
            'labels': ['docs', 'sdk', 'good first issue'],
            'boardFields': {'Status': 'Inbox', 'Area': 'sdk', 'Priority': 'P2'},
            'command': 'gh issue create --repo ancapcloud/ancap-docs --title "Add public integration examples index and cross-links" --body "Add a contributor-friendly index page for payment, wallet, and bridge-facing public examples, then link those examples from docs-repo landing pages and integration docs so the first public integration backlog is easy to browse." --milestone "Integration docs and examples" --label docs --label sdk --label "good first issue"',
            'expectedState': 'CLOSED',
            'statusNote': 'This seeded issue can stay closed because the public integration examples index and the intended cross-links are already live in the exported docs bundle and the matching live repo issue was completed.',
        },
        {
            'title': 'Reconcile roadmap / status / changelog wording for the first monthly update',
            'milestone': 'Roadmap and status sync',
            'labels': ['docs', 'help wanted'],
            'boardFields': {'Status': 'Inbox', 'Area': 'docs', 'Priority': 'P2'},
            'command': 'gh issue create --repo ancapcloud/ancap-docs --title "Reconcile roadmap / status / changelog wording for the first monthly update" --body "Check that MASTER_ROADMAP.md, docs/STATUS_MATRIX.md, and docs/CHANGELOG_PUBLIC.md describe the same shipped truth, turn wording drift into explicit follow-up edits, and leave the first public monthly update with honest source documents." --milestone "Roadmap and status sync" --label docs --label "help wanted"',
            'expectedState': 'CLOSED',
            'statusNote': 'This seeded issue can stay closed because the roadmap / status / changelog wording slice is already aligned in the exported docs bundle and the matching live repo issue was completed.',
        },
    ]
    assert payload['manualFollowUps']['alignmentNote'].startswith('Keep repo settings / labels / milestones / CI seed data aligned')


def test_bootstrap_script_create_repo_apply_path_is_explicit_in_source():
    script_text = SCRIPT_PATH.read_text(encoding='utf-8')

    assert 'if args.create_repo:' in script_text
    assert 'run_command(build_repo_create_command(args.repo, plan["repo_settings"]), dry_run=False)' in script_text
    assert 'milestone_commands = ensure_milestones(args.repo, plan["milestones"], dry_run=True)' in script_text


@pytest.mark.skipif(
    not LIVE_ANCAP_DOCS_VERIFY,
    reason="live ancap-docs verification requires explicit opt-in auth and mutable external GitHub state",
)
def test_bootstrap_script_verifies_live_repo_state():
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            '--repo',
            'ancapcloud/ancap-docs',
            '--verify-live',
            '--format',
            'json',
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr or result.stdout
    payload = json.loads(result.stdout)
    assert payload['repo'] == 'ancapcloud/ancap-docs'
    assert payload['ok'] is True
    assert payload['driftCount'] == 0
    assert payload['unknownCount'] == 0
    assert payload['driftSummary'] == {
        'driftChecks': [],
        'unknownChecks': [],
        'driftCountByScope': {},
        'unknownCountByScope': {},
    }
    checks = {(item['scope'], item['field']): item for item in payload['checks']}
    assert checks[('repo', 'visibility')]['actual'] == 'public'
    assert checks[('repo', 'defaultBranch')]['actual'] == 'main'
    assert checks[('security', 'secretScanning')]['actual'] is True
    assert checks[('security', 'pushProtection')]['actual'] is True
    assert checks[('branchProtection', 'configured')]['actual'] is True
    assert checks[('branchProtection', 'requiredStatusChecks')]['actual'] == ['Docs CI / docs-bundle']
    assert checks[('branchProtection', 'requireCodeOwnerReview')]['actual'] is True


@pytest.mark.skipif(
    not LIVE_ANCAP_DOCS_VERIFY,
    reason="live ancap-docs verification requires explicit opt-in auth and mutable external GitHub state",
)
def test_bootstrap_script_verifies_live_repo_community_state():
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            '--repo',
            'ancapcloud/ancap-docs',
            '--verify-live',
            '--verify-live-community',
            '--format',
            'json',
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr or result.stdout
    payload = json.loads(result.stdout)
    assert payload['repo'] == 'ancapcloud/ancap-docs'
    assert payload['ok'] is False
    assert payload['unknownCount'] == 0
    assert payload['driftCount'] >= 1
    assert payload['driftSummary'] == {
        'driftChecks': [
            {'scope': 'discussionCategory', 'field': 'Ideas'},
            {'scope': 'discussionCategory', 'field': 'Q&A'},
            {'scope': 'discussionCategory', 'field': 'Show and tell'},
            {'scope': 'discussionCategory', 'field': 'Announcements'},
            {'scope': 'discussionCategory', 'field': 'categoryNames'},
            {'scope': 'pinnedDiscussionTopic', 'field': 'Welcome / how to use this repo'},
            {'scope': 'pinnedDiscussionTopic', 'field': 'Where to ask what'},
            {'scope': 'pinnedDiscussionTopic', 'field': 'Public scope boundaries'},
        ],
        'unknownChecks': [],
        'driftCountByScope': {
            'discussionCategory': 5,
            'pinnedDiscussionTopic': 3,
        },
        'unknownCountByScope': {},
    }
    checks = {(item['scope'], item['field']): item for item in payload['checks']}
    assert checks[('initialIssue', 'Align Discussions categories and pin seeded bootstrap topics')] == {
        'scope': 'initialIssue',
        'field': 'Align Discussions categories and pin seeded bootstrap topics',
        'expected': {
            'milestone': 'Docs repo bootstrap',
            'labels': ['docs'],
            'body': 'Remove or repurpose extra default Discussion categories if they still exist, update category descriptions to match the checked-in ANCAP seed, and pin the seeded bootstrap topics so the Discussions landing surface matches the documented baseline.',
            'state': 'OPEN',
        },
        'actual': {
            'milestone': 'Docs repo bootstrap',
            'labels': ['docs'],
            'body': 'Remove or repurpose extra default Discussion categories if they still exist, update category descriptions to match the checked-in ANCAP seed, and pin the seeded bootstrap topics so the Discussions landing surface matches the documented baseline.',
            'url': 'https://github.com/ancapcloud/ancap-docs/issues/5',
            'state': 'OPEN',
        },
        'status': 'match',
    }
    assert checks[('initialIssue', 'Publish official contract-address and verification index')] == {
        'scope': 'initialIssue',
        'field': 'Publish official contract-address and verification index',
        'expected': {
            'milestone': 'Trust and audit docs baseline',
            'labels': ['bridge', 'contracts', 'docs', 'security'],
            'body': 'Create one public-safe page that lists official ACP / wACP / bridge contract addresses and explorer links, cross-links contract-verification guidance and bridge-risk docs, and places explicit fake-contract warnings next to the official address list.',
            'state': 'CLOSED',
        },
        'actual': {
            'milestone': 'Trust and audit docs baseline',
            'labels': ['bridge', 'contracts', 'docs', 'security'],
            'body': 'Create one public-safe page that lists official ACP / wACP / bridge contract addresses and explorer links, cross-links contract-verification guidance and bridge-risk docs, and places explicit fake-contract warnings next to the official address list.',
            'url': 'https://github.com/ancapcloud/ancap-docs/issues/6',
            'state': 'CLOSED',
        },
        'status': 'match',
    }
    assert checks[('label', 'good first issue')]['actual'] == {
        'color': '7057ff',
        'description': 'Small, approachable tasks for new contributors',
    }
    assert checks[('milestone', 'Docs repo bootstrap')]['actual'] == {
        'description': 'First public repo push, governance file verification, issue/PR template verification, CODEOWNERS review-routing verification, and Discussions / labels / project-board setup.',
    }
    assert checks[('discussions', 'enabled')]['actual'] is True
    assert checks[('discussionCategory', 'Ideas')]['status'] == 'drift'
    assert checks[('discussionCategory', 'Ideas')]['actual'] == {
        'id': 'DIC_kwDOSq83QM4C-Dwi',
        'description': 'Share ideas for new features',
        'slug': 'ideas',
        'emojiHtml': '<div>💡</div>',
        'isAnswerable': False,
    }
    assert checks[('discussionCategory', 'Q&A')]['status'] == 'drift'
    assert checks[('discussionCategory', 'Q&A')]['actual'] == {
        'id': 'DIC_kwDOSq83QM4C-Dwh',
        'description': 'Ask the community for help',
        'slug': 'q-a',
        'emojiHtml': '<div>🙏</div>',
        'isAnswerable': True,
    }
    assert checks[('discussionCategory', 'Show and tell')]['status'] == 'drift'
    assert checks[('discussionCategory', 'Show and tell')]['actual'] == {
        'id': 'DIC_kwDOSq83QM4C-Dwj',
        'description': "Show off something you've made",
        'slug': 'show-and-tell',
        'emojiHtml': '<div>🙌</div>',
        'isAnswerable': False,
    }
    assert checks[('discussionCategory', 'Announcements')]['status'] == 'drift'
    assert checks[('discussionCategory', 'Announcements')]['actual'] == {
        'id': 'DIC_kwDOSq83QM4C-Dwf',
        'description': 'Updates from maintainers',
        'slug': 'announcements',
        'emojiHtml': '<div>📣</div>',
        'isAnswerable': False,
    }
    assert checks[('discussionCategory', 'categoryNames')]['status'] == 'drift'
    assert checks[('discussionCategory', 'categoryNames')]['actual'] == ['Announcements', 'General', 'Ideas', 'Polls', 'Q&A', 'Show and tell']
    assert checks[('discussionTopic', 'Welcome / how to use this repo')]['actual'] is True
    assert checks[('discussionTopicBody', 'Welcome / how to use this repo')]['status'] == 'match'
    assert checks[('discussionTopicBody', 'Welcome / how to use this repo')]['actual'] is True
    assert checks[('pinnedDiscussionTopic', 'Welcome / how to use this repo')]['status'] == 'drift'
    assert checks[('pinnedDiscussionTopic', 'Welcome / how to use this repo')]['actual'] is False
    assert checks[('discussionTopic', 'Where to ask what')]['actual'] is True
    assert checks[('discussionTopicBody', 'Where to ask what')]['status'] == 'match'
    assert checks[('discussionTopicBody', 'Where to ask what')]['actual'] is True
    assert checks[('pinnedDiscussionTopic', 'Where to ask what')]['status'] == 'drift'
    assert checks[('pinnedDiscussionTopic', 'Where to ask what')]['actual'] is False
    assert checks[('discussionTopic', 'Public scope boundaries')]['actual'] is True
    assert checks[('discussionTopicBody', 'Public scope boundaries')]['status'] == 'match'
    assert checks[('discussionTopicBody', 'Public scope boundaries')]['actual'] is True
    assert checks[('pinnedDiscussionTopic', 'Public scope boundaries')]['status'] == 'drift'
    assert checks[('pinnedDiscussionTopic', 'Public scope boundaries')]['actual'] is False
    assert payload['manualFollowUps']['initialIssuesNote'] == (
        'Keep the seeded starter backlog explicit via the checked-in gh issue create commands; use them to open the first public queue on a fresh repo, or to recreate/reconcile issues later if live state drifts.'
    )
    assert payload['manualFollowUps']['initialIssues'] == [
        {
            'title': 'Align Discussions categories and pin seeded bootstrap topics',
            'milestone': 'Docs repo bootstrap',
            'labels': ['docs'],
            'bodySummary': 'Remove or repurpose extra default Discussion categories if they still exist, update category descriptions to match the checked-in ANCAP seed, and pin the seeded bootstrap topics so the Discussions landing surface matches the documented baseline.',
            'boardFields': {'Status': 'Inbox', 'Area': 'docs', 'Priority': 'P1'},
            'command': 'gh issue create --repo ancapcloud/ancap-docs --title "Align Discussions categories and pin seeded bootstrap topics" --body "Remove or repurpose extra default Discussion categories if they still exist, update category descriptions to match the checked-in ANCAP seed, and pin the seeded bootstrap topics so the Discussions landing surface matches the documented baseline." --milestone "Docs repo bootstrap" --label docs',
            'exists': True,
            'url': 'https://github.com/ancapcloud/ancap-docs/issues/5',
            'actualMilestone': 'Docs repo bootstrap',
            'actualLabels': ['docs'],
            'actualBodySummary': 'Remove or repurpose extra default Discussion categories if they still exist, update category descriptions to match the checked-in ANCAP seed, and pin the seeded bootstrap topics so the Discussions landing surface matches the documented baseline.',
            'bodyMatchesSeed': True,
            'state': 'OPEN',
            'expectedState': 'OPEN',
            'stateMatchesSeed': True,
            'statusNote': 'This cleanup issue should stay open until the remaining live Discussions category-description drift, extra default categories, and unpinned seeded bootstrap topics are actually fixed in the public repo UI.',
        },
        {
            'title': 'Publish official contract-address and verification index',
            'milestone': 'Trust and audit docs baseline',
            'labels': ['docs', 'contracts', 'security', 'bridge'],
            'bodySummary': 'Create one public-safe page that lists official ACP / wACP / bridge contract addresses and explorer links, cross-links contract-verification guidance and bridge-risk docs, and places explicit fake-contract warnings next to the official address list.',
            'boardFields': {'Status': 'Inbox', 'Area': 'contracts', 'Priority': 'P1'},
            'command': 'gh issue create --repo ancapcloud/ancap-docs --title "Publish official contract-address and verification index" --body "Create one public-safe page that lists official ACP / wACP / bridge contract addresses and explorer links, cross-links contract-verification guidance and bridge-risk docs, and places explicit fake-contract warnings next to the official address list." --milestone "Trust and audit docs baseline" --label docs --label contracts --label security --label bridge',
            'exists': True,
            'url': 'https://github.com/ancapcloud/ancap-docs/issues/6',
            'actualMilestone': 'Trust and audit docs baseline',
            'actualLabels': ['bridge', 'contracts', 'docs', 'security'],
            'actualBodySummary': 'Create one public-safe page that lists official ACP / wACP / bridge contract addresses and explorer links, cross-links contract-verification guidance and bridge-risk docs, and places explicit fake-contract warnings next to the official address list.',
            'bodyMatchesSeed': True,
            'state': 'CLOSED',
            'expectedState': 'CLOSED',
            'stateMatchesSeed': True,
            'statusNote': 'This seeded issue can stay closed because the public-safe contract-address and verification index is already live in the exported docs bundle and the matching live repo issue was completed.',
        },
        {
            'title': 'Add public integration examples index and cross-links',
            'milestone': 'Integration docs and examples',
            'labels': ['docs', 'sdk', 'good first issue'],
            'bodySummary': 'Add a contributor-friendly index page for payment, wallet, and bridge-facing public examples, then link those examples from docs-repo landing pages and integration docs so the first public integration backlog is easy to browse.',
            'boardFields': {'Status': 'Inbox', 'Area': 'sdk', 'Priority': 'P2'},
            'command': 'gh issue create --repo ancapcloud/ancap-docs --title "Add public integration examples index and cross-links" --body "Add a contributor-friendly index page for payment, wallet, and bridge-facing public examples, then link those examples from docs-repo landing pages and integration docs so the first public integration backlog is easy to browse." --milestone "Integration docs and examples" --label docs --label sdk --label "good first issue"',
            'exists': True,
            'url': 'https://github.com/ancapcloud/ancap-docs/issues/7',
            'actualMilestone': 'Integration docs and examples',
            'actualLabels': ['docs', 'good first issue', 'sdk'],
            'actualBodySummary': 'Add a contributor-friendly index page for payment, wallet, and bridge-facing public examples, then link those examples from docs-repo landing pages and integration docs so the first public integration backlog is easy to browse.',
            'bodyMatchesSeed': True,
            'state': 'CLOSED',
            'expectedState': 'CLOSED',
            'stateMatchesSeed': True,
            'statusNote': 'This seeded issue can stay closed because the public integration examples index and the intended cross-links are already live in the exported docs bundle and the matching live repo issue was completed.',
        },
        {
            'title': 'Reconcile roadmap / status / changelog wording for the first monthly update',
            'milestone': 'Roadmap and status sync',
            'labels': ['docs', 'help wanted'],
            'bodySummary': 'Check that MASTER_ROADMAP.md, docs/STATUS_MATRIX.md, and docs/CHANGELOG_PUBLIC.md describe the same shipped truth, turn wording drift into explicit follow-up edits, and leave the first public monthly update with honest source documents.',
            'boardFields': {'Status': 'Inbox', 'Area': 'docs', 'Priority': 'P2'},
            'command': 'gh issue create --repo ancapcloud/ancap-docs --title "Reconcile roadmap / status / changelog wording for the first monthly update" --body "Check that MASTER_ROADMAP.md, docs/STATUS_MATRIX.md, and docs/CHANGELOG_PUBLIC.md describe the same shipped truth, turn wording drift into explicit follow-up edits, and leave the first public monthly update with honest source documents." --milestone "Roadmap and status sync" --label docs --label "help wanted"',
            'exists': True,
            'url': 'https://github.com/ancapcloud/ancap-docs/issues/8',
            'actualMilestone': 'Roadmap and status sync',
            'actualLabels': ['docs', 'help wanted'],
            'actualBodySummary': 'Check that MASTER_ROADMAP.md, docs/STATUS_MATRIX.md, and docs/CHANGELOG_PUBLIC.md describe the same shipped truth, turn wording drift into explicit follow-up edits, and leave the first public monthly update with honest source documents.',
            'bodyMatchesSeed': True,
            'state': 'CLOSED',
            'expectedState': 'CLOSED',
            'stateMatchesSeed': True,
            'statusNote': 'This seeded issue can stay closed because the roadmap / status / changelog wording slice is already aligned in the exported docs bundle and the matching live repo issue was completed.',
        },
    ]
    assert payload['manualFollowUps']['initialIssueActions'] == []
    assert payload['manualFollowUps']['discussionCategories']['missing'] == []
    assert payload['manualFollowUps']['discussionCategories']['unexpected'] == ['General', 'Polls']
    assert payload['manualFollowUps']['discussionUi'] == {
        'landingUrl': 'https://github.com/ancapcloud/ancap-docs/discussions',
        'expectedCategoryNames': ['Announcements', 'Ideas', 'Q&A', 'Show and tell'],
        'expectedCategoryDescriptions': [
            {
                'name': 'Announcements',
                'description': 'Docs repo milestone updates, release-note pointers, public roadmap/status updates, and transparency updates.',
            },
            {
                'name': 'Ideas',
                'description': 'Docs improvements, public transparency ideas, and future public-safe split ideas.',
            },
            {
                'name': 'Q&A',
                'description': 'Integration questions, docs clarification requests, contract verification questions, and bridge-risk trust-surface questions without private operator details.',
            },
            {
                'name': 'Show and tell',
                'description': 'Public integrations, example tooling, tutorials, walkthroughs, and public merchant/wallet/dev experiments.',
            },
        ],
    }
    assert payload['manualFollowUps']['discussionCleanupIssue'] == {
        'title': 'Align Discussions categories and pin seeded bootstrap topics',
        'url': 'https://github.com/ancapcloud/ancap-docs/issues/5',
        'exists': True,
        'state': 'OPEN',
        'milestone': 'Docs repo bootstrap',
        'labels': ['docs'],
    }
    assert payload['manualFollowUps']['discussionCategories']['descriptionDrift'] == [
        {
            'name': 'Announcements',
            'expectedDescription': 'Docs repo milestone updates, release-note pointers, public roadmap/status updates, and transparency updates.',
            'actualDescription': 'Updates from maintainers',
        },
        {
            'name': 'Ideas',
            'expectedDescription': 'Docs improvements, public transparency ideas, and future public-safe split ideas.',
            'actualDescription': 'Share ideas for new features',
        },
        {
            'name': 'Q&A',
            'expectedDescription': 'Integration questions, docs clarification requests, contract verification questions, and bridge-risk trust-surface questions without private operator details.',
            'actualDescription': 'Ask the community for help',
        },
        {
            'name': 'Show and tell',
            'expectedDescription': 'Public integrations, example tooling, tutorials, walkthroughs, and public merchant/wallet/dev experiments.',
            'actualDescription': "Show off something you've made",
        },
    ]
    discussion_topics = payload['manualFollowUps']['discussionTopics']
    assert [item['title'] for item in discussion_topics] == [
        'Welcome / how to use this repo',
        'Where to ask what',
        'Public scope boundaries',
    ]
    assert [item['url'] for item in discussion_topics] == [
        'https://github.com/ancapcloud/ancap-docs/discussions/2',
        'https://github.com/ancapcloud/ancap-docs/discussions/3',
        'https://github.com/ancapcloud/ancap-docs/discussions/4',
    ]
    discussion_ids = [item['discussionId'] for item in discussion_topics]
    assert len(set(discussion_ids)) == 3
    assert all(isinstance(value, str) and value.startswith('D_') for value in discussion_ids)
    assert all(item['expectedBody'].startswith('# ') for item in discussion_topics)
    assert all(item['categoryId'] == 'DIC_kwDOSq83QM4C-Dwf' for item in discussion_topics)
    assert all(item['categorySlug'] == 'announcements' for item in discussion_topics)
    assert all(item['categoryName'] == 'Announcements' for item in discussion_topics)
    assert all(item['categoryDescription'] == 'Updates from maintainers' for item in discussion_topics)
    assert all(item['expectedCategoryName'] == 'Announcements' for item in discussion_topics)
    assert all(item['expectedPinned'] is True for item in discussion_topics)
    assert all(item['actualPinned'] is False for item in discussion_topics)
    assert all(item['bodyMatchesSeed'] is True for item in discussion_topics)
    discussion_admin_actions = payload['manualFollowUps']['discussionAdminActions']
    assert [item['kind'] for item in discussion_admin_actions] == [
        'removeUnexpectedCategory',
        'removeUnexpectedCategory',
        'updateCategoryDescription',
        'updateCategoryDescription',
        'updateCategoryDescription',
        'updateCategoryDescription',
        'pinDiscussionTopic',
        'pinDiscussionTopic',
        'pinDiscussionTopic',
    ]
    assert discussion_admin_actions[0]['categoryName'] == 'General'
    assert isinstance(discussion_admin_actions[0]['actualDescription'], str) and discussion_admin_actions[0]['actualDescription']
    assert discussion_admin_actions[0]['instruction'] == 'Remove or repurpose this extra live Discussions category in the GitHub UI so the category set matches the checked-in seed.'
    assert discussion_admin_actions[1]['kind'] == 'removeUnexpectedCategory'
    assert discussion_admin_actions[1]['categoryName'] == 'Polls'
    assert isinstance(discussion_admin_actions[1]['actualDescription'], str) and discussion_admin_actions[1]['actualDescription']
    assert discussion_admin_actions[1]['instruction'] == 'Remove or repurpose this extra live Discussions category in the GitHub UI so the category set matches the checked-in seed.'
    assert discussion_admin_actions[2] == {
        'kind': 'updateCategoryDescription',
        'categoryName': 'Announcements',
        'expectedDescription': 'Docs repo milestone updates, release-note pointers, public roadmap/status updates, and transparency updates.',
        'actualDescription': 'Updates from maintainers',
        'instruction': 'Update the live Discussions category description in the GitHub UI so it matches the checked-in seed.',
    }
    assert discussion_admin_actions[3] == {
        'kind': 'updateCategoryDescription',
        'categoryName': 'Ideas',
        'expectedDescription': 'Docs improvements, public transparency ideas, and future public-safe split ideas.',
        'actualDescription': 'Share ideas for new features',
        'instruction': 'Update the live Discussions category description in the GitHub UI so it matches the checked-in seed.',
    }
    assert discussion_admin_actions[4] == {
        'kind': 'updateCategoryDescription',
        'categoryName': 'Q&A',
        'expectedDescription': 'Integration questions, docs clarification requests, contract verification questions, and bridge-risk trust-surface questions without private operator details.',
        'actualDescription': 'Ask the community for help',
        'instruction': 'Update the live Discussions category description in the GitHub UI so it matches the checked-in seed.',
    }
    assert discussion_admin_actions[5] == {
        'kind': 'updateCategoryDescription',
        'categoryName': 'Show and tell',
        'expectedDescription': 'Public integrations, example tooling, tutorials, walkthroughs, and public merchant/wallet/dev experiments.',
        'actualDescription': "Show off something you've made",
        'instruction': 'Update the live Discussions category description in the GitHub UI so it matches the checked-in seed.',
    }
    assert discussion_admin_actions[6:] == [
        {
            'kind': 'pinDiscussionTopic',
            'title': 'Welcome / how to use this repo',
            'url': 'https://github.com/ancapcloud/ancap-docs/discussions/2',
            'instruction': 'Pin this already-seeded bootstrap discussion in the GitHub UI so the live Discussions landing surface matches the checked-in seed.',
        },
        {
            'kind': 'pinDiscussionTopic',
            'title': 'Where to ask what',
            'url': 'https://github.com/ancapcloud/ancap-docs/discussions/3',
            'instruction': 'Pin this already-seeded bootstrap discussion in the GitHub UI so the live Discussions landing surface matches the checked-in seed.',
        },
        {
            'kind': 'pinDiscussionTopic',
            'title': 'Public scope boundaries',
            'url': 'https://github.com/ancapcloud/ancap-docs/discussions/4',
            'instruction': 'Pin this already-seeded bootstrap discussion in the GitHub UI so the live Discussions landing surface matches the checked-in seed.',
        },
    ]
    assert payload['manualFollowUps']['discussionAdminActionAutomation'] == [
        {
            'kind': 'removeUnexpectedCategory',
            'target': 'General',
            'status': 'manual_only',
            'mutation': None,
            'reason': "GitHub's public gh/API surface does not expose Discussion category removal admin mutations.",
        },
        {
            'kind': 'removeUnexpectedCategory',
            'target': 'Polls',
            'status': 'manual_only',
            'mutation': None,
            'reason': "GitHub's public gh/API surface does not expose Discussion category removal admin mutations.",
        },
        {
            'kind': 'updateCategoryDescription',
            'target': 'Announcements',
            'status': 'manual_only',
            'mutation': None,
            'reason': "GitHub's public gh/API surface does not expose Discussion category description mutations.",
        },
        {
            'kind': 'updateCategoryDescription',
            'target': 'Ideas',
            'status': 'manual_only',
            'mutation': None,
            'reason': "GitHub's public gh/API surface does not expose Discussion category description mutations.",
        },
        {
            'kind': 'updateCategoryDescription',
            'target': 'Q&A',
            'status': 'manual_only',
            'mutation': None,
            'reason': "GitHub's public gh/API surface does not expose Discussion category description mutations.",
        },
        {
            'kind': 'updateCategoryDescription',
            'target': 'Show and tell',
            'status': 'manual_only',
            'mutation': None,
            'reason': "GitHub's public gh/API surface does not expose Discussion category description mutations.",
        },
        {
            'kind': 'pinDiscussionTopic',
            'target': 'Welcome / how to use this repo',
            'status': 'manual_only',
            'mutation': None,
            'reason': "GitHub's public gh/API surface does not expose discussion pin/unpin admin mutations.",
        },
        {
            'kind': 'pinDiscussionTopic',
            'target': 'Where to ask what',
            'status': 'manual_only',
            'mutation': None,
            'reason': "GitHub's public gh/API surface does not expose discussion pin/unpin admin mutations.",
        },
        {
            'kind': 'pinDiscussionTopic',
            'target': 'Public scope boundaries',
            'status': 'manual_only',
            'mutation': None,
            'reason': "GitHub's public gh/API surface does not expose discussion pin/unpin admin mutations.",
        },
    ]
    assert all('command' not in item for item in payload['manualFollowUps']['discussionAdminActionAutomation'])
    assert payload['manualFollowUps']['projectBoard'] == {
        'ownerLogin': 'ancapcloud',
        'projectsQueryable': False,
        'missingReadProjectScope': True,
        'error': 'Current token lacks read:project scope, so live GitHub Projects board verification is blocked.',
        'authRefreshCommand': 'gh auth refresh -h github.com -s read:project',
        'currentAuth': {
            'host': 'github.com',
            'login': 'ancapcloud',
            'tokenSource': 'keyring',
            'scopes': ['gist', 'read:org', 'repo', 'workflow'],
            'missingScopes': ['read:project'],
        },
        'name': 'ANCAP Docs Roadmap',
        'scope': 'Public-safe docs work only; no private infra, signer, secret-handling, or operator-only tasks.',
        'fields': [
            {
                'name': 'Status',
                'kind': 'single_select',
                'options': ['Inbox', 'Ready', 'In progress', 'Review', 'Done'],
                'source': None,
            },
            {
                'name': 'Area',
                'kind': 'single_select',
                'options': ['docs', 'security', 'bridge', 'wallet', 'sdk', 'contracts', 'frontend'],
                'source': None,
            },
            {
                'name': 'Milestone',
                'kind': 'linked_seed',
                'options': None,
                'source': 'docs/ANCAP_DOCS_MILESTONE_SEED.md',
            },
            {
                'name': 'Priority',
                'kind': 'single_select',
                'options': ['P1', 'P2', 'P3'],
                'source': None,
            },
        ],
        'views': [
            {
                'name': 'Board',
                'layout': 'board',
                'groupBy': 'Status',
                'filters': None,
            },
            {
                'name': 'By milestone',
                'layout': 'table',
                'groupBy': 'Milestone',
                'filters': None,
            },
            {
                'name': 'Good first issues',
                'layout': 'board',
                'groupBy': None,
                'filters': ['label:good first issue', 'status!=Done'],
            },
            {
                'name': 'Trust / audit docs',
                'layout': 'board',
                'groupBy': None,
                'filters': ['area:security|bridge', 'status!=Done'],
            },
        ],
        'notes': [
            'Create the board after labels, milestones, and Discussions are enabled.',
            'Keep the board public-facing and contributor-readable.',
            'Do not mirror private operator execution work into this board.',
        ],
        'projectNumberPlaceholder': '<project-number>',
        'commands': {
            'create': 'gh project create --owner ancapcloud --title "ANCAP Docs Roadmap" --format json',
            'editDescription': 'gh project edit <project-number> --owner ancapcloud --description "Public-safe docs work only; no private infra, signer, secret-handling, or operator-only tasks."',
            'linkRepo': 'gh project link <project-number> --owner ancapcloud --repo ancapcloud/ancap-docs',
        },
        'fieldCommands': [
            {
                'name': 'Status',
                'kind': 'single_select',
                'command': 'gh project field-create <project-number> --owner ancapcloud --name Status --data-type SINGLE_SELECT --single-select-options "Inbox,Ready,In progress,Review,Done"',
                'source': None,
            },
            {
                'name': 'Area',
                'kind': 'single_select',
                'command': 'gh project field-create <project-number> --owner ancapcloud --name Area --data-type SINGLE_SELECT --single-select-options docs,security,bridge,wallet,sdk,contracts,frontend',
                'source': None,
            },
            {
                'name': 'Milestone',
                'kind': 'linked_seed',
                'command': None,
                'source': 'docs/ANCAP_DOCS_MILESTONE_SEED.md',
            },
            {
                'name': 'Priority',
                'kind': 'single_select',
                'command': 'gh project field-create <project-number> --owner ancapcloud --name Priority --data-type SINGLE_SELECT --single-select-options P1,P2,P3',
                'source': None,
            },
        ],
        'manualSteps': [
            'Use repository issue milestones from docs/ANCAP_DOCS_MILESTONE_SEED.md as the board milestone dimension for `Milestone`; gh project field-create does not create linked-seed milestone fields.',
            'Create the seeded project views in the GitHub UI after the fields exist; gh project CLI does not currently expose view creation.',
        ],
        'starterIssueBoarding': {
            'projectIdPlaceholder': '<project-id>',
            'itemIdPlaceholder': '<item-id>',
            'lookupCommands': {
                'view': 'gh project view <project-number> --owner ancapcloud --format json',
                'fieldList': 'gh project field-list <project-number> --owner ancapcloud --format json',
            },
            'notes': [
                'Run the project item-add command with --format json and capture the returned item id before applying field values.',
                'Run the project view command with --format json to capture the stable project id needed by gh project item-edit.',
                'Run the field-list command with --format json to map field ids and single-select option ids before applying the item-edit commands.',
                'The seeded starter issues already carry milestone routing via gh issue create, so the linked milestone board dimension should follow the issue milestone automatically once the issue is added.',
                'Use the live issue URL when one is already known; otherwise replace <issue-url> after creating the seeded starter issue.',
            ],
            'items': [
                {
                    'title': 'Align Discussions categories and pin seeded bootstrap topics',
                    'milestone': 'Docs repo bootstrap',
                    'issueUrl': 'https://github.com/ancapcloud/ancap-docs/issues/5',
                    'issueUrlPlaceholder': False,
                    'addCommand': 'gh project item-add <project-number> --owner ancapcloud --url https://github.com/ancapcloud/ancap-docs/issues/5 --format json',
                    'fieldAssignments': [
                        {
                            'field': 'Status',
                            'kind': 'single_select',
                            'value': 'Inbox',
                            'command': 'gh project item-edit --id <item-id> --project-id <project-id> --field-id <status-field-id> --single-select-option-id <status-inbox-option-id>',
                        },
                        {
                            'field': 'Area',
                            'kind': 'single_select',
                            'value': 'docs',
                            'command': 'gh project item-edit --id <item-id> --project-id <project-id> --field-id <area-field-id> --single-select-option-id <area-docs-option-id>',
                        },
                        {
                            'field': 'Priority',
                            'kind': 'single_select',
                            'value': 'P1',
                            'command': 'gh project item-edit --id <item-id> --project-id <project-id> --field-id <priority-field-id> --single-select-option-id <priority-p1-option-id>',
                        },
                    ],
                },
                {
                    'title': 'Publish official contract-address and verification index',
                    'milestone': 'Trust and audit docs baseline',
                    'issueUrl': 'https://github.com/ancapcloud/ancap-docs/issues/6',
                    'issueUrlPlaceholder': False,
                    'addCommand': 'gh project item-add <project-number> --owner ancapcloud --url https://github.com/ancapcloud/ancap-docs/issues/6 --format json',
                    'fieldAssignments': [
                        {
                            'field': 'Status',
                            'kind': 'single_select',
                            'value': 'Inbox',
                            'command': 'gh project item-edit --id <item-id> --project-id <project-id> --field-id <status-field-id> --single-select-option-id <status-inbox-option-id>',
                        },
                        {
                            'field': 'Area',
                            'kind': 'single_select',
                            'value': 'contracts',
                            'command': 'gh project item-edit --id <item-id> --project-id <project-id> --field-id <area-field-id> --single-select-option-id <area-contracts-option-id>',
                        },
                        {
                            'field': 'Priority',
                            'kind': 'single_select',
                            'value': 'P1',
                            'command': 'gh project item-edit --id <item-id> --project-id <project-id> --field-id <priority-field-id> --single-select-option-id <priority-p1-option-id>',
                        },
                    ],
                },
                {
                    'title': 'Add public integration examples index and cross-links',
                    'milestone': 'Integration docs and examples',
                    'issueUrl': 'https://github.com/ancapcloud/ancap-docs/issues/7',
                    'issueUrlPlaceholder': False,
                    'addCommand': 'gh project item-add <project-number> --owner ancapcloud --url https://github.com/ancapcloud/ancap-docs/issues/7 --format json',
                    'fieldAssignments': [
                        {
                            'field': 'Status',
                            'kind': 'single_select',
                            'value': 'Inbox',
                            'command': 'gh project item-edit --id <item-id> --project-id <project-id> --field-id <status-field-id> --single-select-option-id <status-inbox-option-id>',
                        },
                        {
                            'field': 'Area',
                            'kind': 'single_select',
                            'value': 'sdk',
                            'command': 'gh project item-edit --id <item-id> --project-id <project-id> --field-id <area-field-id> --single-select-option-id <area-sdk-option-id>',
                        },
                        {
                            'field': 'Priority',
                            'kind': 'single_select',
                            'value': 'P2',
                            'command': 'gh project item-edit --id <item-id> --project-id <project-id> --field-id <priority-field-id> --single-select-option-id <priority-p2-option-id>',
                        },
                    ],
                },
                {
                    'title': 'Reconcile roadmap / status / changelog wording for the first monthly update',
                    'milestone': 'Roadmap and status sync',
                    'issueUrl': 'https://github.com/ancapcloud/ancap-docs/issues/8',
                    'issueUrlPlaceholder': False,
                    'addCommand': 'gh project item-add <project-number> --owner ancapcloud --url https://github.com/ancapcloud/ancap-docs/issues/8 --format json',
                    'fieldAssignments': [
                        {
                            'field': 'Status',
                            'kind': 'single_select',
                            'value': 'Inbox',
                            'command': 'gh project item-edit --id <item-id> --project-id <project-id> --field-id <status-field-id> --single-select-option-id <status-inbox-option-id>',
                        },
                        {
                            'field': 'Area',
                            'kind': 'single_select',
                            'value': 'docs',
                            'command': 'gh project item-edit --id <item-id> --project-id <project-id> --field-id <area-field-id> --single-select-option-id <area-docs-option-id>',
                        },
                        {
                            'field': 'Priority',
                            'kind': 'single_select',
                            'value': 'P2',
                            'command': 'gh project item-edit --id <item-id> --project-id <project-id> --field-id <priority-field-id> --single-select-option-id <priority-p2-option-id>',
                        },
                    ],
                },
            ],
        },
    }
    assert payload['manualFollowUps']['projectBoardActions'] == [
        {
            'kind': 'requestProjectScope',
            'instruction': 'Refresh GitHub auth with read:project scope (or switch to owner-capable project auth) before trying live project-board seeding or verification again.',
            'command': 'gh auth refresh -h github.com -s read:project',
        },
        {
            'kind': 'seedProjectBoard',
            'boardName': 'ANCAP Docs Roadmap',
            'instruction': 'Seed or verify the public docs project board from docs/ANCAP_DOCS_PROJECT_BOARD_SEED.md and .github/bootstrap/ancap-docs-project-board.json once project-capable auth exists.',
        },
    ]
    assert payload['manualFollowUpSummary'] == {
        'initialIssueActions': {
            'count': 0,
            'byKind': {},
        },
        'discussionAdminActions': {
            'count': 9,
            'byKind': {
                'removeUnexpectedCategory': 2,
                'updateCategoryDescription': 4,
                'pinDiscussionTopic': 3,
            },
        },
        'projectBoardActions': {
            'count': 2,
            'byKind': {
                'requestProjectScope': 1,
                'seedProjectBoard': 1,
            },
        },
    }
    assert 'community verification mode also checks seeded labels, milestones, initial issue backlog presence/routing, Discussions category state, seeded discussion-topic presence, seeded discussion-topic body alignment, and pinned-discussion presence.' in payload['notes']
    assert 'GitHub Projects boards still require owner-capability follow-up beyond this helper\'s live checks.' in payload['notes']
    assert any('This helper currently verifies Discussions category drift, seeded discussion-topic category/body drift, and pinned-topic presence. GitHub\'s public GraphQL surface does expose createDiscussion/updateDiscussion for future missing-topic, topic-body, or category-reassignment follow-up, but this helper does not apply those mutations today.' in note for note in payload['notes'])
    assert any('The remaining live seeded-surface gaps still need GitHub UI or a future owner-capable automation path because the public gh/API path does not expose a complete category lifecycle/description or discussion-pinning admin flow' in note for note in payload['notes'])
    assert any('live GitHub Projects board verification for ancapcloud is currently blocked because the active token lacks read:project scope' in note for note in payload['notes'])


@pytest.mark.skipif(
    not LIVE_ANCAP_DOCS_VERIFY,
    reason="live ancap-docs verification requires explicit opt-in auth and mutable external GitHub state",
)
def test_bootstrap_script_markdown_output_renders_operator_checklist_for_live_repo_state():
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            '--repo',
            'ancapcloud/ancap-docs',
            '--verify-live',
            '--verify-live-community',
            '--format',
            'markdown',
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr or result.stdout
    output = result.stdout
    assert '# ANCAP docs live follow-up checklist for ancapcloud/ancap-docs' in output
    assert '## Drift summary' in output
    assert '## Initial issue backlog targets' in output
    assert '## Initial issue backlog checklist' not in output
    assert '- [`Align Discussions categories and pin seeded bootstrap topics`](https://github.com/ancapcloud/ancap-docs/issues/5) -> exists `True`, state `OPEN`, milestone `Docs repo bootstrap`, labels `docs`, body matches seed `True`, expected state `OPEN`, state matches seed `True`, board fields `{"Status": "Inbox", "Area": "docs", "Priority": "P1"}`' in output
    assert '  - status note: This cleanup issue should stay open until the remaining live Discussions category-description drift, extra default categories, and unpinned seeded bootstrap topics are actually fixed in the public repo UI.' in output
    assert '- [`Publish official contract-address and verification index`](https://github.com/ancapcloud/ancap-docs/issues/6) -> exists `True`, state `CLOSED`, milestone `Trust and audit docs baseline`, labels `docs, contracts, security, bridge`, body matches seed `True`, expected state `CLOSED`, state matches seed `True`, board fields `{"Status": "Inbox", "Area": "contracts", "Priority": "P1"}`' in output
    assert 'gh issue create --repo ancapcloud/ancap-docs --title "Add public integration examples index and cross-links"' in output
    assert 'seed command:' in output
    assert '## Discussion UI targets' in output
    assert '- Discussions landing page: https://github.com/ancapcloud/ancap-docs/discussions' in output
    assert '- Tracked cleanup issue: [`Align Discussions categories and pin seeded bootstrap topics`](https://github.com/ancapcloud/ancap-docs/issues/5) -> state `OPEN`, milestone `Docs repo bootstrap`, labels `docs`' in output
    assert '- Keep only seeded categories: `Announcements`, `Ideas`, `Q&A`, `Show and tell`' in output
    assert '  - `Announcements` -> `Docs repo milestone updates, release-note pointers, public roadmap/status updates, and transparency updates.`' in output
    assert 'unexpected live Discussion categories' not in output
    assert '- [ ] Remove or repurpose extra Discussion category `General`' in output
    assert '- [ ] Remove or repurpose extra Discussion category `Polls`' in output
    assert '- [ ] Update Discussion category `Announcements` description from `Updates from maintainers` to `Docs repo milestone updates, release-note pointers, public roadmap/status updates, and transparency updates.`.' in output
    assert '- [ ] Pin seeded bootstrap discussion [`Welcome / how to use this repo`](https://github.com/ancapcloud/ancap-docs/discussions/2).' in output
    assert '- [ ] Refresh GitHub auth with `read:project` scope (or switch to owner-capable project auth).' in output
    assert '  - command: `gh auth refresh -h github.com -s read:project`' in output
    assert '## Seeded discussion topics' in output
    assert '[`Where to ask what`](https://github.com/ancapcloud/ancap-docs/discussions/3)' in output
    assert 'expected category `Announcements`' in output
    assert 'body matches seed `True`' in output
    assert '## Discussions automation map' in output
    assert '- `removeUnexpectedCategory` / `General` -> `manual_only`' in output
    assert '  - reason: GitHub\'s public gh/API surface does not expose Discussion category removal admin mutations.' in output
    assert '- `pinDiscussionTopic` / `Welcome / how to use this repo` -> `manual_only`' in output
    assert '  - reason: GitHub\'s public gh/API surface does not expose discussion pin/unpin admin mutations.' in output
    assert '  - command: `gh api graphql --raw-field "query=' not in output
    assert '## Project board seed targets' in output
    assert '- Board name: `ANCAP Docs Roadmap`' in output
    assert '- Scope: `Public-safe docs work only; no private infra, signer, secret-handling, or operator-only tasks.`' in output
    assert '- Live verification status: `Current token lacks read:project scope, so live GitHub Projects board verification is blocked.`' in output
    assert '- Current GitHub auth account: `ancapcloud` via `keyring`' in output
    assert '- Current GitHub auth scopes: `gist`, `read:org`, `repo`, `workflow`' in output
    assert '- Missing project auth scopes: `read:project`' in output
    assert '- Auth refresh command: `gh auth refresh -h github.com -s read:project`' in output
    assert '- Seeded commands:' in output
    assert '  - Create command: `gh project create --owner ancapcloud --title "ANCAP Docs Roadmap" --format json`' in output
    assert '  - Description command: `gh project edit <project-number> --owner ancapcloud --description "Public-safe docs work only; no private infra, signer, secret-handling, or operator-only tasks."`' in output
    assert '  - Repo link command: `gh project link <project-number> --owner ancapcloud --repo ancapcloud/ancap-docs`' in output
    assert '  - `Status` (single_select) -> options `Inbox, Ready, In progress, Review, Done`' in output
    assert '  - `Milestone` (linked_seed) -> source `docs/ANCAP_DOCS_MILESTONE_SEED.md`' in output
    assert '- Seeded field commands:' in output
    assert '  - `Status` -> `gh project field-create <project-number> --owner ancapcloud --name Status --data-type SINGLE_SELECT --single-select-options "Inbox,Ready,In progress,Review,Done"`' in output
    assert '  - `Milestone` -> manual source `docs/ANCAP_DOCS_MILESTONE_SEED.md`' in output
    assert '  - `Good first issues` (board) -> filters `label:good first issue; status!=Done`' in output
    assert '- Manual steps:' in output
    assert '  - Use repository issue milestones from docs/ANCAP_DOCS_MILESTONE_SEED.md as the board milestone dimension for `Milestone`; gh project field-create does not create linked-seed milestone fields.' in output
    assert '- Starter issue project-item lookup commands:' in output
    assert '  - Project view: `gh project view <project-number> --owner ancapcloud --format json`' in output
    assert '  - Field list: `gh project field-list <project-number> --owner ancapcloud --format json`' in output
    assert '- Starter issue project-item commands:' in output
    assert '  - `Align Discussions categories and pin seeded bootstrap topics` -> add issue `https://github.com/ancapcloud/ancap-docs/issues/5` via `gh project item-add <project-number> --owner ancapcloud --url https://github.com/ancapcloud/ancap-docs/issues/5 --format json`' in output
    assert '    - set `Status` to `Inbox` via `gh project item-edit --id <item-id> --project-id <project-id> --field-id <status-field-id> --single-select-option-id <status-inbox-option-id>`' in output
    assert '    - set `Area` to `sdk` via `gh project item-edit --id <item-id> --project-id <project-id> --field-id <area-field-id> --single-select-option-id <area-sdk-option-id>`' in output
    assert '- Starter issue project-item notes:' in output
    assert '  - Run the field-list command with --format json to map field ids and single-select option ids before applying the item-edit commands.' in output
    assert '## Project board checklist' in output
    assert '## Notes' in output


def test_fetch_active_github_auth_context_parses_active_host_entry():
    module = load_bootstrap_script_module()

    payload = {
        'hosts': {
            'github.com': [
                {
                    'active': True,
                    'host': 'github.com',
                    'login': 'ancapcloud',
                    'tokenSource': 'keyring',
                    'scopes': 'gist, read:org, repo, workflow',
                }
            ]
        }
    }

    original = module.run_json_command
    try:
        module.run_json_command = lambda command, allow_not_found=False: payload
        assert module.fetch_active_github_auth_context(required_scopes=['read:project']) == {
            'host': 'github.com',
            'login': 'ancapcloud',
            'tokenSource': 'keyring',
            'scopes': ['gist', 'read:org', 'repo', 'workflow'],
            'missingScopes': ['read:project'],
        }
    finally:
        module.run_json_command = original



def test_fetch_active_github_auth_context_returns_none_when_status_probe_fails():
    module = load_bootstrap_script_module()

    def fail(command, allow_not_found=False):
        raise subprocess.CalledProcessError(1, command, output='', stderr='boom')

    original = module.run_json_command
    try:
        module.run_json_command = fail
        assert module.fetch_active_github_auth_context(required_scopes=['read:project']) is None
    finally:
        module.run_json_command = original



def test_fetch_live_branch_protection_state_returns_auth_probe_marker_when_branch_protection_is_hidden():
    module = load_bootstrap_script_module()

    def fail(command, allow_not_found=False):
        raise subprocess.CalledProcessError(
            1,
            command,
            output='',
            stderr='gh: Resource not accessible by integration (HTTP 403)',
        )

    original = module.run_json_command
    try:
        module.run_json_command = fail
        assert module.fetch_live_branch_protection_state('ancapcloud/ancap-docs', 'main') == {
            '_probeAuthError': 'gh: Resource not accessible by integration (HTTP 403)'
        }
    finally:
        module.run_json_command = original



def test_build_live_verification_snapshot_marks_hidden_branch_protection_as_unknown_not_drift():
    module = load_bootstrap_script_module()
    plan = module.load_bootstrap_plan()

    snapshot = module.build_live_verification_snapshot(
        'ancapcloud/ancap-docs',
        plan,
        repo_state={
            'visibility': plan['repo_settings']['visibility'],
            'description': plan['repo_settings']['description'],
            'homepage': plan['repo_settings']['homepage'],
            'default_branch': plan['repo_settings']['defaultBranch'],
            'has_issues': plan['repo_settings']['features']['issues'],
            'has_discussions': plan['repo_settings']['features']['discussions'],
            'has_projects': plan['repo_settings']['features']['projects'],
            'has_wiki': plan['repo_settings']['features']['wiki'],
            'allow_merge_commit': plan['repo_settings']['mergePolicy']['mergeCommits'],
            'allow_squash_merge': plan['repo_settings']['mergePolicy']['squashMerge'],
            'allow_rebase_merge': plan['repo_settings']['mergePolicy']['rebaseMerge'],
            'delete_branch_on_merge': plan['repo_settings']['mergePolicy']['autoDeleteHeadBranches'],
            'security_and_analysis': {
                'secret_scanning': {'status': 'enabled'},
                'secret_scanning_push_protection': {'status': 'enabled'},
            },
        },
        branch_protection_state={'_probeAuthError': 'gh: Resource not accessible by integration (HTTP 403)'},
        status_check_contexts=['Docs CI / docs-bundle'],
    )

    assert snapshot['ok'] is False
    assert snapshot['driftCount'] == 0
    assert snapshot['unknownCount'] == 3
    branch_checks = {
        (check['field'], check['status']): check
        for check in snapshot['checks']
        if check['scope'] == 'branchProtection'
    }
    assert ('configured', 'unknown') in branch_checks
    assert ('requiredStatusChecks', 'unknown') in branch_checks
    assert ('probeAuth', 'unknown') in branch_checks
    assert any(
        'branch protection details were not exposed in the current GitHub auth context' in note
        for note in snapshot['notes']
    )
    assert any(
        'branch protection probe error: gh: Resource not accessible by integration (HTTP 403)' in note
        for note in snapshot['notes']
    )



def test_build_discussion_admin_action_automation_summary_emits_graphql_commands_for_automatable_actions():
    module = load_bootstrap_script_module()

    actions = [
        {
            'kind': 'createAndPinDiscussionTopic',
            'title': 'Missing topic',
            'body': '# Missing topic\n\nSeed body',
            'expectedCategoryName': 'Announcements',
        },
        {
            'kind': 'moveDiscussionTopicCategory',
            'title': 'Welcome / how to use this repo',
            'expectedCategoryName': 'Announcements',
        },
        {
            'kind': 'updateDiscussionTopicBody',
            'title': 'Welcome / how to use this repo',
            'body': '# Welcome to ANCAP docs\n\nSeed body',
        },
    ]
    categories = {
        'Announcements': {
            'id': 'DIC_kwDOSq83QM4C-Dwf',
        }
    }
    discussion_topics_by_title = {
        'Welcome / how to use this repo': {
            'id': 'D_kwDOSq83QM4AABCD',
        }
    }

    summary = module.build_discussion_admin_action_automation_summary(
        actions,
        categories=categories,
        discussion_topics_by_title=discussion_topics_by_title,
        repository_id='R_kgDOTestRepo',
    )

    assert summary[0]['status'] == 'split_action'
    assert summary[0]['mutation'] == 'createDiscussion'
    assert summary[0]['repositoryId'] == 'R_kgDOTestRepo'
    assert summary[0]['categoryId'] == 'DIC_kwDOSq83QM4C-Dwf'
    assert summary[0]['title'] == 'Missing topic'
    assert summary[0]['body'] == '# Missing topic\n\nSeed body'
    assert summary[0]['command'] == module.format_command([
        'gh',
        'api',
        'graphql',
        '--raw-field',
        'query=mutation{createDiscussion(input:{repositoryId:"R_kgDOTestRepo",categoryId:"DIC_kwDOSq83QM4C-Dwf",title:"Missing topic",body:"# Missing topic\\n\\nSeed body"}){discussion{id url title}}}',
    ])
    assert summary[1]['status'] == 'automatable'
    assert summary[1]['mutation'] == 'updateDiscussion'
    assert summary[1]['discussionId'] == 'D_kwDOSq83QM4AABCD'
    assert summary[1]['categoryId'] == 'DIC_kwDOSq83QM4C-Dwf'
    assert summary[1]['command'] == module.format_command([
        'gh',
        'api',
        'graphql',
        '--raw-field',
        'query=mutation{updateDiscussion(input:{discussionId:"D_kwDOSq83QM4AABCD",categoryId:"DIC_kwDOSq83QM4C-Dwf"}){discussion{id url title}}}',
    ])
    assert summary[2]['status'] == 'automatable'
    assert summary[2]['mutation'] == 'updateDiscussion'
    assert summary[2]['discussionId'] == 'D_kwDOSq83QM4AABCD'
    assert summary[2]['body'] == '# Welcome to ANCAP docs\n\nSeed body'
    assert summary[2]['command'] == module.format_command([
        'gh',
        'api',
        'graphql',
        '--raw-field',
        'query=mutation{updateDiscussion(input:{discussionId:"D_kwDOSq83QM4AABCD",body:"# Welcome to ANCAP docs\\n\\nSeed body"}){discussion{id url title}}}',
    ])



def test_bootstrap_script_output_writes_utf8_file(tmp_path: Path):
    output_path = tmp_path / 'ancap-docs-live-checklist.md'
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            '--repo',
            'ancapcloud/ancap-docs',
            '--verify-live',
            '--verify-live-community',
            '--format',
            'markdown',
            '--output',
            str(output_path),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr or result.stdout
    assert output_path.exists()
    assert output_path.read_text(encoding='utf-8') == result.stdout
    assert output_path.read_bytes()[:2] != b'\xff\xfe'
    assert '# ANCAP docs live follow-up checklist for ancapcloud/ancap-docs' in result.stdout


def test_bootstrap_script_issue_reroute_helpers_render_edit_commands():
    module = load_bootstrap_script_module()

    assert module.parse_issue_number_from_url(
        'ancapcloud/ancap-docs',
        'https://github.com/ancapcloud/ancap-docs/issues/5',
    ) == 5
    assert module.parse_issue_number_from_url(
        'ancapcloud/ancap-docs',
        'https://github.com/ancapcloud/ancap-docs/issues/not-a-number',
    ) is None
    assert module.parse_issue_number_from_url(
        'ancapcloud/ancap-docs',
        'https://github.com/other-owner/ancap-docs/issues/5',
    ) is None

    command = module.build_initial_issue_edit_command(
        'ancapcloud/ancap-docs',
        5,
        body='Seed body',
        milestone='Docs repo bootstrap',
        add_labels=['docs'],
        remove_labels=['help wanted'],
    )
    assert command == [
        'gh',
        'issue',
        'edit',
        '5',
        '--repo',
        'ancapcloud/ancap-docs',
        '--body',
        'Seed body',
        '--milestone',
        'Docs repo bootstrap',
        '--add-label',
        'docs',
        '--remove-label',
        'help wanted',
    ]

    assert module.build_initial_issue_state_command('ancapcloud/ancap-docs', 6, 'CLOSED') == [
        'gh',
        'issue',
        'close',
        '6',
        '--repo',
        'ancapcloud/ancap-docs',
    ]
    assert module.build_initial_issue_state_command('ancapcloud/ancap-docs', 6, 'OPEN') == [
        'gh',
        'issue',
        'reopen',
        '6',
        '--repo',
        'ancapcloud/ancap-docs',
    ]

    output = module.render_live_verification_markdown(
        {
            'repo': 'ancapcloud/ancap-docs',
            'ok': False,
            'driftCount': 1,
            'unknownCount': 0,
            'checks': [],
            'manualFollowUps': {
                'initialIssueActions': [
                    {
                        'kind': 'rerouteInitialIssue',
                        'title': 'Align Discussions categories and pin seeded bootstrap topics',
                        'url': 'https://github.com/ancapcloud/ancap-docs/issues/5',
                        'expectedMilestone': 'Docs repo bootstrap',
                        'expectedLabels': ['docs'],
                        'bodyMatchesSeed': False,
                        'command': 'gh issue edit 5 --repo ancapcloud/ancap-docs --body "Seed body" --milestone "Docs repo bootstrap" --add-label docs --remove-label "help wanted"',
                    },
                    {
                        'kind': 'setInitialIssueState',
                        'title': 'Publish official contract-address and verification index',
                        'url': 'https://github.com/ancapcloud/ancap-docs/issues/6',
                        'expectedState': 'CLOSED',
                        'actualState': 'OPEN',
                        'statusNote': 'This seeded issue can stay closed because the public-safe contract-address and verification index is already live in the exported docs bundle and the matching live repo issue was completed.',
                        'command': 'gh issue close 6 --repo ancapcloud/ancap-docs',
                    }
                ]
            },
        }
    )
    assert '## Initial issue backlog checklist' in output
    assert '- [ ] Align seeded starter issue [`Align Discussions categories and pin seeded bootstrap topics`](https://github.com/ancapcloud/ancap-docs/issues/5) to milestone `Docs repo bootstrap`, labels `docs`, and the checked-in body summary.' in output
    assert '  - command: `gh issue edit 5 --repo ancapcloud/ancap-docs --body "Seed body" --milestone "Docs repo bootstrap" --add-label docs --remove-label "help wanted"`' in output
    assert '- [ ] Set seeded starter issue [`Publish official contract-address and verification index`](https://github.com/ancapcloud/ancap-docs/issues/6) to state `CLOSED`.' in output
    assert '  - status note: This seeded issue can stay closed because the public-safe contract-address and verification index is already live in the exported docs bundle and the matching live repo issue was completed.' in output
    assert '  - command: `gh issue close 6 --repo ancapcloud/ancap-docs`' in output


def test_live_verification_helpers_summarize_drift_and_manual_follow_ups():
    module = load_bootstrap_script_module()

    drift_summary = module.build_live_verification_drift_summary(
        [
            {'scope': 'discussionCategory', 'field': 'Ideas', 'status': 'drift'},
            {'scope': 'discussionCategory', 'field': 'Q&A', 'status': 'drift'},
            {'scope': 'projectBoard', 'field': 'auth', 'status': 'unknown'},
            {'scope': 'repo', 'field': 'visibility', 'status': 'match'},
        ]
    )
    assert drift_summary == {
        'driftChecks': [
            {'scope': 'discussionCategory', 'field': 'Ideas'},
            {'scope': 'discussionCategory', 'field': 'Q&A'},
        ],
        'unknownChecks': [
            {'scope': 'projectBoard', 'field': 'auth'},
        ],
        'driftCountByScope': {
            'discussionCategory': 2,
        },
        'unknownCountByScope': {
            'projectBoard': 1,
        },
    }

    manual_summary = module.build_live_verification_manual_follow_up_summary(
        {
            'discussionAdminActions': [
                {'kind': 'updateCategoryDescription'},
                {'kind': 'updateCategoryDescription'},
                {'kind': 'pinDiscussionTopic'},
            ],
            'projectBoardActions': [
                {'kind': 'requestProjectScope'},
            ],
            'discussionTopics': [],
        }
    )
    assert manual_summary == {
        'discussionAdminActions': {
            'count': 3,
            'byKind': {
                'updateCategoryDescription': 2,
                'pinDiscussionTopic': 1,
            },
        },
        'projectBoardActions': {
            'count': 1,
            'byKind': {
                'requestProjectScope': 1,
            },
        },
    }


def test_bootstrap_script_rejects_invalid_repo_creation_combinations():
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), '--repo', 'badrepo'],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode != 0
    assert '--repo requires OWNER/REPO format' in (result.stderr or result.stdout)

    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), '--repo', 'ancapcloud/ancap-docs', '--create-repo'],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode != 0
    assert '--create-repo requires --apply' in (result.stderr or result.stdout)

    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), '--repo', 'ancapcloud/ancap-docs', '--verify-live', '--apply'],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode != 0
    assert '--verify-live cannot be combined with --apply' in (result.stderr or result.stdout)

    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), '--repo', 'ancapcloud/ancap-docs', '--verify-live', '--create-repo'],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode != 0
    assert '--verify-live cannot be combined with --create-repo' in (result.stderr or result.stdout)

    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), '--repo', 'ancapcloud/ancap-docs', '--verify-live-community'],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode != 0
    assert '--verify-live-community requires --verify-live' in (result.stderr or result.stdout)

    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), '--repo', 'ancapcloud/ancap-docs', '--format', 'markdown'],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode != 0
    assert '--format markdown currently requires --verify-live' in (result.stderr or result.stdout)

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            '--repo',
            'ancapcloud/ancap-docs',
            '--apply',
            '--create-repo',
            '--apply-branch-protection',
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode != 0
    assert '--create-repo cannot be combined with --apply-branch-protection' in (result.stderr or result.stdout)


def test_docs_and_status_files_reference_bootstrap_helper():
    readme_text = README_PATH.read_text(encoding='utf-8')
    roadmap_text = ROADMAP_PATH.read_text(encoding='utf-8')
    status_text = STATUS_MATRIX_PATH.read_text(encoding='utf-8')
    open_source_text = OPEN_SOURCE_DOC_PATH.read_text(encoding='utf-8')
    docs_split_text = DOCS_SPLIT_PLAN_PATH.read_text(encoding='utf-8')
    docs_bootstrap_text = DOCS_BOOTSTRAP_PATH.read_text(encoding='utf-8')

    assert 'scripts/bootstrap_ancap_docs_repo.py' in readme_text
    assert 'scripts/bootstrap_ancap_docs_repo.py' in roadmap_text
    assert 'scripts/bootstrap_ancap_docs_repo.py' in status_text
    assert 'scripts/bootstrap_ancap_docs_repo.py' in open_source_text
    assert 'scripts/bootstrap_ancap_docs_repo.py' in docs_split_text
    assert 'scripts/bootstrap_ancap_docs_repo.py' in docs_bootstrap_text
    assert 'gh-driven helper for public repo creation, repo settings/labels/milestones, live repo verification' in status_text
    assert 'Docs CI / docs-bundle' in status_text
    assert 'the exported bundle has been pushed as the first public-safe seed commit' in status_text
    assert 'gh-driven public repo creation, repo settings, label, milestone, live repo verification, and branch-protection payload application' in open_source_text
    assert 'the initial docs bundle is pushed' in open_source_text
    assert 'default-branch protection is live with the seeded `Docs CI / docs-bundle` required-check context' in open_source_text
    assert '.github/workflows/docs-ci.yml' in open_source_text
    assert 'checked-in seeds with `gh` instead of launch-day retyping' in roadmap_text
    assert 'Docs CI / docs-bundle' in roadmap_text
    assert '--apply-branch-protection --status-check-context <context>' in docs_bootstrap_text
    assert 'Docs CI / docs-bundle' in docs_bootstrap_text
    assert 'default-branch protection payload once public CI status-check names exist' in docs_bootstrap_text
    assert '--verify-live' in docs_bootstrap_text
    assert '--verify-live-community' in docs_bootstrap_text
    assert '--output <path>' in docs_bootstrap_text
    assert 'the exported bundle has already been pushed as the first commit on `main`' in docs_bootstrap_text
    assert 'reports the current repo metadata, branch protection, seeded labels, seeded milestones, Discussions-category drift, seeded discussion-topic presence, seeded discussion-topic body alignment, pinned-discussion presence, per-topic live URLs/categories, and explicit project-board auth-scope blockage against the checked-in seed' in docs_bootstrap_text
    assert 'machine-readable `.github/bootstrap/*.json` seeds still match the human-readable Markdown docs' in docs_bootstrap_text
    script_text = SCRIPT_PATH.read_text(encoding='utf-8')
    assert 'Discussion UI targets' in script_text
    assert 'Discussions automation map' in script_text
    assert 'discussion action automation:' in script_text
    assert 'GitHub\'s public gh/API surface does not expose discussion pin/unpin admin mutations.' in script_text
    assert 'Initial issue backlog commands' in script_text
    assert 'Keep the seeded starter backlog explicit via the checked-in gh issue create commands' in script_text
