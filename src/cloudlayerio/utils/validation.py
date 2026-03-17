"""Client-side input validation for the CloudLayer.io Python SDK."""

from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

from cloudlayerio.errors import CloudLayerValidationError


def validate_base_options(options: dict[str, Any]) -> None:
    """Validate options shared by all conversion endpoints."""
    timeout = options.get("timeout")
    if timeout is not None and (not isinstance(timeout, int) or timeout < 1000):
        raise CloudLayerValidationError("timeout", "must be >= 1000 milliseconds")

    async_mode = options.get("async_mode")
    storage = options.get("storage")
    if async_mode and not storage:
        raise CloudLayerValidationError("async_mode", "async mode requires storage to be set")

    if isinstance(storage, dict):
        storage_id = storage.get("id")
        if not isinstance(storage_id, str) or not storage_id.strip():
            raise CloudLayerValidationError("storage.id", "must be a non-empty string")

    webhook = options.get("webhook")
    if webhook is not None:
        parsed = urlparse(webhook)
        if parsed.scheme != "https" or not parsed.netloc:
            raise CloudLayerValidationError("webhook", "must be a valid HTTPS URL")


def validate_url_options(options: dict[str, Any]) -> None:
    """Validate URL, batch, auth, and cookie options."""
    url = options.get("url")
    batch = options.get("batch")

    if url and batch:
        raise CloudLayerValidationError("url", "url and batch are mutually exclusive")

    if not url and not batch:
        raise CloudLayerValidationError("url", "either url or batch.urls is required")

    if url:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise CloudLayerValidationError("url", f"must be a valid URL, got: {url!r}")

    if batch:
        urls = batch.get("urls", [])
        if not urls:
            raise CloudLayerValidationError("batch.urls", "must contain at least one URL")
        if len(urls) > 20:
            raise CloudLayerValidationError("batch.urls", "maximum 20 URLs allowed")
        for i, u in enumerate(urls):
            parsed = urlparse(u)
            if not parsed.scheme or not parsed.netloc:
                raise CloudLayerValidationError(
                    f"batch.urls[{i}]", f"must be a valid URL, got: {u!r}"
                )

    auth = options.get("authentication")
    if auth and (not auth.get("username") or not auth.get("password")):
        raise CloudLayerValidationError("authentication", "both username and password are required")

    cookies = options.get("cookies")
    if cookies:
        for i, cookie in enumerate(cookies):
            if not cookie.get("name"):
                raise CloudLayerValidationError(f"cookies[{i}].name", "is required")
            if not cookie.get("value"):
                raise CloudLayerValidationError(f"cookies[{i}].value", "is required")


def validate_html_options(options: dict[str, Any]) -> None:
    """Validate HTML options."""
    html = options.get("html")
    if not isinstance(html, str) or not html:
        raise CloudLayerValidationError("html", "must be a non-empty string")


def validate_template_options(options: dict[str, Any]) -> None:
    """Validate template options."""
    template_id = options.get("template_id")
    template = options.get("template")

    if template_id and template:
        raise CloudLayerValidationError(
            "template", "provide either template_id or template, not both"
        )
    if not template_id and not template:
        raise CloudLayerValidationError("template", "either template_id or template is required")


def validate_image_options(options: dict[str, Any]) -> None:
    """Validate image-specific options."""
    quality = options.get("quality")
    if quality is not None and (not isinstance(quality, int) or quality < 0 or quality > 100):
        raise CloudLayerValidationError("quality", "must be between 0 and 100")


def validate_file_input(options: dict[str, Any]) -> None:
    """Validate file input for document conversion endpoints."""
    file = options.get("file")
    if file is None:
        raise CloudLayerValidationError("file", "is required for document conversion")
