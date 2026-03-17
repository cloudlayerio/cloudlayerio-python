"""Tests for snake_case <-> camelCase serialization."""

from __future__ import annotations

from cloudlayerio.utils.serialization import deserialize_response, serialize_options


class TestSerializeOptions:
    def test_basic_fields(self) -> None:
        result = serialize_options({"url": "https://example.com", "print_background": True})
        assert result == {"url": "https://example.com", "printBackground": True}

    def test_async_mode_becomes_async(self) -> None:
        result = serialize_options({"async_mode": True})
        assert result == {"async": True}
        assert "async_mode" not in result

    def test_prefer_css_page_size_casing(self) -> None:
        result = serialize_options({"prefer_css_page_size": True})
        assert result == {"preferCSSPageSize": True}

    def test_none_values_excluded(self) -> None:
        result = serialize_options({"url": "https://a.com", "timeout": None, "filename": None})
        assert result == {"url": "https://a.com"}

    def test_nested_dict_serialized(self) -> None:
        result = serialize_options(
            {
                "view_port": {"width": 1920, "height": 1080, "device_scale_factor": 2.0},
            }
        )
        assert result == {"viewPort": {"width": 1920, "height": 1080, "deviceScaleFactor": 2.0}}

    def test_list_of_dicts_serialized(self) -> None:
        result = serialize_options(
            {
                "cookies": [{"name": "s", "value": "v", "http_only": True}],
            }
        )
        assert result == {"cookies": [{"name": "s", "value": "v", "httpOnly": True}]}

    def test_list_of_primitives_unchanged(self) -> None:
        result = serialize_options({"batch": {"urls": ["https://a.com", "https://b.com"]}})
        assert result == {"batch": {"urls": ["https://a.com", "https://b.com"]}}

    def test_unknown_field_generic_conversion(self) -> None:
        result = serialize_options({"my_custom_field": "value"})
        assert result == {"myCustomField": "value"}

    def test_deeply_nested(self) -> None:
        result = serialize_options(
            {
                "header_template": {
                    "margin": {"top": "20px"},
                    "image_style": {"max_width": "100%"},
                },
            }
        )
        assert result["headerTemplate"]["margin"] == {"top": "20px"}
        assert result["headerTemplate"]["imageStyle"] == {"maxWidth": "100%"}


class TestDeserializeResponse:
    def test_basic_fields(self) -> None:
        result = deserialize_response(
            {"assetUrl": "https://s3.example.com/file.pdf", "workerName": "w1"}
        )
        assert result == {"asset_url": "https://s3.example.com/file.pdf", "worker_name": "w1"}

    def test_unknown_field_generic_conversion(self) -> None:
        result = deserialize_response({"someNewField": "value"})
        assert result == {"some_new_field": "value"}

    def test_nested_dict(self) -> None:
        result = deserialize_response({"params": {"templateId": "t1"}})
        assert result == {"params": {"template_id": "t1"}}

    def test_list_of_dicts(self) -> None:
        result = deserialize_response({"items": [{"fileId": "f1"}, {"fileId": "f2"}]})
        assert result == {"items": [{"file_id": "f1"}, {"file_id": "f2"}]}

    def test_passthrough_simple_fields(self) -> None:
        result = deserialize_response({"id": "123", "status": "success", "timestamp": 1000})
        assert result == {"id": "123", "status": "success", "timestamp": 1000}


class TestRoundTrip:
    def test_known_fields_round_trip(self) -> None:
        original = {
            "print_background": True,
            "prefer_css_page_size": False,
            "image_type": "png",
            "template_id": "t1",
        }
        serialized = serialize_options(original)
        deserialized = deserialize_response(serialized)
        assert deserialized == original
