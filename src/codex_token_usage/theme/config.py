from __future__ import annotations

import json
import os
from dataclasses import replace
from pathlib import Path

from ..forecast import PREDICTION_ALGORITHMS, LimitConfig, PredictionConfig
from ..keybindings import KeybindingConfig, parse_keybindings_config
from ..pricing import ModelPrice, PricingConfig, normalize_model_name
from .models import (
    CONFIG_DIRNAME,
    CONFIG_FILENAME,
    CONFIG_VERSION,
    COLOR_MODES,
    DEFAULT_SHUTDOWN_SECONDS,
    DisplayConfig,
    PLAIN_THEME_NAMES,
    ThemeConfig,
    ThemeLoadResult,
)
from .presets import DEFAULT_THEME_PRESET, PRESETS

def default_config_path() -> Path:
    config_home = os.environ.get("XDG_CONFIG_HOME")
    if config_home:
        root = Path(config_home).expanduser()
    else:
        root = Path.home() / ".config"
    return root / CONFIG_DIRNAME / CONFIG_FILENAME


def load_theme_config(path: Path | None = None) -> ThemeLoadResult:
    config_path = path or default_config_path()
    if not config_path.exists():
        return ThemeLoadResult(config=ThemeConfig(), path=config_path)

    try:
        raw = json.loads(config_path.read_text(encoding="utf-8"))
        config = parse_theme_config(raw)
        display = parse_display_config(raw)
        pricing = parse_pricing_config(raw)
        limits = parse_limit_config(raw)
        prediction = parse_prediction_config(raw)
        auto_refresh_seconds = parse_auto_refresh_config(raw)
        shutdown_seconds = parse_shutdown_config(raw)
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        return ThemeLoadResult(
            config=ThemeConfig(),
            path=config_path,
            status=f"theme config ignored: {exc}",
        )
    status = ""
    try:
        keybindings = parse_keybindings_config(raw)
    except ValueError as exc:
        keybindings = KeybindingConfig()
        status = f"keybindings ignored: {exc}"
    return ThemeLoadResult(
        config=config,
        path=config_path,
        status=status,
        display=display,
        pricing=pricing,
        keybindings=keybindings,
        limits=limits,
        prediction=prediction,
        auto_refresh_seconds=auto_refresh_seconds,
        shutdown_seconds=shutdown_seconds,
    )


def parse_theme_config(raw: object) -> ThemeConfig:
    if not isinstance(raw, dict):
        raise ValueError("config must be a JSON object")

    theme = raw.get("theme", {})
    if not isinstance(theme, dict):
        raise ValueError("theme must be a JSON object")

    enabled = bool(theme.get("enabled", False))
    preset = str(theme.get("preset") or DEFAULT_THEME_PRESET)
    color_mode = str(theme.get("color_mode", "8bit"))
    lightness = float(theme.get("lightness", 1.0))
    show_accent_line = parse_bool(theme.get("show_accent_line", True))
    themed_bars = parse_bool(theme.get("themed_bars", True))

    if preset not in PRESETS:
        raise ValueError(f"unknown theme preset: {preset}")
    if color_mode not in COLOR_MODES:
        raise ValueError(f"unknown theme color_mode: {color_mode}")
    validate_lightness(lightness)

    return ThemeConfig(
        enabled=enabled,
        preset=preset,
        color_mode=color_mode,
        lightness=lightness,
        show_accent_line=show_accent_line,
        themed_bars=themed_bars,
    )


def parse_display_config(raw: object) -> DisplayConfig:
    if not isinstance(raw, dict):
        raise ValueError("config must be a JSON object")

    display = raw.get("display", {})
    if not isinstance(display, dict):
        raise ValueError("display must be a JSON object")

    return DisplayConfig(
        show_cached_tokens=parse_bool(display.get("show_cached_tokens", True)),
        show_cached_percent=parse_bool(display.get("show_cached_percent", True)),
        show_estimated_cost=parse_bool(display.get("show_estimated_cost", False)),
        show_reasoning_level=parse_bool(display.get("show_reasoning_level", True)),
        show_cache_miss=parse_bool(display.get("show_cache_miss", True)),
        show_reasoning_tokens=parse_bool(display.get("show_reasoning_tokens", True)),
        show_model=parse_bool(display.get("show_model", True)),
        show_context=parse_bool(display.get("show_context", True)),
        model_column_width=parse_model_column_width(
            display.get("model_column_width"),
        ),
    )


