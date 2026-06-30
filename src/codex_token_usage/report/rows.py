from __future__ import annotations

from datetime import date
from typing import Iterable

from ..models import SessionUsage, TokenBreakdown, UsageDataset
from ..pricing import CostEstimate, PricingConfig, estimate_session_cost
from .formatting import canonical_group_by, format_datetime, limit_rows
from .models import TIME_GROUPS, ReportRow

def filter_sessions(
    sessions: Iterable[SessionUsage],
    since: date | None = None,
    until: date | None = None,
    include_zero: bool = False,
) -> list[SessionUsage]:
    filtered: list[SessionUsage] = []
    for session in sessions:
        if not include_zero and session.tokens.total_tokens <= 0:
            continue
        day = session.activity_day
        if since and (day is None or day < since):
            continue
        if until and (day is None or day > until):
            continue
        filtered.append(session)
    return filtered
def make_report_rows(
    dataset: UsageDataset,
    group_by: str,
    top: int | None = None,
    pricing: PricingConfig | None = None,
) -> list[ReportRow]:
    group_by = canonical_group_by(group_by)
    sessions = list(dataset.sessions)
    if group_by == "session":
        rows = [
            ReportRow(
                key=session.session_id,
                sessions=1,
                tokens=session.tokens,
                model=session.model,
                cwd=session.cwd,
                title=session.title,
                updated_at=format_datetime(session.updated_at),
                estimated_cost=estimate_session_cost(session, pricing),
            )
            for session in sessions
        ]
        rows.sort(key=lambda row: row.tokens.total_tokens, reverse=True)
        return limit_rows(rows, top)

    grouped: dict[str, tuple[int, TokenBreakdown, float, int, int]] = {}
    for session in sessions:
        key = group_key(session, group_by)
        count, tokens, cost, priced_sessions, unpriced_sessions = grouped.get(
            key,
            (0, TokenBreakdown.empty(), 0.0, 0, 0),
        )
        estimate = estimate_session_cost(session, pricing)
        if estimate.usd is not None:
            cost += estimate.usd
        grouped[key] = (
            count + 1,
            tokens.add(session.tokens),
            cost,
            priced_sessions + estimate.priced_sessions,
            unpriced_sessions + estimate.unpriced_sessions,
        )

    rows = [
        ReportRow(
            key=key,
            sessions=count,
            tokens=tokens,
            estimated_cost=CostEstimate(
                usd=cost if priced_sessions else None,
                priced_sessions=priced_sessions,
                unpriced_sessions=unpriced_sessions,
            ),
        )
        for key, (
            count,
            tokens,
            cost,
            priced_sessions,
            unpriced_sessions,
        ) in grouped.items()
    ]
    if group_by in TIME_GROUPS:
        rows.sort(key=lambda row: row.key)
    else:
        rows.sort(key=lambda row: row.tokens.total_tokens, reverse=True)
    return limit_rows(rows, top)
def group_key(session: SessionUsage, group_by: str) -> str:
    group_by = canonical_group_by(group_by)
    if group_by == "date":
        return session.activity_day.isoformat() if session.activity_day else "(unknown)"
    if group_by == "week":
        day = session.activity_day
        if day is None:
            return "(unknown)"
        iso_week = day.isocalendar()
        return f"{iso_week.year}-W{iso_week.week:02d}"
    if group_by == "month":
        day = session.activity_day
        if day is None:
            return "(unknown)"
        return day.strftime("%Y-%m")
    if group_by == "hour":
        if session.activity_at is None:
            return "(unknown)"
        return session.activity_at.strftime("%Y-%m-%d %H:00")
    if group_by == "model":
        return session.model
    if group_by in {"cwd", "project"}:
        return session.cwd
    raise ValueError(f"unsupported group_by: {group_by}")
