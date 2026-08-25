"""Endpoint groups shared by the synchronous and asynchronous clients."""

from collections.abc import Mapping
from typing import Any, Optional, Union

from ._models import Account, APIResponse, ProxyTier, ScreenshotMode, SearchEngine


def build_serp_payload(
    query: str,
    engine: Union[SearchEngine, str],
    country: Optional[str],
    language: Optional[str],
    pages: int,
    knowledge_graph: bool,
    people_also_ask: bool,
    ai_summary: bool,
    news_aggregation: bool,
    video_aggregation: bool,
    people_also_search_for: bool,
) -> dict[str, Any]:
    """Build a safe SERP request body from public SDK parameters."""

    if not query.strip():
        raise ValueError("query must not be empty")
    try:
        selected_engine = SearchEngine(engine)
    except ValueError as error:
        values = ", ".join(item.value for item in SearchEngine)
        raise ValueError(f"engine must be one of: {values}") from error
    if pages < 1:
        raise ValueError("pages must be at least 1")
    if pages > 1 and selected_engine is not SearchEngine.GOOGLE:
        raise ValueError("pages > 1 is currently supported only for engine='google'")

    payload: dict[str, Any] = {"t": selected_engine.value, "s": query}
    if country:
        payload["country"] = country
    if language:
        payload["language"] = language
    if pages > 1:
        payload["page"] = pages

    optional_features = {
        "knowledgeGraph": knowledge_graph,
        "peopleAlsoAsk": people_also_ask,
        "aiSummary": ai_summary,
        "newsAggregation": news_aggregation,
        "videoAggregation": video_aggregation,
        "peopleAlsoSearchFor": people_also_search_for,
    }
    payload.update({key: value for key, value in optional_features.items() if value})
    return payload


def build_reader_payload(
    url: str,
    *,
    render_js: bool = False,
    wait_ms: Optional[int] = None,
    timeout_ms: Optional[int] = None,
    include_html: bool = False,
    proxy: Union[ProxyTier, int] = ProxyTier.DIRECT,
    solve_captcha: bool = False,
    file: bool = False,
    screenshot: Optional[ScreenshotMode] = None,
) -> dict[str, Any]:
    """Build a Reader request body and reject invalid option combinations."""

    if not url.strip():
        raise ValueError("url must not be empty")
    if wait_ms is not None and not render_js:
        raise ValueError("wait_ms requires render_js=True")
    if wait_ms is not None and wait_ms < 0:
        raise ValueError("wait_ms must not be negative")
    if timeout_ms is not None and timeout_ms < 1:
        raise ValueError("timeout_ms must be positive")
    try:
        proxy_tier = ProxyTier(proxy)
    except ValueError as error:
        raise ValueError("proxy must be a ProxyTier or an integer from 0 to 3") from error

    payload: dict[str, Any] = {"t": "url", "s": url}
    if render_js:
        payload["mode"] = 1
    if wait_ms is not None:
        payload["w"] = wait_ms
    if timeout_ms is not None:
        payload["d"] = timeout_ms
    if include_html:
        payload["html"] = 1
    if proxy_tier is not ProxyTier.DIRECT:
        payload["proxy"] = int(proxy_tier)
    if solve_captcha:
        payload["captcha"] = 1
    if file:
        payload["file"] = 1
    if screenshot is not None:
        payload["image"] = int(screenshot)
    return payload


class SerpService:
    """Synchronous SERP endpoint group."""

    def __init__(self, post: Any) -> None:
        self._post = post

    def search(
        self,
        query: str,
        *,
        engine: Union[SearchEngine, str] = SearchEngine.GOOGLE,
        country: Optional[str] = None,
        language: Optional[str] = None,
        pages: int = 1,
        knowledge_graph: bool = False,
        people_also_ask: bool = False,
        ai_summary: bool = False,
        news_aggregation: bool = False,
        video_aggregation: bool = False,
        people_also_search_for: bool = False,
    ) -> APIResponse[Mapping[str, Any]]:
        payload = build_serp_payload(
            query,
            engine,
            country,
            language,
            pages,
            knowledge_graph,
            people_also_ask,
            ai_summary,
            news_aggregation,
            video_aggregation,
            people_also_search_for,
        )
        return self._post("/api/v1/search", payload)


