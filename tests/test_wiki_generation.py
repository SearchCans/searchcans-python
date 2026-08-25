import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from sync_wiki import synchronize  # noqa: E402


def test_generated_wiki_is_current_and_has_the_expected_navigation() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/generate_wiki.py", "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    home = (ROOT / "docs" / "generated" / "wiki" / "Home.md").read_text(encoding="utf-8")
    sidebar = (ROOT / "docs" / "generated" / "wiki" / "_Sidebar.md").read_text(encoding="utf-8")
    assert "[API Reference](API-Reference)" in home
    assert "[Release and Maintenance](Releases)" in sidebar


def test_wiki_sync_replaces_only_previously_generated_pages(tmp_path: Path) -> None:
    source = ROOT / "docs" / "generated" / "wiki"
    target = tmp_path / "wiki"
    target.mkdir()
    (target / ".searchcans-generated-pages").write_text("Stale.md\n", encoding="utf-8")
    (target / "Stale.md").write_text("stale\n", encoding="utf-8")
    (target / "Manual.md").write_text("keep me\n", encoding="utf-8")

    synchronize(source, target)

    assert not (target / "Stale.md").exists()
    assert (target / "Home.md").read_text(encoding="utf-8") == (source / "Home.md").read_text(
        encoding="utf-8"
    )
    assert (target / "Manual.md").read_text(encoding="utf-8") == "keep me\n"
