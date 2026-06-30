from __future__ import annotations

import json
import sqlite3
from dataclasses import replace
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote

from .models import SessionMetadata, SessionUsage, TokenBreakdown, UsageDataset


TOKEN_COUNT_KEYS = ("token_count", "token_counts", "tokens")
EVENT_TYPE_KEYS = ("type", "event", "name")


def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"invalid date {value!r}; expected YYYY-MM-DD") from exc


def parse_datetime(value: Any) -> datetime | None:
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, (int, float)):
        seconds = float(value)
        if seconds > 10_000_000_000:
            seconds /= 1000
        try:
            return datetime.fromtimestamp(seconds, timezone.utc)
        except (OSError, OverflowError, ValueError):
            return None
    if not isinstance(value, str):
        return None
    text = value.strip()
    if not text:
        return None
    if text.isdigit():
        return parse_datetime(int(text))
    if text.endswith("Z"):
        text = f"{text[:-1]}+00:00"
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def load_usage(
    codex_home: Path,
    since: date | None = None,
    until: date | None = None,
    include_zero: bool = False,
) -> UsageDataset:
    codex_home = codex_home.expanduser()
    sqlite_metadata, sqlite_available, sqlite_error = load_sqlite_metadata(codex_home)
    sessions_dir = codex_home / "sessions"
    sessions: list[SessionUsage] = []

    if sessions_dir.exists():
        for path in sorted(sessions_dir.glob("**/*.jsonl")):
            session = parse_session_jsonl(path)
            session = apply_sqlite_metadata(session, sqlite_metadata)
            if should_include_session(session, since, until, include_zero):
                sessions.append(session)

    return UsageDataset(
        sessions=tuple(sessions),
        codex_home=codex_home,
        loaded_at=datetime.now(timezone.utc),
        sqlite_available=sqlite_available,
        sqlite_error=sqlite_error,
    )


def should_include_session(
    session: SessionUsage,
    since: date | None,
    until: date | None,
    include_zero: bool,
) -> bool:
    if not include_zero and session.tokens.total_tokens <= 0:
        return False
    session_day = session.activity_day
    if since and (session_day is None or session_day < since):
        return False
    if until and (session_day is None or session_day > until):
        return False
    return True


def parse_session_jsonl(path: Path) -> SessionUsage:
    session_id = path.stem
    metadata = SessionMetadata(session_id=session_id)
    final_tokens: TokenBreakdown | None = None
    has_token_event = False
    corrupt_lines = 0
    latest_timestamp: datetime | None = None

    try:
        with path.open(encoding="utf-8") as file:
            for line in file:
                if not line.strip():
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    corrupt_lines += 1
                    continue

                event_time = first_datetime(event, ("timestamp", "created_at", "time"))
                if event_time and is_after(event_time, latest_timestamp):
                    latest_timestamp = event_time

                metadata = merge_session_metadata(metadata, event, path)
                token_payload = extract_token_payload(event)
                if token_payload is not None:
                    has_token_event = True
                    parsed_tokens = parse_token_breakdown(token_payload)
                    final_tokens = parsed_tokens.normalized()
    except OSError:
        corrupt_lines = 1

    if metadata.created_at is None:
        metadata = replace(metadata, created_at=latest_timestamp)
    if latest_timestamp and is_after(latest_timestamp, metadata.updated_at):
        metadata = replace(metadata, updated_at=latest_timestamp)
    elif metadata.updated_at is None:
        metadata = replace(metadata, updated_at=latest_timestamp)
    if metadata.session_id == path.stem and session_id != metadata.session_id:
        session_id = metadata.session_id
    else:
        session_id = metadata.session_id or session_id

    tokens = final_tokens or TokenBreakdown.empty()
    return SessionUsage(
        session_id=session_id,
        path=path,
        tokens=tokens,
        metadata=metadata,
        has_token_event=has_token_event,
        corrupt_lines=corrupt_lines,
    )


