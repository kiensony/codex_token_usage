from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, replace
from importlib.resources import files
from pathlib import Path
from typing import Callable, TextIO

from .keybindings import KeybindingConfig, parse_keybindings_config
from .pricing import MODEL_PRICES, ModelPrice, PricingConfig, normalize_model_name

CONFIG_VERSION = 1
CONFIG_DIRNAME = "codex-token-usage"
CONFIG_FILENAME = "config.json"
COLOR_POLICIES = ("auto", "always", "never")
COLOR_MODES = ("8bit", "rgb")
PLAIN_THEME_NAMES = ("plain", "disabled", "none")

RGB = tuple[int, int, int]


def parse_hex_color(value: str) -> RGB:
    text = value.removeprefix("#")
    if len(text) != 6:
        raise ValueError(f"invalid color: {value}")
    return (
        int(text[0:2], 16),
        int(text[2:4], 16),
        int(text[4:6], 16),
    )


def load_flag_presets() -> dict[str, tuple[RGB, ...]]:
    try:
        raw = json.loads(
            files(__package__).joinpath("flag_presets.json").read_text("utf-8")
        )
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return {}

    presets: dict[str, tuple[RGB, ...]] = {}
    for name, value in raw.items():
        colors = value.get("colors") if isinstance(value, dict) else value
        if not isinstance(colors, list):
            continue
        try:
            presets[str(name)] = tuple(parse_hex_color(str(color)) for color in colors)
        except ValueError:
            continue
    return presets

PRESETS: dict[str, tuple[RGB, ...]] = {
    "rainbow": (
        (228, 3, 3),
        (255, 140, 0),
        (255, 237, 0),
        (0, 128, 38),
        (0, 77, 255),
        (117, 7, 135),
    ),
    "progress": (
        (0, 0, 0),
        (120, 79, 23),
        (228, 3, 3),
        (255, 140, 0),
        (255, 237, 0),
        (0, 128, 38),
        (0, 77, 255),
        (117, 7, 135),
        (91, 206, 250),
        (245, 169, 184),
        (255, 255, 255),
    ),
    "trans": (
        (91, 206, 250),
        (245, 169, 184),
        (255, 255, 255),
        (245, 169, 184),
        (91, 206, 250),
    ),
    "bisexual": (
        (214, 2, 112),
        (155, 79, 150),
        (0, 56, 168),
    ),
    "pansexual": (
        (255, 33, 140),
        (255, 216, 0),
        (33, 177, 255),
    ),
    "polysexual": (
        (246, 28, 135),
        (7, 214, 105),
        (28, 146, 246),
    ),
    "omnisexual": (
        (254, 155, 203),
        (255, 83, 173),
        (32, 31, 66),
        (103, 79, 163),
        (139, 184, 232),
    ),
    "omniromantic": (
        (255, 156, 203),
        (255, 221, 238),
        (32, 31, 66),
        (190, 224, 255),
        (128, 179, 255),
    ),
    "genderfluid": (
        (255, 117, 162),
        (255, 255, 255),
        (190, 24, 214),
        (0, 0, 0),
        (51, 62, 189),
    ),
    "lesbian": (
        (213, 45, 0),
        (239, 118, 39),
        (255, 255, 255),
        (209, 98, 164),
        (163, 2, 98),
    ),
    "gay-men": (
        (7, 141, 112),
        (38, 206, 170),
        (152, 232, 193),
        (255, 255, 255),
        (123, 173, 226),
        (80, 73, 204),
        (61, 26, 120),
    ),
    "nonbinary": (
        (255, 244, 48),
        (255, 255, 255),
        (156, 89, 209),
        (0, 0, 0),
    ),
    "agender": (
        (0, 0, 0),
        (188, 188, 188),
        (255, 255, 255),
        (184, 244, 131),
        (255, 255, 255),
        (188, 188, 188),
        (0, 0, 0),
    ),
    "xenogender": (
        (255, 102, 153),
        (255, 153, 51),
        (255, 255, 255),
        (102, 204, 255),
        (153, 102, 204),
    ),
    "queer": (
        (0, 0, 0),
        (153, 51, 153),
        (255, 255, 255),
        (0, 153, 102),
        (0, 0, 0),
    ),
    "abrosexual": (
        (117, 222, 141),
        (176, 238, 188),
        (255, 255, 255),
        (240, 160, 198),
        (224, 33, 138),
    ),
    "asexual": (
        (0, 0, 0),
        (163, 163, 163),
        (255, 255, 255),
        (128, 0, 128),
    ),
}
_HYFETCH_PRESETS = load_flag_presets()
if _HYFETCH_PRESETS:
    for name, colors in PRESETS.items():
        _HYFETCH_PRESETS.setdefault(name, colors)
    PRESETS = _HYFETCH_PRESETS
for alias, target in {
    "trans": "transgender",
    "nonhuman-unit": "nonhuman-unity",
    "ynullflux": "nullflux",
}.items():
    if target in PRESETS:
        PRESETS[alias] = PRESETS[target]
PRESETS["all"] = tuple(color for colors in tuple(PRESETS.values()) for color in colors)

PRESET_NAMES = tuple(PRESETS)
DEFAULT_THEME_PRESET = "femboy" if "femboy" in PRESETS else "rainbow"


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


