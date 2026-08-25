# Account-aware usage

SearchCans accounts expose two useful controls before a batch job:

- `account.remain`: available credits.
- `account.concurrent`: parallel lane slots.

Use the account response to decide whether to proceed; do not expose key values or account email addresses in logs or generated reports.

```python
from searchcans import SearchCans


def can_start(client: SearchCans, minimum_credits: int) -> bool:
    account = client.account.get().data
    return (account.remain or 0) >= minimum_credits
```

The SDK intentionally has no automatic retry policy. A caller should choose retries, backoff, source budgets, and concurrency limits for its own workload after accounting for credit costs and duplicate-request risk.

For Reader, start with direct extraction. Use browser rendering, CAPTCHA handling, or an elevated proxy tier only when the target requires it.

## Maintainer smoke test

After unit tests pass and before a release, a maintainer can verify the live Account API without issuing a SERP or Reader request:

```bash
export SEARCHCANS_API_KEY="your_api_key"
python scripts/account_smoke.py
```

The script prints only `LIVE_ACCOUNT_SMOKE_OK`. It does not print the key, email address, credit balance, API-key list, or raw response. It is deliberately not part of GitHub Actions because it requires a live credential.
