from __future__ import annotations

import curses
import time
from dataclasses import replace
from datetime import date

from ..keybindings import keymap_for_config
from ..loader import load_usage
from ..models import UsageDataset
from ..theme import RGB
from .prompts import PromptMixin
from .settings_screen import SettingsScreenMixin
from .state import TuiOptions, TuiState
from .theme_renderer import ThemeRendererMixin
from .views import ViewRendererMixin


def run_tui(options: TuiOptions) -> int:
    dataset = load_usage(
        codex_home=options.codex_home,
        since=options.since,
        until=options.until,
        include_zero=options.include_zero,
    )
    state = TuiState(
        dataset=dataset,
        since=options.since,
        until=options.until,
        today=date.today(),
        pricing=options.pricing,
        status=options.theme_status,
    )
    curses.wrapper(lambda stdscr: CursesUi(stdscr, state, options).run())
    return 0


class CursesUi(ThemeRendererMixin, PromptMixin, SettingsScreenMixin, ViewRendererMixin):

    def __init__(self, stdscr, state: TuiState, options: TuiOptions) -> None:
        self.stdscr = stdscr
        self.state = state
        self.options = options
        self.keymap = keymap_for_config(options.keybindings)
        self.theme_pairs: list[int] = []
        self.preview_pairs: dict[RGB, int] = {}
        self.accent_attr = curses.A_BOLD
        self.next_auto_refresh_at: float | None = None

    def run(self) -> None:
        curses.curs_set(0)
        self.stdscr.keypad(True)
        self.init_theme_colors()
        self.schedule_next_auto_refresh()
        try:
            while not self.state.should_quit:
                self.render()
                self.configure_input_timeout()
                key = self.stdscr.getch()
                if key == -1:
                    self.handle_auto_refresh()
                    continue
                self.handle_key(key)
        except KeyboardInterrupt:
            self.state = self.state.quit()
        finally:
            self.render_farewell()

    def handle_key(self, key: int) -> None:
        action = self.keymap.get(key)
        if self.state.help_open:
            if action in ("help", "quit", "back_or_quit") or key == 27:
                self.state = self.state.close_help()
            return
        if self.state.about_open:
            if action in ("open_about", "quit", "back_or_quit") or key in (
                10,
                13,
                curses.KEY_ENTER,
                27,
            ):
                self.state = self.state.close_about()
            return

        if action == "quit":
            self.state = self.state.quit()
        elif action == "back_or_quit":
            if self.state.view == "details":
                self.state = self.state.close_details()
            else:
                self.state = self.state.quit()
        elif action == "next_view":
            self.state = self.state.next_view()
        elif action == "previous_view":
            self.state = self.state.previous_view()
        elif action == "move_down":
            self.state = self.state.move_selection(1)
        elif action == "move_up":
            self.state = self.state.move_selection(-1)
        elif action == "page_down":
            self.state = self.state.page_selection(1)
        elif action == "page_up":
            self.state = self.state.page_selection(-1)
        elif action == "select_first":
            self.state = self.state.select_first()
        elif action == "select_last":
            self.state = self.state.select_last()
        elif action == "open_details":
            self.state = self.state.open_details()
        elif action == "cycle_sort":
            self.state = self.state.cycle_sort()
        elif action == "toggle_sort_direction":
            self.state = self.state.toggle_sort_direction()
        elif action == "cycle_date_preset":
            self.state = self.state.cycle_date_preset()
            if self.state.date_preset == "all":
                self.reload_all_time()
        elif action == "show_all_time":
            self.show_all_time()
        elif action == "shift_date_backward":
            self.state = self.state.shift_date_window(-1)
        elif action == "shift_date_forward":
            self.state = self.state.shift_date_window(1)
        elif action == "reload":
            self.state = self.state.reload(self.reload_dataset)
            self.schedule_next_auto_refresh()
        elif action == "open_settings":
            self.open_settings()
        elif action == "open_about":
            self.state = self.state.open_about()
        elif action == "filter":
            self.prompt_filter()
        elif action == "back":
            self.state = self.state.close_details()
        elif action == "help":
            self.state = self.state.open_help()

    def reload_dataset(self, since: date | None, until: date | None) -> UsageDataset:
        return load_usage(
            codex_home=self.options.codex_home,
            since=since,
            until=until,
            include_zero=self.options.include_zero,
        )

    def show_all_time(self) -> None:
        self.state = self.state.set_all_time()
        self.reload_all_time()

    def reload_all_time(self) -> None:
        self.state = self.state.reload(self.reload_dataset)
        self.state = replace(self.state, status="date range: all time")
        self.schedule_next_auto_refresh()

    def configure_input_timeout(self) -> None:
        if self.stdscr is None or not hasattr(self.stdscr, "timeout"):
            return
        timeout_ms = self.next_input_timeout_ms(time.monotonic())
        self.stdscr.timeout(timeout_ms)

    def set_blocking_input(self) -> None:
        if self.stdscr is None or not hasattr(self.stdscr, "timeout"):
            return
        self.stdscr.timeout(-1)

    def next_input_timeout_ms(self, now: float) -> int:
        if self.options.auto_refresh_seconds is None:
            return -1
        if self.next_auto_refresh_at is None:
            return 0
        remaining = self.next_auto_refresh_at - now
        if remaining <= 0:
            return 0
        return max(1, round(remaining * 1000))

    def schedule_next_auto_refresh(self, now: float | None = None) -> None:
        if self.options.auto_refresh_seconds is None:
            self.next_auto_refresh_at = None
            return
        current = time.monotonic() if now is None else now
        self.next_auto_refresh_at = current + self.options.auto_refresh_seconds

    def handle_auto_refresh(self) -> None:
        if self.options.auto_refresh_seconds is None:
            return
        now = time.monotonic()
        if self.next_auto_refresh_at is not None and now < self.next_auto_refresh_at:
            return
        self.state = self.state.reload(self.reload_dataset)
        self.state = replace(
            self.state,
            status=f"auto-refreshed {len(self.state.dataset.sessions)} sessions",
        )
        self.schedule_next_auto_refresh(now)
