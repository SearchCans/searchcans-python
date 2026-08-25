# Contributing

Thank you for helping improve the official SearchCans Python SDK.

## Local setup

```bash
python -m venv .venv
. .venv/bin/activate  # Windows PowerShell: .venv\\Scripts\\Activate.ps1
python -m pip install -e ".[dev,docs]"
python -m pytest
ruff check .
mkdocs build --strict
```

## Contribution rules

- Do not commit API keys, account responses, or unredacted API fixtures.
- Add a focused test for every public behavior change.
- Preserve the distinction between Google batch `page` behavior and unsupported raw `p` behavior.
- Do not add automatic retries to billable operations without an explicit product decision and tests.
- Keep response models forward-compatible: unknown fields remain in `raw` rather than being discarded.

Open an issue before a large public API change so maintainers can agree on versioning and documentation.
