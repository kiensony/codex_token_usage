from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timedelta, timezone
from typing import Iterable

from .models import SessionUsage, UsageDataset

FIVE_HOUR_WINDOW = timedelta(hours=5)
DAY_WINDOW = timedelta(days=1)
WEEK_WINDOW = timedelta(days=7)
MONTH_WINDOW = timedelta(days=30)
WEEK_WINDOW_HOURS = 24 * 7
MONTH_WINDOW_HOURS = 24 * 30
MIN_SAMPLE_HOURS = 1.0
PREDICTION_ALGORITHMS = ("recent_rate", "previous_period")


@dataclass(frozen=True)
class LimitConfig:
    five_hour_tokens: int | None = None
    weekly_tokens: int | None = None

    @property
    def has_limits(self) -> bool:
        return enabled_limit(self.five_hour_tokens) or enabled_limit(self.weekly_tokens)

    def with_overrides(
        self,
        five_hour_tokens: int | None = None,
        weekly_tokens: int | None = None,
    ) -> "LimitConfig":
        return LimitConfig(
            five_hour_tokens=(
                five_hour_tokens
                if five_hour_tokens is not None
                else self.five_hour_tokens
            ),
            weekly_tokens=(
                weekly_tokens if weekly_tokens is not None else self.weekly_tokens
            ),
        )


@dataclass(frozen=True)
class PredictionConfig:
    algorithm: str = "recent_rate"


@dataclass(frozen=True)
class ForecastWindow:
    name: str
    status: str
    limit: int | None
    used: int
    remaining: int | None
    projected: int
    rate_per_hour: float
    window_start: datetime
    window_end: datetime

    @property
    def enabled(self) -> bool:
        return enabled_limit(self.limit)


@dataclass(frozen=True)
class UsagePrediction:
    name: str
    projected: int
    rate_per_hour: float
    sample_start: datetime
    sample_end: datetime
    horizon_hours: float


@dataclass(frozen=True)
class UsageForecast:
    generated_at: datetime
    five_hour: ForecastWindow
    weekly: ForecastWindow
    predictions: tuple[UsagePrediction, ...] = ()

    @property
    def has_limits(self) -> bool:
        return self.five_hour.enabled or self.weekly.enabled

    @property
    def has_warnings(self) -> bool:
        return self.five_hour.status in WARNING_STATUSES or self.weekly.status in WARNING_STATUSES


WARNING_STATUSES = {"warning", "exceeded"}


def make_usage_forecast(
    dataset: UsageDataset,
    limits: LimitConfig,
    prediction: PredictionConfig = PredictionConfig(),
    as_of: datetime | None = None,
) -> UsageForecast:
    generated_at = normalize_datetime(as_of or dataset.loaded_at)
    sessions = tuple(dataset.sessions)
    five_hour_start = generated_at - FIVE_HOUR_WINDOW
    week_start = iso_week_start(generated_at)
    week_end = week_start + timedelta(days=7)

    five_hour = forecast_window(
        name="5h",
        sessions=sessions,
        limit=limits.five_hour_tokens,
        window_start=five_hour_start,
        window_end=generated_at,
        projection_end=generated_at + FIVE_HOUR_WINDOW,
        projection_hours=5.0,
        sample_from_first_event=True,
    )

    return UsageForecast(
        generated_at=generated_at,
        five_hour=five_hour,
        weekly=forecast_window(
            name="week",
            sessions=sessions,
            limit=limits.weekly_tokens,
            window_start=week_start,
            window_end=generated_at,
            projection_end=week_end,
            projection_hours=float(WEEK_WINDOW_HOURS),
            sample_from_first_event=False,
        ),
        predictions=(
            prediction_window(
                name="next_5_hours",
                sessions=sessions,
                as_of=generated_at,
                lookback=FIVE_HOUR_WINDOW,
                horizon_hours=5.0,
                algorithm=prediction.algorithm,
            ),
            prediction_window(
                name="next_day",
                sessions=sessions,
                as_of=generated_at,
                lookback=DAY_WINDOW,
                horizon_hours=24.0,
                algorithm=prediction.algorithm,
            ),
            prediction_window(
                name="next_week",
                sessions=sessions,
                as_of=generated_at,
                lookback=WEEK_WINDOW,
                horizon_hours=float(WEEK_WINDOW_HOURS),
                algorithm=prediction.algorithm,
            ),
            prediction_window(
                name="next_month",
                sessions=sessions,
                as_of=generated_at,
                lookback=MONTH_WINDOW,
                horizon_hours=float(MONTH_WINDOW_HOURS),
                algorithm=prediction.algorithm,
            ),
        ),
    )


