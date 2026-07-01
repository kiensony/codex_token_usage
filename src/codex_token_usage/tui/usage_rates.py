from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time
from typing import Iterable

from ..forecast import (
    FIVE_HOUR_WINDOW,
    iso_week_start,
    normalize_datetime,
    sessions_in_window,
)
from ..models import SessionUsage
from ..report import format_int


@dataclass(frozen=True)
class UsageRateWindow:
    label: str
    window_start: datetime
    window_end: datetime
    tokens: int
    requests: int

    @property
    def duration_seconds(self) -> float:
        return max(1.0, (self.window_end - self.window_start).total_seconds())

    @property
    def tokens_per_second(self) -> float:
        return self.tokens / self.duration_seconds

    @property
    def requests_per_second(self) -> float:
        return self.requests / self.duration_seconds


def current_usage_rate_rows(
    sessions: Iterable[SessionUsage],
    as_of: datetime,
) -> list[tuple[str, str]]:
    return [
        (window.label, format_usage_rate_indicator(window))
        for window in current_usage_rate_windows(sessions, as_of)
    ]


def current_usage_rate_windows(
    sessions: Iterable[SessionUsage],
    as_of: datetime,
) -> tuple[UsageRateWindow, ...]:
    current = normalize_datetime(as_of)
    session_tuple = tuple(sessions)
    month_start = datetime.combine(
        current.date().replace(day=1),
        time.min,
        tzinfo=current.tzinfo,
    )
    windows = (
        ("Current 5h TPS/RPS", current - FIVE_HOUR_WINDOW),
        (
            "Current day TPS/RPS",
            datetime.combine(current.date(), time.min, tzinfo=current.tzinfo),
        ),
        ("Current week TPS/RPS", iso_week_start(current)),
        ("Current month TPS/RPS", month_start),
    )
    return tuple(
        usage_rate_window(label, session_tuple, start, current)
        for label, start in windows
    )


def usage_rate_window(
    label: str,
    sessions: Iterable[SessionUsage],
    window_start: datetime,
    window_end: datetime,
) -> UsageRateWindow:
    window_sessions = sessions_in_window(sessions, window_start, window_end)
    return UsageRateWindow(
        label=label,
        window_start=window_start,
        window_end=window_end,
        tokens=sum(session.tokens.total_tokens for session in window_sessions),
        requests=sum(session_request_count(session) for session in window_sessions),
    )


def session_request_count(session: SessionUsage) -> int:
    if session.request_count > 0:
        return session.request_count
    if session.has_token_event or session.tokens.total_tokens > 0:
        return 1
    return 0


def format_usage_rate_indicator(window: UsageRateWindow) -> str:
    return (
        f"{format_rate(window.tokens_per_second)} tok/s  "
        f"{format_rate(window.requests_per_second)} req/s  "
        f"({format_int(window.tokens)} tokens, {format_int(window.requests)} req)"
    )


def format_rate(value: float) -> str:
    if value >= 100:
        return f"{value:,.0f}"
    if value >= 10:
        return f"{value:,.1f}"
    if value >= 1:
        return f"{value:,.2f}"
    if value >= 0.01:
        return f"{value:.3f}"
    return f"{value:.6f}"
