"""Official Python SDK for the SearchCans SERP API and Reader API."""

from ._client import AsyncSearchCans, SearchCans
from ._errors import (
    APIError,
    AuthenticationError,
    ConcurrencyLimitError,
    HTTPStatusError,
    InsufficientCreditsError,
    ResponseFormatError,
    SearchCansError,
    TransportError,
)
from ._models import Account, APIKey, APIResponse, ProxyTier, ScreenshotMode, SearchEngine
from ._version import __version__

__all__ = [
    "APIError",
    "APIKey",
    "APIResponse",
    "Account",
    "AsyncSearchCans",
    "AuthenticationError",
    "ConcurrencyLimitError",
    "HTTPStatusError",
    "InsufficientCreditsError",
    "ProxyTier",
    "ResponseFormatError",
    "ScreenshotMode",
    "SearchCans",
    "SearchCansError",
    "SearchEngine",
    "TransportError",
    "__version__",
]
