from __future__ import annotations

import curses
from dataclasses import replace

from ..forecast import ForecastWindow, make_usage_forecast
from ..models import SessionUsage
from ..pricing import estimate_session_cost, estimate_sessions_cost, format_cost
from ..report import format_int, format_percent
from ..theme import themed_bar_segments
from .forecast_display import (
    forecast_key_values,
    prediction_key_values,
    usage_row_forecast_status,
)
from .formatting import truncate, visible_start
from .formatting import format_token_count
from .settings_model import prediction_algorithm_label
from .state import TAB_VIEWS, VIEW_LABELS
from .usage_rates import (
    current_usage_rate_rows,
    format_rate,
    statistic_line_series,
    statistic_usage_rate_windows,
)
from .view_overlays import ViewOverlayMixin


def downsample_series(values: tuple[float, ...], width: int) -> tuple[float, ...]:
    if width <= 0:
        return ()
    if len(values) <= width:
        return values
    sampled: list[float] = []
    count = len(values)
    for index in range(width):
        start = (index * count) // width
        end = max(start + 1, ((index + 1) * count) // width)
        sampled.append(max(values[start:end]))
    return tuple(sampled)


BRAILLE_DOTS = (
    (0x01, 0x02, 0x04, 0x40),
    (0x08, 0x10, 0x20, 0x80),
)


def braille_dot(mask: int) -> str:
    if mask == 0:
        return " "
    return chr(0x2800 + mask)


def draw_braille_dot(canvas: list[list[int]], x: int, y: int) -> None:
    if y < 0 or y >= len(canvas) * 4:
        return
    if not canvas or x < 0 or x >= len(canvas[0]) * 2:
        return
    cell_x = x // 2
    cell_y = y // 4
    canvas[cell_y][cell_x] |= BRAILLE_DOTS[x % 2][y % 4]


def draw_braille_segment(
    canvas: list[list[int]],
    start_x: int,
    start_y: int,
    end_x: int,
    end_y: int,
) -> None:
    x = start_x
    y = start_y
    dx = abs(end_x - start_x)
    dy = -abs(end_y - start_y)
    step_x = 1 if start_x < end_x else -1
    step_y = 1 if start_y < end_y else -1
    error = dx + dy
    while True:
        draw_braille_dot(canvas, x, y)
        if x == end_x and y == end_y:
            break
        doubled_error = 2 * error
        if doubled_error >= dy:
            error += dy
            x += step_x
        if doubled_error <= dx:
            error += dx
            y += step_y


def line_chart_rows(
    values: tuple[float, ...],
    width: int,
    height: int,
) -> list[str]:
    if width <= 0 or height <= 0:
        return []
    label_width = 9
    plot_width = width - label_width - 3
    if plot_width <= 0:
        return []
    sampled = downsample_series(values, plot_width * 2)
    if not sampled:
        return []
    max_value = max(sampled)
    mid_value = max_value / 2
    dot_width = plot_width * 2
    dot_height = height * 4
    points: list[tuple[int, int]] = []
    for index, value in enumerate(sampled):
        if len(sampled) == 1:
            x = 0
        else:
            x = round(index * (dot_width - 1) / (len(sampled) - 1))
        if max_value <= 0:
            y = dot_height - 1
        else:
            ratio = min(max(value / max_value, 0.0), 1.0)
            y = dot_height - 1 - round(ratio * (dot_height - 1))
        points.append((x, y))
    canvas = [[0 for _ in range(plot_width)] for _ in range(height)]
    previous_point: tuple[int, int] | None = None
    for point in points:
        if previous_point is None:
            draw_braille_dot(canvas, point[0], point[1])
        else:
            draw_braille_segment(
                canvas,
                previous_point[0],
                previous_point[1],
                point[0],
                point[1],
            )
        previous_point = point
    labeled_rows: list[str] = []
    labeled_rows.append(
        f"{format_rate(max_value):>{label_width}} ┌{'─' * plot_width}┐"
    )
    for row_index, row in enumerate(canvas):
        if row_index == height // 2:
            label = format_rate(mid_value)
        else:
            label = ""
        plot = "".join(braille_dot(cell) for cell in row)
        labeled_rows.append(f"{label:>{label_width}} │{plot}│")
    labeled_rows.append(f"{'0':>{label_width}} └{'─' * plot_width}┘")
    if plot_width >= 10:
        axis_label = f"{'older':<{plot_width // 2}}{'now':>{plot_width - (plot_width // 2)}}"
    else:
        axis_label = "older now"[:plot_width]
    labeled_rows.append(f"{'':>{label_width}}  {axis_label}")
    return labeled_rows


class ViewRendererMixin(ViewOverlayMixin):
    def render(self) -> None:
        self.stdscr.erase()
        height, width = self.stdscr.getmaxyx()
        self.render_header(width)
        if self.state.view == "overview":
            self.render_overview(height, width)
        elif self.state.view == "statistic":
            self.render_statistic(height, width)
        elif self.state.view == "daily":
            self.render_daily(height, width)
        elif self.state.view == "weekly":
            self.render_weekly(height, width)
        elif self.state.view == "monthly":
            self.render_monthly(height, width)
        elif self.state.view == "hourly":
            self.render_hourly(height, width)
        elif self.state.view == "models":
            self.render_models(height, width)
        elif self.state.view == "projects":
            self.render_projects(height, width)
        elif self.state.view == "sessions":
            self.render_sessions(height, width)
        elif self.state.view == "details":
            self.render_details(height, width)
        if self.state.help_open:
            self.render_help(height, width)
        if self.state.about_open:
            self.render_about(height, width)
        self.render_footer(height, width)
        self.stdscr.refresh()
    def render_header(self, width: int) -> None:
        self.render_themed_text(0, 0, "Codex Token Usage", curses.A_BOLD)
        self.render_tabs(1, width)
        filters = []
        if self.state.filter_text:
            filters.append(f"filter={self.state.filter_text}")
        filters.append(f"range={self.state.range_label()}")
        filters.append(
            f"sort={self.state.sort_field} {self.state.sort_direction_label}"
        )
        if self.state.view == "projects":
            filters.append(f"mode={self.state.project_display_mode}")
        self.render_themed_text(
            2,
            0,
            "  ".join(filters)[: max(0, width - 1)],
            curses.A_DIM,
            start_index=2,
        )
        self.render_accent_line(3, width)
    def render_tabs(self, y: int, width: int) -> None:
        x = 0
        for index, view in enumerate(TAB_VIEWS):
            label = f" {VIEW_LABELS[view]} "
            attr = (
                self.theme_attr(index, curses.A_REVERSE | curses.A_BOLD)
                if self.state.tab_view == view
                else self.theme_attr(index)
            )
            if x + len(label) >= width:
                break
            self.safe_addstr(y, x, label, attr)
            x += len(label) + 1
    def render_accent_line(self, y: int, width: int) -> None:
        if not self.options.theme.show_accent_line or not self.theme_pairs or width <= 1:
            return
        segments = themed_bar_segments(
            1,
            1,
            width - 1,
            self.options.theme,
            fill_char="-",
            empty_char="-",
        )
        self.render_bar_segments(y, 0, segments)
    def render_overview(self, height: int, width: int) -> None:
        totals = self.state.filtered_totals()
        rows = [
            ("Sessions", str(len(self.state.visible_sessions()))),
            ("Total tokens", format_int(totals.total_tokens)),
            ("Input incl. cache", format_int(totals.input_tokens)),
            ("Output tokens", format_int(totals.output_tokens)),
            ("Cached input", format_int(totals.cached_input_tokens)),
            ("Uncached input", format_int(totals.cache_miss_input_tokens)),
            ("Reasoning output", format_int(totals.reasoning_output_tokens)),
            ("Codex home", str(self.state.dataset.codex_home)),
            ("Loaded", self.state.dataset.loaded_at.isoformat()),
            ("SQLite metadata", "yes" if self.state.dataset.sqlite_available else "no"),
        ]
        if self.options.display.show_cached_percent:
            rows.insert(5, ("Cached input %", format_percent(totals.cached_input_percent)))
        if self.options.display.show_estimated_cost:
            estimate = estimate_sessions_cost(
                self.state.visible_sessions(),
                self.state.pricing,
            )
            rows.insert(7, ("Estimated API cost", format_cost(estimate)))
            if estimate.unpriced_sessions:
                rows.insert(
                    8,
                    ("Unpriced sessions", format_int(estimate.unpriced_sessions)),
                )
        if self.state.dataset.sqlite_error:
            rows.append(("SQLite note", self.state.dataset.sqlite_error))
        forecast = make_usage_forecast(
            replace(self.state.dataset, sessions=tuple(self.state.visible_sessions())),
            self.options.limits,
            prediction=self.options.prediction,
        )
        rows.append(
            (
                "Prediction algorithm",
                prediction_algorithm_label(self.options.prediction.algorithm),
            )
        )
        rows.extend(prediction_key_values(forecast))
        if forecast.has_limits:
            rows.extend(forecast_key_values(forecast))
        rows.extend(
            current_usage_rate_rows(self.state.visible_sessions(), forecast.generated_at)
        )
        self.render_key_values(4, rows, width, height)
    def render_statistic(self, height: int, width: int) -> None:
        windows = statistic_usage_rate_windows(
            self.state.visible_sessions(),
            self.state.dataset.loaded_at,
        )
        if self.state.statistic_display_mode == "line":
            self.render_statistic_line_chart(height, width)
            return
        header = (
            f"{'window':<12} {'rps':>8} {'rpm':>8} {'rph':>8} "
            f"{'tps':>12} {'tpm':>12} {'tph':>12} {'tpr':>12}"
        )
        self.render_themed_text(4, 0, header[: max(0, width - 1)], curses.A_BOLD)
        for offset, row in enumerate(windows[: max(0, height - 7)], start=5):
            line = (
                f"{row.label:<12} "
                f"{format_rate(row.rps):>8} "
                f"{format_rate(row.rpm):>8} "
                f"{format_rate(row.rph):>8} "
                f"{format_rate(row.tps):>12} "
                f"{format_rate(row.tpm):>12} "
                f"{format_rate(row.tph):>12} "
                f"{format_rate(row.tpr):>12}"
            )
            self.safe_addstr(offset, 0, line[: max(0, width - 1)])

    def render_statistic_line_chart(self, height: int, width: int) -> None:
        last_y = height - 3
        if last_y < 4 or width <= 1:
            return
        series_rows = statistic_line_series(
            self.state.visible_sessions(),
            self.state.dataset.loaded_at,
        )
        y = 4
        self.render_themed_text(
            y,
            0,
            "Statistic line chart"[: max(0, width - 1)],
            curses.A_BOLD,
        )
        y += 1
        available = max(0, last_y - y + 1)
        chart_height = max(1, min(6, (available - 9) // max(1, len(series_rows))))
        chart_width = max(1, width - 1)
        for index, series in enumerate(series_rows):
            if y > last_y:
                break
            max_value = max(series.values, default=0.0)
            latest = series.values[-1] if series.values else 0.0
            title = (
                f"{series.label}  max {format_rate(max_value)}  "
                f"latest {format_rate(latest)}  bucket {series.bucket_label}"
            )
            self.render_themed_text(y, 0, title[: max(0, width - 1)], curses.A_BOLD)
            y += 1
            for row in line_chart_rows(series.values, chart_width, chart_height):
                if y > last_y:
                    break
                self.safe_addstr(y, 0, row[: max(0, width - 1)])
                y += 1
            if index < len(series_rows) - 1:
                y += 1
    def render_daily(self, height: int, width: int) -> None:
        rows = self.state.daily_rows()
        self.render_usage_rows("date", rows, height, width)
    def render_weekly(self, height: int, width: int) -> None:
        rows = self.state.weekly_rows()
        forecast = make_usage_forecast(
            replace(self.state.dataset, sessions=tuple(self.state.visible_sessions())),
            self.options.limits,
            prediction=self.options.prediction,
        )
        self.render_usage_rows("week", rows, height, width, forecast.weekly)
    def render_monthly(self, height: int, width: int) -> None:
        rows = self.state.monthly_rows()
        self.render_usage_rows("month", rows, height, width)
    def render_hourly(self, height: int, width: int) -> None:
        rows = self.state.hourly_rows()
        self.render_usage_rows("hour", rows, height, width)
    def render_models(self, height: int, width: int) -> None:
        rows = self.state.model_rows()
        max_label = max((len(row.key) for row in rows), default=len("model"))
        label_width = min(max(16, max_label), max(16, width // 3))
        self.render_usage_rows("model", rows, height, width, label_width=label_width)
    def render_projects(self, height: int, width: int) -> None:
        rows = self.state.project_model_rows()
        token_rows: list = []
        for row in rows:
            token_rows.append(row.project)
            token_rows.extend(row.models)
        token_widths = self._aggregate_token_widths(token_rows)
        max_label = max(
            (len(row.project.key) for row in rows),
            default=len("project"),
        )
        label_width = min(max(16, max_label), max(16, width // 3))
        max_total = max(
            (row.project.tokens.total_tokens for row in rows),
            default=0,
        )
        selected_index = min(self.state.selected_project_index, len(rows) - 1)
        header = (
            f" {'project':<{label_width}} {'usage':<14} "
            f"{self.aggregate_header_fields(token_widths)}"
        )
        self.render_themed_text(4, 0, header[: max(0, width - 1)], curses.A_BOLD)
        rows_available = max(0, height - 7)
        y = 5
        rendered = 0
        show_models = self.state.project_display_mode == "models"
        for project_index, row in enumerate(rows):
            if rendered >= rows_available:
                break
            selected = project_index == selected_index
            attr = self.theme_attr(project_index, curses.A_REVERSE) if selected else 0
            self.render_usage_row(
                y,
                "project",
                row.project,
                max_total,
                width,
                label_width,
                marker=">" if selected else " ",
                attr=attr,
                token_widths=token_widths,
                bar_width=14,
            )
            y += 1
            rendered += 1
            if not show_models:
                continue
            for model_row in row.models:
                if rendered >= rows_available:
                    break
                self.render_usage_row(
                    y,
                    "project",
                    model_row,
                    max_total,
                    width,
                    label_width,
                    row_key=f"  {model_row.key}",
                    marker=" ",
                    token_widths=token_widths,
                    bar_width=14,
                )
                y += 1
                rendered += 1
    @staticmethod
    def _format_token_count(
        compact: bool,
        value: int,
        width: int,
    ) -> str:
        if compact:
            return format_token_count(value, width)
        return format_int(value)

    def _aggregate_token_widths(self, rows) -> dict[str, int]:
        if self.options.display.compact_token_counts:
            return {
                "sessions": 8,
                "total": 12,
                "cached": 12,
                "cached_percent": 8,
                "estimated_cost": 10,
                "miss": 12,
                "reason": 10,
            }
        aggregate_rows = tuple(rows)
        return {
            "sessions": max(
                (len("sessions"), *(len(format_int(row.sessions)) for row in aggregate_rows)),
            ),
            "total": max(
                (
                    len("total"),
                    *(len(format_int(row.tokens.total_tokens)) for row in aggregate_rows),
                ),
            ),
            "cached": max(
                (
                    len("cached"),
                    *(len(format_int(row.tokens.cached_input_tokens)) for row in aggregate_rows),
                ),
            ),
            "cached_percent": 8,
            "estimated_cost": 10,
            "miss": max(
                (
                    len("miss"),
                    *(
                        len(format_int(row.tokens.cache_miss_input_tokens))
                        for row in aggregate_rows
                    ),
                ),
            ),
            "reason": max(
                (
                    len("reason"),
                    *(
                        len(format_int(row.tokens.reasoning_output_tokens))
                        for row in aggregate_rows
                    ),
                ),
            ),
        }

    def _session_token_widths(self, sessions) -> dict[str, int]:
        if self.options.display.compact_token_counts:
            return {
                "total": 10,
                "cached": 10,
                "cached_percent": 8,
                "estimated_cost": 10,
                "reasoning_level": 8,
                "miss": 10,
                "reason": 8,
            }
        session_rows = tuple(sessions)
        return {
            "total": max(
                (
                    len("total"),
                    *(len(format_int(session.tokens.total_tokens)) for session in session_rows),
                ),
            ),
            "cached": max(
                (
                    len("cached"),
                    *(
                        len(format_int(session.tokens.cached_input_tokens))
                        for session in session_rows
                    ),
                ),
            ),
            "cached_percent": 8,
            "estimated_cost": 10,
            "reasoning_level": 8,
            "miss": max(
                (
                    len("miss"),
                    *(
                        len(format_int(session.tokens.cache_miss_input_tokens))
                        for session in session_rows
                    ),
                ),
            ),
            "reason": max(
                (
                    len("reason"),
                    *(
                        len(format_int(session.tokens.reasoning_output_tokens))
                        for session in session_rows
                    ),
                ),
            ),
        }

    def aggregate_header_fields(self, token_widths: dict[str, int] | None = None) -> str:
        fields: list[tuple[str, int]] = [
            ("sessions", token_widths["sessions"] if token_widths else 8),
            ("total", token_widths["total"] if token_widths else 12),
        ]
        if self.options.display.show_cached_tokens:
            fields.append(("cached", token_widths["cached"] if token_widths else 12))
        if self.options.display.show_cached_percent:
            fields.append(("cached%", token_widths["cached_percent"] if token_widths else 8))
        if self.options.display.show_estimated_cost:
            fields.append(("est $", token_widths["estimated_cost"] if token_widths else 10))
        if self.options.display.show_cache_miss:
            fields.append(("miss", token_widths["miss"] if token_widths else 12))
        if self.options.display.show_reasoning_tokens:
            fields.append(("reason", token_widths["reason"] if token_widths else 10))
        return self.right_aligned_fields(fields)

    def aggregate_value_fields(
        self,
        row,
        token_widths: dict[str, int] | None = None,
    ) -> str:
        total_width = 12 if token_widths is None else token_widths["total"]
        cached_width = 12 if token_widths is None else token_widths["cached"]
        miss_width = 12 if token_widths is None else token_widths["miss"]
        reason_width = 10 if token_widths is None else token_widths["reason"]
        fields: list[tuple[str, int]] = [
            (format_int(row.sessions), token_widths["sessions"] if token_widths else 8),
            (
                self._format_token_count(
                    self.options.display.compact_token_counts,
                    row.tokens.total_tokens,
                    total_width,
                ),
                total_width,
            ),
        ]
        if self.options.display.show_cached_tokens:
            fields.append(
                (
                    self._format_token_count(
                        self.options.display.compact_token_counts,
                        row.tokens.cached_input_tokens,
                        cached_width,
                    ),
                    cached_width,
                ),
            )
        if self.options.display.show_cached_percent:
            fields.append((format_percent(row.tokens.cached_input_percent), 8))
        if self.options.display.show_estimated_cost:
            fields.append((format_cost(row.estimated_cost), 10))
        if self.options.display.show_cache_miss:
            fields.append(
                (
                    self._format_token_count(
                        self.options.display.compact_token_counts,
                        row.tokens.cache_miss_input_tokens,
                        miss_width,
                    ),
                    miss_width,
                ),
            )
        if self.options.display.show_reasoning_tokens:
            fields.append(
                (
                    self._format_token_count(
                        self.options.display.compact_token_counts,
                        row.tokens.reasoning_output_tokens,
                        reason_width,
                    ),
                    reason_width,
                ),
            )
        return self.right_aligned_fields(fields)

    def session_header_fields(self, token_widths: dict[str, int] | None = None) -> str:
        fields: list[tuple[str, int]] = [
            ("total", token_widths["total"] if token_widths else 10),
        ]
        if self.options.display.show_cached_tokens:
            fields.append(("cached", token_widths["cached"] if token_widths else 10))
        if self.options.display.show_cached_percent:
            fields.append(("cached%", token_widths["cached_percent"] if token_widths else 8))
        if self.options.display.show_estimated_cost:
            fields.append(("est $", token_widths["estimated_cost"] if token_widths else 10))
        if self.options.display.show_reasoning_level:
            fields.append(("effort", 8))
        if self.options.display.show_cache_miss:
            fields.append(("miss", token_widths["miss"] if token_widths else 10))
        if self.options.display.show_reasoning_tokens:
            fields.append(("reason", token_widths["reason"] if token_widths else 8))
        return self.right_aligned_fields(fields)

    def session_value_fields(
        self,
        session: SessionUsage,
        token_widths: dict[str, int] | None = None,
    ) -> str:
        total_width = 10 if token_widths is None else token_widths["total"]
        cached_width = 10 if token_widths is None else token_widths["cached"]
        miss_width = 10 if token_widths is None else token_widths["miss"]
        reason_width = 8 if token_widths is None else token_widths["reason"]
        fields: list[tuple[str, int]] = [
            (
                self._format_token_count(
                    self.options.display.compact_token_counts,
                    session.tokens.total_tokens,
                    total_width,
                ),
                total_width,
            ),
        ]
        if self.options.display.show_cached_tokens:
            fields.append(
                (
                    self._format_token_count(
                        self.options.display.compact_token_counts,
                        session.tokens.cached_input_tokens,
                        cached_width,
                    ),
                    cached_width,
                ),
            )
        if self.options.display.show_cached_percent:
            fields.append((format_percent(session.tokens.cached_input_percent), 8))
        if self.options.display.show_estimated_cost:
            fields.append(
                (format_cost(estimate_session_cost(session, self.state.pricing)), 10)
            )
        if self.options.display.show_reasoning_level:
            fields.append((truncate(session.reasoning_level, 8), 8))
        if self.options.display.show_cache_miss:
            fields.append(
                (
                    self._format_token_count(
                        self.options.display.compact_token_counts,
                        session.tokens.cache_miss_input_tokens,
                        miss_width,
                    ),
                    miss_width,
                ),
            )
        if self.options.display.show_reasoning_tokens:
            fields.append(
                (
                    self._format_token_count(
                        self.options.display.compact_token_counts,
                        session.tokens.reasoning_output_tokens,
                        reason_width,
                    ),
                    reason_width,
                ),
            )
        return self.right_aligned_fields(fields)

    @staticmethod
    def right_aligned_fields(fields: list[tuple[str, int]]) -> str:
        return " ".join(f"{value:>{width}}" for value, width in fields)

    @staticmethod
    def session_model_width(width: int, configured_width: int | None = None) -> int:
        if configured_width is not None:
            return configured_width
        if width >= 150:
            return 24
        if width >= 120:
            return 22
        if width >= 100:
            return 18
        return 14
    def render_usage_rows(
        self,
        label: str,
        rows,
        height: int,
        width: int,
        forecast_window: ForecastWindow | None = None,
        label_width: int = 16,
    ) -> None:
        rows = tuple(rows)
        token_widths = self._aggregate_token_widths(rows)
        max_total = max((row.tokens.total_tokens for row in rows), default=0)
        header = (
            f"{label:<{label_width}} {'usage':<14} "
            f"{self.aggregate_header_fields(token_widths)}"
        )
        if forecast_window and forecast_window.enabled and label == "week":
            header += " forecast"
        self.render_themed_text(4, 0, header[: max(0, width - 1)], curses.A_BOLD)
        for offset, row in enumerate(rows[: max(0, height - 7)], start=5):
            self.render_usage_row(
                offset,
                label,
                row,
                max_total,
                width,
                label_width,
                forecast_window,
                token_widths=token_widths,
                bar_width=14,
            )

    def render_usage_row(
        self,
        y: int,
        label: str,
        row,
        max_total: int,
        width: int,
        label_width: int,
        forecast_window: ForecastWindow | None = None,
        row_key: str | None = None,
        marker: str | None = None,
        token_widths: dict[str, int] | None = None,
        bar_width: int = 14,
        attr: int = 0,
    ) -> None:
        key = row.key if row_key is None else row_key
        display_key = truncate(key, label_width)
        if marker is None:
            prefix = f"{display_key:<{label_width}} "
        else:
            prefix = f"{marker}{display_key:<{label_width}} "
        if label == "session":
            suffix = " " + self.session_value_fields(row, token_widths)
        else:
            suffix = " " + self.aggregate_value_fields(row, token_widths)
        status = usage_row_forecast_status(label, row.key, forecast_window)
        if status:
            suffix += f" {status}"
        self.safe_addstr(y, 0, prefix, attr)
        self.render_themed_bar(
            y,
            len(prefix),
            row.tokens.total_tokens,
            max_total,
            bar_width,
            attr,
        )
        self.safe_addstr(
            y,
            len(prefix) + bar_width,
            suffix[: max(0, width - len(prefix) - bar_width)],
            attr,
        )
    def render_sessions(self, height: int, width: int) -> None:
        sessions = self.state.visible_sessions()
        token_widths = self._session_token_widths(sessions)
        max_total = max((session.tokens.total_tokens for session in sessions), default=0)
        rows_available = max(0, height - 7)
        start_index = visible_start(self.state.selected_index, rows_available, len(sessions))
        model_width = self.session_model_width(
            width,
            self.options.display.model_column_width,
        )
        header = f"{'session':<12} {'usage':<10} {self.session_header_fields(token_widths)}"
        if self.options.display.show_model:
            header += f"  {'model':<{model_width}}"
        if self.options.display.show_context:
            header += "  cwd/title"
        self.render_themed_text(4, 0, header[: max(0, width - 1)], curses.A_BOLD)
        visible = sessions[start_index : start_index + rows_available]
        for row_offset, session in enumerate(visible):
            row_index = start_index + row_offset
            marker = ">" if row_index == self.state.selected_index else " "
            context = f"{session.cwd}  {session.title}"
            prefix = (
                f"{marker}{session.session_id[:12]:<12} "
            )
            suffix = " " + self.session_value_fields(session, token_widths)
            if self.options.display.show_model:
                suffix += f"  {truncate(session.model, model_width):<{model_width}}"
            if self.options.display.show_context:
                suffix += f"  {truncate(context, max(8, width // 3))}"
            attr = (
                self.theme_attr(row_offset, curses.A_REVERSE)
                if row_index == self.state.selected_index
                else 0
            )
            y = 5 + row_offset
            self.safe_addstr(y, 0, prefix, attr)
            self.render_themed_bar(
                y,
                len(prefix),
                session.tokens.total_tokens,
                max_total,
                10,
                attr,
            )
            self.safe_addstr(y, len(prefix) + 10, suffix, attr)
    def render_details(self, height: int, width: int) -> None:
        if self.state.tab_view == "projects":
            self.render_project_details(height, width)
            return
        session = self.state.selected_session()
        if session is None:
            self.safe_addstr(2, 0, "No session selected.")
            return
        rows = [
            ("Session", session.session_id),
            ("Title", session.title),
            ("Model", session.model),
            ("Reasoning level", session.reasoning_level),
            ("CWD", session.cwd),
            ("Created", session.created_at.isoformat() if session.created_at else ""),
            ("Updated", session.updated_at.isoformat() if session.updated_at else ""),
            ("Path", str(session.path)),
            ("Total", format_int(session.tokens.total_tokens)),
            ("Input incl. cache", format_int(session.tokens.input_tokens)),
            ("Output", format_int(session.tokens.output_tokens)),
            ("Cached input", format_int(session.tokens.cached_input_tokens)),
            ("Uncached input", format_int(session.tokens.cache_miss_input_tokens)),
            ("Reasoning output", format_int(session.tokens.reasoning_output_tokens)),
            ("Corrupt lines skipped", str(session.corrupt_lines)),
        ]
        if self.options.display.show_cached_percent:
            rows.insert(
                11,
                ("Cached input %", format_percent(session.tokens.cached_input_percent)),
            )
        if self.options.display.show_estimated_cost:
            rows.insert(
                13,
                (
                    "Estimated API cost",
                    format_cost(estimate_session_cost(session, self.state.pricing)),
                ),
            )
        self.render_key_values(4, rows, width, height)

    def render_project_details(self, height: int, width: int) -> None:
        project = self.state.selected_project()
        if project is None:
            self.safe_addstr(2, 0, "No project selected.")
            return
        tokens = project.project.tokens
        rows = [
            ("Project", project.project.key),
            ("Sessions", format_int(project.project.sessions)),
            ("Models", format_int(len(project.models))),
            ("Total", format_int(tokens.total_tokens)),
            ("Input incl. cache", format_int(tokens.input_tokens)),
            ("Output", format_int(tokens.output_tokens)),
            ("Cached input", format_int(tokens.cached_input_tokens)),
            ("Uncached input", format_int(tokens.cache_miss_input_tokens)),
            ("Reasoning output", format_int(tokens.reasoning_output_tokens)),
        ]
        if self.options.display.show_cached_percent:
            rows.insert(
                7,
                ("Cached input %", format_percent(tokens.cached_input_percent)),
            )
        if self.options.display.show_estimated_cost:
            rows.insert(
                4,
                ("Estimated API cost", format_cost(project.project.estimated_cost)),
            )
        summary_count = min(len(rows), max(0, height - 12))
        self.render_key_values(4, rows[:summary_count], width, height)
        table_y = 4 + summary_count + 1
        if table_y >= height - 2:
            return
        model_width = min(
            max(16, max((len(row.key) for row in project.models), default=5)),
            max(16, width // 3),
        )
        token_widths = self._aggregate_token_widths(project.models)
        header = (
            f"{'model':<{model_width}} {'usage':<14} "
            f"{self.aggregate_header_fields(token_widths)}"
        )
        self.render_themed_text(table_y, 0, header[: max(0, width - 1)], curses.A_BOLD)
        max_total = max((row.tokens.total_tokens for row in project.models), default=0)
        rows_available = max(0, height - table_y - 2)
        for offset, row in enumerate(project.models[:rows_available], start=table_y + 1):
            self.render_usage_row(
                offset,
                "model",
                row,
                max_total,
                width,
                model_width,
                token_widths=token_widths,
                bar_width=14,
            )
