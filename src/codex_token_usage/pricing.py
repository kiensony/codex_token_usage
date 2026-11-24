from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .model_catalog import MODEL_PRICES, REFERENCE_PRICING, ModelPrice
from .models import SessionUsage, TokenBreakdown, UsageDataset


@dataclass(frozen=True)
class CostEstimate:
    usd: float | None
    priced_sessions: int = 0
    unpriced_sessions: int = 0


@dataclass(frozen=True)
class PricingConfig:
    model_prices: tuple[tuple[str, ModelPrice], ...] = ()


def model_price(
    model: str | None,
    pricing: PricingConfig | None = None,
) -> ModelPrice | None:
    if not model:
        return None
    name = normalize_model_name(model)
    if pricing and pricing.model_prices:
        override = dict(pricing.model_prices).get(name)
        if override is not None:
            return override
    return MODEL_PRICES.get(name)


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


def available_model_names(
    dataset: UsageDataset,
    custom_prices: dict[str, ModelPrice],
) -> list[str]:
    names = MODEL_PRICES.keys() | REFERENCE_PRICING.keys() | custom_prices.keys()
    for session in dataset.sessions:
        model = normalize_model_name(session.model)
        if model and model != "(unknown)":
            names.add(model)
    return sorted(names)


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
