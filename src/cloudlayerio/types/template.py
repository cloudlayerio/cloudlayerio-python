"""Template option types and public template model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from typing_extensions import TypedDict


class TemplateOptions(TypedDict, total=False):
    """Options for template-based conversions.

    Exactly one of `template_id` or `template` must be provided.
    Note: `name` is inherited from BaseOptions in composite endpoint types.
    """

    template_id: str
    template: str  # Base64-encoded template string
    data: dict[str, Any]


@dataclass
class PublicTemplate:
    """A publicly available template from the CloudLayer API."""

    id: str
    extra_fields: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PublicTemplate:
        """Create a PublicTemplate from an API response dict."""
        id_val = data.get("id", "")
        extra = {k: v for k, v in data.items() if k != "id"}
        return cls(id=id_val, extra_fields=extra)
