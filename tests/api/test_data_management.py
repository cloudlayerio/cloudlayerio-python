"""Tests for data management API methods (jobs, assets, storage, account, templates)."""

from __future__ import annotations

from typing import Any

import httpx
import pytest
import respx

from cloudlayerio.client import CloudLayer
from cloudlayerio.errors import CloudLayerValidationError
from cloudlayerio.types.account import AccountInfo, StatusResponse
from cloudlayerio.types.asset import Asset
from cloudlayerio.types.job import Job
from cloudlayerio.types.storage import StorageDetail, StorageListItem, StorageNotAllowedResponse
from cloudlayerio.types.template import PublicTemplate


class TestJobsApi:
    @respx.mock
    def test_list_jobs(self, sample_job: dict[str, Any]) -> None:
        respx.get("https://api.cloudlayer.io/v2/jobs").mock(
            return_value=httpx.Response(200, json=[sample_job])
        )
        with CloudLayer("key", api_version="v2") as client:
            jobs = client.list_jobs()
        assert len(jobs) == 1
        assert isinstance(jobs[0], Job)
        assert jobs[0].id == "job-123"
        assert jobs[0].asset_url == "https://s3.example.com/result.pdf"

    @respx.mock
    def test_list_jobs_empty(self) -> None:
        respx.get("https://api.cloudlayer.io/v2/jobs").mock(
            return_value=httpx.Response(200, json=[])
        )
        with CloudLayer("key", api_version="v2") as client:
            jobs = client.list_jobs()
        assert jobs == []

    @respx.mock
    def test_get_job(self, sample_job: dict[str, Any]) -> None:
        respx.get("https://api.cloudlayer.io/v2/jobs/job-123").mock(
            return_value=httpx.Response(200, json=sample_job)
        )
        with CloudLayer("key", api_version="v2") as client:
            job = client.get_job("job-123")
        assert isinstance(job, Job)
        assert job.id == "job-123"
        assert job.worker_name == "worker-1"

    def test_get_job_empty_id_raises(self) -> None:
        with CloudLayer("key", api_version="v2") as client:
            with pytest.raises(CloudLayerValidationError, match="job_id"):
                client.get_job("")


class TestAssetsApi:
    @respx.mock
    def test_list_assets(self, sample_asset: dict[str, Any]) -> None:
        respx.get("https://api.cloudlayer.io/v2/assets").mock(
            return_value=httpx.Response(200, json=[sample_asset])
        )
        with CloudLayer("key", api_version="v2") as client:
            assets = client.list_assets()
        assert len(assets) == 1
        assert isinstance(assets[0], Asset)
        assert assets[0].uid == "user-456"
        assert assets[0].file_id == "file-abc"

    @respx.mock
    def test_get_asset(self, sample_asset: dict[str, Any]) -> None:
        respx.get("https://api.cloudlayer.io/v2/assets/asset-789").mock(
            return_value=httpx.Response(200, json=sample_asset)
        )
        with CloudLayer("key", api_version="v2") as client:
            asset = client.get_asset("asset-789")
        assert isinstance(asset, Asset)
        assert asset.preview_url == "https://s3.example.com/preview.png"

    def test_get_asset_empty_id_raises(self) -> None:
        with CloudLayer("key", api_version="v2") as client:
            with pytest.raises(CloudLayerValidationError, match="asset_id"):
                client.get_asset("")


