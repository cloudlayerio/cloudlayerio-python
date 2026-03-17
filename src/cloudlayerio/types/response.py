"""Conversion result and response header types."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class CloudLayerResponseHeaders:
    """Parsed CloudLayer custom response headers (cl-* headers)."""

    worker_job_id: str | None = None
    cluster_id: str | None = None
    worker: str | None = None
    bandwidth: int | None = None
    process_time: int | None = None
    calls_remaining: int | None = None
    charged_time: int | None = None
    bandwidth_cost: float | None = None
    process_time_cost: float | None = None
    api_credit_cost: float | None = None

    @classmethod
    def from_headers(cls, headers: dict[str, str]) -> CloudLayerResponseHeaders:
        """Parse CloudLayer custom headers from an HTTP response."""

        def _int(key: str) -> int | None:
            val = headers.get(key)
            if val is None:
                return None
            try:
                return int(val)
            except (ValueError, TypeError):
                return None

        def _float(key: str) -> float | None:
            val = headers.get(key)
            if val is None:
                return None
            try:
                return float(val)
            except (ValueError, TypeError):
                return None

        return cls(
            worker_job_id=headers.get("cl-worker-job-id"),
            cluster_id=headers.get("cl-cluster-id"),
            worker=headers.get("cl-worker"),
            bandwidth=_int("cl-bandwidth"),
            process_time=_int("cl-process-time"),
            calls_remaining=_int("cl-calls-remaining"),
            charged_time=_int("cl-charged-time"),
            bandwidth_cost=_float("cl-bandwidth-cost"),
            process_time_cost=_float("cl-process-time-cost"),
            api_credit_cost=_float("cl-api-credit-cost"),
        )


@dataclass
class ConversionResult(Generic[T]):
    """Result of a conversion API call.

    For v2: `data` is a `Job` object.
    For v1 sync: `data` is `bytes` (raw PDF/image).
    """

    data: T
    headers: CloudLayerResponseHeaders
    status: int
    filename: str | None = None
