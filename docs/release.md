# Release process

## Before the first PyPI release

1. Create the `searchcans` project on PyPI using the intended version, or publish it once from an authorized maintainer account.
2. In PyPI, configure a **Trusted Publisher** for repository `SearchCans/searchcans-python`, workflow file `.github/workflows/publish-pypi.yml`, and environment `pypi`.
3. In GitHub, protect the `pypi` environment with the approvers your team requires.

No PyPI API token should be stored in this repository.

## Release a version

1. Update the version in `pyproject.toml`, `src/searchcans/__init__.py`, and `CHANGELOG.md`.
2. Run `python -m pytest`, `ruff check .`, `python -m build`, and `mkdocs build --strict` locally.
3. Merge the release commit to `main`.
4. Create and push an annotated tag such as `v0.1.0`.
5. The `Create GitHub Release` workflow verifies the package, builds distributions, and creates a GitHub Release with generated notes.
6. Use the manual **Publish to PyPI** workflow, selecting that exact tag. Approve the `pypi` environment when prompted.
7. Verify `pip install searchcans==<version>` in a clean environment and add the PyPI installation command to release communications.