def merge_session_metadata(
    current: SessionMetadata, event: dict[str, Any], path: Path
) -> SessionMetadata:
    payload = event.get("payload") if isinstance(event.get("payload"), dict) else {}
    event_type = event.get("type")
    payload_type = payload.get("type")

    candidates: list[dict[str, Any]] = []
    if event_type == "session_meta":
        candidates.append({**event, **payload})
    if payload_type in {"session_meta", "turn_context"}:
        candidates.append({**event, **payload})
    if event_type == "turn_context":
        candidates.append({**event, **payload})

    session_id = current.session_id
    title = current.title
    model = current.model
    reasoning_level = current.reasoning_level
    cwd = current.cwd
    created_at = current.created_at
    updated_at = current.updated_at

    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        session_id = str(
            first_present(candidate, ("id", "session_id", "thread_id")) or session_id
        )
        title = first_str(candidate, ("title", "name", "summary")) or title
        model = first_str(candidate, ("model", "model_slug")) or model
        reasoning_level = first_reasoning_level(candidate) or reasoning_level
        cwd = first_str(candidate, ("cwd", "working_directory", "workdir")) or cwd
        candidate_created = first_datetime(
            candidate, ("created_at", "createdAt", "created", "timestamp")
        )
        candidate_updated = first_datetime(
            candidate, ("updated_at", "updatedAt", "updated", "timestamp")
        )
        if candidate_created and created_at is None:
            created_at = candidate_created
        if candidate_updated and is_after(candidate_updated, updated_at):
            updated_at = candidate_updated

    if session_id == "":
        session_id = path.stem
    return SessionMetadata(
        session_id=session_id,
        title=title,
        model=model,
        reasoning_level=reasoning_level,
        cwd=cwd,
        created_at=created_at,
        updated_at=updated_at,
    )


def extract_token_payload(event: dict[str, Any]) -> dict[str, Any] | None:
    if is_token_event(event):
        return token_container(event)
    payload = event.get("payload")
    if isinstance(payload, dict) and is_token_event(payload):
        return token_container(payload)
    return None


def is_token_event(data: dict[str, Any]) -> bool:
    for key in EVENT_TYPE_KEYS:
        if data.get(key) == "token_count":
            return True
    return any(key in data for key in TOKEN_COUNT_KEYS)


def token_container(data: dict[str, Any]) -> dict[str, Any]:
    info = data.get("info")
    if isinstance(info, dict):
        total_usage = info.get("total_token_usage")
        if isinstance(total_usage, dict):
            return total_usage
        token_count = info.get("token_count")
        if isinstance(token_count, dict):
            return token_count
        return info
    for key in TOKEN_COUNT_KEYS:
        value = data.get(key)
        if isinstance(value, dict):
            return value
    return data


def parse_token_breakdown(data: dict[str, Any]) -> TokenBreakdown:
    return TokenBreakdown(
        input_tokens=first_int(data, ("input_tokens", "input", "prompt_tokens")),
        output_tokens=first_int(data, ("output_tokens", "output", "completion_tokens")),
        cached_input_tokens=first_int(
            data, ("cached_input_tokens", "cached_tokens", "cached")
        ),
        reasoning_output_tokens=first_int(
            data,
            (
                "reasoning_output_tokens",
                "reasoning_tokens",
                "reasoning",
            ),
        ),
        total_tokens=first_int(data, ("total_tokens", "total", "tokens_used")),
    )


def load_sqlite_metadata(
    codex_home: Path,
) -> tuple[dict[str, SessionMetadata], bool, str | None]:
    db_path = codex_home / "state_5.sqlite"
    if not db_path.exists():
        return {}, False, None

    uri = f"file:{quote(str(db_path.resolve()), safe='/')}?mode=ro"
    try:
        conn = sqlite3.connect(uri, uri=True)
        conn.row_factory = sqlite3.Row
    except sqlite3.Error as exc:
        return {}, False, str(exc)

    try:
        metadata = read_metadata_tables(conn)
        return metadata, True, None
    except sqlite3.Error as exc:
        return {}, False, str(exc)
    finally:
        conn.close()


