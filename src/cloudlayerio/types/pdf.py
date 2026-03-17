"""PDF-specific option types."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from typing_extensions import TypedDict

if TYPE_CHECKING:
    from cloudlayerio.types.puppeteer import LayoutDimension

PDFFormat = Literal[
    "letter",
    "legal",
    "tabloid",
    "ledger",
    "a0",
    "a1",
    "a2",
    "a3",
    "a4",
    "a5",
    "a6",
]
"""Supported PDF page formats."""

HeaderFooterTemplateMethod = Literal["template", "extract"]
"""Method for generating header/footer content."""


class Margin(TypedDict, total=False):
    """Page margin configuration."""

    top: LayoutDimension
    bottom: LayoutDimension
    left: LayoutDimension
    right: LayoutDimension


class HeaderFooterTemplate(TypedDict, total=False):
    """Header or footer template configuration."""

    method: HeaderFooterTemplateMethod
    selector: str
    margin: Margin
    style: dict[str, Any]
    image_style: dict[str, Any]
    template: str
    template_string: str


class PreviewOptionsBase(TypedDict):
    """Required fields for preview options."""

    quality: int


class PreviewOptionsOptional(PreviewOptionsBase, total=False):
    """Preview generation options. `quality` is required."""

    width: int
    height: int
    type: Literal["jpg", "jpeg", "png", "svg", "webp"]
    maintain_aspect_ratio: bool


class PdfOptions(TypedDict, total=False):
    """Options specific to PDF output."""

    print_background: bool
    format: PDFFormat
    margin: Margin
    header_template: HeaderFooterTemplate
    footer_template: HeaderFooterTemplate
    generate_preview: PreviewOptionsOptional | bool
