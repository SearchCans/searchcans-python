#!/usr/bin/env python3
"""Generate the SDK GitHub Wiki from the maintained Markdown documentation."""

from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WIKI_DIR = ROOT / "docs" / "generated" / "wiki"
MANIFEST = ".searchcans-generated-pages"


def home() -> str:
    return """# SearchCans Python SDK

> Official Python client for the SearchCans SERP API, Reader API, and Account API.

Build account-aware search, research, SEO/GEO, and RAG applications with explicit request controls
and typed errors.

## Install

Until the first PyPI release, install the verified main branch:

```bash
pip install "git+https://github.com/SearchCans/searchcans-python.git@main"
```

Keep `SEARCHCANS_API_KEY` in an environment variable. Never put a key in a prompt, source file,
report, issue, or commit.

## Start here

- [Getting Started](Getting-Started)
- [API Reference](API-Reference)
- [Account-Aware Usage](Account-Aware-Usage)
- [Release and Maintenance](Releases)

[Visit SearchCans](https://www.searchcans.com/) ·
[API documentation](https://www.searchcans.com/apis/) ·
[SDK documentation site](https://searchcans.github.io/searchcans-python/)

[Source repository](https://github.com/SearchCans/searchcans-python)
"""


def sidebar() -> str:
    return """## SearchCans Python SDK

- [Home](Home)
- [Getting Started](Getting-Started)
- [API Reference](API-Reference)
- [Account-Aware Usage](Account-Aware-Usage)
- [Release and Maintenance](Releases)
"""


def outputs() -> dict[str, str]:
    source_pages = {
        "Getting-Started.md": "quickstart.md",
        "API-Reference.md": "reference.md",
        "Account-Aware-Usage.md": "account-aware.md",
        "Releases.md": "release.md",
    }
    pages = {"Home.md": home(), "_Sidebar.md": sidebar()}
    pages.update(
        {
            target: (ROOT / "docs" / source).read_text(encoding="utf-8")
            for target, source in source_pages.items()
        }
    )
    return pages


def write_or_check(pages: dict[str, str], check: bool) -> list[Path]:
    expected = {**pages, MANIFEST: "\n".join(sorted(pages)) + "\n"}
    changed: list[Path] = []
    for name, content in expected.items():
        path = WIKI_DIR / name
        if not path.is_file() or path.read_text(encoding="utf-8") != content:
            changed.append(path)
            if not check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
    return changed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="Fail if generated Wiki pages are stale."
    )
    args = parser.parse_args()
    changed = write_or_check(outputs(), args.check)
    if args.check and changed:
        print("Generated Wiki pages are stale:")
        print("\n".join(str(path.relative_to(ROOT)) for path in changed))
        return 1
    print(f"SDK Wiki pages are {'current' if args.check else 'generated'}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
