#!/usr/bin/env python3
"""Validate that a release tag is annotated and matches the package version."""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def git_output(repository: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=repository, text=True, capture_output=True, check=False
    )
    if result.returncode:
        raise ValueError(result.stderr.strip() or "Git release validation failed")
    return result.stdout.strip()


def package_version(repository: Path) -> str:
    metadata = (repository / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'^version = "([^"]+)"$', metadata, flags=re.MULTILINE)
    if match is None:
        raise ValueError("Could not read package version from pyproject.toml")
    return match.group(1)


def validate_release_tag(repository: Path, tag: str) -> None:
    if not re.fullmatch(r"v[0-9][0-9A-Za-z.+!-]*", tag):
        raise ValueError("Release tag must look like v0.1.0")
    try:
        tag_type = git_output(repository, "cat-file", "-t", f"refs/tags/{tag}")
    except ValueError as error:
        raise ValueError(f"Release tag does not exist: {tag}") from error
    if tag_type != "tag":
        raise ValueError(f"Release tag must be annotated: {tag}")
    if git_output(repository, "rev-parse", f"{tag}^{{commit}}") != git_output(
        repository, "rev-parse", "HEAD"
    ):
        raise ValueError(f"Release tag does not point to HEAD: {tag}")
    if tag.removeprefix("v") != package_version(repository):
        raise ValueError(f"Release tag {tag} does not match the package version")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", required=True, help="Annotated release tag, for example v0.1.0")
    parser.add_argument("--repository", type=Path, default=ROOT, help=argparse.SUPPRESS)
    args = parser.parse_args()
    validate_release_tag(args.repository.resolve(), args.tag)
    print(f"Release tag is valid: {args.tag}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
