from __future__ import annotations

import csv
import io
import json
from dataclasses import dataclass
from datetime import date, datetime
from typing import Iterable

from .forecast import (
    ForecastWindow,
    LimitConfig,
    PredictionConfig,
    UsagePrediction,
    UsageForecast,
    forecast_to_dict,
    make_usage_forecast,
)
from .models import SessionUsage, TokenBreakdown, UsageDataset
from .pricing import CostEstimate, PricingConfig, estimate_session_cost
from .theme import ThemeConfig, themed_ansi_bar

TIME_GROUPS = {"date", "day", "week", "month", "hour"}


@dataclass(frozen=True)
class ReportRow:
    key: str
    sessions: int
    tokens: TokenBreakdown
    model: str | None = None
    cwd: str | None = None
    title: str | None = None
    updated_at: str | None = None
    estimated_cost: CostEstimate = CostEstimate(usd=None)


def filter_sessions(
    sessions: Iterable[SessionUsage],
    since: date | None = None,
    until: date | None = None,
    include_zero: bool = False,
) -> list[SessionUsage]:
    filtered: list[SessionUsage] = []
    for session in sessions:
        if not include_zero and session.tokens.total_tokens <= 0:
            continue
        day = session.activity_day
        if since and (day is None or day < since):
            continue
        if until and (day is None or day > until):
            continue
        filtered.append(session)
    return filtered


def make_report_rows(
    dataset: UsageDataset,
    group_by: str,
    top: int | None = None,
    pricing: PricingConfig | None = None,
) -> list[ReportRow]:
    group_by = canonical_group_by(group_by)
    sessions = list(dataset.sessions)
    if group_by == "session":
        rows = [
            ReportRow(
                key=session.session_id,
                sessions=1,
                tokens=session.tokens,
                model=session.model,
                cwd=session.cwd,
                title=session.title,
                updated_at=format_datetime(session.updated_at),
                estimated_cost=estimate_session_cost(session, pricing),
            )
            for session in sessions
        ]
        rows.sort(key=lambda row: row.tokens.total_tokens, reverse=True)
        return limit_rows(rows, top)

    grouped: dict[str, tuple[int, TokenBreakdown, float, int, int]] = {}
    for session in sessions:
        key = group_key(session, group_by)
        count, tokens, cost, priced_sessions, unpriced_sessions = grouped.get(
            key,
            (0, TokenBreakdown.empty(), 0.0, 0, 0),
        )
        estimate = estimate_session_cost(session, pricing)
        if estimate.usd is not None:
            cost += estimate.usd
        grouped[key] = (
            count + 1,
            tokens.add(session.tokens),
            cost,
            priced_sessions + estimate.priced_sessions,
            unpriced_sessions + estimate.unpriced_sessions,
        )

    rows = [
        ReportRow(
            key=key,
            sessions=count,
            tokens=tokens,
            estimated_cost=CostEstimate(
                usd=cost if priced_sessions else None,
                priced_sessions=priced_sessions,
                unpriced_sessions=unpriced_sessions,
            ),
        )
        for key, (
            count,
            tokens,
            cost,
            priced_sessions,
            unpriced_sessions,
        ) in grouped.items()
    ]
    if group_by in TIME_GROUPS:
        rows.sort(key=lambda row: row.key)
    else:
        rows.sort(key=lambda row: row.tokens.total_tokens, reverse=True)
    return limit_rows(rows, top)


def group_key(session: SessionUsage, group_by: str) -> str:
    group_by = canonical_group_by(group_by)
    if group_by == "date":
        return session.activity_day.isoformat() if session.activity_day else "(unknown)"
    if group_by == "week":
        day = session.activity_day
        if day is None:
            return "(unknown)"
        iso_week = day.isocalendar()
        return f"{iso_week.year}-W{iso_week.week:02d}"
    if group_by == "month":
        day = session.activity_day
        if day is None:
            return "(unknown)"
        return day.strftime("%Y-%m")
    if group_by == "hour":
        if session.activity_at is None:
            return "(unknown)"
        return session.activity_at.strftime("%Y-%m-%d %H:00")
    if group_by == "model":
        return session.model
    if group_by in {"cwd", "project"}:
        return session.cwd
    raise ValueError(f"unsupported group_by: {group_by}")


