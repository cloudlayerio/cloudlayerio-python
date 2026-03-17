"""Image-specific option types."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from typing_extensions import TypedDict

if TYPE_CHECKING:
    from cloudlayerio.types.pdf import PreviewOptionsOptional

ImageType = Literal["jpg", "jpeg", "png", "svg", "webp"]
"""Supported output image formats."""


class ImageOptions(TypedDict, total=False):
    """Options specific to image output."""

    image_type: ImageType
    quality: int  # 0-100, default 80
    trim: bool
    transparent: bool
    generate_preview: PreviewOptionsOptional | bool
