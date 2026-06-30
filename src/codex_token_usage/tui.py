from __future__ import annotations

import curses
from dataclasses import dataclass, replace
from datetime import date, timedelta
from pathlib import Path
from typing import Callable

from .forecast import (
    PREDICTION_ALGORITHMS,
    ForecastWindow,
    LimitConfig,
    PredictionConfig,
    UsageForecast,
    make_usage_forecast,
)
from .keybindings import (
    KEYBINDING_ACTION_LABELS,
    KEYBINDING_ACTIONS,
    KeybindingConfig,
    format_keybinding_config,
    format_keybinding_labels,
    key_label_for_code,
    keymap_for_config,
    reset_keybinding,
    update_keybinding,
)
from .loader import load_usage
from .models import SessionUsage, TokenBreakdown, UsageDataset
from .pricing import (
    MODEL_PRICES,
    ModelPrice,
    PricingConfig,
    estimate_session_cost,
    estimate_sessions_cost,
    format_cost,
    normalize_model_name,
)
from .report import ReportRow, format_int, format_percent, make_report_rows
from .theme import (
    BarSegment,
    COLOR_MODES,
    DEFAULT_THEME_PRESET,
    DisplayConfig,
    PRESET_NAMES,
    RGB,
    ThemeConfig,
    load_theme_config,
    rgb_to_ansi256,
    rgb_to_basic_color,
    save_theme_config,
    theme_palette,
    themed_bar_segments,
)

VIEWS = ("overview", "daily", "weekly", "monthly", "hourly", "sessions", "details")
TAB_VIEWS = ("overview", "daily", "weekly", "monthly", "hourly", "sessions")
VIEW_LABELS = {
    "overview": "Overview",
    "daily": "By Date",
    "weekly": "By Week",
    "monthly": "By Month",
    "hourly": "By Hour",
    "sessions": "By Session",
    "details": "Details",
}
SORT_FIELDS = (
    "total",
    "input",
    "output",
    "cached",
    "cached_pct",
    "cost",
    "effort",
    "miss",
    "reasoning",
    "model",
    "context",
    "updated",
)
REASONING_LEVEL_RANK = {
    "-": 0,
    "none": 0,
    "minimal": 1,
    "low": 2,
    "medium": 3,
    "high": 4,
}
DATE_PRESETS = ("all", "today", "7d", "30d", "90d")
DEFAULT_PAGE_SIZE = 10
RATE_FIELDS = ("input", "cached", "output")
THEME_PRESET_CHOICES = ("plain", *PRESET_NAMES)
FLAG_PICKER_COLUMNS = 4
FLAG_PICKER_TOP = 5
FLAG_PICKER_PREVIEW_HEIGHT = 5
APPEARANCE_PREVIEW_BLOCK_HEIGHT = 5
SETTINGS_TABS = (
    "Model Pricing",
    "Display Columns",
    "Appearance",
    "Keybindings",
    "Misc",
)
DISPLAY_SETTING_FIELDS = (
    "cached_tokens",
    "cached_percent",
    "estimated_cost",
    "reasoning_level",
    "cache_miss",
    "reasoning_tokens",
    "model",
    "context",
    "model_width",
)
APPEARANCE_SETTING_FIELDS = (
    "flag",
    "color",
    "light",
    "accent_line",
    "themed_bars",
)
MISC_SETTING_FIELDS = ("prediction_algorithm",)


@dataclass(frozen=True)
class TuiOptions:
    codex_home: Path
    since: date | None = None
    until: date | None = None
    include_zero: bool = False
    theme: ThemeConfig = ThemeConfig()
    display: DisplayConfig = DisplayConfig()
    pricing: PricingConfig = PricingConfig()
    keybindings: KeybindingConfig = KeybindingConfig()
    theme_status: str = ""
    limits: LimitConfig = LimitConfig()
    prediction: PredictionConfig = PredictionConfig()


