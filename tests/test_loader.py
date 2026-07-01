from __future__ import annotations

import json
import sqlite3
import tempfile
import unittest
from datetime import date
from pathlib import Path

from codex_token_usage.loader import load_usage, parse_session_jsonl


class LoaderTests(unittest.TestCase):
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
