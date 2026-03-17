"""Tests for HttpTransport."""

from __future__ import annotations

from unittest.mock import patch

import httpx
import pytest
import respx

from cloudlayerio.errors import (
    CloudLayerApiError,
    CloudLayerAuthError,
    CloudLayerNetworkError,
    CloudLayerRateLimitError,
    CloudLayerTimeoutError,
)
from cloudlayerio.http import HttpTransport, _calculate_backoff, _parse_cl_headers, _parse_filename


@pytest.fixture
def http() -> HttpTransport:
    t = HttpTransport(
        api_key="test-key",
        base_url="https://api.cloudlayer.io",
        api_version="v2",
        timeout=5000,
        max_retries=2,
    )
    yield t
    t.close()


class TestUrlBuilding:
    def test_normal_url(self, http: HttpTransport) -> None:
        assert http._build_url("/url/pdf") == "https://api.cloudlayer.io/v2/url/pdf"

    def test_absolute_path(self, http: HttpTransport) -> None:
        assert (
            http._build_url("/v2/templates", absolute_path=True)
            == "https://api.cloudlayer.io/v2/templates"
        )

    def test_trailing_slash_stripped(self) -> None:
        t = HttpTransport(
            api_key="k",
            base_url="https://api.cloudlayer.io/",
            api_version="v1",
            timeout=5000,
            max_retries=0,
        )
        assert t._build_url("/url/pdf") == "https://api.cloudlayer.io/v1/url/pdf"
        t.close()


class TestAuthHeaders:
    @respx.mock
    def test_sends_api_key(self, http: HttpTransport) -> None:
        route = respx.get("https://api.cloudlayer.io/v2/jobs").mock(
            return_value=httpx.Response(200, json=[])
        )
        http.get("/jobs")
        assert route.calls[0].request.headers["x-api-key"] == "test-key"

    @respx.mock
    def test_custom_headers(self) -> None:
        t = HttpTransport(
            api_key="k",
            base_url="https://api.cloudlayer.io",
            api_version="v2",
            timeout=5000,
            max_retries=0,
            headers={"X-Custom": "val"},
        )
        route = respx.get("https://api.cloudlayer.io/v2/jobs").mock(
            return_value=httpx.Response(200, json=[])
        )
        t.get("/jobs")
        assert route.calls[0].request.headers["x-custom"] == "val"
        t.close()


