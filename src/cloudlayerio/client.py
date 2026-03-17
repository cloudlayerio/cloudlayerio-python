"""CloudLayer client classes (sync and async)."""

from __future__ import annotations

import asyncio
import time
from typing import TYPE_CHECKING, Any
from urllib.parse import urlparse

import httpx

from cloudlayerio.api import account as account_api
from cloudlayerio.api import assets as assets_api
from cloudlayerio.api import conversion as conversion_api
from cloudlayerio.api import jobs as jobs_api
from cloudlayerio.api import storage as storage_api
from cloudlayerio.api import templates as templates_api
from cloudlayerio.errors import (
    CloudLayerApiError,
    CloudLayerConfigError,
    CloudLayerTimeoutError,
    CloudLayerValidationError,
)
from cloudlayerio.http import AsyncHttpTransport, HttpTransport

if TYPE_CHECKING:
    from cloudlayerio.types.account import AccountInfo, StatusResponse
    from cloudlayerio.types.asset import Asset
    from cloudlayerio.types.job import Job
    from cloudlayerio.types.response import ConversionResult
    from cloudlayerio.types.storage import (
        StorageDetail,
        StorageListItem,
        StorageNotAllowedResponse,
    )
    from cloudlayerio.types.template import PublicTemplate


def _validate_config(
    api_key: str,
    api_version: str,
    base_url: str,
    timeout: int,
    max_retries: int,
) -> None:
    """Validate client configuration. Raises CloudLayerConfigError on invalid input."""
    if not isinstance(api_key, str) or not api_key.strip():
        raise CloudLayerConfigError("apiKey is required and must be a non-empty string")

    if api_version not in ("v1", "v2"):
        raise CloudLayerConfigError('apiVersion must be "v1" or "v2"')

    parsed = urlparse(base_url)
    if not parsed.scheme or not parsed.netloc:
        raise CloudLayerConfigError(f"baseUrl must be a valid URL, got: {base_url!r}")

    if not isinstance(timeout, int) or timeout <= 0:
        raise CloudLayerConfigError("timeout must be a positive integer (milliseconds)")

    if not isinstance(max_retries, int) or max_retries < 0 or max_retries > 5:
        raise CloudLayerConfigError("maxRetries must be an integer between 0 and 5")


