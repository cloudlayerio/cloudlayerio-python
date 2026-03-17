"""Shared test fixtures for the cloudlayer.io Python SDK."""

from __future__ import annotations

from typing import Any

import pytest
import respx

from cloudlayerio.client import CloudLayer
from cloudlayerio.http import HttpTransport


@pytest.fixture
def mock_router() -> respx.MockRouter:
    """Create a respx mock router."""
    with respx.mock(base_url="https://api.cloudlayer.io") as router:
        yield router


@pytest.fixture
def transport() -> HttpTransport:
    """Create an HttpTransport for testing."""
    t = HttpTransport(
        api_key="test-key",
        base_url="https://api.cloudlayer.io",
        api_version="v2",
        timeout=30000,
        max_retries=2,
    )
    yield t
    t.close()


@pytest.fixture
def v1_transport() -> HttpTransport:
    """Create a v1 HttpTransport for testing."""
    t = HttpTransport(
        api_key="test-key",
        base_url="https://api.cloudlayer.io",
        api_version="v1",
        timeout=30000,
        max_retries=2,
    )
    yield t
    t.close()


@pytest.fixture
def client() -> CloudLayer:
    """Create a CloudLayer client for testing."""
    c = CloudLayer("test-key", api_version="v2")
    yield c
    c.close()


@pytest.fixture
def v1_client() -> CloudLayer:
    """Create a v1 CloudLayer client for testing."""
    c = CloudLayer("test-key", api_version="v1")
    yield c
    c.close()


@pytest.fixture
def sample_job() -> dict[str, Any]:
    """Sample job API response (camelCase keys)."""
    return {
        "id": "job-123",
        "uid": "user-456",
        "status": "success",
        "timestamp": 1700000000,
        "name": "test-job",
        "type": "url-pdf",
        "assetUrl": "https://s3.example.com/result.pdf",
        "workerName": "worker-1",
        "processTime": 2500,
        "processTimeCost": 0.05,
        "apiCreditCost": 0.01,
        "bandwidthCost": 0.002,
        "totalCost": 0.062,
        "size": 150000,
    }


@pytest.fixture
def sample_pending_job() -> dict[str, Any]:
    """Sample pending job API response."""
    return {
        "id": "job-pending",
        "uid": "user-456",
        "status": "pending",
        "timestamp": 1700000000,
    }


@pytest.fixture
def sample_error_job() -> dict[str, Any]:
    """Sample error job API response."""
    return {
        "id": "job-error",
        "uid": "user-456",
        "status": "error",
        "timestamp": 1700000000,
        "error": "Template rendering failed",
    }


@pytest.fixture
def sample_asset() -> dict[str, Any]:
    """Sample asset API response (camelCase keys)."""
    return {
        "uid": "user-456",
        "id": "asset-789",
        "fileId": "file-abc",
        "previewFileId": "preview-def",
        "type": "application/pdf",
        "ext": "pdf",
        "url": "https://s3.example.com/asset.pdf",
        "previewUrl": "https://s3.example.com/preview.png",
        "size": 150000,
        "timestamp": 1700000000,
        "projectId": "proj-123",
        "jobId": "job-123",
        "name": "test-document.pdf",
    }


@pytest.fixture
def sample_account() -> dict[str, Any]:
    """Sample account API response (camelCase keys)."""
    return {
        "email": "test@example.com",
        "callsLimit": 1000,
        "calls": 42,
        "storageUsed": 5000000,
        "storageLimit": 100000000,
        "subscription": "pro",
        "bytesTotal": 50000000,
        "bytesLimit": 500000000,
        "computeTimeTotal": 3600,
        "computeTimeLimit": -1,
        "subType": "usage",
        "uid": "user-456",
        "subActive": True,
        "credit": 100,
    }


@pytest.fixture
def sample_storage() -> dict[str, Any]:
    """Sample storage detail API response."""
    return {
        "data": "encrypted-config-data",
        "id": "storage-123",
        "title": "My S3 Bucket",
        "uid": "user-456",
    }


@pytest.fixture
def cl_headers() -> dict[str, str]:
    """Sample CloudLayer custom response headers."""
    return {
        "cl-worker-job-id": "wj-123",
        "cl-cluster-id": "cluster-1",
        "cl-worker": "worker-a",
        "cl-bandwidth": "15000",
        "cl-process-time": "2500",
        "cl-calls-remaining": "958",
        "cl-charged-time": "3000",
        "cl-bandwidth-cost": "0.002",
        "cl-process-time-cost": "0.05",
        "cl-api-credit-cost": "0.01",
    }
