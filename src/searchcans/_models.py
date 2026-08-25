"""Small, stable models for SearchCans API envelopes and account data."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import Any, Callable, Generic, Optional, TypeVar

T = TypeVar("T")
U = TypeVar("U")


class SearchEngine(str, Enum):
    """SERP engines currently exposed by the SearchCans API."""

    GOOGLE = "google"
    BING = "bing"
    GOOGLE_NEWS = "google_news"
    GOOGLE_SHOPPING = "google_shopping"
    GOOGLE_IMAGES = "google_images"
    GOOGLE_VIDEOS = "google_videos"
    GOOGLE_SHORT_VIDEOS = "google_short_videos"


class ProxyTier(IntEnum):
    """Reader proxy tiers. Higher tiers can consume additional credits."""

    DIRECT = 0
    SHARED = 1
    DATACENTER = 2
    RESIDENTIAL = 3


class ScreenshotMode(IntEnum):
    """Reader screenshot capture modes."""

    VIEWPORT = 1
    FULL_PAGE = 2


@dataclass(frozen=True)
class APIResponse(Generic[T]):
    """A successful SearchCans response envelope."""

    code: int
    data: T
    message: str
    request_id: Optional[str] = None
    raw: Mapping[str, Any] = field(default_factory=dict, repr=False)

    def map(self, transform: Callable[[T], U]) -> "APIResponse[U]":
        """Return an equivalent envelope with its data transformed."""

        return APIResponse(
            code=self.code,
            data=transform(self.data),
            message=self.message,
            request_id=self.request_id,
            raw=self.raw,
        )


@dataclass(frozen=True)
class APIKey:
    """A key entry returned by the Account API."""

    name: Optional[str]
    active: Optional[bool]
    total: Optional[int]
    remain: Optional[int]
    id: Optional[str]

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "APIKey":
        return cls(
            name=_optional_str(value.get("name")),
            active=_optional_bool(value.get("active")),
            total=_optional_int(value.get("total")),
            remain=_optional_int(value.get("remain")),
            id=_optional_str(value.get("id")),
        )


@dataclass(frozen=True)
class Account:
    """Stable account fields useful for request and credit planning."""

    remain: Optional[int]
    concurrent: Optional[int]
    total: Optional[int]
    current: Optional[int]
    month: Optional[int]
    permanent_remain: Optional[int]
    keys: list[APIKey]
    nickname: Optional[str]
    email: Optional[str]
    raw: Mapping[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "Account":
        key_values = value.get("keys")
        if isinstance(key_values, list):
            keys = [APIKey.from_mapping(key) for key in key_values if isinstance(key, Mapping)]
        else:
            keys = []
        return cls(
            remain=_optional_int(value.get("remain")),
            concurrent=_optional_int(value.get("concurrent")),
            total=_optional_int(value.get("total")),
            current=_optional_int(value.get("current")),
            month=_optional_int(value.get("month")),
            permanent_remain=_optional_int(value.get("permanentRemain")),
            keys=keys,
            nickname=_optional_str(value.get("nickName")),
            email=_optional_str(value.get("email")),
            raw=dict(value),
        )


def _optional_int(value: Any) -> Optional[int]:
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _optional_bool(value: Any) -> Optional[bool]:
    return value if isinstance(value, bool) else None


def _optional_str(value: Any) -> Optional[str]:
    return value if isinstance(value, str) else None
