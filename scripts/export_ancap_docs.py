from __future__ import annotations

import argparse
import os
import re
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_NAME = "EXPORT_MANIFEST.md"
SOURCE_REPO_WEB_BASE = "https://github.com/ancapcloud/ancap"
SOURCE_REPO_REF = "master"
MARKDOWN_LINK_RE = re.compile(r"(?P<prefix>!?\[[^\]]*\]\()(?P<target>[^)]+)(?P<suffix>\))")
EXTERNAL_LINK_PREFIXES = ("http://", "https://", "mailto:", "tel:", "data:")

EXPORT_ENTRIES = [
    (Path("docs/ANCAP_DOCS_REPO_README.md"), Path("README.md")),
    (Path("LICENSE"), Path("LICENSE")),
    (Path("CONTRIBUTING.md"), Path("CONTRIBUTING.md")),
    (Path("SECURITY.md"), Path("SECURITY.md")),
    (Path("CODE_OF_CONDUCT.md"), Path("CODE_OF_CONDUCT.md")),
    (Path(".github/CODEOWNERS"), Path(".github/CODEOWNERS")),
    (Path(".github/bootstrap/README.md"), Path(".github/bootstrap/README.md")),
    (Path(".github/bootstrap/ancap-docs-contributor-intake.json"), Path(".github/bootstrap/ancap-docs-contributor-intake.json")),
    (Path(".github/bootstrap/ancap-docs-dependabot.yml"), Path(".github/bootstrap/ancap-docs-dependabot.yml")),
    (Path(".github/pull_request_template.md"), Path(".github/pull_request_template.md")),
    (Path(".github/ISSUE_TEMPLATE/bug_report.md"), Path(".github/ISSUE_TEMPLATE/bug_report.md")),
    (Path(".github/ISSUE_TEMPLATE/feature_request.md"), Path(".github/ISSUE_TEMPLATE/feature_request.md")),
    (Path(".github/ISSUE_TEMPLATE/config.yml"), Path(".github/ISSUE_TEMPLATE/config.yml")),
    (Path(".github/workflows/docs-ci.yml"), Path(".github/workflows/docs-ci.yml")),
    (Path(".github/bootstrap/ancap-docs-labels.json"), Path(".github/bootstrap/ancap-docs-labels.json")),
    (Path(".github/bootstrap/ancap-docs-milestones.json"), Path(".github/bootstrap/ancap-docs-milestones.json")),
    (Path(".github/bootstrap/ancap-docs-discussions.json"), Path(".github/bootstrap/ancap-docs-discussions.json")),
    (Path(".github/bootstrap/ancap-docs-project-board.json"), Path(".github/bootstrap/ancap-docs-project-board.json")),
    (Path(".github/bootstrap/ancap-docs-initial-issues.json"), Path(".github/bootstrap/ancap-docs-initial-issues.json")),
    (Path(".github/bootstrap/ancap-docs-repo-settings.json"), Path(".github/bootstrap/ancap-docs-repo-settings.json")),
    (Path(".github/bootstrap/ancap-docs-update-cadence.json"), Path(".github/bootstrap/ancap-docs-update-cadence.json")),
    (Path(".github/bootstrap/ancap-docs-ci.json"), Path(".github/bootstrap/ancap-docs-ci.json")),
    (Path(".github/bootstrap/ancap-docs-ci-workflow.yml"), Path(".github/bootstrap/ancap-docs-ci-workflow.yml")),
    (Path("MASTER_ROADMAP.md"), Path("MASTER_ROADMAP.md")),
    (Path("docs/STATUS_MATRIX.md"), Path("docs/STATUS_MATRIX.md")),
    (Path("docs/OPEN_SOURCE_GITHUB_TRANSPARENCY.md"), Path("docs/OPEN_SOURCE_GITHUB_TRANSPARENCY.md")),
    (Path("docs/ANCAP_DOCS_SPLIT.md"), Path("docs/ANCAP_DOCS_SPLIT.md")),
    (Path("docs/ANCAP_DOCS_REPO_BOOTSTRAP.md"), Path("docs/ANCAP_DOCS_REPO_BOOTSTRAP.md")),
    (Path("docs/ANCAP_DOCS_CONTRIBUTOR_INTAKE_SEED.md"), Path("docs/ANCAP_DOCS_CONTRIBUTOR_INTAKE_SEED.md")),
    (Path("docs/ANCAP_DOCS_LABEL_SEED.md"), Path("docs/ANCAP_DOCS_LABEL_SEED.md")),
    (Path("docs/ANCAP_DOCS_DISCUSSIONS_SEED.md"), Path("docs/ANCAP_DOCS_DISCUSSIONS_SEED.md")),
    (Path("docs/ANCAP_DOCS_MILESTONE_SEED.md"), Path("docs/ANCAP_DOCS_MILESTONE_SEED.md")),
    (Path("docs/ANCAP_DOCS_PROJECT_BOARD_SEED.md"), Path("docs/ANCAP_DOCS_PROJECT_BOARD_SEED.md")),
    (Path("docs/ANCAP_DOCS_INITIAL_ISSUES_SEED.md"), Path("docs/ANCAP_DOCS_INITIAL_ISSUES_SEED.md")),
    (Path("docs/ANCAP_DOCS_REPO_SETTINGS_SEED.md"), Path("docs/ANCAP_DOCS_REPO_SETTINGS_SEED.md")),
    (Path("docs/ANCAP_DOCS_UPDATE_CADENCE_SEED.md"), Path("docs/ANCAP_DOCS_UPDATE_CADENCE_SEED.md")),
    (Path("docs/ANCAP_DOCS_CI_SEED.md"), Path("docs/ANCAP_DOCS_CI_SEED.md")),
    (Path("docs/ANCAP_DOCS_DEPENDABOT_SEED.md"), Path("docs/ANCAP_DOCS_DEPENDABOT_SEED.md")),
    (Path("docs/VISION.md"), Path("docs/VISION.md")),
    (Path("docs/ARCHITECTURE_LAYERS.md"), Path("docs/ARCHITECTURE_LAYERS.md")),
    (Path("docs/PLAN_L0_TO_L3.md"), Path("docs/PLAN_L0_TO_L3.md")),
    (Path("docs/REPUTATION_2.md"), Path("docs/REPUTATION_2.md")),
    (Path("docs/STAKING.md"), Path("docs/STAKING.md")),
    (Path("docs/WHITEPAPER_PROJECT.md"), Path("docs/WHITEPAPER_PROJECT.md")),
    (Path("docs/WHITEPAPER_ACP.md"), Path("docs/WHITEPAPER_ACP.md")),
    (Path("docs/LEGAL_TERMS_TEMPLATE.md"), Path("docs/LEGAL_TERMS_TEMPLATE.md")),
    (Path("docs/BRIDGE_RISK_DOCUMENTATION.md"), Path("docs/BRIDGE_RISK_DOCUMENTATION.md")),
    (Path("docs/OFFICIAL_CONTRACT_ADDRESSES.md"), Path("docs/OFFICIAL_CONTRACT_ADDRESSES.md")),
    (Path("docs/CONTRACT_VERIFICATION_GUIDE.md"), Path("docs/CONTRACT_VERIFICATION_GUIDE.md")),
    (Path("docs/TESTNET_DEPLOYMENT_GUIDE.md"), Path("docs/TESTNET_DEPLOYMENT_GUIDE.md")),
    (Path("docs/AUDIT_CHECKLIST.md"), Path("docs/AUDIT_CHECKLIST.md")),
    (Path("docs/CHANGELOG_PUBLIC.md"), Path("docs/CHANGELOG_PUBLIC.md")),
    (Path("docs/PUBLIC_INTEGRATION_EXAMPLES.md"), Path("docs/PUBLIC_INTEGRATION_EXAMPLES.md")),
]
DOCS_DEPENDABOT_TEMPLATE_SOURCE = Path(".github/bootstrap/ancap-docs-dependabot.yml")
DOCS_DEPENDABOT_EXPORT_PATH = Path(".github/dependabot.yml")

