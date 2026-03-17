"""Account and status response models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# Fields in the AccountInfo dataclass
_ACCOUNT_FIELDS = {
    "email",
    "calls_limit",
    "calls",
    "storage_used",
    "storage_limit",
    "subscription",
    "bytes_total",
    "bytes_limit",
    "compute_time_total",
    "compute_time_limit",
    "sub_type",
    "uid",
    "credit",
    "sub_active",
}

# camelCase -> snake_case mapping for Account response deserialization
_ACCOUNT_FIELD_MAP: dict[str, str] = {
    "callsLimit": "calls_limit",
    "storageUsed": "storage_used",
    "storageLimit": "storage_limit",
    "bytesTotal": "bytes_total",
    "bytesLimit": "bytes_limit",
    "computeTimeTotal": "compute_time_total",
    "computeTimeLimit": "compute_time_limit",
    "subType": "sub_type",
    "subActive": "sub_active",
}


@dataclass
class AccountInfo:
    """Account information from the CloudLayer API."""

    email: str = ""
    uid: str = ""
    calls: int = 0
    calls_limit: int = 0
    storage_used: int = 0
    storage_limit: int = 0
    subscription: str = ""
    bytes_total: int = 0
    bytes_limit: int = 0
    compute_time_total: int = 0
    compute_time_limit: int = 0
    sub_type: str = ""  # "usage" | "limit" at runtime
    sub_active: bool = False
    credit: int | None = None
    extra_fields: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AccountInfo:
        """Create an AccountInfo from an API response dict (camelCase keys)."""
        converted: dict[str, Any] = {}
        extra: dict[str, Any] = {}
        for key, value in data.items():
            snake_key = _ACCOUNT_FIELD_MAP.get(key, key)
            if snake_key in _ACCOUNT_FIELDS:
                converted[snake_key] = value
            else:
                extra[key] = value
        converted["extra_fields"] = extra
        return cls(**converted)


@dataclass
class StatusResponse:
    """API status response."""

    status: str  # Note: legacy API returns "ok " with trailing space

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StatusResponse:
        """Create a StatusResponse from an API response dict."""
        return cls(status=data.get("status", ""))
