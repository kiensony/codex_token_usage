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
from .settings_model import prediction_algorithm_label
from .state import TAB_VIEWS, VIEW_LABELS
from .usage_rates import current_usage_rate_rows
from .view_overlays import ViewOverlayMixin


class ViewRendererMixin(ViewOverlayMixin):
    def render(self) -> None:
        self.stdscr.erase()
        height, width = self.stdscr.getmaxyx()
        self.render_header(width)
        if self.state.view == "overview":
            self.render_overview(height, width)
        elif self.state.view == "daily":
            self.render_daily(height, width)
        elif self.state.view == "weekly":
            self.render_weekly(height, width)
        elif self.state.view == "monthly":
            self.render_monthly(height, width)
        elif self.state.view == "hourly":
            self.render_hourly(height, width)
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
            ("Input tokens", format_int(totals.input_tokens)),
            ("Output tokens", format_int(totals.output_tokens)),
            ("Cached input", format_int(totals.cached_input_tokens)),
            ("Cache miss input", format_int(totals.cache_miss_input_tokens)),
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
    def render_projects(self, height: int, width: int) -> None:
        rows = self.state.project_rows()
        max_label = max((len(row.key) for row in rows), default=len("project"))
        label_width = min(max(16, max_label), max(16, width // 3))
        self.render_usage_rows(
            "project",
            rows,
            height,
            width,
            label_width=label_width,
        )
    def aggregate_header_fields(self) -> str:
        fields: list[tuple[str, int]] = [
            ("sessions", 8),
            ("total", 12),
        ]
        if self.options.display.show_cached_tokens:
            fields.append(("cached", 12))
        if self.options.display.show_cached_percent:
            fields.append(("cached%", 8))
        if self.options.display.show_estimated_cost:
            fields.append(("est $", 10))
        if self.options.display.show_cache_miss:
            fields.append(("miss", 12))
        if self.options.display.show_reasoning_tokens:
            fields.append(("reason", 10))
        return self.right_aligned_fields(fields)
    def aggregate_value_fields(self, row) -> str:
        fields: list[tuple[str, int]] = [
            (format_int(row.sessions), 8),
            (format_int(row.tokens.total_tokens), 12),
        ]
        if self.options.display.show_cached_tokens:
            fields.append((format_int(row.tokens.cached_input_tokens), 12))
        if self.options.display.show_cached_percent:
            fields.append((format_percent(row.tokens.cached_input_percent), 8))
        if self.options.display.show_estimated_cost:
            fields.append((format_cost(row.estimated_cost), 10))
        if self.options.display.show_cache_miss:
            fields.append((format_int(row.tokens.cache_miss_input_tokens), 12))
        if self.options.display.show_reasoning_tokens:
            fields.append((format_int(row.tokens.reasoning_output_tokens), 10))
        return self.right_aligned_fields(fields)
    def session_header_fields(self) -> str:
        fields: list[tuple[str, int]] = [
            ("total", 10),
        ]
        if self.options.display.show_cached_tokens:
            fields.append(("cached", 10))
        if self.options.display.show_cached_percent:
            fields.append(("cached%", 8))
        if self.options.display.show_estimated_cost:
            fields.append(("est $", 10))
        if self.options.display.show_reasoning_level:
            fields.append(("effort", 8))
        if self.options.display.show_cache_miss:
            fields.append(("miss", 10))
        if self.options.display.show_reasoning_tokens:
            fields.append(("reason", 8))
        return self.right_aligned_fields(fields)
    def session_value_fields(self, session: SessionUsage) -> str:
        fields: list[tuple[str, int]] = [
            (format_int(session.tokens.total_tokens), 10),
        ]
        if self.options.display.show_cached_tokens:
            fields.append((format_int(session.tokens.cached_input_tokens), 10))
        if self.options.display.show_cached_percent:
            fields.append((format_percent(session.tokens.cached_input_percent), 8))
        if self.options.display.show_estimated_cost:
            fields.append(
                (format_cost(estimate_session_cost(session, self.state.pricing)), 10)
            )
        if self.options.display.show_reasoning_level:
            fields.append((truncate(session.reasoning_level, 8), 8))
        if self.options.display.show_cache_miss:
            fields.append((format_int(session.tokens.cache_miss_input_tokens), 10))
        if self.options.display.show_reasoning_tokens:
            fields.append((format_int(session.tokens.reasoning_output_tokens), 8))
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
        max_total = max((row.tokens.total_tokens for row in rows), default=0)
        header = (
            f"{label:<{label_width}} {'usage':<14} "
            f"{self.aggregate_header_fields()}"
        )
        if forecast_window and forecast_window.enabled and label == "week":
            header += " forecast"
        self.render_themed_text(4, 0, header[: max(0, width - 1)], curses.A_BOLD)
        for offset, row in enumerate(rows[: max(0, height - 7)], start=5):
            row_key = truncate(row.key, label_width)
            prefix = f"{row_key:<{label_width}} "
            suffix = " " + self.aggregate_value_fields(row)
            status = usage_row_forecast_status(label, row.key, forecast_window)
            if status:
                suffix += f" {status}"
            self.safe_addstr(offset, 0, prefix)
            self.render_themed_bar(
                offset,
                len(prefix),
                row.tokens.total_tokens,
                max_total,
                14,
            )
            self.safe_addstr(offset, len(prefix) + 14, suffix)
    def render_sessions(self, height: int, width: int) -> None:
        sessions = self.state.visible_sessions()
        max_total = max((session.tokens.total_tokens for session in sessions), default=0)
        rows_available = max(0, height - 7)
        start_index = visible_start(self.state.selected_index, rows_available, len(sessions))
        model_width = self.session_model_width(
            width,
            self.options.display.model_column_width,
        )
        header = f"{'session':<12} {'usage':<10} {self.session_header_fields()}"
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
            suffix = " " + self.session_value_fields(session)
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
            ("Input", format_int(session.tokens.input_tokens)),
            ("Output", format_int(session.tokens.output_tokens)),
            ("Cached input", format_int(session.tokens.cached_input_tokens)),
            ("Cache miss input", format_int(session.tokens.cache_miss_input_tokens)),
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
