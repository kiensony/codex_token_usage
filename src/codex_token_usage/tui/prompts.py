from __future__ import annotations

import curses
from dataclasses import replace

from ..pricing import ModelPrice
from .settings_model import format_settings_rate, parse_settings_rate


class PromptMixin:

    def prompt_input(self, prompt: str, initial: str = "") -> str | None:
        height, width = self.stdscr.getmaxyx()
        value = initial
        position = len(value)
        curses.curs_set(1)
        try:
            while True:
                self.stdscr.move(height - 1, 0)
                self.stdscr.clrtoeol()
                display_value = value[: max(0, width - len(prompt) - 1)]
                self.safe_addstr(height - 1, 0, prompt + display_value)
                self.stdscr.move(height - 1, min(len(prompt) + position, width - 1))
                key = self.stdscr.getch()
                if key in (10, 13, curses.KEY_ENTER):
                    return value.strip()
                if key == 27:
                    return None
                if key in (curses.KEY_BACKSPACE, 127, 8):
                    if position > 0:
                        value = value[: position - 1] + value[position:]
                        position -= 1
                    continue
                if key == curses.KEY_LEFT:
                    position = max(0, position - 1)
                    continue
                if key == curses.KEY_RIGHT:
                    position = min(len(value), position + 1)
                    continue
                if key == curses.KEY_HOME:
                    position = 0
                    continue
                if key == curses.KEY_END:
                    position = len(value)
                    continue
                if 32 <= key <= 126:
                    value = value[:position] + chr(key) + value[position:]
                    position += 1
        finally:
            curses.curs_set(0)

    def confirm_settings_action(self, prompt: str) -> bool:
        height, width = self.stdscr.getmaxyx()
        self.stdscr.move(height - 1, 0)
        self.stdscr.clrtoeol()
        self.safe_addstr(height - 1, 0, prompt[: max(0, width - 1)], curses.A_REVERSE)
        self.stdscr.refresh()
        return self.stdscr.getch() in (ord("y"), ord("Y"))

    def prompt_full_model_price(
        self,
        model: str,
        current: ModelPrice | None,
    ) -> ModelPrice | None:
        input_rate = self.prompt_required_rate(
            f"{model} input $/1M: ",
            current.input_per_million if current else None,
        )
        if input_rate is None:
            return None
        cached_ok, cached_rate = self.prompt_cached_rate(
            f"{model} cached $/1M (- for input rate): ",
            current.cached_input_per_million if current else None,
        )
        if not cached_ok:
            return None
        output_rate = self.prompt_required_rate(
            f"{model} output $/1M: ",
            current.output_per_million if current else None,
        )
        if output_rate is None:
            return None
        return ModelPrice(input_rate, cached_rate, output_rate)

    def prompt_rate_field(
        self,
        model: str,
        price: ModelPrice,
        field: str,
    ) -> ModelPrice | None:
        if field == "cached":
            ok, rate = self.prompt_cached_rate(
                f"{model} cached $/1M (- for input rate): ",
                price.cached_input_per_million,
            )
            if not ok:
                return None
            return replace(price, cached_input_per_million=rate)

        current = price.input_per_million if field == "input" else price.output_per_million
        rate = self.prompt_required_rate(f"{model} {field} $/1M: ", current)
        if rate is None:
            return None
        if field == "input":
            return replace(price, input_per_million=rate)
        return replace(price, output_per_million=rate)

    def prompt_required_rate(self, prompt: str, default: float | None) -> float | None:
        initial = "" if default is None else format_settings_rate(default)
        while True:
            raw = self.prompt_input(prompt, initial)
            if raw is None:
                return None
            if raw == "" and default is not None:
                return default
            rate = parse_settings_rate(raw)
            if isinstance(rate, str):
                self.show_prompt_message(rate)
                continue
            return rate

    def prompt_cached_rate(
        self,
        prompt: str,
        default: float | None,
    ) -> tuple[bool, float | None]:
        initial = "-" if default is None else format_settings_rate(default)
        while True:
            raw = self.prompt_input(prompt, initial)
            if raw is None:
                return False, None
            if raw in ("", "-"):
                return True, None if raw == "-" else default
            rate = parse_settings_rate(raw)
            if isinstance(rate, str):
                self.show_prompt_message(rate)
                continue
            return True, rate

    def show_prompt_message(self, message: str) -> None:
        height, width = self.stdscr.getmaxyx()
        self.stdscr.move(height - 2, 0)
        self.stdscr.clrtoeol()
        self.safe_addstr(height - 2, 0, message[: max(0, width - 1)], curses.A_DIM)
        self.stdscr.getch()

    def prompt_filter(self) -> None:
        self.set_blocking_input()
        height, width = self.stdscr.getmaxyx()
        prompt = "filter: "
        self.stdscr.move(height - 1, 0)
        self.stdscr.clrtoeol()
        self.safe_addstr(height - 1, 0, prompt)
        curses.curs_set(1)
        value = self.state.filter_text
        position = len(value)
        try:
            while True:
                self.stdscr.move(height - 1, 0)
                self.stdscr.clrtoeol()
                display_value = value[: max(0, width - len(prompt) - 1)]
                self.safe_addstr(height - 1, 0, prompt + display_value)
                self.stdscr.move(height - 1, min(len(prompt) + position, width - 1))
                key = self.stdscr.getch()
                if key in (10, 13, curses.KEY_ENTER):
                    self.state = self.state.set_filter(value)
                    return
                if key == 27:
                    if value:
                        self.state = self.state.clear_filter()
                    else:
                        self.state = self.state.cancel_filter()
                    return
                if key in (curses.KEY_BACKSPACE, 127, 8):
                    if position > 0:
                        value = value[: position - 1] + value[position:]
                        position -= 1
                    continue
                if key == curses.KEY_LEFT:
                    position = max(0, position - 1)
                    continue
                if key == curses.KEY_RIGHT:
                    position = min(len(value), position + 1)
                    continue
                if key == curses.KEY_HOME:
                    position = 0
                    continue
                if key == curses.KEY_END:
                    position = len(value)
                    continue
                if 32 <= key <= 126:
                    value = value[:position] + chr(key) + value[position:]
                    position += 1
        finally:
            curses.curs_set(0)
