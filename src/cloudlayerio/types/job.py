"""Job response model."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

JobType = Literal[
    "url-image",
    "url-pdf",
    "html-image",
    "html-pdf",
    "template-pdf",
    "template-image",
    "docx-pdf",
    "docx-html",
    "image-pdf",
    "pdf-image",
    "pdf-docx",
    "merge-pdf",
]
"""Supported job types."""

JobStatus = Literal["pending", "success", "error"]
"""Job processing status."""

# Fields in the Job dataclass, for filtering unknown API response keys
_JOB_FIELDS = {
    "id",
    "uid",
    "status",
    "timestamp",
    "name",
    "type",
    "worker_name",
    "process_time",
    "api_key_used",
    "process_time_cost",
    "api_credit_cost",
    "bandwidth_cost",
    "total_cost",
    "size",
    "params",
    "asset_url",
    "preview_url",
    "self_link",
    "asset_id",
    "project_id",
    "error",
}

# camelCase -> snake_case mapping for Job response deserialization
_JOB_FIELD_MAP: dict[str, str] = {
    "workerName": "worker_name",
    "processTime": "process_time",
    "apiKeyUsed": "api_key_used",
    "processTimeCost": "process_time_cost",
    "apiCreditCost": "api_credit_cost",
    "bandwidthCost": "bandwidth_cost",
    "totalCost": "total_cost",
    "assetUrl": "asset_url",
    "previewUrl": "preview_url",
    "self": "self_link",
    "assetId": "asset_id",
    "projectId": "project_id",
}


@dataclass
class Job:
    """A document generation job returned by the CloudLayer API."""

    id: str
    status: str  # JobStatus at runtime
    uid: str = ""
    timestamp: int = 0
    name: str | None = None
    type: str | None = None  # JobType at runtime
    worker_name: str | None = None
    process_time: int | None = None
    api_key_used: str | None = None
    process_time_cost: float | None = None
    api_credit_cost: float | None = None
    bandwidth_cost: float | None = None
    total_cost: float | None = None
    size: int | None = None
    params: dict[str, Any] | None = None
    asset_url: str | None = None
    preview_url: str | None = None
    self_link: str | None = None  # "self" is a Python keyword
    asset_id: str | None = None
    project_id: str | None = None
    error: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Job:
        """Create a Job from an API response dict (camelCase keys)."""
        converted: dict[str, Any] = {}
        for key, value in data.items():
            snake_key = _JOB_FIELD_MAP.get(key, key)
            if snake_key in _JOB_FIELDS:
                converted[snake_key] = value
        return cls(**converted)
