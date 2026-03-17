"""Puppeteer/browser option types."""

from __future__ import annotations

from typing import Literal, Union

from typing_extensions import TypedDict

LayoutDimension = Union[str, int]
"""A CSS dimension value — either a string like "100px" or a number of pixels."""

WaitUntilOption = Literal["load", "domcontentloaded", "networkidle0", "networkidle2"]
"""When to consider navigation complete."""


class WaitForSelectorInnerOptions(TypedDict, total=False):
    """Inner options for wait-for-selector."""

    visible: bool
    hidden: bool
    timeout: int


class WaitForSelectorOptions(TypedDict, total=False):
    """Wait for a DOM selector before proceeding."""

    selector: str
    options: WaitForSelectorInnerOptions


class Viewport(TypedDict, total=False):
    """Browser viewport configuration."""

    width: int
    height: int
    device_scale_factor: float
    is_mobile: bool
    has_touch: bool
    is_landscape: bool


class PuppeteerOptions(TypedDict, total=False):
    """Puppeteer browser options for URL, HTML, and template conversions."""

    wait_until: WaitUntilOption
    wait_for_frame: bool
    wait_for_frame_attachment: bool
    wait_for_frame_navigation: WaitUntilOption
    wait_for_frame_images: bool
    wait_for_frame_selector: WaitForSelectorOptions
    wait_for_selector: WaitForSelectorOptions
    prefer_css_page_size: bool
    scale: float
    height: LayoutDimension
    width: LayoutDimension
    landscape: bool
    page_ranges: str
    auto_scroll: bool
    view_port: Viewport
    time_zone: str
    emulate_media_type: Literal["screen", "print"] | None
