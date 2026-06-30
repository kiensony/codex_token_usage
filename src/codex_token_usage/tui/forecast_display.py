from __future__ import annotations

from datetime import date

from ..forecast import ForecastWindow, UsageForecast
from ..report import format_int

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
