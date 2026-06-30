from __future__ import annotations

from dataclasses import replace
from textwrap import wrap

from .. import __version__
from ..forecast import PREDICTION_ALGORITHMS, LimitConfig, PredictionConfig
from ..keybindings import KEYBINDING_ACTION_LABELS, KeybindingConfig
from ..models import UsageDataset
from ..pricing import MODEL_PRICES, ModelPrice, normalize_model_name
from ..theme import (
    COLOR_MODES,
    DEFAULT_SHUTDOWN_SECONDS,
    DEFAULT_THEME_PRESET,
    DisplayConfig,
    PRESET_NAMES,
    ThemeConfig,
    parse_auto_refresh_seconds,
    parse_shutdown_seconds,
)

RATE_FIELDS = ("input", "cached", "output")
THEME_PRESET_CHOICES = ("plain", *PRESET_NAMES)
SETTINGS_TABS = (
    "Model Pricing",
    "Display Columns",
    "Appearance",
    "Keybindings",
    "Misc",
)
DISPLAY_SETTING_FIELDS = (
    "cached_tokens",
    "cached_percent",
    "estimated_cost",
    "reasoning_level",
    "cache_miss",
    "reasoning_tokens",
    "model",
    "context",
    "model_width",
)
APPEARANCE_SETTING_FIELDS = (
    "flag",
    "color",
    "light",
    "accent_line",
    "themed_bars",
)
MISC_SETTING_FIELDS = (
    "prediction_algorithm",
    "auto_refresh_seconds",
    "shutdown_seconds",
    "about",
    "reset_setup",
)
FLAG_PICKER_COLUMNS = 4
FLAG_PICKER_TOP = 5
FLAG_PICKER_PREVIEW_HEIGHT = 5
APPEARANCE_PREVIEW_BLOCK_HEIGHT = 5

def settings_snapshot(
    theme: ThemeConfig,
    display: DisplayConfig,
    custom_prices: dict[str, ModelPrice],
    keybindings: KeybindingConfig,
    limits: LimitConfig,
    prediction: PredictionConfig,
    auto_refresh_seconds: int | None,
    shutdown_seconds: float,
) -> tuple[object, ...]:
    return (
        theme,
        display,
        tuple(sorted(custom_prices.items())),
        keybindings,
        limits,
        prediction,
        auto_refresh_seconds,
        shutdown_seconds,
    )


def default_setup_values() -> tuple[
    ThemeConfig,
    DisplayConfig,
    dict[str, ModelPrice],
    KeybindingConfig,
    LimitConfig,
    PredictionConfig,
    int | None,
    float,
]:
    return (
        ThemeConfig(),
        DisplayConfig(),
        {},
        KeybindingConfig(),
        LimitConfig(),
        PredictionConfig(),
        None,
        DEFAULT_SHUTDOWN_SECONDS,
    )


def settings_model_names(
    dataset: UsageDataset,
    custom_prices: dict[str, ModelPrice],
) -> list[str]:
    names = set(MODEL_PRICES)
    names.update(custom_prices)
    for session in dataset.sessions:
        model = normalize_model_name(session.model)
        if model and model != "(unknown)":
            names.add(model)
    return sorted(names)


def effective_settings_price(
    model: str,
    custom_prices: dict[str, ModelPrice],
) -> ModelPrice | None:
    return custom_prices.get(model) or MODEL_PRICES.get(model)


def settings_price_source(model: str, custom_prices: dict[str, ModelPrice]) -> str:
    if model in custom_prices:
        return "custom"
    if model in MODEL_PRICES:
        return "built-in"
    return "unpriced"


def settings_rate_text(price: ModelPrice | None, field: str) -> str:
    if price is None:
        return "n/a"
    if field == "input":
        return format_settings_rate(price.input_per_million)
    if field == "cached":
        if price.cached_input_per_million is None:
            return "-"
        return format_settings_rate(price.cached_input_per_million)
    if field == "output":
        return format_settings_rate(price.output_per_million)
    return "n/a"