class ReaderService:
    """Synchronous Reader endpoint group."""

    def __init__(self, post: Any) -> None:
        self._post = post

    def extract(
        self,
        url: str,
        *,
        render_js: bool = False,
        wait_ms: Optional[int] = None,
        timeout_ms: Optional[int] = None,
        include_html: bool = False,
        proxy: Union[ProxyTier, int] = ProxyTier.DIRECT,
        solve_captcha: bool = False,
    ) -> APIResponse[Mapping[str, Any]]:
        payload = build_reader_payload(
            url,
            render_js=render_js,
            wait_ms=wait_ms,
            timeout_ms=timeout_ms,
            include_html=include_html,
            proxy=proxy,
            solve_captcha=solve_captcha,
        )
        return self._post("/api/v1/url", payload)

    def extract_file(
        self,
        url: str,
        *,
        timeout_ms: Optional[int] = None,
        proxy: Union[ProxyTier, int] = ProxyTier.DIRECT,
    ) -> APIResponse[Mapping[str, Any]]:
        payload = build_reader_payload(url, timeout_ms=timeout_ms, proxy=proxy, file=True)
        return self._post("/api/v1/url", payload)

    def screenshot(
        self,
        url: str,
        *,
        full_page: bool = False,
        wait_ms: Optional[int] = None,
        timeout_ms: Optional[int] = None,
        proxy: Union[ProxyTier, int] = ProxyTier.DIRECT,
    ) -> APIResponse[Mapping[str, Any]]:
        mode = ScreenshotMode.FULL_PAGE if full_page else ScreenshotMode.VIEWPORT
        payload = build_reader_payload(
            url,
            render_js=True,
            wait_ms=wait_ms,
            timeout_ms=timeout_ms,
            proxy=proxy,
            screenshot=mode,
        )
        return self._post("/api/v1/url", payload)


class AccountService:
    """Synchronous account endpoint group."""

    def __init__(self, post: Any) -> None:
        self._post = post

    def get(self) -> APIResponse[Account]:
        return self._post("/api/user/key", {}).map(Account.from_mapping)


class AsyncSerpService:
    """Asynchronous SERP endpoint group."""

    def __init__(self, post: Any) -> None:
        self._post = post

    async def search(
        self,
        query: str,
        *,
        engine: Union[SearchEngine, str] = SearchEngine.GOOGLE,
        country: Optional[str] = None,
        language: Optional[str] = None,
        pages: int = 1,
        knowledge_graph: bool = False,
        people_also_ask: bool = False,
        ai_summary: bool = False,
        news_aggregation: bool = False,
        video_aggregation: bool = False,
        people_also_search_for: bool = False,
    ) -> APIResponse[Mapping[str, Any]]:
        payload = build_serp_payload(
            query,
            engine,
            country,
            language,
            pages,
            knowledge_graph,
            people_also_ask,
            ai_summary,
            news_aggregation,
            video_aggregation,
            people_also_search_for,
        )
        return await self._post("/api/v1/search", payload)


class AsyncReaderService:
    """Asynchronous Reader endpoint group."""

    def __init__(self, post: Any) -> None:
        self._post = post

    async def extract(
        self,
        url: str,
        *,
        render_js: bool = False,
        wait_ms: Optional[int] = None,
        timeout_ms: Optional[int] = None,
        include_html: bool = False,
        proxy: Union[ProxyTier, int] = ProxyTier.DIRECT,
        solve_captcha: bool = False,
    ) -> APIResponse[Mapping[str, Any]]:
        payload = build_reader_payload(
            url,
            render_js=render_js,
            wait_ms=wait_ms,
            timeout_ms=timeout_ms,
            include_html=include_html,
            proxy=proxy,
            solve_captcha=solve_captcha,
        )
        return await self._post("/api/v1/url", payload)

    async def extract_file(
        self,
        url: str,
        *,
        timeout_ms: Optional[int] = None,
        proxy: Union[ProxyTier, int] = ProxyTier.DIRECT,
    ) -> APIResponse[Mapping[str, Any]]:
        payload = build_reader_payload(url, timeout_ms=timeout_ms, proxy=proxy, file=True)
        return await self._post("/api/v1/url", payload)

    async def screenshot(
        self,
        url: str,
        *,
        full_page: bool = False,
        wait_ms: Optional[int] = None,
        timeout_ms: Optional[int] = None,
        proxy: Union[ProxyTier, int] = ProxyTier.DIRECT,
    ) -> APIResponse[Mapping[str, Any]]:
        mode = ScreenshotMode.FULL_PAGE if full_page else ScreenshotMode.VIEWPORT
        payload = build_reader_payload(
            url,
            render_js=True,
            wait_ms=wait_ms,
            timeout_ms=timeout_ms,
            proxy=proxy,
            screenshot=mode,
        )
        return await self._post("/api/v1/url", payload)


class AsyncAccountService:
    """Asynchronous account endpoint group."""

    def __init__(self, post: Any) -> None:
        self._post = post

    async def get(self) -> APIResponse[Account]:
        response = await self._post("/api/user/key", {})
        return response.map(Account.from_mapping)