EXPORT_SOURCE_TO_OUTPUT = {source.as_posix(): output for source, output in EXPORT_ENTRIES}
EXPORT_OUTPUT_SET = {output.as_posix() for _, output in EXPORT_ENTRIES}
EXPORT_OUTPUT_SET.add(DOCS_DEPENDABOT_EXPORT_PATH.as_posix())


def _validate_export_paths() -> None:
    missing = [str(source) for source, _ in EXPORT_ENTRIES if not (REPO_ROOT / source).exists()]
    if missing:
        joined = ", ".join(sorted(missing))
        raise FileNotFoundError(f"missing export source files: {joined}")


def _manifest_text(exported_paths: list[Path]) -> str:
    lines = [
        "# ANCAP public docs export manifest",
        "",
        "Generated by `scripts/export_ancap_docs.py`.",
        "",
        "This bundle is the repo-staged source for the future public `ancap-docs` repository.",
        "It intentionally includes only public-safe documentation, governance files, contributor issue/PR templates, a copy-ready Docs CI workflow, a docs-repo-specific Dependabot config, the first-push labels / Discussions / milestone / project-board / initial-issues / repo-settings / contributor-intake / update-cadence / CI bootstrap checklist, the contributor-intake seed for the future docs repo, the label seed for the future docs repo, the initial Discussions category seed with copy-ready pinned-topic text, the initial milestone seed, the initial project-board seed, the initial issue seed, the initial repo-settings seed, the initial public update-cadence seed with copy-ready update/release-note templates, the initial Docs CI seed with a documented default required-check context, the initial docs-repo Dependabot seed, the matching bootstrap workflow template referenced by that CI seed, the matching bootstrap Dependabot template for the exported `.github/dependabot.yml`, automation-ready contributor-intake / label / milestone / Discussions / project-board / initial-issues / repo-settings / update-cadence / CI metadata, machine-readable contributor-intake seeds plus machine-readable label / milestone / Discussions / project-board / initial-issues / repo-settings / update-cadence / CI seeds, a bootstrap-seed README, and a baseline CODEOWNERS file for review routing.",
        "Relative links to files outside this bundle are rewritten to the source monorepo on GitHub so the export stays navigable as a standalone repo seed.",
        "",
        "## Exported files",
    ]
    lines.extend(f"- `{path.as_posix()}`" for path in exported_paths)
    lines.extend(
        [
            "",
            "## Excluded by design",
            "- runtime secrets (`.env`, deploy secrets, API keys, mnemonics, private keys)`",
            "- operational infrastructure (`infra/`, `deploy/`, `Sicret/`, server credentials)`",
            "- hot-wallet / bridge-signer internals and other abuse-sensitive implementation details",
            "",
            "## Source-monorepo fallback for rewritten links",
            f"- `{SOURCE_REPO_WEB_BASE}/blob/{SOURCE_REPO_REF}/...` for files",
            f"- `{SOURCE_REPO_WEB_BASE}/tree/{SOURCE_REPO_REF}/...` for directories",
        ]
    )
    return "\n".join(lines) + "\n"


