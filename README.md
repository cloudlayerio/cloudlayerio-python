# cloudlayer.io Python SDK

[![PyPI version](https://img.shields.io/pypi/v/cloudlayerio.svg)](https://pypi.org/project/cloudlayerio/)
[![Python versions](https://img.shields.io/pypi/pyversions/cloudlayerio.svg)](https://pypi.org/project/cloudlayerio/)
[![License](https://img.shields.io/pypi/l/cloudlayerio.svg)](https://github.com/cloudlayerio/cloudlayerio-python/blob/main/LICENSE)
[![CI](https://github.com/cloudlayerio/cloudlayerio-python/actions/workflows/ci.yml/badge.svg)](https://github.com/cloudlayerio/cloudlayerio-python/actions/workflows/ci.yml)

Official Python SDK for the [cloudlayer.io](https://cloudlayer.io) document generation API. Convert URLs, HTML, and templates to PDF and images.

## Installation

```bash
pip install cloudlayerio
```

**Requirements:** Python 3.9+

## Quick Start

```python
from cloudlayerio import CloudLayer

with CloudLayer("your-api-key", api_version="v2") as client:
    # Convert a URL to PDF
    result = client.url_to_pdf({"url": "https://example.com"})
    job = result.data

    # Wait for completion and download
    completed = client.wait_for_job(job.id)
    pdf_bytes = client.download_job_result(completed)

    with open("output.pdf", "wb") as f:
        f.write(pdf_bytes)
```

## API Version Differences

The SDK requires you to choose an API version:

| | v1 | v2 |
|---|---|---|
| **Default mode** | Synchronous (returns binary) | Asynchronous (returns Job) |
| **Sync response** | Raw binary (PDF/image bytes) | JSON Job object |
| **Binary access** | Direct from `result.data` | Via `download_job_result()` |
| **Endpoint prefix** | `/v1/` | `/v2/` |

**Recommendation:** Use v2 for new projects.

## Configuration

```python
from cloudlayerio import CloudLayer

client = CloudLayer(
    "your-api-key",
    api_version="v2",              # Required: "v1" or "v2"
    base_url="https://api.cloudlayer.io",  # Default
    timeout=30000,                 # Request timeout in ms (default: 30000)
    max_retries=2,                 # Retry count for data endpoints (default: 2, max: 5)
    headers={"X-Custom": "value"}, # Additional headers (optional)
)
```

## Conversion Methods

### URL to PDF / Image

```python
# URL to PDF
result = client.url_to_pdf({"url": "https://example.com"})

# URL to Image
result = client.url_to_image({
    "url": "https://example.com",
    "image_type": "png",
    "quality": 90,
})

# With browser options
result = client.url_to_pdf({
    "url": "https://example.com",
    "print_background": True,
    "format": "a4",
    "margin": {"top": "20px", "bottom": "20px"},
    "wait_until": "networkidle0",
})
```

### HTML to PDF / Image

```python
import base64

html = base64.b64encode(b"<h1>Hello World</h1>").decode()

result = client.html_to_pdf({"html": html})
result = client.html_to_image({"html": html, "image_type": "png"})
```

### Template Rendering

```python
# Using a template ID
result = client.template_to_pdf({
    "template_id": "tmpl-123",
    "data": {"name": "John", "amount": "$100"},
})

# Using inline Base64 template
result = client.template_to_pdf({
    "template": base64_encoded_template,
    "data": {"items": [{"name": "Widget", "qty": 5}]},
})
```

### Document Conversion

```python
from pathlib import Path

# DOCX to PDF (file upload)
result = client.docx_to_pdf({"file": Path("document.docx")})

# Also accepts bytes
result = client.docx_to_pdf({"file": docx_bytes})

# DOCX to HTML
result = client.docx_to_html({"file": Path("document.docx")})

# PDF to DOCX
result = client.pdf_to_docx({"file": Path("document.pdf")})
```

### PDF Merge

```python
result = client.merge_pdfs({
    "batch": {
        "urls": [
            "https://example.com/doc1.pdf",
            "https://example.com/doc2.pdf",
        ]
    }
})
```

## Async Mode & Job Polling

### v2 Async (default)

```python
# v2 returns a Job object
result = client.url_to_pdf({"url": "https://example.com"})
job = result.data  # Job with status="pending"

# Poll until complete
completed = client.wait_for_job(job.id, interval=5000, max_wait=300000)

# Download the result
pdf_bytes = client.download_job_result(completed)
```

### v2 with explicit async + storage

```python
result = client.url_to_pdf({
    "url": "https://example.com",
    "async_mode": True,
    "storage": True,
})
```

## Data Management

```python
# Jobs
jobs = client.list_jobs()           # WARNING: returns ALL jobs
job = client.get_job("job-id")

# Assets
assets = client.list_assets()       # WARNING: returns ALL assets
asset = client.get_asset("asset-id")

# Storage
storages = client.list_storage()
detail = client.get_storage("storage-id")
result = client.add_storage({
    "title": "My S3",
    "region": "us-east-1",
    "access_key_id": "AKIA...",
    "secret_access_key": "...",
    "bucket": "my-bucket",
})
client.delete_storage("storage-id")

# Account
account = client.get_account()
status = client.get_status()

# Templates (public, no auth required)
templates = client.list_templates()
template = client.get_template("template-id")
```

## Async Client

```python
import asyncio
from cloudlayerio import AsyncCloudLayer

async def main():
    async with AsyncCloudLayer("your-api-key", api_version="v2") as client:
        result = await client.url_to_pdf({"url": "https://example.com"})
        job = result.data

        completed = await client.wait_for_job(job.id)
        pdf_bytes = await client.download_job_result(completed)

asyncio.run(main())
```

All methods on `AsyncCloudLayer` are `async` and return the same types as the sync client.

## Error Handling

```python
from cloudlayerio import CloudLayer
from cloudlayerio.errors import (
    CloudLayerError,          # Base for all errors
    CloudLayerConfigError,    # Invalid client configuration
    CloudLayerValidationError,# Client-side input validation
    CloudLayerApiError,       # HTTP 4xx/5xx responses
    CloudLayerAuthError,      # 401/403 authentication errors
    CloudLayerRateLimitError, # 429 rate limiting
    CloudLayerTimeoutError,   # Request timeouts
    CloudLayerNetworkError,   # DNS/connection failures
)

try:
    result = client.url_to_pdf({"url": "https://example.com"})
except CloudLayerAuthError as e:
    print(f"Auth failed: {e} (status={e.status})")
except CloudLayerRateLimitError as e:
    print(f"Rate limited, retry after {e.retry_after}s")
except CloudLayerTimeoutError as e:
    print(f"Timed out after {e.timeout}ms")
except CloudLayerApiError as e:
    print(f"API error {e.status}: {e.body}")
except CloudLayerError as e:
    print(f"SDK error: {e}")
```

## Performance Notes

- `list_jobs()` and `list_assets()` return **ALL** records (no pagination). Use sparingly.
- `wait_for_job()` uses a 5-second default polling interval to minimize backend costs. Minimum interval is 2 seconds.
- Conversion endpoints are **not** automatically retried (they are expensive operations).
- Data endpoints (jobs, assets, storage, account) **are** retried on 429/5xx errors.
- Always use the context manager (`with`/`async with`) to ensure connections are cleaned up.

## Other SDKs

- **JavaScript/TypeScript:** [@cloudlayerio/sdk](https://www.npmjs.com/package/@cloudlayerio/sdk) ([GitHub](https://github.com/cloudlayerio/cloudlayerio-js))
- **Go:** [cloudlayerio-go](https://pkg.go.dev/github.com/cloudlayerio/cloudlayerio-go) ([GitHub](https://github.com/cloudlayerio/cloudlayerio-go))
- **PHP:** [cloudlayerio/cloudlayerio-php](https://packagist.org/packages/cloudlayerio/cloudlayerio-php) ([GitHub](https://github.com/cloudlayerio/cloudlayerio-php))
- **.NET C#:** [cloudlayerio-dotnet](https://www.nuget.org/packages/cloudlayerio-dotnet/) ([GitHub](https://github.com/cloudlayerio/cloudlayerio-dotnet))

## License

Apache-2.0 - see [LICENSE](LICENSE) for details.
