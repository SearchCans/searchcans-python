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
6. Run `python scripts/validate_release.py --tag v0.1.0` locally. The check requires an annotated tag at `HEAD` whose version matches `pyproject.toml`.
7. The `Create GitHub Release` workflow repeats the SDK, generated Wiki, tag, package, and distribution checks before creating a GitHub Release with generated notes.
8. Use the manual **Publish to PyPI** workflow, selecting that exact tag. It repeats the annotated-tag/version check. Approve the `pypi` environment when prompted.
9. Verify `pip install searchcans==<version>` in a clean environment and add the PyPI installation command to release communications.

## GitHub Wiki

The Wiki is generated from the Markdown files in `docs/`. Do not hand-edit generated pages. To initialize it once, create any `Home` page from the repository's **Wiki** tab, then add the repository secret `WIKI_SYNC_TOKEN` with a classic PAT that can push to `SearchCans/searchcans-python.wiki`.

After that, run **Sync generated GitHub Wiki** once from GitHub Actions. Later changes to `docs/*.md` automatically regenerate and synchronize the generated Wiki pages. The sync script preserves Wiki pages that are not listed in `.searchcans-generated-pages`.
