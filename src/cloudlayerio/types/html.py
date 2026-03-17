"""HTML option types."""

from __future__ import annotations

from typing_extensions import TypedDict


class HtmlOptions(TypedDict):
    """Options for HTML-based conversions. `html` is required (Base64-encoded)."""

    html: str
