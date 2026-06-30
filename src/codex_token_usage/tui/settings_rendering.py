from __future__ import annotations

import curses

from ..forecast import PredictionConfig
from ..keybindings import KEYBINDING_ACTIONS, KeybindingConfig, format_keybinding_config
from ..pricing import ModelPrice
from ..theme import DisplayConfig, ThemeConfig, theme_palette
from .formatting import on_off, settings_columns, truncate, visible_start
from .settings_model import (
    RATE_FIELDS,
    SETTINGS_TABS,
    appearance_preview_block_height,
    auto_refresh_label,
    effective_settings_price,
    format_settings_rate,
    keybinding_action_label,
    prediction_algorithm_label,
    settings_price_source,
    settings_rate_text,
    shutdown_seconds_label,
    theme_current_preset_label,
)


class SettingsRenderingMixin:

    def render_settings(
        self,
        theme: ThemeConfig,
        display: DisplayConfig,
        custom_prices: dict[str, ModelPrice],
        model_names: list[str],
        tab_index: int,
        model_index: int,
        rate_field_index: int,
        display_field_index: int,
        appearance_field_index: int,
        keybindings: KeybindingConfig,
        keybinding_index: int,
        prediction: PredictionConfig,
        auto_refresh_seconds: int | None,
        shutdown_seconds: float,
        misc_field_index: int,
        status: str,
    ) -> None:
        self.stdscr.erase()
        height, width = self.stdscr.getmaxyx()
        self.render_themed_text(0, 0, "Settings", curses.A_BOLD)
        self.render_settings_tabs(1, width, tab_index)
        content_top = 3
        if tab_index == 1:
            self.render_display_settings(content_top, width, display, display_field_index)
        elif tab_index == 2:
            self.render_appearance_settings(content_top, height, width, theme, appearance_field_index)
        elif tab_index == 3:
            self.render_keybinding_settings(
                content_top,
                height,
                width,
                keybindings,
                keybinding_index,
            )
        elif tab_index == 4:
            self.render_misc_settings(
                content_top,
                width,
                prediction,
                auto_refresh_seconds,
                shutdown_seconds,
                misc_field_index,
            )
        else:
            self.render_model_pricing_settings(
                content_top,
                height,
                width,
                custom_prices,
                model_names,
                model_index,
                rate_field_index,
            )

        self.render_themed_text(
            height - 2,
            0,
            status[: max(0, width - 1)],
            curses.A_DIM,
            start_index=1,
        )
        footer = (
            "1-5 tabs  h/j/k/l select  enter/e edit  model: a add x reset  keys: a add x reset  "
            "s save  q cancel  changed asks confirm"
        )
        self.render_themed_text(
            height - 1,
            0,
            footer[: max(0, width - 1)],
            curses.A_DIM,
            start_index=2,
        )
        self.stdscr.refresh()

    def render_settings_tabs(self, y: int, width: int, selected_tab: int) -> None:
        x = 0
        for index, label in enumerate(SETTINGS_TABS):
            text = f" {index + 1} {label} "
            attr = curses.A_REVERSE | curses.A_BOLD if index == selected_tab else 0
            if x + len(text) >= width:
                break
            self.safe_addstr(y, x, text, attr)
            x += len(text) + 1

    def render_display_settings(
        self,
        top: int,
        width: int,
        display: DisplayConfig,
        selected_field: int,
    ) -> None:
        rows = [
            ("cached_tokens", "Cached tokens column", on_off(display.show_cached_tokens)),
            ("cached_percent", "Cached input % column", on_off(display.show_cached_percent)),
            ("estimated_cost", "Estimated API cost column", on_off(display.show_estimated_cost)),
            ("reasoning_level", "Reasoning level column", on_off(display.show_reasoning_level)),
            ("cache_miss", "Cache miss column", on_off(display.show_cache_miss)),
            ("reasoning_tokens", "Reasoning tokens column", on_off(display.show_reasoning_tokens)),
            ("model", "Model column", on_off(display.show_model)),
            ("context", "CWD/title column", on_off(display.show_context)),
            (
                "model_width",
                "Model column width",
                "auto" if display.model_column_width is None else str(display.model_column_width),
            ),
        ]
        self.safe_addstr(top, 0, "Display Columns", self.accent_attr)
        for index, (_, label, value) in enumerate(rows):
            attr = curses.A_REVERSE if index == selected_field else 0
            self.safe_addstr(
                top + 2 + index,
                0,
                f"{'>' if index == selected_field else ' '} {label:<28} {value}",
                attr,
            )
        self.safe_addstr(
            top + 2 + len(rows) + 1,
            0,
            "Enter toggles boolean columns or edits model width.",
            curses.A_DIM,
        )

    def render_appearance_settings(
        self,
        top: int,
        height: int,
        width: int,
        theme: ThemeConfig,
        selected_field: int,
    ) -> None:
        rows = [
            ("flag", "Current preset", theme_current_preset_label(theme)),
            ("color", "Color mode", theme.color_mode),
            ("light", "Lightness", format_settings_rate(theme.lightness)),
            ("accent_line", "Accent line", on_off(theme.show_accent_line)),
            ("themed_bars", "Themed usage bars", on_off(theme.themed_bars)),
        ]
        self.safe_addstr(top, 0, "Appearance", self.accent_attr)
        for index, (_, label, value) in enumerate(rows):
            attr = curses.A_REVERSE if index == selected_field else 0
            self.safe_addstr(
                top + 2 + index,
                0,
                f"{'>' if index == selected_field else ' '} {label:<28} {value}",
                attr,
            )
        self.safe_addstr(
            top + 2 + len(rows) + 1,
            0,
            "Enter cycles values, toggles booleans, or edits lightness.",
            curses.A_DIM,
        )
        preview_top = top + 2 + len(rows) + 3
        self.safe_addstr(preview_top, 0, "Current Color Scheme", self.accent_attr)
        preview_y = preview_top + 2
        block_height = appearance_preview_block_height(height, preview_y)
        self.render_theme_preview(preview_y, width, theme, block_height)

    def render_keybinding_settings(
        self,
        top: int,
        height: int,
        width: int,
        keybindings: KeybindingConfig,
        selected_action: int,
    ) -> None:
        self.safe_addstr(top, 0, "Keybindings", self.accent_attr)
        self.safe_addstr(
            top + 1,
            0,
            "Enter captures a replacement key. a adds a key. x resets the selected action.",
            curses.A_DIM,
        )
        header_y = top + 3
        action_width = min(34, max(18, width // 3))
        self.safe_addstr(header_y, 0, "  " + f"{'action':<{action_width}} keys", curses.A_BOLD)
        row_count = max(0, height - header_y - 3)
        start_index = visible_start(selected_action, row_count, len(KEYBINDING_ACTIONS))
        visible = KEYBINDING_ACTIONS[start_index : start_index + row_count]
        for offset, action in enumerate(visible):
            row_index = start_index + offset
            selected = row_index == selected_action
            marker = ">" if selected else " "
            attr = curses.A_REVERSE if selected else 0
            y = header_y + 1 + offset
            label = truncate(keybinding_action_label(action), action_width)
            keys = format_keybinding_config(keybindings, action)
            self.safe_addstr(
                y,
                0,
                f"{marker} {label:<{action_width}} {keys}",
                attr,
            )

    def render_misc_settings(
        self,
        top: int,
        width: int,
        prediction: PredictionConfig,
        auto_refresh_seconds: int | None,
        shutdown_seconds: float,
        selected_field: int,
    ) -> None:
        rows = [
            (
                "prediction_algorithm",
                "Prediction algorithm",
                prediction_algorithm_label(prediction.algorithm),
            ),
            (
                "auto_refresh_seconds",
                "Auto refresh",
                auto_refresh_label(auto_refresh_seconds),
            ),
            (
                "shutdown_seconds",
                "Shutdown time",
                shutdown_seconds_label(shutdown_seconds),
            ),
            (
                "about",
                "About",
                "show",
            ),
            (
                "reset_setup",
                "Reset all setup",
                "confirm",
            ),
        ]
        self.safe_addstr(top, 0, "Misc", self.accent_attr)
        for index, (_, label, value) in enumerate(rows):
            attr = curses.A_REVERSE if index == selected_field else 0
            self.safe_addstr(
                top + 2 + index,
                0,
                f"{'>' if index == selected_field else ' '} {label:<28} {value}",
                attr,
            )
        self.safe_addstr(
            top + 2 + len(rows) + 1,
            0,
            "Enter cycles prediction algorithms, edits timings, shows About, or resets setup.",
            curses.A_DIM,
        )

    def render_theme_preview(
        self,
        y: int,
        width: int,
        theme: ThemeConfig,
        block_height: int,
    ) -> None:
        if not theme.enabled:
            self.safe_addstr(y, 0, "plain: colors disabled", curses.A_DIM)
            preview_width = min(36, max(0, width - 1))
            for row in range(block_height):
                self.safe_addstr(y + 2 + row, 0, "#" * preview_width, curses.A_DIM)
            return

        palette = theme_palette(theme)
        if not palette:
            self.safe_addstr(y, 0, "no colors available", curses.A_DIM)
            return

        label = f"{theme.preset} / {theme.color_mode} / light {format_settings_rate(theme.lightness)}"
        self.safe_addstr(y, 0, label[: max(0, width - 1)], curses.A_DIM)
        swatch_x = 0
        for _index, rgb in enumerate(palette):
            if swatch_x + 3 >= width:
                break
            attr = self.preview_attr(rgb, curses.A_REVERSE | curses.A_BOLD)
            self.safe_addstr(y + 1, swatch_x, "  ", attr)
            swatch_x += 3

        preview_width = min(48, max(0, width - 1))
        self.render_palette_block(y + 2, 0, preview_width, block_height, palette)

    def render_model_pricing_settings(
        self,
        top: int,
        height: int,
        width: int,
        custom_prices: dict[str, ModelPrice],
        model_names: list[str],
        model_index: int,
        rate_field_index: int,
    ) -> None:
        model_width, input_x, cached_x, output_x, source_x = settings_columns(width)
        self.safe_addstr(top, 0, "Model Pricing", self.accent_attr)
        self.safe_addstr(
            top + 1,
            0,
            "Model rates are USD per 1M tokens. Custom rates override built-ins.",
            curses.A_DIM,
        )

        header_y = top + 3
        self.safe_addstr(header_y, 0, "  " + f"{'model':<{model_width}}", curses.A_BOLD)
        self.safe_addstr(header_y, input_x, f"{'input':>10}", curses.A_BOLD)
        self.safe_addstr(header_y, cached_x, f"{'cached':>10}", curses.A_BOLD)
        self.safe_addstr(header_y, output_x, f"{'output':>10}", curses.A_BOLD)
        self.safe_addstr(header_y, source_x, "source", curses.A_BOLD)

        row_count = max(0, height - header_y - 3)
        start_index = visible_start(model_index, row_count, len(model_names))
        visible = model_names[start_index : start_index + row_count]
        for offset, model in enumerate(visible):
            row_index = start_index + offset
            y = header_y + 1 + offset
            selected = row_index == model_index
            price = effective_settings_price(model, custom_prices)
            source = settings_price_source(model, custom_prices)
            row_attr = curses.A_REVERSE if selected else 0
            marker = ">" if selected else " "
            self.safe_addstr(
                y,
                0,
                f"{marker} {truncate(model, model_width):<{model_width}}",
                row_attr,
            )
            for index, (field, x) in enumerate(
                zip(RATE_FIELDS, (input_x, cached_x, output_x))
            ):
                attr = row_attr
                if selected and index == rate_field_index:
                    attr = curses.A_REVERSE | curses.A_BOLD
                self.safe_addstr(
                    y,
                    x,
                    f"{settings_rate_text(price, field):>10}",
                    attr,
                )
            self.safe_addstr(y, source_x, source, row_attr)
