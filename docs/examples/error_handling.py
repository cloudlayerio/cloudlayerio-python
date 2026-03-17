"""Error handling patterns example."""

from cloudlayerio import CloudLayer
from cloudlayerio.errors import (
    CloudLayerApiError,
    CloudLayerAuthError,
    CloudLayerError,
    CloudLayerRateLimitError,
    CloudLayerTimeoutError,
    CloudLayerValidationError,
)

API_KEY = "your-api-key"

with CloudLayer(API_KEY, api_version="v2") as client:
    try:
        result = client.url_to_pdf({"url": "https://example.com"})
        job = result.data
        print(f"Job {job.id}: {job.status}")

    except CloudLayerValidationError as e:
        # Client-side validation failed (before HTTP request)
        print(f"Invalid input on field '{e.field}': {e}")

    except CloudLayerAuthError as e:
        # 401 or 403 — invalid or missing API key
        print(f"Authentication failed (HTTP {e.status}): {e}")

    except CloudLayerRateLimitError as e:
        # 429 — too many requests
        if e.retry_after:
            print(f"Rate limited. Retry after {e.retry_after} seconds.")
        else:
            print("Rate limited. Please wait before retrying.")

    except CloudLayerTimeoutError as e:
        # Request timed out
        print(f"Request timed out after {e.timeout}ms")

    except CloudLayerApiError as e:
        # Other API errors (4xx/5xx)
        print(f"API error {e.status}: {e.body}")

    except CloudLayerError as e:
        # Catch-all for any SDK error
        print(f"SDK error: {e}")
