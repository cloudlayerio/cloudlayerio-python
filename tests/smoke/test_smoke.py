"""Live API smoke tests. Requires CLOUDLAYER_API_KEY env var.

Run with: pytest -m smoke
Excluded from CI by default.
"""

from __future__ import annotations

import os

import pytest

from cloudlayerio import CloudLayer

API_KEY = os.environ.get("CLOUDLAYER_API_KEY", "")
pytestmark = pytest.mark.smoke


@pytest.fixture
def live_client() -> CloudLayer:
    if not API_KEY:
        pytest.skip("CLOUDLAYER_API_KEY not set")
    c = CloudLayer(API_KEY, api_version="v2")
    yield c
    c.close()


def test_get_status(live_client: CloudLayer) -> None:
    status = live_client.get_status()
    assert status.status.strip() == "ok"


def test_get_account(live_client: CloudLayer) -> None:
    account = live_client.get_account()
    assert account.email
    assert account.uid


def test_list_templates(live_client: CloudLayer) -> None:
    templates = live_client.list_templates()
    assert isinstance(templates, list)


def test_list_jobs(live_client: CloudLayer) -> None:
    jobs = live_client.list_jobs()
    assert isinstance(jobs, list)
