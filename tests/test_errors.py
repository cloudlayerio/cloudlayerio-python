"""Tests for the exception hierarchy."""

from __future__ import annotations

import pytest

from cloudlayerio.errors import (
    CloudLayerApiError,
    CloudLayerAuthError,
    CloudLayerConfigError,
    CloudLayerError,
    CloudLayerNetworkError,
    CloudLayerRateLimitError,
    CloudLayerTimeoutError,
    CloudLayerValidationError,
)


class TestErrorHierarchy:
    def test_config_error_is_cloudlayer_error(self) -> None:
        assert issubclass(CloudLayerConfigError, CloudLayerError)

    def test_validation_error_is_cloudlayer_error(self) -> None:
        assert issubclass(CloudLayerValidationError, CloudLayerError)

    def test_network_error_is_cloudlayer_error(self) -> None:
        assert issubclass(CloudLayerNetworkError, CloudLayerError)

    def test_timeout_error_is_cloudlayer_error(self) -> None:
        assert issubclass(CloudLayerTimeoutError, CloudLayerError)

    def test_api_error_is_cloudlayer_error(self) -> None:
        assert issubclass(CloudLayerApiError, CloudLayerError)

    def test_auth_error_is_api_error(self) -> None:
        assert issubclass(CloudLayerAuthError, CloudLayerApiError)

    def test_rate_limit_error_is_api_error(self) -> None:
        assert issubclass(CloudLayerRateLimitError, CloudLayerApiError)


class TestErrorMessages:
    def test_config_error_message(self) -> None:
        e = CloudLayerConfigError("apiKey is required and must be a non-empty string")
        assert str(e) == "apiKey is required and must be a non-empty string"

    def test_validation_error_message(self) -> None:
        e = CloudLayerValidationError("quality", "must be between 0 and 100")
        assert str(e) == 'Validation error on "quality": must be between 0 and 100'
        assert e.field == "quality"

    def test_auth_error_401_message(self) -> None:
        e = CloudLayerAuthError(
            status=401,
            status_text="Unauthorized",
            request_path="/v2/url/pdf",
            request_method="POST",
        )
        assert str(e) == "Authentication failed: invalid or missing API key"
        assert e.status == 401

    def test_auth_error_403_message(self) -> None:
        e = CloudLayerAuthError(
            status=403,
            status_text="Forbidden",
            request_path="/v2/url/pdf",
            request_method="POST",
        )
        assert str(e) == "Authorization failed: insufficient permissions"

    def test_rate_limit_with_retry_after(self) -> None:
        e = CloudLayerRateLimitError(
            status=429,
            status_text="Too Many Requests",
            request_path="/v2/jobs",
            request_method="GET",
            retry_after=30,
        )
        assert str(e) == "Rate limit exceeded. Retry after 30s."
        assert e.retry_after == 30

    def test_rate_limit_without_retry_after(self) -> None:
        e = CloudLayerRateLimitError(
            status=429,
            status_text="Too Many Requests",
            request_path="/v2/jobs",
            request_method="GET",
        )
        assert str(e) == "Rate limit exceeded."
        assert e.retry_after is None

    def test_timeout_error_message(self) -> None:
        e = CloudLayerTimeoutError(
            timeout=30000,
            request_path="/v2/url/pdf",
            request_method="POST",
        )
        assert str(e) == "Request timed out after 30000ms: POST /v2/url/pdf"
        assert e.timeout == 30000

    def test_network_error_message(self) -> None:
        e = CloudLayerNetworkError(
            "Network error: DNS failed",
            request_path="/v2/url/pdf",
            request_method="POST",
        )
        assert str(e) == "Network error: DNS failed"
        assert e.request_path == "/v2/url/pdf"

    def test_api_error_with_body(self) -> None:
        e = CloudLayerApiError(
            "Something went wrong",
            status=500,
            status_text="Internal Server Error",
            body={"message": "Something went wrong"},
            request_path="/v2/url/pdf",
            request_method="POST",
        )
        assert e.status == 500
        assert e.body == {"message": "Something went wrong"}
        assert e.request_path == "/v2/url/pdf"
        assert e.request_method == "POST"

    def test_api_error_none_body(self) -> None:
        e = CloudLayerApiError(
            "API error: 500 Internal Server Error",
            status=500,
            status_text="Internal Server Error",
            request_path="/v2/url/pdf",
            request_method="POST",
        )
        assert e.body is None


class TestErrorRepr:
    def test_base_error_repr(self) -> None:
        e = CloudLayerError("test")
        assert "CloudLayerError" in repr(e)
        assert "test" in repr(e)

    def test_validation_error_repr(self) -> None:
        e = CloudLayerValidationError("url", "invalid")
        r = repr(e)
        assert "CloudLayerValidationError" in r
        assert "url" in r

    def test_timeout_error_repr(self) -> None:
        e = CloudLayerTimeoutError(timeout=5000, request_path="/x", request_method="GET")
        assert "CloudLayerTimeoutError" in repr(e)


class TestErrorCause:
    def test_network_error_preserves_cause(self) -> None:
        orig = ConnectionError("DNS failed")
        try:
            raise CloudLayerNetworkError(
                "Network error: DNS failed",
                request_path="/v2",
                request_method="GET",
            ) from orig
        except CloudLayerNetworkError as e:
            assert e.__cause__ is orig

    def test_all_catchable_by_base(self) -> None:
        errors = [
            CloudLayerConfigError("x"),
            CloudLayerValidationError("f", "m"),
            CloudLayerNetworkError("n", request_path="/", request_method="GET"),
            CloudLayerTimeoutError(timeout=1, request_path="/", request_method="GET"),
            CloudLayerApiError(
                "a", status=500, status_text="", request_path="/", request_method="GET"
            ),
            CloudLayerAuthError(status=401, status_text="", request_path="/", request_method="GET"),
            CloudLayerRateLimitError(
                status=429, status_text="", request_path="/", request_method="GET"
            ),
        ]
        for error in errors:
            with pytest.raises(CloudLayerError):
                raise error
