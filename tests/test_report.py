from __future__ import annotations

import csv
import io
import json
import tempfile
import unittest
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

from codex_token_usage.forecast import LimitConfig
from codex_token_usage.models import (
    SessionMetadata,
    SessionUsage,
    TokenBreakdown,
    UsageDataset,
    UsageEvent,
)
from codex_token_usage.report import filter_sessions, make_report_rows, render_report
from codex_token_usage.theme import ThemeConfig


class ReportTests(unittest.TestCase):
    def test_unreliable_or_partial_timeline_preserves_final_total(self) -> None:
        base = session("partial", 300, "2026-09-16T12:00:00+00:00", Path("/tmp"))
        for event_total in (100, 400):
            with self.subTest(event_total=event_total):
                usage = replace(
                    base, tokens=TokenBreakdown(total_tokens=300),
                    usage_events=(UsageEvent(
                        datetime.fromisoformat("2026-08-31T12:00:00+00:00"),
                        TokenBreakdown(total_tokens=event_total),
                    ),),
                )
                data = replace(sample_dataset(), sessions=(usage,))
                rows = make_report_rows(data, "date")
                self.assertEqual(sum(r.tokens.total_tokens for r in rows), 300)
                self.assertEqual(rows[-1].tokens.total_tokens, 200 if event_total == 100 else 300)

    def test_date_buckets_use_utc_boundaries(self) -> None:
        at = datetime.fromisoformat("2026-09-17T00:30:00+02:00")
        usage = replace(
            sample_dataset().sessions[0],
            tokens=TokenBreakdown(total_tokens=100),
            usage_events=(UsageEvent(at, TokenBreakdown(total_tokens=100)),),
        )
        data = replace(sample_dataset(), sessions=(usage,))
        rows = make_report_rows(data, "date")
        self.assertEqual(rows[0].key, "2026-09-16")
        selected = filter_sessions(data.sessions, until=datetime(2026, 9, 16).date())
        self.assertEqual(selected[0].tokens.total_tokens, 100)

    def test_resumed_thread_usage_is_split_across_periods(self) -> None:
        events = tuple(
            UsageEvent(datetime.fromisoformat(at), TokenBreakdown(input_tokens=count).normalized())
            for at, count in (
                ("2026-08-31T12:00:00+00:00", 3_150_000_000),
                ("2026-09-16T11:00:00+00:00", 400_000_000),
                ("2026-09-16T12:00:00+00:00", 450_000_000),
            )
        )
        usage = replace(
            session("resumed", 4_000_000_000, "2026-09-16T12:00:00+00:00", Path("/tmp")),
            tokens=TokenBreakdown(input_tokens=4_000_000_000).normalized(),
            usage_events=events,
        )
        data = replace(sample_dataset(), sessions=(usage,))
        for group_by in ("date", "week", "month", "hour"):
            with self.subTest(group_by=group_by):
                rows = make_report_rows(data, group_by)
                self.assertEqual(sum(r.tokens.input_tokens for r in rows), 4_000_000_000)
                self.assertTrue(all(r.sessions == 1 for r in rows))
                expected = [3_150_000_000, 400_000_000, 450_000_000] if group_by == "hour" else [3_150_000_000, 850_000_000]
                self.assertEqual([r.tokens.input_tokens for r in rows], expected)

        selected = filter_sessions(data.sessions, since=events[1].occurred_at.date())
        today = replace(data, sessions=tuple(selected))
        # CLI filtering and report filtering may run twice; never restore lifetime usage.
        again = filter_sessions(today.sessions, since=events[1].occurred_at.date())
        self.assertEqual(again[0].tokens.input_tokens, 850_000_000)
        payload = json.loads(render_report(today, "json", "date"))
        self.assertEqual(payload["totals"]["input"], 850_000_000)
        self.assertEqual(payload["rows"][0]["tokens"]["input"], 850_000_000)
        csv_rows = list(csv.DictReader(io.StringIO(render_report(today, "csv", "date"))))
        self.assertEqual(csv_rows[0]["input"], "850000000")
        self.assertIn("850,000,000", render_report(today, "table", "date"))

    def test_group_by_date_week_month_hour_day_alias_and_model(self) -> None:
        dataset = sample_dataset()

        date_rows = make_report_rows(dataset, group_by="date")
        day_rows = make_report_rows(dataset, group_by="day")
        week_rows = make_report_rows(dataset, group_by="week")
        month_rows = make_report_rows(dataset, group_by="month")
        hour_rows = make_report_rows(dataset, group_by="hour")
        model_rows = make_report_rows(dataset, group_by="model")

        self.assertEqual([row.key for row in date_rows], ["2026-06-01", "2026-06-02"])
        self.assertEqual([row.key for row in day_rows], [row.key for row in date_rows])
        self.assertEqual([row.key for row in week_rows], ["2026-W23"])
        self.assertEqual(week_rows[0].sessions, 2)
        self.assertEqual(week_rows[0].tokens.total_tokens, 3000)
        self.assertEqual([row.key for row in month_rows], ["2026-06"])
        self.assertEqual(month_rows[0].sessions, 2)
        self.assertEqual(month_rows[0].tokens.total_tokens, 3000)
        self.assertEqual(
            [row.key for row in hour_rows],
            ["2026-06-01 00:00", "2026-06-02 13:00"],
        )
        self.assertEqual(date_rows[0].tokens.total_tokens, 1000)
        self.assertEqual(model_rows[0].key, "gpt-5")
        self.assertEqual(model_rows[0].tokens.total_tokens, 3000)

    def test_group_by_project_uses_exact_cwd_and_folder_alias(self) -> None:
        root = Path("/tmp")
        dataset = UsageDataset(
            sessions=(
                session(
                    "s1",
                    1000,
                    "2026-06-01T00:00:00+00:00",
                    root,
                    cwd="/work/app",
                ),
                session(
                    "s2",
                    2000,
                    "2026-06-02T00:00:00+00:00",
                    root,
                    cwd="/work/app",
                ),
                session(
                    "s3",
                    1500,
                    "2026-06-03T00:00:00+00:00",
                    root,
                    cwd="/other/app",
                ),
            ),
            codex_home=root,
            loaded_at=datetime.now(timezone.utc),
            sqlite_available=False,
        )

        project_rows = make_report_rows(dataset, group_by="project")
        folder_rows = make_report_rows(dataset, group_by="folder")

        self.assertEqual(
            [row.key for row in project_rows],
            ["/work/app", "/other/app"],
        )
        self.assertEqual(project_rows[0].sessions, 2)
        self.assertEqual(project_rows[0].tokens.total_tokens, 3000)
        self.assertEqual(
            [row.key for row in folder_rows],
            [row.key for row in project_rows],
        )

    def test_table_json_csv_and_graph_output(self) -> None:
        dataset = sample_dataset()

        table = render_report(dataset, "table", "session")
        payload = json.loads(render_report(dataset, "json", "model"))
        csv_rows = list(
            csv.DictReader(io.StringIO(render_report(dataset, "csv", "cwd")))
        )
        graph = render_report(dataset, "graph", "hour")

        self.assertIn("session", table)
        self.assertIn("2,000", table)
        self.assertIn("cached_percent", table)
        self.assertIn("cache_miss", table)
        self.assertEqual(payload["totals"]["total"], 3000)
        self.assertEqual(payload["totals"]["cached_percent"], 0.13)
        self.assertEqual(payload["totals"]["cache_miss"], 2994)
        self.assertEqual(csv_rows[0]["total"], "3000")
        self.assertEqual(csv_rows[0]["cached_percent"], "0.13")
        self.assertEqual(csv_rows[0]["cache_miss"], "2994")
        self.assertIn("hour token usage", graph)
        self.assertIn("cached", graph)
        self.assertIn("cached%", graph)
        self.assertIn("miss", graph)

    def test_cached_percent_uses_input_tokens(self) -> None:
        self.assertEqual(
            TokenBreakdown(input_tokens=10, cached_input_tokens=3).cached_input_percent,
            30.0,
        )
        self.assertEqual(
            TokenBreakdown(input_tokens=0, cached_input_tokens=3).cached_input_percent,
            0.0,
        )
        self.assertEqual(
            TokenBreakdown(input_tokens=10, cached_input_tokens=30).cached_input_percent,
            100.0,
        )

    def test_ansi_only_appears_for_themed_graph_output(self) -> None:
        dataset = sample_dataset()
        theme = ThemeConfig(enabled=True, preset="trans", color_mode="8bit")

        colored_graph = render_report(
            dataset,
            "graph",
            "hour",
            theme=theme,
            color_enabled=True,
        )
        plain_graph = render_report(
            dataset,
            "graph",
            "hour",
            theme=theme,
            color_enabled=False,
        )
        table = render_report(
            dataset,
            "table",
            "hour",
            theme=theme,
            color_enabled=True,
        )
        csv_output = render_report(
            dataset,
            "csv",
            "hour",
            theme=theme,
            color_enabled=True,
        )
        json_output = render_report(
            dataset,
            "json",
            "hour",
            theme=theme,
            color_enabled=True,
        )

        self.assertIn("\x1b[", colored_graph)
        self.assertNotIn("\x1b[", plain_graph)
        self.assertNotIn("\x1b[", table)
        self.assertNotIn("\x1b[", csv_output)
        self.assertNotIn("\x1b[", json_output)

    def test_top_limits_rows(self) -> None:
        rows = make_report_rows(sample_dataset(), group_by="session", top=1)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].key, "s2")

    def test_forecast_output_for_table_json_and_csv(self) -> None:
        dataset = sample_dataset()
        limits = LimitConfig(five_hour_tokens=5_000, weekly_tokens=10_000)
        as_of = datetime.fromisoformat("2026-06-02T14:00:00+00:00")

        table = render_report(
            dataset,
            "table",
            "week",
            limits=limits,
            as_of=as_of,
        )
        payload = json.loads(
            render_report(
                dataset,
                "json",
                "week",
                limits=limits,
                as_of=as_of,
            )
        )
        csv_rows = list(
            csv.DictReader(
                io.StringIO(
                    render_report(
                        dataset,
                        "csv",
                        "week",
                        limits=limits,
                        as_of=as_of,
                    )
                )
            )
        )

        self.assertIn("forecast warnings", table)
        self.assertIn("usage predictions", table)
        self.assertIn("forecast_status", table)
        self.assertIn("5h", table)
        self.assertEqual(payload["forecast"]["five_hour"]["status"], "warning")
        self.assertEqual(payload["forecast"]["weekly"]["status"], "warning")
        self.assertEqual(payload["forecast"]["predictions"][0]["name"], "next_5_hours")
        self.assertEqual(payload["forecast"]["predictions"][0]["projected"], 10_000)
        self.assertEqual(csv_rows[0]["forecast_status"], "warning")
        self.assertEqual(csv_rows[0]["forecast_limit"], "10000")
        self.assertEqual(csv_rows[0]["forecast_projected"], "13263")


def sample_dataset() -> UsageDataset:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        sessions = (
            session("s1", 1000, "2026-06-01T00:00:00+00:00", root),
            session("s2", 2000, "2026-06-02T13:30:00+00:00", root),
        )
        return UsageDataset(
            sessions=sessions,
            codex_home=root,
            loaded_at=datetime.now(timezone.utc),
            sqlite_available=False,
        )


def session(
    session_id: str,
    total: int,
    updated_at: str,
    root: Path,
    cwd: str = "/repo",
) -> SessionUsage:
    updated = datetime.fromisoformat(updated_at)
    return SessionUsage(
        session_id=session_id,
        path=root / f"{session_id}.jsonl",
        tokens=TokenBreakdown(
            input_tokens=total - 1,
            output_tokens=1,
            cached_input_tokens=2,
            reasoning_output_tokens=3,
            total_tokens=total,
        ),
        metadata=SessionMetadata(
            session_id=session_id,
            title=f"title {session_id}",
            model="gpt-5",
            cwd=cwd,
            created_at=updated,
            updated_at=updated,
        ),
        has_token_event=True,
    )


if __name__ == "__main__":
    unittest.main()
