# SearchCans Python SDK

Official Python SDK for the [SearchCans SERP API](https://www.searchcans.com/google-search-api/) and [Reader API](https://www.searchcans.com/reader-api/).

[Visit SearchCans](https://www.searchcans.com/) for API access, product information, and developer resources.

Build account-aware search, research, SEO/GEO, and RAG applications with one small client. The SDK supports Google, Bing, Google verticals, web extraction, document extraction, screenshots, and account pre-flight checks.

> The verified `main` branch is available now. The `v0.1.0` GitHub Release and PyPI package will be created after final release approval.

```bash
pip install "git+https://github.com/SearchCans/searchcans-python.git@main"
```

After PyPI publication:

```bash
pip install searchcans
```

## Quick start

Create an API key in the [SearchCans dashboard](https://www.searchcans.com/dashboard/) and keep it in an environment variable.

```python
import os

from searchcans import SearchCans

with SearchCans(api_key=os.environ["SEARCHCANS_API_KEY"]) as client:
    account = client.account.get().data
    print(f"{account.remain} credits; {account.concurrent} parallel lanes")

    results = client.serp.search(
        "deep research agent",
        engine="google",
        country="us",
        language="en",
        pages=2,
        people_also_ask=True,
    )

    page = client.reader.extract("https://www.searchcans.com/reader-api/")
    print(page.data.get("title"))
```

## Safe pagination

The raw SERP API has two similarly named parameters. This SDK deliberately exposes only `pages`:

- `pages=2` sends the documented `page: 2` batch request for **Google Search**.
- It may return results from more than one upstream page. Preserve the API's per-item page label; result positions are page-local.
- The SDK does not expose raw `p`, and it rejects batch pages for Bing and Google vertical engines. This prevents ambiguous or unsupported requests.

## Reader API

```python
document = client.reader.extract_file("https://example.com/report.pdf")
image = client.reader.screenshot("https://example.com", full_page=True)
```

Use direct extraction first. Browser rendering and paid proxy tiers are explicit options so applications can control latency and credit use.

## Async client

```python
import os

from searchcans import AsyncSearchCans


async def main() -> None:
    async with AsyncSearchCans(api_key=os.environ["SEARCHCANS_API_KEY"]) as client:
        response = await client.serp.search("RAG source curation", country="us", language="en")
        print(response.data)
```

## Errors and request control

The client raises typed errors for authentication, insufficient credits, concurrency limits, invalid API envelopes, and transport failures. It performs no automatic retry by default: a request can be billable, so retry policy belongs to the calling application.

Call `client.account.get()` before material batch work and use `Account.remain` and `Account.concurrent` to size the job.

## Documentation and maintenance

- [Documentation](https://searchcans.github.io/searchcans-python/)
- [Contributing](CONTRIBUTING.md)
- [Security policy](SECURITY.md)
- [Release process](docs/release.md)

## License

Apache-2.0. See [LICENSE](LICENSE).
