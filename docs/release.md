# Release process

## Before the first PyPI release

1. In the PyPI account sidebar, open **Publishing** and create a **pending GitHub Actions Trusted Publisher** for project name `searchcans`.
2. Set repository owner to `SearchCans`, repository name to `searchcans-python`, workflow filename to `publish-pypi.yml`, and environment name to `pypi`.
3. In GitHub, protect the `pypi` environment with the approvers your team requires. The first approved publication converts the pending publisher into the normal publisher and creates the PyPI project.

No PyPI API token should be stored in this repository.

## Release a version

1. Update the version in `pyproject.toml`, `src/searchcans/_version.py`, and `CHANGELOG.md`.
2. Run `python -m pytest`, `ruff check .`, `python -m build`, and `mkdocs build --strict` locally.
3. With an authorized local API key, run `python scripts/account_smoke.py`. Do not add the key to GitHub Actions.
4. Merge the release commit to `main`.
5. Create and push an annotated tag such as `v0.1.0`.
6. The `Create GitHub Release` workflow verifies the package, builds distributions, and creates a GitHub Release with generated notes.
7. Use the manual **Publish to PyPI** workflow, selecting that exact tag. It rejects branches, lightweight tags, and tags whose version does not match `pyproject.toml`. Approve the `pypi` environment when prompted.
8. Verify `pip install searchcans==<version>` in a clean environment and add the PyPI installation command to release communications.
