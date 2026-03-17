"""HTML to PDF conversion example."""

import base64

from cloudlayerio import CloudLayer

API_KEY = "your-api-key"

# HTML must be Base64-encoded
html_content = """
<html>
<body>
  <h1>Invoice #1234</h1>
  <p>Thank you for your purchase.</p>
  <table>
    <tr><td>Widget</td><td>$10.00</td></tr>
    <tr><td>Gadget</td><td>$25.00</td></tr>
    <tr><td><strong>Total</strong></td><td><strong>$35.00</strong></td></tr>
  </table>
</body>
</html>
"""
html_b64 = base64.b64encode(html_content.encode()).decode()

with CloudLayer(API_KEY, api_version="v2") as client:
    result = client.html_to_pdf({"html": html_b64, "print_background": True})
    completed = client.wait_for_job(result.data.id)
    pdf_bytes = client.download_job_result(completed)

    with open("invoice.pdf", "wb") as f:
        f.write(pdf_bytes)

    print(f"Invoice PDF saved ({len(pdf_bytes)} bytes)")