@dataclass(frozen=True)
class TuiState:
    dataset: UsageDataset
    view_index: int = 0
    previous_view_index: int = 0
    selected_index: int = 0
    sort_index: int = 0
    sort_descending: bool = True
    filter_text: str = ""
    date_preset_index: int = 0
    since: date | None = None
    until: date | None = None
    help_open: bool = False
    should_quit: bool = False
    status: str = ""
    today: date | None = None
    pricing: PricingConfig = PricingConfig()

    @property
    def view(self) -> str:
        return VIEWS[self.view_index]

    @property
    def sort_field(self) -> str:
        return SORT_FIELDS[self.sort_index]

    @property
    def date_preset(self) -> str:
        return DATE_PRESETS[self.date_preset_index]

    def next_view(self) -> "TuiState":
        next_index = (TAB_VIEWS.index(self.tab_view) + 1) % len(TAB_VIEWS)
        return replace(self, view_index=VIEWS.index(TAB_VIEWS[next_index]))

    def previous_view(self) -> "TuiState":
        previous_index = (TAB_VIEWS.index(self.tab_view) - 1) % len(TAB_VIEWS)
        return replace(self, view_index=VIEWS.index(TAB_VIEWS[previous_index]))

    @property
    def tab_view(self) -> str:
        if self.view == "details":
            return VIEWS[self.previous_view_index]
        return self.view

    def move_selection(self, delta: int) -> "TuiState":
        sessions = self.visible_sessions()
        if not sessions:
            return replace(self, selected_index=0)
        selected = min(max(self.selected_index + delta, 0), len(sessions) - 1)
        return replace(self, selected_index=selected)

    def page_selection(self, delta: int, page_size: int = DEFAULT_PAGE_SIZE) -> "TuiState":
        return self.move_selection(delta * max(1, page_size))

    def select_first(self) -> "TuiState":
        return replace(self, selected_index=0)

    def select_last(self) -> "TuiState":
        sessions = self.visible_sessions()
        if not sessions:
            return replace(self, selected_index=0)
        return replace(self, selected_index=len(sessions) - 1)

    def open_details(self) -> "TuiState":
        if self.visible_sessions():
            return replace(
                self,
                view_index=VIEWS.index("details"),
                previous_view_index=VIEWS.index(self.tab_view),
            )
        return self

    def close_details(self) -> "TuiState":
        if self.view == "details":
            return replace(self, view_index=self.previous_view_index)
        return self

    def cycle_sort(self) -> "TuiState":
        next_index = (self.sort_index + 1) % len(SORT_FIELDS)
        return replace(
            self,
            sort_index=next_index,
            selected_index=0,
            status=f"sort: {SORT_FIELDS[next_index]} {self.sort_direction_label}",
        )

    def toggle_sort_direction(self) -> "TuiState":
        next_descending = not self.sort_descending
        direction = "desc" if next_descending else "asc"
        return replace(
            self,
            sort_descending=next_descending,
            selected_index=0,
            status=f"sort direction: {direction}",
        )

    @property
    def sort_direction_label(self) -> str:
        return "desc" if self.sort_descending else "asc"

    def set_filter(self, value: str) -> "TuiState":
        value = value.strip()
        status = f"filter: {value}" if value else "filter cleared"
        return replace(self, filter_text=value, selected_index=0, status=status)

    def clear_filter(self) -> "TuiState":
        return replace(self, filter_text="", selected_index=0, status="filter cleared")

    def cancel_filter(self) -> "TuiState":
        return replace(self, status="filter canceled")

    def set_all_time(self) -> "TuiState":
        return replace(
            self,
            date_preset_index=DATE_PRESETS.index("all"),
            since=None,
            until=None,
            selected_index=0,
            status="date range: all time",
        )

    def cycle_date_preset(self) -> "TuiState":
        index = (self.date_preset_index + 1) % len(DATE_PRESETS)
        preset = DATE_PRESETS[index]
        today = self.today or date.today()
        since: date | None = None
        until: date | None = None
        if preset == "today":
            since = today
            until = today
        elif preset.endswith("d"):
            days = int(preset[:-1])
            since = today - timedelta(days=days - 1)
            until = today
        return replace(
            self,
            date_preset_index=index,
            since=since,
            until=until,
            selected_index=0,
            status=f"date range: {'all time' if preset == 'all' else preset}",
        )

    def shift_date_window(self, direction: int) -> "TuiState":
        if self.since is None or self.until is None:
            return replace(self, status="date shift needs an active range")
        span = max(1, (self.until - self.since).days + 1)
        delta = timedelta(days=span * direction)
        since = self.since + delta
        until = self.until + delta
        return replace(
            self,
            since=since,
            until=until,
            selected_index=0,
            status=f"range: {since}..{until}",
        )

    def reload(self, loader: Callable[[date | None, date | None], UsageDataset]) -> "TuiState":
        selected_session = self.selected_session()
        selected_id = selected_session.session_id if selected_session else None
        dataset = loader(self.since, self.until)
        next_state = replace(
            self,
            dataset=dataset,
            selected_index=0,
            status=f"reloaded {len(dataset.sessions)} sessions",
        )
        if selected_id is None:
            return next_state
        return next_state.select_session_id(selected_id)

    def select_session_id(self, session_id: str) -> "TuiState":
        for index, session in enumerate(self.visible_sessions()):
            if session.session_id == session_id:
                return replace(self, selected_index=index)
        return self

    def quit(self) -> "TuiState":
        return replace(self, should_quit=True)

    def open_help(self) -> "TuiState":
        return replace(self, help_open=True, status="")

    def close_help(self) -> "TuiState":
        return replace(self, help_open=False, status="")

    def toggle_help(self) -> "TuiState":
        return self.close_help() if self.help_open else self.open_help()

    def visible_sessions(self) -> list[SessionUsage]:
        sessions = [
            session
            for session in self.dataset.sessions
            if self.matches_filter(session) and self.matches_date(session)
        ]
        sessions.sort(key=self.sort_key, reverse=self.sort_descending)
        return sessions

    def selected_session(self) -> SessionUsage | None:
        sessions = self.visible_sessions()
        if not sessions:
            return None
        index = min(self.selected_index, len(sessions) - 1)
        return sessions[index]

    def daily_rows(self):
        dataset = replace(self.dataset, sessions=tuple(self.visible_sessions()))
        return self.sorted_report_rows(
            make_report_rows(dataset, group_by="date", pricing=self.pricing)
        )

    def weekly_rows(self):
        dataset = replace(self.dataset, sessions=tuple(self.visible_sessions()))
        return self.sorted_report_rows(
            make_report_rows(dataset, group_by="week", pricing=self.pricing)
        )

    def monthly_rows(self):
        dataset = replace(self.dataset, sessions=tuple(self.visible_sessions()))
        return self.sorted_report_rows(
            make_report_rows(dataset, group_by="month", pricing=self.pricing)
        )

    def hourly_rows(self):
        dataset = replace(self.dataset, sessions=tuple(self.visible_sessions()))
        return self.sorted_report_rows(
            make_report_rows(dataset, group_by="hour", pricing=self.pricing)
        )

    def filtered_totals(self) -> TokenBreakdown:
        total = TokenBreakdown.empty()
        for session in self.visible_sessions():
            total = total.add(session.tokens)
        return total

    def matches_filter(self, session: SessionUsage) -> bool:
        if not self.filter_text:
            return True
        needle = self.filter_text.lower()
        fields = (
            session.session_id,
            session.title,
            session.model,
            session.cwd,
        )
        return any(needle in field.lower() for field in fields)

    def matches_date(self, session: SessionUsage) -> bool:
        day = session.activity_day
        if self.since and (day is None or day < self.since):
            return False
        if self.until and (day is None or day > self.until):
            return False
        return True

    def sort_key(self, session: SessionUsage):
        return session_sort_key(session, self.sort_field, self.pricing)

    def sorted_report_rows(self, rows: list[ReportRow]) -> list[ReportRow]:
        return sorted(
            rows,
            key=lambda row: report_row_sort_key(row, self.sort_field),
            reverse=self.sort_descending,
        )

    def range_label(self) -> str:
        if self.since is None and self.until is None:
            return "all time"
        if self.since == self.until:
            return self.since.isoformat() if self.since else "all time"
        if self.since is None:
            return f"..{self.until}"
        if self.until is None:
            return f"{self.since}.."
        return f"{self.since}..{self.until}"


def session_sort_key(
    session: SessionUsage,
    sort_field: str,
    pricing: PricingConfig,
):
    tokens = session.tokens
    if sort_field == "total":
        return tokens.total_tokens
    if sort_field == "input":
        return tokens.input_tokens
    if sort_field == "output":
        return tokens.output_tokens
    if sort_field == "cached":
        return tokens.cached_input_tokens
    if sort_field == "cached_pct":
        return tokens.cached_input_percent
    if sort_field == "cost":
        estimate = estimate_session_cost(session, pricing)
        return estimate.usd if estimate.usd is not None else float("-inf")
    if sort_field == "effort":
        return reasoning_level_sort_key(session.reasoning_level)
    if sort_field == "miss":
        return tokens.cache_miss_input_tokens
    if sort_field == "reasoning":
        return tokens.reasoning_output_tokens
    if sort_field == "model":
        return session.model.casefold()
    if sort_field == "context":
        return f"{session.cwd} {session.title}".casefold()
    if sort_field == "updated":
        return datetime_sort_key(session.updated_at)
    return tokens.total_tokens


def report_row_sort_key(row: ReportRow, sort_field: str):
    tokens = row.tokens
    if sort_field == "total":
        return tokens.total_tokens
    if sort_field == "input":
        return tokens.input_tokens
    if sort_field == "output":
        return tokens.output_tokens
    if sort_field == "cached":
        return tokens.cached_input_tokens
    if sort_field == "cached_pct":
        return tokens.cached_input_percent
    if sort_field == "cost":
        return row.estimated_cost.usd if row.estimated_cost.usd is not None else float("-inf")
    if sort_field == "miss":
        return tokens.cache_miss_input_tokens
    if sort_field == "reasoning":
        return tokens.reasoning_output_tokens
    return row.key.casefold()


def forecast_key_values(forecast: UsageForecast) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for window in (forecast.five_hour, forecast.weekly):
        if window.enabled:
            rows.append((forecast_label(window), format_forecast_window(window)))
    return rows


def prediction_key_values(forecast: UsageForecast) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for prediction in forecast.predictions:
        rows.append(
            (
                prediction_overview_label(prediction.name),
                f"{format_int(prediction.projected)} tokens",
            )
        )
    return rows


def prediction_overview_label(name: str) -> str:
    labels = {
        "next_5_hours": "Next 5h estimate",
        "next_day": "Next day estimate",
        "next_week": "Next week estimate",
        "next_month": "Next month estimate",
    }
    return labels.get(name, name.replace("_", " ").title())


def forecast_label(window: ForecastWindow) -> str:
    if window.name == "5h":
        return "5h forecast"
    return "Weekly forecast"


def format_forecast_window(window: ForecastWindow) -> str:
    remaining = "-" if window.remaining is None else format_int(window.remaining)
    limit = "-" if window.limit is None else format_int(window.limit)
    return (
        f"{window.status}; used {format_int(window.used)} / {limit}; "
        f"remaining {remaining}; projected {format_int(window.projected)}"
    )


def usage_row_forecast_status(
    label: str,
    row_key: str,
    forecast_window: ForecastWindow | None,
) -> str:
    if label != "week" or forecast_window is None or not forecast_window.enabled:
        return ""
    if row_key != week_key(forecast_window.window_start.date()):
        return ""
    return forecast_window.status


def week_key(value: date) -> str:
    iso_week = value.isocalendar()
    return f"{iso_week.year}-W{iso_week.week:02d}"


