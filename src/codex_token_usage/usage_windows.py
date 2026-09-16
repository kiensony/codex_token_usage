from __future__ import annotations

from dataclasses import fields, replace
from datetime import date, datetime, timezone
from typing import Callable, Iterable

from .models import SessionUsage, TokenBreakdown, UsageEvent


def utc_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def sum_tokens(events: Iterable[UsageEvent]) -> TokenBreakdown:
    total = TokenBreakdown.empty()
    for event in events:
        total = total.add(event.tokens)
    return total


def session_events(session: SessionUsage) -> tuple[UsageEvent, ...]:
    """Use request timestamps, with a last-activity fallback for undated usage."""
    events = session.usage_events
    dated = sum_tokens(events)
    if any(
        getattr(dated, field.name) > getattr(session.tokens, field.name)
        for field in fields(TokenBreakdown)
    ):
        # A reset/correction makes the delta timeline unreliable. Keep the
        # authoritative final count rather than multiplying usage across days.
        events = ()
        dated = TokenBreakdown.empty()
    remainder = TokenBreakdown(**{
        field.name: max(0, getattr(session.tokens, field.name) - getattr(dated, field.name))
        for field in fields(TokenBreakdown)
    })
    if session.activity_at is not None and (not events or remainder != TokenBreakdown.empty()):
        requests = max(0, session.request_count - sum(e.requests for e in events))
        if not events and session.tokens.total_tokens > 0:
            requests = max(1, requests)
        events += (UsageEvent(session.activity_at, remainder, requests=requests),)
    return events


def slice_session(
    session: SessionUsage, matches: Callable[[datetime], bool]
) -> SessionUsage | None:
    events = tuple(e for e in session_events(session) if matches(utc_datetime(e.occurred_at)))
    if not events:
        return None
    return replace(
        session,
        tokens=sum_tokens(events),
        request_count=sum(e.requests for e in events),
        usage_events=events,
    )


def slice_session_dates(
    session: SessionUsage, since: date | None, until: date | None
) -> SessionUsage | None:
    if since is None and until is None:
        return session
    return slice_session(
        session,
        lambda at: (since is None or at.date() >= since)
        and (until is None or at.date() <= until),
    )


def slice_session_window(
    session: SessionUsage, window_start: datetime, window_end: datetime
) -> SessionUsage | None:
    start, end = utc_datetime(window_start), utc_datetime(window_end)
    return slice_session(session, lambda at: start <= at <= end)
