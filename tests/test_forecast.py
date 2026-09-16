from __future__ import annotations

import tempfile
import unittest
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

from codex_token_usage.forecast import (
    LimitConfig,
    PredictionConfig,
    make_usage_forecast,
)
from codex_token_usage.models import (
    SessionMetadata,
    SessionUsage,
    TokenBreakdown,
    UsageDataset,
    UsageEvent,
)


class ForecastTests(unittest.TestCase):
    def test_disabled_limits_do_not_warn(self) -> None:
        forecast = make_usage_forecast(
            dataset(
                session("s1", 100_000, "2026-06-02T11:00:00+00:00"),
                loaded_at=dt("2026-06-02T12:00:00+00:00"),
            ),
            LimitConfig(),
        )

        self.assertFalse(forecast.has_limits)
        self.assertEqual(forecast.five_hour.status, "disabled")
        self.assertEqual(forecast.weekly.status, "disabled")

    def test_five_hour_projection_warns_before_limit_is_exceeded(self) -> None:
        forecast = make_usage_forecast(
            dataset(
                session("s1", 80_000, "2026-06-02T11:00:00+00:00"),
                loaded_at=dt("2026-06-02T12:00:00+00:00"),
            ),
            LimitConfig(five_hour_tokens=100_000),
        )

        self.assertEqual(forecast.five_hour.used, 80_000)
        self.assertEqual(forecast.five_hour.remaining, 20_000)
        self.assertEqual(forecast.five_hour.projected, 400_000)
        self.assertEqual(forecast.five_hour.status, "warning")

    def test_five_hour_exceeded_status_takes_priority(self) -> None:
        forecast = make_usage_forecast(
            dataset(
                session("s1", 120_000, "2026-06-02T11:00:00+00:00"),
                loaded_at=dt("2026-06-02T12:00:00+00:00"),
            ),
            LimitConfig(five_hour_tokens=100_000),
        )

        self.assertEqual(forecast.five_hour.status, "exceeded")
        self.assertEqual(forecast.five_hour.remaining, 0)

    def test_five_hour_window_includes_start_and_excludes_future(self) -> None:
        forecast = make_usage_forecast(
            dataset(
                session("start", 10, "2026-06-02T07:00:00+00:00"),
                session("before", 100, "2026-06-02T06:59:59+00:00"),
                session("future", 1000, "2026-06-02T12:00:01+00:00"),
                loaded_at=dt("2026-06-02T12:00:00+00:00"),
            ),
            LimitConfig(five_hour_tokens=100),
        )

        self.assertEqual(forecast.five_hour.used, 10)
        self.assertEqual(forecast.five_hour.status, "ok")

    def test_weekly_projection_uses_current_iso_week(self) -> None:
        forecast = make_usage_forecast(
            dataset(
                session("s1", 50_000, "2026-06-29T12:00:00+00:00"),
                session("old", 1_000_000, "2026-06-28T23:59:59+00:00"),
                loaded_at=dt("2026-06-29T12:00:00+00:00"),
            ),
            LimitConfig(weekly_tokens=100_000),
        )

        self.assertEqual(forecast.weekly.used, 50_000)
        self.assertEqual(forecast.weekly.projected, 700_000)
        self.assertEqual(forecast.weekly.status, "warning")

    def test_empty_enabled_limits_are_ok(self) -> None:
        forecast = make_usage_forecast(
            dataset(loaded_at=dt("2026-06-02T12:00:00+00:00")),
            LimitConfig(five_hour_tokens=100, weekly_tokens=100),
        )

        self.assertEqual(forecast.five_hour.status, "ok")
        self.assertEqual(forecast.five_hour.projected, 0)
        self.assertEqual(forecast.weekly.status, "ok")
        self.assertEqual(forecast.weekly.projected, 0)

    def test_prediction_algorithms(self) -> None:
        sample = dataset(
            session("s1", 80_000, "2026-06-02T11:00:00+00:00"),
            loaded_at=dt("2026-06-02T12:00:00+00:00"),
        )

        recent = make_usage_forecast(
            sample,
            LimitConfig(),
            prediction=PredictionConfig(algorithm="recent_rate"),
        )
        previous = make_usage_forecast(
            sample,
            LimitConfig(),
            prediction=PredictionConfig(algorithm="previous_period"),
        )

        self.assertEqual(prediction(recent, "next_5_hours").projected, 400_000)
        self.assertEqual(prediction(recent, "next_day").projected, 1_920_000)
        self.assertEqual(prediction(previous, "next_5_hours").projected, 80_000)
        self.assertEqual(prediction(previous, "next_day").projected, 80_000)

    def test_resumed_session_forecasts_only_usage_inside_each_window(self) -> None:
        sample = dataset(
            event_session(
                "resumed",
                "2026-09-16T12:00:00+00:00",
                ("2026-09-01T11:00:00+00:00", 3_150_000_000),
                ("2026-09-16T07:00:00+00:00", 0),
                ("2026-09-16T08:00:00+00:00", 800_000_000),
                ("2026-09-16T11:00:00+00:00", 50_000_000),
            ),
            loaded_at=dt("2026-09-16T12:00:00+00:00"),
        )

        forecast = make_usage_forecast(
            sample,
            LimitConfig(five_hour_tokens=900_000_000, weekly_tokens=3_000_000_000),
        )

        self.assertEqual(sample.totals.input_tokens, 4_000_000_000)
        self.assertEqual(forecast.five_hour.used, 850_000_000)
        self.assertEqual(forecast.five_hour.remaining, 50_000_000)
        self.assertEqual(forecast.five_hour.rate_per_hour, 212_500_000)
        self.assertEqual(forecast.five_hour.projected, 1_062_500_000)
        self.assertEqual(forecast.five_hour.status, "warning")
        self.assertEqual(forecast.weekly.used, 850_000_000)
        self.assertEqual(forecast.weekly.projected, 2_380_000_000)
        self.assertEqual(forecast.weekly.status, "ok")
        self.assertEqual(prediction(forecast, "next_5_hours").projected, 1_062_500_000)
        self.assertEqual(prediction(forecast, "next_day").projected, 5_100_000_000)

        previous = make_usage_forecast(
            sample,
            LimitConfig(),
            prediction=PredictionConfig(algorithm="previous_period"),
        )
        for name in ("next_5_hours", "next_day", "next_week"):
            self.assertEqual(prediction(previous, name).projected, 850_000_000)
        self.assertEqual(prediction(previous, "next_month").projected, 4_000_000_000)

    def test_event_window_includes_boundaries_despite_future_session_activity(self) -> None:
        forecast = make_usage_forecast(
            dataset(
                event_session(
                    "spanning",
                    "2026-09-17T12:00:00+00:00",
                    ("2026-09-16T06:59:59+00:00", 100),
                    ("2026-09-16T07:00:00+00:00", 10),
                    ("2026-09-16T12:00:00+00:00", 20),
                    ("2026-09-16T12:00:01+00:00", 1_000),
                ),
                loaded_at=dt("2026-09-16T12:00:00+00:00"),
            ),
            LimitConfig(),
        )

        self.assertEqual(forecast.five_hour.used, 30)
        self.assertEqual(forecast.five_hour.rate_per_hour, 6)
        self.assertEqual(forecast.five_hour.projected, 30)

    def test_recent_metadata_without_usage_does_not_revive_old_tokens(self) -> None:
        forecast = make_usage_forecast(
            dataset(
                event_session(
                    "inactive",
                    "2026-09-16T11:00:00+00:00",
                    ("2026-09-01T11:00:00+00:00", 4_000_000_000),
                ),
                loaded_at=dt("2026-09-16T12:00:00+00:00"),
            ),
            LimitConfig(),
        )

        self.assertEqual(forecast.five_hour.used, 0)
        self.assertEqual(forecast.weekly.used, 0)
        self.assertEqual(prediction(forecast, "next_day").projected, 0)