def _split_markdown_target(target: str) -> tuple[str, str, str]:
    clean = target.strip()
    if clean.startswith("<") and clean.endswith(">"):
        clean = clean[1:-1].strip()

    fragment = ""
    if "#" in clean:
        clean, fragment_part = clean.split("#", 1)
        fragment = f"#{fragment_part}"

    query = ""
    if "?" in clean:
        clean, query_part = clean.split("?", 1)
        query = f"?{query_part}"

    return clean, query, fragment


def _is_external_target(target_path: str) -> bool:
    lowered = target_path.lower()
    return lowered.startswith(EXTERNAL_LINK_PREFIXES)


def _resolve_repo_target(source_rel_path: Path, target_path: str) -> Path | None:
    resolved = (REPO_ROOT / source_rel_path.parent / target_path).resolve()
    try:
        return resolved.relative_to(REPO_ROOT)
    except ValueError:
        return None


def _relative_bundle_path(output_rel_path: Path, target_output_rel_path: Path) -> str:
    relative = os.path.relpath(REPO_ROOT / target_output_rel_path, start=(REPO_ROOT / output_rel_path).parent)
    return Path(relative).as_posix()


def _source_repo_url(target_rel_path: Path) -> str:
    target_abs_path = REPO_ROOT / target_rel_path
    kind = "tree" if target_abs_path.is_dir() else "blob"
    return f"{SOURCE_REPO_WEB_BASE}/{kind}/{SOURCE_REPO_REF}/{target_rel_path.as_posix()}"


