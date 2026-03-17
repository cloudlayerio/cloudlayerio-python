"""Storage API methods."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from cloudlayerio.types.storage import (
    StorageDetail,
    StorageListItem,
    StorageNotAllowedResponse,
)
from cloudlayerio.utils.serialization import serialize_options

if TYPE_CHECKING:
    from cloudlayerio.http import AsyncHttpTransport, HttpTransport


def _parse_storage_response(
    data: dict[str, Any],
) -> StorageDetail | StorageNotAllowedResponse:
    """Parse add_storage response — may be StorageDetail or StorageNotAllowedResponse."""
    if data.get("allowed") is False:
        return StorageNotAllowedResponse.from_dict(data)
    return StorageDetail.from_dict(data)


def list_storage(http: HttpTransport) -> list[StorageListItem]:
    """List all storage configurations."""
    response = http.get("/storage", retryable=True)
    return [StorageListItem.from_dict(item) for item in response.json()]


def get_storage(http: HttpTransport, storage_id: str) -> StorageDetail:
    """Get a single storage configuration."""
    response = http.get(f"/storage/{storage_id}", retryable=True)
    return StorageDetail.from_dict(response.json())


def add_storage(
    http: HttpTransport, config: dict[str, Any]
) -> StorageDetail | StorageNotAllowedResponse:
    """Add a new storage configuration."""
    body = serialize_options(config)
    response = http.post("/storage", body)
    return _parse_storage_response(response.json())


def delete_storage(http: HttpTransport, storage_id: str) -> None:
    """Delete a storage configuration."""
    http.delete(f"/storage/{storage_id}")


async def async_list_storage(http: AsyncHttpTransport) -> list[StorageListItem]:
    """List all storage configurations (async)."""
    response = await http.get("/storage", retryable=True)
    return [StorageListItem.from_dict(item) for item in response.json()]


async def async_get_storage(http: AsyncHttpTransport, storage_id: str) -> StorageDetail:
    """Get a single storage configuration (async)."""
    response = await http.get(f"/storage/{storage_id}", retryable=True)
    return StorageDetail.from_dict(response.json())


async def async_add_storage(
    http: AsyncHttpTransport, config: dict[str, Any]
) -> StorageDetail | StorageNotAllowedResponse:
    """Add a new storage configuration (async)."""
    body = serialize_options(config)
    response = await http.post("/storage", body)
    return _parse_storage_response(response.json())


async def async_delete_storage(http: AsyncHttpTransport, storage_id: str) -> None:
    """Delete a storage configuration (async)."""
    await http.delete(f"/storage/{storage_id}")
