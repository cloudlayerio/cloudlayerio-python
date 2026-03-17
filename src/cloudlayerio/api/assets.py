"""Assets API methods."""

from __future__ import annotations

from typing import TYPE_CHECKING

from cloudlayerio.errors import CloudLayerValidationError
from cloudlayerio.types.asset import Asset

if TYPE_CHECKING:
    from cloudlayerio.http import AsyncHttpTransport, HttpTransport


def list_assets(http: HttpTransport) -> list[Asset]:
    """List all assets. WARNING: Returns ALL assets, no pagination."""
    response = http.get("/assets", retryable=True)
    return [Asset.from_dict(item) for item in response.json()]


def get_asset(http: HttpTransport, asset_id: str) -> Asset:
    """Get a single asset by ID."""
    if not asset_id or not isinstance(asset_id, str):
        raise CloudLayerValidationError("asset_id", "must be a non-empty string")
    response = http.get(f"/assets/{asset_id}", retryable=True)
    return Asset.from_dict(response.json())


async def async_list_assets(http: AsyncHttpTransport) -> list[Asset]:
    """List all assets (async). WARNING: Returns ALL assets, no pagination."""
    response = await http.get("/assets", retryable=True)
    return [Asset.from_dict(item) for item in response.json()]


async def async_get_asset(http: AsyncHttpTransport, asset_id: str) -> Asset:
    """Get a single asset by ID (async)."""
    if not asset_id or not isinstance(asset_id, str):
        raise CloudLayerValidationError("asset_id", "must be a non-empty string")
    response = await http.get(f"/assets/{asset_id}", retryable=True)
    return Asset.from_dict(response.json())
