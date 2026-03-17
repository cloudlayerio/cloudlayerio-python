"""URL to PDF conversion example (v2)."""

from cloudlayerio import CloudLayer

API_KEY = "your-api-key"

with CloudLayer(API_KEY, api_version="v2") as client:
    # Convert URL to PDF
    result = client.url_to_pdf({
        "url": "https://example.com",
        "print_background": True,
        "format": "a4",
        "margin": {"top": "20px", "bottom": "20px", "left": "20px", "right": "20px"},
    })

    job = result.data
    print(f"Job created: {job.id} (status: {job.status})")

    # Wait for the job to complete
    completed = client.wait_for_job(job.id)
    print(f"Job completed: {completed.id}")

    # Download the PDF
    pdf_bytes = client.download_job_result(completed)
    with open("output.pdf", "wb") as f:
        f.write(pdf_bytes)

    print(f"PDF saved ({len(pdf_bytes)} bytes)")