def prediction_window(
    name: str,
    sessions: Iterable[SessionUsage],
    as_of: datetime,
    lookback: timedelta,
    horizon_hours: float,
    algorithm: str,
) -> UsagePrediction:
    sample_start = as_of - lookback
    sample_sessions = sessions_in_window(sessions, sample_start, as_of)
    used = sum(session.tokens.total_tokens for session in sample_sessions)
    lookback_hours = max(MIN_SAMPLE_HOURS, lookback.total_seconds() / 3600)

    if algorithm == "previous_period":
        rate_per_hour = used / lookback_hours
        projected = round(rate_per_hour * horizon_hours)
    else:
        elapsed_hours = elapsed_sample_hours(
            sample_sessions,
            sample_start,
            as_of,
            sample_from_first_event=True,
        )
        rate_per_hour = used / elapsed_hours if elapsed_hours > 0 else 0.0
        projected = round(rate_per_hour * horizon_hours)

    return UsagePrediction(
        name=name,
        projected=projected,
        rate_per_hour=rate_per_hour,
        sample_start=sample_start,
        sample_end=as_of,
        horizon_hours=horizon_hours,
    )


def forecast_window(
    name: str,
    sessions: Iterable[SessionUsage],
    limit: int | None,
    window_start: datetime,
    window_end: datetime,
    projection_end: datetime,
    projection_hours: float,
    sample_from_first_event: bool,
) -> ForecastWindow:
    window_sessions = sessions_in_window(sessions, window_start, window_end)
    used = sum(session.tokens.total_tokens for session in window_sessions)
    elapsed_hours = elapsed_sample_hours(
        window_sessions,
        window_start,
        window_end,
        sample_from_first_event=sample_from_first_event,
    )
    rate_per_hour = used / elapsed_hours if elapsed_hours > 0 else 0.0
    projected = round(rate_per_hour * projection_hours)
    remaining = None
    status = "disabled"
    if enabled_limit(limit):
        remaining = max(0, limit - used)
        if used >= limit:
            status = "exceeded"
        elif projected > limit:
            status = "warning"
        else:
            status = "ok"

    return ForecastWindow(
        name=name,
        status=status,
        limit=limit,
        used=used,
        remaining=remaining,
        projected=projected,
        rate_per_hour=rate_per_hour,
        window_start=window_start,
        window_end=projection_end,
    )


def sessions_in_window(
    sessions: Iterable[SessionUsage],
    window_start: datetime,
    window_end: datetime,
) -> list[SessionUsage]:
    selected: list[SessionUsage] = []
    for session in sessions:
        activity_at = session.activity_at
        if activity_at is None:
            continue
        activity_at = normalize_datetime(activity_at)
        if window_start <= activity_at <= window_end:
            selected.append(session)
    return selected


def elapsed_sample_hours(
    sessions: list[SessionUsage],
    window_start: datetime,
    window_end: datetime,
    sample_from_first_event: bool,
) -> float:
    if sample_from_first_event and sessions:
        first_activity = min(
            normalize_datetime(session.activity_at)
            for session in sessions
            if session.activity_at is not None
        )
        start = max(window_start, first_activity)
    else:
        start = window_start
    elapsed = (window_end - start).total_seconds() / 3600
    return max(MIN_SAMPLE_HOURS, elapsed)


def iso_week_start(value: datetime) -> datetime:
    value = normalize_datetime(value)
    start_day = value.date() - timedelta(days=value.isoweekday() - 1)
    return datetime.combine(start_day, time.min, tzinfo=value.tzinfo)


def normalize_datetime(value: datetime | None) -> datetime:
    if value is None:
        return datetime.now(timezone.utc)
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def enabled_limit(value: int | None) -> bool:
    return value is not None and value > 0


def forecast_to_dict(forecast: UsageForecast) -> dict[str, object]:
    return {
        "generated_at": forecast.generated_at.isoformat(),
        "five_hour": forecast_window_to_dict(forecast.five_hour),
        "weekly": forecast_window_to_dict(forecast.weekly),
        "predictions": [
            prediction_to_dict(prediction)
            for prediction in forecast.predictions
        ],
    }


def forecast_window_to_dict(window: ForecastWindow) -> dict[str, object]:
    return {
        "status": window.status,
        "limit": window.limit,
        "used": window.used,
        "remaining": window.remaining,
        "projected": window.projected,
        "rate_per_hour": round(window.rate_per_hour, 2),
        "window_start": window.window_start.isoformat(),
        "window_end": window.window_end.isoformat(),
    }


def prediction_to_dict(prediction: UsagePrediction) -> dict[str, object]:
    return {
        "name": prediction.name,
        "projected": prediction.projected,
        "rate_per_hour": round(prediction.rate_per_hour, 2),
        "sample_start": prediction.sample_start.isoformat(),
        "sample_end": prediction.sample_end.isoformat(),
        "horizon_hours": prediction.horizon_hours,
    }
