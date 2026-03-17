"""Conversion API methods (URL, HTML, template, document, merge)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any, BinaryIO

from cloudlayerio.http import (
    AsyncHttpTransport,
    HttpTransport,
    _is_json_content_type,
    _parse_cl_headers,
    _parse_filename,
)
from cloudlayerio.types.job import Job
from cloudlayerio.types.response import ConversionResult
from cloudlayerio.utils.serialization import serialize_options
from cloudlayerio.utils.validation import (
    validate_base_options,
    validate_file_input,
    validate_html_options,
    validate_image_options,
    validate_template_options,
    validate_url_options,
)

if TYPE_CHECKING:
    import httpx

# SDK-only fields to strip before sending to API
_SDK_ONLY_FIELDS = {"file"}


def _build_conversion_result(response: httpx.Response) -> ConversionResult[Any]:
    """Parse an HTTP response into a ConversionResult."""
    cl_headers = _parse_cl_headers(response.headers)
    filename = _parse_filename(response.headers)
    content_type = response.headers.get("content-type")

    result_data: Job | bytes
    if _is_json_content_type(content_type):
        result_data = Job.from_dict(response.json())
    else:
        result_data = response.content

    return ConversionResult(
        data=result_data,
        headers=cl_headers,
        status=response.status_code,
        filename=filename,
    )


def _prepare_options(options: dict[str, Any]) -> dict[str, Any]:
    """Serialize options and strip SDK-only fields."""
    serialized = serialize_options(options)
    for field in _SDK_ONLY_FIELDS:
        serialized.pop(field, None)
    return serialized


def _prepare_file_form(
    file: Path | bytes | BinaryIO,
    options: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Build multipart form data from file and options.

    Returns (files_dict, data_dict) for httpx.
    """
    if isinstance(file, Path):
        files = {"file": (file.name, file.read_bytes())}
    elif isinstance(file, bytes):
        files = {"file": ("file", file)}
    else:
        files = {"file": ("file", file.read())}

    # Remaining options as form fields
    serialized = serialize_options(options)
    for field in _SDK_ONLY_FIELDS:
        serialized.pop(field, None)

    # Complex values need JSON serialization for form fields
    form_data: dict[str, Any] = {}
    for key, value in serialized.items():
        if isinstance(value, (dict, list)):
            form_data[key] = json.dumps(value)
        elif isinstance(value, bool):
            form_data[key] = str(value).lower()
        else:
            form_data[key] = str(value)

    return files, form_data


# --- Sync conversion methods ---


def url_to_pdf(http: HttpTransport, options: dict[str, Any]) -> ConversionResult[Any]:
    """Convert a URL to PDF."""
    validate_base_options(options)
    validate_url_options(options)
    body = _prepare_options(options)
    response = http.post("/url/pdf", body)
    return _build_conversion_result(response)


def url_to_image(http: HttpTransport, options: dict[str, Any]) -> ConversionResult[Any]:
    """Convert a URL to image."""
    validate_base_options(options)
    validate_url_options(options)
    validate_image_options(options)
    body = _prepare_options(options)
    response = http.post("/url/image", body)
    return _build_conversion_result(response)


def html_to_pdf(http: HttpTransport, options: dict[str, Any]) -> ConversionResult[Any]:
    """Convert HTML to PDF."""
    validate_base_options(options)
    validate_html_options(options)
    body = _prepare_options(options)
    response = http.post("/html/pdf", body)
    return _build_conversion_result(response)


def html_to_image(http: HttpTransport, options: dict[str, Any]) -> ConversionResult[Any]:
    """Convert HTML to image."""
    validate_base_options(options)
    validate_html_options(options)
    validate_image_options(options)
    body = _prepare_options(options)
    response = http.post("/html/image", body)
    return _build_conversion_result(response)


def template_to_pdf(http: HttpTransport, options: dict[str, Any]) -> ConversionResult[Any]:
    """Convert a template to PDF."""
    validate_base_options(options)
    validate_template_options(options)
    body = _prepare_options(options)
    response = http.post("/template/pdf", body)
    return _build_conversion_result(response)


def template_to_image(http: HttpTransport, options: dict[str, Any]) -> ConversionResult[Any]:
    """Convert a template to image."""
    validate_base_options(options)
    validate_template_options(options)
    validate_image_options(options)
    body = _prepare_options(options)
    response = http.post("/template/image", body)
    return _build_conversion_result(response)


def docx_to_pdf(http: HttpTransport, options: dict[str, Any]) -> ConversionResult[Any]:
    """Convert DOCX to PDF via multipart upload."""
    validate_base_options(options)
    validate_file_input(options)
    files, _data = _prepare_file_form(options["file"], options)
    response = http.request("POST", "/docx/pdf", files=files)
    return _build_conversion_result(response)