def display_setting_label(field: str) -> str:
    labels = {
        "cached_tokens": "cached tokens",
        "cached_percent": "cached %",
        "estimated_cost": "estimated cost",
        "reasoning_level": "reasoning level",
        "cache_miss": "cache miss",
        "reasoning_tokens": "reasoning tokens",
        "model": "model",
        "context": "cwd/title",
        "model_width": "model width",
    }
    return labels.get(field, field)


def appearance_setting_label(field: str) -> str:
    labels = {
        "flag": "flag preset",
        "color": "color mode",
        "light": "lightness",
        "accent_line": "accent line",
        "themed_bars": "themed usage bars",
    }
    return labels.get(field, field)


def misc_setting_label(field: str) -> str:
    labels = {
        "prediction_algorithm": "prediction algorithm",
        "auto_refresh_seconds": "auto refresh",
        "shutdown_seconds": "shutdown time",
        "about": "about",
        "reset_setup": "reset all setup",
    }
    return labels.get(field, field)


def cycle_prediction_algorithm(prediction: PredictionConfig) -> PredictionConfig:
    try:
        index = PREDICTION_ALGORITHMS.index(prediction.algorithm)
    except ValueError:
        index = 0
    algorithm = PREDICTION_ALGORITHMS[(index + 1) % len(PREDICTION_ALGORITHMS)]
    return PredictionConfig(algorithm=algorithm)


def prediction_algorithm_label(algorithm: str) -> str:
    labels = {
        "recent_rate": "recent rate",
        "previous_period": "previous period",
    }
    return labels.get(algorithm, algorithm.replace("_", " "))


def auto_refresh_label(seconds: int | None) -> str:
    if seconds is None:
        return "off"
    unit = "second" if seconds == 1 else "seconds"
    return f"{seconds} {unit}"


def auto_refresh_input_value(seconds: int | None) -> str:
    return "0" if seconds is None else str(seconds)


def shutdown_seconds_label(seconds: float) -> str:
    value = f"{seconds:g}"
    unit = "second" if seconds == 1 else "seconds"
    return f"{value} {unit}"


def shutdown_seconds_input_value(seconds: float) -> str:
    return f"{seconds:g}"


def parse_settings_auto_refresh_seconds(value: str) -> int | None | str:
    try:
        return parse_auto_refresh_seconds(value, "auto refresh")
    except ValueError as exc:
        return str(exc)


def parse_settings_shutdown_seconds(value: str) -> float | str:
    try:
        return parse_shutdown_seconds(value, "shutdown time")
    except ValueError as exc:
        return str(exc)


def keybinding_action_label(action: str) -> str:
    return KEYBINDING_ACTION_LABELS.get(action, action.replace("_", " "))


def format_settings_rate(value: float) -> str:
    return f"{value:g}"


def parse_settings_rate(value: str) -> float | str:
    try:
        rate = float(value)
    except ValueError:
        return "rate must be a number"
    if rate < 0:
        return "rate must not be negative"
    return rate


def parse_settings_model_width(value: str) -> int | None | str:
    value = value.strip().lower()
    if value in ("", "auto"):
        return None
    try:
        width = int(value)
    except ValueError:
        return "model width must be auto or an integer"
    if width < 8 or width > 40:
        return "model width must be from 8 to 40"
    return width


def theme_preset_label(theme: ThemeConfig) -> str:
    return theme.preset if theme.enabled else "plain"


def theme_current_preset(theme: ThemeConfig) -> str:
    if theme.preset in PRESET_NAMES:
        return theme.preset
    return DEFAULT_THEME_PRESET


def theme_current_preset_label(theme: ThemeConfig) -> str:
    preset = theme_current_preset(theme)
    return preset if theme.enabled else f"{preset} (plain)"


def flag_display_name(preset: str) -> str:
    names = {
        "all": "all communities",
        "trans": "transgender",
    }
    name = names.get(preset, preset)
    return name.replace(".", " ").replace("-", " ")


