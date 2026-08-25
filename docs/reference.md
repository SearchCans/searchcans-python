# API reference

## `SearchCans` and `AsyncSearchCans`

```python
SearchCans(api_key: str, base_url: str = "https://www.searchcans.com", timeout: float = 30.0)
```

Both clients expose `serp`, `reader`, and `account`. Use a context manager so the HTTP connection closes cleanly.

## `client.serp.search`

```python
client.serp.search(
    query,
    engine="google",
    country=None,
    language=None,
    pages=1,
    timeout_ms=None,
    include_html=False,
    knowledge_graph=False,
    people_also_ask=False,
    ai_summary=False,
    news_aggregation=False,
    video_aggregation=False,
    people_also_search_for=False,
)
```

Supported engines are `google`, `bing`, `google_news`, `google_shopping`, `google_images`, `google_videos`, and `google_short_videos`.

`pages > 1` is accepted only for `google`. The SDK rejects it for Bing and Google vertical engines rather than send an ambiguous request.

`timeout_ms` maps to the API's `d` parameter. Set `include_html=True` only when you need raw SERP HTML; otherwise the SDK omits it to keep responses smaller.

## `client.reader`

```python
client.reader.extract(
    url,
    render_js=False,
    wait_ms=None,
    timeout_ms=None,
    include_html=False,
    proxy=0,
    solve_captcha=False,
)
client.reader.extract_file(url, timeout_ms=None, proxy=0)
client.reader.screenshot(url, full_page=False, wait_ms=None, timeout_ms=None, proxy=0)
```

`ProxyTier.SHARED`, `ProxyTier.DATACENTER`, and `ProxyTier.RESIDENTIAL` are explicit because they can increase credit cost. `screenshot(..., full_page=True)` requests full-page capture; the default requests the first viewport.

## `client.account.get`

Returns `APIResponse[Account]`. The stable fields include `remain`, `concurrent`, account totals, and key metadata. The original response remains available as `response.raw` and `account.raw` for forward compatibility.

## Errors

| Error | Meaning |
| --- | --- |
| `AuthenticationError` | Invalid key, expired key, or denied resource. |
| `InsufficientCreditsError` | Not enough credits for the request. |
| `ConcurrencyLimitError` | Too many concurrent calls (`1009`, `1010`, or HTTP `429`). |
| `HTTPStatusError` | Non-success HTTP response without a usable API envelope. |
| `ResponseFormatError` | Unexpected response JSON shape. |
| `TransportError` | Network or HTTP-client failure. |