def docx_to_html(http: HttpTransport, options: dict[str, Any]) -> ConversionResult[Any]:
    """Convert DOCX to HTML via multipart upload."""
    validate_base_options(options)
    validate_file_input(options)
    files, _data = _prepare_file_form(options["file"], options)
    response = http.request("POST", "/docx/html", files=files)
    return _build_conversion_result(response)


def pdf_to_docx(http: HttpTransport, options: dict[str, Any]) -> ConversionResult[Any]:
    """Convert PDF to DOCX via multipart upload."""
    validate_base_options(options)
    validate_file_input(options)
    files, _data = _prepare_file_form(options["file"], options)
    response = http.request("POST", "/pdf/docx", files=files)
    return _build_conversion_result(response)


def merge_pdfs(http: HttpTransport, options: dict[str, Any]) -> ConversionResult[Any]:
    """Merge multiple PDFs."""
    validate_base_options(options)
    validate_url_options(options)
    body = _prepare_options(options)
    response = http.post("/pdf/merge", body)
    return _build_conversion_result(response)


# --- Async conversion methods ---


async def async_url_to_pdf(
    http: AsyncHttpTransport, options: dict[str, Any]
) -> ConversionResult[Any]:
    """Convert a URL to PDF (async)."""
    validate_base_options(options)
    validate_url_options(options)
    body = _prepare_options(options)
    response = await http.post("/url/pdf", body)
    return _build_conversion_result(response)


async def async_url_to_image(
    http: AsyncHttpTransport, options: dict[str, Any]
) -> ConversionResult[Any]:
    """Convert a URL to image (async)."""
    validate_base_options(options)
    validate_url_options(options)
    validate_image_options(options)
    body = _prepare_options(options)
    response = await http.post("/url/image", body)
    return _build_conversion_result(response)


async def async_html_to_pdf(
    http: AsyncHttpTransport, options: dict[str, Any]
) -> ConversionResult[Any]:
    """Convert HTML to PDF (async)."""
    validate_base_options(options)
    validate_html_options(options)
    body = _prepare_options(options)
    response = await http.post("/html/pdf", body)
    return _build_conversion_result(response)


async def async_html_to_image(
    http: AsyncHttpTransport, options: dict[str, Any]
) -> ConversionResult[Any]:
    """Convert HTML to image (async)."""
    validate_base_options(options)
    validate_html_options(options)
    validate_image_options(options)
    body = _prepare_options(options)
    response = await http.post("/html/image", body)
    return _build_conversion_result(response)


async def async_template_to_pdf(
    http: AsyncHttpTransport, options: dict[str, Any]
) -> ConversionResult[Any]:
    """Convert a template to PDF (async)."""
    validate_base_options(options)
    validate_template_options(options)
    body = _prepare_options(options)
    response = await http.post("/template/pdf", body)
    return _build_conversion_result(response)


async def async_template_to_image(
    http: AsyncHttpTransport, options: dict[str, Any]
) -> ConversionResult[Any]:
    """Convert a template to image (async)."""
    validate_base_options(options)
    validate_template_options(options)
    validate_image_options(options)
    body = _prepare_options(options)
    response = await http.post("/template/image", body)
    return _build_conversion_result(response)


async def async_docx_to_pdf(
    http: AsyncHttpTransport, options: dict[str, Any]
) -> ConversionResult[Any]:
    """Convert DOCX to PDF via multipart upload (async)."""
    validate_base_options(options)
    validate_file_input(options)
    files, _data = _prepare_file_form(options["file"], options)
    response = await http.request("POST", "/docx/pdf", files=files)
    return _build_conversion_result(response)


async def async_docx_to_html(
    http: AsyncHttpTransport, options: dict[str, Any]
) -> ConversionResult[Any]:
    """Convert DOCX to HTML via multipart upload (async)."""
    validate_base_options(options)
    validate_file_input(options)
    files, _data = _prepare_file_form(options["file"], options)
    response = await http.request("POST", "/docx/html", files=files)
    return _build_conversion_result(response)


async def async_pdf_to_docx(
    http: AsyncHttpTransport, options: dict[str, Any]
) -> ConversionResult[Any]:
    """Convert PDF to DOCX via multipart upload (async)."""
    validate_base_options(options)
    validate_file_input(options)
    files, _data = _prepare_file_form(options["file"], options)
    response = await http.request("POST", "/pdf/docx", files=files)
    return _build_conversion_result(response)


async def async_merge_pdfs(
    http: AsyncHttpTransport, options: dict[str, Any]
) -> ConversionResult[Any]:
    """Merge multiple PDFs (async)."""
    validate_base_options(options)
    validate_url_options(options)
    body = _prepare_options(options)
    response = await http.post("/pdf/merge", body)
    return _build_conversion_result(response)
