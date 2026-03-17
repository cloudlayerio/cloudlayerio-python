"""Snake_case <-> camelCase serialization for API communication.

Uses an explicit FIELD_MAP for all known fields to handle non-standard
casing (e.g., preferCSSPageSize) and the `async` keyword rename.
Falls back to generic snake_to_camel for unmapped fields.
"""

from __future__ import annotations

import re
from typing import Any

# Explicit snake_case -> camelCase mapping for request serialization.
# Covers all known fields including non-standard casing.
FIELD_MAP: dict[str, str] = {
    # Python keyword rename
    "async_mode": "async",
    # BaseOptions
    "api_ver": "apiVer",
    "project_id": "projectId",
    # PuppeteerOptions
    "view_port": "viewPort",
    "wait_until": "waitUntil",
    "wait_for_frame": "waitForFrame",
    "wait_for_frame_attachment": "waitForFrameAttachment",
    "wait_for_frame_navigation": "waitForFrameNavigation",
    "wait_for_frame_images": "waitForFrameImages",
    "wait_for_frame_selector": "waitForFrameSelector",
    "wait_for_selector": "waitForSelector",
    "prefer_css_page_size": "preferCSSPageSize",  # Non-standard casing!
    "page_ranges": "pageRanges",
    "auto_scroll": "autoScroll",
    "time_zone": "timeZone",
    "emulate_media_type": "emulateMediaType",
    # Viewport
    "device_scale_factor": "deviceScaleFactor",
    "is_mobile": "isMobile",
    "has_touch": "hasTouch",
    "is_landscape": "isLandscape",
    # PdfOptions
    "print_background": "printBackground",
    "header_template": "headerTemplate",
    "footer_template": "footerTemplate",
    "generate_preview": "generatePreview",
    "maintain_aspect_ratio": "maintainAspectRatio",
    "template_string": "templateString",
    "image_style": "imageStyle",
    # ImageOptions
    "image_type": "imageType",
    # TemplateOptions
    "template_id": "templateId",
    # Cookie
    "http_only": "httpOnly",
    "same_site": "sameSite",
    # StorageParams
    "access_key_id": "accessKeyId",
    "secret_access_key": "secretAccessKey",
}

# Reverse mapping: camelCase -> snake_case for response deserialization.
REVERSE_FIELD_MAP: dict[str, str] = {v: k for k, v in FIELD_MAP.items()}

# Additional response-only fields not in request FIELD_MAP
REVERSE_FIELD_MAP.update(
    {
        "assetUrl": "asset_url",
        "workerName": "worker_name",
        "processTime": "process_time",
        "apiKeyUsed": "api_key_used",
        "processTimeCost": "process_time_cost",
        "apiCreditCost": "api_credit_cost",
        "bandwidthCost": "bandwidth_cost",
        "totalCost": "total_cost",
        "previewUrl": "preview_url",
        "assetId": "asset_id",
        "fileId": "file_id",
        "previewFileId": "preview_file_id",
        "previewExt": "preview_ext",
        "jobId": "job_id",
        "statusCode": "status_code",
        "subType": "sub_type",
        "subActive": "sub_active",
        "callsLimit": "calls_limit",
        "storageUsed": "storage_used",
        "storageLimit": "storage_limit",
        "bytesTotal": "bytes_total",
        "bytesLimit": "bytes_limit",
        "computeTimeTotal": "compute_time_total",
        "computeTimeLimit": "compute_time_limit",
    }
)


def _snake_to_camel(name: str) -> str:
    """Convert snake_case to camelCase as a generic fallback.

    Does NOT handle non-standard casing like preferCSSPageSize.
    """
    parts = name.split("_")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


def _camel_to_snake(name: str) -> str:
    """Convert camelCase to snake_case as a generic fallback."""
    s1 = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def serialize_options(options: dict[str, Any]) -> dict[str, Any]:
    """Convert a snake_case options dict to camelCase for the API.

    - Uses FIELD_MAP for known fields, generic conversion for unknown.
    - Recursively serializes nested dicts.
    - Recursively serializes dicts within lists.
    - Excludes None values (API expects missing fields, not null).
    """
    result: dict[str, Any] = {}
    for key, value in options.items():
        if value is None:
            continue

        camel_key = FIELD_MAP.get(key, _snake_to_camel(key))

        if isinstance(value, dict):
            result[camel_key] = serialize_options(value)
        elif isinstance(value, list):
            result[camel_key] = [
                serialize_options(item) if isinstance(item, dict) else item for item in value
            ]
        else:
            result[camel_key] = value

    return result


def deserialize_response(data: dict[str, Any]) -> dict[str, Any]:
    """Convert a camelCase API response dict to snake_case.

    - Uses REVERSE_FIELD_MAP for known fields, generic conversion for unknown.
    - Recursively deserializes nested dicts.
    """
    result: dict[str, Any] = {}
    for key, value in data.items():
        snake_key = REVERSE_FIELD_MAP.get(key, _camel_to_snake(key))

        if isinstance(value, dict):
            result[snake_key] = deserialize_response(value)
        elif isinstance(value, list):
            result[snake_key] = [
                deserialize_response(item) if isinstance(item, dict) else item for item in value
            ]
        else:
            result[snake_key] = value

    return result
