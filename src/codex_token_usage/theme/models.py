from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..forecast import LimitConfig, PredictionConfig
from ..keybindings import KeybindingConfig
from ..pricing import PricingConfig
from .presets import DEFAULT_THEME_PRESET, RGB

CONFIG_VERSION = 1
CONFIG_DIRNAME = "codex-token-usage"
CONFIG_FILENAME = "config.json"
COLOR_POLICIES = ("auto", "always", "never")
COLOR_MODES = ("8bit", "rgb")
PLAIN_THEME_NAMES = ("plain", "disabled", "none")
DEFAULT_SHUTDOWN_SECONDS = 2.45

@dataclass(frozen=True)
class ThemeConfig:
    enabled: bool = False
    preset: str = DEFAULT_THEME_PRESET
    color_mode: str = "8bit"
    lightness: float = 1.0
    show_accent_line: bool = True
    themed_bars: bool = True


@dataclass(frozen=True)
class DisplayConfig:
    show_cached_tokens: bool = True
    show_cached_percent: bool = True
    show_estimated_cost: bool = False
    show_reasoning_level: bool = True
    show_cache_miss: bool = True
    show_reasoning_tokens: bool = True
    show_model: bool = True
    show_context: bool = True
    model_column_width: int | None = None


@dataclass(frozen=True)
class ThemeLoadResult:
    config: ThemeConfig
    path: Path
    status: str = ""
    display: DisplayConfig = DisplayConfig()
    pricing: PricingConfig = PricingConfig()
    keybindings: KeybindingConfig = KeybindingConfig()
    limits: LimitConfig = LimitConfig()
    prediction: PredictionConfig = PredictionConfig()
    auto_refresh_seconds: int | None = None
    shutdown_seconds: float = DEFAULT_SHUTDOWN_SECONDS


@dataclass(frozen=True)
class BarSegment:
    text: str
    color_index: int | None = None
    rgb: RGB | None = None
