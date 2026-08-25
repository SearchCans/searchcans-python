# Quickstart

```python
import os

from searchcans import SearchCans


with SearchCans(api_key=os.environ["SEARCHCANS_API_KEY"]) as client:
    account = client.account.get().data
    print(account.remain, account.concurrent)

    serp = client.serp.search(
        "deep research agent",
        engine="google",
        country="us",
        language="en",
        pages=2,
        people_also_ask=True,
    )
    print(serp.data)

    page = client.reader.extract("https://www.searchcans.com/reader-api/", render_js=True)
    print(page.data.get("markdown", "")[:300])
```

## Async applications

```python
import os

from searchcans import AsyncSearchCans


async def research() -> None:
    async with AsyncSearchCans(api_key=os.environ["SEARCHCANS_API_KEY"]) as client:
        response = await client.serp.search("RAG source curation", country="us", language="en")
        print(response.data)
```

## Keep pagination unambiguous

Use `pages` only for a Google Search batch. The SDK maps `pages=2` to the raw API's `page: 2` field and does not expose raw `p`.

This may return data from multiple upstream pages. Positions are page-local, so keep the result item's own page label when comparing records.
