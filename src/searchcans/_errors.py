"""Exceptions raised by the SearchCans SDK."""

from collections.abc import Mapping
from typing import Any, Optional


class SearchCansError(Exception):
    """Base class for all SDK errors."""


class TransportError(SearchCansError):
    """The HTTP client could not reach SearchCans or finish a request."""


class ResponseFormatError(SearchCansError):
    """SearchCans returned a response that was not a valid API envelope."""


class HTTPStatusError(SearchCansError):
    """SearchCans returned a non-success HTTP status without an API error envelope."""

    def __init__(self, status_code: int, message: str, request_id: Optional[str] = None) -> None:
        super().__init__(f"HTTP {status_code}: {message}")
        self.status_code = status_code
        self.message = message
        self.request_id = request_id


class APIError(SearchCansError):
    """SearchCans returned an API envelope with a non-zero code."""

    def __init__(
        self,
        code: int,
        message: str,
        request_id: Optional[str] = None,
        payload: Optional[Mapping[str, Any]] = None,
    ) -> None:
        super().__init__(f"SearchCans API error {code}: {message}")
        self.code = code
        self.message = message
        self.request_id = request_id
        self.payload = payload


class AuthenticationError(APIError):
    """The API key is invalid, expired, or lacks access to the requested resource."""


class InsufficientCreditsError(APIError):
    """The account does not have enough credits to complete the request."""


class ConcurrencyLimitError(APIError):
    """The account has exceeded the endpoint's concurrent request capacity."""
