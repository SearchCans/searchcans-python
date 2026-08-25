"""Synchronous and asynchronous HTTP clients for SearchCans."""

from collections.abc import Mapping
from typing import Any, Callable, Optional

import httpx

from ._errors import (
    APIError,
    AuthenticationError,
    ConcurrencyLimitError,
    HTTPStatusError,
    InsufficientCreditsError,
    ResponseFormatError,
    TransportError,
)
from ._models import APIResponse
from ._services import (
    AccountService,
    AsyncAccountService,
    AsyncReaderService,
    AsyncSerpService,
    ReaderService,
    SerpService,
)

DEFAULT_BASE_URL = "https://www.searchcans.com"


def _headers(api_key: str) -> Mapping[str, str]:
    if not api_key.strip():
        raise ValueError("api_key must not be empty")
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "searchcans-python/0.1.0",
    }


def _error_from_payload(payload: Mapping[str, Any]) -> APIError:
    code = payload.get("code")
    message = payload.get("msg")
    request_id = payload.get("requestId")
    safe_code = code if isinstance(code, int) else -1
    safe_message = message if isinstance(message, str) else "Unknown SearchCans API error"
    safe_request_id = request_id if isinstance(request_id, str) else None
    error_type: Callable[..., APIError]
    if safe_code in {401, 403, -2008}:
        error_type = AuthenticationError
    elif safe_code == 402:
        error_type = InsufficientCreditsError
    elif safe_code == 1009:
        error_type = ConcurrencyLimitError
    else:
        error_type = APIError
    return error_type(safe_code, safe_message, safe_request_id, payload)


def _decode_response(response: httpx.Response) -> APIResponse[Mapping[str, Any]]:
    try:
        payload = response.json()
    except ValueError as error:
        if not response.is_success:
            raise HTTPStatusError(response.status_code, response.text[:500]) from error
        raise ResponseFormatError("SearchCans returned invalid JSON") from error
    if not isinstance(payload, Mapping):
        raise ResponseFormatError("SearchCans response must be a JSON object")

    code = payload.get("code")
    if isinstance(code, int) and code != 0:
        raise _error_from_payload(payload)
    if not response.is_success:
        message = payload.get("msg")
        raise HTTPStatusError(
            response.status_code,
            message if isinstance(message, str) else "Unexpected HTTP response",
            payload.get("requestId") if isinstance(payload.get("requestId"), str) else None,
        )
    if not isinstance(code, int):
        raise ResponseFormatError("SearchCans response is missing an integer 'code'")

    data = payload.get("data")
    if not isinstance(data, Mapping):
        raise ResponseFormatError("SearchCans success response must contain an object 'data'")
    message = payload.get("msg")
    request_id = payload.get("requestId")
    return APIResponse(
        code=code,
        data=data,
        message=message if isinstance(message, str) else "",
        request_id=request_id if isinstance(request_id, str) else None,
        raw=dict(payload),
    )


class SearchCans:
    """Synchronous client for the SearchCans SERP, Reader, and Account APIs."""

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
        http_client: Optional[httpx.Client] = None,
    ) -> None:
        self._owns_client = http_client is None
        self._http = http_client or httpx.Client(timeout=timeout)
        self._base_url = base_url.rstrip("/")
        self._request_headers = _headers(api_key)
        self.serp = SerpService(self._post)
        self.reader = ReaderService(self._post)
        self.account = AccountService(self._post)

    def _post(self, path: str, payload: Mapping[str, Any]) -> APIResponse[Mapping[str, Any]]:
        try:
            response = self._http.post(
                f"{self._base_url}{path}", headers=self._request_headers, json=dict(payload)
            )
        except httpx.HTTPError as error:
            raise TransportError(f"SearchCans request failed: {error}") from error
        return _decode_response(response)

    def close(self) -> None:
        """Close the underlying HTTP client when it is owned by this SDK instance."""

        if self._owns_client:
            self._http.close()

    def __enter__(self) -> "SearchCans":
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.close()


class AsyncSearchCans:
    """Asynchronous client for the SearchCans SERP, Reader, and Account APIs."""

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
        http_client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        self._owns_client = http_client is None
        self._http = http_client or httpx.AsyncClient(timeout=timeout)
        self._base_url = base_url.rstrip("/")
        self._request_headers = _headers(api_key)
        self.serp = AsyncSerpService(self._post)
        self.reader = AsyncReaderService(self._post)
        self.account = AsyncAccountService(self._post)

    async def _post(self, path: str, payload: Mapping[str, Any]) -> APIResponse[Mapping[str, Any]]:
        try:
            response = await self._http.post(
                f"{self._base_url}{path}", headers=self._request_headers, json=dict(payload)
            )
        except httpx.HTTPError as error:
            raise TransportError(f"SearchCans request failed: {error}") from error
        return _decode_response(response)

    async def aclose(self) -> None:
        """Close the underlying HTTP client when it is owned by this SDK instance."""

        if self._owns_client:
            await self._http.aclose()

    async def __aenter__(self) -> "AsyncSearchCans":
        return self

    async def __aexit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        await self.aclose()