class TestStorageApi:
    @respx.mock
    def test_list_storage(self) -> None:
        respx.get("https://api.cloudlayer.io/v2/storage").mock(
            return_value=httpx.Response(200, json=[{"id": "s1", "title": "My Bucket"}])
        )
        with CloudLayer("key", api_version="v2") as client:
            items = client.list_storage()
        assert len(items) == 1
        assert isinstance(items[0], StorageListItem)
        assert items[0].title == "My Bucket"

    @respx.mock
    def test_get_storage(self, sample_storage: dict[str, Any]) -> None:
        respx.get("https://api.cloudlayer.io/v2/storage/storage-123").mock(
            return_value=httpx.Response(200, json=sample_storage)
        )
        with CloudLayer("key", api_version="v2") as client:
            detail = client.get_storage("storage-123")
        assert isinstance(detail, StorageDetail)
        assert detail.uid == "user-456"

    @respx.mock
    def test_add_storage_success(self) -> None:
        respx.post("https://api.cloudlayer.io/v2/storage").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": "enc",
                    "id": "s-new",
                    "title": "New",
                    "uid": "u1",
                },
            )
        )
        with CloudLayer("key", api_version="v2") as client:
            result = client.add_storage(
                {
                    "title": "New",
                    "region": "us-east-1",
                    "access_key_id": "AK",
                    "secret_access_key": "SK",
                    "bucket": "my-bucket",
                }
            )
        assert isinstance(result, StorageDetail)
        assert result.id == "s-new"

    @respx.mock
    def test_add_storage_not_allowed(self) -> None:
        respx.post("https://api.cloudlayer.io/v2/storage").mock(
            return_value=httpx.Response(
                200,
                json={
                    "allowed": False,
                    "reason": "Plan does not support custom storage",
                    "statusCode": 401,
                },
            )
        )
        with CloudLayer("key", api_version="v2") as client:
            result = client.add_storage(
                {
                    "title": "T",
                    "region": "r",
                    "access_key_id": "a",
                    "secret_access_key": "s",
                    "bucket": "b",
                }
            )
        assert isinstance(result, StorageNotAllowedResponse)
        assert result.allowed is False

    @respx.mock
    def test_delete_storage(self) -> None:
        respx.delete("https://api.cloudlayer.io/v2/storage/s1").mock(
            return_value=httpx.Response(204)
        )
        with CloudLayer("key", api_version="v2") as client:
            result = client.delete_storage("s1")
        assert result is None


class TestAccountApi:
    @respx.mock
    def test_get_account(self, sample_account: dict[str, Any]) -> None:
        respx.get("https://api.cloudlayer.io/v2/account").mock(
            return_value=httpx.Response(200, json=sample_account)
        )
        with CloudLayer("key", api_version="v2") as client:
            account = client.get_account()
        assert isinstance(account, AccountInfo)
        assert account.email == "test@example.com"
        assert account.calls_limit == 1000
        assert account.sub_type == "usage"
        assert account.sub_active is True

    @respx.mock
    def test_get_status(self) -> None:
        respx.get("https://api.cloudlayer.io/v2/getStatus").mock(
            return_value=httpx.Response(200, json={"status": "ok "})
        )
        with CloudLayer("key", api_version="v2") as client:
            status = client.get_status()
        assert isinstance(status, StatusResponse)
        assert status.status == "ok "  # Trailing space preserved


class TestTemplatesApi:
    @respx.mock
    def test_list_templates(self) -> None:
        respx.get("https://api.cloudlayer.io/v2/templates").mock(
            return_value=httpx.Response(
                200,
                json=[
                    {"id": "t1", "name": "Invoice", "category": "business"},
                    {"id": "t2", "name": "Report", "category": "business"},
                ],
            )
        )
        with CloudLayer("key", api_version="v2") as client:
            templates = client.list_templates()
        assert len(templates) == 2
        assert isinstance(templates[0], PublicTemplate)
        assert templates[0].id == "t1"
        assert templates[0].extra_fields["name"] == "Invoice"

    @respx.mock
    def test_list_templates_on_v1_client_still_uses_v2_path(self) -> None:
        route = respx.get("https://api.cloudlayer.io/v2/templates").mock(
            return_value=httpx.Response(200, json=[])
        )
        with CloudLayer("key", api_version="v1") as client:
            client.list_templates()
        assert len(route.calls) == 1

    @respx.mock
    def test_get_template(self) -> None:
        respx.get("https://api.cloudlayer.io/v2/template/t1").mock(
            return_value=httpx.Response(200, json={"id": "t1", "name": "Invoice"})
        )
        with CloudLayer("key", api_version="v2") as client:
            template = client.get_template("t1")
        assert isinstance(template, PublicTemplate)
        assert template.id == "t1"

    @respx.mock
    def test_list_templates_with_options(self) -> None:
        route = respx.get("https://api.cloudlayer.io/v2/templates").mock(
            return_value=httpx.Response(200, json=[])
        )
        with CloudLayer("key", api_version="v2") as client:
            client.list_templates({"type": "pdf", "category": "business"})
        url = str(route.calls[0].request.url)
        assert "type=pdf" in url
        assert "category=business" in url
