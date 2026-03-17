"""URL-related option types."""

from __future__ import annotations

from typing import Literal

from typing_extensions import TypedDict


class Authentication(TypedDict):
    """HTTP basic authentication credentials."""

    username: str
    password: str


class Batch(TypedDict):
    """Batch URL processing options."""

    urls: list[str]  # Required, 1-20 URLs


class _CookieRequired(TypedDict):
    """Required cookie fields."""

    name: str
    value: str


class Cookie(_CookieRequired, total=False):
    """Browser cookie to set before page load."""

    url: str
    domain: str
    path: str
    expires: int
    http_only: bool
    secure: bool
    same_site: Literal["Strict", "Lax"]


class UrlOptions(TypedDict, total=False):
    """Options for URL-based conversions. `url` and `batch` are mutually exclusive."""

    url: str
    authentication: Authentication
    batch: Batch
    cookies: list[Cookie]
