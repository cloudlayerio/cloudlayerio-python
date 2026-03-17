"""Async client usage example."""

import asyncio

from cloudlayerio import AsyncCloudLayer

API_KEY = "your-api-key"


async def main() -> None:
    async with AsyncCloudLayer(API_KEY, api_version="v2") as client:
        # Convert URL to PDF
        result = await client.url_to_pdf({"url": "https://example.com"})
        job = result.data
        print(f"Job created: {job.id}")

        # Wait for completion
        completed = await client.wait_for_job(job.id)
        print(f"Job completed: {completed.status}")

        # Download result
        pdf_bytes = await client.download_job_result(completed)
        with open("async_output.pdf", "wb") as f:
            f.write(pdf_bytes)

        print(f"PDF saved ({len(pdf_bytes)} bytes)")


asyncio.run(main())
