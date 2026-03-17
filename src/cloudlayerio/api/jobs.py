"""Jobs API methods."""

from __future__ import annotations

from typing import TYPE_CHECKING

from cloudlayerio.errors import CloudLayerValidationError
from cloudlayerio.types.job import Job

if TYPE_CHECKING:
    from cloudlayerio.http import AsyncHttpTransport, HttpTransport


def list_jobs(http: HttpTransport) -> list[Job]:
    """List all jobs. WARNING: Returns ALL jobs, no pagination."""
    response = http.get("/jobs", retryable=True)
    return [Job.from_dict(item) for item in response.json()]


def get_job(http: HttpTransport, job_id: str) -> Job:
    """Get a single job by ID."""
    if not job_id or not isinstance(job_id, str):
        raise CloudLayerValidationError("job_id", "must be a non-empty string")
    response = http.get(f"/jobs/{job_id}", retryable=True)
    return Job.from_dict(response.json())


async def async_list_jobs(http: AsyncHttpTransport) -> list[Job]:
    """List all jobs (async). WARNING: Returns ALL jobs, no pagination."""
    response = await http.get("/jobs", retryable=True)
    return [Job.from_dict(item) for item in response.json()]


async def async_get_job(http: AsyncHttpTransport, job_id: str) -> Job:
    """Get a single job by ID (async)."""
    if not job_id or not isinstance(job_id, str):
        raise CloudLayerValidationError("job_id", "must be a non-empty string")
    response = await http.get(f"/jobs/{job_id}", retryable=True)
    return Job.from_dict(response.json())
