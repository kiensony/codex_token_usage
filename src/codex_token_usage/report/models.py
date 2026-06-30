from __future__ import annotations

from dataclasses import dataclass

from ..models import TokenBreakdown
from ..pricing import CostEstimate

TIME_GROUPS = {"date", "day", "week", "month", "hour"}


@dataclass(frozen=True)
class ReportRow:
    key: str
    sessions: int
    tokens: TokenBreakdown
    model: str | None = None
    cwd: str | None = None
    title: str | None = None
    updated_at: str | None = None
    estimated_cost: CostEstimate = CostEstimate(usd=None)
