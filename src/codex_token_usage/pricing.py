from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .models import SessionUsage, TokenBreakdown


@dataclass(frozen=True)
class ModelPrice:
    input_per_million: float
    cached_input_per_million: float | None
    output_per_million: float


@dataclass(frozen=True)
class CostEstimate:
    usd: float | None
    priced_sessions: int = 0
    unpriced_sessions: int = 0


@dataclass(frozen=True)
class PricingConfig:
    model_prices: tuple[tuple[str, ModelPrice], ...] = ()


# USD per 1M tokens, standard processing, short-context rates where applicable.
# Refresh from https://developers.openai.com/api/docs/pricing when model prices change.
MODEL_PRICES: dict[str, ModelPrice] = {
    "chat-latest": ModelPrice(5.00, 0.50, 30.00),
    "gpt-5.3-codex": ModelPrice(1.75, 0.175, 14.00),
    "gpt-5.4": ModelPrice(2.50, 0.25, 15.00),
    "gpt-5.4-mini": ModelPrice(0.75, 0.075, 4.50),
    "gpt-5.4-nano": ModelPrice(0.20, 0.02, 1.25),
    "gpt-5.4-pro": ModelPrice(30.00, None, 180.00),
    "gpt-5.5": ModelPrice(5.00, 0.50, 30.00),
    "gpt-5.5-pro": ModelPrice(30.00, None, 180.00),
}


def model_price(
    model: str | None,
    pricing: PricingConfig | None = None,
) -> ModelPrice | None:
    if not model:
        return None
    return model_prices(pricing).get(normalize_model_name(model))


def model_prices(pricing: PricingConfig | None = None) -> dict[str, ModelPrice]:
    prices = dict(MODEL_PRICES)
    if pricing is not None:
        prices.update(dict(pricing.model_prices))
    return prices


def normalize_model_name(model: str) -> str:
    normalized = model.strip().lower()
    for prefix in ("openai/", "models/"):
        if normalized.startswith(prefix):
            normalized = normalized[len(prefix) :]
    return normalized


def estimate_tokens_cost(tokens: TokenBreakdown, price: ModelPrice) -> float:
    cached_input = min(max(0, tokens.cached_input_tokens), tokens.input_tokens)
    uncached_input = max(0, tokens.input_tokens - cached_input)
    cached_rate = (
        price.cached_input_per_million
        if price.cached_input_per_million is not None
        else price.input_per_million
    )
    return (
        (uncached_input * price.input_per_million)
        + (cached_input * cached_rate)
        + (tokens.output_tokens * price.output_per_million)
    ) / 1_000_000


def estimate_session_cost(
    session: SessionUsage,
    pricing: PricingConfig | None = None,
) -> CostEstimate:
    price = model_price(session.model, pricing)
    if price is None:
        return CostEstimate(usd=None, priced_sessions=0, unpriced_sessions=1)
    return CostEstimate(
        usd=estimate_tokens_cost(session.tokens, price),
        priced_sessions=1,
        unpriced_sessions=0,
    )


def estimate_sessions_cost(
    sessions: Iterable[SessionUsage],
    pricing: PricingConfig | None = None,
) -> CostEstimate:
    total = 0.0
    priced_sessions = 0
    unpriced_sessions = 0
    for session in sessions:
        estimate = estimate_session_cost(session, pricing)
        priced_sessions += estimate.priced_sessions
        unpriced_sessions += estimate.unpriced_sessions
        if estimate.usd is not None:
            total += estimate.usd
    if priced_sessions == 0:
        return CostEstimate(
            usd=None,
            priced_sessions=priced_sessions,
            unpriced_sessions=unpriced_sessions,
        )
    return CostEstimate(
        usd=total,
        priced_sessions=priced_sessions,
        unpriced_sessions=unpriced_sessions,
    )


def format_cost(estimate: CostEstimate) -> str:
    if estimate.usd is None:
        return "n/a"
    if estimate.usd == 0:
        value = "$0.00"
    elif estimate.usd < 0.01:
        value = f"${estimate.usd:.4f}"
    else:
        value = f"${estimate.usd:,.2f}"
    if estimate.unpriced_sessions:
        return f"{value}*"
    return value
