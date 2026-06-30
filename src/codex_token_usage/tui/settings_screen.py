from __future__ import annotations

import curses
from dataclasses import replace

from ..keybindings import KEYBINDING_ACTIONS, keymap_for_config, reset_keybinding
from ..pricing import MODEL_PRICES, PricingConfig, normalize_model_name
from ..theme import load_theme_config, save_theme_config
from .settings_actions import SettingsActionsMixin
from .settings_flag_picker import SettingsFlagPickerMixin
from .settings_model import (
    APPEARANCE_SETTING_FIELDS,
    DISPLAY_SETTING_FIELDS,
    MISC_SETTING_FIELDS,
    RATE_FIELDS,
    SETTINGS_TABS,
    appearance_setting_label,
    default_setup_values,
    display_setting_label,
    keybinding_action_label,
    misc_setting_label,
    settings_model_names,
    settings_snapshot,
)
from .settings_rendering import SettingsRenderingMixin


class SettingsScreenMixin(
    SettingsRenderingMixin,
    SettingsActionsMixin,
    SettingsFlagPickerMixin,
):

    def open_settings(self) -> None:
        self.set_blocking_input()
        theme = self.options.theme
        display = self.options.display
        custom_prices = dict(self.options.pricing.model_prices)
        keybindings = self.options.keybindings
        limits = self.options.limits
        prediction = self.options.prediction
        auto_refresh_seconds = self.options.auto_refresh_seconds
        shutdown_seconds = self.options.shutdown_seconds
        model_names = settings_model_names(self.state.dataset, custom_prices)
        tab_index = 0
        model_index = 0
        rate_field_index = 0
        display_field_index = 0
        appearance_field_index = 0
        keybinding_index = 0
        misc_field_index = 0
        status = "settings: press 1-5 for tabs, enter/e to edit selected item"
        initial_settings = settings_snapshot(
            theme,
            display,
            custom_prices,
            keybindings,
            limits,
            prediction,
            auto_refresh_seconds,
            shutdown_seconds,
        )

        while True:
            model_names = settings_model_names(self.state.dataset, custom_prices)
            if not model_names:
                model_names = ["custom-model"]
            model_index = min(max(model_index, 0), len(model_names) - 1)
            self.render_settings(
                theme,
                display,
                custom_prices,
                model_names,
                tab_index,
                model_index,
                rate_field_index,
                display_field_index,
                appearance_field_index,
                keybindings,
                keybinding_index,
                prediction,
                auto_refresh_seconds,
                shutdown_seconds,
                misc_field_index,
                status,
            )
            key = self.stdscr.getch()
            settings_changed = (
                settings_snapshot(
                    theme,
                    display,
                    custom_prices,
                    keybindings,
                    limits,
                    prediction,
                    auto_refresh_seconds,
                    shutdown_seconds,
                )
                != initial_settings
            )

            if key in (ord("q"), 27):
                if settings_changed and not self.confirm_settings_action(
                    "Discard settings changes? y/N: "
                ):
                    status = "settings discard canceled"
                    continue
                self.state = replace(self.state, status="settings canceled")
                return
            if ord("1") <= key <= ord(str(len(SETTINGS_TABS))):
                tab_index = int(chr(key)) - 1
                status = f"tab: {SETTINGS_TABS[tab_index]}"
                continue
            if key == ord("s"):
                if settings_changed and not self.confirm_settings_action(
                    "Save settings changes? y/N: "
                ):
                    status = "settings save canceled"
                    continue
                pricing = PricingConfig(model_prices=tuple(sorted(custom_prices.items())))
                try:
                    path = save_theme_config(
                        theme,
                        display=display,
                        pricing=pricing,
                        keybindings=keybindings,
                        limits=limits,
                        prediction=prediction,
                        auto_refresh_seconds=auto_refresh_seconds,
                        shutdown_seconds=shutdown_seconds,
                    )
                except OSError as exc:
                    status = f"settings save failed: {exc}"
                    continue
                loaded = load_theme_config(path)
                self.options = replace(
                    self.options,
                    theme=loaded.config,
                    display=loaded.display,
                    pricing=loaded.pricing,
                    keybindings=loaded.keybindings,
                    limits=loaded.limits,
                    prediction=loaded.prediction,
                    auto_refresh_seconds=loaded.auto_refresh_seconds,
                    shutdown_seconds=loaded.shutdown_seconds,
                    theme_status=loaded.status,
                )
                self.keymap = keymap_for_config(loaded.keybindings)
                self.schedule_next_auto_refresh()
                self.theme_pairs = []
                self.accent_attr = curses.A_BOLD
                self.init_theme_colors()
                self.state = replace(
                    self.state,
                    pricing=loaded.pricing,
                    status=f"settings saved: {path}",
                )
                return
            if key in (ord("h"), curses.KEY_LEFT):
                if tab_index == 0:
                    rate_field_index = (rate_field_index - 1) % len(RATE_FIELDS)
                    status = f"field: {RATE_FIELDS[rate_field_index]}"
                elif tab_index == 1:
                    display_field_index = (display_field_index - 1) % len(DISPLAY_SETTING_FIELDS)
                    status = f"display: {display_setting_label(DISPLAY_SETTING_FIELDS[display_field_index])}"
                elif tab_index == 2:
                    appearance_field_index = (appearance_field_index - 1) % len(APPEARANCE_SETTING_FIELDS)
                    status = f"appearance: {appearance_setting_label(APPEARANCE_SETTING_FIELDS[appearance_field_index])}"
                elif tab_index == 3:
                    keybinding_index = (keybinding_index - 1) % len(KEYBINDING_ACTIONS)
                    status = f"keybinding: {keybinding_action_label(KEYBINDING_ACTIONS[keybinding_index])}"
                else:
                    misc_field_index = (misc_field_index - 1) % len(MISC_SETTING_FIELDS)
                    status = f"misc: {misc_setting_label(MISC_SETTING_FIELDS[misc_field_index])}"
                continue
            if key in (ord("l"), curses.KEY_RIGHT):
                if tab_index == 0:
                    rate_field_index = (rate_field_index + 1) % len(RATE_FIELDS)
                    status = f"field: {RATE_FIELDS[rate_field_index]}"
                elif tab_index == 1:
                    display_field_index = (display_field_index + 1) % len(DISPLAY_SETTING_FIELDS)
                    status = f"display: {display_setting_label(DISPLAY_SETTING_FIELDS[display_field_index])}"
                elif tab_index == 2:
                    appearance_field_index = (appearance_field_index + 1) % len(APPEARANCE_SETTING_FIELDS)
                    status = f"appearance: {appearance_setting_label(APPEARANCE_SETTING_FIELDS[appearance_field_index])}"
                elif tab_index == 3:
                    keybinding_index = (keybinding_index + 1) % len(KEYBINDING_ACTIONS)
                    status = f"keybinding: {keybinding_action_label(KEYBINDING_ACTIONS[keybinding_index])}"
                else:
                    misc_field_index = (misc_field_index + 1) % len(MISC_SETTING_FIELDS)
                    status = f"misc: {misc_setting_label(MISC_SETTING_FIELDS[misc_field_index])}"
                continue
            if key in (ord("j"), ord("n"), curses.KEY_DOWN):
                if tab_index == 0:
                    model_index = min(model_index + 1, len(model_names) - 1)
                    status = f"model: {model_names[model_index]}"
                elif tab_index == 1:
                    display_field_index = (display_field_index + 1) % len(DISPLAY_SETTING_FIELDS)
                    status = f"display: {display_setting_label(DISPLAY_SETTING_FIELDS[display_field_index])}"
                elif tab_index == 2:
                    appearance_field_index = (appearance_field_index + 1) % len(APPEARANCE_SETTING_FIELDS)
                    status = f"appearance: {appearance_setting_label(APPEARANCE_SETTING_FIELDS[appearance_field_index])}"
                elif tab_index == 3:
                    keybinding_index = min(keybinding_index + 1, len(KEYBINDING_ACTIONS) - 1)
                    status = f"keybinding: {keybinding_action_label(KEYBINDING_ACTIONS[keybinding_index])}"
                else:
                    misc_field_index = (misc_field_index + 1) % len(MISC_SETTING_FIELDS)
                    status = f"misc: {misc_setting_label(MISC_SETTING_FIELDS[misc_field_index])}"
                continue
            if key in (ord("k"), ord("p"), curses.KEY_UP):
                if tab_index == 0:
                    model_index = max(model_index - 1, 0)
                    status = f"model: {model_names[model_index]}"
                elif tab_index == 1:
                    display_field_index = (display_field_index - 1) % len(DISPLAY_SETTING_FIELDS)
                    status = f"display: {display_setting_label(DISPLAY_SETTING_FIELDS[display_field_index])}"
                elif tab_index == 2:
                    appearance_field_index = (appearance_field_index - 1) % len(APPEARANCE_SETTING_FIELDS)
                    status = f"appearance: {appearance_setting_label(APPEARANCE_SETTING_FIELDS[appearance_field_index])}"
                elif tab_index == 3:
                    keybinding_index = max(keybinding_index - 1, 0)
                    status = f"keybinding: {keybinding_action_label(KEYBINDING_ACTIONS[keybinding_index])}"
                else:
                    misc_field_index = (misc_field_index - 1) % len(MISC_SETTING_FIELDS)
                    status = f"misc: {misc_setting_label(MISC_SETTING_FIELDS[misc_field_index])}"
                continue
            if key in (ord("a"),):
                if tab_index == 3:
                    action = KEYBINDING_ACTIONS[keybinding_index]
                    keybindings, status = self.capture_keybinding(
                        keybindings,
                        action,
                        append=True,
                    )
                    continue
                if tab_index != 0:
                    status = "add is only available on Model Pricing or Keybindings"
                    continue
                model = self.prompt_input("model name: ")
                if not model:
                    status = "add model canceled"
                    continue
                model = normalize_model_name(model)
                price = self.prompt_full_model_price(model, custom_prices.get(model) or MODEL_PRICES.get(model))
                if price is None:
                    status = "add model canceled"
                    continue
                custom_prices[model] = price
                model_index = settings_model_names(self.state.dataset, custom_prices).index(model)
                status = f"custom rate saved for {model}"
                continue
            if key in (ord("x"),):
                if tab_index == 3:
                    action = KEYBINDING_ACTIONS[keybinding_index]
                    keybindings = reset_keybinding(keybindings, action)
                    status = f"{keybinding_action_label(action)} reset to default"
                    continue
                if tab_index != 0:
                    status = "reset is only available on Model Pricing or Keybindings"
                    continue
                model = model_names[model_index]
                if model in custom_prices:
                    del custom_prices[model]
                    status = f"custom override removed for {model}"
                else:
                    status = f"{model} has no custom override"
                continue
            if key in (ord("e"), ord(" "), 10, 13, curses.KEY_ENTER):
                if tab_index == 1:
                    display, status = self.apply_display_setting(
                        display,
                        DISPLAY_SETTING_FIELDS[display_field_index],
                    )
                    continue
                if tab_index == 2:
                    theme, status = self.apply_appearance_setting(
                        theme,
                        APPEARANCE_SETTING_FIELDS[appearance_field_index],
                    )
                    continue
                if tab_index == 3:
                    action = KEYBINDING_ACTIONS[keybinding_index]
                    keybindings, status = self.apply_keybinding_setting(
                        keybindings,
                        action,
                    )
                    continue
                if tab_index == 4:
                    misc_field = MISC_SETTING_FIELDS[misc_field_index]
                    if misc_field == "reset_setup":
                        if not self.confirm_settings_action(
                            "Reset all setup to defaults? y/N: "
                        ):
                            status = "reset all setup canceled"
                            continue
                        (
                            theme,
                            display,
                            custom_prices,
                            keybindings,
                            limits,
                            prediction,
                            auto_refresh_seconds,
                            shutdown_seconds,
                        ) = default_setup_values()
                        model_index = 0
                        rate_field_index = 0
                        display_field_index = 0
                        appearance_field_index = 0
                        keybinding_index = 0
                        status = "all setup reset to defaults; press s to save"
                        continue
                    (
                        prediction,
                        auto_refresh_seconds,
                        shutdown_seconds,
                        status,
                    ) = self.apply_misc_setting(
                        prediction,
                        auto_refresh_seconds,
                        shutdown_seconds,
                        misc_field,
                    )
                    continue
                model = model_names[model_index]
                price = custom_prices.get(model) or MODEL_PRICES.get(model)
                if price is None:
                    price = self.prompt_full_model_price(model, None)
                    if price is None:
                        status = "rate edit canceled"
                        continue
                    custom_prices[model] = price
                    status = f"custom rate saved for {model}"
                    continue
                next_price = self.prompt_rate_field(model, price, RATE_FIELDS[rate_field_index])
                if next_price is None:
                    status = "rate edit canceled"
                    continue
                custom_prices[model] = next_price
                status = f"{model} {RATE_FIELDS[rate_field_index]} rate updated"