def render_report(
    dataset: UsageDataset,
    output_format: str,
    group_by: str,
    top: int | None = None,
    theme: ThemeConfig | None = None,
    color_enabled: bool = False,
    limits: LimitConfig | None = None,
    prediction: PredictionConfig = PredictionConfig(),
    as_of: datetime | None = None,
) -> str:
    group_by = canonical_group_by(group_by)
    rows = make_report_rows(dataset, group_by=group_by, top=top)
    forecast = (
        make_usage_forecast(dataset, limits, prediction=prediction, as_of=as_of)
        if limits and limits.has_limits
        else None
    )
    if output_format == "table":
        return render_table(rows, group_by, forecast=forecast)
    if output_format == "json":
        return render_json(rows, dataset, group_by, forecast=forecast)
    if output_format == "csv":
        return render_csv(rows, group_by, forecast=forecast)
    if output_format == "graph":
        return render_graph(
            rows,
            group_by,
            theme=theme,
            color_enabled=color_enabled,
            forecast=forecast,
        )
    raise ValueError(f"unsupported format: {output_format}")


def render_table(
    rows: list[ReportRow],
    group_by: str,
    forecast: UsageForecast | None = None,
) -> str:
    if group_by == "session":
        headers = [
            "session",
            "title",
            "model",
            "total",
            "input",
            "output",
            "cached",
            "cached_percent",
            "cache_miss",
            "reasoning",
            "updated",
        ]
        body = [
            [
                short(row.key),
                row.title or "",
                row.model or "",
                format_int(row.tokens.total_tokens),
                format_int(row.tokens.input_tokens),
                format_int(row.tokens.output_tokens),
                format_int(row.tokens.cached_input_tokens),
                format_percent(row.tokens.cached_input_percent),
                format_int(row.tokens.cache_miss_input_tokens),
                format_int(row.tokens.reasoning_output_tokens),
                row.updated_at or "",
            ]
            for row in rows
        ]
    else:
        headers = [
            group_by,
            "sessions",
            "total",
            "input",
            "output",
            "cached",
            "cached_percent",
            "cache_miss",
            "reasoning",
        ]
        if forecast and group_by == "week" and forecast.weekly.enabled:
            headers.extend(
                ["forecast_status", "forecast_remaining", "forecast_projected"]
            )
        body = [aggregate_table_row(row, group_by, forecast) for row in rows]

    output = table_from_rows(headers, body)
    if forecast:
        output += "\n" + render_forecast_table(forecast)
        output += "\n" + render_prediction_table(forecast.predictions)
    return output


def aggregate_table_row(
    row: ReportRow,
    group_by: str,
    forecast: UsageForecast | None,
) -> list[str]:
    cells = [
        row.key,
        format_int(row.sessions),
        format_int(row.tokens.total_tokens),
        format_int(row.tokens.input_tokens),
        format_int(row.tokens.output_tokens),
        format_int(row.tokens.cached_input_tokens),
        format_percent(row.tokens.cached_input_percent),
        format_int(row.tokens.cache_miss_input_tokens),
        format_int(row.tokens.reasoning_output_tokens),
    ]
    row_forecast = forecast_for_row(row, group_by, forecast)
    if forecast and group_by == "week" and forecast.weekly.enabled:
        cells.extend(
            [
                row_forecast.status if row_forecast else "",
                format_optional_int(row_forecast.remaining) if row_forecast else "",
                format_int(row_forecast.projected) if row_forecast else "",
            ]
        )
    return cells


