from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timedelta
from typing import Iterable

from ..forecast import (
    DAY_WINDOW,
    FIVE_HOUR_WINDOW,
    WEEK_WINDOW,
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


@dataclass(frozen=True)
class StatisticUsageRateWindow:
    label: str
    window_start: datetime
    window_end: datetime
    tokens: int
    requests: int

    @property
    def duration_seconds(self) -> float:
        return max(1.0, (self.window_end - self.window_start).total_seconds())

    @property
    def duration_minutes(self) -> float:
        return self.duration_seconds / 60

    @property
    def duration_hours(self) -> float:
        return self.duration_seconds / 3600

    @property
    def rps(self) -> float:
        return self.requests / self.duration_seconds

    @property
    def rpm(self) -> float:
        return self.requests / self.duration_minutes

    @property
    def rph(self) -> float:
        return self.requests / self.duration_hours

    @property
    def tps(self) -> float:
        return self.tokens / self.duration_seconds

    @property
    def tpm(self) -> float:
        return self.tokens / self.duration_minutes

    @property
    def tph(self) -> float:
        return self.tokens / self.duration_hours

    @property
    def tpr(self) -> float:
        if self.requests <= 0:
            return 0.0
        return self.tokens / self.requests


@dataclass(frozen=True)
class StatisticLineSeries:
    label: str
    bucket_label: str
    values: tuple[float, ...]


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


def statistic_usage_rate_windows(
    sessions: Iterable[SessionUsage],
    as_of: datetime,
) -> tuple[StatisticUsageRateWindow, ...]:
    current = normalize_datetime(as_of)
    hour_end = rounded_hour_start(current)
    day_end = datetime.combine(current.date(), time.min, tzinfo=current.tzinfo)
    week_end = iso_week_start(current)
    month_end = datetime.combine(
        current.date().replace(day=1),
        time.min,
        tzinfo=current.tzinfo,
    )
    session_tuple = tuple(sessions)
    windows = (
        ("Last hour", hour_end - timedelta(hours=1), hour_end),
        ("Last 5h", hour_end - FIVE_HOUR_WINDOW, hour_end),
        ("Last day", day_end - DAY_WINDOW, day_end),
        ("Last week", week_end - WEEK_WINDOW, week_end),
        ("Last month", previous_month_start(month_end), month_end),
    )
    return tuple(
        statistic_usage_rate_window(label, session_tuple, start, end)
        for label, start, end in windows
    )


def statistic_line_series(
    sessions: Iterable[SessionUsage],
    as_of: datetime,
) -> tuple[StatisticLineSeries, StatisticLineSeries]:
    current = normalize_datetime(as_of)
    session_tuple = tuple(sessions)
    return (
        token_bucket_series(
            label="TPS last 1m",
            bucket_label="1s",
            sessions=session_tuple,
            window_end=current,
            bucket_count=60,
            bucket_seconds=1,
        ),
        token_bucket_series(
            label="TPM last 1h",
            bucket_label="1m",
            sessions=session_tuple,
            window_end=current,
            bucket_count=60,
            bucket_seconds=60,
        ),
    )


def token_bucket_series(
    label: str,
    bucket_label: str,
    sessions: Iterable[SessionUsage],
    window_end: datetime,
    bucket_count: int,
    bucket_seconds: int,
) -> StatisticLineSeries:
    end = normalize_datetime(window_end)
    start = end - timedelta(seconds=bucket_count * bucket_seconds)
    values = [0.0] * bucket_count
    for session in sessions:
        for event in session.usage_events:
            occurred_at = normalize_datetime(event.occurred_at)
            if occurred_at < start or occurred_at >= end:
                continue
            index = int((occurred_at - start).total_seconds() // bucket_seconds)
            if 0 <= index < bucket_count:
                values[index] += max(0, event.tokens.total_tokens)
    return StatisticLineSeries(
        label=label,
        bucket_label=bucket_label,
        values=tuple(values),
    )


def statistic_usage_rate_window(
    label: str,
    sessions: Iterable[SessionUsage],
    window_start: datetime,
    window_end: datetime,
) -> StatisticUsageRateWindow:
    start = normalize_datetime(window_start)
    end = normalize_datetime(window_end)
    tokens = 0
    requests = 0
    for session in sessions:
        for event in session.usage_events:
            occurred_at = normalize_datetime(event.occurred_at)
            if occurred_at < start or occurred_at >= end:
                continue
            requests += max(0, event.requests)
            tokens += max(0, event.tokens.total_tokens)

    return StatisticUsageRateWindow(
        label=label,
        window_start=start,
        window_end=end,
        tokens=tokens,
        requests=requests,
    )


def rounded_hour_start(value: datetime) -> datetime:
    return value.replace(minute=0, second=0, microsecond=0)


def previous_month_start(month_start: datetime) -> datetime:
    previous_day = month_start.date().replace(day=1) - timedelta(days=1)
    return datetime.combine(
        previous_day.replace(day=1),
        time.min,
        tzinfo=month_start.tzinfo,
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
