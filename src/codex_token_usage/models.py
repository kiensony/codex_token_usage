from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date, datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class TokenBreakdown:
    input_tokens: int = 0
    output_tokens: int = 0
    cached_input_tokens: int = 0
    reasoning_output_tokens: int = 0
    total_tokens: int = 0

    @classmethod
    def empty(cls) -> "TokenBreakdown":
        return cls()

    def normalized(self) -> "TokenBreakdown":
        total = self.total_tokens
        if total <= 0:
            total = self.input_tokens + self.output_tokens
        return replace(self, total_tokens=max(0, total))

    @property
    def cache_miss_input_tokens(self) -> int:
        return max(0, self.input_tokens - self.cached_input_tokens)

    @property
    def cached_input_percent(self) -> float:
        if self.input_tokens <= 0:
            return 0.0
        cached = min(max(0, self.cached_input_tokens), self.input_tokens)
        return (cached / self.input_tokens) * 100

    def add(self, other: "TokenBreakdown") -> "TokenBreakdown":
        return TokenBreakdown(
            input_tokens=self.input_tokens + other.input_tokens,
            output_tokens=self.output_tokens + other.output_tokens,
            cached_input_tokens=self.cached_input_tokens + other.cached_input_tokens,
            reasoning_output_tokens=self.reasoning_output_tokens
            + other.reasoning_output_tokens,
            total_tokens=self.total_tokens + other.total_tokens,
        )


@dataclass(frozen=True)
class SessionMetadata:
    session_id: str
    title: str | None = None
    model: str | None = None
    reasoning_level: str | None = None
    cwd: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def merge_prefer(self, preferred: "SessionMetadata | None") -> "SessionMetadata":
        if preferred is None:
            return self
        return SessionMetadata(
            session_id=self.session_id,
            title=preferred.title or self.title,
            model=preferred.model or self.model,
            reasoning_level=preferred.reasoning_level or self.reasoning_level,
            cwd=preferred.cwd or self.cwd,
            created_at=preferred.created_at or self.created_at,
            updated_at=preferred.updated_at or self.updated_at,
        )


@dataclass(frozen=True)
class SessionUsage:
    session_id: str
    path: Path
    tokens: TokenBreakdown
    metadata: SessionMetadata
    has_token_event: bool = False
    request_count: int = 0
    corrupt_lines: int = 0

    @property
    def title(self) -> str:
        return self.metadata.title or self.session_id

    @property
    def model(self) -> str:
        return self.metadata.model or "(unknown)"

    @property
    def reasoning_level(self) -> str:
        return self.metadata.reasoning_level or "-"

    @property
    def cwd(self) -> str:
        return self.metadata.cwd or "(unknown)"

    @property
    def created_at(self) -> datetime | None:
        return self.metadata.created_at

    @property
    def updated_at(self) -> datetime | None:
        return self.metadata.updated_at

    @property
    def activity_at(self) -> datetime | None:
        return self.updated_at or self.created_at

    @property
    def activity_day(self) -> date | None:
        if self.activity_at is None:
            return None
        return self.activity_at.date()


@dataclass(frozen=True)
class UsageDataset:
    sessions: tuple[SessionUsage, ...]
    codex_home: Path
    loaded_at: datetime
    sqlite_available: bool
    sqlite_error: str | None = None

    @property
    def totals(self) -> TokenBreakdown:
        total = TokenBreakdown.empty()
        for session in self.sessions:
            total = total.add(session.tokens)
        return total

    @classmethod
    def empty(cls, codex_home: Path) -> "UsageDataset":
        return cls(
            sessions=(),
            codex_home=codex_home,
            loaded_at=datetime.now(timezone.utc),
            sqlite_available=False,
        )
