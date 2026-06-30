from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date, timedelta
from pathlib import Path
from typing import Callable

from ..forecast import LimitConfig, PredictionConfig
from ..keybindings import KeybindingConfig
from ..models import SessionUsage, TokenBreakdown, UsageDataset
from ..pricing import PricingConfig, estimate_session_cost
from ..report import ReportRow, make_report_rows
from ..theme import DEFAULT_SHUTDOWN_SECONDS, DisplayConfig, ThemeConfig

VIEWS = (
    "overview",
    "daily",
    "weekly",
    "monthly",
    "hourly",
    "projects",
    "sessions",
    "details",
)
TAB_VIEWS = (
    "overview",
    "daily",
    "weekly",
    "monthly",
    "hourly",
    "projects",
    "sessions",
)
VIEW_LABELS = {
    "overview": "Overview",
    "daily": "By Date",
    "weekly": "By Week",
    "monthly": "By Month",
    "hourly": "By Hour",
    "projects": "By Project",
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
    auto_refresh_seconds: int | None = None
    shutdown_seconds: float = DEFAULT_SHUTDOWN_SECONDS


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
    about_open: bool = False
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
        return replace(self, help_open=True, about_open=False, status="")

    def close_help(self) -> "TuiState":
        return replace(self, help_open=False, status="")

    def toggle_help(self) -> "TuiState":
        return self.close_help() if self.help_open else self.open_help()

    def open_about(self) -> "TuiState":
        return replace(self, about_open=True, help_open=False, status="")

    def close_about(self) -> "TuiState":
        return replace(self, about_open=False, status="")

    def toggle_about(self) -> "TuiState":
        return self.close_about() if self.about_open else self.open_about()

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

    def project_rows(self):
        dataset = replace(self.dataset, sessions=tuple(self.visible_sessions()))
        return self.sorted_report_rows(
            make_report_rows(dataset, group_by="project", pricing=self.pricing)
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


def reasoning_level_sort_key(level: str) -> tuple[int, str]:
    normalized = level.casefold()
    return (REASONING_LEVEL_RANK.get(normalized, 0), normalized)


def datetime_sort_key(value) -> float:
    if value is None:
        return float("-inf")
    return value.timestamp()
