from __future__ import annotations

from datetime import datetime

from ..forecast import ForecastWindow, UsageForecast, UsagePrediction
from .formatting import format_int, format_optional_int, table_from_rows
from .models import ReportRow

def render_forecast_table(forecast: UsageForecast) -> str:
    rows = forecast_rows(forecast)
    body = [
        [
            row.name,
            row.status,
            format_int(row.used),
            format_optional_int(row.limit),
            format_optional_int(row.remaining),
            format_int(row.projected),
            f"{row.rate_per_hour:.1f}",
        ]
        for row in rows
    ]
    return "forecast warnings\n" + table_from_rows(
        ["window", "status", "used", "limit", "remaining", "projected", "rate/hr"],
        body,
    )
def render_forecast_lines(forecast: UsageForecast) -> list[str]:
    lines = ["forecast warnings"]
    for row in forecast_rows(forecast):
        lines.append(
            f"{row.name:<6} {row.status:<8} "
            f"used {format_int(row.used)} / {format_optional_int(row.limit)}  "
            f"remaining {format_optional_int(row.remaining)}  "
            f"projected {format_int(row.projected)}"
        )
    return lines
def render_prediction_table(predictions: tuple[UsagePrediction, ...]) -> str:
    body = [
        [
            prediction_label(prediction.name),
            format_int(prediction.projected),
            f"{prediction.rate_per_hour:.1f}",
        ]
        for prediction in predictions
    ]
    return "usage predictions\n" + table_from_rows(
        ["period", "projected", "rate/hr"],
        body,
    )
def render_prediction_lines(predictions: tuple[UsagePrediction, ...]) -> list[str]:
    lines = ["usage predictions"]
    for prediction in predictions:
        lines.append(
            f"{prediction_label(prediction.name):<12} "
            f"projected {format_int(prediction.projected)}  "
            f"rate/hr {prediction.rate_per_hour:.1f}"
        )
    return lines
def forecast_rows(forecast: UsageForecast) -> list[ForecastWindow]:
    return [row for row in (forecast.five_hour, forecast.weekly) if row.enabled]
def prediction_label(name: str) -> str:
    labels = {
        "next_5_hours": "next 5h",
        "next_day": "next day",
        "next_week": "next week",
        "next_month": "next month",
    }
    return labels.get(name, name.replace("_", " "))
def forecast_for_row(
    row: ReportRow,
    group_by: str | None,
    forecast: UsageForecast | None,
) -> ForecastWindow | None:
    if forecast is None or group_by != "week" or not forecast.weekly.enabled:
        return None
    if row.key != week_key(forecast.generated_at):
        return None
    return forecast.weekly
def row_forecast_to_dict(window: ForecastWindow) -> dict[str, object]:
    return {
        "status": window.status,
        "limit": window.limit,
        "remaining": window.remaining,
        "projected": window.projected,
    }
def week_key(value: datetime) -> str:
    iso_week = value.date().isocalendar()
    return f"{iso_week.year}-W{iso_week.week:02d}"
