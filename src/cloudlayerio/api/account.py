"""Account API methods."""

from __future__ import annotations

from typing import TYPE_CHECKING

from cloudlayerio.types.account import AccountInfo, StatusResponse

if TYPE_CHECKING:
    from cloudlayerio.http import AsyncHttpTransport, HttpTransport


def get_account(http: HttpTransport) -> AccountInfo:
    """Get account information."""
    response = http.get("/account", retryable=True)
    return AccountInfo.from_dict(response.json())


def get_status(http: HttpTransport) -> StatusResponse:
    """Get API status. Note: returns {"status": "ok "} with trailing space."""
    response = http.get("/getStatus", retryable=True)
    return StatusResponse.from_dict(response.json())


async def async_get_account(http: AsyncHttpTransport) -> AccountInfo:
    """Get account information (async)."""
    response = await http.get("/account", retryable=True)
    return AccountInfo.from_dict(response.json())


async def async_get_status(http: AsyncHttpTransport) -> StatusResponse:
    """Get API status (async). Note: returns {"status": "ok "} with trailing space."""
    response = await http.get("/getStatus", retryable=True)
    return StatusResponse.from_dict(response.json())
