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
