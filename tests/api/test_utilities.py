"""Tests for utility methods (download_job_result, wait_for_job)."""

from __future__ import annotations

from typing import Any
from unittest.mock import patch

import httpx
import pytest
import respx

from cloudlayerio.client import CloudLayer
from cloudlayerio.errors import (
    CloudLayerApiError,
    CloudLayerTimeoutError,
    CloudLayerValidationError,
)
from cloudlayerio.types.job import Job


class TestDownloadJobResult:
    @respx.mock
    def test_downloads_binary(self) -> None:
        respx.get("https://s3.example.com/result.pdf").mock(
            return_value=httpx.Response(200, content=b"%PDF-1.4 binary content")
        )
        job = Job(
            id="j1",
            uid="u1",
            status="success",
            timestamp=1000,
            asset_url="https://s3.example.com/result.pdf",
        )
        with CloudLayer("key", api_version="v2") as client:
            data = client.download_job_result(job)
        assert data == b"%PDF-1.4 binary content"

    def test_no_asset_url_raises(self) -> None:
        job = Job(id="j1", uid="u1", status="success", timestamp=1000)
        with CloudLayer("key", api_version="v2") as client:
            with pytest.raises(CloudLayerValidationError, match="asset_url"):
                client.download_job_result(job)

    @respx.mock
    def test_403_raises_expired(self) -> None:
        respx.get("https://s3.example.com/result.pdf").mock(return_value=httpx.Response(403))
        job = Job(
            id="j1",
            uid="u1",
            status="success",
            timestamp=1000,
            asset_url="https://s3.example.com/result.pdf",
        )
        with CloudLayer("key", api_version="v2") as client:
            with pytest.raises(CloudLayerApiError, match="expired"):
                client.download_job_result(job)

    @respx.mock
    def test_404_raises(self) -> None:
        respx.get("https://s3.example.com/result.pdf").mock(return_value=httpx.Response(404))
        job = Job(
            id="j1",
            uid="u1",
            status="success",
            timestamp=1000,
            asset_url="https://s3.example.com/result.pdf",
        )
        with CloudLayer("key", api_version="v2") as client:
            with pytest.raises(CloudLayerApiError, match="Failed to download"):
                client.download_job_result(job)

    @respx.mock
    def test_no_auth_header_sent(self) -> None:
        route = respx.get("https://s3.example.com/result.pdf").mock(
            return_value=httpx.Response(200, content=b"data")
        )
        job = Job(
            id="j1",
            uid="u1",
            status="success",
            timestamp=1000,
            asset_url="https://s3.example.com/result.pdf",
        )
        with CloudLayer("key", api_version="v2") as client:
            client.download_job_result(job)
        assert "x-api-key" not in route.calls[0].request.headers


class TestWaitForJob:
    @respx.mock
    def test_returns_immediately_if_success(self, sample_job: dict[str, Any]) -> None:
        respx.get("https://api.cloudlayer.io/v2/jobs/job-123").mock(
            return_value=httpx.Response(200, json=sample_job)
        )
        with CloudLayer("key", api_version="v2") as client:
            job = client.wait_for_job("job-123")
        assert job.status == "success"

    @respx.mock
    def test_polls_until_success(self, sample_job: dict[str, Any]) -> None:
        pending = {"id": "job-123", "uid": "u1", "status": "pending", "timestamp": 1000}
        route = respx.get("https://api.cloudlayer.io/v2/jobs/job-123")
        route.side_effect = [
            httpx.Response(200, json=pending),
            httpx.Response(200, json=pending),
            httpx.Response(200, json=sample_job),
        ]
        with CloudLayer("key", api_version="v2") as client:
            with patch("cloudlayerio.client.time.sleep") as mock_sleep:
                job = client.wait_for_job("job-123", interval=2000)
        assert job.status == "success"
        assert mock_sleep.call_count == 2

    @respx.mock
    def test_error_status_raises(self, sample_error_job: dict[str, Any]) -> None:
        respx.get("https://api.cloudlayer.io/v2/jobs/job-error").mock(
            return_value=httpx.Response(200, json=sample_error_job)
        )
        with CloudLayer("key", api_version="v2") as client:
            with pytest.raises(CloudLayerApiError, match="Template rendering failed"):
                client.wait_for_job("job-error")

    @respx.mock
    def test_timeout_raises(self) -> None:
        pending = {"id": "j1", "uid": "u1", "status": "pending", "timestamp": 1000}
        respx.get("https://api.cloudlayer.io/v2/jobs/j1").mock(
            return_value=httpx.Response(200, json=pending)
        )
        with CloudLayer("key", api_version="v2") as client:
            with pytest.raises(CloudLayerTimeoutError):
                with patch("cloudlayerio.client.time.sleep"):
                    client.wait_for_job("j1", interval=2000, max_wait=3000)

    def test_interval_below_minimum_raises(self) -> None:
        with CloudLayer("key", api_version="v2") as client:
            with pytest.raises(CloudLayerValidationError, match="interval"):
                client.wait_for_job("j1", interval=1000)

    @respx.mock
    def test_preemptive_timeout(self) -> None:
        """Should raise timeout when elapsed + interval > max_wait."""
        pending = {"id": "j1", "uid": "u1", "status": "pending", "timestamp": 1000}
        route = respx.get("https://api.cloudlayer.io/v2/jobs/j1")
        route.side_effect = [
            httpx.Response(200, json=pending),
            httpx.Response(200, json=pending),
        ]
        with CloudLayer("key", api_version="v2") as client:
            with pytest.raises(CloudLayerTimeoutError):
                with patch("cloudlayerio.client.time.sleep"):
                    client.wait_for_job("j1", interval=5000, max_wait=6000)