def render_json(
    rows: list[ReportRow],
    dataset: UsageDataset,
    group_by: str,
    forecast: UsageForecast | None = None,
) -> str:
    payload = {
        "codex_home": str(dataset.codex_home),
        "loaded_at": dataset.loaded_at.isoformat(),
        "group_by": group_by,
        "sqlite_available": dataset.sqlite_available,
        "sqlite_error": dataset.sqlite_error,
        "totals": tokens_to_dict(dataset.totals),
        "rows": [row_to_dict(row, group_by, forecast) for row in rows],
    }
    if forecast:
        payload["forecast"] = forecast_to_dict(forecast)
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def render_csv(
    rows: list[ReportRow],
    group_by: str,
    forecast: UsageForecast | None = None,
) -> str:
    output = io.StringIO()
    if group_by == "session":
        fieldnames = [
            "session",
            "title",
            "model",
            "cwd",
            "total",
            "input",
            "output",
            "cached",
            "cached_percent",
            "cache_miss",
            "reasoning",
            "updated",
        ]
    else:
        fieldnames = [
            group_by,
            "sessions",
            "total",
            "input",
            "output",
            "cached",
            "cached_percent",
            "cache_miss",
            "reasoning",
        ]
    if forecast:
        fieldnames.extend(
            [
                "forecast_status",
                "forecast_limit",
                "forecast_remaining",
                "forecast_projected",
            ]
        )
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        data = row_to_csv_dict(row, group_by, forecast)
        writer.writerow(data)
    return output.getvalue()


def render_graph(
    rows: list[ReportRow],
    group_by: str,
    theme: ThemeConfig | None = None,
    color_enabled: bool = False,
    forecast: UsageForecast | None = None,
) -> str:
    if not rows:
        lines = [f"{group_by} token usage", "(no rows)"]
    else:
        label_width = min(max(len(row.key) for row in rows), 36)
        max_total = max(row.tokens.total_tokens for row in rows)
        bar_width = 40
        use_theme = bool(theme and theme.enabled and color_enabled)
        lines = [f"{group_by} token usage"]
        for row in rows:
            if max_total <= 0:
                filled = 0
            else:
                filled = max(1, round((row.tokens.total_tokens / max_total) * bar_width))
            label = row.key
            if len(label) > label_width:
                label = label[: label_width - 1] + "~"
            if use_theme and theme is not None:
                bar = themed_ansi_bar(row.tokens.total_tokens, max_total, bar_width, theme)
                lines.append(
                    f"{label:<{label_width}} | {bar} "
                    f"total {format_int(row.tokens.total_tokens)}  "
                    f"cached {format_int(row.tokens.cached_input_tokens)}  "
                    f"cached% {format_percent(row.tokens.cached_input_percent)}  "
                    f"miss {format_int(row.tokens.cache_miss_input_tokens)}"
                )
            else:
                bar = "#" * filled
                lines.append(
                    f"{label:<{label_width}} | {bar:<{bar_width}} "
                    f"total {format_int(row.tokens.total_tokens)}  "
                    f"cached {format_int(row.tokens.cached_input_tokens)}  "
                    f"cached% {format_percent(row.tokens.cached_input_percent)}  "
                    f"miss {format_int(row.tokens.cache_miss_input_tokens)}"
                )
    if forecast:
        lines.append("")
        lines.extend(render_forecast_lines(forecast))
        lines.append("")
        lines.extend(render_prediction_lines(forecast.predictions))
    return "\n".join(lines) + "\n"


def row_to_dict(
    row: ReportRow,
    group_by: str | None = None,
    forecast: UsageForecast | None = None,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "key": row.key,
        "sessions": row.sessions,
        "title": row.title,
        "model": row.model,
        "cwd": row.cwd,
        "updated_at": row.updated_at,
        "tokens": tokens_to_dict(row.tokens),
    }
    row_forecast = forecast_for_row(row, group_by, forecast)
    if row_forecast:
        payload["forecast"] = row_forecast_to_dict(row_forecast)
    return payload