class CloudLayer:
    """Synchronous CloudLayer API client.

    Usage::

        with CloudLayer("your-api-key", api_version="v2") as client:
            result = client.url_to_pdf({"url": "https://example.com"})
            print(result.data)
    """

    def __init__(
        self,
        api_key: str,
        *,
        api_version: str,
        base_url: str = "https://api.cloudlayer.io",
        timeout: int = 30000,
        max_retries: int = 2,
        headers: dict[str, str] | None = None,
    ) -> None:
        _validate_config(api_key, api_version, base_url, timeout, max_retries)

        self._api_key = api_key
        self._api_version = api_version
        self._base_url = base_url
        self._timeout = timeout
        self._max_retries = max_retries

        self._http = HttpTransport(
            api_key=api_key,
            base_url=base_url,
            api_version=api_version,
            timeout=timeout,
            max_retries=max_retries,
            headers=headers,
        )

    @property
    def api_version(self) -> str:
        """The API version this client uses."""
        return self._api_version

    @property
    def base_url(self) -> str:
        """The base URL this client targets."""
        return self._base_url

    def close(self) -> None:
        """Close the underlying HTTP client and release resources."""
        self._http.close()

    def __enter__(self) -> CloudLayer:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    # --- Conversion methods ---

    def url_to_pdf(self, options: dict[str, Any]) -> ConversionResult[Any]:
        """Convert a URL to PDF."""
        return conversion_api.url_to_pdf(self._http, options)

    def url_to_image(self, options: dict[str, Any]) -> ConversionResult[Any]:
        """Convert a URL to image."""
        return conversion_api.url_to_image(self._http, options)

    def html_to_pdf(self, options: dict[str, Any]) -> ConversionResult[Any]:
        """Convert HTML to PDF."""
        return conversion_api.html_to_pdf(self._http, options)

    def html_to_image(self, options: dict[str, Any]) -> ConversionResult[Any]:
        """Convert HTML to image."""
        return conversion_api.html_to_image(self._http, options)

    def template_to_pdf(self, options: dict[str, Any]) -> ConversionResult[Any]:
        """Convert a template to PDF."""
        return conversion_api.template_to_pdf(self._http, options)

    def template_to_image(self, options: dict[str, Any]) -> ConversionResult[Any]:
        """Convert a template to image."""
        return conversion_api.template_to_image(self._http, options)

    def docx_to_pdf(self, options: dict[str, Any]) -> ConversionResult[Any]:
        """Convert DOCX to PDF."""
        return conversion_api.docx_to_pdf(self._http, options)

    def docx_to_html(self, options: dict[str, Any]) -> ConversionResult[Any]:
        """Convert DOCX to HTML."""
        return conversion_api.docx_to_html(self._http, options)

    def pdf_to_docx(self, options: dict[str, Any]) -> ConversionResult[Any]:
        """Convert PDF to DOCX."""
        return conversion_api.pdf_to_docx(self._http, options)

    def merge_pdfs(self, options: dict[str, Any]) -> ConversionResult[Any]:
        """Merge multiple PDFs."""
        return conversion_api.merge_pdfs(self._http, options)

    # --- Data management methods ---

    def list_jobs(self) -> list[Job]:
        """List all jobs. WARNING: Returns ALL jobs, no pagination."""
        return jobs_api.list_jobs(self._http)

    def get_job(self, job_id: str) -> Job:
        """Get a single job by ID."""
        return jobs_api.get_job(self._http, job_id)

    def list_assets(self) -> list[Asset]:
        """List all assets. WARNING: Returns ALL assets, no pagination."""
        return assets_api.list_assets(self._http)

    def get_asset(self, asset_id: str) -> Asset:
        """Get a single asset by ID."""
        return assets_api.get_asset(self._http, asset_id)

    def list_storage(self) -> list[StorageListItem]:
        """List all storage configurations."""
        return storage_api.list_storage(self._http)

    def get_storage(self, storage_id: str) -> StorageDetail:
        """Get a single storage configuration."""
        return storage_api.get_storage(self._http, storage_id)

    def add_storage(self, config: dict[str, Any]) -> StorageDetail | StorageNotAllowedResponse:
        """Add a new storage configuration."""
        return storage_api.add_storage(self._http, config)

    def delete_storage(self, storage_id: str) -> None:
        """Delete a storage configuration."""
        storage_api.delete_storage(self._http, storage_id)

    def get_account(self) -> AccountInfo:
        """Get account information."""
        return account_api.get_account(self._http)

    def get_status(self) -> StatusResponse:
        """Get API status."""
        return account_api.get_status(self._http)

    def list_templates(self, options: dict[str, Any] | None = None) -> list[PublicTemplate]:
        """List public templates."""
        return templates_api.list_templates(self._http, options)

    def get_template(self, template_id: str) -> PublicTemplate:
        """Get a public template by ID."""
        return templates_api.get_template(self._http, template_id)

    # --- Utility methods ---

    def download_job_result(self, job: Job) -> bytes:
        """Download the binary result of a completed job.

        Uses a direct HTTP request (not the SDK transport) because
        asset_url is a presigned S3 URL, not a CloudLayer API endpoint.
        """
        if not job.asset_url:
            raise CloudLayerValidationError(
                "asset_url", "job has no asset_url (may not be complete or may have failed)"
            )
        response = httpx.get(job.asset_url)
        if response.status_code == 403:
            raise CloudLayerApiError(
                "Asset URL has expired or is inaccessible (403)",
                status=403,
                status_text="Forbidden",
                request_path=job.asset_url,
                request_method="GET",
            )
        if not response.is_success:
            raise CloudLayerApiError(
                f"Failed to download asset: {response.status_code}",
                status=response.status_code,
                status_text=response.reason_phrase or "",
                request_path=job.asset_url,
                request_method="GET",
            )
        return response.content

    def wait_for_job(
        self,
        job_id: str,
        *,
        interval: int = 5000,
        max_wait: int = 300000,
    ) -> Job:
        """Poll for job completion.

        Args:
            job_id: The job ID to poll.
            interval: Polling interval in milliseconds (default 5000, minimum 2000).
            max_wait: Maximum wait time in milliseconds (default 300000 = 5 minutes).

        Returns:
            The completed Job (status = "success").

        Raises:
            CloudLayerValidationError: If interval < 2000ms.
            CloudLayerTimeoutError: If max_wait exceeded.
            CloudLayerApiError: If job status is "error".
        """
        if interval < 2000:
            raise CloudLayerValidationError("interval", "must be >= 2000 milliseconds")

        interval_s = interval / 1000.0
        elapsed = 0.0

        while True:
            job = self.get_job(job_id)

            if job.status == "success":
                return job

            if job.status == "error":
                raise CloudLayerApiError(
                    f"Job failed: {job.error or 'unknown error'}",
                    status=0,
                    status_text="Job Error",
                    body={"error": job.error},
                    request_path=f"/jobs/{job_id}",
                    request_method="GET",
                )

            # Preemptive timeout check
            if elapsed + interval > max_wait:
                raise CloudLayerTimeoutError(
                    timeout=max_wait,
                    request_path=f"/jobs/{job_id}",
                    request_method="GET",
                )

            time.sleep(interval_s)
            elapsed += interval