class TestErrorMapping:
    @respx.mock
    def test_401_raises_auth_error(self, http: HttpTransport) -> None:
        respx.get("https://api.cloudlayer.io/v2/jobs").mock(
            return_value=httpx.Response(401, json={"message": "Unauthorized"})
        )
        with pytest.raises(CloudLayerAuthError) as exc_info:
            http.get("/jobs")
        assert exc_info.value.status == 401
        assert exc_info.value.request_path == "/jobs"

    @respx.mock
    def test_403_raises_auth_error(self, http: HttpTransport) -> None:
        respx.get("https://api.cloudlayer.io/v2/jobs").mock(
            return_value=httpx.Response(403, json={})
        )
        with pytest.raises(CloudLayerAuthError) as exc_info:
            http.get("/jobs")
        assert exc_info.value.status == 403

    @respx.mock
    def test_429_raises_rate_limit_error(self, http: HttpTransport) -> None:
        respx.get("https://api.cloudlayer.io/v2/jobs").mock(
            return_value=httpx.Response(429, headers={"retry-after": "30"}, json={})
        )
        with pytest.raises(CloudLayerRateLimitError) as exc_info:
            http.get("/jobs")
        assert exc_info.value.retry_after == 30

    @respx.mock
    def test_400_raises_api_error_no_retry(self, http: HttpTransport) -> None:
        respx.get("https://api.cloudlayer.io/v2/jobs").mock(
            return_value=httpx.Response(400, json={"message": "Bad request"})
        )
        with pytest.raises(CloudLayerApiError) as exc_info:
            http.get("/jobs", retryable=True)
        assert exc_info.value.status == 400

    @respx.mock
    def test_500_raises_api_error(self, http: HttpTransport) -> None:
        respx.get("https://api.cloudlayer.io/v2/jobs").mock(
            return_value=httpx.Response(500, json={"message": "Server error"})
        )
        with pytest.raises(CloudLayerApiError) as exc_info:
            http.get("/jobs")
        assert exc_info.value.status == 500

    @respx.mock
    def test_error_body_parsed_as_json(self, http: HttpTransport) -> None:
        respx.get("https://api.cloudlayer.io/v2/jobs").mock(
            return_value=httpx.Response(
                422, json={"message": "Validation failed", "details": {"field": "url"}}
            )
        )
        with pytest.raises(CloudLayerApiError) as exc_info:
            http.get("/jobs")
        assert isinstance(exc_info.value.body, dict)
        assert exc_info.value.body["message"] == "Validation failed"

    @respx.mock
    def test_error_body_falls_back_to_text(self, http: HttpTransport) -> None:
        respx.get("https://api.cloudlayer.io/v2/jobs").mock(
            return_value=httpx.Response(500, text="Internal Server Error")
        )
        with pytest.raises(CloudLayerApiError) as exc_info:
            http.get("/jobs")
        assert exc_info.value.body == "Internal Server Error"

    @respx.mock
    def test_timeout_raises_timeout_error(self, http: HttpTransport) -> None:
        respx.get("https://api.cloudlayer.io/v2/jobs").mock(
            side_effect=httpx.ReadTimeout("timeout")
        )
        with pytest.raises(CloudLayerTimeoutError) as exc_info:
            http.get("/jobs")
        assert exc_info.value.timeout == 5000

    @respx.mock
    def test_network_error_raises(self, http: HttpTransport) -> None:
        respx.get("https://api.cloudlayer.io/v2/jobs").mock(
            side_effect=httpx.ConnectError("DNS failed")
        )
        with pytest.raises(CloudLayerNetworkError) as exc_info:
            http.get("/jobs")
        assert "DNS failed" in str(exc_info.value)
        assert exc_info.value.__cause__ is not None


class TestRetryLogic:
    @respx.mock
    def test_retries_on_500_when_retryable(self, http: HttpTransport) -> None:
        route = respx.get("https://api.cloudlayer.io/v2/jobs")
        route.side_effect = [
            httpx.Response(500, json={"message": "error"}),
            httpx.Response(500, json={"message": "error"}),
            httpx.Response(200, json=[]),
        ]
        with patch("cloudlayerio.http.time.sleep"):
            result = http.get("/jobs", retryable=True)
        assert result.status_code == 200
        assert len(route.calls) == 3

    @respx.mock
    def test_no_retry_when_not_retryable(self, http: HttpTransport) -> None:
        route = respx.get("https://api.cloudlayer.io/v2/url/pdf")
        route.side_effect = [httpx.Response(500, json={"message": "error"})]
        with pytest.raises(CloudLayerApiError):
            http.get("/url/pdf", retryable=False)
        assert len(route.calls) == 1

    @respx.mock
    def test_no_retry_on_client_error(self, http: HttpTransport) -> None:
        route = respx.get("https://api.cloudlayer.io/v2/jobs")
        route.side_effect = [httpx.Response(422, json={"message": "invalid"})]
        with pytest.raises(CloudLayerApiError):
            http.get("/jobs", retryable=True)
        assert len(route.calls) == 1

    @respx.mock
    def test_retries_on_429_with_retry_after(self, http: HttpTransport) -> None:
        route = respx.get("https://api.cloudlayer.io/v2/jobs")
        route.side_effect = [
            httpx.Response(429, headers={"retry-after": "1"}, json={}),
            httpx.Response(200, json=[]),
        ]
        with patch("cloudlayerio.http.time.sleep") as mock_sleep:
            result = http.get("/jobs", retryable=True)
        assert result.status_code == 200
        mock_sleep.assert_called_once_with(1.0)

    @respx.mock
    def test_exhausts_retries(self, http: HttpTransport) -> None:
        route = respx.get("https://api.cloudlayer.io/v2/jobs")
        route.side_effect = [
            httpx.Response(500, json={"message": "err"}),
            httpx.Response(500, json={"message": "err"}),
            httpx.Response(500, json={"message": "err"}),
        ]
        with patch("cloudlayerio.http.time.sleep"), pytest.raises(CloudLayerApiError):
            http.get("/jobs", retryable=True)
        assert len(route.calls) == 3  # 1 initial + 2 retries