def parse_pricing_config(raw: object) -> PricingConfig:
    if not isinstance(raw, dict):
        raise ValueError("config must be a JSON object")

    pricing = raw.get("pricing", {})
    if not isinstance(pricing, dict):
        raise ValueError("pricing must be a JSON object")

    raw_prices = pricing.get("model_prices", {})
    if not isinstance(raw_prices, dict):
        raise ValueError("pricing.model_prices must be a JSON object")

    model_prices: list[tuple[str, ModelPrice]] = []
    for raw_model, raw_price in raw_prices.items():
        if not isinstance(raw_price, dict):
            raise ValueError(f"pricing for {raw_model!r} must be a JSON object")
        model = normalize_model_name(str(raw_model))
        input_rate = parse_rate(raw_price.get("input_per_million"), "input_per_million")
        output_rate = parse_rate(
            raw_price.get("output_per_million"),
            "output_per_million",
        )
        cached_value = raw_price.get("cached_input_per_million")
        cached_rate = None if cached_value in (None, "", "-") else parse_rate(
            cached_value,
            "cached_input_per_million",
        )
        model_prices.append(
            (
                model,
                ModelPrice(
                    input_per_million=input_rate,
                    cached_input_per_million=cached_rate,
                    output_per_million=output_rate,
                ),
            )
        )
    return PricingConfig(model_prices=tuple(sorted(model_prices)))


def parse_limit_config(raw: object) -> LimitConfig:
    if not isinstance(raw, dict):
        raise ValueError("config must be a JSON object")

    limits = raw.get("limits", {})
    if not isinstance(limits, dict):
        raise ValueError("limits must be a JSON object")

    return LimitConfig(
        five_hour_tokens=parse_token_limit(
            limits.get("five_hour_tokens"),
            "limits.five_hour_tokens",
        ),
        weekly_tokens=parse_token_limit(
            limits.get("weekly_tokens"),
            "limits.weekly_tokens",
        ),
    )


def parse_prediction_config(raw: object) -> PredictionConfig:
    if not isinstance(raw, dict):
        raise ValueError("config must be a JSON object")

    prediction = raw.get("prediction", {})
    if not isinstance(prediction, dict):
        raise ValueError("prediction must be a JSON object")

    algorithm = str(prediction.get("algorithm") or "recent_rate")
    if algorithm not in PREDICTION_ALGORITHMS:
        choices = ", ".join(PREDICTION_ALGORITHMS)
        raise ValueError(f"prediction.algorithm must be one of: {choices}")
    return PredictionConfig(algorithm=algorithm)


def parse_auto_refresh_config(raw: object) -> int | None:
    if not isinstance(raw, dict):
        raise ValueError("config must be a JSON object")

    misc = raw.get("misc", {})
    if not isinstance(misc, dict):
        raise ValueError("misc must be a JSON object")
    return parse_auto_refresh_seconds(
        misc.get("auto_refresh_seconds"),
        "misc.auto_refresh_seconds",
    )


def parse_shutdown_config(raw: object) -> float:
    if not isinstance(raw, dict):
        raise ValueError("config must be a JSON object")

    misc = raw.get("misc", {})
    if not isinstance(misc, dict):
        raise ValueError("misc must be a JSON object")
    return parse_shutdown_seconds(
        misc.get("shutdown_seconds", DEFAULT_SHUTDOWN_SECONDS),
        "misc.shutdown_seconds",
    )