def read_metadata_tables(conn: sqlite3.Connection) -> dict[str, SessionMetadata]:
    table_names = {
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_schema WHERE type = 'table'"
        ).fetchall()
    }
    metadata: dict[str, SessionMetadata] = {}
    for table in ("threads", "sessions"):
        if table not in table_names:
            continue
        metadata.update(read_metadata_table(conn, table))
    return metadata


def read_metadata_table(
    conn: sqlite3.Connection, table: str
) -> dict[str, SessionMetadata]:
    columns = [row[1] for row in conn.execute(f'PRAGMA table_info("{table}")')]
    if not columns:
        return {}
    id_col = choose_column(columns, ("id", "thread_id", "session_id"))
    if not id_col:
        return {}
    selected = [id_col]
    for choices in (
        ("title", "name", "summary"),
        ("model", "model_slug"),
        (
            "reasoning_effort",
            "reasoning_level",
            "reasoning",
            "reasoningEffort",
            "reasoningLevel",
        ),
        ("cwd", "working_directory", "workdir"),
        ("created_at", "createdAt", "created", "timestamp"),
        ("updated_at", "updatedAt", "updated", "last_active_at"),
    ):
        col = choose_column(columns, choices)
        if col and col not in selected:
            selected.append(col)

    select_sql = ", ".join(quote_identifier(col) for col in selected)
    rows = conn.execute(f'SELECT {select_sql} FROM "{table}"').fetchall()

    result: dict[str, SessionMetadata] = {}
    for row in rows:
        data = dict(row)
        session_id_value = data.get(id_col)
        if session_id_value is None:
            continue
        session_id = str(session_id_value)
        result[session_id] = SessionMetadata(
            session_id=session_id,
            title=first_str(data, ("title", "name", "summary")),
            model=first_str(data, ("model", "model_slug")),
            reasoning_level=first_reasoning_level(data),
            cwd=first_str(data, ("cwd", "working_directory", "workdir")),
            created_at=first_datetime(
                data, ("created_at", "createdAt", "created", "timestamp")
            ),
            updated_at=first_datetime(
                data, ("updated_at", "updatedAt", "updated", "last_active_at")
            ),
        )
    return result


def apply_sqlite_metadata(
    session: SessionUsage, sqlite_metadata: dict[str, SessionMetadata]
) -> SessionUsage:
    preferred = sqlite_metadata.get(session.session_id) or sqlite_metadata.get(
        session.path.stem
    )
    if preferred is None:
        return session
    merged = session.metadata.merge_prefer(preferred)
    return replace(session, metadata=merged, session_id=merged.session_id)


def quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def choose_column(columns: list[str], choices: tuple[str, ...]) -> str | None:
    by_lower = {column.lower(): column for column in columns}
    for choice in choices:
        exact = by_lower.get(choice.lower())
        if exact:
            return exact
    return None


def first_present(data: dict[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        if key in data and data[key] not in (None, ""):
            return data[key]
    return None


def first_str(data: dict[str, Any], keys: tuple[str, ...]) -> str | None:
    value = first_present(data, keys)
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def first_reasoning_level(data: dict[str, Any]) -> str | None:
    value = first_present(
        data,
        (
            "reasoning_effort",
            "reasoning_level",
            "reasoningEffort",
            "reasoningLevel",
            "reasoning",
        ),
    )
    if isinstance(value, dict):
        return first_str(
            value,
            (
                "effort",
                "level",
                "reasoning_effort",
                "reasoning_level",
                "reasoningEffort",
                "reasoningLevel",
            ),
        )
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def first_int(data: dict[str, Any], keys: tuple[str, ...]) -> int:
    value = first_present(data, keys)
    if value is None:
        return 0
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return max(0, value)
    if isinstance(value, float):
        return max(0, int(value))
    try:
        return max(0, int(str(value)))
    except ValueError:
        return 0


def first_datetime(data: dict[str, Any], keys: tuple[str, ...]) -> datetime | None:
    value = first_present(data, keys)
    return parse_datetime(value)


def is_after(candidate: datetime, current: datetime | None) -> bool:
    if current is None:
        return True
    return datetime_sort_key(candidate) > datetime_sort_key(current)


def datetime_sort_key(value: datetime) -> float:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.timestamp()
