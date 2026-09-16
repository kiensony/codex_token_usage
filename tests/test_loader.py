from __future__ import annotations

import json
import sqlite3
import tempfile
import unittest
from datetime import date
from pathlib import Path

from codex_token_usage.loader import load_usage, parse_session_jsonl
from codex_token_usage.models import TokenBreakdown


class LoaderTests(unittest.TestCase):
    def test_repeated_astra_snapshots_do_not_multiply_tokens(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "astra.jsonl"
            event = token_event(100_000, 17_000, 90_000, 10_000, 117_000)
            event["payload"]["info"]["last_token_usage"] = {
                "input_tokens": 20_000,
                "output_tokens": 2_000,
                "total_tokens": 22_000,
            }
            write_jsonl(path, [
                {"type": "turn_context", "payload": {"model": "gpt-6-astra"}},
                *[event] * 10,
            ])

            usage = parse_session_jsonl(path)

        self.assertEqual(usage.tokens.total_tokens, 117_000)
        self.assertEqual(usage.request_count, 1)
        self.assertEqual(len(usage.usage_events), 1)
        self.assertEqual(usage.tokens.cache_miss_input_tokens, 10_000)
        self.assertEqual(sum(e.tokens.total_tokens for e in usage.usage_events), 117_000)

    def test_rate_limit_refresh_does_not_reset_cumulative_baseline(self) -> None:
        for info in (None, {}, {"total_token_usage": None}, {"total_token_usage": {}}, {"token_count": {}}):
            with self.subTest(info=info), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "session.jsonl"
                refresh = {"type": "event_msg", "payload": {"type": "token_count", "info": info}}
                write_jsonl(path, [
                    token_event(100, 10, 50, 5, 110),
                    refresh,
                    token_event(200, 20, 100, 10, 220),
                    refresh,
                ])
                usage = parse_session_jsonl(path)
                self.assertEqual(usage.tokens.total_tokens, 220)
                self.assertEqual(sum(e.tokens.total_tokens for e in usage.usage_events), 220)
                self.assertEqual(usage.request_count, 2)

    def test_date_range_counts_only_new_tokens_in_resumed_session(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "sessions").mkdir()
            write_jsonl(root / "sessions" / "resumed.jsonl", [
                {"type": "session_meta", "payload": {"id": "resumed", "model": "gpt-6-astra"}},
                token_event(3_150_000_000, 0, 0, 0, 3_150_000_000, "2026-08-31T12:00:00Z"),
                token_event(4_000_000_000, 0, 0, 0, 4_000_000_000, "2026-09-16T12:00:00Z"),
            ])
            all_time = load_usage(root)
            today = load_usage(root, since=date(2026, 9, 16), until=date(2026, 9, 16))
            past = load_usage(root, until=date(2026, 8, 31))

        self.assertEqual(all_time.totals.input_tokens, 4_000_000_000)
        self.assertEqual(today.totals.input_tokens, 850_000_000)
        self.assertEqual(today.sessions[0].request_count, 1)
        self.assertEqual(past.totals.input_tokens, 3_150_000_000)

    def test_final_cumulative_token_count_event_is_counted_once(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "session-1.jsonl"
            write_jsonl(
                path,
                [
                    {
                        "timestamp": "2026-06-01T10:00:00Z",
                        "type": "session_meta",
                        "payload": {
                            "id": "session-1",
                            "cwd": "/repo",
                            "reasoning": {"effort": "medium"},
                        },
                    },
                    token_event(10, 4, 2, 1, 14),
                    token_event(20, 8, 5, 3, 28),
                ],
            )

            session = parse_session_jsonl(path)

            self.assertEqual(session.tokens.total_tokens, 28)
            self.assertEqual(session.tokens.input_tokens, 20)
            self.assertEqual(session.tokens.output_tokens, 8)
            self.assertEqual(session.tokens.cached_input_tokens, 5)
            self.assertEqual(session.tokens.reasoning_output_tokens, 3)
            self.assertEqual(session.request_count, 2)
            self.assertEqual(
                [event.tokens for event in session.usage_events],
                [
                    TokenBreakdown(
                        input_tokens=10,
                        output_tokens=4,
                        cached_input_tokens=2,
                        reasoning_output_tokens=1,
                        total_tokens=14,
                    ),
                    TokenBreakdown(
                        input_tokens=10,
                        output_tokens=4,
                        cached_input_tokens=3,
                        reasoning_output_tokens=2,
                        total_tokens=14,
                    ),
                ],
            )
            self.assertEqual(
                [event.occurred_at.isoformat() for event in session.usage_events],
                [
                    "2026-06-01T10:01:00+00:00",
                    "2026-06-01T10:01:00+00:00",
                ],
            )
            self.assertEqual(session.reasoning_level, "medium")

    def test_corrupt_jsonl_lines_are_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.jsonl"
            path.write_text(
                "\n".join(
                    [
                        json.dumps({"type": "session_meta", "payload": {"id": "bad"}}),
                        "{not-json",
                        json.dumps(token_event(2, 3, 0, 0, 5)),
                    ]
                ),
                encoding="utf-8",
            )

            session = parse_session_jsonl(path)

            self.assertEqual(session.corrupt_lines, 1)
            self.assertEqual(session.tokens.total_tokens, 5)

    def test_missing_metadata_falls_back_to_file_stem(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "stem-id.jsonl"
            write_jsonl(path, [token_event(1, 2, 0, 0, 3)])

            session = parse_session_jsonl(path)

            self.assertEqual(session.session_id, "stem-id")
            self.assertEqual(session.title, "stem-id")

    def test_sqlite_metadata_overrides_session_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            codex_home = Path(tmp)
            sessions = codex_home / "sessions"
            sessions.mkdir()
            write_jsonl(
                sessions / "s1.jsonl",
                [
                    {
                        "timestamp": "2026-06-01T00:00:00Z",
                        "type": "session_meta",
                        "payload": {"id": "s1", "cwd": "/jsonl", "model": "jsonl-model"},
                    },
                    token_event(5, 5, 0, 0, 10),
                ],
            )
            db = sqlite3.connect(codex_home / "state_5.sqlite")
            db.execute(
                "CREATE TABLE threads (id TEXT, title TEXT, model TEXT, reasoning_effort TEXT, cwd TEXT, created_at TEXT, updated_at TEXT, tokens_used INTEGER)"
            )
            db.execute(
                "INSERT INTO threads VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    "s1",
                    "SQLite title",
                    "sqlite-model",
                    "high",
                    "/sqlite",
                    "2026-06-02T00:00:00Z",
                    "2026-06-03T00:00:00Z",
                    10,
                ),
            )
            db.commit()
            db.close()

            dataset = load_usage(codex_home)

            self.assertTrue(dataset.sqlite_available)
            self.assertEqual(len(dataset.sessions), 1)
            session = dataset.sessions[0]
            self.assertEqual(session.title, "SQLite title")
            self.assertEqual(session.model, "sqlite-model")
            self.assertEqual(session.reasoning_level, "high")
            self.assertEqual(session.cwd, "/sqlite")
            self.assertEqual(session.activity_day.isoformat(), "2026-06-03")

    def test_invalid_sqlite_falls_back_to_jsonl_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            codex_home = Path(tmp)
            sessions = codex_home / "sessions"
            sessions.mkdir()
            write_jsonl(
                sessions / "s1.jsonl",
                [
                    {"type": "session_meta", "payload": {"id": "s1", "cwd": "/jsonl"}},
                    token_event(1, 1, 0, 0, 2),
                ],
            )
            (codex_home / "state_5.sqlite").write_text("not sqlite", encoding="utf-8")

            dataset = load_usage(codex_home)

            self.assertFalse(dataset.sqlite_available)
            self.assertEqual(dataset.sessions[0].cwd, "/jsonl")

    def test_date_filtering_and_include_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            codex_home = Path(tmp)
            sessions = codex_home / "sessions"
            sessions.mkdir()
            write_jsonl(
                sessions / "old.jsonl",
                [
                    {"timestamp": "2026-05-01T00:00:00Z", "type": "session_meta"},
                    token_event(1, 1, 0, 0, 2, timestamp="2026-05-01T00:01:00Z"),
                ],
            )
            write_jsonl(
                sessions / "new.jsonl",
                [
                    {"timestamp": "2026-06-01T00:00:00Z", "type": "session_meta"},
                    token_event(2, 2, 0, 0, 4),
                ],
            )
            write_jsonl(
                sessions / "zero.jsonl",
                [{"timestamp": "2026-06-02T00:00:00Z", "type": "session_meta"}],
            )

            dataset = load_usage(
                codex_home,
                since=date(2026, 6, 1),
                include_zero=True,
            )

            self.assertEqual([session.path.stem for session in dataset.sessions], ["new", "zero"])


def token_event(
    input_tokens: int,
    output_tokens: int,
    cached_tokens: int,
    reasoning_tokens: int,
    total_tokens: int,
    timestamp: str = "2026-06-01T10:01:00Z",
) -> dict:
    return {
        "timestamp": timestamp,
        "type": "event_msg",
        "payload": {
            "type": "token_count",
            "info": {
                "total_token_usage": {
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "cached_input_tokens": cached_tokens,
                    "reasoning_output_tokens": reasoning_tokens,
                    "total_tokens": total_tokens,
                }
            },
        },
    }


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "\n".join(json.dumps(row) for row in rows) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    unittest.main()
