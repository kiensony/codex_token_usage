from __future__ import annotations

import curses

from ..theme import (
    BarSegment,
    RGB,
    rgb_to_ansi256,
    rgb_to_basic_color,
    theme_palette,
    themed_bar_segments,
)
from .formatting import usage_bar


class ThemeRendererMixin:

    def init_theme_colors(self) -> None:
        palette = theme_palette(self.options.theme)
        self.preview_pairs = {}
        if not palette:
            return
        try:
            if not curses.has_colors():
                return
            curses.start_color()
            background = -1
            try:
                curses.use_default_colors()
            except curses.error:
                background = 0
            max_pairs = max(0, getattr(curses, "COLOR_PAIRS", 0) - 1)
            for index, rgb in enumerate(palette[:max_pairs], start=1):
                foreground = (
                    rgb_to_ansi256(rgb)
                    if getattr(curses, "COLORS", 0) >= 256
                    else rgb_to_basic_color(rgb)
                )
                try:
                    curses.init_pair(index, foreground, background)
                except curses.error:
                    if background == -1:
                        curses.init_pair(index, foreground, 0)
                    else:
                        raise
                self.theme_pairs.append(index)
        except curses.error:
            self.theme_pairs = []
        if self.theme_pairs:
            self.accent_attr = self.theme_attr(0, curses.A_BOLD)

    def theme_attr(self, color_index: int = 0, base_attr: int = 0) -> int:
        if not self.theme_pairs:
            return base_attr
        pair = self.theme_pairs[color_index % len(self.theme_pairs)]
        return base_attr | curses.color_pair(pair)

    def preview_attr(self, rgb: RGB, base_attr: int = 0) -> int:
        if not curses.has_colors():
            return base_attr
        try:
            curses.start_color()
            try:
                curses.use_default_colors()
            except curses.error:
                pass
        except curses.error:
            return base_attr
        if rgb not in self.preview_pairs:
            max_pairs = max(0, getattr(curses, "COLOR_PAIRS", 0) - 1)
            pair = len(self.theme_pairs) + len(self.preview_pairs) + 1
            if pair > max_pairs:
                return base_attr
            foreground = (
                rgb_to_ansi256(rgb)
                if getattr(curses, "COLORS", 0) >= 256
                else rgb_to_basic_color(rgb)
            )
            try:
                curses.init_pair(pair, foreground, -1)
            except curses.error:
                try:
                    curses.init_pair(pair, foreground, 0)
                except curses.error:
                    return base_attr
            self.preview_pairs[rgb] = pair
        return base_attr | curses.color_pair(self.preview_pairs[rgb])

    def render_palette_block(
        self,
        y: int,
        x: int,
        width: int,
        height: int,
        palette: tuple[RGB, ...],
        base_attr: int = 0,
    ) -> None:
        if width <= 0 or height <= 0 or not palette:
            return
        for row in range(height):
            rgb = palette[min(len(palette) - 1, (row * len(palette)) // height)]
            self.safe_addstr(y + row, x, " " * width, self.preview_attr(rgb, base_attr | curses.A_REVERSE))

    def safe_addstr(self, y: int, x: int, text: str, attr: int = 0) -> None:
        height, width = self.stdscr.getmaxyx()
        if y < 0 or y >= height or x < 0 or x >= width:
            return
        clipped = text[: max(0, width - x)]
        try:
            self.stdscr.addstr(y, x, clipped, attr)
        except curses.error:
            if y == height - 1 and x + len(clipped) >= width and clipped:
                self.stdscr.addstr(y, x, clipped[:-1], attr)
                return
            raise

    def render_themed_text(
        self,
        y: int,
        x: int,
        text: str,
        base_attr: int = 0,
        start_index: int = 0,
    ) -> None:
        if not self.theme_pairs:
            self.safe_addstr(y, x, text, base_attr)
            return

        height, width = self.stdscr.getmaxyx()
        if y < 0 or y >= height or x < 0 or x >= width:
            return
        text = text[: max(0, width - x)]
        if not text:
            return

        cursor = x
        chunk: list[str] = []
        current_color = start_index % len(self.theme_pairs)
        for offset, char in enumerate(text):
            color_index = (start_index + offset) % len(self.theme_pairs)
            if color_index != current_color:
                self.safe_addstr(
                    y,
                    cursor,
                    "".join(chunk),
                    self.theme_attr(current_color, base_attr),
                )
                cursor += len(chunk)
                chunk = []
                current_color = color_index
            chunk.append(char)
        if chunk:
            self.safe_addstr(
                y,
                cursor,
                "".join(chunk),
                self.theme_attr(current_color, base_attr),
            )

    def render_themed_bar(
        self,
        y: int,
        x: int,
        value: int,
        max_value: int,
        width: int,
        base_attr: int = 0,
    ) -> None:
        if not self.options.theme.themed_bars or not self.theme_pairs:
            self.safe_addstr(y, x, usage_bar(value, max_value, width), base_attr)
            return
        segments = themed_bar_segments(value, max_value, width, self.options.theme)
        self.render_bar_segments(y, x, segments, base_attr)

    def render_bar_segments(
        self,
        y: int,
        x: int,
        segments: list[BarSegment],
        base_attr: int = 0,
    ) -> None:
        cursor = x
        for segment in segments:
            attr = base_attr
            if segment.color_index is not None and self.theme_pairs:
                attr = self.theme_attr(segment.color_index, base_attr)
            self.safe_addstr(y, cursor, segment.text, attr)
            cursor += len(segment.text)
