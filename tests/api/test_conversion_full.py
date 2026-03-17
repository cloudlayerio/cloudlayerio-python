"""Additional conversion tests for full coverage."""

from __future__ import annotations

import httpx
import respx

from cloudlayerio.client import CloudLayer
from cloudlayerio.types.job import Job

JOB_RESPONSE = httpx.Response(
    200,
    json={
        "id": "j1",
        "uid": "u1",
        "status": "success",
        "timestamp": 1000,
    },
    headers={"content-type": "application/json"},
)


class TestRemainingConversions:
    @respx.mock
    def test_html_to_image(self) -> None:
        respx.post("https://api.cloudlayer.io/v2/html/image").mock(return_value=JOB_RESPONSE)
        with CloudLayer("key", api_version="v2") as client:
            result = client.html_to_image({"html": "PGh0bWw+"})
        assert isinstance(result.data, Job)

    @respx.mock
    def test_template_to_image(self) -> None:
        respx.post("https://api.cloudlayer.io/v2/template/image").mock(return_value=JOB_RESPONSE)
        with CloudLayer("key", api_version="v2") as client:
            result = client.template_to_image({"template_id": "t1"})
        assert isinstance(result.data, Job)

    @respx.mock
    def test_docx_to_html(self) -> None:
        respx.post("https://api.cloudlayer.io/v2/docx/html").mock(return_value=JOB_RESPONSE)
        with CloudLayer("key", api_version="v2") as client:
            result = client.docx_to_html({"file": b"fake-docx"})
        assert isinstance(result.data, Job)

    @respx.mock
    def test_pdf_to_docx(self) -> None:
        respx.post("https://api.cloudlayer.io/v2/pdf/docx").mock(return_value=JOB_RESPONSE)
        with CloudLayer("key", api_version="v2") as client:
            result = client.pdf_to_docx({"file": b"fake-pdf"})
        assert isinstance(result.data, Job)

    @respx.mock
    def test_filename_extracted(self) -> None:
        respx.post("https://api.cloudlayer.io/v1/url/pdf").mock(
            return_value=httpx.Response(
                200,
                content=b"%PDF",
                headers={
                    "content-type": "application/pdf",
                    "content-disposition": 'attachment; filename="output.pdf"',
                },
            )
        )
        with CloudLayer("key", api_version="v1") as client:
            result = client.url_to_pdf({"url": "https://example.com"})
        assert result.filename == "output.pdf"