class TestBackoff:
    def test_first_attempt_around_1s(self) -> None:
        delay = _calculate_backoff(0)
        assert 1.0 <= delay < 1.5

    def test_second_attempt_around_2s(self) -> None:
        delay = _calculate_backoff(1)
        assert 2.0 <= delay < 2.5

    def test_third_attempt_around_4s(self) -> None:
        delay = _calculate_backoff(2)
        assert 4.0 <= delay < 4.5


class TestResponseParsing:
    @respx.mock
    def test_json_response(self, http: HttpTransport) -> None:
        respx.get("https://api.cloudlayer.io/v2/jobs").mock(
            return_value=httpx.Response(200, json={"id": "j1"})
        )
        response = http.get("/jobs")
        assert response.json() == {"id": "j1"}

    @respx.mock
    def test_binary_response(self, http: HttpTransport) -> None:
        respx.post("https://api.cloudlayer.io/v2/url/pdf").mock(
            return_value=httpx.Response(
                200, content=b"%PDF-1.4", headers={"content-type": "application/pdf"}
            )
        )
        response = http.post("/url/pdf", {"url": "https://example.com"})
        assert response.content == b"%PDF-1.4"

    @respx.mock
    def test_204_no_content(self, http: HttpTransport) -> None:
        respx.delete("https://api.cloudlayer.io/v2/storage/s1").mock(
            return_value=httpx.Response(204)
        )
        response = http.delete("/storage/s1")
        assert response.status_code == 204


class TestClHeaders:
    def test_parse_all_headers(self, cl_headers: dict[str, str]) -> None:
        headers = httpx.Headers(cl_headers)
        parsed = _parse_cl_headers(headers)
        assert parsed.worker_job_id == "wj-123"
        assert parsed.cluster_id == "cluster-1"
        assert parsed.worker == "worker-a"
        assert parsed.bandwidth == 15000
        assert parsed.process_time == 2500
        assert parsed.calls_remaining == 958
        assert parsed.charged_time == 3000
        assert parsed.bandwidth_cost == 0.002
        assert parsed.process_time_cost == 0.05
        assert parsed.api_credit_cost == 0.01

    def test_missing_headers_are_none(self) -> None:
        headers = httpx.Headers({})
        parsed = _parse_cl_headers(headers)
        assert parsed.worker_job_id is None
        assert parsed.bandwidth is None
        assert parsed.bandwidth_cost is None

    def test_non_numeric_header_is_none(self) -> None:
        headers = httpx.Headers({"cl-bandwidth": "not-a-number"})
        parsed = _parse_cl_headers(headers)
        assert parsed.bandwidth is None


class TestFilename:
    def test_parse_filename(self) -> None:
        headers = httpx.Headers({"content-disposition": 'attachment; filename="test.pdf"'})
        assert _parse_filename(headers) == "test.pdf"

    def test_no_content_disposition(self) -> None:
        headers = httpx.Headers({})
        assert _parse_filename(headers) is None

    def test_filename_without_quotes(self) -> None:
        headers = httpx.Headers({"content-disposition": "attachment; filename=test.pdf"})
        assert _parse_filename(headers) == "test.pdf"


class TestContextManager:
    def test_context_manager_closes(self) -> None:
        with HttpTransport(
            api_key="k",
            base_url="https://api.cloudlayer.io",
            api_version="v2",
            timeout=5000,
            max_retries=0,
        ) as t:
            assert t is not None


class TestQueryParams:
    @respx.mock
    def test_none_params_filtered(self, http: HttpTransport) -> None:
        route = respx.get("https://api.cloudlayer.io/v2/templates").mock(
            return_value=httpx.Response(200, json=[])
        )
        http.request("GET", "/templates", params={"type": "pdf", "category": None})
        url = str(route.calls[0].request.url)
        assert "type=pdf" in url
        assert "category" not in url
