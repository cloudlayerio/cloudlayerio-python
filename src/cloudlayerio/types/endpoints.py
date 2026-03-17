"""Composite endpoint option types."""

from __future__ import annotations

from pathlib import Path
from typing import BinaryIO, Union

from typing_extensions import TypedDict

from cloudlayerio.types.html import HtmlOptions
from cloudlayerio.types.image import ImageOptions
from cloudlayerio.types.options import BaseOptions
from cloudlayerio.types.pdf import PdfOptions
from cloudlayerio.types.puppeteer import PuppeteerOptions
from cloudlayerio.types.template import TemplateOptions
from cloudlayerio.types.url import UrlOptions

FileInput = Union[Path, bytes, BinaryIO]
"""Accepted file input types for document conversion endpoints."""


class UrlToPdfOptions(UrlOptions, PuppeteerOptions, PdfOptions, BaseOptions):
    """Options for URL to PDF conversion."""


class UrlToImageOptions(UrlOptions, PuppeteerOptions, ImageOptions, BaseOptions):
    """Options for URL to image conversion."""


class HtmlToPdfOptions(HtmlOptions, PuppeteerOptions, PdfOptions, BaseOptions):
    """Options for HTML to PDF conversion."""


class HtmlToImageOptions(HtmlOptions, PuppeteerOptions, ImageOptions, BaseOptions):
    """Options for HTML to image conversion."""


class TemplateToPdfOptions(TemplateOptions, PuppeteerOptions, PdfOptions, BaseOptions):
    """Options for template to PDF conversion."""


class TemplateToImageOptions(TemplateOptions, PuppeteerOptions, ImageOptions, BaseOptions):
    """Options for template to image conversion."""


class _DocxOptionsBase(BaseOptions):
    """Base for document conversion options with file input."""

    file: FileInput


class DocxToPdfOptions(_DocxOptionsBase):
    """Options for DOCX to PDF conversion."""


class DocxToHtmlOptions(_DocxOptionsBase):
    """Options for DOCX to HTML conversion."""


class PdfToDocxOptions(_DocxOptionsBase):
    """Options for PDF to DOCX conversion."""


class MergePdfsOptions(UrlOptions, BaseOptions):
    """Options for merging multiple PDFs."""


class ListTemplatesOptions(TypedDict, total=False):
    """Options for listing public templates."""

    type: str
    category: str
    tags: str
    expand: bool
