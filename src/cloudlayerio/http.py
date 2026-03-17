"""HTTP transport layer for the CloudLayer.io Python SDK.

Handles authentication, retries, timeouts, error mapping, and response parsing.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import random
import re
import time
from typing import Any

import httpx

from cloudlayerio.errors import (
    CloudLayerApiError,
    CloudLayerAuthError,
    CloudLayerNetworkError,
    CloudLayerRateLimitError,
    CloudLayerTimeoutError,
)
from cloudlayerio.types.response import CloudLayerResponseHeaders

# Status codes that trigger retry (when retryable=True)
_RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}

# Status codes that are never retried (client errors)
_NON_RETRYABLE_STATUS_CODES = {400, 401, 403, 404, 422}


def _parse_cl_headers(headers: httpx.Headers) -> CloudLayerResponseHeaders:
    """Parse CloudLayer custom headers from an HTTP response."""
    return CloudLayerResponseHeaders.from_headers(dict(headers))


def _parse_filename(headers: httpx.Headers) -> str | None:
    """Extract filename from Content-Disposition header."""
    cd = headers.get("content-disposition")
    if not cd:
        return None
    match = re.search(r'filename[*]?=["\']?([^"\';\s]+)', cd)
    return match.group(1) if match else None


def _is_json_content_type(content_type: str | None) -> bool:
    """Check if the content type indicates JSON."""
    if not content_type:
        return False
    ct = content_type.lower()
    return "application/json" in ct or "text/json" in ct


def _parse_error_body(response: httpx.Response) -> Any:
    """Parse the error response body. Try JSON first, fall back to text."""
    try:
        return response.json()
    except (json.JSONDecodeError, ValueError):
        text = response.text
        return text if text else None


def _make_error_message(status: int, status_text: str, body: Any) -> str:
    """Build a human-readable error message from response details."""
    if isinstance(body, dict) and "message" in body:
        return str(body["message"])
    return f"API error: {status} {status_text}"


def _calculate_backoff(attempt: int) -> float:
    """Calculate retry delay with exponential backoff and jitter.

    Base delays: 1s, 2s, 4s + 0-500ms random jitter.
    """
    base = float(min(2**attempt, 4))
    jitter = random.random() * 0.5
    return base + jitter


def _map_error(
    response: httpx.Response,
    request_path: str,
    request_method: str,
) -> CloudLayerApiError:
    """Map an HTTP error response to the appropriate exception type."""
    status = response.status_code
    status_text = response.reason_phrase or ""
    body = _parse_error_body(response)

    if status in (401, 403):
        return CloudLayerAuthError(
            status=status,
            status_text=status_text,
            body=body,
            request_path=request_path,
            request_method=request_method,
        )

    if status == 429:
        retry_after: int | None = None
        ra_header = response.headers.get("retry-after")
        if ra_header:
            with contextlib.suppress(ValueError, TypeError):
                retry_after = int(ra_header)
        return CloudLayerRateLimitError(
            status=status,
            status_text=status_text,
            body=body,
            request_path=request_path,
            request_method=request_method,
            retry_after=retry_after,
        )

    message = _make_error_message(status, status_text, body)
    return CloudLayerApiError(
        message,
        status=status,
        status_text=status_text,
        body=body,
        request_path=request_path,
        request_method=request_method,
    )


class HttpTransport:
    """Synchronous HTTP transport for the CloudLayer API."""

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        api_version: str,
        timeout: int,
        max_retries: int,
        headers: dict[str, str] | None = None,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._api_version = api_version
        self._timeout = timeout
        self._max_retries = max_retries

        default_headers = {"X-API-Key": api_key}
        if headers:
            default_headers.update(headers)

        self._client = httpx.Client(headers=default_headers)

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()

    def __enter__(self) -> HttpTransport:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def _build_url(self, path: str, *, absolute_path: bool = False) -> str:
        """Build the full URL for a request."""
        if absolute_path:
            return f"{self._base_url}{path}"
        return f"{self._base_url}/{self._api_version}{path}"

    def request(
        self,
        method: str,
        path: str,
        *,
        json_body: Any = None,
        files: Any = None,
        timeout: int | None = None,
        params: dict[str, Any] | None = None,
        retryable: bool = False,
        absolute_path: bool = False,
    ) -> httpx.Response:
        """Make an HTTP request with retry logic and error handling."""
        url = self._build_url(path, absolute_path=absolute_path)
        timeout_s = (timeout or self._timeout) / 1000.0
        max_attempts = (self._max_retries + 1) if retryable else 1

        # Filter None values from query params
        clean_params: dict[str, Any] | None = None
        if params:
            clean_params = {k: v for k, v in params.items() if v is not None}

        last_error: Exception | None = None

        for attempt in range(max_attempts):
            try:
                request_kwargs: dict[str, Any] = {
                    "method": method,
                    "url": url,
                    "timeout": timeout_s,
                }

                if clean_params:
                    request_kwargs["params"] = clean_params

                if files is not None:
                    request_kwargs["files"] = files
                elif json_body is not None:
                    request_kwargs["json"] = json_body

                response = self._client.request(**request_kwargs)

            except httpx.TimeoutException as e:
                raise CloudLayerTimeoutError(
                    timeout=timeout or self._timeout,
                    request_path=path,
                    request_method=method,
                ) from e
            except (httpx.ConnectError, httpx.NetworkError) as e:
                raise CloudLayerNetworkError(
                    f"Network error: {e}",
                    request_path=path,
                    request_method=method,
                ) from e

            # Success
            if response.is_success:
                return response

            # Map to typed error
            error = _map_error(response, path, method)

            # Don't retry client errors or non-retryable requests
            if response.status_code in _NON_RETRYABLE_STATUS_CODES or not retryable:
                raise error

            # Retryable error — check if we have attempts left
            if attempt < max_attempts - 1:
                if isinstance(error, CloudLayerRateLimitError) and error.retry_after:
                    delay = float(error.retry_after)
                else:
                    delay = _calculate_backoff(attempt)
                time.sleep(delay)
                last_error = error
            else:
                raise error

        # Should not reach here, but satisfy type checker
        if last_error:  # pragma: no cover
            raise last_error
        raise RuntimeError("Unexpected state in retry loop")  # pragma: no cover

    def get(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        retryable: bool = False,
        absolute_path: bool = False,
        timeout: int | None = None,
    ) -> httpx.Response:
        """Make a GET request."""
        return self.request(
            "GET",
            path,
            params=params,
            retryable=retryable,
            absolute_path=absolute_path,
            timeout=timeout,
        )

    def post(
        self,
        path: str,
        body: Any = None,
        *,
        retryable: bool = False,
        absolute_path: bool = False,
        timeout: int | None = None,
    ) -> httpx.Response:
        """Make a POST request with JSON body."""
        return self.request(
            "POST",
            path,
            json_body=body,
            retryable=retryable,
            absolute_path=absolute_path,
            timeout=timeout,
        )

    def post_multipart(
        self,
        path: str,
        files: Any,
        *,
        retryable: bool = False,
        absolute_path: bool = False,
        timeout: int | None = None,
    ) -> httpx.Response:
        """Make a POST request with multipart form data."""
        return self.request(
            "POST",
            path,
            files=files,
            retryable=retryable,
            absolute_path=absolute_path,
            timeout=timeout,
        )

    def delete(
        self,
        path: str,
        *,
        retryable: bool = False,
        absolute_path: bool = False,
        timeout: int | None = None,
    ) -> httpx.Response:
        """Make a DELETE request."""
        return self.request(
            "DELETE",
            path,
            retryable=retryable,
            absolute_path=absolute_path,
            timeout=timeout,
        )


class AsyncHttpTransport:
    """Asynchronous HTTP transport for the CloudLayer API."""

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        api_version: str,
        timeout: int,
        max_retries: int,
        headers: dict[str, str] | None = None,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._api_version = api_version
        self._timeout = timeout
        self._max_retries = max_retries

        default_headers = {"X-API-Key": api_key}
        if headers:
            default_headers.update(headers)

        self._client = httpx.AsyncClient(headers=default_headers)

    async def close(self) -> None:
        """Close the underlying async HTTP client."""
        await self._client.aclose()

    async def __aenter__(self) -> AsyncHttpTransport:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    def _build_url(self, path: str, *, absolute_path: bool = False) -> str:
        """Build the full URL for a request."""
        if absolute_path:
            return f"{self._base_url}{path}"
        return f"{self._base_url}/{self._api_version}{path}"

    async def request(
        self,
        method: str,
        path: str,
        *,
        json_body: Any = None,
        files: Any = None,
        timeout: int | None = None,
        params: dict[str, Any] | None = None,
        retryable: bool = False,
        absolute_path: bool = False,
    ) -> httpx.Response:
        """Make an async HTTP request with retry logic and error handling."""
        url = self._build_url(path, absolute_path=absolute_path)
        timeout_s = (timeout or self._timeout) / 1000.0
        max_attempts = (self._max_retries + 1) if retryable else 1

        clean_params: dict[str, Any] | None = None
        if params:
            clean_params = {k: v for k, v in params.items() if v is not None}

        last_error: Exception | None = None

        for attempt in range(max_attempts):
            try:
                request_kwargs: dict[str, Any] = {
                    "method": method,
                    "url": url,
                    "timeout": timeout_s,
                }

                if clean_params:
                    request_kwargs["params"] = clean_params

                if files is not None:
                    request_kwargs["files"] = files
                elif json_body is not None:
                    request_kwargs["json"] = json_body

                response = await self._client.request(**request_kwargs)

            except httpx.TimeoutException as e:
                raise CloudLayerTimeoutError(
                    timeout=timeout or self._timeout,
                    request_path=path,
                    request_method=method,
                ) from e
            except (httpx.ConnectError, httpx.NetworkError) as e:
                raise CloudLayerNetworkError(
                    f"Network error: {e}",
                    request_path=path,
                    request_method=method,
                ) from e

            if response.is_success:
                return response

            error = _map_error(response, path, method)

            if response.status_code in _NON_RETRYABLE_STATUS_CODES or not retryable:
                raise error

            if attempt < max_attempts - 1:
                if isinstance(error, CloudLayerRateLimitError) and error.retry_after:
                    delay = float(error.retry_after)
                else:
                    delay = _calculate_backoff(attempt)
                await asyncio.sleep(delay)
                last_error = error
            else:
                raise error

        if last_error:  # pragma: no cover
            raise last_error
        raise RuntimeError("Unexpected state in retry loop")  # pragma: no cover

    async def get(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        retryable: bool = False,
        absolute_path: bool = False,
        timeout: int | None = None,
    ) -> httpx.Response:
        """Make an async GET request."""
        return await self.request(
            "GET",
            path,
            params=params,
            retryable=retryable,
            absolute_path=absolute_path,
            timeout=timeout,
        )

    async def post(
        self,
        path: str,
        body: Any = None,
        *,
        retryable: bool = False,
        absolute_path: bool = False,
        timeout: int | None = None,
    ) -> httpx.Response:
        """Make an async POST request with JSON body."""
        return await self.request(
            "POST",
            path,
            json_body=body,
            retryable=retryable,
            absolute_path=absolute_path,
            timeout=timeout,
        )

    async def post_multipart(
        self,
        path: str,
        files: Any,
        *,
        retryable: bool = False,
        absolute_path: bool = False,
        timeout: int | None = None,
    ) -> httpx.Response:
        """Make an async POST request with multipart form data."""
        return await self.request(
            "POST",
            path,
            files=files,
            retryable=retryable,
            absolute_path=absolute_path,
            timeout=timeout,
        )

    async def delete(
        self,
        path: str,
        *,
        retryable: bool = False,
        absolute_path: bool = False,
        timeout: int | None = None,
    ) -> httpx.Response:
        """Make an async DELETE request."""
        return await self.request(
            "DELETE",
            path,
            retryable=retryable,
            absolute_path=absolute_path,
            timeout=timeout,
        )
