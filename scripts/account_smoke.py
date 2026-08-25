"""Opt-in live Account API smoke test for maintainers.

Run this locally with SEARCHCANS_API_KEY set. It sends no SERP or Reader
request and prints no account data or credentials.
"""

import os

from searchcans import SearchCans, SearchCansError


def main() -> None:
    api_key = os.environ.get("SEARCHCANS_API_KEY")
    if not api_key:
        raise SystemExit("Set SEARCHCANS_API_KEY before running this smoke test.")

    try:
        with SearchCans(api_key=api_key) as client:
            account = client.account.get().data
    except SearchCansError as error:
        raise SystemExit("Account smoke test failed.") from error

    if account.remain is None or account.concurrent is None:
        raise SystemExit("Account smoke test failed: required account fields were not returned.")

    print("LIVE_ACCOUNT_SMOKE_OK")


if __name__ == "__main__":
    main()
