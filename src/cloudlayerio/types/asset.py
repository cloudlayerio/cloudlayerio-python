"""Asset response model."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# Fields in the Asset dataclass
_ASSET_FIELDS = {
    "uid",
    "id",
    "file_id",
    "preview_file_id",
    "type",
    "ext",
    "preview_ext",
    "url",
    "preview_url",
    "size",
    "timestamp",
    "project_id",
    "job_id",
    "name",
}

# camelCase -> snake_case mapping for Asset response deserialization
_ASSET_FIELD_MAP: dict[str, str] = {
    "fileId": "file_id",
    "previewFileId": "preview_file_id",
    "previewExt": "preview_ext",
    "previewUrl": "preview_url",
    "projectId": "project_id",
    "jobId": "job_id",
}


@dataclass
class Asset:
    """A generated asset (file) from the CloudLayer API."""

    uid: str
    file_id: str
    id: str | None = None
    preview_file_id: str | None = None
    type: str | None = None
    ext: str | None = None
    preview_ext: str | None = None
    url: str | None = None
    preview_url: str | None = None
    size: int | None = None
    timestamp: int | None = None
    project_id: str | None = None
    job_id: str | None = None
    name: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Asset:
        """Create an Asset from an API response dict (camelCase keys)."""
        converted: dict[str, Any] = {}
        for key, value in data.items():
            snake_key = _ASSET_FIELD_MAP.get(key, key)
            if snake_key in _ASSET_FIELDS:
                converted[snake_key] = value
        return cls(**converted)
