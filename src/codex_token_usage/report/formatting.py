from __future__ import annotations

from ..models import TokenBreakdown
from .models import ReportRow

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
