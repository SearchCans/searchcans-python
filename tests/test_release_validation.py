import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_release import validate_release_tag  # noqa: E402


def git(repository: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repository,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


def release_repository(tmp_path: Path, version: str = "0.1.0") -> Path:
    repository = tmp_path / "release-repository"
    repository.mkdir()
    git(repository, "init")
    git(repository, "config", "user.name", "SearchCans Test")
    git(repository, "config", "user.email", "sdk-test@example.invalid")
    (repository / "pyproject.toml").write_text(
        f'[project]\nname = "searchcans"\nversion = "{version}"\n', encoding="utf-8"
    )
    git(repository, "add", "pyproject.toml")
    git(repository, "commit", "-m", "release candidate")
    return repository


def test_annotated_matching_tag_is_valid(tmp_path: Path) -> None:
    repository = release_repository(tmp_path)
    git(repository, "tag", "-a", "v0.1.0", "-m", "release")

    validate_release_tag(repository, "v0.1.0")


def test_lightweight_tag_is_rejected(tmp_path: Path) -> None:
    repository = release_repository(tmp_path)
    git(repository, "tag", "v0.1.0")

    with pytest.raises(ValueError, match="annotated"):
        validate_release_tag(repository, "v0.1.0")


def test_version_mismatch_is_rejected(tmp_path: Path) -> None:
    repository = release_repository(tmp_path)
    git(repository, "tag", "-a", "v0.1.1", "-m", "wrong version")

    with pytest.raises(ValueError, match="does not match"):
        validate_release_tag(repository, "v0.1.1")