def rewrite_markdown_links(source_rel_path: Path, output_rel_path: Path, text: str) -> str:
    unresolved: list[str] = []

    def replace(match: re.Match[str]) -> str:
        raw_target = match.group("target")
        target_path, query, fragment = _split_markdown_target(raw_target)

        if not target_path or target_path.startswith("#") or _is_external_target(target_path):
            return match.group(0)

        resolved = _resolve_repo_target(source_rel_path, target_path)
        if resolved is None:
            unresolved.append(f"{source_rel_path.as_posix()} -> {target_path}")
            return match.group(0)

        target_abs_path = REPO_ROOT / resolved
        if not target_abs_path.exists():
            unresolved.append(f"{source_rel_path.as_posix()} -> {resolved.as_posix()}")
            return match.group(0)

        target_output_rel_path = EXPORT_SOURCE_TO_OUTPUT.get(resolved.as_posix())
        if target_output_rel_path is not None:
            rewritten_target = _relative_bundle_path(output_rel_path, target_output_rel_path)
        else:
            rewritten_target = _source_repo_url(resolved)

        return f"{match.group('prefix')}{rewritten_target}{query}{fragment}{match.group('suffix')}"

    rewritten = MARKDOWN_LINK_RE.sub(replace, text)
    if unresolved:
        joined = "; ".join(unresolved)
        raise ValueError(f"unresolved markdown links in export source: {joined}")
    return rewritten



def find_unresolved_bundle_links(target_dir: Path) -> list[str]:
    unresolved: list[str] = []

    for markdown_path in sorted(target_dir.rglob("*.md")):
        relative_markdown_path = markdown_path.relative_to(target_dir)
        text = markdown_path.read_text(encoding="utf-8")
        for match in MARKDOWN_LINK_RE.finditer(text):
            target_path, _, _ = _split_markdown_target(match.group("target"))
            if not target_path or target_path.startswith("#") or _is_external_target(target_path):
                continue

            resolved = (markdown_path.parent / target_path).resolve()
            try:
                resolved.relative_to(target_dir.resolve())
            except ValueError:
                unresolved.append(f"{relative_markdown_path.as_posix()} -> {target_path}")
                continue

            if not resolved.exists():
                unresolved.append(f"{relative_markdown_path.as_posix()} -> {target_path}")

    return unresolved


def copy_export_bundle(target_dir: Path, *, clean: bool = False) -> list[Path]:
    _validate_export_paths()

    if clean and target_dir.exists():
        shutil.rmtree(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    exported: list[Path] = []
    for source_rel_path, output_rel_path in EXPORT_ENTRIES:
        source = REPO_ROOT / source_rel_path
        destination = target_dir / output_rel_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        if source_rel_path.suffix.lower() == ".md":
            destination.write_text(
                rewrite_markdown_links(source_rel_path, output_rel_path, source.read_text(encoding="utf-8")),
                encoding="utf-8",
            )
        else:
            shutil.copy2(source, destination)
        exported.append(output_rel_path)

    docs_dependabot_destination = target_dir / DOCS_DEPENDABOT_EXPORT_PATH
    docs_dependabot_destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(target_dir / DOCS_DEPENDABOT_TEMPLATE_SOURCE, docs_dependabot_destination)
    exported.append(DOCS_DEPENDABOT_EXPORT_PATH)

    manifest_path = target_dir / MANIFEST_NAME
    manifest_path.write_text(_manifest_text(exported), encoding="utf-8")

    unresolved = find_unresolved_bundle_links(target_dir)
    if unresolved:
        joined = "; ".join(unresolved)
        raise ValueError(f"export bundle still has unresolved relative links: {joined}")

    return exported


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Export the public-safe ANCAP docs bundle for the future ancap-docs repo."
    )
    parser.add_argument("--target", required=True, help="Target directory for the exported docs bundle")
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Delete the target directory before exporting",
    )
    args = parser.parse_args(argv)

    target_dir = Path(args.target).resolve()
    exported = copy_export_bundle(target_dir, clean=args.clean)
    print(f"Exported {len(exported)} files to {target_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
