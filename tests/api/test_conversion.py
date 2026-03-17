"""Tests for conversion API methods."""

from __future__ import annotations

import httpx
import pytest
import respx

from cloudlayerio.client import CloudLayer
from cloudlayerio.errors import CloudLayerValidationError
from cloudlayerio.types.job import Job


class TestUrlToPdf:
    @respx.mock
    def test_v2_returns_job(self) -> None:
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
        with CloudLayer("key", api_version="v2") as client:
            result = client.url_to_pdf({"url": "https://example.com"})
        assert isinstance(result.data, Job)
        assert result.data.id == "j1"
        assert result.status == 200

    @respx.mock
    def test_v1_sync_returns_bytes(self) -> None:
        respx.post("https://api.cloudlayer.io/v1/url/pdf").mock(
            return_value=httpx.Response(
                200, content=b"%PDF-1.4", headers={"content-type": "application/pdf"}
            )
        )
        with CloudLayer("key", api_version="v1") as client:
            result = client.url_to_pdf({"url": "https://example.com"})
        assert isinstance(result.data, bytes)
        assert result.data.startswith(b"%PDF")

    @respx.mock
    def test_async_mode_serialized(self) -> None:
        route = respx.post("https://api.cloudlayer.io/v2/url/pdf").mock(
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
        with CloudLayer("key", api_version="v2") as client:
            client.url_to_pdf({"url": "https://example.com", "async_mode": True, "storage": True})
        import json

        body = json.loads(route.calls[0].request.content)
        assert body["async"] is True
        assert "async_mode" not in body

    @respx.mock
    def test_cl_headers_parsed(self, cl_headers: dict[str, str]) -> None:
        respx.post("https://api.cloudlayer.io/v2/url/pdf").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": "j1",
                    "uid": "u1",
                    "status": "success",
                    "timestamp": 1000,
                },
                headers={**cl_headers, "content-type": "application/json"},
            )
        )
        with CloudLayer("key", api_version="v2") as client:
            result = client.url_to_pdf({"url": "https://example.com"})
        assert result.headers.worker_job_id == "wj-123"
        assert result.headers.bandwidth == 15000

    def test_invalid_url_raises(self) -> None:
        with CloudLayer("key", api_version="v2") as client:
            with pytest.raises(CloudLayerValidationError, match="url"):
                client.url_to_pdf({"url": "not-a-url"})

    def test_missing_url_raises(self) -> None:
        with CloudLayer("key", api_version="v2") as client:
            with pytest.raises(CloudLayerValidationError, match="required"):
                client.url_to_pdf({})


class TestUrlToImage:
    @respx.mock
    def test_returns_job(self) -> None:
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
        with CloudLayer("key", api_version="v2") as client:
            result = client.url_to_image({"url": "https://example.com"})
        assert isinstance(result.data, Job)

    def test_invalid_quality_raises(self) -> None:
        with CloudLayer("key", api_version="v2") as client:
            with pytest.raises(CloudLayerValidationError, match="quality"):
                client.url_to_image({"url": "https://example.com", "quality": 150})


class TestHtmlToPdf:
    @respx.mock
    def test_sends_html(self) -> None:
        route = respx.post("https://api.cloudlayer.io/v2/html/pdf").mock(
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
        with CloudLayer("key", api_version="v2") as client:
            client.html_to_pdf({"html": "PGh0bWw+"})
        import json

        body = json.loads(route.calls[0].request.content)
        assert body["html"] == "PGh0bWw+"

    def test_empty_html_raises(self) -> None:
        with CloudLayer("key", api_version="v2") as client:
            with pytest.raises(CloudLayerValidationError, match="html"):
                client.html_to_pdf({"html": ""})


class TestTemplateToPdf:
    @respx.mock
    def test_with_template_id(self) -> None:
        route = respx.post("https://api.cloudlayer.io/v2/template/pdf").mock(
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
        with CloudLayer("key", api_version="v2") as client:
            client.template_to_pdf({"template_id": "tmpl-123", "data": {"name": "John"}})
        import json

        body = json.loads(route.calls[0].request.content)
        assert body["templateId"] == "tmpl-123"

    def test_neither_raises(self) -> None:
        with CloudLayer("key", api_version="v2") as client:
            with pytest.raises(CloudLayerValidationError, match="required"):
                client.template_to_pdf({})


class TestDocxToPdf:
    @respx.mock
    def test_multipart_upload(self) -> None:
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
        with CloudLayer("key", api_version="v2") as client:
            result = client.docx_to_pdf({"file": b"fake-docx-bytes"})
        assert isinstance(result.data, Job)

    def test_missing_file_raises(self) -> None:
        with CloudLayer("key", api_version="v2") as client:
            with pytest.raises(CloudLayerValidationError, match="file"):
                client.docx_to_pdf({})


class TestMergePdfs:
    @respx.mock
    def test_with_batch(self) -> None:
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
        with CloudLayer("key", api_version="v2") as client:
            result = client.merge_pdfs(
                {"batch": {"urls": ["https://a.com/1.pdf", "https://b.com/2.pdf"]}}
            )
        assert isinstance(result.data, Job)
