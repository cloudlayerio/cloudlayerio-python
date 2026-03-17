"""Comprehensive async client tests covering all API methods."""

from __future__ import annotations

from typing import Any

import httpx
import respx

from cloudlayerio.client import AsyncCloudLayer
from cloudlayerio.types.asset import Asset
from cloudlayerio.types.job import Job
from cloudlayerio.types.storage import StorageDetail, StorageListItem
from cloudlayerio.types.template import PublicTemplate


class TestAsyncConversionAll:
    @respx.mock
    async def test_html_to_pdf(self) -> None:
        respx.post("https://api.cloudlayer.io/v2/html/pdf").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": "j1",
                    "uid": "u1",
                    "status": "success",
                    "timestamp": 1000,
                },
                headers={"content-type": "application/json"},
            )
        )
        async with AsyncCloudLayer("key", api_version="v2") as client:
            result = await client.html_to_pdf({"html": "PGh0bWw+"})
        assert isinstance(result.data, Job)

    @respx.mock
    async def test_html_to_image(self) -> None:
        respx.post("https://api.cloudlayer.io/v2/html/image").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": "j1",
                    "uid": "u1",
                    "status": "success",
                    "timestamp": 1000,
                },
                headers={"content-type": "application/json"},
            )
        )
        async with AsyncCloudLayer("key", api_version="v2") as client:
            result = await client.html_to_image({"html": "PGh0bWw+"})
        assert isinstance(result.data, Job)

    @respx.mock
    async def test_url_to_image(self) -> None:
        respx.post("https://api.cloudlayer.io/v2/url/image").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": "j1",
                    "uid": "u1",
                    "status": "success",
                    "timestamp": 1000,
                },
                headers={"content-type": "application/json"},
            )
        )
        async with AsyncCloudLayer("key", api_version="v2") as client:
            result = await client.url_to_image({"url": "https://example.com"})
        assert isinstance(result.data, Job)

    @respx.mock
    async def test_template_to_pdf(self) -> None:
        respx.post("https://api.cloudlayer.io/v2/template/pdf").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": "j1",
                    "uid": "u1",
                    "status": "success",
                    "timestamp": 1000,
                },
                headers={"content-type": "application/json"},
            )
        )
        async with AsyncCloudLayer("key", api_version="v2") as client:
            result = await client.template_to_pdf({"template_id": "t1"})
        assert isinstance(result.data, Job)

    @respx.mock
    async def test_template_to_image(self) -> None:
        respx.post("https://api.cloudlayer.io/v2/template/image").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": "j1",
                    "uid": "u1",
                    "status": "success",
                    "timestamp": 1000,
                },
                headers={"content-type": "application/json"},
            )
        )
        async with AsyncCloudLayer("key", api_version="v2") as client:
            result = await client.template_to_image({"template_id": "t1"})
        assert isinstance(result.data, Job)

    @respx.mock
    async def test_docx_to_pdf(self) -> None:
        respx.post("https://api.cloudlayer.io/v2/docx/pdf").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": "j1",
                    "uid": "u1",
                    "status": "success",
                    "timestamp": 1000,
                },
                headers={"content-type": "application/json"},
            )
        )
        async with AsyncCloudLayer("key", api_version="v2") as client:
            result = await client.docx_to_pdf({"file": b"fake-bytes"})
        assert isinstance(result.data, Job)

    @respx.mock
    async def test_docx_to_html(self) -> None:
        respx.post("https://api.cloudlayer.io/v2/docx/html").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": "j1",
                    "uid": "u1",
                    "status": "success",
                    "timestamp": 1000,
                },
                headers={"content-type": "application/json"},
            )
        )
        async with AsyncCloudLayer("key", api_version="v2") as client:
            result = await client.docx_to_html({"file": b"fake-bytes"})
        assert isinstance(result.data, Job)

    @respx.mock
    async def test_pdf_to_docx(self) -> None:
        respx.post("https://api.cloudlayer.io/v2/pdf/docx").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": "j1",
                    "uid": "u1",
                    "status": "success",
                    "timestamp": 1000,
                },
                headers={"content-type": "application/json"},
            )
        )
        async with AsyncCloudLayer("key", api_version="v2") as client:
            result = await client.pdf_to_docx({"file": b"fake-bytes"})
        assert isinstance(result.data, Job)

    @respx.mock
    async def test_merge_pdfs(self) -> None:
        respx.post("https://api.cloudlayer.io/v2/pdf/merge").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": "j1",
                    "uid": "u1",
                    "status": "success",
                    "timestamp": 1000,
                },
                headers={"content-type": "application/json"},
            )
        )
        async with AsyncCloudLayer("key", api_version="v2") as client:
            result = await client.merge_pdfs({"url": "https://example.com/1.pdf"})
        assert isinstance(result.data, Job)


