"""Exception hierarchy for the CloudLayer.io Python SDK.

Mirrors the JS SDK's 8 error classes with request context for debugging.
"""

from __future__ import annotations

from typing import Any


class CloudLayerError(Exception):
    """Base error class for all CloudLayer SDK errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.message!r})"


class CloudLayerConfigError(CloudLayerError):
    """Thrown when the CloudLayer client is configured with invalid options."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class CloudLayerValidationError(CloudLayerError):
    """Thrown when client-side input validation fails before making the API request."""

    field: str

    def __init__(self, field: str, message: str) -> None:
        self.field = field
        super().__init__(f'Validation error on "{field}": {message}')

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(field={self.field!r}, message={self.message!r})"


class CloudLayerNetworkError(CloudLayerError):
    """Thrown when a network error occurs (DNS failure, connection refused, etc.)."""

    request_path: str
    request_method: str

    def __init__(
        self,
        message: str,
        *,
        request_path: str,
        request_method: str,
    ) -> None:
        self.request_path = request_path
        self.request_method = request_method
        super().__init__(message)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"message={self.message!r}, "
            f"request_path={self.request_path!r}, "
            f"request_method={self.request_method!r})"
        )


class CloudLayerTimeoutError(CloudLayerError):
    """Thrown when a request times out."""

    timeout: int
    request_path: str
    request_method: str

    def __init__(
        self,
        *,
        timeout: int,
        request_path: str,
        request_method: str,
    ) -> None:
        self.timeout = timeout
        self.request_path = request_path
        self.request_method = request_method
        super().__init__(f"Request timed out after {timeout}ms: {request_method} {request_path}")

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"timeout={self.timeout!r}, "
            f"request_path={self.request_path!r}, "
            f"request_method={self.request_method!r})"
        )


class CloudLayerApiError(CloudLayerError):
    """Thrown when the CloudLayer API returns an error response (4xx/5xx)."""

    status: int
    status_text: str
    body: Any
    request_path: str
    request_method: str

    def __init__(
        self,
        message: str,
        *,
        status: int,
        status_text: str,
        body: Any = None,
        request_path: str,
        request_method: str,
    ) -> None:
        self.status = status
        self.status_text = status_text
        self.body = body
        self.request_path = request_path
        self.request_method = request_method
        super().__init__(message)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"status={self.status!r}, "
            f"request_path={self.request_path!r}, "
            f"request_method={self.request_method!r})"
        )


class CloudLayerAuthError(CloudLayerApiError):
    """Thrown when the API rejects the request due to invalid or missing authentication.

    HTTP 401 (Unauthorized) or 403 (Forbidden).
    """

    def __init__(
        self,
        *,
        status: int,
        status_text: str,
        body: Any = None,
        request_path: str,
        request_method: str,
    ) -> None:
        message = (
            "Authentication failed: invalid or missing API key"
            if status == 401
            else "Authorization failed: insufficient permissions"
        )
        super().__init__(
            message,
            status=status,
            status_text=status_text,
            body=body,
            request_path=request_path,
            request_method=request_method,
        )


class CloudLayerRateLimitError(CloudLayerApiError):
    """Thrown when the API rate limit is exceeded (HTTP 429)."""

    retry_after: int | None

    def __init__(
        self,
        *,
        status: int,
        status_text: str,
        body: Any = None,
        request_path: str,
        request_method: str,
        retry_after: int | None = None,
    ) -> None:
        self.retry_after = retry_after
        retry_msg = f" Retry after {retry_after}s." if retry_after else ""
        super().__init__(
            f"Rate limit exceeded.{retry_msg}",
            status=status,
            status_text=status_text,
            body=body,
            request_path=request_path,
            request_method=request_method,
        )

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"status={self.status!r}, "
            f"retry_after={self.retry_after!r}, "
            f"request_path={self.request_path!r})"
        )
