from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "generate_ancap_docs_live_followup.py"
BOOTSTRAP_SCRIPT_PATH = REPO_ROOT / "scripts" / "bootstrap_ancap_docs_repo.py"
LIVE_ANCAP_DOCS_VERIFY = os.environ.get("RUN_ANCAP_DOCS_LIVE_VERIFY") == "1"


def load_module():
    spec = importlib.util.spec_from_file_location("generate_ancap_docs_live_followup", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_build_output_paths_uses_basename_and_date_label():
    module = load_module()

    markdown_path, json_path = module.build_output_paths(
        output_dir=Path("tmp"),
        basename="ancap-docs-live-follow-up",
        date_label="2026-06-01",
    )

    assert markdown_path == Path("tmp/ancap-docs-live-follow-up-2026-06-01.md")
    assert json_path == Path("tmp/ancap-docs-live-follow-up-2026-06-01.json")


def test_build_latest_alias_paths_use_stable_latest_suffix():
    module = load_module()

    markdown_path, json_path = module.build_latest_alias_paths(
        output_dir=Path("tmp"),
        basename="ancap-docs-live-follow-up",
    )

    assert markdown_path == Path("tmp/ancap-docs-live-follow-up-latest.md")
    assert json_path == Path("tmp/ancap-docs-live-follow-up-latest.json")


def test_validate_filename_component_accepts_plain_filename_components():
    module = load_module()

    assert module._validate_filename_component("ancap-docs-live-follow-up", flag_name="--basename") == "ancap-docs-live-follow-up"
    assert module._validate_filename_component("2026-06-01", flag_name="--date-label") == "2026-06-01"


def test_validate_filename_component_rejects_paths_and_dot_segments():
    module = load_module()

    for value in ["nested/path", r"nested\\path", ".", ".."]:
        try:
            module._validate_filename_component(value, flag_name="--basename")
        except ValueError as exc:
            message = str(exc)
        else:
            raise AssertionError(f"expected filename-component validation to fail for {value!r}")

        assert "filename component only" in message or "must not be '.' or '..'" in message


def test_generate_followup_script_mentions_default_artifact_pair_and_bootstrap_helper():
    script_text = SCRIPT_PATH.read_text(encoding="utf-8")

    assert "ancap-docs-live-follow-up" in script_text
    assert "--verify-live" in script_text
    assert "--verify-live-community" in script_text
    assert "--format" in script_text
    assert "markdown" in script_text
    assert "json" in script_text
    assert "--verbose-child-output" in script_text
    assert "--write-latest-alias" in script_text
    assert "<basename>-latest.md" in script_text
    assert "<basename>-latest.json" in script_text
    assert "artifactMetadata" in script_text
    assert "repoHead" in script_text
    assert "Generator repo HEAD:" in script_text
    assert "Generated at (UTC):" in script_text
    assert "By default this wrapper keeps terminal output concise" in script_text
    assert "Saved paired ancap-docs live follow-up artifacts:" in script_text
    assert "Saved stable latest-alias artifacts:" in script_text
    assert "scripts/bootstrap_ancap_docs_repo.py" in script_text


@pytest.mark.skipif(
    not LIVE_ANCAP_DOCS_VERIFY,
    reason="live ancap-docs verification requires explicit opt-in auth and mutable external GitHub state",
)
def test_generate_followup_script_writes_default_artifact_pair(tmp_path: Path):
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--repo",
            "ancapcloud/ancap-docs",
            "--output-dir",
            str(tmp_path),
            "--date-label",
            "2026-06-01",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr or result.stdout
    markdown_output = tmp_path / "ancap-docs-live-follow-up-2026-06-01.md"
    json_output = tmp_path / "ancap-docs-live-follow-up-2026-06-01.json"
    markdown_latest = tmp_path / "ancap-docs-live-follow-up-latest.md"
    json_latest = tmp_path / "ancap-docs-live-follow-up-latest.json"
    assert markdown_output.exists()
    assert json_output.exists()
    assert markdown_latest.exists()
    assert json_latest.exists()
    assert markdown_output.read_bytes()[:2] != b"\xff\xfe"
    assert markdown_output.read_bytes()[:2] != b"\xfe\xff"
    assert json_output.read_bytes()[:2] != b"\xff\xfe"
    assert json_output.read_bytes()[:2] != b"\xfe\xff"
    assert markdown_latest.read_bytes() == markdown_output.read_bytes()
    assert json_latest.read_bytes() == json_output.read_bytes()
    markdown_output_posix = markdown_output.as_posix()
    json_output_posix = json_output.as_posix()
    markdown_latest_posix = markdown_latest.as_posix()
    json_latest_posix = json_latest.as_posix()
    markdown_text = markdown_output.read_text(encoding="utf-8")
    assert "# ANCAP docs live follow-up checklist for ancapcloud/ancap-docs" in markdown_text
    assert "## Discussion UI targets" in markdown_text
    assert "Tracked cleanup issue: [`Align Discussions categories and pin seeded bootstrap topics`](https://github.com/ancapcloud/ancap-docs/issues/5)" in markdown_text
    assert "## Discussions admin checklist" in markdown_text
    assert "Pin seeded bootstrap discussion [`Welcome / how to use this repo`](https://github.com/ancapcloud/ancap-docs/discussions/2)." in markdown_text
    assert "## Project board seed targets" in markdown_text
    assert "Auth refresh command: `gh auth refresh -h github.com -s read:project`" in markdown_text
    assert "## Project board checklist" in markdown_text
    assert "## Discussions automation map" in markdown_text
    assert "## Artifact metadata" in markdown_text
    assert "- Generator: `scripts/generate_ancap_docs_live_followup.py`" in markdown_text
    assert "- Bootstrap source: `scripts/bootstrap_ancap_docs_repo.py`" in markdown_text
    assert "- Generator repo HEAD: `" in markdown_text
    assert "working tree)" in markdown_text
    assert f"- Dated markdown artifact: `{markdown_output_posix}`" in markdown_text
    assert f"- Dated JSON artifact: `{json_output_posix}`" in markdown_text
    assert f"- Latest markdown alias: `{markdown_latest_posix}`" in markdown_text
    assert f"- Latest JSON alias: `{json_latest_posix}`" in markdown_text
    json_payload = json.loads(json_output.read_text(encoding="utf-8"))
    assert json_payload["repo"] == "ancapcloud/ancap-docs"
    assert json_payload["artifactMetadata"] == {
        "repo": "ancapcloud/ancap-docs",
        "generatedAt": json_payload["artifactMetadata"]["generatedAt"],
        "dateLabel": "2026-06-01",
        "basename": "ancap-docs-live-follow-up",
        "generator": "scripts/generate_ancap_docs_live_followup.py",
        "bootstrapScript": "scripts/bootstrap_ancap_docs_repo.py",
        "repoHead": json_payload["artifactMetadata"]["repoHead"],
        "artifacts": {
            "markdown": markdown_output_posix,
            "json": json_output_posix,
        },
        "latestAliases": {
            "markdown": markdown_latest_posix,
            "json": json_latest_posix,
        },
    }
    assert json_payload["artifactMetadata"]["generatedAt"].endswith("Z")
    assert isinstance(json_payload["artifactMetadata"]["repoHead"], dict)
    assert "headRef" in json_payload["artifactMetadata"]["repoHead"]
    assert "headCommit" in json_payload["artifactMetadata"]["repoHead"]
    assert "workingTreeDirty" in json_payload["artifactMetadata"]["repoHead"]
    assert str(markdown_output).replace("\\", "/") in result.stdout.replace("\\", "/")
    assert str(json_output).replace("\\", "/") in result.stdout.replace("\\", "/")
    assert str(markdown_latest).replace("\\", "/") in result.stdout.replace("\\", "/")
    assert str(json_latest).replace("\\", "/") in result.stdout.replace("\\", "/")
    assert "Live follow-up summary:" in result.stdout
    assert f"- Overall OK: {json_payload['ok']}" in result.stdout
    assert f"- Drift count: {json_payload['driftCount']}" in result.stdout
    assert f"- Unknown count: {json_payload['unknownCount']}" in result.stdout
    assert "- Drift by scope:" in result.stdout
    assert "  - discussionCategory: 5" in result.stdout
    assert "  - pinnedDiscussionTopic: 3" in result.stdout
    assert "- Manual follow-up counts:" in result.stdout
    assert "  - discussionAdminActions: 9 (pinDiscussionTopic=3, removeUnexpectedCategory=2, updateCategoryDescription=4)" in result.stdout
    assert "  - projectBoardActions: 2 (requestProjectScope=1, seedProjectBoard=1)" in result.stdout
    assert "## Drift summary" not in result.stdout
    assert '"driftCount": 8' not in result.stdout


@pytest.mark.skipif(
    not LIVE_ANCAP_DOCS_VERIFY,
    reason="live ancap-docs verification requires explicit opt-in auth and mutable external GitHub state",
)
def test_generate_followup_script_verbose_mode_echoes_child_output(tmp_path: Path):
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--repo",
            "ancapcloud/ancap-docs",
            "--output-dir",
            str(tmp_path),
            "--date-label",
            "2026-06-01",
            "--verbose-child-output",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr or result.stdout
    assert "## Drift summary" in result.stdout
    assert '"driftCount": 8' in result.stdout


def test_generate_followup_script_rejects_blank_basename(tmp_path: Path):
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--repo",
            "ancapcloud/ancap-docs",
            "--output-dir",
            str(tmp_path),
            "--basename",
            "   ",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode != 0
    assert "--basename requires a non-empty value" in (result.stderr or result.stdout)


def test_generate_followup_script_rejects_invalid_repo_argument(tmp_path: Path):
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--repo",
            "badrepo",
            "--output-dir",
            str(tmp_path),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode != 0
    assert "--repo requires OWNER/REPO format" in (result.stderr or result.stdout)


def test_generate_followup_script_rejects_blank_date_label(tmp_path: Path):
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--repo",
            "ancapcloud/ancap-docs",
            "--output-dir",
            str(tmp_path),
            "--date-label",
            "   ",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode != 0
    assert "--date-label requires a non-empty value" in (result.stderr or result.stdout)



def test_generate_followup_script_rejects_path_like_basename(tmp_path: Path):
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--repo",
            "ancapcloud/ancap-docs",
            "--output-dir",
            str(tmp_path),
            "--basename",
            "nested/path",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode != 0
    assert "--basename must be a filename component only, not a path: nested/path" in (result.stderr or result.stdout)



def test_generate_followup_script_rejects_path_like_date_label(tmp_path: Path):
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--repo",
            "ancapcloud/ancap-docs",
            "--output-dir",
            str(tmp_path),
            "--date-label",
            "nested/path",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode != 0
    assert "--date-label must be a filename component only, not a path: nested/path" in (result.stderr or result.stdout)



def test_validate_distinct_artifact_paths_rejects_latest_alias_collisions(tmp_path: Path):
    module = load_module()

    dated_markdown = tmp_path / "ancap-docs-live-follow-up-latest.md"
    dated_json = tmp_path / "ancap-docs-live-follow-up-latest.json"
    latest_markdown, latest_json = module.build_latest_alias_paths(
        output_dir=tmp_path,
        basename="ancap-docs-live-follow-up",
    )

    try:
        module._validate_distinct_artifact_paths(
            markdown_output=dated_markdown,
            json_output=dated_json,
            markdown_alias=latest_markdown,
            json_alias=latest_json,
            write_latest_alias=True,
        )
    except ValueError as exc:
        message = str(exc)
    else:
        raise AssertionError("expected latest-alias collision validation to fail")

    assert "Choose a different --date-label or pass --no-write-latest-alias" in message
    assert "dated markdown artifact" in message or "dated JSON artifact" in message



def test_summary_exit_code_stays_zero_without_fail_on_not_ok():
    module = load_module()

    assert module._summary_exit_code(overall_ok=True, fail_on_not_ok=False) == 0
    assert module._summary_exit_code(overall_ok=False, fail_on_not_ok=False) == 0



def test_summary_exit_code_returns_two_when_fail_on_not_ok_requested():
    module = load_module()

    assert module._summary_exit_code(overall_ok=True, fail_on_not_ok=True) == 0
    assert module._summary_exit_code(overall_ok=False, fail_on_not_ok=True) == 2



def test_generate_followup_script_fail_on_not_ok_returns_nonzero_and_writes_artifacts(tmp_path: Path):
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--repo",
            "ancapcloud/ancap-docs",
            "--output-dir",
            str(tmp_path),
            "--date-label",
            "2026-06-01",
            "--fail-on-not-ok",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 2, result.stderr or result.stdout
    markdown_output = tmp_path / "ancap-docs-live-follow-up-2026-06-01.md"
    json_output = tmp_path / "ancap-docs-live-follow-up-2026-06-01.json"
    markdown_latest = tmp_path / "ancap-docs-live-follow-up-latest.md"
    json_latest = tmp_path / "ancap-docs-live-follow-up-latest.json"
    assert markdown_output.exists()
    assert json_output.exists()
    assert markdown_latest.exists()
    assert json_latest.exists()
    assert "Live follow-up summary:" in result.stdout
    assert "- Overall OK: False" in result.stdout
    assert "Live follow-up summary is not OK; exiting non-zero because --fail-on-not-ok was requested." in result.stderr


def test_generate_followup_script_can_skip_latest_alias_writes(tmp_path: Path):
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--repo",
            "ancapcloud/ancap-docs",
            "--output-dir",
            str(tmp_path),
            "--date-label",
            "2026-06-01",
            "--no-write-latest-alias",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr or result.stdout
    markdown_output = tmp_path / "ancap-docs-live-follow-up-2026-06-01.md"
    json_output = tmp_path / "ancap-docs-live-follow-up-2026-06-01.json"
    assert markdown_output.exists()
    assert json_output.exists()
    assert not (tmp_path / "ancap-docs-live-follow-up-latest.md").exists()
    assert not (tmp_path / "ancap-docs-live-follow-up-latest.json").exists()
    markdown_text = markdown_output.read_text(encoding="utf-8")
    assert "- Latest aliases: not written (`--no-write-latest-alias`)" in markdown_text
    json_payload = json.loads(json_output.read_text(encoding="utf-8"))
    assert json_payload["artifactMetadata"]["latestAliases"] is None
    assert "Saved stable latest-alias artifacts:" not in result.stdout



def test_generate_followup_script_rejects_date_label_that_collides_with_latest_alias(tmp_path: Path):
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--repo",
            "ancapcloud/ancap-docs",
            "--output-dir",
            str(tmp_path),
            "--date-label",
            "latest",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode != 0
    message = result.stderr or result.stdout
    assert "Choose a different --date-label or pass --no-write-latest-alias" in message
    assert "latest markdown alias" in message or "latest JSON alias" in message



def test_generate_followup_script_rejects_missing_bootstrap_script(tmp_path: Path):
    missing_script = tmp_path / "missing-bootstrap.py"
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--repo",
            "ancapcloud/ancap-docs",
            "--output-dir",
            str(tmp_path),
            "--bootstrap-script",
            str(missing_script),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode != 0
    assert f"--bootstrap-script does not exist: {missing_script}" in (result.stderr or result.stdout)



def test_generate_followup_script_rejects_non_file_bootstrap_script(tmp_path: Path):
    bootstrap_dir = tmp_path / "bootstrap-dir"
    bootstrap_dir.mkdir()
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--repo",
            "ancapcloud/ancap-docs",
            "--output-dir",
            str(tmp_path),
            "--bootstrap-script",
            str(bootstrap_dir),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode != 0
    assert f"--bootstrap-script must point to a file: {bootstrap_dir}" in (result.stderr or result.stdout)



def test_generate_followup_script_rejects_output_dir_that_is_a_file(tmp_path: Path):
    output_file = tmp_path / "not-a-directory.txt"
    output_file.write_text("placeholder\n", encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--repo",
            "ancapcloud/ancap-docs",
            "--output-dir",
            str(output_file),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode != 0
    assert f"--output-dir must be a directory path: {output_file}" in (result.stderr or result.stdout)
