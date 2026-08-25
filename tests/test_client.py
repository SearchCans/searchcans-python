import asyncio
import json
import re
from pathlib import Path
from typing import Any

import httpx
import pytest

from searchcans import (
    AsyncSearchCans,
    AuthenticationError,
    ConcurrencyLimitError,
    InsufficientCreditsError,
    SearchCans,
    __version__,
)


def success_response(data: dict[str, Any]) -> dict[str, Any]:
    return {"code": 0, "data": data, "msg": "success", "requestId": "req_123"}


def sync_client(handler: Any) -> SearchCans:
    transport = httpx.MockTransport(handler)
    return SearchCans(
        api_key="test-key",
        base_url="https://api.example.test",
        http_client=httpx.Client(transport=transport),
    )


def request_json(request: httpx.Request) -> dict[str, Any]:
    return json.loads(request.content.decode("utf-8"))


def test_account_parses_credit_and_lane_fields() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/user/key"
        assert request.headers["authorization"] == "Bearer test-key"
        assert request.headers["user-agent"] == f"searchcans-python/{__version__}"
        return httpx.Response(
            200,
            json=success_response(
                {"remain": 998, "concurrent": 3, "keys": [{"name": "primary", "active": True}]}
            ),
        )

    client = sync_client(handler)
    account = client.account.get().data

    assert account.remain == 998
    assert account.concurrent == 3
    assert account.keys[0].name == "primary"
    client.close()


def test_google_batch_pages_uses_only_the_safe_page_parameter() -> None:
    observed: list[dict[str, Any]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        observed.append(request_json(request))
        return httpx.Response(200, json=success_response({"organic": []}))

    client = sync_client(handler)
    client.serp.search("research agents", country="us", language="en", pages=2)

    assert observed == [
        {"t": "google", "s": "research agents", "country": "us", "language": "en", "page": 2}
    ]
    client.close()


def test_serp_timeout_and_raw_html_map_to_documented_parameters() -> None:
    observed: list[dict[str, Any]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        observed.append(request_json(request))
        return httpx.Response(200, json=success_response({"organic": []}))

    client = sync_client(handler)
    client.serp.search("research agents", timeout_ms=20000, include_html=True)

    assert observed == [{"t": "google", "s": "research agents", "d": 20000, "html": 1}]
    client.close()


def test_serp_rejects_non_positive_timeout_before_a_request() -> None:
    client = sync_client(lambda request: pytest.fail("request should not be sent"))

    with pytest.raises(ValueError, match="timeout_ms must be positive"):
        client.serp.search("research agents", timeout_ms=0)
    client.close()


def test_runtime_version_matches_package_metadata() -> None:
    root = Path(__file__).resolve().parents[1]
    metadata = (root / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'^version = "([^"]+)"$', metadata, flags=re.MULTILINE)

    assert match is not None
    assert __version__ == match.group(1)


def test_non_google_batch_pages_are_rejected_before_a_request() -> None:
    client = sync_client(lambda request: pytest.fail("request should not be sent"))

    with pytest.raises(ValueError, match="only for engine='google'"):
        client.serp.search("research agents", engine="bing", pages=2)
    client.close()


def test_reader_file_and_screenshot_options_map_to_documented_payloads() -> None:
    observed: list[dict[str, Any]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        observed.append(request_json(request))
        return httpx.Response(200, json=success_response({"markdown": "ok"}))

    client = sync_client(handler)
    client.reader.extract_file("https://example.com/report.pdf", timeout_ms=60000)
    client.reader.screenshot("https://example.com", full_page=True, wait_ms=1000)

    assert observed == [
        {"t": "url", "s": "https://example.com/report.pdf", "d": 60000, "file": 1},
        {"t": "url", "s": "https://example.com", "mode": 1, "w": 1000, "image": 2},
    ]
    client.close()


@pytest.mark.parametrize(
    ("code", "error_type"),
    [
        (401, AuthenticationError),
        (402, InsufficientCreditsError),
        (1009, ConcurrencyLimitError),
        (1010, ConcurrencyLimitError),
    ],
)
def test_api_envelope_errors_are_typed(code: int, error_type: type) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"code": code, "msg": "not available", "data": {}})

    client = sync_client(handler)
    with pytest.raises(error_type):
        client.serp.search("test")
    client.close()


def test_http_lane_limit_is_typed_as_concurrency_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, json={"code": 429, "msg": "All lanes are occupied"})

    client = sync_client(handler)
    with pytest.raises(ConcurrencyLimitError):
        client.serp.search("test")
    client.close()


def test_non_json_http_lane_limit_is_typed_as_concurrency_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, text="All lanes are occupied")

    client = sync_client(handler)
    with pytest.raises(ConcurrencyLimitError):
        client.serp.search("test")
    client.close()


def test_async_client_uses_the_same_safe_payload() -> None:
    async def run() -> None:
        observed: list[dict[str, Any]] = []

        async def handler(request: httpx.Request) -> httpx.Response:
            observed.append(request_json(request))
            return httpx.Response(200, json=success_response({"organic": []}))

        transport = httpx.MockTransport(handler)
        async with AsyncSearchCans(
            api_key="test-key",
            base_url="https://api.example.test",
            http_client=httpx.AsyncClient(transport=transport),
        ) as client:
            response = await client.serp.search("research agents", pages=2)
            assert response.request_id == "req_123"
        assert observed == [{"t": "google", "s": "research agents", "page": 2}]

    asyncio.run(run())
