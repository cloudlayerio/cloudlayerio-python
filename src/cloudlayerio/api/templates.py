"""Templates API methods (public, no auth required)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from cloudlayerio.types.template import PublicTemplate

if TYPE_CHECKING:
    from cloudlayerio.http import AsyncHttpTransport, HttpTransport


def list_templates(
    http: HttpTransport, options: dict[str, Any] | None = None
) -> list[PublicTemplate]:
    """List public templates. Always uses /v2/templates regardless of client version."""
    params = options if options else None
    response = http.get("/v2/templates", retryable=True, absolute_path=True, params=params)
    return [PublicTemplate.from_dict(item) for item in response.json()]


def get_template(http: HttpTransport, template_id: str) -> PublicTemplate:
    """Get a public template by ID. Always uses /v2/template/{id}."""
    response = http.get(f"/v2/template/{template_id}", retryable=True, absolute_path=True)
    return PublicTemplate.from_dict(response.json())


async def async_list_templates(
    http: AsyncHttpTransport, options: dict[str, Any] | None = None
) -> list[PublicTemplate]:
    """List public templates (async). Always uses /v2/templates."""
    params = options if options else None
    response = await http.get("/v2/templates", retryable=True, absolute_path=True, params=params)
    return [PublicTemplate.from_dict(item) for item in response.json()]


async def async_get_template(http: AsyncHttpTransport, template_id: str) -> PublicTemplate:
    """Get a public template by ID (async). Always uses /v2/template/{id}."""
    response = await http.get(f"/v2/template/{template_id}", retryable=True, absolute_path=True)
    return PublicTemplate.from_dict(response.json())
