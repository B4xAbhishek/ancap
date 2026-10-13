from pathlib import Path


STATUS_PATH = Path("STATUS.md")


def test_status_docs_clear_false_readme_and_monetization_blockers():
    status_text = STATUS_PATH.read_text(encoding="utf-8")
    roadmap_text = Path("MASTER_ROADMAP.md").read_text(encoding="utf-8")
    status_matrix = Path("docs/STATUS_MATRIX.md").read_text(encoding="utf-8")

    assert Path("README.md").is_file()
    assert Path("LICENSE").is_file()
    assert Path("CONTRIBUTING.md").is_file()
    assert Path("SECURITY.md").is_file()
    assert Path("CODE_OF_CONDUCT.md").is_file()

    assert "Work-stop blockers: none" in status_text
    assert "Work-stop blockers: none" in roadmap_text
    assert "Work-stop blockers: none" in status_matrix
    assert "add `README.md`, `LICENSE`" not in roadmap_text
    assert "[x] `README.md`, `LICENSE`, `CONTRIBUTING.md`, `SECURITY.md`, and `CODE_OF_CONDUCT.md` in the repo root" in roadmap_text
    assert "do **not** report missing `README.md`" in status_text
    assert "do **not** report missing `README.md`" in roadmap_text
    assert "Do **not** report “monetization after the first ACP cycle” as a blocker" in status_text
    assert "Do **not** report “monetization after the first ACP cycle” as a blocker" in roadmap_text
    assert "monetization depth after the first ACP-first revenue loop" not in status_text
    assert "deepening monetization after the first ACP-first revenue loop" not in roadmap_text


def test_status_summary_keeps_ancap_docs_live_followup_truth_explicit():
    status_text = STATUS_PATH.read_text(encoding="utf-8")

    assert "https://github.com/ancapcloud/ancap-docs" in status_text
    assert "scripts/generate_ancap_docs_live_followup.py" in status_text
    assert "tmp/ancap-docs-live-follow-up-latest.md" in status_text
    assert "tmp/ancap-docs-live-follow-up-latest.json" in status_text
    assert "filename components instead of path fragments" in status_text
    assert "--fail-on-not-ok" in status_text
    assert "exit code `2`" in status_text or "exits with code `2`" in status_text
    assert "General` / `Polls`" in status_text
    assert "Announcements` / `Ideas` / `Q&A` / `Show and tell`" in status_text
    assert "read:project" in status_text
    assert "pinning" in status_text or "pinning," in status_text
