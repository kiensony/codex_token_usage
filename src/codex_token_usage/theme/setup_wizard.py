from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path
from typing import Callable, TextIO

from ..forecast import PREDICTION_ALGORITHMS, LimitConfig, PredictionConfig
from ..pricing import MODEL_PRICES, ModelPrice, PricingConfig, normalize_model_name
from .config import (
    load_theme_config,
    parse_auto_refresh_seconds,
    parse_lightness,
    parse_model_column_width,
    parse_rate,
    parse_shutdown_seconds,
    parse_token_limit,
    save_theme_config,
)
from .models import COLOR_MODES, DEFAULT_SHUTDOWN_SECONDS, DisplayConfig
from .presets import PRESET_NAMES
from .rendering import preview_theme

def run_setup_wizard(
    path: Path | None = None,
    input_fn: Callable[[str], str] = input,
    output: TextIO = sys.stdout,
) -> int:
    result = load_theme_config(path)
    config_path = path or result.path
    current = result.config
    current_display = result.display
    current_pricing = result.pricing
    current_keybindings = result.keybindings
    current_limits = result.limits
    current_prediction = result.prediction
    current_auto_refresh_seconds = result.auto_refresh_seconds
    current_shutdown_seconds = result.shutdown_seconds

    def write(line: str = "") -> None:
        output.write(line + "\n")

    write("Codex Token Usage theme setup")
    write(f"Config: {config_path}")
    if result.status:
        write(result.status)
    write("")

    try:
        color_mode = prompt_choice(
            "Color mode",
            COLOR_MODES,
            current.color_mode,
            input_fn,
            write,
        )
        preset = prompt_choice(
            "Theme preset",
            ("plain", *PRESET_NAMES),
            current.preset if current.enabled else "plain",
            input_fn,
            write,
        )
        if preset == "plain":
            next_config = replace(current, enabled=False, color_mode=color_mode)
            write(preview_theme(next_config))
        else:
            next_config = replace(
                current,
                enabled=True,
                preset=preset,
                color_mode=color_mode,
            )
            write(preview_theme(next_config))
            default_lightness = f"{next_config.lightness:.2f}".rstrip("0").rstrip(".")
            raw_lightness = input_fn(f"Lightness 0..1 [{default_lightness}]: ").strip()
            if raw_lightness:
                next_config = replace(
                    next_config,
                    lightness=parse_lightness(raw_lightness),
                )
                write(preview_theme(next_config))

        write("")
        write("Display columns:")
        next_display = DisplayConfig(
            show_cached_percent=prompt_bool(
                "Show cached input percentage",
                current_display.show_cached_percent,
                input_fn,
                write,
            ),
            show_estimated_cost=prompt_bool(
                "Show estimated API cost",
                current_display.show_estimated_cost,
                input_fn,
                write,
            ),
            show_reasoning_level=prompt_bool(
                "Show reasoning level",
                current_display.show_reasoning_level,
                input_fn,
                write,
            ),
            model_column_width=prompt_model_column_width(
                current_display.model_column_width,
                input_fn,
                write,
            ),
        )
        next_pricing = prompt_pricing_config(current_pricing, input_fn, write)
        next_limits = prompt_limit_config(current_limits, input_fn, write)
        next_prediction = prompt_prediction_config(current_prediction, input_fn, write)
        next_auto_refresh_seconds = prompt_auto_refresh_config(
            current_auto_refresh_seconds,
            input_fn,
            write,
        )
        next_shutdown_seconds = prompt_shutdown_config(
            current_shutdown_seconds,
            input_fn,
            write,
        )

        answer = input_fn("Save this config? [Y/n]: ").strip().lower()
    except (EOFError, KeyboardInterrupt, ValueError) as exc:
        write(f"setup canceled: {exc}")
        return 1

    if answer not in ("", "y", "yes"):
        write("setup canceled")
        return 1

    saved = save_theme_config(
        next_config,
        config_path,
        display=next_display,
        pricing=next_pricing,
        keybindings=current_keybindings,
        limits=next_limits,
        prediction=next_prediction,
        auto_refresh_seconds=next_auto_refresh_seconds,
        shutdown_seconds=next_shutdown_seconds,
    )
    write(f"saved {saved}")
    return 0


def prompt_choice(
    title: str,
    choices: tuple[str, ...],
    default: str,
    input_fn: Callable[[str], str],
    write: Callable[[str], None],
) -> str:
    write(title + ":")
    for index, choice in enumerate(choices, start=1):
        marker = " [default]" if choice == default else ""
        write(f"  {index}. {choice}{marker}")

    while True:
        raw = input_fn(f"Choose {title.lower()} [{default}]: ").strip().lower()
        if not raw:
            return default
        if raw in choices:
            return raw
        if raw.isdigit():
            index = int(raw)
            if 1 <= index <= len(choices):
                return choices[index - 1]
        write("Please choose one of the listed options.")


def prompt_bool(
    title: str,
    default: bool,
    input_fn: Callable[[str], str],
    write: Callable[[str], None],
) -> bool:
    suffix = "Y/n" if default else "y/N"
    while True:
        raw = input_fn(f"{title}? [{suffix}]: ").strip().lower()
        if not raw:
            return default
        if raw in ("y", "yes", "true", "1", "on"):
            return True
        if raw in ("n", "no", "false", "0", "off"):
            return False
        write("Please answer yes or no.")


