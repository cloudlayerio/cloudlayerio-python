"""Public type definitions for the cloudlayer.io Python SDK."""

from __future__ import annotations

from cloudlayerio.types.account import AccountInfo, StatusResponse
from cloudlayerio.types.asset import Asset
from cloudlayerio.types.endpoints import (
    DocxToHtmlOptions,
    DocxToPdfOptions,
    FileInput,
    HtmlToImageOptions,
    HtmlToPdfOptions,
    ListTemplatesOptions,
    MergePdfsOptions,
    PdfToDocxOptions,
    TemplateToImageOptions,
    TemplateToPdfOptions,
    UrlToImageOptions,
    UrlToPdfOptions,
)
from cloudlayerio.types.error import ApiErrorBody
from cloudlayerio.types.html import HtmlOptions
from cloudlayerio.types.image import ImageOptions, ImageType
from cloudlayerio.types.job import Job, JobStatus, JobType
from cloudlayerio.types.options import BaseOptions, StorageRequestOptions
from cloudlayerio.types.pdf import (
    HeaderFooterTemplate,
    HeaderFooterTemplateMethod,
    Margin,
    PDFFormat,
    PdfOptions,
    PreviewOptionsBase,
    PreviewOptionsOptional,
)
from cloudlayerio.types.puppeteer import (
    LayoutDimension,
    PuppeteerOptions,
    Viewport,
    WaitForSelectorInnerOptions,
    WaitForSelectorOptions,
    WaitUntilOption,
)
from cloudlayerio.types.response import CloudLayerResponseHeaders, ConversionResult
from cloudlayerio.types.storage import (
    StorageDetail,
    StorageListItem,
    StorageNotAllowedResponse,
    StorageParamsOptional,
    StorageParamsRequired,
)
from cloudlayerio.types.template import PublicTemplate, TemplateOptions
from cloudlayerio.types.url import Authentication, Batch, Cookie, UrlOptions

__all__ = [
    "AccountInfo",
    "ApiErrorBody",
    "Asset",
    "Authentication",
    "BaseOptions",
    "Batch",
    "CloudLayerResponseHeaders",
    "ConversionResult",
    "Cookie",
    "DocxToHtmlOptions",
    "DocxToPdfOptions",
    "FileInput",
    "HeaderFooterTemplate",
    "HeaderFooterTemplateMethod",
    "HtmlOptions",
    "HtmlToImageOptions",
    "HtmlToPdfOptions",
    "ImageOptions",
    "ImageType",
    "Job",
    "JobStatus",
    "JobType",
    "LayoutDimension",
    "ListTemplatesOptions",
    "Margin",
    "MergePdfsOptions",
    "PDFFormat",
    "PdfOptions",
    "PdfToDocxOptions",
    "PreviewOptionsBase",
    "PreviewOptionsOptional",
    "PublicTemplate",
    "PuppeteerOptions",
    "StatusResponse",
    "StorageDetail",
    "StorageListItem",
    "StorageNotAllowedResponse",
    "StorageParamsOptional",
    "StorageParamsRequired",
    "StorageRequestOptions",
    "TemplateOptions",
    "TemplateToImageOptions",
    "TemplateToPdfOptions",
    "UrlOptions",
    "UrlToImageOptions",
    "UrlToPdfOptions",
    "Viewport",
    "WaitForSelectorInnerOptions",
    "WaitForSelectorOptions",
    "WaitUntilOption",
]
