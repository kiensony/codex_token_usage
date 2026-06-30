from __future__ import annotations

import curses
from dataclasses import replace

from ..theme import ThemeConfig, theme_palette
from .settings_model import (
    FLAG_PICKER_COLUMNS,
    FLAG_PICKER_TOP,
    THEME_PRESET_CHOICES,
    flag_display_name,
    flag_picker_block_height,
    flag_picker_page_size,
    theme_current_preset,
)


class SettingsFlagPickerMixin:

    def choose_flag_preset(self, theme: ThemeConfig) -> ThemeConfig | None:
        current = theme_current_preset(theme)
        selected_index = THEME_PRESET_CHOICES.index(current)
        status = "choose flag: h/j/k/l move, n/p page, Enter select, q cancel"
        while True:
            self.render_flag_picker(theme, selected_index, status)
            key = self.stdscr.getch()
            height, _width = self.stdscr.getmaxyx()
            page_size = flag_picker_page_size(height)
            if key in (ord("q"), 27):
                return None
            if key in (curses.KEY_RIGHT, ord("l")):
                selected_index = min(selected_index + 1, len(THEME_PRESET_CHOICES) - 1)
                continue
            if key in (curses.KEY_LEFT, ord("h")):
                selected_index = max(selected_index - 1, 0)
                continue
            if key in (curses.KEY_DOWN, ord("j")):
                selected_index = min(
                    selected_index + FLAG_PICKER_COLUMNS,
                    len(THEME_PRESET_CHOICES) - 1,
                )
                continue
            if key in (curses.KEY_UP, ord("k")):
                selected_index = max(selected_index - FLAG_PICKER_COLUMNS, 0)
                continue
            if key == ord("n"):
                selected_index = min(
                    selected_index + page_size,
                    len(THEME_PRESET_CHOICES) - 1,
                )
                continue
            if key == ord("p"):
                selected_index = max(selected_index - page_size, 0)
                continue
            if key == curses.KEY_HOME:
                selected_index = 0
                continue
            if key == curses.KEY_END:
                selected_index = len(THEME_PRESET_CHOICES) - 1
                continue
            if key in (10, 13, curses.KEY_ENTER):
                preset = THEME_PRESET_CHOICES[selected_index]
                if preset == "plain":
                    return replace(theme, enabled=False)
                return replace(theme, enabled=True, preset=preset)

    def render_flag_picker(
        self,
        theme: ThemeConfig,
        selected_index: int,
        status: str,
    ) -> None:
        self.stdscr.erase()
        height, width = self.stdscr.getmaxyx()
        page_size = flag_picker_page_size(height)
        total_pages = max(1, (len(THEME_PRESET_CHOICES) + page_size - 1) // page_size)
        page = selected_index // page_size
        start_index = page * page_size
        visible = THEME_PRESET_CHOICES[start_index : start_index + page_size]
        self.render_themed_text(0, 0, "Available flag presets:", curses.A_BOLD)
        self.safe_addstr(1, 0, f"Page: {page + 1} of {total_pages}", curses.A_DIM)
        self.safe_addstr(2, 0, status[: max(0, width - 1)], curses.A_DIM)

        card_width = max(16, min(28, width // FLAG_PICKER_COLUMNS))
        block_width = max(12, min(24, card_width - 4))
        block_height = flag_picker_block_height(height)
        row_height = block_height + 3
        top = FLAG_PICKER_TOP
        for offset, preset in enumerate(visible):
            row = offset // FLAG_PICKER_COLUMNS
            column = offset % FLAG_PICKER_COLUMNS
            row_index = start_index + offset
            selected = row_index == selected_index
            x = column * card_width + max(0, (card_width - block_width) // 2)
            y = top + row * row_height
            if y + block_height + 1 >= height:
                break
            label = flag_display_name(preset)
            label_x = column * card_width + max(0, (card_width - len(label)) // 2)
            attr = curses.A_REVERSE | curses.A_BOLD if selected else 0
            self.render_flag_block(y, x, block_width, block_height, theme, preset, selected)
            self.safe_addstr(y + block_height + 1, label_x, label[: max(0, card_width - 1)], attr)
        self.stdscr.refresh()

    def render_flag_block(
        self,
        y: int,
        x: int,
        width: int,
        height: int,
        theme: ThemeConfig,
        preset: str,
        selected: bool = False,
    ) -> None:
        if width <= 0:
            return
        if preset == "plain":
            attr = curses.A_REVERSE | curses.A_BOLD if selected else curses.A_DIM
            for row in range(height):
                text = "plain".center(width) if row == height // 2 else " " * width
                self.safe_addstr(y + row, x, text, attr)
            return
        preview_theme = replace(theme, enabled=True, preset=preset)
        palette = theme_palette(preview_theme)
        base_attr = curses.A_REVERSE | curses.A_BOLD if selected else 0
        self.render_palette_block(y, x, width, height, palette, base_attr)
        if selected and y > 0:
            self.safe_addstr(y - 1, x, "^".center(width), curses.A_BOLD)