class AsyncCloudLayer:
    """Asynchronous CloudLayer API client.

    Usage::

        async with AsyncCloudLayer("your-api-key", api_version="v2") as client:
            result = await client.url_to_pdf({"url": "https://example.com"})
            print(result.data)
    """

    def __init__(
        self,
        api_key: str,
        *,
        api_version: str,
        base_url: str = "https://api.cloudlayer.io",
        timeout: int = 30000,
        max_retries: int = 2,
        headers: dict[str, str] | None = None,
    ) -> None:
        _validate_config(api_key, api_version, base_url, timeout, max_retries)

        self._api_key = api_key
        self._api_version = api_version
        self._base_url = base_url
        self._timeout = timeout
        self._max_retries = max_retries

        self._http = AsyncHttpTransport(
            api_key=api_key,
            base_url=base_url,
            api_version=api_version,
            timeout=timeout,
            max_retries=max_retries,
            headers=headers,
        )

    @property
    def api_version(self) -> str:
        """The API version this client uses."""
        return self._api_version

    @property
    def base_url(self) -> str:
        """The base URL this client targets."""
        return self._base_url

    async def close(self) -> None:
        """Close the underlying async HTTP client and release resources."""
        await self._http.close()

    async def __aenter__(self) -> AsyncCloudLayer:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()

    # --- Conversion methods ---

    async def url_to_pdf(self, options: dict[str, Any]) -> ConversionResult[Any]:
        """Convert a URL to PDF."""
        return await conversion_api.async_url_to_pdf(self._http, options)

    async def url_to_image(self, options: dict[str, Any]) -> ConversionResult[Any]:
        """Convert a URL to image."""
        return await conversion_api.async_url_to_image(self._http, options)

    async def html_to_pdf(self, options: dict[str, Any]) -> ConversionResult[Any]:
        """Convert HTML to PDF."""
        return await conversion_api.async_html_to_pdf(self._http, options)

    async def html_to_image(self, options: dict[str, Any]) -> ConversionResult[Any]:
        """Convert HTML to image."""
        return await conversion_api.async_html_to_image(self._http, options)

    async def template_to_pdf(self, options: dict[str, Any]) -> ConversionResult[Any]:
        """Convert a template to PDF."""
        return await conversion_api.async_template_to_pdf(self._http, options)

    async def template_to_image(self, options: dict[str, Any]) -> ConversionResult[Any]:
        """Convert a template to image."""
        return await conversion_api.async_template_to_image(self._http, options)

    async def docx_to_pdf(self, options: dict[str, Any]) -> ConversionResult[Any]:
        """Convert DOCX to PDF."""
        return await conversion_api.async_docx_to_pdf(self._http, options)

    async def docx_to_html(self, options: dict[str, Any]) -> ConversionResult[Any]:
        """Convert DOCX to HTML."""
        return await conversion_api.async_docx_to_html(self._http, options)

    async def pdf_to_docx(self, options: dict[str, Any]) -> ConversionResult[Any]:
        """Convert PDF to DOCX."""
        return await conversion_api.async_pdf_to_docx(self._http, options)

    async def merge_pdfs(self, options: dict[str, Any]) -> ConversionResult[Any]:
        """Merge multiple PDFs."""
        return await conversion_api.async_merge_pdfs(self._http, options)

    # --- Data management methods ---

    async def list_jobs(self) -> list[Job]:
        """List all jobs. WARNING: Returns ALL jobs, no pagination."""
        return await jobs_api.async_list_jobs(self._http)

    async def get_job(self, job_id: str) -> Job:
        """Get a single job by ID."""
        return await jobs_api.async_get_job(self._http, job_id)

    async def list_assets(self) -> list[Asset]:
        """List all assets. WARNING: Returns ALL assets, no pagination."""
        return await assets_api.async_list_assets(self._http)

    async def get_asset(self, asset_id: str) -> Asset:
        """Get a single asset by ID."""
        return await assets_api.async_get_asset(self._http, asset_id)

    async def list_storage(self) -> list[StorageListItem]:
        """List all storage configurations."""
        return await storage_api.async_list_storage(self._http)

    async def get_storage(self, storage_id: str) -> StorageDetail:
        """Get a single storage configuration."""
        return await storage_api.async_get_storage(self._http, storage_id)

    async def add_storage(
        self, config: dict[str, Any]
    ) -> StorageDetail | StorageNotAllowedResponse:
        """Add a new storage configuration."""
        return await storage_api.async_add_storage(self._http, config)

    async def delete_storage(self, storage_id: str) -> None:
        """Delete a storage configuration."""
        await storage_api.async_delete_storage(self._http, storage_id)

    async def get_account(self) -> AccountInfo:
        """Get account information."""
        return await account_api.async_get_account(self._http)

    async def get_status(self) -> StatusResponse:
        """Get API status."""
        return await account_api.async_get_status(self._http)

    async def list_templates(self, options: dict[str, Any] | None = None) -> list[PublicTemplate]:
        """List public templates."""
        return await templates_api.async_list_templates(self._http, options)

    async def get_template(self, template_id: str) -> PublicTemplate:
        """Get a public template by ID."""
        return await templates_api.async_get_template(self._http, template_id)

    # --- Utility methods ---

    async def download_job_result(self, job: Job) -> bytes:
        """Download the binary result of a completed job (async)."""
        if not job.asset_url:
            raise CloudLayerValidationError(
                "asset_url", "job has no asset_url (may not be complete or may have failed)"
            )
        async with httpx.AsyncClient() as client:
            response = await client.get(job.asset_url)
        if response.status_code == 403:
            raise CloudLayerApiError(
                "Asset URL has expired or is inaccessible (403)",
                status=403,
                status_text="Forbidden",
                request_path=job.asset_url,
                request_method="GET",
            )
        if not response.is_success:
            raise CloudLayerApiError(
                f"Failed to download asset: {response.status_code}",
                status=response.status_code,
                status_text=response.reason_phrase or "",
                request_path=job.asset_url,
                request_method="GET",
            )
        return response.content

    async def wait_for_job(
        self,
        job_id: str,
        *,
        interval: int = 5000,
        max_wait: int = 300000,
    ) -> Job:
        """Poll for job completion (async)."""
        if interval < 2000:
            raise CloudLayerValidationError("interval", "must be >= 2000 milliseconds")

        interval_s = interval / 1000.0
        elapsed = 0.0

        while True:
            job = await self.get_job(job_id)

            if job.status == "success":
                return job

            if job.status == "error":
                raise CloudLayerApiError(
                    f"Job failed: {job.error or 'unknown error'}",
                    status=0,
                    status_text="Job Error",
                    body={"error": job.error},
                    request_path=f"/jobs/{job_id}",
                    request_method="GET",
                )

            if elapsed + interval > max_wait:
                raise CloudLayerTimeoutError(
                    timeout=max_wait,
                    request_path=f"/jobs/{job_id}",
                    request_method="GET",
                )

            await asyncio.sleep(interval_s)
            elapsed += interval
