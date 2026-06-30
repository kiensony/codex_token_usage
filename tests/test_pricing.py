from __future__ import annotations

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
from codex_token_usage.pricing import (
    ModelPrice,
    PricingConfig,
    estimate_session_cost,
    estimate_sessions_cost,
    format_cost,
)
from codex_token_usage.report import make_report_rows


class PricingTests(unittest.TestCase):
    def test_estimates_session_cost_with_cached_input_discount(self) -> None:
        estimate = estimate_session_cost(
            session(
                "priced",
                "gpt-5.3-codex",
                TokenBreakdown(
                    input_tokens=1_000_000,
                    cached_input_tokens=250_000,
                    output_tokens=100_000,
                    total_tokens=1_100_000,
                ),
            )
        )

        self.assertAlmostEqual(estimate.usd or 0, 2.75625)
        self.assertEqual(estimate.priced_sessions, 1)
        self.assertEqual(estimate.unpriced_sessions, 0)

    def test_unknown_model_is_unpriced(self) -> None:
        estimate = estimate_session_cost(
            session(
                "unknown",
                "custom-model",
                TokenBreakdown(input_tokens=1_000, output_tokens=1_000),
            )
        )

        self.assertIsNone(estimate.usd)
        self.assertEqual(format_cost(estimate), "n/a")

    def test_custom_pricing_config_overrides_unknown_model(self) -> None:
        pricing = PricingConfig(
            model_prices=(
                ("custom-model", ModelPrice(2.0, 0.5, 8.0)),
            )
        )

        estimate = estimate_session_cost(
            session(
                "custom",
                "custom-model",
                TokenBreakdown(
                    input_tokens=1_000_000,
                    cached_input_tokens=500_000,
                    output_tokens=250_000,
                ),
            ),
            pricing,
        )

        self.assertAlmostEqual(estimate.usd or 0, 3.25)

    def test_aggregate_cost_marks_partial_estimates(self) -> None:
        sessions = [
            session(
                "priced",
                "gpt-5.3-codex",
                TokenBreakdown(input_tokens=1_000, output_tokens=1_000),
            ),
            session(
                "unknown",
                "custom-model",
                TokenBreakdown(input_tokens=1_000, output_tokens=1_000),
            ),
        ]

        estimate = estimate_sessions_cost(sessions)

        self.assertIsNotNone(estimate.usd)
        self.assertEqual(estimate.priced_sessions, 1)
        self.assertEqual(estimate.unpriced_sessions, 1)
        self.assertTrue(format_cost(estimate).endswith("*"))

    def test_report_rows_include_aggregate_costs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            dataset = UsageDataset(
                sessions=(
                    session(
                        "first",
                        "gpt-5.3-codex",
                        TokenBreakdown(input_tokens=1_000, output_tokens=1_000),
                        root,
                    ),
                    session(
                        "second",
                        "gpt-5.3-codex",
                        TokenBreakdown(input_tokens=2_000, output_tokens=2_000),
                        root,
                    ),
                ),
                codex_home=root,
                loaded_at=datetime.now(timezone.utc),
                sqlite_available=False,
            )

            rows = make_report_rows(dataset, group_by="date")

        self.assertEqual(len(rows), 1)
        self.assertIsNotNone(rows[0].estimated_cost.usd)
        self.assertEqual(rows[0].estimated_cost.priced_sessions, 2)


def session(
    session_id: str,
    model: str,
    tokens: TokenBreakdown,
    root: Path | None = None,
) -> SessionUsage:
    root = root or Path("/tmp")
    updated = datetime(2026, 6, 1, tzinfo=timezone.utc)
    return SessionUsage(
        session_id=session_id,
        path=root / f"{session_id}.jsonl",
        tokens=tokens.normalized(),
        metadata=SessionMetadata(
            session_id=session_id,
            model=model,
            cwd="/repo",
            created_at=updated,
            updated_at=updated,
        ),
        has_token_event=True,
    )


if __name__ == "__main__":
    unittest.main()
