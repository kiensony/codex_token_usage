from __future__ import annotations

import csv
import io
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from codex_token_usage.models import (
    SessionMetadata,
    SessionUsage,
    TokenBreakdown,
    UsageDataset,
)
from codex_token_usage.report import make_report_rows, render_report
from codex_token_usage.theme import ThemeConfig


class ReportTests(unittest.TestCase):
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
    session_id: str, total: int, updated_at: str, root: Path
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
            cwd="/repo",
            created_at=updated,
            updated_at=updated,
        ),
        has_token_event=True,
    )


if __name__ == "__main__":
    unittest.main()