@dataclass(frozen=True)
class BarSegment:
    text: str
    color_index: int | None = None
    rgb: RGB | None = None


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


def save_theme_config(
    config: ThemeConfig,
    path: Path | None = None,
    display: DisplayConfig | None = None,
    pricing: PricingConfig | None = None,
    keybindings: KeybindingConfig | None = None,
) -> Path:
    config_path = path or default_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    display_config = display or DisplayConfig()
    pricing_config = pricing or PricingConfig()
    keybinding_config = keybindings or KeybindingConfig()
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


def theme_palette(config: ThemeConfig) -> tuple[RGB, ...]:
    if not config.enabled:
        return ()
    colors = PRESETS.get(config.preset)
    if not colors:
        return ()
    return tuple(adjust_lightness(color, config.lightness) for color in colors)


def adjust_lightness(rgb: RGB, lightness: float) -> RGB:
    validate_lightness(lightness)
    return tuple(max(0, min(255, round(channel * lightness))) for channel in rgb)  # type: ignore[return-value]


def filled_bar_width(value: int, max_value: int, width: int) -> int:
    if width <= 0 or max_value <= 0 or value <= 0:
        return 0
    return min(width, max(1, round((value / max_value) * width)))


def plain_bar(
    value: int,
    max_value: int,
    width: int,
    fill_char: str = "#",
    empty_char: str = ".",
) -> str:
    filled = filled_bar_width(value, max_value, width)
    return fill_char * filled + empty_char * max(0, width - filled)


def themed_bar_segments(
    value: int,
    max_value: int,
    width: int,
    config: ThemeConfig,
    fill_char: str = "#",
    empty_char: str = ".",
) -> list[BarSegment]:
    if width <= 0:
        return []

    filled = filled_bar_width(value, max_value, width)
    palette = theme_palette(config)
    if not palette or filled <= 0:
        return [
            BarSegment(
                plain_bar(
                    value,
                    max_value,
                    width,
                    fill_char=fill_char,
                    empty_char=empty_char,
                )
            )
        ]

    segments: list[BarSegment] = []
    current_color_index: int | None = None
    current_rgb: RGB | None = None
    current_text: list[str] = []

    for index in range(filled):
        color_index = min(len(palette) - 1, (index * len(palette)) // filled)
        rgb = palette[color_index]
        if current_color_index is None:
            current_color_index = color_index
            current_rgb = rgb
        if color_index != current_color_index:
            segments.append(
                BarSegment(
                    text="".join(current_text),
                    color_index=current_color_index,
                    rgb=current_rgb,
                )
            )
            current_text = []
            current_color_index = color_index
            current_rgb = rgb
        current_text.append(fill_char)

    if current_text and current_color_index is not None:
        segments.append(
            BarSegment(
                text="".join(current_text),
                color_index=current_color_index,
                rgb=current_rgb,
            )
        )

    empty_width = width - filled
    if empty_width > 0:
        segments.append(BarSegment(empty_char * empty_width))
    return segments


def themed_ansi_bar(
    value: int,
    max_value: int,
    width: int,
    config: ThemeConfig,
    fill_char: str = "#",
    empty_char: str = " ",
) -> str:
    parts = []
    for segment in themed_bar_segments(
        value,
        max_value,
        width,
        config,
        fill_char=fill_char,
        empty_char=empty_char,
    ):
        if segment.rgb is None:
            parts.append(segment.text)
        else:
            parts.append(ansi_wrap(segment.text, segment.rgb, config.color_mode))
    return "".join(parts)


def ansi_wrap(text: str, rgb: RGB, color_mode: str = "8bit") -> str:
    if not text:
        return text
    if color_mode == "rgb":
        r, g, b = rgb
        return f"\x1b[38;2;{r};{g};{b}m{text}\x1b[0m"
    color = rgb_to_ansi256(rgb)
    return f"\x1b[38;5;{color}m{text}\x1b[0m"


def rgb_to_ansi256(rgb: RGB) -> int:
    r, g, b = rgb
    if r == g == b:
        if r < 8:
            return 16
        if r > 248:
            return 231
        return round(((r - 8) / 247) * 24) + 232
    red = round((r / 255) * 5)
    green = round((g / 255) * 5)
    blue = round((b / 255) * 5)
    return 16 + 36 * red + 6 * green + blue


def rgb_to_basic_color(rgb: RGB) -> int:
    candidates = (
        (0, (0, 0, 0)),
        (1, (205, 0, 0)),
        (2, (0, 205, 0)),
        (3, (205, 205, 0)),
        (4, (0, 0, 238)),
        (5, (205, 0, 205)),
        (6, (0, 205, 205)),
        (7, (229, 229, 229)),
    )
    return min(
        candidates,
        key=lambda item: sum((channel - target) ** 2 for channel, target in zip(rgb, item[1])),
    )[0]


def should_use_ansi_color(policy: str, stream: TextIO = sys.stdout) -> bool:
    if policy == "always":
        return True
    if policy == "never":
        return False
    return bool(getattr(stream, "isatty", lambda: False)())


def preview_theme(config: ThemeConfig, width: int = 36) -> str:
    if not config.enabled:
        return "plain: " + plain_bar(1, 1, width)
    return f"{config.preset}: " + themed_ansi_bar(1, 1, width, config)


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
