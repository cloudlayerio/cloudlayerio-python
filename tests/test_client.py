"""Tests for CloudLayer and AsyncCloudLayer client construction and config validation."""

from __future__ import annotations

import pytest

from cloudlayerio import AsyncCloudLayer, CloudLayer
from cloudlayerio.errors import CloudLayerConfigError


class TestCloudLayerConfig:
    def test_valid_v2_config(self) -> None:
        c = CloudLayer("my-key", api_version="v2")
        assert c.api_version == "v2"
        assert c.base_url == "https://api.cloudlayer.io"
        c.close()

    def test_valid_v1_config(self) -> None:
        c = CloudLayer("my-key", api_version="v1")
        assert c.api_version == "v1"
        c.close()

    def test_custom_base_url(self) -> None:
        c = CloudLayer("key", api_version="v2", base_url="https://custom.api.com")
        assert c.base_url == "https://custom.api.com"
        c.close()

    def test_custom_timeout(self) -> None:
        c = CloudLayer("key", api_version="v2", timeout=60000)
        c.close()

    def test_custom_max_retries(self) -> None:
        c = CloudLayer("key", api_version="v2", max_retries=0)
        c.close()

    def test_custom_headers(self) -> None:
        c = CloudLayer("key", api_version="v2", headers={"X-Custom": "value"})
        c.close()

    def test_empty_api_key_raises(self) -> None:
        with pytest.raises(CloudLayerConfigError, match="apiKey"):
            CloudLayer("", api_version="v2")

    def test_none_api_key_raises(self) -> None:
        with pytest.raises(CloudLayerConfigError, match="apiKey"):
            CloudLayer(None, api_version="v2")  # type: ignore[arg-type]

    def test_whitespace_api_key_raises(self) -> None:
        with pytest.raises(CloudLayerConfigError, match="apiKey"):
            CloudLayer("   ", api_version="v2")

    def test_invalid_version_raises(self) -> None:
        with pytest.raises(CloudLayerConfigError, match="apiVersion"):
            CloudLayer("key", api_version="v3")

    def test_negative_timeout_raises(self) -> None:
        with pytest.raises(CloudLayerConfigError, match="timeout"):
            CloudLayer("key", api_version="v2", timeout=-1)

    def test_zero_timeout_raises(self) -> None:
        with pytest.raises(CloudLayerConfigError, match="timeout"):
            CloudLayer("key", api_version="v2", timeout=0)

    def test_negative_retries_raises(self) -> None:
        with pytest.raises(CloudLayerConfigError, match="maxRetries"):
            CloudLayer("key", api_version="v2", max_retries=-1)

    def test_too_many_retries_raises(self) -> None:
        with pytest.raises(CloudLayerConfigError, match="maxRetries"):
            CloudLayer("key", api_version="v2", max_retries=6)

    def test_invalid_base_url_raises(self) -> None:
        with pytest.raises(CloudLayerConfigError, match="baseUrl"):
            CloudLayer("key", api_version="v2", base_url="not-a-url")

    def test_context_manager(self) -> None:
        with CloudLayer("key", api_version="v2") as c:
            assert c.api_version == "v2"

    def test_context_manager_on_exception(self) -> None:
        try:
            with CloudLayer("key", api_version="v2"):
                raise ValueError("test")
        except ValueError:
            pass  # Client should be closed


class TestAsyncCloudLayerConfig:
    def test_valid_config(self) -> None:
        ac = AsyncCloudLayer("my-key", api_version="v2")
        assert ac.api_version == "v2"
        assert ac.base_url == "https://api.cloudlayer.io"

    def test_empty_api_key_raises(self) -> None:
        with pytest.raises(CloudLayerConfigError, match="apiKey"):
            AsyncCloudLayer("", api_version="v2")

    def test_invalid_version_raises(self) -> None:
        with pytest.raises(CloudLayerConfigError, match="apiVersion"):
            AsyncCloudLayer("key", api_version="v3")

    async def test_async_context_manager(self) -> None:
        async with AsyncCloudLayer("key", api_version="v2") as c:
            assert c.api_version == "v2"
