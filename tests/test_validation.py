"""Tests for client-side input validation."""

from __future__ import annotations

import pytest

from cloudlayerio.errors import CloudLayerValidationError
from cloudlayerio.utils.validation import (
    validate_base_options,
    validate_file_input,
    validate_html_options,
    validate_image_options,
    validate_template_options,
    validate_url_options,
)


class TestBaseOptionsValidation:
    def test_valid_options_pass(self) -> None:
        validate_base_options({"timeout": 5000, "webhook": "https://example.com/hook"})

    def test_empty_options_pass(self) -> None:
        validate_base_options({})

    def test_timeout_below_1000_raises(self) -> None:
        with pytest.raises(CloudLayerValidationError, match="timeout"):
            validate_base_options({"timeout": 999})

    def test_timeout_1000_passes(self) -> None:
        validate_base_options({"timeout": 1000})

    def test_async_without_storage_raises(self) -> None:
        with pytest.raises(CloudLayerValidationError, match="async_mode"):
            validate_base_options({"async_mode": True})

    def test_async_with_storage_bool_passes(self) -> None:
        validate_base_options({"async_mode": True, "storage": True})

    def test_async_with_storage_dict_passes(self) -> None:
        validate_base_options({"async_mode": True, "storage": {"id": "s-123"}})

    def test_storage_id_empty_raises(self) -> None:
        with pytest.raises(CloudLayerValidationError, match=r"storage\.id"):
            validate_base_options({"storage": {"id": ""}})

    def test_storage_id_whitespace_raises(self) -> None:
        with pytest.raises(CloudLayerValidationError, match=r"storage\.id"):
            validate_base_options({"storage": {"id": "   "}})

    def test_webhook_http_raises(self) -> None:
        with pytest.raises(CloudLayerValidationError, match="webhook"):
            validate_base_options({"webhook": "http://example.com/hook"})

    def test_webhook_invalid_raises(self) -> None:
        with pytest.raises(CloudLayerValidationError, match="webhook"):
            validate_base_options({"webhook": "not-a-url"})

    def test_webhook_https_passes(self) -> None:
        validate_base_options({"webhook": "https://example.com/hook"})


class TestUrlOptionsValidation:
    def test_valid_url_passes(self) -> None:
        validate_url_options({"url": "https://example.com"})

    def test_invalid_url_raises(self) -> None:
        with pytest.raises(CloudLayerValidationError, match="url"):
            validate_url_options({"url": "not-a-url"})

    def test_url_and_batch_raises(self) -> None:
        with pytest.raises(CloudLayerValidationError, match="mutually exclusive"):
            validate_url_options({"url": "https://a.com", "batch": {"urls": ["https://b.com"]}})

    def test_neither_url_nor_batch_raises(self) -> None:
        with pytest.raises(CloudLayerValidationError, match="required"):
            validate_url_options({})

    def test_batch_max_20_raises(self) -> None:
        urls = [f"https://example.com/{i}" for i in range(21)]
        with pytest.raises(CloudLayerValidationError, match="20"):
            validate_url_options({"batch": {"urls": urls}})

    def test_batch_empty_raises(self) -> None:
        with pytest.raises(CloudLayerValidationError, match="at least one"):
            validate_url_options({"batch": {"urls": []}})

    def test_batch_invalid_url_raises(self) -> None:
        with pytest.raises(CloudLayerValidationError, match=r"batch\.urls"):
            validate_url_options({"batch": {"urls": ["https://valid.com", "invalid"]}})

    def test_batch_valid_passes(self) -> None:
        validate_url_options({"batch": {"urls": ["https://a.com", "https://b.com"]}})

    def test_auth_missing_password_raises(self) -> None:
        with pytest.raises(CloudLayerValidationError, match="authentication"):
            validate_url_options({"url": "https://a.com", "authentication": {"username": "u"}})

    def test_auth_missing_username_raises(self) -> None:
        with pytest.raises(CloudLayerValidationError, match="authentication"):
            validate_url_options({"url": "https://a.com", "authentication": {"password": "p"}})

    def test_auth_valid_passes(self) -> None:
        validate_url_options(
            {
                "url": "https://a.com",
                "authentication": {"username": "u", "password": "p"},
            }
        )

    def test_cookie_missing_name_raises(self) -> None:
        with pytest.raises(CloudLayerValidationError, match="cookies"):
            validate_url_options({"url": "https://a.com", "cookies": [{"value": "v"}]})

    def test_cookie_missing_value_raises(self) -> None:
        with pytest.raises(CloudLayerValidationError, match="cookies"):
            validate_url_options({"url": "https://a.com", "cookies": [{"name": "n"}]})

    def test_cookie_valid_passes(self) -> None:
        validate_url_options(
            {
                "url": "https://a.com",
                "cookies": [{"name": "n", "value": "v"}],
            }
        )


class TestHtmlOptionsValidation:
    def test_valid_html_passes(self) -> None:
        validate_html_options({"html": "PGh0bWw+"})

    def test_empty_html_raises(self) -> None:
        with pytest.raises(CloudLayerValidationError, match="html"):
            validate_html_options({"html": ""})

    def test_missing_html_raises(self) -> None:
        with pytest.raises(CloudLayerValidationError, match="html"):
            validate_html_options({})

    def test_non_string_html_raises(self) -> None:
        with pytest.raises(CloudLayerValidationError, match="html"):
            validate_html_options({"html": 123})


class TestTemplateOptionsValidation:
    def test_template_id_passes(self) -> None:
        validate_template_options({"template_id": "tmpl-123"})

    def test_template_string_passes(self) -> None:
        validate_template_options({"template": "PGh0bWw+"})

    def test_both_raises(self) -> None:
        with pytest.raises(CloudLayerValidationError, match="not both"):
            validate_template_options({"template_id": "tmpl-123", "template": "PGh0bWw+"})

    def test_neither_raises(self) -> None:
        with pytest.raises(CloudLayerValidationError, match="required"):
            validate_template_options({})


class TestImageOptionsValidation:
    def test_valid_quality_passes(self) -> None:
        validate_image_options({"quality": 80})

    def test_quality_zero_passes(self) -> None:
        validate_image_options({"quality": 0})

    def test_quality_100_passes(self) -> None:
        validate_image_options({"quality": 100})

    def test_quality_negative_raises(self) -> None:
        with pytest.raises(CloudLayerValidationError, match="quality"):
            validate_image_options({"quality": -1})

    def test_quality_over_100_raises(self) -> None:
        with pytest.raises(CloudLayerValidationError, match="quality"):
            validate_image_options({"quality": 101})

    def test_no_quality_passes(self) -> None:
        validate_image_options({})


class TestFileInputValidation:
    def test_valid_file_passes(self) -> None:
        validate_file_input({"file": b"pdf-bytes"})

    def test_missing_file_raises(self) -> None:
        with pytest.raises(CloudLayerValidationError, match="file"):
            validate_file_input({})

    def test_none_file_raises(self) -> None:
        with pytest.raises(CloudLayerValidationError, match="file"):
            validate_file_input({"file": None})