class TestAsyncDataAll:
    @respx.mock
    async def test_list_assets(self) -> None:
        respx.get("https://api.cloudlayer.io/v2/assets").mock(
            return_value=httpx.Response(
                200,
                json=[
                    {"uid": "u1", "fileId": "f1"},
                ],
            )
        )
        async with AsyncCloudLayer("key", api_version="v2") as client:
            assets = await client.list_assets()
        assert len(assets) == 1
        assert isinstance(assets[0], Asset)

    @respx.mock
    async def test_get_asset(self) -> None:
        respx.get("https://api.cloudlayer.io/v2/assets/a1").mock(
            return_value=httpx.Response(200, json={"uid": "u1", "fileId": "f1"})
        )
        async with AsyncCloudLayer("key", api_version="v2") as client:
            asset = await client.get_asset("a1")
        assert isinstance(asset, Asset)

    @respx.mock
    async def test_list_storage(self) -> None:
        respx.get("https://api.cloudlayer.io/v2/storage").mock(
            return_value=httpx.Response(200, json=[{"id": "s1", "title": "T"}])
        )
        async with AsyncCloudLayer("key", api_version="v2") as client:
            items = await client.list_storage()
        assert len(items) == 1
        assert isinstance(items[0], StorageListItem)

    @respx.mock
    async def test_get_storage(self) -> None:
        respx.get("https://api.cloudlayer.io/v2/storage/s1").mock(
            return_value=httpx.Response(
                200, json={"data": "d", "id": "s1", "title": "T", "uid": "u1"}
            )
        )
        async with AsyncCloudLayer("key", api_version="v2") as client:
            detail = await client.get_storage("s1")
        assert isinstance(detail, StorageDetail)

    @respx.mock
    async def test_add_storage(self) -> None:
        respx.post("https://api.cloudlayer.io/v2/storage").mock(
            return_value=httpx.Response(
                200, json={"data": "d", "id": "s-new", "title": "T", "uid": "u1"}
            )
        )
        async with AsyncCloudLayer("key", api_version="v2") as client:
            result = await client.add_storage(
                {
                    "title": "T",
                    "region": "r",
                    "access_key_id": "a",
                    "secret_access_key": "s",
                    "bucket": "b",
                }
            )
        assert isinstance(result, StorageDetail)

    @respx.mock
    async def test_delete_storage(self) -> None:
        respx.delete("https://api.cloudlayer.io/v2/storage/s1").mock(
            return_value=httpx.Response(204)
        )
        async with AsyncCloudLayer("key", api_version="v2") as client:
            result = await client.delete_storage("s1")
        assert result is None

    @respx.mock
    async def test_get_account(self, sample_account: dict[str, Any]) -> None:
        respx.get("https://api.cloudlayer.io/v2/account").mock(
            return_value=httpx.Response(200, json=sample_account)
        )
        async with AsyncCloudLayer("key", api_version="v2") as client:
            account = await client.get_account()
        assert account.email == "test@example.com"

    @respx.mock
    async def test_list_templates(self) -> None:
        respx.get("https://api.cloudlayer.io/v2/templates").mock(
            return_value=httpx.Response(200, json=[{"id": "t1"}])
        )
        async with AsyncCloudLayer("key", api_version="v2") as client:
            templates = await client.list_templates()
        assert len(templates) == 1
        assert isinstance(templates[0], PublicTemplate)

    @respx.mock
    async def test_get_template(self) -> None:
        respx.get("https://api.cloudlayer.io/v2/template/t1").mock(
            return_value=httpx.Response(200, json={"id": "t1", "name": "Test"})
        )
        async with AsyncCloudLayer("key", api_version="v2") as client:
            template = await client.get_template("t1")
        assert template.id == "t1"
