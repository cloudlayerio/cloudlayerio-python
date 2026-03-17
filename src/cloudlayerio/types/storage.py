"""Storage-related types and models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from typing_extensions import TypedDict


class StorageParamsRequired(TypedDict):
    """Required fields for adding a new storage configuration."""

    title: str
    region: str
    access_key_id: str
    secret_access_key: str
    bucket: str


class StorageParamsOptional(StorageParamsRequired, total=False):
    """Storage configuration parameters. All required except `endpoint`."""

    endpoint: str  # For non-AWS S3-compatible services


@dataclass
class StorageListItem:
    """A storage configuration summary from list endpoint."""

    id: str
    title: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StorageListItem:
        """Create a StorageListItem from an API response dict."""
        return cls(
            id=data.get("id", ""),
            title=data.get("title", ""),
        )


@dataclass
class StorageDetail:
    """A full storage configuration detail."""

    data: str
    id: str
    title: str
    uid: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StorageDetail:
        """Create a StorageDetail from an API response dict."""
        return cls(
            data=data.get("data", ""),
            id=data.get("id", ""),
            title=data.get("title", ""),
            uid=data.get("uid", ""),
        )


@dataclass
class StorageNotAllowedResponse:
    """Response when storage operations are not allowed on the user's plan."""

    allowed: bool
    reason: str
    status_code: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StorageNotAllowedResponse:
        """Create a StorageNotAllowedResponse from an API response dict."""
        return cls(
            allowed=data.get("allowed", False),
            reason=data.get("reason", ""),
            status_code=data.get("statusCode", 0),
        )