def pride_community_message(theme: ThemeConfig) -> str:
    return pride_message_for_preset(theme_current_preset(theme))


ABOUT_DESCRIPTION = (
    "A local terminal application for inspecting Codex CLI token usage, forecasts, "
    "pricing estimates, sessions, models, and project folders from your local "
    "Codex data."
)
OFFBOARD_MESSAGE = (
    "Thank you for using Codex Token Usage. Keep building with care, and keep "
    "being yourself."
)


def about_content_lines(theme: ThemeConfig, width: int) -> tuple[str, ...]:
    content = [
        "About",
        "Codex Token Usage",
        f"Version {__version__}",
    ]
    for paragraph in (ABOUT_DESCRIPTION, pride_community_message(theme)):
        content.extend(wrap_text(paragraph, width))
    return tuple(content)


def wrap_text(text: str, width: int) -> list[str]:
    if width <= 0:
        return [""]
    return wrap(text, width=width) or [""]


def farewell_content_lines(theme: ThemeConfig, width: int) -> tuple[str, ...]:
    community = flag_display_name(theme_current_preset(theme))
    content = ["Bye bye", f"From the {community} flag."]
    content.extend(wrap_text(OFFBOARD_MESSAGE, width))
    return tuple(content)


def farewell_flag_height(
    terminal_height: int,
    line_count: int,
    palette: tuple[RGB, ...],
) -> int:
    if not palette:
        return 0
    available = terminal_height - line_count - 5
    if available <= 0:
        return 0
    return min(len(palette), max(1, available))


def farewell_frame_delay(shutdown_seconds: float) -> int:
    return max(1, round(shutdown_seconds * 1000))


def pride_message_for_preset(preset: str) -> str:
    if preset == "all":
        return (
            "Pride: every community in this app belongs here; "
            "be yourself and be proud to be there."
        )
    community = flag_display_name(preset)
    return (
        f"Pride: {community} community, you belong here; "
        "be yourself and be proud to be there."
    )


def pride_messages_for_presets(presets: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(pride_message_for_preset(preset) for preset in presets)


def flag_picker_block_height(terminal_height: int) -> int:
    if terminal_height >= 22:
        return FLAG_PICKER_PREVIEW_HEIGHT
    if terminal_height >= 18:
        return 4
    return 3


def flag_picker_visible_rows(terminal_height: int) -> int:
    block_height = flag_picker_block_height(terminal_height)
    row_height = block_height + 3
    available = max(0, terminal_height - FLAG_PICKER_TOP - 1)
    return max(1, min(2, available // row_height))


def flag_picker_page_size(terminal_height: int) -> int:
    return FLAG_PICKER_COLUMNS * flag_picker_visible_rows(terminal_height)


def appearance_preview_block_height(terminal_height: int, preview_y: int) -> int:
    block_start = preview_y + 2
    available = terminal_height - 2 - block_start
    return max(0, min(APPEARANCE_PREVIEW_BLOCK_HEIGHT, available))


def cycle_theme_preset(theme: ThemeConfig) -> ThemeConfig:
    current = theme_preset_label(theme)
    index = THEME_PRESET_CHOICES.index(current)
    next_preset = THEME_PRESET_CHOICES[(index + 1) % len(THEME_PRESET_CHOICES)]
    if next_preset == "plain":
        return replace(theme, enabled=False)
    return replace(theme, enabled=True, preset=next_preset)


def cycle_theme_color_mode(theme: ThemeConfig) -> ThemeConfig:
    index = COLOR_MODES.index(theme.color_mode)
    return replace(theme, color_mode=COLOR_MODES[(index + 1) % len(COLOR_MODES)])


def parse_settings_lightness(value: str) -> float | str:
    try:
        lightness = float(value)
    except ValueError:
        return "lightness must be a number from 0 to 1"
    if lightness < 0 or lightness > 1:
        return "lightness must be from 0 to 1"
    return lightness
