from __future__ import annotations

import curses
from dataclasses import replace

from ..forecast import PredictionConfig
from ..keybindings import (
    KeybindingConfig,
    format_keybinding_labels,
    key_label_for_code,
    update_keybinding,
)
from ..theme import DisplayConfig, ThemeConfig
from .formatting import on_off
from .settings_model import (
    auto_refresh_input_value,
    auto_refresh_label,
    cycle_prediction_algorithm,
    cycle_theme_color_mode,
    format_settings_rate,
    keybinding_action_label,
    parse_settings_auto_refresh_seconds,
    parse_settings_lightness,
    parse_settings_model_width,
    parse_settings_shutdown_seconds,
    prediction_algorithm_label,
    shutdown_seconds_input_value,
    shutdown_seconds_label,
    theme_preset_label,
)


class SettingsActionsMixin:

    def apply_display_setting(
        self,
        display: DisplayConfig,
        field: str,
    ) -> tuple[DisplayConfig, str]:
        if field == "cached_tokens":
            next_display = replace(
                display,
                show_cached_tokens=not display.show_cached_tokens,
            )
            return next_display, f"cached tokens column: {on_off(next_display.show_cached_tokens)}"
        if field == "cached_percent":
            next_display = replace(
                display,
                show_cached_percent=not display.show_cached_percent,
            )
            return next_display, f"cached % column: {on_off(next_display.show_cached_percent)}"
        if field == "estimated_cost":
            next_display = replace(
                display,
                show_estimated_cost=not display.show_estimated_cost,
            )
            return next_display, f"estimated cost column: {on_off(next_display.show_estimated_cost)}"
        if field == "reasoning_level":
            next_display = replace(
                display,
                show_reasoning_level=not display.show_reasoning_level,
            )
            return next_display, f"reasoning level column: {on_off(next_display.show_reasoning_level)}"
        if field == "cache_miss":
            next_display = replace(
                display,
                show_cache_miss=not display.show_cache_miss,
            )
            return next_display, f"cache miss column: {on_off(next_display.show_cache_miss)}"
        if field == "reasoning_tokens":
            next_display = replace(
                display,
                show_reasoning_tokens=not display.show_reasoning_tokens,
            )
            return next_display, f"reasoning tokens column: {on_off(next_display.show_reasoning_tokens)}"
        if field == "model":
            next_display = replace(
                display,
                show_model=not display.show_model,
            )
            return next_display, f"model column: {on_off(next_display.show_model)}"
        if field == "context":
            next_display = replace(
                display,
                show_context=not display.show_context,
            )
            return next_display, f"cwd/title column: {on_off(next_display.show_context)}"

        width_value = self.prompt_input(
            "model column width 8..40 or auto: ",
            "auto" if display.model_column_width is None else str(display.model_column_width),
        )
        if width_value is None:
            return display, "model width unchanged"
        parsed_width = parse_settings_model_width(width_value)
        if isinstance(parsed_width, str):
            return display, parsed_width
        next_display = replace(display, model_column_width=parsed_width)
        status = (
            "model column width: auto"
            if parsed_width is None
            else f"model column width: {parsed_width}"
        )
        return next_display, status

    def apply_appearance_setting(
        self,
        theme: ThemeConfig,
        field: str,
    ) -> tuple[ThemeConfig, str]:
        if field == "flag":
            next_theme = self.choose_flag_preset(theme)
            if next_theme is None:
                return theme, "flag preset unchanged"
            return next_theme, f"flag preset: {theme_preset_label(next_theme)}"
        if field == "color":
            next_theme = cycle_theme_color_mode(theme)
            return next_theme, f"color mode: {next_theme.color_mode}"
        if field == "accent_line":
            next_theme = replace(theme, show_accent_line=not theme.show_accent_line)
            return next_theme, f"accent line: {on_off(next_theme.show_accent_line)}"
        if field == "themed_bars":
            next_theme = replace(theme, themed_bars=not theme.themed_bars)
            return next_theme, f"themed usage bars: {on_off(next_theme.themed_bars)}"

        lightness_value = self.prompt_input(
            "theme lightness 0..1: ",
            format_settings_rate(theme.lightness),
        )
        if lightness_value is None:
            return theme, "theme lightness unchanged"
        parsed_lightness = parse_settings_lightness(lightness_value)
        if isinstance(parsed_lightness, str):
            return theme, parsed_lightness
        next_theme = replace(theme, lightness=parsed_lightness)
        return next_theme, f"theme lightness: {format_settings_rate(parsed_lightness)}"

    def apply_misc_setting(
        self,
        prediction: PredictionConfig,
        auto_refresh_seconds: int | None,
        shutdown_seconds: float,
        field: str,
    ) -> tuple[PredictionConfig, int | None, float, str]:
        if field == "prediction_algorithm":
            next_prediction = cycle_prediction_algorithm(prediction)
            return (
                next_prediction,
                auto_refresh_seconds,
                shutdown_seconds,
                f"prediction algorithm: {prediction_algorithm_label(next_prediction.algorithm)}",
            )
        if field == "auto_refresh_seconds":
            refresh_value = self.prompt_input(
                "auto refresh seconds, 0/off disables: ",
                auto_refresh_input_value(auto_refresh_seconds),
            )
            if refresh_value is None:
                return (
                    prediction,
                    auto_refresh_seconds,
                    shutdown_seconds,
                    "auto refresh unchanged",
                )
            parsed_refresh = parse_settings_auto_refresh_seconds(refresh_value)
            if isinstance(parsed_refresh, str):
                return prediction, auto_refresh_seconds, shutdown_seconds, parsed_refresh
            return (
                prediction,
                parsed_refresh,
                shutdown_seconds,
                f"auto refresh: {auto_refresh_label(parsed_refresh)}",
            )
        if field == "shutdown_seconds":
            shutdown_value = self.prompt_input(
                "shutdown closing frame seconds: ",
                shutdown_seconds_input_value(shutdown_seconds),
            )
            if shutdown_value is None:
                return (
                    prediction,
                    auto_refresh_seconds,
                    shutdown_seconds,
                    "shutdown time unchanged",
                )
            parsed_shutdown = parse_settings_shutdown_seconds(shutdown_value)
            if isinstance(parsed_shutdown, str):
                return (
                    prediction,
                    auto_refresh_seconds,
                    shutdown_seconds,
                    parsed_shutdown,
                )
            return (
                prediction,
                auto_refresh_seconds,
                parsed_shutdown,
                f"shutdown time: {shutdown_seconds_label(parsed_shutdown)}",
            )
        if field == "about":
            self.show_about_dialog()
            return prediction, auto_refresh_seconds, shutdown_seconds, "about shown"
        return prediction, auto_refresh_seconds, shutdown_seconds, "unknown misc setting"

    def apply_keybinding_setting(
        self,
        keybindings: KeybindingConfig,
        action: str,
    ) -> tuple[KeybindingConfig, str]:
        return self.capture_keybinding(keybindings, action, append=False)

    def capture_keybinding(
        self,
        keybindings: KeybindingConfig,
        action: str,
        append: bool,
    ) -> tuple[KeybindingConfig, str]:
        label = self.capture_keybinding_label(
            f"{keybinding_action_label(action)}: press key to bind"
        )
        if label is None:
            return keybindings, "unsupported key"
        labels = keybindings.labels(action)
        if append:
            if label in labels:
                return keybindings, f"{label} is already assigned to {keybinding_action_label(action)}"
            next_labels = (*labels, label)
        else:
            next_labels = (label,)
        try:
            next_keybindings = update_keybinding(keybindings, action, next_labels)
        except ValueError as exc:
            return keybindings, str(exc)
        return (
            next_keybindings,
            f"{keybinding_action_label(action)}: {format_keybinding_labels(next_labels)}",
        )

    def capture_keybinding_label(self, prompt: str) -> str | None:
        height, width = self.stdscr.getmaxyx()
        self.stdscr.move(height - 1, 0)
        self.stdscr.clrtoeol()
        self.safe_addstr(height - 1, 0, prompt[: max(0, width - 1)], curses.A_DIM)
        key = self.stdscr.getch()
        return key_label_for_code(key)
