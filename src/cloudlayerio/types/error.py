"""API error body type."""

from __future__ import annotations

from typing import Any

from typing_extensions import TypedDict


class ApiErrorBody(TypedDict, total=False):
    """Structure of error response bodies from the CloudLayer API."""

    status_code: int
    error: str
    message: str
    details: dict[str, Any]