def save_theme_config(
    config: ThemeConfig,
    path: Path | None = None,
    display: DisplayConfig | None = None,
    pricing: PricingConfig | None = None,
    keybindings: KeybindingConfig | None = None,
    limits: LimitConfig | None = None,
    prediction: PredictionConfig | None = None,
    auto_refresh_seconds: int | None = None,
    shutdown_seconds: float = DEFAULT_SHUTDOWN_SECONDS,
) -> Path:
    config_path = path or default_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    display_config = display or DisplayConfig()
    pricing_config = pricing or PricingConfig()
    keybinding_config = keybindings or KeybindingConfig()
    limit_config = limits or LimitConfig()
    prediction_config = prediction or PredictionConfig()
    refresh_seconds = parse_auto_refresh_seconds(
        auto_refresh_seconds,
        "misc.auto_refresh_seconds",
    )
    parsed_shutdown_seconds = parse_shutdown_seconds(
        shutdown_seconds,
        "misc.shutdown_seconds",
    )
    payload = {
        "version": CONFIG_VERSION,
        "theme": {
            "enabled": config.enabled,
            "preset": config.preset,
            "color_mode": config.color_mode,
            "lightness": config.lightness,
            "show_accent_line": config.show_accent_line,
            "themed_bars": config.themed_bars,
        },
        "display": {
            "model_column_width": display_config.model_column_width,
            "show_cache_miss": display_config.show_cache_miss,
            "show_cached_tokens": display_config.show_cached_tokens,
            "show_cached_percent": display_config.show_cached_percent,
            "show_context": display_config.show_context,
            "show_estimated_cost": display_config.show_estimated_cost,
            "show_model": display_config.show_model,
            "show_reasoning_level": display_config.show_reasoning_level,
            "show_reasoning_tokens": display_config.show_reasoning_tokens,
        },
        "pricing": {
            "model_prices": {
                model: {
                    "cached_input_per_million": price.cached_input_per_million,
                    "input_per_million": price.input_per_million,
                    "output_per_million": price.output_per_million,
                }
                for model, price in pricing_config.model_prices
            },
        },
        "limits": {
            "five_hour_tokens": limit_config.five_hour_tokens,
            "weekly_tokens": limit_config.weekly_tokens,
        },
        "prediction": {
            "algorithm": prediction_config.algorithm,
        },
        "misc": {
            "auto_refresh_seconds": refresh_seconds,
            "shutdown_seconds": parsed_shutdown_seconds,
        },
        "keybindings": {
            action: list(labels)
            for action, labels in keybinding_config.as_dict().items()
        },
    }
    config_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return config_path


def apply_theme_overrides(
    config: ThemeConfig,
    preset: str | None = None,
    lightness: float | None = None,
) -> ThemeConfig:
    next_config = config
    if preset:
        if preset in PLAIN_THEME_NAMES:
            next_config = replace(next_config, enabled=False)
        elif preset in PRESETS:
            next_config = replace(next_config, enabled=True, preset=preset)
        else:
            raise ValueError(f"unknown theme preset: {preset}")
    if lightness is not None:
        validate_lightness(lightness)
        next_config = replace(next_config, lightness=lightness)
    return next_config


def parse_lightness(value: str) -> float:
    try:
        lightness = float(value)
    except ValueError as exc:
        raise ValueError("lightness must be a number from 0 to 1") from exc
    validate_lightness(lightness)
    return lightness


def validate_lightness(value: float) -> None:
    if value < 0 or value > 1:
        raise ValueError("lightness must be from 0 to 1")


def parse_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in ("1", "true", "yes", "y", "on"):
            return True
        if normalized in ("0", "false", "no", "n", "off"):
            return False
    return bool(value)


def parse_rate(value: object, name: str) -> float:
    try:
        rate = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a number") from exc
    if rate < 0:
        raise ValueError(f"{name} must not be negative")
    return rate


def parse_token_limit(value: object, name: str = "token limit") -> int | None:
    if isinstance(value, str):
        value = value.strip()
        if value.lower() in ("", "-", "none"):
            return None
    if value is None:
        return None
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a whole number")
    if isinstance(value, float) and not value.is_integer():
        raise ValueError(f"{name} must be a whole number")
    try:
        limit = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a whole number") from exc
    if limit < 0:
        raise ValueError(f"{name} must not be negative")
    if limit == 0:
        return None
    return limit


def parse_auto_refresh_seconds(
    value: object,
    name: str = "auto refresh seconds",
) -> int | None:
    if isinstance(value, str):
        value = value.strip()
        if value.lower() in ("", "-", "none", "off", "disabled"):
            return None
    if value is None:
        return None
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a whole number of seconds")
    if isinstance(value, float) and not value.is_integer():
        raise ValueError(f"{name} must be a whole number of seconds")
    try:
        seconds = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a whole number of seconds") from exc
    if seconds < 0:
        raise ValueError(f"{name} must not be negative")
    if seconds == 0:
        return None
    return seconds


def parse_shutdown_seconds(
    value: object,
    name: str = "shutdown seconds",
) -> float:
    if isinstance(value, str):
        value = value.strip()
        if value == "":
            return DEFAULT_SHUTDOWN_SECONDS
    if value is None:
        return DEFAULT_SHUTDOWN_SECONDS
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a positive number of seconds")
    try:
        seconds = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a positive number of seconds") from exc
    if seconds <= 0:
        raise ValueError(f"{name} must be positive")
    return seconds


def parse_model_column_width(value: object) -> int | None:
    if value in (None, "", "auto"):
        return None
    try:
        width = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("display.model_column_width must be auto or an integer") from exc
    validate_model_column_width(width)
    return width


def validate_model_column_width(width: int) -> None:
    if width < 8 or width > 40:
        raise ValueError("display.model_column_width must be from 8 to 40")