def reasoning_level_sort_key(level: str) -> tuple[int, str]:
    normalized = level.casefold()
    return (REASONING_LEVEL_RANK.get(normalized, 0), normalized)


def datetime_sort_key(value) -> float:
    if value is None:
        return float("-inf")
    return value.timestamp()


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


class CursesUi:
    def __init__(self, stdscr, state: TuiState, options: TuiOptions) -> None:
        self.stdscr = stdscr
        self.state = state
        self.options = options
        self.keymap = keymap_for_config(options.keybindings)
        self.theme_pairs: list[int] = []
        self.preview_pairs: dict[RGB, int] = {}
        self.accent_attr = curses.A_BOLD

    def run(self) -> None:
        curses.curs_set(0)
        self.stdscr.keypad(True)
        self.init_theme_colors()
        while not self.state.should_quit:
            self.render()
            key = self.stdscr.getch()
            self.handle_key(key)

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

    def handle_key(self, key: int) -> None:
        action = self.keymap.get(key)
        if self.state.help_open:
            if action in ("help", "quit", "back_or_quit") or key == 27:
                self.state = self.state.close_help()
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
        elif action == "open_settings":
            self.open_settings()
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

    def open_settings(self) -> None:
        theme = self.options.theme
        display = self.options.display
        custom_prices = dict(self.options.pricing.model_prices)
        keybindings = self.options.keybindings
        prediction = self.options.prediction
        model_names = settings_model_names(self.state.dataset, custom_prices)
        tab_index = 0
        model_index = 0
        rate_field_index = 0
        display_field_index = 0
        appearance_field_index = 0
        keybinding_index = 0
        misc_field_index = 0
        status = "settings: press 1-5 for tabs, enter/e to edit selected item"

        while True:
            model_names = settings_model_names(self.state.dataset, custom_prices)
            if not model_names:
                model_names = ["custom-model"]
            model_index = min(max(model_index, 0), len(model_names) - 1)
            self.render_settings(
                theme,
                display,
                custom_prices,
                model_names,
                tab_index,
                model_index,
                rate_field_index,
                display_field_index,
                appearance_field_index,
                keybindings,
                keybinding_index,
                prediction,
                misc_field_index,
                status,
            )
            key = self.stdscr.getch()

            if key in (ord("q"), 27):
                self.state = replace(self.state, status="settings canceled")
                return
            if ord("1") <= key <= ord(str(len(SETTINGS_TABS))):
                tab_index = int(chr(key)) - 1
                status = f"tab: {SETTINGS_TABS[tab_index]}"
                continue
            if key == ord("s"):
                pricing = PricingConfig(model_prices=tuple(sorted(custom_prices.items())))
                try:
                    path = save_theme_config(
                        theme,
                        display=display,
                        pricing=pricing,
                        keybindings=keybindings,
                        limits=self.options.limits,
                        prediction=prediction,
                    )
                except OSError as exc:
                    status = f"settings save failed: {exc}"
                    continue
                loaded = load_theme_config(path)
                self.options = replace(
                    self.options,
                    theme=loaded.config,
                    display=loaded.display,
                    pricing=loaded.pricing,
                    keybindings=loaded.keybindings,
                    limits=loaded.limits,
                    prediction=loaded.prediction,
                    theme_status=loaded.status,
                )
                self.keymap = keymap_for_config(loaded.keybindings)
                self.theme_pairs = []
                self.accent_attr = curses.A_BOLD
                self.init_theme_colors()
                self.state = replace(
                    self.state,
                    pricing=loaded.pricing,
                    status=f"settings saved: {path}",
                )
                return
            if key in (ord("h"), curses.KEY_LEFT):
                if tab_index == 0:
                    rate_field_index = (rate_field_index - 1) % len(RATE_FIELDS)
                    status = f"field: {RATE_FIELDS[rate_field_index]}"
                elif tab_index == 1:
                    display_field_index = (display_field_index - 1) % len(DISPLAY_SETTING_FIELDS)
                    status = f"display: {display_setting_label(DISPLAY_SETTING_FIELDS[display_field_index])}"
                elif tab_index == 2:
                    appearance_field_index = (appearance_field_index - 1) % len(APPEARANCE_SETTING_FIELDS)
                    status = f"appearance: {appearance_setting_label(APPEARANCE_SETTING_FIELDS[appearance_field_index])}"
                elif tab_index == 3:
                    keybinding_index = (keybinding_index - 1) % len(KEYBINDING_ACTIONS)
                    status = f"keybinding: {keybinding_action_label(KEYBINDING_ACTIONS[keybinding_index])}"
                else:
                    misc_field_index = (misc_field_index - 1) % len(MISC_SETTING_FIELDS)
                    status = f"misc: {misc_setting_label(MISC_SETTING_FIELDS[misc_field_index])}"
                continue
            if key in (ord("l"), curses.KEY_RIGHT):
                if tab_index == 0:
                    rate_field_index = (rate_field_index + 1) % len(RATE_FIELDS)
                    status = f"field: {RATE_FIELDS[rate_field_index]}"
                elif tab_index == 1:
                    display_field_index = (display_field_index + 1) % len(DISPLAY_SETTING_FIELDS)
                    status = f"display: {display_setting_label(DISPLAY_SETTING_FIELDS[display_field_index])}"
                elif tab_index == 2:
                    appearance_field_index = (appearance_field_index + 1) % len(APPEARANCE_SETTING_FIELDS)
                    status = f"appearance: {appearance_setting_label(APPEARANCE_SETTING_FIELDS[appearance_field_index])}"
                elif tab_index == 3:
                    keybinding_index = (keybinding_index + 1) % len(KEYBINDING_ACTIONS)
                    status = f"keybinding: {keybinding_action_label(KEYBINDING_ACTIONS[keybinding_index])}"
                else:
                    misc_field_index = (misc_field_index + 1) % len(MISC_SETTING_FIELDS)
                    status = f"misc: {misc_setting_label(MISC_SETTING_FIELDS[misc_field_index])}"
                continue
            if key in (ord("j"), ord("n"), curses.KEY_DOWN):
                if tab_index == 0:
                    model_index = min(model_index + 1, len(model_names) - 1)
                    status = f"model: {model_names[model_index]}"
                elif tab_index == 1:
                    display_field_index = (display_field_index + 1) % len(DISPLAY_SETTING_FIELDS)
                    status = f"display: {display_setting_label(DISPLAY_SETTING_FIELDS[display_field_index])}"
                elif tab_index == 2:
                    appearance_field_index = (appearance_field_index + 1) % len(APPEARANCE_SETTING_FIELDS)
                    status = f"appearance: {appearance_setting_label(APPEARANCE_SETTING_FIELDS[appearance_field_index])}"
                elif tab_index == 3:
                    keybinding_index = min(keybinding_index + 1, len(KEYBINDING_ACTIONS) - 1)
                    status = f"keybinding: {keybinding_action_label(KEYBINDING_ACTIONS[keybinding_index])}"
                else:
                    misc_field_index = (misc_field_index + 1) % len(MISC_SETTING_FIELDS)
                    status = f"misc: {misc_setting_label(MISC_SETTING_FIELDS[misc_field_index])}"
                continue
            if key in (ord("k"), ord("p"), curses.KEY_UP):
                if tab_index == 0:
                    model_index = max(model_index - 1, 0)
                    status = f"model: {model_names[model_index]}"
                elif tab_index == 1:
                    display_field_index = (display_field_index - 1) % len(DISPLAY_SETTING_FIELDS)
                    status = f"display: {display_setting_label(DISPLAY_SETTING_FIELDS[display_field_index])}"
                elif tab_index == 2:
                    appearance_field_index = (appearance_field_index - 1) % len(APPEARANCE_SETTING_FIELDS)
                    status = f"appearance: {appearance_setting_label(APPEARANCE_SETTING_FIELDS[appearance_field_index])}"
                elif tab_index == 3:
                    keybinding_index = max(keybinding_index - 1, 0)
                    status = f"keybinding: {keybinding_action_label(KEYBINDING_ACTIONS[keybinding_index])}"
                else:
                    misc_field_index = (misc_field_index - 1) % len(MISC_SETTING_FIELDS)
                    status = f"misc: {misc_setting_label(MISC_SETTING_FIELDS[misc_field_index])}"
                continue
            if key in (ord("a"),):
                if tab_index == 3:
                    action = KEYBINDING_ACTIONS[keybinding_index]
                    keybindings, status = self.capture_keybinding(
                        keybindings,
                        action,
                        append=True,
                    )
                    continue
                if tab_index != 0:
                    status = "add is only available on Model Pricing or Keybindings"
                    continue
                model = self.prompt_input("model name: ")
                if not model:
                    status = "add model canceled"
                    continue
                model = normalize_model_name(model)
                price = self.prompt_full_model_price(model, custom_prices.get(model) or MODEL_PRICES.get(model))
                if price is None:
                    status = "add model canceled"
                    continue
                custom_prices[model] = price
                model_index = settings_model_names(self.state.dataset, custom_prices).index(model)
                status = f"custom rate saved for {model}"
                continue
            if key in (ord("x"),):
                if tab_index == 3:
                    action = KEYBINDING_ACTIONS[keybinding_index]
                    keybindings = reset_keybinding(keybindings, action)
                    status = f"{keybinding_action_label(action)} reset to default"
                    continue
                if tab_index != 0:
                    status = "reset is only available on Model Pricing or Keybindings"
                    continue
                model = model_names[model_index]
                if model in custom_prices:
                    del custom_prices[model]
                    status = f"custom override removed for {model}"
                else:
                    status = f"{model} has no custom override"
                continue
            if key in (ord("e"), ord(" "), 10, 13, curses.KEY_ENTER):
                if tab_index == 1:
                    display, status = self.apply_display_setting(
                        display,
                        DISPLAY_SETTING_FIELDS[display_field_index],
                    )
                    continue
                if tab_index == 2:
                    theme, status = self.apply_appearance_setting(
                        theme,
                        APPEARANCE_SETTING_FIELDS[appearance_field_index],
                    )
                    continue
                if tab_index == 3:
                    action = KEYBINDING_ACTIONS[keybinding_index]
                    keybindings, status = self.apply_keybinding_setting(
                        keybindings,
                        action,
                    )
                    continue
                if tab_index == 4:
                    prediction, status = self.apply_misc_setting(
                        prediction,
                        MISC_SETTING_FIELDS[misc_field_index],
                    )
                    continue
                model = model_names[model_index]
                price = custom_prices.get(model) or MODEL_PRICES.get(model)
                if price is None:
                    price = self.prompt_full_model_price(model, None)
                    if price is None:
                        status = "rate edit canceled"
                        continue
                    custom_prices[model] = price
                    status = f"custom rate saved for {model}"
                    continue
                next_price = self.prompt_rate_field(model, price, RATE_FIELDS[rate_field_index])
                if next_price is None:
                    status = "rate edit canceled"
                    continue
                custom_prices[model] = next_price
                status = f"{model} {RATE_FIELDS[rate_field_index]} rate updated"

    def render_settings(
        self,
        theme: ThemeConfig,
        display: DisplayConfig,
        custom_prices: dict[str, ModelPrice],
        model_names: list[str],
        tab_index: int,
        model_index: int,
        rate_field_index: int,
        display_field_index: int,
        appearance_field_index: int,
        keybindings: KeybindingConfig,
        keybinding_index: int,
        prediction: PredictionConfig,
        misc_field_index: int,
        status: str,
    ) -> None:
        self.stdscr.erase()
        height, width = self.stdscr.getmaxyx()
        self.render_themed_text(0, 0, "Settings", curses.A_BOLD)
        self.render_settings_tabs(1, width, tab_index)
        content_top = 3
        if tab_index == 1:
            self.render_display_settings(content_top, width, display, display_field_index)
        elif tab_index == 2:
            self.render_appearance_settings(content_top, height, width, theme, appearance_field_index)
        elif tab_index == 3:
            self.render_keybinding_settings(
                content_top,
                height,
                width,
                keybindings,
                keybinding_index,
            )
        elif tab_index == 4:
            self.render_misc_settings(
                content_top,
                width,
                prediction,
                misc_field_index,
            )
        else:
            self.render_model_pricing_settings(
                content_top,
                height,
                width,
                custom_prices,
                model_names,
                model_index,
                rate_field_index,
            )

        self.render_themed_text(
            height - 2,
            0,
            status[: max(0, width - 1)],
            curses.A_DIM,
            start_index=1,
        )
        footer = (
            "1-5 tabs  h/j/k/l select  enter/e edit  model: a add x reset  keys: a add x reset  "
            "s save  q cancel"
        )
        self.render_themed_text(
            height - 1,
            0,
            footer[: max(0, width - 1)],
            curses.A_DIM,
            start_index=2,
        )
        self.stdscr.refresh()

    def render_settings_tabs(self, y: int, width: int, selected_tab: int) -> None:
        x = 0
        for index, label in enumerate(SETTINGS_TABS):
            text = f" {index + 1} {label} "
            attr = curses.A_REVERSE | curses.A_BOLD if index == selected_tab else 0
            if x + len(text) >= width:
                break
            self.safe_addstr(y, x, text, attr)
            x += len(text) + 1

    def render_display_settings(
        self,
        top: int,
        width: int,
        display: DisplayConfig,
        selected_field: int,
    ) -> None:
        rows = [
            ("cached_tokens", "Cached tokens column", on_off(display.show_cached_tokens)),
            ("cached_percent", "Cached input % column", on_off(display.show_cached_percent)),
            ("estimated_cost", "Estimated API cost column", on_off(display.show_estimated_cost)),
            ("reasoning_level", "Reasoning level column", on_off(display.show_reasoning_level)),
            ("cache_miss", "Cache miss column", on_off(display.show_cache_miss)),
            ("reasoning_tokens", "Reasoning tokens column", on_off(display.show_reasoning_tokens)),
            ("model", "Model column", on_off(display.show_model)),
            ("context", "CWD/title column", on_off(display.show_context)),
            (
                "model_width",
                "Model column width",
                "auto" if display.model_column_width is None else str(display.model_column_width),
            ),
        ]
        self.safe_addstr(top, 0, "Display Columns", self.accent_attr)
        for index, (_, label, value) in enumerate(rows):
            attr = curses.A_REVERSE if index == selected_field else 0
            self.safe_addstr(
                top + 2 + index,
                0,
                f"{'>' if index == selected_field else ' '} {label:<28} {value}",
                attr,
            )
        self.safe_addstr(
            top + 2 + len(rows) + 1,
            0,
            "Enter toggles boolean columns or edits model width.",
            curses.A_DIM,
        )

    def render_appearance_settings(
        self,
        top: int,
        height: int,
        width: int,
        theme: ThemeConfig,
        selected_field: int,
    ) -> None:
        rows = [
            ("flag", "Current preset", theme_current_preset_label(theme)),
            ("color", "Color mode", theme.color_mode),
            ("light", "Lightness", format_settings_rate(theme.lightness)),
            ("accent_line", "Accent line", on_off(theme.show_accent_line)),
            ("themed_bars", "Themed usage bars", on_off(theme.themed_bars)),
        ]
        self.safe_addstr(top, 0, "Appearance", self.accent_attr)
        for index, (_, label, value) in enumerate(rows):
            attr = curses.A_REVERSE if index == selected_field else 0
            self.safe_addstr(
                top + 2 + index,
                0,
                f"{'>' if index == selected_field else ' '} {label:<28} {value}",
                attr,
            )
        self.safe_addstr(
            top + 2 + len(rows) + 1,
            0,
            "Enter cycles values, toggles booleans, or edits lightness.",
            curses.A_DIM,
        )
        preview_top = top + 2 + len(rows) + 3
        self.safe_addstr(preview_top, 0, "Current Color Scheme", self.accent_attr)
        preview_y = preview_top + 2
        block_height = appearance_preview_block_height(height, preview_y)
        self.render_theme_preview(preview_y, width, theme, block_height)

    def render_keybinding_settings(
        self,
        top: int,
        height: int,
        width: int,
        keybindings: KeybindingConfig,
        selected_action: int,
    ) -> None:
        self.safe_addstr(top, 0, "Keybindings", self.accent_attr)
        self.safe_addstr(
            top + 1,
            0,
            "Enter captures a replacement key. a adds a key. x resets the selected action.",
            curses.A_DIM,
        )
        header_y = top + 3
        action_width = min(34, max(18, width // 3))
        self.safe_addstr(header_y, 0, "  " + f"{'action':<{action_width}} keys", curses.A_BOLD)
        row_count = max(0, height - header_y - 3)
        start_index = visible_start(selected_action, row_count, len(KEYBINDING_ACTIONS))
        visible = KEYBINDING_ACTIONS[start_index : start_index + row_count]
        for offset, action in enumerate(visible):
            row_index = start_index + offset
            selected = row_index == selected_action
            marker = ">" if selected else " "
            attr = curses.A_REVERSE if selected else 0
            y = header_y + 1 + offset
            label = truncate(keybinding_action_label(action), action_width)
            keys = format_keybinding_config(keybindings, action)
            self.safe_addstr(
                y,
                0,
                f"{marker} {label:<{action_width}} {keys}",
                attr,
            )

    def render_misc_settings(
        self,
        top: int,
        width: int,
        prediction: PredictionConfig,
        selected_field: int,
    ) -> None:
        rows = [
            (
                "prediction_algorithm",
                "Prediction algorithm",
                prediction_algorithm_label(prediction.algorithm),
            ),
        ]
        self.safe_addstr(top, 0, "Misc", self.accent_attr)
        for index, (_, label, value) in enumerate(rows):
            attr = curses.A_REVERSE if index == selected_field else 0
            self.safe_addstr(
                top + 2 + index,
                0,
                f"{'>' if index == selected_field else ' '} {label:<28} {value}",
                attr,
            )
        self.safe_addstr(
            top + 2 + len(rows) + 1,
            0,
            "Enter cycles prediction algorithms.",
            curses.A_DIM,
        )

    def render_theme_preview(
        self,
        y: int,
        width: int,
        theme: ThemeConfig,
        block_height: int,
    ) -> None:
        if not theme.enabled:
            self.safe_addstr(y, 0, "plain: colors disabled", curses.A_DIM)
            preview_width = min(36, max(0, width - 1))
            for row in range(block_height):
                self.safe_addstr(y + 2 + row, 0, "#" * preview_width, curses.A_DIM)
            return

        palette = theme_palette(theme)
        if not palette:
            self.safe_addstr(y, 0, "no colors available", curses.A_DIM)
            return

        label = f"{theme.preset} / {theme.color_mode} / light {format_settings_rate(theme.lightness)}"
        self.safe_addstr(y, 0, label[: max(0, width - 1)], curses.A_DIM)
        swatch_x = 0
        for _index, rgb in enumerate(palette):
            if swatch_x + 3 >= width:
                break
            attr = self.preview_attr(rgb, curses.A_REVERSE | curses.A_BOLD)
            self.safe_addstr(y + 1, swatch_x, "  ", attr)
            swatch_x += 3

        preview_width = min(48, max(0, width - 1))
        self.render_palette_block(y + 2, 0, preview_width, block_height, palette)

    def render_model_pricing_settings(
        self,
        top: int,
        height: int,
        width: int,
        custom_prices: dict[str, ModelPrice],
        model_names: list[str],
        model_index: int,
        rate_field_index: int,
    ) -> None:
        model_width, input_x, cached_x, output_x, source_x = settings_columns(width)
        self.safe_addstr(top, 0, "Model Pricing", self.accent_attr)
        self.safe_addstr(
            top + 1,
            0,
            "Model rates are USD per 1M tokens. Custom rates override built-ins.",
            curses.A_DIM,
        )

        header_y = top + 3
        self.safe_addstr(header_y, 0, "  " + f"{'model':<{model_width}}", curses.A_BOLD)
        self.safe_addstr(header_y, input_x, f"{'input':>10}", curses.A_BOLD)
        self.safe_addstr(header_y, cached_x, f"{'cached':>10}", curses.A_BOLD)
        self.safe_addstr(header_y, output_x, f"{'output':>10}", curses.A_BOLD)
        self.safe_addstr(header_y, source_x, "source", curses.A_BOLD)

        row_count = max(0, height - header_y - 3)
        start_index = visible_start(model_index, row_count, len(model_names))
        visible = model_names[start_index : start_index + row_count]
        for offset, model in enumerate(visible):
            row_index = start_index + offset
            y = header_y + 1 + offset
            selected = row_index == model_index
            price = effective_settings_price(model, custom_prices)
            source = settings_price_source(model, custom_prices)
            row_attr = curses.A_REVERSE if selected else 0
            marker = ">" if selected else " "
            self.safe_addstr(
                y,
                0,
                f"{marker} {truncate(model, model_width):<{model_width}}",
                row_attr,
            )
            for index, (field, x) in enumerate(
                zip(RATE_FIELDS, (input_x, cached_x, output_x))
            ):
                attr = row_attr
                if selected and index == rate_field_index:
                    attr = curses.A_REVERSE | curses.A_BOLD
                self.safe_addstr(
                    y,
                    x,
                    f"{settings_rate_text(price, field):>10}",
                    attr,
                )
            self.safe_addstr(y, source_x, source, row_attr)

    def apply_display_setting(
        self,
        display: DisplayConfig,
        field: str,
    ) -> tuple[DisplayConfig, str]:
        if field == "cached_tokens":
            next_display = replace(
                display,
                show_cached_tokens=not display.show_cached_tokens,
            )
            return next_display, f"cached tokens column: {on_off(next_display.show_cached_tokens)}"
        if field == "cached_percent":
            next_display = replace(
                display,
                show_cached_percent=not display.show_cached_percent,
            )
            return next_display, f"cached % column: {on_off(next_display.show_cached_percent)}"
        if field == "estimated_cost":
            next_display = replace(
                display,
                show_estimated_cost=not display.show_estimated_cost,
            )
            return next_display, f"estimated cost column: {on_off(next_display.show_estimated_cost)}"
        if field == "reasoning_level":
            next_display = replace(
                display,
                show_reasoning_level=not display.show_reasoning_level,
            )
            return next_display, f"reasoning level column: {on_off(next_display.show_reasoning_level)}"
        if field == "cache_miss":
            next_display = replace(
                display,
                show_cache_miss=not display.show_cache_miss,
            )
            return next_display, f"cache miss column: {on_off(next_display.show_cache_miss)}"
        if field == "reasoning_tokens":
            next_display = replace(
                display,
                show_reasoning_tokens=not display.show_reasoning_tokens,
            )
            return next_display, f"reasoning tokens column: {on_off(next_display.show_reasoning_tokens)}"
        if field == "model":
            next_display = replace(
                display,
                show_model=not display.show_model,
            )
            return next_display, f"model column: {on_off(next_display.show_model)}"
        if field == "context":
            next_display = replace(
                display,
                show_context=not display.show_context,
            )
            return next_display, f"cwd/title column: {on_off(next_display.show_context)}"

        width_value = self.prompt_input(
            "model column width 8..40 or auto: ",
            "auto" if display.model_column_width is None else str(display.model_column_width),
        )
        if width_value is None:
            return display, "model width unchanged"
        parsed_width = parse_settings_model_width(width_value)
        if isinstance(parsed_width, str):
            return display, parsed_width
        next_display = replace(display, model_column_width=parsed_width)
        status = (
            "model column width: auto"
            if parsed_width is None
            else f"model column width: {parsed_width}"
        )
        return next_display, status

    def apply_appearance_setting(
        self,
        theme: ThemeConfig,
        field: str,
    ) -> tuple[ThemeConfig, str]:
        if field == "flag":
            next_theme = self.choose_flag_preset(theme)
            if next_theme is None:
                return theme, "flag preset unchanged"
            return next_theme, f"flag preset: {theme_preset_label(next_theme)}"
        if field == "color":
            next_theme = cycle_theme_color_mode(theme)
            return next_theme, f"color mode: {next_theme.color_mode}"
        if field == "accent_line":
            next_theme = replace(theme, show_accent_line=not theme.show_accent_line)
            return next_theme, f"accent line: {on_off(next_theme.show_accent_line)}"
        if field == "themed_bars":
            next_theme = replace(theme, themed_bars=not theme.themed_bars)
            return next_theme, f"themed usage bars: {on_off(next_theme.themed_bars)}"

        lightness_value = self.prompt_input(
            "theme lightness 0..1: ",
            format_settings_rate(theme.lightness),
        )
        if lightness_value is None:
            return theme, "theme lightness unchanged"
        parsed_lightness = parse_settings_lightness(lightness_value)
        if isinstance(parsed_lightness, str):
            return theme, parsed_lightness
        next_theme = replace(theme, lightness=parsed_lightness)
        return next_theme, f"theme lightness: {format_settings_rate(parsed_lightness)}"

    def apply_misc_setting(
        self,
        prediction: PredictionConfig,
        field: str,
    ) -> tuple[PredictionConfig, str]:
        if field == "prediction_algorithm":
            next_prediction = cycle_prediction_algorithm(prediction)
            return (
                next_prediction,
                f"prediction algorithm: {prediction_algorithm_label(next_prediction.algorithm)}",
            )
        return prediction, "unknown misc setting"

    def apply_keybinding_setting(
        self,
        keybindings: KeybindingConfig,
        action: str,
    ) -> tuple[KeybindingConfig, str]:
        return self.capture_keybinding(keybindings, action, append=False)

    def capture_keybinding(
        self,
        keybindings: KeybindingConfig,
        action: str,
        append: bool,
    ) -> tuple[KeybindingConfig, str]:
        label = self.capture_keybinding_label(
            f"{keybinding_action_label(action)}: press key to bind"
        )
        if label is None:
            return keybindings, "unsupported key"
        labels = keybindings.labels(action)
        if append:
            if label in labels:
                return keybindings, f"{label} is already assigned to {keybinding_action_label(action)}"
            next_labels = (*labels, label)
        else:
            next_labels = (label,)
        try:
            next_keybindings = update_keybinding(keybindings, action, next_labels)
        except ValueError as exc:
            return keybindings, str(exc)
        return (
            next_keybindings,
            f"{keybinding_action_label(action)}: {format_keybinding_labels(next_labels)}",
        )

    def capture_keybinding_label(self, prompt: str) -> str | None:
        height, width = self.stdscr.getmaxyx()
        self.stdscr.move(height - 1, 0)
        self.stdscr.clrtoeol()
        self.safe_addstr(height - 1, 0, prompt[: max(0, width - 1)], curses.A_DIM)
        key = self.stdscr.getch()
        return key_label_for_code(key)

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

    def render(self) -> None:
        self.stdscr.erase()
        height, width = self.stdscr.getmaxyx()
        self.render_header(width)
        if self.state.view == "overview":
            self.render_overview(height, width)
        elif self.state.view == "daily":
            self.render_daily(height, width)
        elif self.state.view == "weekly":
            self.render_weekly(height, width)
        elif self.state.view == "monthly":
            self.render_monthly(height, width)
        elif self.state.view == "hourly":
            self.render_hourly(height, width)
        elif self.state.view == "sessions":
            self.render_sessions(height, width)
        elif self.state.view == "details":
            self.render_details(height, width)
        if self.state.help_open:
            self.render_help(height, width)
        self.render_footer(height, width)
        self.stdscr.refresh()

    def render_header(self, width: int) -> None:
        self.render_themed_text(0, 0, "Codex Token Usage", curses.A_BOLD)
        self.render_tabs(1, width)
        filters = []
        if self.state.filter_text:
            filters.append(f"filter={self.state.filter_text}")
        filters.append(f"range={self.state.range_label()}")
        filters.append(
            f"sort={self.state.sort_field} {self.state.sort_direction_label}"
        )
        self.render_themed_text(
            2,
            0,
            "  ".join(filters)[: max(0, width - 1)],
            curses.A_DIM,
            start_index=2,
        )
        self.render_accent_line(3, width)

    def render_tabs(self, y: int, width: int) -> None:
        x = 0
        for index, view in enumerate(TAB_VIEWS):
            label = f" {VIEW_LABELS[view]} "
            attr = (
                self.theme_attr(index, curses.A_REVERSE | curses.A_BOLD)
                if self.state.tab_view == view
                else self.theme_attr(index)
            )
            if x + len(label) >= width:
                break
            self.safe_addstr(y, x, label, attr)
            x += len(label) + 1

    def render_accent_line(self, y: int, width: int) -> None:
        if not self.options.theme.show_accent_line or not self.theme_pairs or width <= 1:
            return
        segments = themed_bar_segments(
            1,
            1,
            width - 1,
            self.options.theme,
            fill_char="-",
            empty_char="-",
        )
        self.render_bar_segments(y, 0, segments)

    def render_overview(self, height: int, width: int) -> None:
        totals = self.state.filtered_totals()
        rows = [
            ("Sessions", str(len(self.state.visible_sessions()))),
            ("Total tokens", format_int(totals.total_tokens)),
            ("Input tokens", format_int(totals.input_tokens)),
            ("Output tokens", format_int(totals.output_tokens)),
            ("Cached input", format_int(totals.cached_input_tokens)),
            ("Cache miss input", format_int(totals.cache_miss_input_tokens)),
            ("Reasoning output", format_int(totals.reasoning_output_tokens)),
            ("Codex home", str(self.state.dataset.codex_home)),
            ("Loaded", self.state.dataset.loaded_at.isoformat()),
            ("SQLite metadata", "yes" if self.state.dataset.sqlite_available else "no"),
        ]
        if self.options.display.show_cached_percent:
            rows.insert(5, ("Cached input %", format_percent(totals.cached_input_percent)))
        if self.options.display.show_estimated_cost:
            estimate = estimate_sessions_cost(
                self.state.visible_sessions(),
                self.state.pricing,
            )
            rows.insert(7, ("Estimated API cost", format_cost(estimate)))
            if estimate.unpriced_sessions:
                rows.insert(
                    8,
                    ("Unpriced sessions", format_int(estimate.unpriced_sessions)),
                )
        if self.state.dataset.sqlite_error:
            rows.append(("SQLite note", self.state.dataset.sqlite_error))
        forecast = make_usage_forecast(
            replace(self.state.dataset, sessions=tuple(self.state.visible_sessions())),
            self.options.limits,
            prediction=self.options.prediction,
        )
        rows.append(
            (
                "Prediction algorithm",
                prediction_algorithm_label(self.options.prediction.algorithm),
            )
        )
        rows.extend(prediction_key_values(forecast))
        if forecast.has_limits:
            rows.extend(forecast_key_values(forecast))
        self.render_key_values(4, rows, width, height)

    def render_daily(self, height: int, width: int) -> None:
        rows = self.state.daily_rows()
        self.render_usage_rows("date", rows, height, width)

    def render_weekly(self, height: int, width: int) -> None:
        rows = self.state.weekly_rows()
        forecast = make_usage_forecast(
            replace(self.state.dataset, sessions=tuple(self.state.visible_sessions())),
            self.options.limits,
            prediction=self.options.prediction,
        )
        self.render_usage_rows("week", rows, height, width, forecast.weekly)

    def render_monthly(self, height: int, width: int) -> None:
        rows = self.state.monthly_rows()
        self.render_usage_rows("month", rows, height, width)

    def render_hourly(self, height: int, width: int) -> None:
        rows = self.state.hourly_rows()
        self.render_usage_rows("hour", rows, height, width)

    def aggregate_header_fields(self) -> str:
        fields: list[tuple[str, int]] = [
            ("sessions", 8),
            ("total", 12),
        ]
        if self.options.display.show_cached_tokens:
            fields.append(("cached", 12))
        if self.options.display.show_cached_percent:
            fields.append(("cached%", 8))
        if self.options.display.show_estimated_cost:
            fields.append(("est $", 10))
        if self.options.display.show_cache_miss:
            fields.append(("miss", 12))
        if self.options.display.show_reasoning_tokens:
            fields.append(("reason", 10))
        return self.right_aligned_fields(fields)

    def aggregate_value_fields(self, row) -> str:
        fields: list[tuple[str, int]] = [
            (format_int(row.sessions), 8),
            (format_int(row.tokens.total_tokens), 12),
        ]
        if self.options.display.show_cached_tokens:
            fields.append((format_int(row.tokens.cached_input_tokens), 12))
        if self.options.display.show_cached_percent:
            fields.append((format_percent(row.tokens.cached_input_percent), 8))
        if self.options.display.show_estimated_cost:
            fields.append((format_cost(row.estimated_cost), 10))
        if self.options.display.show_cache_miss:
            fields.append((format_int(row.tokens.cache_miss_input_tokens), 12))
        if self.options.display.show_reasoning_tokens:
            fields.append((format_int(row.tokens.reasoning_output_tokens), 10))
        return self.right_aligned_fields(fields)

    def session_header_fields(self) -> str:
        fields: list[tuple[str, int]] = [
            ("total", 10),
        ]
        if self.options.display.show_cached_tokens:
            fields.append(("cached", 10))
        if self.options.display.show_cached_percent:
            fields.append(("cached%", 8))
        if self.options.display.show_estimated_cost:
            fields.append(("est $", 10))
        if self.options.display.show_reasoning_level:
            fields.append(("effort", 8))
        if self.options.display.show_cache_miss:
            fields.append(("miss", 10))
        if self.options.display.show_reasoning_tokens:
            fields.append(("reason", 8))
        return self.right_aligned_fields(fields)

    def session_value_fields(self, session: SessionUsage) -> str:
        fields: list[tuple[str, int]] = [
            (format_int(session.tokens.total_tokens), 10),
        ]
        if self.options.display.show_cached_tokens:
            fields.append((format_int(session.tokens.cached_input_tokens), 10))
        if self.options.display.show_cached_percent:
            fields.append((format_percent(session.tokens.cached_input_percent), 8))
        if self.options.display.show_estimated_cost:
            fields.append(
                (format_cost(estimate_session_cost(session, self.state.pricing)), 10)
            )
        if self.options.display.show_reasoning_level:
            fields.append((truncate(session.reasoning_level, 8), 8))
        if self.options.display.show_cache_miss:
            fields.append((format_int(session.tokens.cache_miss_input_tokens), 10))
        if self.options.display.show_reasoning_tokens:
            fields.append((format_int(session.tokens.reasoning_output_tokens), 8))
        return self.right_aligned_fields(fields)

    @staticmethod
    def right_aligned_fields(fields: list[tuple[str, int]]) -> str:
        return " ".join(f"{value:>{width}}" for value, width in fields)

    @staticmethod
    def session_model_width(width: int, configured_width: int | None = None) -> int:
        if configured_width is not None:
            return configured_width
        if width >= 150:
            return 24
        if width >= 120:
            return 22
        if width >= 100:
            return 18
        return 14

    def render_usage_rows(
        self,
        label: str,
        rows,
        height: int,
        width: int,
        forecast_window: ForecastWindow | None = None,
    ) -> None:
        max_total = max((row.tokens.total_tokens for row in rows), default=0)
        header = (
            f"{label:<16} {'usage':<14} "
            f"{self.aggregate_header_fields()}"
        )
        if forecast_window and forecast_window.enabled and label == "week":
            header += " forecast"
        self.render_themed_text(4, 0, header[: max(0, width - 1)], curses.A_BOLD)
        for offset, row in enumerate(rows[: max(0, height - 7)], start=5):
            prefix = f"{row.key:<16} "
            suffix = " " + self.aggregate_value_fields(row)
            status = usage_row_forecast_status(label, row.key, forecast_window)
            if status:
                suffix += f" {status}"
            self.safe_addstr(offset, 0, prefix)
            self.render_themed_bar(
                offset,
                len(prefix),
                row.tokens.total_tokens,
                max_total,
                14,
            )
            self.safe_addstr(offset, len(prefix) + 14, suffix)

    def render_sessions(self, height: int, width: int) -> None:
        sessions = self.state.visible_sessions()
        max_total = max((session.tokens.total_tokens for session in sessions), default=0)
        rows_available = max(0, height - 7)
        start_index = visible_start(self.state.selected_index, rows_available, len(sessions))
        model_width = self.session_model_width(
            width,
            self.options.display.model_column_width,
        )
        header = f"{'session':<12} {'usage':<10} {self.session_header_fields()}"
        if self.options.display.show_model:
            header += f"  {'model':<{model_width}}"
        if self.options.display.show_context:
            header += "  cwd/title"
        self.render_themed_text(4, 0, header[: max(0, width - 1)], curses.A_BOLD)
        visible = sessions[start_index : start_index + rows_available]
        for row_offset, session in enumerate(visible):
            row_index = start_index + row_offset
            marker = ">" if row_index == self.state.selected_index else " "
            context = f"{session.cwd}  {session.title}"
            prefix = (
                f"{marker}{session.session_id[:12]:<12} "
            )
            suffix = " " + self.session_value_fields(session)
            if self.options.display.show_model:
                suffix += f"  {truncate(session.model, model_width):<{model_width}}"
            if self.options.display.show_context:
                suffix += f"  {truncate(context, max(8, width // 3))}"
            attr = (
                self.theme_attr(row_offset, curses.A_REVERSE)
                if row_index == self.state.selected_index
                else 0
            )
            y = 5 + row_offset
            self.safe_addstr(y, 0, prefix, attr)
            self.render_themed_bar(
                y,
                len(prefix),
                session.tokens.total_tokens,
                max_total,
                10,
                attr,
            )
            self.safe_addstr(y, len(prefix) + 10, suffix, attr)

    def render_details(self, height: int, width: int) -> None:
        session = self.state.selected_session()
        if session is None:
            self.safe_addstr(2, 0, "No session selected.")
            return
        rows = [
            ("Session", session.session_id),
            ("Title", session.title),
            ("Model", session.model),
            ("Reasoning level", session.reasoning_level),
            ("CWD", session.cwd),
            ("Created", session.created_at.isoformat() if session.created_at else ""),
            ("Updated", session.updated_at.isoformat() if session.updated_at else ""),
            ("Path", str(session.path)),
            ("Total", format_int(session.tokens.total_tokens)),
            ("Input", format_int(session.tokens.input_tokens)),
            ("Output", format_int(session.tokens.output_tokens)),
            ("Cached input", format_int(session.tokens.cached_input_tokens)),
            ("Cache miss input", format_int(session.tokens.cache_miss_input_tokens)),
            ("Reasoning output", format_int(session.tokens.reasoning_output_tokens)),
            ("Corrupt lines skipped", str(session.corrupt_lines)),
        ]
        if self.options.display.show_cached_percent:
            rows.insert(
                11,
                ("Cached input %", format_percent(session.tokens.cached_input_percent)),
            )
        if self.options.display.show_estimated_cost:
            rows.insert(
                13,
                (
                    "Estimated API cost",
                    format_cost(estimate_session_cost(session, self.state.pricing)),
                ),
            )
        self.render_key_values(4, rows, width, height)

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

    def safe_addstr(self, y: int, x: int, text: str, attr: int = 0) -> None:
        height, width = self.stdscr.getmaxyx()
        if y < 0 or y >= height or x < 0 or x >= width:
            return
        self.stdscr.addstr(y, x, text[: max(0, width - x - 1)], attr)

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
        text = text[: max(0, width - x - 1)]
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


def usage_bar(value: int, max_value: int, width: int) -> str:
    if width <= 0:
        return ""
    if max_value <= 0 or value <= 0:
        return "." * width
    filled = max(1, round((value / max_value) * width))
    filled = min(width, filled)
    return "#" * filled + "." * (width - filled)


def settings_model_names(
    dataset: UsageDataset,
    custom_prices: dict[str, ModelPrice],
) -> list[str]:
    names = set(MODEL_PRICES)
    names.update(custom_prices)
    for session in dataset.sessions:
        model = normalize_model_name(session.model)
        if model and model != "(unknown)":
            names.add(model)
    return sorted(names)


def effective_settings_price(
    model: str,
    custom_prices: dict[str, ModelPrice],
) -> ModelPrice | None:
    return custom_prices.get(model) or MODEL_PRICES.get(model)


def settings_price_source(model: str, custom_prices: dict[str, ModelPrice]) -> str:
    if model in custom_prices:
        return "custom"
    if model in MODEL_PRICES:
        return "built-in"
    return "unpriced"


def settings_rate_text(price: ModelPrice | None, field: str) -> str:
    if price is None:
        return "n/a"
    if field == "input":
        return format_settings_rate(price.input_per_million)
    if field == "cached":
        if price.cached_input_per_million is None:
            return "-"
        return format_settings_rate(price.cached_input_per_million)
    if field == "output":
        return format_settings_rate(price.output_per_million)
    return "n/a"


def display_setting_label(field: str) -> str:
    labels = {
        "cached_tokens": "cached tokens",
        "cached_percent": "cached %",
        "estimated_cost": "estimated cost",
        "reasoning_level": "reasoning level",
        "cache_miss": "cache miss",
        "reasoning_tokens": "reasoning tokens",
        "model": "model",
        "context": "cwd/title",
        "model_width": "model width",
    }
    return labels.get(field, field)


def appearance_setting_label(field: str) -> str:
    labels = {
        "flag": "flag preset",
        "color": "color mode",
        "light": "lightness",
        "accent_line": "accent line",
        "themed_bars": "themed usage bars",
    }
    return labels.get(field, field)


def misc_setting_label(field: str) -> str:
    labels = {
        "prediction_algorithm": "prediction algorithm",
    }
    return labels.get(field, field)


def cycle_prediction_algorithm(prediction: PredictionConfig) -> PredictionConfig:
    try:
        index = PREDICTION_ALGORITHMS.index(prediction.algorithm)
    except ValueError:
        index = 0
    algorithm = PREDICTION_ALGORITHMS[(index + 1) % len(PREDICTION_ALGORITHMS)]
    return PredictionConfig(algorithm=algorithm)


def prediction_algorithm_label(algorithm: str) -> str:
    labels = {
        "recent_rate": "recent rate",
        "previous_period": "previous period",
    }
    return labels.get(algorithm, algorithm.replace("_", " "))


def keybinding_action_label(action: str) -> str:
    return KEYBINDING_ACTION_LABELS.get(action, action.replace("_", " "))


def format_settings_rate(value: float) -> str:
    return f"{value:g}"


def parse_settings_rate(value: str) -> float | str:
    try:
        rate = float(value)
    except ValueError:
        return "rate must be a number"
    if rate < 0:
        return "rate must not be negative"
    return rate


def parse_settings_model_width(value: str) -> int | None | str:
    value = value.strip().lower()
    if value in ("", "auto"):
        return None
    try:
        width = int(value)
    except ValueError:
        return "model width must be auto or an integer"
    if width < 8 or width > 40:
        return "model width must be from 8 to 40"
    return width


def theme_preset_label(theme: ThemeConfig) -> str:
    return theme.preset if theme.enabled else "plain"


def theme_current_preset(theme: ThemeConfig) -> str:
    if theme.preset in PRESET_NAMES:
        return theme.preset
    return DEFAULT_THEME_PRESET


def theme_current_preset_label(theme: ThemeConfig) -> str:
    preset = theme_current_preset(theme)
    return preset if theme.enabled else f"{preset} (plain)"


def flag_display_name(preset: str) -> str:
    names = {
        "trans": "transgender",
    }
    return names.get(preset, preset)


def flag_picker_block_height(terminal_height: int) -> int:
    if terminal_height >= 22:
        return FLAG_PICKER_PREVIEW_HEIGHT
    if terminal_height >= 18:
        return 4
    return 3


def flag_picker_visible_rows(terminal_height: int) -> int:
    block_height = flag_picker_block_height(terminal_height)
    row_height = block_height + 3
    available = max(0, terminal_height - FLAG_PICKER_TOP - 1)
    return max(1, min(2, available // row_height))


def flag_picker_page_size(terminal_height: int) -> int:
    return FLAG_PICKER_COLUMNS * flag_picker_visible_rows(terminal_height)


def appearance_preview_block_height(terminal_height: int, preview_y: int) -> int:
    block_start = preview_y + 2
    available = terminal_height - 2 - block_start
    return max(0, min(APPEARANCE_PREVIEW_BLOCK_HEIGHT, available))


def cycle_theme_preset(theme: ThemeConfig) -> ThemeConfig:
    current = theme_preset_label(theme)
    index = THEME_PRESET_CHOICES.index(current)
    next_preset = THEME_PRESET_CHOICES[(index + 1) % len(THEME_PRESET_CHOICES)]
    if next_preset == "plain":
        return replace(theme, enabled=False)
    return replace(theme, enabled=True, preset=next_preset)


def cycle_theme_color_mode(theme: ThemeConfig) -> ThemeConfig:
    index = COLOR_MODES.index(theme.color_mode)
    return replace(theme, color_mode=COLOR_MODES[(index + 1) % len(COLOR_MODES)])


def parse_settings_lightness(value: str) -> float | str:
    try:
        lightness = float(value)
    except ValueError:
        return "lightness must be a number from 0 to 1"
    if lightness < 0 or lightness > 1:
        return "lightness must be from 0 to 1"
    return lightness


def settings_columns(width: int) -> tuple[int, int, int, int, int]:
    rate_width = 12
    source_width = 10
    model_width = max(12, min(42, width - (2 + rate_width * 3 + source_width + 5)))
    input_x = 2 + model_width + 2
    cached_x = input_x + rate_width
    output_x = cached_x + rate_width
    source_x = output_x + rate_width
    return model_width, input_x, cached_x, output_x, source_x


def on_off(value: bool) -> str:
    return "on" if value else "off"


def visible_start(selected_index: int, rows_available: int, total_rows: int) -> int:
    if rows_available <= 0 or total_rows <= rows_available:
        return 0
    selected_index = min(max(0, selected_index), total_rows - 1)
    return min(max(0, selected_index - rows_available + 1), total_rows - rows_available)


def truncate(value: str, width: int) -> str:
    if width <= 0:
        return ""
    if len(value) <= width:
        return value
    if width == 1:
        return "~"
    return value[: width - 1] + "~"