def dataset(*sessions: SessionUsage, loaded_at: datetime) -> UsageDataset:
    with tempfile.TemporaryDirectory() as tmp:
        return UsageDataset(
            sessions=sessions,
            codex_home=Path(tmp),
            loaded_at=loaded_at,
            sqlite_available=False,
        )


def session(session_id: str, total: int, updated_at: str) -> SessionUsage:
    updated = dt(updated_at)
    return SessionUsage(
        session_id=session_id,
        path=Path("/tmp") / f"{session_id}.jsonl",
        tokens=TokenBreakdown(total_tokens=total),
        metadata=SessionMetadata(
            session_id=session_id,
            created_at=updated,
            updated_at=updated,
        ),
        has_token_event=True,
    )


def dt(value: str) -> datetime:
    return datetime.fromisoformat(value).astimezone(timezone.utc)


def event_session(
    session_id: str, updated_at: str, *events: tuple[str, int]
) -> SessionUsage:
    total = sum(tokens for _, tokens in events)
    return replace(
        session(session_id, total, updated_at),
        tokens=TokenBreakdown(input_tokens=total, total_tokens=total),
        usage_events=tuple(
            UsageEvent(
                occurred_at=dt(occurred_at),
                tokens=TokenBreakdown(input_tokens=tokens, total_tokens=tokens),
            )
            for occurred_at, tokens in events
        ),
    )


def prediction(forecast, name: str):
    for item in forecast.predictions:
        if item.name == name:
            return item
    raise AssertionError(f"missing prediction {name}")


if __name__ == "__main__":
    unittest.main()
