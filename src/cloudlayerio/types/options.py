"""Base options shared by all API methods."""

from __future__ import annotations

from typing_extensions import TypedDict


class StorageRequestOptions(TypedDict):
    """Reference to a saved storage configuration."""

    id: str


class BaseOptions(TypedDict, total=False):
    """Options shared by all conversion and data management endpoints."""

    name: str
    timeout: int
    delay: int
    filename: str
    inline: bool
    async_mode: bool  # Serialized as "async" in JSON (Python keyword)
    storage: StorageRequestOptions | bool
    webhook: str
    api_ver: str
    project_id: str