def row_to_csv_dict(
    row: ReportRow,
    group_by: str,
    forecast: UsageForecast | None = None,
) -> dict[str, object]:
    if group_by == "session":
        payload: dict[str, object] = {
            "session": row.key,
            "title": row.title or "",
            "model": row.model or "",
            "cwd": row.cwd or "",
            "total": row.tokens.total_tokens,
            "input": row.tokens.input_tokens,
            "output": row.tokens.output_tokens,
            "cached": row.tokens.cached_input_tokens,
            "cached_percent": round_percent(row.tokens.cached_input_percent),
            "cache_miss": row.tokens.cache_miss_input_tokens,
            "reasoning": row.tokens.reasoning_output_tokens,
            "updated": row.updated_at or "",
        }
    else:
        payload = {
            group_by: row.key,
            "sessions": row.sessions,
            "total": row.tokens.total_tokens,
            "input": row.tokens.input_tokens,
            "output": row.tokens.output_tokens,
            "cached": row.tokens.cached_input_tokens,
            "cached_percent": round_percent(row.tokens.cached_input_percent),
            "cache_miss": row.tokens.cache_miss_input_tokens,
            "reasoning": row.tokens.reasoning_output_tokens,
        }
    if forecast:
        row_forecast = forecast_for_row(row, group_by, forecast)
        payload.update(
            {
                "forecast_status": row_forecast.status if row_forecast else "",
                "forecast_limit": row_forecast.limit if row_forecast else "",
                "forecast_remaining": (
                    row_forecast.remaining if row_forecast else ""
                ),
                "forecast_projected": row_forecast.projected if row_forecast else "",
            }
        )
    return payload


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


def tokens_to_dict(tokens: TokenBreakdown) -> dict[str, int | float]:
    return {
        "input": tokens.input_tokens,
        "output": tokens.output_tokens,
        "cached": tokens.cached_input_tokens,
        "cached_percent": round_percent(tokens.cached_input_percent),
        "cache_miss": tokens.cache_miss_input_tokens,
        "reasoning": tokens.reasoning_output_tokens,
        "total": tokens.total_tokens,
    }


def table_from_rows(headers: list[str], rows: list[list[str]]) -> str:
    all_rows = [headers, *rows]
    widths = [
        max(len(str(row[index])) for row in all_rows)
        for index in range(len(headers))
    ]
    lines = [format_table_line(headers, widths)]
    lines.append("  ".join("-" * width for width in widths))
    for row in rows:
        lines.append(format_table_line(row, widths))
    return "\n".join(lines) + "\n"


def format_table_line(row: list[str], widths: list[int]) -> str:
    cells = []
    for index, value in enumerate(row):
        text = str(value)
        if index >= 1 and is_formatted_number(text):
            cells.append(text.rjust(widths[index]))
        else:
            cells.append(text.ljust(widths[index]))
    return "  ".join(cells).rstrip()


def limit_rows(rows: list[ReportRow], top: int | None) -> list[ReportRow]:
    if top is None or top <= 0:
        return rows
    return rows[:top]


def format_datetime(value) -> str | None:
    if value is None:
        return None
    return value.isoformat()


def short(value: str, length: int = 12) -> str:
    if len(value) <= length:
        return value
    return value[:length]


def format_int(value: int) -> str:
    return f"{value:,}"


def format_optional_int(value: int | None) -> str:
    if value is None:
        return "-"
    return format_int(value)


def format_percent(value: float) -> str:
    return f"{value:.1f}%"


def round_percent(value: float) -> float:
    return round(value, 2)


def is_formatted_number(value: str) -> bool:
    normalized = value.removesuffix("%").replace(",", "")
    if not normalized:
        return False
    return normalized.replace(".", "", 1).isdigit()


def canonical_group_by(group_by: str) -> str:
    if group_by == "day":
        return "date"
    if group_by == "folder":
        return "project"
    return group_by
