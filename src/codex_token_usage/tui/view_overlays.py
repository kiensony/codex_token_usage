from __future__ import annotations

import curses
import time
from dataclasses import replace

from ..keybindings import format_keybinding_config
from ..theme import theme_palette
from .formatting import FORCE_SHUTDOWN_KEYS
from .settings_model import (
    about_content_lines,
    farewell_content_lines,
    farewell_flag_height,
    farewell_frame_delay,
    theme_current_preset,
)


class ViewOverlayMixin:
    def render_help(self, height: int, width: int) -> None:
        lines = [
            "Help",
            f"{self.keys_for_action('next_view')} / {self.keys_for_action('previous_view')}  switch views",
            f"{self.keys_for_action('move_down')} / {self.keys_for_action('move_up')}  move selection",
            f"{self.keys_for_action('page_down')} / {self.keys_for_action('page_up')}  move by page",
            f"{self.keys_for_action('select_first')} / {self.keys_for_action('select_last')}  jump to top or bottom",
            f"{self.keys_for_action('open_details')}  open selected session details",
            (
                f"{self.keys_for_action('back')} / {self.keys_for_action('back_or_quit')}  "
                "return from details"
            ),
            f"{self.keys_for_action('cycle_sort')}  cycle sort field",
            f"{self.keys_for_action('toggle_sort_direction')}  reverse sort direction",
            f"{self.keys_for_action('filter')}  filter sessions; Esc clears/cancels filter input",
            f"{self.keys_for_action('cycle_date_preset')}  cycle date range preset",
            f"{self.keys_for_action('show_all_time')}  show all time",
            (
                f"{self.keys_for_action('shift_date_backward')} / "
                f"{self.keys_for_action('shift_date_forward')}  move date range"
            ),
            f"{self.keys_for_action('reload')}  reload local Codex data",
            f"{self.keys_for_action('open_settings')}  open settings",
            f"{self.keys_for_action('open_about')}  about this software",
            f"{self.keys_for_action('help')}  open or close help",
            f"{self.keys_for_action('quit')}  quit",
        ]
        top = max(1, (height - len(lines) - 2) // 2)
        left = max(0, (width - 78) // 2)
        box_width = min(width - left - 1, 78)
        if box_width <= 10:
            return
        border = "+" + "-" * (box_width - 2) + "+"
        self.render_themed_text(top, left, border, curses.A_REVERSE)
        for index, line in enumerate(lines, start=1):
            text = f"| {line:<{box_width - 4}} |"
            attr = curses.A_BOLD if index == 1 else curses.A_REVERSE
            self.safe_addstr(top + index, left, text[:box_width], attr)
        self.render_themed_text(
            top + len(lines) + 1,
            left,
            border,
            curses.A_REVERSE,
            start_index=len(lines),
        )
    def show_about_dialog(self) -> None:
        self.set_blocking_input()
        height, width = self.stdscr.getmaxyx()
        self.render_about(height, width)
        self.stdscr.refresh()
        self.stdscr.getch()
    def render_about(self, height: int, width: int) -> None:
        left = max(0, (width - 78) // 2)
        box_width = min(width - left - 1, 78)
        if box_width <= 10:
            return
        cell_width = box_width - 4
        lines = about_content_lines(self.options.theme, cell_width)
        top = max(1, (height - len(lines) - 2) // 2)
        border = "+" + "-" * (box_width - 2) + "+"
        self.render_themed_text(top, left, border, curses.A_REVERSE)
        for index, line in enumerate(lines, start=1):
            text = f"| {line:<{cell_width}} |"
            attr = curses.A_BOLD if index == 1 else curses.A_REVERSE
            self.safe_addstr(top + index, left, text[:box_width], attr)
        self.render_themed_text(
            top + len(lines) + 1,
            left,
            border,
            curses.A_REVERSE,
            start_index=len(lines),
        )
    def render_farewell(self) -> None:
        if self.stdscr is None:
            return
        try:
            self.set_blocking_input()
            self.stdscr.erase()
            height, width = self.stdscr.getmaxyx()
            left = max(0, (width - 78) // 2)
            box_width = min(width - left - 1, 78)
            if box_width <= 10:
                return
            cell_width = box_width - 4
            lines = farewell_content_lines(self.options.theme, cell_width)
            palette = theme_palette(
                replace(
                    self.options.theme,
                    enabled=True,
                    preset=theme_current_preset(self.options.theme),
                )
            )
            flag_height = farewell_flag_height(height, len(lines), palette)
            top = max(1, (height - len(lines) - flag_height - 5) // 2)
            border = "+" + "-" * (box_width - 2) + "+"
            self.render_themed_text(top, left, border, curses.A_REVERSE)
            for index, line in enumerate(lines, start=1):
                text = f"| {line:<{cell_width}} |"
                attr = curses.A_BOLD if index == 1 else curses.A_REVERSE
                self.safe_addstr(top + index, left, text[:box_width], attr)
            flag_y = top + len(lines) + 1
            if flag_height:
                self.render_palette_block(flag_y, left + 2, cell_width, flag_height, palette)
            closing_y = flag_y + flag_height
            frame_ms = farewell_frame_delay(self.options.shutdown_seconds)
            for closing in ("Closing .", "Closing ..", "Closing ..."):
                text = f"| {closing:<{cell_width}} |"
                self.safe_addstr(closing_y, left, text[:box_width], curses.A_REVERSE)
                self.stdscr.refresh()
                if self.wait_for_farewell_frame(frame_ms):
                    return
            self.render_themed_text(
                closing_y + 1,
                left,
                border,
                curses.A_REVERSE,
                start_index=len(lines),
            )
            self.stdscr.refresh()
        except curses.error:
            return
    def wait_for_farewell_frame(self, frame_ms: int) -> bool:
        if self.stdscr is None:
            curses.napms(frame_ms)
            return False
        if not hasattr(self.stdscr, "timeout"):
            curses.napms(frame_ms)
            return False

        deadline = time.monotonic() + (frame_ms / 1000)
        try:
            while True:
                remaining_ms = round((deadline - time.monotonic()) * 1000)
                if remaining_ms <= 0:
                    return False
                self.stdscr.timeout(remaining_ms)
                key = self.stdscr.getch()
                if key in FORCE_SHUTDOWN_KEYS:
                    return True
                if key == -1:
                    return False
        except KeyboardInterrupt:
            return True
        finally:
            self.stdscr.timeout(-1)
    def keys_for_action(self, action: str) -> str:
        return format_keybinding_config(self.options.keybindings, action)
    def render_key_values(
        self, top: int, rows: list[tuple[str, str]], width: int, height: int
    ) -> None:
        label_width = max((len(label) for label, _ in rows), default=0)
        for index, (label, value) in enumerate(rows[: max(0, height - top - 2)]):
            label_text = f"{label:<{label_width}}"
            self.safe_addstr(
                top + index,
                0,
                label_text,
                self.theme_attr(index, curses.A_BOLD),
            )
            self.safe_addstr(
                top + index,
                label_width,
                f"  {value}"[: max(0, width - label_width - 1)],
            )
    def render_footer(self, height: int, width: int) -> None:
        sqlite_status = "sqlite:on" if self.state.dataset.sqlite_available else "sqlite:off"
        loaded = self.state.dataset.loaded_at.strftime("%Y-%m-%d %H:%M:%S")
        meta = (
            f"loaded {loaded}  sessions {len(self.state.visible_sessions())}  "
            f"{sqlite_status}"
        )
        footer = (
            f"{self.keys_for_action('next_view')} view  "
            f"{self.keys_for_action('open_details')} details  "
            f"{self.keys_for_action('move_down')}/{self.keys_for_action('move_up')} move  "
            f"{self.keys_for_action('page_down')} page  "
            f"{self.keys_for_action('cycle_sort')}/{self.keys_for_action('toggle_sort_direction')} sort  "
            f"{self.keys_for_action('filter')} filter  "
            f"{self.keys_for_action('cycle_date_preset')} date  "
            f"{self.keys_for_action('show_all_time')} all-time  "
            f"{self.keys_for_action('reload')} reload  "
            f"{self.keys_for_action('open_settings')} settings  "
            f"{self.keys_for_action('open_about')} about  "
            f"{self.keys_for_action('help')} help  "
            f"{self.keys_for_action('quit')} quit"
        )
        if self.state.status:
            footer = f"{self.state.status} | {footer}"
        self.render_themed_text(
            height - 2,
            0,
            meta[: max(0, width - 1)],
            curses.A_DIM,
            start_index=1,
        )
        self.render_themed_text(
            height - 1,
            0,
            footer[: max(0, width - 1)],
            curses.A_DIM,
            start_index=2,
        )
