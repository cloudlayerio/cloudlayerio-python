"""Tests for AsyncCloudLayer client."""

from __future__ import annotations

from typing import Any

import httpx
import pytest
import respx

from cloudlayerio.client import AsyncCloudLayer
from cloudlayerio.errors import CloudLayerApiError, CloudLayerValidationError
from cloudlayerio.types.job import Job


class TestAsyncConversion:
    @respx.mock
    async def test_url_to_pdf(self) -> None:
        respx.post("https://api.cloudlayer.io/v2/url/pdf").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": "j1",
                    "uid": "u1",
                    "status": "pending",
                    "timestamp": 1000,
                },
                headers={"content-type": "application/json"},
            )
        )
        async with AsyncCloudLayer("key", api_version="v2") as client:
            result = await client.url_to_pdf({"url": "https://example.com"})
        assert isinstance(result.data, Job)


class TestAsyncDataManagement:
    @respx.mock
    async def test_list_jobs(self) -> None:
        respx.get("https://api.cloudlayer.io/v2/jobs").mock(
            return_value=httpx.Response(
                200,
                json=[
                    {"id": "j1", "uid": "u1", "status": "success", "timestamp": 1000},
                ],
            )
        )
        async with AsyncCloudLayer("key", api_version="v2") as client:
            jobs = await client.list_jobs()
        assert len(jobs) == 1
        assert isinstance(jobs[0], Job)

    @respx.mock
    async def test_get_job(self, sample_job: dict[str, Any]) -> None:
        respx.get("https://api.cloudlayer.io/v2/jobs/job-123").mock(
            return_value=httpx.Response(200, json=sample_job)
        )
        async with AsyncCloudLayer("key", api_version="v2") as client:
            job = await client.get_job("job-123")
        assert job.id == "job-123"

    @respx.mock
    async def test_get_status(self) -> None:
        respx.get("https://api.cloudlayer.io/v2/getStatus").mock(
            return_value=httpx.Response(200, json={"status": "ok "})
        )
        async with AsyncCloudLayer("key", api_version="v2") as client:
            status = await client.get_status()
        assert status.status == "ok "


class TestAsyncDownload:
    @respx.mock
    async def test_download_job_result(self) -> None:
        respx.get("https://s3.example.com/result.pdf").mock(
            return_value=httpx.Response(200, content=b"%PDF-data")
        )
        job = Job(
            id="j1",
            uid="u1",
            status="success",
            timestamp=1000,
            asset_url="https://s3.example.com/result.pdf",
        )
        async with AsyncCloudLayer("key", api_version="v2") as client:
            data = await client.download_job_result(job)
        assert data == b"%PDF-data"

    async def test_no_asset_url_raises(self) -> None:
        job = Job(id="j1", uid="u1", status="success", timestamp=1000)
        async with AsyncCloudLayer("key", api_version="v2") as client:
            with pytest.raises(CloudLayerValidationError, match="asset_url"):
                await client.download_job_result(job)


class TestAsyncWaitForJob:
    @respx.mock
    async def test_wait_success(self, sample_job: dict[str, Any]) -> None:
        respx.get("https://api.cloudlayer.io/v2/jobs/job-123").mock(
            return_value=httpx.Response(200, json=sample_job)
        )
        async with AsyncCloudLayer("key", api_version="v2") as client:
            job = await client.wait_for_job("job-123")
        assert job.status == "success"

    @respx.mock
    async def test_wait_error_raises(self, sample_error_job: dict[str, Any]) -> None:
        respx.get("https://api.cloudlayer.io/v2/jobs/job-error").mock(
            return_value=httpx.Response(200, json=sample_error_job)
        )
        async with AsyncCloudLayer("key", api_version="v2") as client:
            with pytest.raises(CloudLayerApiError, match="Template rendering failed"):
                await client.wait_for_job("job-error")

    async def test_interval_below_minimum_raises(self) -> None:
        async with AsyncCloudLayer("key", api_version="v2") as client:
            with pytest.raises(CloudLayerValidationError, match="interval"):
                await client.wait_for_job("j1", interval=1999)
