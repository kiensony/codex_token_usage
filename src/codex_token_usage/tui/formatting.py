from __future__ import annotations

FLAG_PICKER_COLUMNS = 4
FLAG_PICKER_TOP = 5
FLAG_PICKER_PREVIEW_HEIGHT = 5
APPEARANCE_PREVIEW_BLOCK_HEIGHT = 5
FORCE_SHUTDOWN_KEYS = (27, ord("q"), ord("Q"))

def usage_bar(value: int, max_value: int, width: int) -> str:
    if width <= 0:
        return ""
    if max_value <= 0 or value <= 0:
        return "." * width
    filled = max(1, round((value / max_value) * width))
    filled = min(width, filled)
    return "#" * filled + "." * (width - filled)

def settings_columns(width: int) -> tuple[int, int, int, int, int]:
    rate_width = 12
    source_width = 10
    model_width = max(12, min(42, width - (2 + rate_width * 3 + source_width + 5)))
    input_x = 2 + model_width + 2
    cached_x = input_x + rate_width
    output_x = cached_x + rate_width
    source_x = output_x + rate_width
    return model_width, input_x, cached_x, output_x, source_x


def on_off(value: bool) -> str:
    return "on" if value else "off"


def visible_start(selected_index: int, rows_available: int, total_rows: int) -> int:
    if rows_available <= 0 or total_rows <= rows_available:
        return 0
    selected_index = min(max(0, selected_index), total_rows - 1)
    return min(max(0, selected_index - rows_available + 1), total_rows - rows_available)


def truncate(value: str, width: int) -> str:
    if width <= 0:
        return ""
    if len(value) <= width:
        return value
    if width == 1:
        return "~"
    return value[: width - 1] + "~"
