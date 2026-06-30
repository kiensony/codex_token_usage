from __future__ import annotations

import sys
from typing import TextIO

from .config import validate_lightness
from .models import BarSegment, ThemeConfig
from .presets import PRESETS, RGB

def theme_palette(config: ThemeConfig) -> tuple[RGB, ...]:
    if not config.enabled:
        return ()
    colors = PRESETS.get(config.preset)
    if not colors:
        return ()
    return tuple(adjust_lightness(color, config.lightness) for color in colors)


def adjust_lightness(rgb: RGB, lightness: float) -> RGB:
    validate_lightness(lightness)
    return tuple(max(0, min(255, round(channel * lightness))) for channel in rgb)  # type: ignore[return-value]


def filled_bar_width(value: int, max_value: int, width: int) -> int:
    if width <= 0 or max_value <= 0 or value <= 0:
        return 0
    return min(width, max(1, round((value / max_value) * width)))


def plain_bar(
    value: int,
    max_value: int,
    width: int,
    fill_char: str = "#",
    empty_char: str = ".",
) -> str:
    filled = filled_bar_width(value, max_value, width)
    return fill_char * filled + empty_char * max(0, width - filled)


def themed_bar_segments(
    value: int,
    max_value: int,
    width: int,
    config: ThemeConfig,
    fill_char: str = "#",
    empty_char: str = ".",
) -> list[BarSegment]:
    if width <= 0:
        return []

    filled = filled_bar_width(value, max_value, width)
    palette = theme_palette(config)
    if not palette or filled <= 0:
        return [
            BarSegment(
                plain_bar(
                    value,
                    max_value,
                    width,
                    fill_char=fill_char,
                    empty_char=empty_char,
                )
            )
        ]

    segments: list[BarSegment] = []
    current_color_index: int | None = None
    current_rgb: RGB | None = None
    current_text: list[str] = []

    for index in range(filled):
        color_index = min(len(palette) - 1, (index * len(palette)) // filled)
        rgb = palette[color_index]
        if current_color_index is None:
            current_color_index = color_index
            current_rgb = rgb
        if color_index != current_color_index:
            segments.append(
                BarSegment(
                    text="".join(current_text),
                    color_index=current_color_index,
                    rgb=current_rgb,
                )
            )
            current_text = []
            current_color_index = color_index
            current_rgb = rgb
        current_text.append(fill_char)

    if current_text and current_color_index is not None:
        segments.append(
            BarSegment(
                text="".join(current_text),
                color_index=current_color_index,
                rgb=current_rgb,
            )
        )

    empty_width = width - filled
    if empty_width > 0:
        segments.append(BarSegment(empty_char * empty_width))
    return segments


def themed_ansi_bar(
    value: int,
    max_value: int,
    width: int,
    config: ThemeConfig,
    fill_char: str = "#",
    empty_char: str = " ",
) -> str:
    parts = []
    for segment in themed_bar_segments(
        value,
        max_value,
        width,
        config,
        fill_char=fill_char,
        empty_char=empty_char,
    ):
        if segment.rgb is None:
            parts.append(segment.text)
        else:
            parts.append(ansi_wrap(segment.text, segment.rgb, config.color_mode))
    return "".join(parts)


def ansi_wrap(text: str, rgb: RGB, color_mode: str = "8bit") -> str:
    if not text:
        return text
    if color_mode == "rgb":
        r, g, b = rgb
        return f"\x1b[38;2;{r};{g};{b}m{text}\x1b[0m"
    color = rgb_to_ansi256(rgb)
    return f"\x1b[38;5;{color}m{text}\x1b[0m"


def rgb_to_ansi256(rgb: RGB) -> int:
    r, g, b = rgb
    if r == g == b:
        if r < 8:
            return 16
        if r > 248:
            return 231
        return round(((r - 8) / 247) * 24) + 232
    red = round((r / 255) * 5)
    green = round((g / 255) * 5)
    blue = round((b / 255) * 5)
    return 16 + 36 * red + 6 * green + blue


def rgb_to_basic_color(rgb: RGB) -> int:
    candidates = (
        (0, (0, 0, 0)),
        (1, (205, 0, 0)),
        (2, (0, 205, 0)),
        (3, (205, 205, 0)),
        (4, (0, 0, 238)),
        (5, (205, 0, 205)),
        (6, (0, 205, 205)),
        (7, (229, 229, 229)),
    )
    return min(
        candidates,
        key=lambda item: sum((channel - target) ** 2 for channel, target in zip(rgb, item[1])),
    )[0]


def should_use_ansi_color(policy: str, stream: TextIO = sys.stdout) -> bool:
    if policy == "always":
        return True
    if policy == "never":
        return False
    return bool(getattr(stream, "isatty", lambda: False)())


def preview_theme(config: ThemeConfig, width: int = 36) -> str:
    if not config.enabled:
        return "plain: " + plain_bar(1, 1, width)
    return f"{config.preset}: " + themed_ansi_bar(1, 1, width, config)
