from __future__ import annotations

import csv
import io
import json
from datetime import datetime

from ..forecast import (
    LimitConfig,
    PredictionConfig,
    UsageForecast,
    forecast_to_dict,
    make_usage_forecast,
)
from ..models import UsageDataset
from ..theme import ThemeConfig, themed_ansi_bar
from .forecast_display import (
    forecast_for_row,
    render_forecast_lines,
    render_forecast_table,
    render_prediction_lines,
    render_prediction_table,
    row_forecast_to_dict,
)
from .formatting import (
    format_int,
    format_optional_int,
    format_percent,
    round_percent,
    short,
    table_from_rows,
    tokens_to_dict,
    canonical_group_by,
)
from .models import ReportRow
from .rows import make_report_rows

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