def prompt_pricing_config(
    current: PricingConfig,
    input_fn: Callable[[str], str],
    write: Callable[[str], None],
) -> PricingConfig:
    custom_prices = dict(current.model_prices)
    write("")
    write("Model rates:")
    if custom_prices:
        for model, price in sorted(custom_prices.items()):
            cached = (
                "-"
                if price.cached_input_per_million is None
                else f"{price.cached_input_per_million:g}"
            )
            write(
                f"  {model}: input {price.input_per_million:g}, "
                f"cached {cached}, output {price.output_per_million:g}"
            )
    else:
        write("  no custom rates configured")
    if not prompt_bool("Add or update custom model rates", False, input_fn, write):
        return current

    while True:
        raw_model = input_fn("Model name to add/update [blank to finish]: ").strip()
        if not raw_model:
            break
        model = normalize_model_name(raw_model)
        default_price = custom_prices.get(model) or MODEL_PRICES.get(model)
        input_rate = prompt_rate(
            "Input $ per 1M tokens",
            default_price.input_per_million if default_price else None,
            input_fn,
            write,
        )
        cached_rate = prompt_optional_rate(
            "Cached input $ per 1M tokens",
            default_price.cached_input_per_million if default_price else None,
            input_fn,
            write,
        )
        output_rate = prompt_rate(
            "Output $ per 1M tokens",
            default_price.output_per_million if default_price else None,
            input_fn,
            write,
        )
        custom_prices[model] = ModelPrice(
            input_per_million=input_rate,
            cached_input_per_million=cached_rate,
            output_per_million=output_rate,
        )
        write(f"saved rate for {model}")

    return PricingConfig(model_prices=tuple(sorted(custom_prices.items())))


def prompt_limit_config(
    current: LimitConfig,
    input_fn: Callable[[str], str],
    write: Callable[[str], None],
) -> LimitConfig:
    write("")
    write("Token limits:")
    write("  Blank or 0 disables a limit.")
    return LimitConfig(
        five_hour_tokens=prompt_token_limit(
            "Rolling 5-hour token limit",
            current.five_hour_tokens,
            input_fn,
            write,
        ),
        weekly_tokens=prompt_token_limit(
            "Weekly token limit",
            current.weekly_tokens,
            input_fn,
            write,
        ),
    )


def prompt_prediction_config(
    current: PredictionConfig,
    input_fn: Callable[[str], str],
    write: Callable[[str], None],
) -> PredictionConfig:
    write("")
    write("Prediction:")
    algorithm = prompt_choice(
        "Prediction algorithm",
        PREDICTION_ALGORITHMS,
        current.algorithm,
        input_fn,
        write,
    )
    return PredictionConfig(algorithm=algorithm)


def prompt_auto_refresh_config(
    current: int | None,
    input_fn: Callable[[str], str],
    write: Callable[[str], None],
) -> int | None:
    write("")
    write("Auto refresh:")
    write("  Blank keeps the current value. Use 0 or off to disable.")
    default_text = "off" if current is None else str(current)
    while True:
        raw = input_fn(f"TUI auto refresh seconds [{default_text}]: ").strip()
        if not raw:
            return current
        try:
            return parse_auto_refresh_seconds(raw, "TUI auto refresh seconds")
        except ValueError as exc:
            write(str(exc))


def prompt_shutdown_config(
    current: float,
    input_fn: Callable[[str], str],
    write: Callable[[str], None],
) -> float:
    write("")
    write("Shutdown:")
    default_text = f"{current:g}"
    while True:
        raw = input_fn(f"Shutdown closing frame seconds [{default_text}]: ").strip()
        if not raw:
            return current
        try:
            return parse_shutdown_seconds(raw, "Shutdown closing frame seconds")
        except ValueError as exc:
            write(str(exc))


def prompt_token_limit(
    title: str,
    default: int | None,
    input_fn: Callable[[str], str],
    write: Callable[[str], None],
) -> int | None:
    default_text = "disabled" if default is None else str(default)
    while True:
        raw = input_fn(f"{title} [{default_text}]: ").strip()
        if not raw:
            return default
        try:
            return parse_token_limit(raw, title)
        except ValueError as exc:
            write(str(exc))


def prompt_rate(
    title: str,
    default: float | None,
    input_fn: Callable[[str], str],
    write: Callable[[str], None],
) -> float:
    suffix = f" [{default:g}]" if default is not None else ""
    while True:
        raw = input_fn(f"{title}{suffix}: ").strip()
        if not raw and default is not None:
            return default
        try:
            return parse_rate(raw, title)
        except ValueError as exc:
            write(str(exc))


def prompt_optional_rate(
    title: str,
    default: float | None,
    input_fn: Callable[[str], str],
    write: Callable[[str], None],
) -> float | None:
    default_text = "-" if default is None else f"{default:g}"
    while True:
        raw = input_fn(f"{title} [{default_text}; '-' uses input rate]: ").strip()
        if not raw:
            return default
        if raw == "-":
            return None
        try:
            return parse_rate(raw, title)
        except ValueError as exc:
            write(str(exc))


def prompt_model_column_width(
    default: int | None,
    input_fn: Callable[[str], str],
    write: Callable[[str], None],
) -> int | None:
    default_text = "auto" if default is None else str(default)
    while True:
        raw = input_fn(
            f"Model column width, 8..40 or auto [{default_text}]: "
        ).strip().lower()
        if not raw:
            return default
        if raw == "auto":
            return None
        try:
            width = parse_model_column_width(raw)
        except ValueError as exc:
            write(str(exc))
            continue
        return width
